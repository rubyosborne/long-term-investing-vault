# Methodology

## The 7-step Wide > Narrow > Confirm Funnel
Every stock idea passes all 7 steps. No exceptions.

1. **Macro Context** — rates, flows, cycle. Determines which themes to hunt in. Sources: FRED API (via scripts/fetch_macro.py), Macrotrends, Koyfin.
2. **Theme-Based Screening** — sector, cap, growth, valuation. Sources: Finviz scrape with yfinance fallback. Produces 10-20 candidates.
3. **Rapid Triage** — health check, red flag filter. Sources: Simply Wall St, Seeking Alpha, yfinance. Cuts to 5-7.
4. **Deep Research** — 5-10 year trends, moat, margin of safety. Sources: Stock Analysis, Stockstory, AlphaSpread (web), yfinance financials (API fallback).
5. **Institutional Signal Check** — congressional trades, options flow, 13Fs. Confirming signals only, never leading. Sources: Quiver Quant, Unusual Whales, 13f.info (web), with graceful degradation if scrape fails.
6. **Timing** — chart entry zone, earnings risk, support/resistance. Sources: TradingView (web), Earnings Whispers, yfinance (API fallback).
7. **Synthesis** — bull thesis, bear case, entry zone, invalidation trigger, dollar allocation, conviction rating.

## Data sourcing strategy
- **Primary:** scrape public web tools where possible
- **Fallback:** yfinance + FRED for stable APIs when scrape fails
- **Graceful degradation:** if both fail, document the gap in the brief, mark the pick as "data-incomplete"
- Brief always succeeds. Missing data is reported, not a failure.

## The 10 Analytical Templates
Used as needed, not on every pick:
1. Morgan Stanley DCF — 3-scenario single-stock valuation
2. Goldman Sachs sector screener — comparative ranking
3. Bridgewater risk framework — inflation/growth quadrant stress-test
4. JPMorgan earnings breakdown — post-earnings dissection
5. BlackRock portfolio construction — allocation and correlation
6. Citadel technical analysis — chart + options flow
7. Harvard endowment dividend — income + total return
8. Bain competitive advantage — moat depth across 5 types
9. Renaissance pattern finder — momentum, revisions, short interest
10. McKinsey macro impact — first/second-order sector winners

## The 6Rs Processing
1. **Record** — capture without friction (mobile Code tab > ops/inbox.md)
2. **Reduce** — Monday routine processes inbox into target notes
3. **Reflect** — graph pass, find unlinked connections
4. **Reweave** — quarterly, update older notes with new context
5. **Verify** — vault health check (Sunday routine)
6. **Rethink** — quarterly, steelman the bear case on every position
