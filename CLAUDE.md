# Long Term Investing — Repo Instructions

## At session start, read in this order
1. `self/identity.md`
2. `self/methodology.md`
3. `self/style.md`
4. `self/investment-policy.md`
5. `Investing Knowledge Base/Home.md`
6. `Investing Knowledge Base/03-Themes/Theme Index.md`
7. `Investing Knowledge Base/06-Watchlist/Current Watchlist.md`
8. `Investing Knowledge Base/07-Portfolio/Holdings.md`
9. `ops/processing-queue.md`
10. `ops/inbox.md`
11. `ops/trades.md`

## Routing rules
- Investing notes go inside `Investing Knowledge Base/` only.
- Identity, style, methodology, policy go in `self/`.
- Inbox, queue, prices, logs go in `ops/`.
- Routine prompts go in `prompts/`.
- Python scripts go in `scripts/`.
- Never write at repo root except README.md and CLAUDE.md.

## Model selection
- Opus: Monday brief, deep research, DCFs, funnel synthesis, asymmetric bet bear cases
- Sonnet: inbox processing, mechanical edits, link audits, commit messages

## Operating reminders
- Investment policy in `self/investment-policy.md` is enforced, not advisory.
- Brief must run all six required sections (portfolio overview, gap check, exit review, ideas, watchlist, allocation) even if some have nothing to report.
- Failed data sources are reported, not faked.
