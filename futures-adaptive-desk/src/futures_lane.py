"""
futures_lane.py — one paper tick, end to end.

This is the simplified orchestrator that ties the showcase modules together in
the same order the production desk uses:

    scan -> score -> gate (risk) -> (paper) record -> learn

The production loop runs this every ~5 minutes, persists state to JSON/SQLite,
manages open positions, and refreshes dashboards. Here we keep just enough to
make the control flow legible. Paper-only; nothing here can place a real order.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import confluence_engine as confluence
import signal_engine as signals
from risk_engine import RiskEngine
from score_validator import validate


def tick(instrument: str = "MES",
         bars: Optional[Sequence[signals.Bar]] = None,
         risk: Optional[RiskEngine] = None) -> Dict[str, Any]:
    """Run a single paper tick and return a structured result."""
    risk = risk or RiskEngine.from_defaults()
    found = signals.scan_signals(instrument=instrument, bars=bars)

    decisions: List[Dict[str, Any]] = []
    for sig in found:
        sig["confluence"] = confluence.score(sig)
        verdict = risk.evaluate(sig)
        decisions.append({
            "strategy": sig["strategy"],
            "side": sig["side"],
            "confluence": sig["confluence"],
            "decision": verdict,
            "reason": sig.get("reason"),
        })

    taken = [d for d in decisions if d["decision"].startswith("TAKE")]
    return {
        "instrument": instrument,
        "n_signals": len(found),
        "n_taken": len(taken),
        "decisions": decisions,
        "stage": "OPEN_POSITION" if taken else ("NO_CANDIDATE" if not found else "BLOCKED"),
    }


def run_learning_review(closed_trades: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Convenience wrapper: score -> outcome validation over closed trades."""
    return validate(closed_trades)


if __name__ == "__main__":
    # No live bars in the showcase -> NO_CANDIDATE is the honest result.
    print(tick("MES"))
