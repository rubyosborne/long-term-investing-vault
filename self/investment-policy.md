# Investment Policy

This file is the operating constitution. Every brief must enforce these rules. Violations must be flagged in the brief, not silently overridden.

## Capital allocation
- $250/week DCA, weekly cadence
- Sliding split between core and discretionary based on conviction:
  - High conviction week: up to 100% to a single core compounder
  - Average week: spread across 2-4 picks
  - Low conviction week: hold cash, deploy double next week (max 1-week skip)
- Total allocation per week must equal $250 unless skipping

## Position sizing buckets
| Bucket | Target % of portfolio | Per-position cap |
|---|---|---|
| Growth compounders | 60-70% | 15% of portfolio |
| Theme plays | 20-30% | 8% of portfolio |
| Asymmetric bets | 0-10% | 2% of portfolio at entry |

If any cap is breached, the brief flags it with ⚠️ and proposes rebalancing in next week's allocation.

## Asymmetric bet guardrails (all five required)
1. **Position cap:** ≤2% of total portfolio at entry. Winners can run, but no adding.
2. **Mandatory thesis structure:** binary catalyst + specific date window + upside multiple (2x/5x/10x) + explicit kill condition.
3. **Bear case at 2x depth:** ≥400 words of bear case (vs ≥200 for normal picks).
4. **18-month sunset:** if catalyst hasn't played out in 18 months, exit regardless of price. Asymmetric bets that drift become dead money.
5. **Bucket cap:** total asymmetric allocation ≤10% of portfolio. If you keep finding "asymmetric" bets, you are miscategorising. They are really speculative growth.

## Insight handling (mid-week submissions)
1. **48-hour cooldown:** insights submitted Wednesday onwards are not actioned in the immediate Monday brief unless confirmed by an independent source. Treat as "watching" not "buying."
2. **Source tier:** every insight must declare a source tier:
   - **Tier 1:** SEC filing, earnings call transcript, primary company doc. Full weight.
   - **Tier 2:** Tier-1 financial press (Bloomberg, Reuters, FT, WSJ). Full weight after independent confirmation.
   - **Tier 3:** secondary press, analyst notes, Substacks. Discounted, watchlist only.
   - **Tier 4:** social (X, Reddit, podcasts). Noted but never trade trigger.
3. **Frequency limit:** if more than 5 insights submitted in a single week, brief flags it: "high insight volume detected. Consider whether you are trading on news rather than investing on theses."

## Theme construction
- Themes are additive overlays on top of stock-by-stock selection, not the only direction.
- "Infrastructure" theme means AI compute, energy, semis, datacenter, not specific company names.
- The Gap & Concentration Check must include cross-theme correlation analysis. Tickers appearing in 2+ themes are flagged. Effective theme count (after correlation adjustment) must be reported.

## Exit framework (read every Monday)
For every active position:
1. Re-read the invalidation trigger from the stock note
2. Check current price/fundamentals against the trigger
3. If breached: brief includes "EXIT TRIGGERED" callout with rationale
4. If approaching breach (within 20%): "WATCH" callout
5. If thesis intact: "HOLD" with one-line confirmation

## Tax trajectory (FIF)
- Track NZD cost basis cumulatively (not market value)
- When cost basis exceeds NZD $40k, brief includes "FIF threshold approaching" warning
- When cost basis exceeds NZD $50k, brief mandates a strategy review section discussing FDR vs comparative value method

## FX context
- Every brief includes current NZD/USD vs 5-year mean
- If NZD is >10% below 5-year mean: flag as "expensive USD entry" in allocation discussion
- If NZD is >10% above 5-year mean: flag as "cheap USD entry"
- This does not change recommendations. It informs them.

## Forbidden actions
- Claude never executes trades. Ruby places every order.
- Claude never invents prices. If yfinance and scraping both fail, the brief reports the gap.
- Claude never deletes files without explicit confirmation.
- Claude never recommends leverage, options, shorting, or derivatives without explicit Ruby request.
