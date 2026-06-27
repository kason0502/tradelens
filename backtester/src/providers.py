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


def get_provider(cfg: dict) -> BaseProvider:
    name = cfg["data"]["provider"]
    if name == "thetadata":
        return ThetaDataProvider(cfg)
    if name == "local":
        return LocalFileProvider(cfg)
    raise ValueError(f"Unknown data provider '{name}'. See config.json data.provider.")
