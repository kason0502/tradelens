"""
SYNTHETIC data provider — for wiring up / demoing the UI only.

Everything here is FAKE: a random-walk underlying with an engineered opening-range
breakout, and a toy option chain priced off intrinsic value + a crude time value.
It exists so you can see STRATA's 0DTE Lab render before paying for a data feed.

Results produced from this are stamped synthetic=true and must NEVER be read as
real performance. The real path (providers.ThetaDataProvider / LocalFileProvider)
uses genuine NBBO quotes and aborts on missing fields.
"""
from __future__ import annotations
import datetime as dt
import numpy as np
import pandas as pd

from .providers import BaseProvider


class DemoProvider(BaseProvider):
    def __init__(self, cfg: dict):
        super().__init__(cfg)
        self.rng = np.random.default_rng(7)

    def load_underlying(self, day: dt.date) -> pd.DataFrame:
        # Deterministic per day so fragility re-runs compare apples to apples.
        self.rng = np.random.default_rng(day.toordinal())
        # 390 one-minute bars 09:30–16:00.
        start = pd.Timestamp(day, tz=self.tz) + pd.Timedelta(hours=9, minutes=30)
        ts = [start + pd.Timedelta(minutes=i) for i in range(390)]
        px0 = 500 + self.rng.normal(0, 3)
        steps = self.rng.normal(0, 0.05, 390).cumsum()
        # engineer a small opening range then a drift so breakouts sometimes occur
        drift = np.linspace(0, self.rng.normal(0.6, 1.2), 390)
        close = px0 + steps + drift
        high = close + np.abs(self.rng.normal(0, 0.06, 390))
        low = close - np.abs(self.rng.normal(0, 0.06, 390))
        opn = np.concatenate([[close[0]], close[:-1]])
        return pd.DataFrame({"ts": ts, "open": opn, "high": high, "low": low, "close": close})

    def load_options(self, day: dt.date) -> pd.DataFrame:
        und = self.load_underlying(day)
        rows = []
        atm = round(und["close"].iloc[0])
        strikes = [atm + k for k in range(-6, 7)]
        for _, b in und.iterrows():
            S = b["close"]
            mins_left = max(1, (pd.Timestamp(day, tz=self.tz) + pd.Timedelta(hours=16) - b["ts"]).total_seconds() / 60)
            tv = 0.9 * np.sqrt(mins_left / 390)  # crude time value, decays into the close
            for K in strikes:
                for typ in ("C", "P"):
                    intrinsic = max(0, S - K) if typ == "C" else max(0, K - S)
                    mid = intrinsic + tv
                    spread = 0.04 + 0.02 * abs(S - K) / 5     # wider OTM
                    bid = max(0.01, mid - spread / 2)
                    ask = mid + spread / 2
                    moneyness = (S - K) if typ == "C" else (K - S)
                    delta = float(np.clip(0.5 + moneyness * 0.12, 0.02, 0.98))
                    if typ == "P":
                        delta = -delta
                    rows.append({
                        "ts": b["ts"], "expiration": day, "strike": float(K), "type": typ,
                        "bid": round(bid, 2), "ask": round(ask, 2),
                        "delta": round(abs(delta), 3), "gamma": 0.05, "theta": -round(tv / mins_left, 4),
                        "underlying_price": round(S, 2),
                    })
        return pd.DataFrame(rows)
