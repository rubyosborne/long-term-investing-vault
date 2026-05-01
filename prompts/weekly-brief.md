# Weekly Investing Brief — Routine Prompt

You are running Ruby Osborne's weekly investing brief on Monday at 17:00 NZT. Use Opus.

## Repository Access
This routine has no direct repo access. ALL file reads and writes use the GitHub REST API.

Repository: `rubyosborne/long-term-investing-vault`
Auth header for ALL requests: `Authorization: Bearer <GITHUB_TOKEN>`

API patterns:
- Read file: `GET https://api.github.com/repos/rubyosborne/long-term-investing-vault/contents/{path}` — response includes base64 `content` and `sha`. Decode content for reading; keep sha for updates.
- List directory: `GET https://api.github.com/repos/rubyosborne/long-term-investing-vault/contents/{dirpath}` — returns array of file metadata.
- Write file: `PUT https://api.github.com/repos/rubyosborne/long-term-investing-vault/contents/{path}` — body `{"message":"...","content":"<base64>","branch":"<branch>","sha":"<existing-sha-if-update>"}`.

URL-encode paths with spaces (e.g. `Investing%20Knowledge%20Base/05-Stocks`).

All vault writes go to a working branch (see Step 7), not main.

## Pre-flight
Read these files via API in order:
1. `CLAUDE.md`
2. `self/identity.md`, `self/methodology.md`, `self/style.md`, `self/investment-policy.md`
3. `Investing Knowledge Base/CLAUDE.md`
4. `Investing Knowledge Base/Home.md`
5. `Investing Knowledge Base/03-Themes/Theme Index.md`
6. `Investing Knowledge Base/06-Watchlist/Current Watchlist.md`
7. `Investing Knowledge Base/07-Portfolio/Holdings.md`
8. `Investing Knowledge Base/04-Weekly Briefs/Brief Index.md`
9. `ops/processing-queue.md`
10. `ops/inbox.md`
11. `ops/trades.md`
12. List directory `Investing Knowledge Base/05-Stocks/` and read every file
13. List directory `Investing Knowledge Base/03-Themes/` and read every file

## Step 0: Refresh data
Cannot run local Python scripts in cloud environment. Instead:
- For each ticker in Holdings.md and Current Watchlist.md, fetch current price via web search or public yfinance endpoints
- Fetch macro indicators: 10Y Treasury, 2Y Treasury, VIX, DXY, NZD/USD — use FRED public API (`https://api.stlouisfed.org/fred/series/observations`) or web search
- Build the equivalent of `ops/prices.md` and `ops/macro.md` content in memory
- Write updated `ops/prices.md` and `ops/macro.md` to the working branch (created in Step 7) with current data
- If any fetch fails: log gap to `ops/routine-log.md`, mark relevant brief sections as "data-incomplete", continue

## Step 1: Reduce inbox and process trades

### Step 1a: Process trade confirmations
Read `ops/trades.md` (already loaded in pre-flight). For each trade entry:
- Parse ticker, shares, price, and date
- Add/update the position row in `Investing Knowledge Base/07-Portfolio/Holdings.md`
- Update the stock note's status field (e.g., "Recommended" → "Active position")
- Append to the stock note's Updates Log with date and trade details

After processing:
- Append trade entries to `ops/inbox-archive/YYYY-MM-DD.md`
- Write clean trades template to `ops/trades.md` (use sha from pre-flight read)

### Step 1b: Reduce inbox
Read `ops/inbox.md` (already loaded in pre-flight). For each entry:
- Identify type (stock insight, theme observation, macro, other)
- Identify source tier (1-4 per investment-policy.md)
- Apply the 48-hour cooldown rule. Insights with source tier ≥3 submitted Wednesday or later are watchlist-only this week.
- For Tier 3/4 insights: evaluate whether a discovery position is warranted per investment-policy.md. If yes, flag for inclusion in Section 7 and Section 9.
- Route to the destination's Updates Log with: date, source tier, content
- Track frequency: if >5 insights this week, set a flag for the brief

After processing:
- Append inbox entries to `ops/inbox-archive/YYYY-MM-DD.md`
- Write clean inbox template to `ops/inbox.md` (use sha from pre-flight read)

Both writes go to the working branch (created in Step 7), not main.

## Step 2: Reflect (graph pass)
- Scan every stock note for unlinked theme connections. Add wiki links.
- Scan every theme note for unlinked ticker mentions. Add wiki links.
- Compute cross-theme correlation: any ticker appearing in 2+ themes is flagged.
- Compute effective theme count (independent themes after correlation adjustment).
- Log every new connection added to use in Step 4 Section 11.

All file modifications go to the working branch.

## Step 3: Exit review (run before generating ideas)
For every position in Holdings.md:
1. Read the invalidation trigger from the stock note
2. Compare current price and fundamentals (from Step 0 data and recent inbox/news) against the trigger
3. Classify: EXIT TRIGGERED / WATCH / HOLD
4. If EXIT TRIGGERED: detailed rationale. This is the highest-priority section in the brief.
5. If WATCH (within 20% of breach): one-paragraph note
6. If HOLD: one-line confirmation

