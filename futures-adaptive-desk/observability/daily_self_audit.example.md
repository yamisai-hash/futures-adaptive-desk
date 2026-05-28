# Daily Self-Audit (example output)

Generated: 2026-05-28 01:46  *(illustrative)*

| Check | Status |
| --- | --- |
| Loop alive | OK (pid present, ticks advancing) |
| Bars source | OK (real bars; MultiIndex flatten applied) |
| Lifetime counters vs journal | OK (reconciled) |
| Kill switch | OK (disengaged) |
| Score validator | PARTIALLY_PREDICTIVE (n=20) |
| Governor readiness | 100% (holding; total_changes=0) |
| Stale modules | 1 (replay_learning) |
| Code drift since launch | none (restart_required=false) |

Severity legend: OK / NOTE / WARN / ALERT.
