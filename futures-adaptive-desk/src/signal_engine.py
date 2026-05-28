"""
signal_engine.py — rule-based setup detection.

Representative showcase module. The production desk pulls live bars through a
data provider and runs ~11 explainable strategies; here we keep three clean,
self-contained detectors so the *shape* of the logic is reviewable without the
full runtime. Every signal carries a human-readable ``reason`` — that is what
makes the downstream score -> outcome analysis interpretable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class Bar:
    ts: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


def _ema(values: Sequence[float], period: int) -> Optional[float]:
    if len(values) < period:
        return None
    k = 2 / (period + 1)
    ema = values[0]
    for v in values[1:]:
        ema = v * k + ema * (1 - k)
    return ema


def _vwap(bars: Sequence[Bar]) -> Optional[float]:
    num = sum(((b.high + b.low + b.close) / 3) * (b.volume or 1) for b in bars)
    den = sum((b.volume or 1) for b in bars)
    return num / den if den else None


def detect_vwap_reclaim(bars: Sequence[Bar], instrument: str) -> Optional[Dict[str, Any]]:
    """Price dips below VWAP then closes back above it = long reclaim."""
    if len(bars) < 5:
        return None
    vwap = _vwap(bars)
    if vwap is None:
        return None
    prev, last = bars[-2], bars[-1]
    if prev.close < vwap <= last.close:
        return {"strategy": "vwap_reclaim", "instrument": instrument, "side": "long",
                "reason": "close reclaimed VWAP after dip below"}
    return None


def detect_ema_continuation(bars: Sequence[Bar], instrument: str) -> Optional[Dict[str, Any]]:
    """Pullback to fast EMA in the direction of the slow EMA = continuation."""
    closes = [b.close for b in bars]
    fast, slow = _ema(closes, 9), _ema(closes, 21)
    if fast is None or slow is None:
        return None
    side = "long" if fast > slow else "short"
    return {"strategy": "ema_continuation", "instrument": instrument, "side": side,
            "reason": f"fast/slow EMA aligned ({side})"}


def detect_liquidity_sweep(bars: Sequence[Bar], instrument: str) -> Optional[Dict[str, Any]]:
    """Wick takes prior swing high/low then closes back inside = stop sweep."""
    if len(bars) < 6:
        return None
    swing_high = max(b.high for b in bars[-6:-1])
    last = bars[-1]
    if last.high > swing_high and last.close < swing_high:
        return {"strategy": "liquidity_sweep", "instrument": instrument, "side": "short",
                "reason": "swept prior swing high, closed back inside"}
    return None


DETECTORS = (detect_vwap_reclaim, detect_ema_continuation, detect_liquidity_sweep)


def scan_signals(instrument: str = "MES", bars: Optional[Sequence[Bar]] = None) -> List[Dict[str, Any]]:
    """Run every detector and return the setups found.

    In the showcase, calling without ``bars`` returns ``[]`` (no synthetic
    fabrication). The production version supplies freshly fetched bars.
    """
    if not bars:
        return []
    out: List[Dict[str, Any]] = []
    for detect in DETECTORS:
        sig = detect(bars, instrument)
        if sig:
            out.append(sig)
    return out
