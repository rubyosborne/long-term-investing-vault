# Vault Health Check — Sunday Routine

Runs Sunday 18:00 NZT. Use Sonnet.

## Tasks
1. Run /reflect (or equivalent) on the vault — find broken wiki links, orphan notes, stale theme entries
2. Check that /ops/routine-log.md has an entry for the previous Monday's brief
   - If missing: this means the brief routine failed silently last week
   - Email Ruby: "Last week's Monday brief did not run. Investigate."
3. Validate all stock notes have:
   - An invalidation trigger
   - A bucket assignment (growth/theme/asymmetric)
   - An entry date
   - A position size
4. Validate all theme notes have:
   - A status (🟢 / 🟡 / ⚪)
   - Last updated date within 30 days
5. Generate a health report at /ops/health-YYYY-MM-DD.md
6. If issues found: open PR `claude/health-YYYY-MM-DD` with fixes for mechanical issues, flag substantive ones to Ruby
