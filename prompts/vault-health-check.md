# Vault Health Check — Sunday Routine

Runs Sunday 18:00 NZT. Use Sonnet.

## Repository Access
This routine has no direct repo access. ALL file reads and writes use the GitHub REST API.

Repository: `rubyosborne/long-term-investing-vault`
Auth: use the same GitHub PAT as defined in `prompts/weekly-brief.md` (Repository Access section).

API patterns:
- Read file: `GET https://api.github.com/repos/rubyosborne/long-term-investing-vault/contents/{path}` — response includes base64 `content` and `sha`. Decode content for reading; keep sha for updates.
- List directory: `GET https://api.github.com/repos/rubyosborne/long-term-investing-vault/contents/{dirpath}` — returns array of file metadata.
- Write file: `PUT https://api.github.com/repos/rubyosborne/long-term-investing-vault/contents/{path}` — body `{"message":"...","content":"<base64>","branch":"<branch>","sha":"<existing-sha-if-update>"}`.

URL-encode paths with spaces (e.g. `Investing%20Knowledge%20Base/05-Stocks`).

## Pre-flight
Read these files via API:
1. `CLAUDE.md`
2. `self/identity.md`, `self/investment-policy.md`, `self/style.md`
3. `Investing Knowledge Base/CLAUDE.md`
4. `ops/routine-log.md`
5. `ops/processing-queue.md`
6. `ops/inbox.md`
7. List and read all files in `Investing Knowledge Base/05-Stocks/`
8. List and read all files in `Investing Knowledge Base/03-Themes/`
9. `Investing Knowledge Base/06-Watchlist/Current Watchlist.md`
10. `Investing Knowledge Base/07-Portfolio/Holdings.md`
11. `Investing Knowledge Base/04-Weekly Briefs/Brief Index.md`
12. `Investing Knowledge Base/00-Meta/MOC - Stocks.md`

## Step 1: Branch creation
1. Get SHA of main: `GET /repos/.../git/ref/heads/main`
2. Create branch `claude/health-YYYY-MM-DD` from that SHA
3. All writes target this branch

## Step 2: Monday brief verification
Check `ops/routine-log.md` for an entry dated the previous Monday (or most recent Monday).
- If present: note status (success/partial/failed) and any data gaps logged
- If missing: flag as **CRITICAL** — the Monday brief did not run. Include this prominently in the health report and the Gmail draft.

## Step 3: Wiki link integrity
Scan every `.md` file in `Investing Knowledge Base/` for `[[wiki links]]`.
For each link:
- Check that a matching file exists (e.g. `[[GOOGL]]` should match `05-Stocks/GOOGL.md`, `[[AI Infrastructure]]` should match `03-Themes/AI Infrastructure.md`)
- If no match: log as broken link
- Fix obvious cases (typos, missing files that should exist) on the branch. Flag ambiguous ones in the report.

## Step 4: Stock note validation
For each file in `Investing Knowledge Base/05-Stocks/`:
- **Invalidation trigger**: must be present and specific (not vague like "if thesis breaks"). Flag if missing.
- **Bucket assignment**: must be one of: Growth compounder / Theme play / Asymmetric bet. Flag if missing.
- **Entry date** (Added field): must be present. Flag if missing.
- **Position size**: required only if the ticker appears in Holdings.md. Skip this check for watchlist-only stocks.

## Step 5: Theme note validation
For each file in `Investing Knowledge Base/03-Themes/` (excluding Theme Index.md):
- **Status**: must be one of: Active / Watching / Paused (plain text, not emojis). Flag if missing or uses emoji format.
- **Last Updated date**: must be present and within 30 days of today. Flag if stale.
- **Linked tickers**: must reference at least one stock note. Flag orphaned themes.

## Step 6: Processing queue review
Read `ops/processing-queue.md`. For each item:
- If it references a specific date (e.g. "Review after earnings May 4") and that date has passed: flag as overdue.
- If an item has been on the queue for >14 days: flag as stale.

## Step 7: Watchlist hygiene
Read `Investing Knowledge Base/06-Watchlist/Current Watchlist.md`. For each entry:
- If the "Key Catalyst" references a date that has passed: flag as "catalyst expired — needs update or removal."
- If an entry has been in "Flagged" status for >4 weeks: flag for promotion to "Watching" or removal.

## Step 8: Inbox check
Read `ops/inbox.md`.
- If there are entries older than 7 days: flag as "unprocessed inbox items — should have been caught by Monday brief."

## Step 9: Orphan detection
Cross-reference:
- `MOC - Stocks.md` against actual files in `05-Stocks/`. Flag any mismatches (listed but no file, or file exists but not listed).
- `Theme Index.md` against actual files in `03-Themes/`. Same check.
- Holdings.md tickers against stock notes. Every held ticker must have a stock note.

## Step 10: Generate health report
Write `ops/health-YYYY-MM-DD.md` to the branch with:

```
# Vault Health Check — YYYY-MM-DD

## Summary
- Status: HEALTHY / ISSUES FOUND / CRITICAL
- Stock notes checked: X
- Theme notes checked: X
- Wiki links checked: X
- Issues found: X
- Auto-fixed: X

## Critical
(Monday brief missing, broken holdings references, etc.)

## Issues
(Broken links, missing fields, stale entries — itemised)

## Auto-fixed
(What was corrected on this branch)

## Info
(Non-actionable observations)
```

## Step 11: PR and merge
- Create PR: `POST /repos/.../pulls` with title "Vault Health Check — YYYY-MM-DD", body = summary section from the health report, head = `claude/health-YYYY-MM-DD`, base = `main`.
- If the PR contains only mechanical fixes (link corrections, date updates, field additions): merge immediately via `PUT /repos/.../pulls/{number}/merge` with `merge_method: squash`.
- If the PR contains substantive changes or flagged items needing Ruby's review: leave open for review.

## Step 12: Gmail notification
Create a Gmail draft to ruby.osborne@gmail.com.
- Subject: "Vault Health Check — YYYY-MM-DD"
- Body: the Summary and Critical sections from the health report. If status is HEALTHY, keep it to one line ("All clear, no issues found.").
- Note: the Gmail connector creates drafts only. Ruby will need to find it in Drafts and send.

## Failure handling
- If any step fails: log the failure, continue to the next step, include it in the health report.
- If the routine cannot connect to the repo at all: create a Gmail draft with subject "HEALTH CHECK FAILED" and the error details.
