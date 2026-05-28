# Architecture — Futures Adaptive Desk

> Representative/cleaned subset of a larger private system. Paper-only.

## Tick lifecycle (~5 min)

```mermaid
flowchart TD
    A[Market data: bars] --> B[HTF bias 4H/1H/30M/5M]
    B --> C[Session + volatility classifier]
    C --> D[signal_engine: rule-based scan]
    D --> E[confluence_engine: score 0-100 / NO_TRADE]
    E --> F{risk_engine gate stack}
    F -->|TAKE| G[Paper execution: simulated fill]
    F -->|BLOCK| H[Shadow evaluator: log 'would-have-traded']
    G --> J[Journal + realized R]
    H --> J
    J --> K[score_validator: did score predict R?]
    K --> L[Adaptive governor: conservative self-tune]
    L -. recommended weights .-> E
    J --> M[Dashboards + daily self-audit]
```

![Architecture](../assets/architecture.png)

## Modules in this showcase

| File | Responsibility |
| --- | --- |
| `src/signal_engine.py` | Rule-based, explainable setup detection (3 sample strategies) |
| `src/confluence_engine.py` | Transparent 0-100 weighted score; `NO_TRADE` below threshold |
| `src/risk_engine.py` | Gate stack: kill-switch, news window, trade cap, drawdown, cooldown |
| `src/score_validator.py` | Score -> outcome correlation + honest predictiveness verdict |
| `src/futures_lane.py` | One-tick orchestrator wiring the above together |

## What is intentionally *not* here

The full runtime adds higher-timeframe bias computation, a live data provider,
position management (break-even/trail), SQLite bar persistence, a shadow
evaluator, the self-tuning governor, and Streamlit dashboards. Those are
summarized in the diagram and screenshots but kept out of this public subset.

## Design principles

- **Explainable over clever** — every signal has a reason; the score is a plain weighted sum.
- **Measure before trusting** — see [`learning_loop.md`](learning_loop.md).
- **Safe by default** — see [`safety_model.md`](safety_model.md).
