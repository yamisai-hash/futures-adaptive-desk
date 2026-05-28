"""
confluence_engine.py — turn a raw setup into a 0-100 confidence score.

The score is a transparent weighted sum of a few factors (higher-timeframe
bias, market structure, session quality, news proximity). Anything below the
``no_trade_threshold`` returns ``NO_TRADE`` and hard-blocks downstream.

Deliberately simple and explainable: the whole point of the project is to test
whether *these* factors predict outcomes, so the scoring must be auditable.
"""
from __future__ import annotations

from typing import Any, Dict, Union

DEFAULT_WEIGHTS = {
    "htf_bias": 0.30,
    "structure": 0.30,
    "session": 0.20,
    "news_guard": 0.20,
}
NO_TRADE_THRESHOLD = 50


def _factor_scores(signal: Dict[str, Any]) -> Dict[str, float]:
    """Map signal context to 0-1 factor scores.

    Uses whatever context the signal carries; missing context scores neutral
    (0.5) rather than guessing. Real desk fills these from htf_bias /
    session_strength / news guards.
    """
    ctx = signal.get("context", {})
    return {
        "htf_bias":   1.0 if ctx.get("htf_aligned") else (0.5 if ctx.get("htf_aligned") is None else 0.2),
        "structure":  float(ctx.get("structure_quality", 0.5)),
        "session":    {"london": 0.9, "ny": 0.9, "overlap": 1.0, "asia": 0.4}.get(ctx.get("session"), 0.5),
        "news_guard": 0.0 if ctx.get("news_within_60min") else 1.0,
    }


def score(signal: Dict[str, Any], weights: Dict[str, float] = None,
          threshold: int = NO_TRADE_THRESHOLD) -> Union[int, str]:
    """Return an int 0-100, or the string ``"NO_TRADE"`` if below threshold."""
    weights = weights or DEFAULT_WEIGHTS
    factors = _factor_scores(signal)
    raw = sum(factors[k] * weights.get(k, 0) for k in factors)
    value = round(raw * 100)
    return value if value >= threshold else "NO_TRADE"


def breakdown(signal: Dict[str, Any], weights: Dict[str, float] = None) -> Dict[str, Any]:
    """Same computation, but return the per-factor contributions (for the UI)."""
    weights = weights or DEFAULT_WEIGHTS
    factors = _factor_scores(signal)
    contrib = {k: round(factors[k] * weights.get(k, 0) * 100, 1) for k in factors}
    total = round(sum(contrib.values()))
    return {"factors": factors, "contributions": contrib, "score": total,
            "verdict": "NO_TRADE" if total < NO_TRADE_THRESHOLD else "TRADEABLE"}
