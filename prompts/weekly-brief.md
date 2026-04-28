# Weekly Investing Brief — Routine Prompt

You are running Ruby Osborne's weekly investing brief on Monday at 17:00 NZT. Use Opus.

## Pre-flight
Read in this order:
1. /CLAUDE.md
2. /self/identity.md, methodology.md, style.md, investment-policy.md
3. /Investing Knowledge Base/CLAUDE.md
4. /Investing Knowledge Base/Home.md
5. /Investing Knowledge Base/03-Themes/Theme Index.md
6. /Investing Knowledge Base/06-Watchlist/Current Watchlist.md
7. /Investing Knowledge Base/07-Portfolio/Holdings.md
8. /Investing Knowledge Base/04-Weekly Briefs/Brief Index.md
9. /ops/processing-queue.md
10. /ops/inbox.md
11. Every file in /Investing Knowledge Base/05-Stocks/
12. Every file in /Investing Knowledge Base/03-Themes/

## Step 0: Refresh data
Run `python scripts/fetch_prices.py`. Run `python scripts/fetch_macro.py`. If either fails, log the failure to ops/routine-log.md and continue. The brief reports data gaps but does not abort.

## Step 1: Reduce inbox
Read /ops/inbox.md. For each entry:
- Identify type (stock insight, theme observation, macro, trade confirmation, other)
- Identify source tier (1-4 per investment-policy.md)
- Apply the 48-hour cooldown rule. Insights with source tier ≥3 submitted Wednesday or later are watchlist-only this week.
- Route to the destination's Updates Log with: date, source tier, content
- Track frequency: if >5 insights this week, set a flag for the brief

After processing, archive /ops/inbox.md to /ops/inbox-archive/YYYY-MM-DD.md and reset /ops/inbox.md to a clean template.

## Step 2: Reflect (graph pass)
- Scan every stock note for unlinked theme connections. Add wiki links.
- Scan every theme note for unlinked ticker mentions. Add wiki links.
- Compute cross-theme correlation: any ticker appearing in 2+ themes is flagged.
- Compute effective theme count (independent themes after correlation adjustment).
- Log every new connection added to use in Step 4 Section 11.

## Step 3: Exit review (run before generating ideas)
For every position in Holdings.md:
1. Read the invalidation trigger from the stock note
2. Compare current price and fundamentals (from ops/prices.md and recent inbox/news) against the trigger
3. Classify: EXIT TRIGGERED / WATCH / HOLD
4. If EXIT TRIGGERED: detailed rationale. This is the highest-priority section in the brief.
5. If WATCH (within 20% of breach): one-paragraph note
6. If HOLD: one-line confirmation

## Step 4: Generate the brief
Create /Investing Knowledge Base/04-Weekly Briefs/[YYYY-MM-DD] - Weekly Brief.md with these sections in order:

### Section 1: Portfolio Overview
- Pulled from /ops/portfolio-overview.md
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
- From ops/macro.md
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
- "Reply with trades placed in the format: 'Bought X.XX TICKER at $YY.YY on YYYY-MM-DD'"

## Step 5: Generate .docx
Use the docx skill to render the brief markdown to a .docx file at `/tmp/Weekly Investing Brief - YYYY-MM-DD.docx`. This file is for email attachment. It is not committed (see .gitignore).

## Step 6: Update vault
- Append to /Investing Knowledge Base/04-Weekly Briefs/Brief Index.md
- Update Watchlist with new picks (status: flagged or watching per cooldown)
- Update Theme Index dates
- Update /ops/processing-queue.md (clear processed, add follow-ups)
- Create new stock notes in /Investing Knowledge Base/05-Stocks/ for fully researched picks
- Update MOC - Stocks.md if positions changed

## Step 7: Commit and PR
This routine runs in a cloud environment — use the GitHub REST API, not local git.

Requires: `GITHUB_TOKEN` secret set in this routine (Personal Access Token with `repo` scope — generate at github.com/settings/tokens).

1. Get current SHA of main:
   `GET https://api.github.com/repos/rubyosborne/long-term-investing-vault/git/ref/heads/main`

2. Create branch `claude/brief-YYYY-MM-DD` from that SHA:
   `POST https://api.github.com/repos/rubyosborne/long-term-investing-vault/git/refs`
   Body: `{"ref":"refs/heads/claude/brief-YYYY-MM-DD","sha":"<sha-from-step-1>"}`

3. For each file created or modified in Steps 1–6, push to the branch via the Contents API:
   `PUT https://api.github.com/repos/rubyosborne/long-term-investing-vault/contents/{filepath}`
   Body: `{"message":"Weekly brief YYYY-MM-DD","content":"<base64-encoded-content>","branch":"claude/brief-YYYY-MM-DD","sha":"<existing-file-sha-if-updating>"}`

4. Create PR:
   `POST https://api.github.com/repos/rubyosborne/long-term-investing-vault/pulls`
   - Title: "Weekly Investing Brief — YYYY-MM-DD"
   - Body: Section 10 (Synthesis) + Exit Review summary if EXIT TRIGGERED
   - Head: `claude/brief-YYYY-MM-DD` → Base: `main`

5. Enable auto-merge on the PR.

All requests must include header: `Authorization: Bearer $GITHUB_TOKEN`

If GITHUB_TOKEN is missing or any API call fails: log to ops/routine-log.md, continue to Step 8, and include a PR failure note in the email body. The brief is not blocked by a PR failure.

## Step 8: Email
Use the Gmail connector. To: ruby.osborne@gmail.com. Subject: "Weekly Investing Brief — YYYY-MM-DD".
Email body structure:
1. Portfolio Overview (from Section 1)
2. Exit Review summary (from Section 2)
3. This Week's Synthesis (from Section 10)
4. "See attached for full brief"
Attach: /tmp/Weekly Investing Brief - YYYY-MM-DD.docx

## Step 9: Log
Append to /ops/routine-log.md: timestamp, status (success / partial / failed), data gaps if any, notable events.

## Failure handling
- If any single step fails: log it, continue, surface in routine-log.md and email body
- If routine cannot start (auth, etc.): the Sunday health check (separate routine) will detect missing Monday brief and notify