## Step 4: Generate the brief
Create `Investing Knowledge Base/04-Weekly Briefs/[YYYY-MM-DD] - Weekly Brief.md` with these sections in order:

### Section 1: Portfolio Overview
- Total cost basis (USD and NZD)
- Total current value
- Total return % (and per-position breakdown)
- FIF trajectory: current NZD cost basis vs $50k threshold

### Section 2: Exit Review
- Output of Step 3
- EXIT TRIGGERED items first, in red
- WATCH items second
- HOLD items as a compact table at the end

### Section 3: Macro Snapshot
- From Step 0 macro data
- One paragraph on rates, one on flows, one on FX
- NZD/USD context per investment-policy.md

### Section 4: Gap & Concentration Check
- Position bucket analysis (growth / theme / asymmetric, vs targets)
- Per-position size vs caps
- Cross-theme correlation analysis from Step 2
- Effective theme count
- Any ⚠️ breaches with rebalancing proposals

### Section 5: Theme Tracker
- Each active theme with the week's updates
- Status (🟢 active / 🟡 watching / ⚪ paused)
- New tickers under each theme

### Section 6: Inbox Insights This Week
- Summary of inbox items processed in Step 1
- Grouped by source tier
- Frequency flag if triggered

### Section 7: New Ideas (3-5 picks)
For each pick, all 7 funnel steps applied. Format:
- Conviction: HIGH / MEDIUM / LOW
- Bucket: growth compounder / theme play / asymmetric
- Bull thesis (1 sentence)
- Bear case (≥200 words, ≥400 if asymmetric)
- Entry zone: "buy zone within X% of current" (no false precision on dollars)
- Invalidation trigger (specific, dated, measurable)
- Dollar allocation proposal
- Data confidence: full / partial / data-gap

If a pick is asymmetric, include all 5 guardrails inline.
If a pick is a discovery position (Tier 3/4 exception), label it as such and include: bull case, kill condition, source tier justification, 6-month sunset date, and fee check confirmation.

### Section 8: Watchlist Update
- Prior picks: thesis check-in
- Insights from this week added to watchlist (per cooldown rule)
- Removals (with reason)

### Section 9: Weekly Allocation Table
- Total: $250
- Per-pick dollar amounts
- Conviction-weighted
- If low-conviction week: propose holding cash, deploy double next week
- Must respect bucket caps from investment-policy.md

### Section 10: This Week's Synthesis
- Highest-conviction pick + 2-sentence rationale
- What to pass on this week + 1-sentence reason
- This is the section that goes in the email body

### Section 11: Knowledge Graph Updates
- New connections added in Step 2
- Bullet list, brief

### Section 12: Trade Confirmation Prompt
- "Log trades in `ops/trades.md` via the GitHub app. Format: `Bought X.XX TICKER at $YY.YY` under a `### YYYY-MM-DD` heading. They'll be processed in next Monday's brief."

Write the brief to the working branch via API.

## Step 5: Update vault
All updates via API on the working branch:
- Append to `Investing Knowledge Base/04-Weekly Briefs/Brief Index.md`
- Update Watchlist with new picks (status: flagged or watching per cooldown)
- Update Theme Index dates
- Update `ops/processing-queue.md` (clear processed, add follow-ups)
- Create new stock notes in `Investing Knowledge Base/05-Stocks/` for fully researched picks
- Update `MOC - Stocks.md` if positions changed

## Step 7: Branch and PR
This step is split: branch creation happens BEFORE Steps 0–6 so all writes can target it. PR creation happens AFTER all writes complete.

### Step 7a (run first, before Step 0):
1. Get SHA of main: `GET https://api.github.com/repos/rubyosborne/long-term-investing-vault/git/ref/heads/main`
2. Create branch `claude/brief-YYYY-MM-DD` from that SHA: `POST https://api.github.com/repos/rubyosborne/long-term-investing-vault/git/refs` body `{"ref":"refs/heads/claude/brief-YYYY-MM-DD","sha":"<main-sha>"}`

All file writes in Steps 0–6 use this branch.

### Step 7b (run after Step 6):
3. Create PR: `POST https://api.github.com/repos/rubyosborne/long-term-investing-vault/pulls` body `{"title":"Weekly Investing Brief — YYYY-MM-DD","body":"<Section 10 + Exit Review summary>","head":"claude/brief-YYYY-MM-DD","base":"main"}`
4. Enable auto-merge on the PR.

If any API call fails: log to `ops/routine-log.md`, continue. Brief is not blocked by PR failure.

## Step 8: Email
Use the Gmail connector. To: ruby.osborne@gmail.com. Subject: "Weekly Investing Brief — YYYY-MM-DD".
Email body structure:
1. Portfolio Overview (from Section 1)
2. Exit Review summary (from Section 2)
3. This Week's Synthesis (from Section 10)
4. Link to the PR for the full brief

## Step 9: Log
Append to `ops/routine-log.md` (via API on the working branch): timestamp, status (success / partial / failed), data gaps if any, notable events.

## Failure handling
- If any single step fails: log it, continue, surface in routine-log.md and email body
- If routine cannot start (auth, etc.): the Friday health check (separate routine) will detect missing Monday brief and notify
