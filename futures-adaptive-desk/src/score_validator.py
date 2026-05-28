"""
score_validator.py — the heart of the project.

Given closed paper trades that each carry the confluence score they had *at
signal time* plus their realized R, this answers one question: did higher
scores actually lead to better outcomes? It buckets by score, computes
per-bucket win rate / average R, and a rank correlation, then emits an honest
verdict (it will say PARTIALLY_PREDICTIVE / NOT_PREDICTIVE when that is true).

No external deps — the rank correlation is implemented inline.
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence

BUCKETS = [(0, 39), (40, 49), (50, 59), (60, 69), (70, 100)]


def _spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Spearman rank correlation; returns 0.0 if undefined."""
    n = len(xs)
    if n < 3:
        return 0.0

    def ranks(vals: Sequence[float]) -> List[float]:
        order = sorted(range(n), key=lambda i: vals[i])
        rk = [0.0] * n
        for pos, idx in enumerate(order):
            rk[idx] = pos + 1
        return rk

    rx, ry = ranks(xs), ranks(ys)
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return round(1 - (6 * d2) / (n * (n * n - 1)), 3)


def _bucket(score: int) -> str:
    for lo, hi in BUCKETS:
        if lo <= score <= hi:
            return f"{lo}-{hi}"
    return "other"


def validate(closed_trades: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Return bucket stats + rank correlation + an honest verdict."""
    scored = [t for t in closed_trades if isinstance(t.get("confluence_score"), (int, float))]
    if not scored:
        return {"sample_size": 0, "overall_verdict": "INCONCLUSIVE",
                "note": "no scored trades yet"}

    buckets: Dict[str, Dict[str, Any]] = {}
    for t in scored:
        b = _bucket(int(t["confluence_score"]))
        d = buckets.setdefault(b, {"n": 0, "r_sum": 0.0, "wins": 0})
        d["n"] += 1
        d["r_sum"] += float(t.get("r", 0))
        d["wins"] += 1 if t.get("result") == "win" else 0
    for d in buckets.values():
        d["avg_r"] = round(d["r_sum"] / d["n"], 2)
        d["win_rate"] = round(d["wins"] / d["n"], 3)
        d.pop("r_sum")

    rc = _spearman([t["confluence_score"] for t in scored],
                   [t.get("r", 0) for t in scored])
    predictive = rc >= 0.3
    verdict = ("PREDICTIVE" if predictive
               else "PARTIALLY_PREDICTIVE" if rc > 0
               else "NOT_PREDICTIVE")

    return {
        "sample_size": len(scored),
        "bucket_stats": buckets,
        "rank_correlation": rc,
        "scoring_predictive": predictive,
        "overall_verdict": verdict,
        "note": "Honest read-out; small samples are reported as such. "
                "Weights are not retuned until the sample is large enough.",
    }
