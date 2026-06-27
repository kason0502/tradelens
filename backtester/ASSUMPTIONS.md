# Assumptions & where results can STILL overstate real performance

You asked me to walk through every assumption and say specifically where these
results could overstate reality. Here it is. Read it before trusting any green number.

## What the engine does well (the conservative parts)
1. **Buy at ask, sell at bid, always** — no mid-price fantasy.
2. **Extra slippage** (1.5¢/contract default) against you on both legs.
3. **$0.65/contract/leg commission.**
4. **Wide-spread filter** — trades with spread > $0.10 are skipped (or explicitly
   filled at the worse side if you choose `take_worse`).
5. **No look-ahead** — asof quotes (`ts <=` the bar), guards marked in source.
6. **Next-bar execution** — signals fill on the following bar, not the signal bar.
7. **Fragility report** — re-runs with harsher slippage; flags a profit→loss flip loudly.

## Where it can STILL overstate (be skeptical here)

1. **Fills assume your order *exists* at the quoted size.** We pay the ask, but on a
   fast 0DTE quote the displayed ask may be for 1 lot and vanish before you're filled.
   Real fills can be worse than "ask + 1.5¢," especially in size. → Stress slippage
   harder than 1.5¢ in the fragility scenarios; size sensitivity is not modeled.

2. **No partial fills / no queue position.** You're assumed fully filled instantly at
   the next bar. Marketable limits in fast tape may partially fill or miss.

3. **Minute bars hide intrabar path.** If both take-profit and stop are touchable
   within the same minute, the engine uses the bar's close-based logic — it can
   credit a TP that, intrabar, would have hit the stop first (or vice-versa). This is
   the single biggest optimism risk for intraday. → Use finer data, or model
   "stop-checked-before-target within the bar" pessimistically (not yet implemented
   for options legs — the *underlying* stop uses bar close).

4. **Quote timestamp ≠ your latency.** Even asof-correct quotes assume you act on the
   next *minute* bar. A real discretionary/algo entry has its own lag and may get a
   different quote. Sub-minute reality is not captured.

5. **Greeks are the vendor's, at the vendor's vol.** Contract selection by delta is
   only as good as the feed's greeks; stale or model-based greeks bias selection.

6. **Survivorship / data gaps.** Days that fail to load are skipped, not zero-filled.
   If your feed silently drops illiquid/halted days, the sample is rosier than live.

7. **Assignment/early-exercise, halts, and odd settlements** are not modeled. For
   0DTE these are usually minor but not zero (esp. pin risk near the close).

8. **No borrow/financing, no PDT/margin constraints, no taxes.**

9. **One symbol, one strategy, in-sample.** Tuning take-profit %, delta, or the
   opening-range length on the same data you measure is curve-fitting. Always keep a
   true out-of-sample window you never touched while building.

10. **Starting-capital % / Sharpe are sizing artifacts.** With 1 contract/trade, the
    "% return" just scales with the capital you typed in `config.json`. Treat dollar
    P&L and profit factor as primary; Sharpe here is a rough daily-aggregate proxy.

## Bottom line
If the **base case is barely positive and the fragility report shows it flips on a
50% slippage bump, treat it as no edge.** A real edge survives harsher fills, holds
up out-of-sample on data you never tuned against, and doesn't depend on the minute-bar
intrabar ambiguity in (3).
