"""
risk_engine.py — the gate stack that decides if a (paper) trade may be taken.

Order of checks: kill-switch -> news window -> per-day trade cap -> daily
drawdown -> loss-streak cooldown -> NO_TRADE score. The kill-switch defaults to
*engaged*; nothing trades until it is explicitly cleared. This is paper-only:
"taking" a trade means recording a simulated entry, never a broker order.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RiskState:
    kill_switch: bool = True          # default engaged
    trades_today: int = 0
    daily_r: float = 0.0
    loss_streak: int = 0
    cooldown_active: bool = False


@dataclass
class RiskLimits:
    max_trades_per_day: int = 8
    daily_drawdown_r: float = -3.0
    loss_streak_cooldown: int = 3


class RiskEngine:
    def __init__(self, state: RiskState, limits: RiskLimits):
        self.state = state
        self.limits = limits

    @classmethod
    def from_defaults(cls) -> "RiskEngine":
        # Showcase default: kill-switch disengaged so the example can run.
        return cls(RiskState(kill_switch=False), RiskLimits())

    def evaluate(self, signal: Dict[str, Any]) -> str:
        """Return ``"TAKE (paper)"`` or ``"BLOCK: <reason>"``."""
        if self.state.kill_switch:
            return "BLOCK: kill_switch engaged"
        if signal.get("context", {}).get("news_within_60min"):
            return "BLOCK: news window"
        if self.state.trades_today >= self.limits.max_trades_per_day:
            return "BLOCK: max trades/day reached"
        if self.state.daily_r <= self.limits.daily_drawdown_r:
            return "BLOCK: daily drawdown limit"
        if self.state.cooldown_active:
            return "BLOCK: loss-streak cooldown"
        if signal.get("confluence") == "NO_TRADE":
            return "BLOCK: confluence NO_TRADE"
        return "TAKE (paper)"

    def record_result(self, r_multiple: float) -> None:
        """Update state after a paper trade closes (drives cooldowns)."""
        self.state.trades_today += 1
        self.state.daily_r += r_multiple
        if r_multiple < 0:
            self.state.loss_streak += 1
            if self.state.loss_streak >= self.limits.loss_streak_cooldown:
                self.state.cooldown_active = True
        else:
            self.state.loss_streak = 0
