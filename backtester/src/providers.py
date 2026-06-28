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
import os
import pickle
from urllib.parse import quote as _urlquote
import pandas as pd
import requests

from . import schema

# US equity-market full closures 2023–2026 (NYSE). Used to skip days that have no
# data so we don't hammer the feed with requests that can only come back empty.
NYSE_HOLIDAYS = {
    # 2023
    "2023-01-02", "2023-01-16", "2023-02-20", "2023-04-07", "2023-05-29",
    "2023-06-19", "2023-07-04", "2023-09-04", "2023-11-23", "2023-12-25",
    # 2024
    "2024-01-01", "2024-01-15", "2024-02-19", "2024-03-29", "2024-05-27",
    "2024-06-19", "2024-07-04", "2024-09-02", "2024-11-28", "2024-12-25",
    # 2025
    "2025-01-01", "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26",
    "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27", "2025-12-25",
    # 2026
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
}


class BaseProvider:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.symbol = cfg["symbol"]
        self.tz = cfg["timezone"]

    def trading_days(self) -> list[dt.date]:
        start = pd.Timestamp(self.cfg["start_date"]).date()
        end = pd.Timestamp(self.cfg["end_date"]).date()
        # Mon–Fri minus known market holidays (so we don't request closed days).
        days = pd.bdate_range(start, end)
        return [d.date() for d in days if d.strftime("%Y-%m-%d") not in NYSE_HOLIDAYS]

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
    ThetaData Terminal v3 (port 25503, /v3 REST, CSV responses).

    Verified against a live STANDARD options + FREE stock account:
      * /v3/option/history/quote  interval=1m  -> real NBBO bid/ask (the honest core).  ✓
      * /v3/option/history/greeks/eod          -> greeks + underlying_price, but EOD only.
      * minute greeks are NOT available, and stock endpoints are blocked on FREE.

    So intraday greeks and a stock price feed don't exist on this tier. We:
      - select the contract by NEAREST-ATM strike (no greeks needed), and
      - RECONSTRUCT the intraday underlying from option quotes via PUT-CALL PARITY:
        S(t) = K + call_mid(t) - put_mid(t)  (exact for 0DTE up to tiny rate/div terms).
        This uses only the real quotes you have; it is labelled reconstructed, not a feed.
    """

    def __init__(self, cfg: dict):
        super().__init__(cfg)
        self.base = cfg["data"]["thetadata"]["base_url"].rstrip("/")
        self.window = cfg["data"].get("thetadata", {}).get("strike_window", 8)
        self._cache = {}   # day -> {"underlying": df, "chain": df}

    def _get_csv(self, path: str, params: dict) -> pd.DataFrame:
        r = requests.get(f"{self.base}{path}", params=params, timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"ThetaData {path} -> {r.status_code}: {r.text[:200]}")
        df = pd.read_csv(io.StringIO(r.text))
        # follow pagination if the Terminal sets a Next-Page header
        nxt = r.headers.get("Next-Page") or r.headers.get("next-page")
        while nxt and nxt.lower() != "null":
            r = requests.get(nxt, timeout=120)
            if r.status_code != 200:
                break
            df = pd.concat([df, pd.read_csv(io.StringIO(r.text))], ignore_index=True)
            nxt = r.headers.get("Next-Page") or r.headers.get("next-page")
        return df

    def _ts(self, s: pd.Series) -> pd.Series:
        # v3 timestamps are naive ISO in exchange (ET) time, e.g. 2024-05-15T09:31:00.000
        return pd.to_datetime(s).dt.tz_localize(self.tz)

    def _quotes(self, day: dt.date, strike, right: str) -> pd.DataFrame:
        ds = day.strftime("%Y-%m-%d")
        raw = self._get_csv("/v3/option/history/quote", {
            "symbol": self.symbol, "expiration": ds, "strike": strike, "right": right,
            "start_date": ds, "end_date": ds, "interval": "1m",
        })
        if raw.empty or "bid" not in raw.columns:
            return pd.DataFrame(columns=["ts", "strike", "bid", "ask"])
        out = pd.DataFrame({
            "ts": self._ts(raw["timestamp"]),
            "strike": raw["strike"].astype(float),
            "bid": raw["bid"].astype(float),
            "ask": raw["ask"].astype(float),
        })
        return out[(out["bid"] > 0) & (out["ask"] >= out["bid"])].reset_index(drop=True)

    def _atm_strike(self, day: dt.date) -> float:
        ds = day.strftime("%Y-%m-%d")
        g = self._get_csv("/v3/option/history/greeks/eod", {
            "symbol": self.symbol, "expiration": ds, "strike": "*", "right": "call",
            "start_date": ds, "end_date": ds,
        })
        up = pd.to_numeric(g.get("underlying_price"), errors="coerce").dropna()
        strikes = pd.to_numeric(g.get("strike"), errors="coerce").dropna().unique()
        if up.empty or not len(strikes):
            raise RuntimeError(f"Couldn't anchor ATM for {self.symbol} {day} (greeks/eod empty).")
        anchor = float(up.median())
        return float(min(strikes, key=lambda k: abs(k - anchor)))

    def _disk_path(self, day: dt.date) -> str:
        d = os.path.join(os.path.dirname(__file__), "..", ".cache")
        os.makedirs(d, exist_ok=True)
        # "cp" = calls+puts cache (v2). Bumped from call-only so spreads have put data.
        return os.path.join(d, f"{self.symbol}_{day}_w{self.window}_cp.pkl")

    def _load_day(self, day: dt.date):
        if day in self._cache:                              # in-memory (this run)
            return self._cache[day]
        p = self._disk_path(day)
        if os.path.exists(p):                               # on-disk (previous runs) — no re-download
            try:
                with open(p, "rb") as f:
                    obj = pickle.load(f)
                self._cache[day] = obj
                return obj
            except Exception:
                pass
        k0 = self._atm_strike(day)                          # ATM anchor (any liquid strike works for parity)
        calls = self._quotes(day, "*", "call")              # full call chain @1m (real bid/ask)
        puts = self._quotes(day, "*", "put")                # full put chain @1m (needed for spreads + parity)
        if calls.empty or puts.empty:
            self._cache[day] = {"underlying": pd.DataFrame(), "chain": pd.DataFrame()}
            return self._cache[day]
        call0 = calls[(calls["strike"] - k0).abs() < 1e-3]
        put0 = puts[(puts["strike"] - k0).abs() < 1e-3]
        # ── PUT-CALL PARITY underlying: S = K + call_mid - put_mid (per minute) ──
        cm = call0.assign(cmid=(call0["bid"] + call0["ask"]) / 2)[["ts", "cmid"]]
        pm = put0.assign(pmid=(put0["bid"] + put0["ask"]) / 2)[["ts", "pmid"]]
        par = cm.merge(pm, on="ts", how="inner")
        par["S"] = k0 + par["cmid"] - par["pmid"]
        und = pd.DataFrame({
            "ts": par["ts"], "open": par["S"], "high": par["S"],
            "low": par["S"], "close": par["S"],
        }).sort_values("ts").reset_index(drop=True)
        smap = dict(zip(und["ts"], und["close"]))
        # restrict the tradeable chain to a window around the anchor; greeks unavailable intraday
        cwin = calls[(calls["strike"] >= k0 - self.window) & (calls["strike"] <= k0 + self.window)].copy()
        pwin = puts[(puts["strike"] >= k0 - self.window) & (puts["strike"] <= k0 + self.window)].copy()
        cwin["type"] = "C"
        pwin["type"] = "P"
        chain = pd.concat([cwin, pwin], ignore_index=True)
        chain["expiration"] = day
        chain["underlying_price"] = chain["ts"].map(smap)
        chain["delta"] = float("nan")
        chain["gamma"] = float("nan")
        chain["theta"] = float("nan")
        self._cache[day] = {"underlying": und, "chain": chain.reset_index(drop=True)}
        try:                                                # persist so re-runs skip the download
            with open(p, "wb") as f:
                pickle.dump(self._cache[day], f)
        except Exception:
            pass
        return self._cache[day]

    def load_underlying(self, day: dt.date) -> pd.DataFrame:
        return self._load_day(day)["underlying"]

    def load_options(self, day: dt.date) -> pd.DataFrame:
        return self._load_day(day)["chain"]


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


class YahooProvider(BaseProvider):
    """
    FREE price bars from Yahoo Finance — for FUTURES / stocks / ETFs (no options).

    Honest limits of free data:
      * Daily bars go back years; 5-min bars ~60 days; 1-min ~7 days. So an
        intraday futures backtest here only covers the recent weeks Yahoo serves.
      * OHLC only — there is NO bid/ask, so fills are modeled as bar price ± a
        slippage assumption (configurable), not a real quote. Futures spreads are
        tiny, so this is far less of a fudge than it would be for options.

    Use for futures (e.g. symbol "ES=F", "NQ=F", "MES=F", "MNQ=F").
    """
    def __init__(self, cfg: dict):
        super().__init__(cfg)
        yc = cfg["data"].get("yahoo", {})
        self.interval = yc.get("interval", "5m")
        self.range = yc.get("range", "60d")
        self._df = self._fetch()

    def _fetch(self) -> pd.DataFrame:
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{_urlquote(self.symbol)}"
               f"?interval={self.interval}&range={self.range}")
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        if r.status_code != 200:
            raise RuntimeError(f"Yahoo {self.symbol} -> {r.status_code}: {r.text[:160]}")
        res = (r.json().get("chart", {}).get("result") or [None])[0]
        if not res or "timestamp" not in res:
            raise RuntimeError(f"Yahoo returned no bars for {self.symbol} (bad symbol or range?).")
        q = res["indicators"]["quote"][0]
        df = pd.DataFrame({
            "ts": pd.to_datetime(res["timestamp"], unit="s", utc=True).tz_convert(self.tz),
            "open": q.get("open"), "high": q.get("high"), "low": q.get("low"), "close": q.get("close"),
        }).dropna()
        # regular cash session only (so the opening-range concept is meaningful)
        df = df[(df["ts"].dt.time >= dt.time(9, 30)) & (df["ts"].dt.time <= dt.time(16, 0))]
        return df.sort_values("ts").reset_index(drop=True)

    def trading_days(self) -> list[dt.date]:
        start = pd.Timestamp(self.cfg["start_date"]).date()
        end = pd.Timestamp(self.cfg["end_date"]).date()
        days = sorted(set(self._df["ts"].dt.date))
        return [d for d in days if start <= d <= end]

    def load_underlying(self, day: dt.date) -> pd.DataFrame:
        return self._df[self._df["ts"].dt.date == day].reset_index(drop=True)

    def load_options(self, day: dt.date) -> pd.DataFrame:
        return pd.DataFrame()   # futures mode trades the contract directly — no options


def get_provider(cfg: dict) -> BaseProvider:
    name = cfg["data"]["provider"]
    if name == "thetadata":
        return ThetaDataProvider(cfg)
    if name == "polygon":
        return PolygonProvider(cfg)
    if name == "yahoo":
        return YahooProvider(cfg)
    if name == "local":
        return LocalFileProvider(cfg)
    raise ValueError(f"Unknown data provider '{name}'. See config.json data.provider.")
