# Safety Model — Futures Adaptive Desk

This is a **research/paper** system. The safety model exists so that an
always-on autonomous loop can never do something irreversible.

## Hard guarantees

1. **Paper-only by construction.** "Taking" a trade records a simulated entry.
   The (omitted) broker client refuses any non-demo endpoint. There is no code
   path to a live order in this showcase.
2. **Kill-switch defaults to engaged.** Nothing trades until it is explicitly
   cleared (`RiskState.kill_switch = False`).
3. **Gate stack runs in fixed order** (`risk_engine.evaluate`):
   kill-switch -> news window -> max trades/day -> daily drawdown -> loss-streak
   cooldown -> `NO_TRADE` score. First failing gate blocks and is logged.

## Limits (configurable, see `configs/desk_config.example.yaml`)

| Limit | Default |
| --- | --- |
| Max trades / day | 8 |
| Daily drawdown | -3.0 R |
| Loss-streak cooldown | after 3 consecutive losses |
| News window | block new entries within 60 min of high-impact events |

## Observability as safety

- A **daily self-audit** consolidates health checks (see
  `observability/daily_self_audit.example.md`).
- The runtime detects when its **own source changed since launch** and raises
  `restart_required` instead of running stale code — a real incident this caught
  in practice.

## Honesty constraints

- No live-profitability claims. Reported numbers are small paper results.
- Counters are reconciled against the real journal to prevent metric drift.
