"""
Data providers — normalize a vendor's options data into the schema in schema.py.

Swappable by design: implement `load_options(day)` and `load_underlying(day)`
returning frames in the normalized schema, and the engine doesn't care where the
data came from. Two adapters ship here:

  - ThetaDataProvider : pulls real minute NBBO bid/ask + greeks via the local
                        Theta Terminal REST API. THE honest path for 0DTE.
  - LocalFileProvider : reads CSV/Parquet you've already downloaded.

IMPORTANT honesty note on ThetaData: the exact endpoint paths/params and which
greeks your subscription exposes vary by tier and Terminal version. The mapping
below targets the v2 REST API; verify field names against the docs you have
access to. If greeks aren't in your tier, the run ABORTS (schema.py) rather than
inventing them.
"""
from __future__ import annotations
import datetime as dt
import io
import pandas as pd
import requests

from . import schema


class BaseProvider:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.symbol = cfg["symbol"]
        self.tz = cfg["timezone"]

    def trading_days(self) -> list[dt.date]:
        start = pd.Timestamp(self.cfg["start_date"]).date()
        end = pd.Timestamp(self.cfg["end_date"]).date()
        # Mon–Fri only; real holiday calendar is the user's job (see README).
        days = pd.bdate_range(start, end)
        return [d.date() for d in days]

    def load_options(self, day: dt.date) -> pd.DataFrame:
        raise NotImplementedError

    def load_underlying(self, day: dt.date) -> pd.DataFrame:
        raise NotImplementedError


class LocalFileProvider(BaseProvider):
    """Reads pre-downloaded files. The reliable, vendor-agnostic path."""

    def __init__(self, cfg: dict):
        super().__init__(cfg)
        opt = cfg["data"]["local"]["quotes_path"]
        und = cfg["data"]["local"]["underlying_path"]
        self._opt = self._read(opt)
        self._und = self._read(und)
        # localize naive ts if needed
        for df in (self._opt, self._und):
            if "ts" in df.columns and not isinstance(df["ts"].dtype, pd.DatetimeTZDtype):
                df["ts"] = pd.to_datetime(df["ts"]).dt.tz_localize(self.tz)
        if "expiration" in self._opt.columns:
            self._opt["expiration"] = pd.to_datetime(self._opt["expiration"]).dt.date

    @staticmethod
    def _read(path: str) -> pd.DataFrame:
        if path.endswith(".parquet"):
            return pd.read_parquet(path)
        return pd.read_csv(path)

    def load_options(self, day: dt.date) -> pd.DataFrame:
        d = self._opt[self._opt["ts"].dt.date == day].copy()
        # 0DTE only: keep contracts expiring the SAME day.
        return d[d["expiration"] == day].copy()

    def load_underlying(self, day: dt.date) -> pd.DataFrame:
        return self._und[self._und["ts"].dt.date == day].copy()


class ThetaDataProvider(BaseProvider):
    """
    Pulls minute NBBO quotes + greeks from a locally-running Theta Terminal.
    Endpoints used (v2 REST): /v2/hist/option/quote, /v2/hist/option/greeks,
    /v2/hist/stock/ohlc. ivl=60000 ms => 1-minute bars.
    """

    def __init__(self, cfg: dict):
        super().__init__(cfg)
        self.base = cfg["data"]["thetadata"]["base_url"].rstrip("/")

    def _get_csv(self, path: str, params: dict) -> pd.DataFrame:
        params = dict(params)
        params.setdefault("use_csv", "true")
        r = requests.get(f"{self.base}{path}", params=params, timeout=60)
        if r.status_code != 200:
            raise RuntimeError(
                f"ThetaData {path} returned {r.status_code}: {r.text[:200]}\n"
                "Is Theta Terminal running and logged in? Does your tier cover this endpoint?"
            )
        return pd.read_csv(io.StringIO(r.text))

    def load_underlying(self, day: dt.date) -> pd.DataFrame:
        ds = day.strftime("%Y%m%d")
        raw = self._get_csv("/v2/hist/stock/ohlc", {
            "root": self.symbol, "start_date": ds, "end_date": ds, "ivl": 60000,
        })
        # Theta returns ms_of_day + date; build a tz-aware ts.
        ts = self._build_ts(raw, day)
        out = pd.DataFrame({
            "ts": ts,
            "open": raw["open"].astype(float),
            "high": raw["high"].astype(float),
            "low": raw["low"].astype(float),
            "close": raw["close"].astype(float),
        })
        return out

    def load_options(self, day: dt.date) -> pd.DataFrame:
        ds = day.strftime("%Y%m%d")
        # One bulk pull of the whole same-day-expiry chain (quotes), then greeks, then merge.
        q = self._get_csv("/v2/bulk_hist/option/quote", {
            "root": self.symbol, "exp": ds, "start_date": ds, "end_date": ds, "ivl": 60000,
        })
        g = self._get_csv("/v2/bulk_hist/option/greeks", {
            "root": self.symbol, "exp": ds, "start_date": ds, "end_date": ds, "ivl": 60000,
        })
        q_ts = self._build_ts(q, day)
        g_ts = self._build_ts(g, day)
        quotes = pd.DataFrame({
            "ts": q_ts,
            "strike": q["strike"].astype(float) / 1000.0,   # Theta strikes are in 1/10 cents
            "type": q["right"].str.upper().str[0],
            "bid": q["bid"].astype(float),
            "ask": q["ask"].astype(float),
            "underlying_price": q.get("underlying_price", pd.Series([float("nan")] * len(q))),
        })
        greeks = pd.DataFrame({
            "ts": g_ts,
            "strike": g["strike"].astype(float) / 1000.0,
            "type": g["right"].str.upper().str[0],
            "delta": g.get("delta"),
            "gamma": g.get("gamma"),
            "theta": g.get("theta"),
        })
        df = quotes.merge(greeks, on=["ts", "strike", "type"], how="left")
        df["expiration"] = day
        return df

    def _build_ts(self, raw: pd.DataFrame, day: dt.date) -> pd.Series:
        # Theta gives ms_of_day (and sometimes a 'date' column). Build tz-aware ts.
        if "ms_of_day" not in raw.columns:
            raise RuntimeError(
                "ThetaData response missing 'ms_of_day' — cannot build timestamps. "
                "Verify the endpoint/version; the engine will not guess timestamps."
            )
        base = pd.Timestamp(day, tz=self.tz)
        return base + pd.to_timedelta(raw["ms_of_day"].astype("int64"), unit="ms")


class PolygonProvider(BaseProvider):
    """
    Polygon.io adapter.

    HONEST LIMITS (read these):
      * Polygon gives REAL NBBO bid/ask via /v3/quotes (tick-level) — requires an
        Options tier that includes QUOTES. If your plan only has trade aggregates,
        load_options ABORTS rather than faking bid/ask from trades.
      * Polygon does NOT serve historical greeks (delta/gamma/theta are live-snapshot
        only). So this provider returns greeks = NaN and the strategy must select by
        nearest-ATM strike (set strategy.contract_selection = "nearest_atm"). We never
        invent greeks.

    To stay tractable we only pull quotes for strikes within `strike_window` of the
    opening ATM (a 0DTE call chain is huge); that's fine for an ATM strategy.
    """
    BASE = "https://api.polygon.io"

    def __init__(self, cfg: dict):
        super().__init__(cfg)
        import os
        pc = cfg["data"].get("polygon", {})
        self.key = os.environ.get(pc.get("api_key_env", "POLYGON_API_KEY")) or pc.get("api_key")
        if not self.key:
            raise RuntimeError(
                "No Polygon API key. Set the POLYGON_API_KEY environment variable "
                "(preferred — keeps it out of the committed config) or data.polygon.api_key."
            )
        self.window = pc.get("strike_window", 8)
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {self.key}"})

    def _get(self, url: str, params: dict | None = None):
        import time
        full = url if url.startswith("http") else self.BASE + url
        for attempt in range(6):
            r = self.s.get(full, params=params, timeout=60)
            if r.status_code == 429:                       # rate limited — back off
                time.sleep(1.5 * (attempt + 1)); continue
            if r.status_code != 200:
                raise RuntimeError(f"Polygon {url} -> {r.status_code}: {r.text[:200]}")
            return r.json()
        raise RuntimeError("Polygon kept returning 429 (rate limit). Slow down or upgrade tier.")

    def diagnose(self, day: dt.date) -> dict:
        """Probe what this API key is actually entitled to (no exceptions raised)."""
        ds = day.strftime("%Y-%m-%d")
        out = {}

        def probe(label, url, params=None):
            full = url if url.startswith("http") else self.BASE + url
            try:
                r = self.s.get(full, params=params, timeout=30)
                ok = r.status_code == 200
                msg = ""
                if not ok:
                    try:
                        msg = r.json().get("message", "")[:140]
                    except Exception:
                        msg = r.text[:140]
                out[label] = {"ok": ok, "status": r.status_code, "msg": msg}
                return r
            except Exception as e:
                out[label] = {"ok": False, "status": "ERR", "msg": str(e)[:140]}
                return None

        probe("Stocks minute bars (underlying SPY)",
              f"/v2/aggs/ticker/{self.symbol}/range/1/minute/{ds}/{ds}", {"limit": 1})
        rc = probe("Options contracts list (0DTE calls)", "/v3/reference/options/contracts",
                   {"underlying_ticker": self.symbol, "expiration_date": ds,
                    "contract_type": "call", "expired": "true", "limit": 1})
        tk = None
        try:
            if rc is not None and rc.status_code == 200:
                res = rc.json().get("results", [])
                if res:
                    tk = res[0]["ticker"]
        except Exception:
            pass
        if tk:
            probe(f"Options QUOTES bid/ask ({tk})", f"/v3/quotes/{tk}", {"limit": 1})
        else:
            out["Options QUOTES bid/ask"] = {"ok": False, "status": "-",
                                             "msg": "couldn't list a contract to test (reference call failed)"}
        return out

    def load_underlying(self, day: dt.date) -> pd.DataFrame:
        ds = day.strftime("%Y-%m-%d")
        j = self._get(f"/v2/aggs/ticker/{self.symbol}/range/1/minute/{ds}/{ds}",
                      {"adjusted": "true", "sort": "asc", "limit": 50000})
        res = j.get("results") or []
        if not res:
            raise RuntimeError(f"No {self.symbol} minute bars for {ds} (non-trading day or entitlement).")
        ts = pd.to_datetime([r["t"] for r in res], unit="ms", utc=True).tz_convert(self.tz)
        df = pd.DataFrame({
            "ts": ts,
            "open": [r["o"] for r in res], "high": [r["h"] for r in res],
            "low": [r["l"] for r in res], "close": [r["c"] for r in res],
        })
        # regular session only
        df = df[(df["ts"].dt.time >= dt.time(9, 30)) & (df["ts"].dt.time <= dt.time(16, 0))]
        return df.reset_index(drop=True)

    def _list_calls(self, day: dt.date, atm: float):
        ds = day.strftime("%Y-%m-%d")
        params = {
            "underlying_ticker": self.symbol, "expiration_date": ds, "contract_type": "call",
            "strike_price.gte": atm - self.window, "strike_price.lte": atm + self.window,
            "expired": "true", "limit": 1000,
        }
        j = self._get("/v3/reference/options/contracts", params)
        out = []
        while True:
            for c in j.get("results", []):
                out.append({"ticker": c["ticker"], "strike": float(c["strike_price"])})
            nxt = j.get("next_url")
            if not nxt:
                break
            j = self._get(nxt)
        return out

    def _minute_quotes(self, opt_ticker: str, day: dt.date):
        start = pd.Timestamp(day, tz=self.tz) + pd.Timedelta(hours=9, minutes=30)
        end = pd.Timestamp(day, tz=self.tz) + pd.Timedelta(hours=16)
        params = {
            "timestamp.gte": int(start.value), "timestamp.lte": int(end.value),  # nanoseconds, UTC
            "order": "asc", "limit": 50000,
        }
        rows = []
        j = self._get(f"/v3/quotes/{opt_ticker}", params)
        while True:
            for q in j.get("results", []):
                rows.append((q.get("sip_timestamp"), q.get("bid_price"), q.get("ask_price")))
            nxt = j.get("next_url")
            if not nxt:
                break
            j = self._get(nxt)
        if not rows:
            return None
        qdf = pd.DataFrame(rows, columns=["ns", "bid", "ask"]).dropna()
        if qdf.empty:
            return None
        qts = pd.to_datetime(qdf["ns"], unit="ns", utc=True).dt.tz_convert(self.tz)
        qdf["ts"] = qts.dt.floor("min")
        last = qdf.sort_values("ns").groupby("ts", as_index=False).tail(1)  # last quote in each minute
        return last[["ts", "bid", "ask"]]

    def load_options(self, day: dt.date) -> pd.DataFrame:
        und = self.load_underlying(day)
        if und.empty:
            return pd.DataFrame()
        atm = round(float(und["close"].iloc[0]))
        contracts = self._list_calls(day, atm)
        if not contracts:
            raise RuntimeError(f"No 0DTE call contracts listed for {self.symbol} {day}.")
        umap = dict(zip(und["ts"], und["close"]))
        frames = []
        for c in contracts:
            qm = self._minute_quotes(c["ticker"], day)
            if qm is None or qm.empty:
                continue
            qm = qm.copy()
            qm["expiration"] = day
            qm["strike"] = c["strike"]
            qm["type"] = "C"
            qm["underlying_price"] = qm["ts"].map(umap)
            qm["delta"] = float("nan")   # Polygon has no historical greeks — NOT estimated
            qm["gamma"] = float("nan")
            qm["theta"] = float("nan")
            frames.append(qm)
        if not frames:
            raise RuntimeError(
                f"No NBBO quotes returned for {self.symbol} 0DTE on {day}. Your Polygon plan most "
                "likely lacks OPTIONS QUOTES (NBBO) — it only has trade aggregates. The engine will "
                "NOT fabricate bid/ask from trades. Upgrade to an Options tier that includes quotes."
            )
        return pd.concat(frames, ignore_index=True)


def get_provider(cfg: dict) -> BaseProvider:
    name = cfg["data"]["provider"]
    if name == "thetadata":
        return ThetaDataProvider(cfg)
    if name == "polygon":
        return PolygonProvider(cfg)
    if name == "local":
        return LocalFileProvider(cfg)
    raise ValueError(f"Unknown data provider '{name}'. See config.json data.provider.")
