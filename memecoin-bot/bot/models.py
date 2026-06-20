"""Core data models shared across the bot.

All prices are expressed in SOL per token unless noted otherwise. Keeping a
single, well-documented unit convention avoids the classic trading-bot bug of
mixing quote currencies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ExitReason(str, Enum):
    """Why a position was closed. Useful for post-run analytics."""

    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    TRAILING_STOP = "trailing_stop"
    MAX_HOLD = "max_hold"
    MANUAL = "manual"


@dataclass
class TokenEvent:
    """A newly observed token launch."""

    mint: str
    symbol: str
    name: str
    # First observed price in SOL/token. May be None if not yet known.
    price_sol: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    source: str = "unknown"


@dataclass
class TradeTick:
    """A price observation for a token we are tracking."""

    mint: str
    price_sol: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class Position:
    """An open paper position in a single token."""

    mint: str
    symbol: str
    entry_price_sol: float
    token_amount: float
    # SOL actually spent to open (including fees/slippage).
    cost_sol: float
    opened_at: float = field(default_factory=time.time)
    # Highest price seen since entry, used for the trailing stop.
    peak_price_sol: float = 0.0

    def __post_init__(self) -> None:
        if self.peak_price_sol <= 0:
            self.peak_price_sol = self.entry_price_sol

    def unrealized_pct(self, current_price_sol: float) -> float:
        """Return the unrealized return as a fraction (0.25 == +25%)."""
        if self.entry_price_sol <= 0:
            return 0.0
        return (current_price_sol - self.entry_price_sol) / self.entry_price_sol

    def age_seconds(self, now: Optional[float] = None) -> float:
        return (now or time.time()) - self.opened_at


@dataclass
class ClosedTrade:
    """A completed round-trip trade, recorded for reporting."""

    mint: str
    symbol: str
    entry_price_sol: float
    exit_price_sol: float
    token_amount: float
    cost_sol: float
    proceeds_sol: float
    opened_at: float
    closed_at: float
    reason: ExitReason

    @property
    def pnl_sol(self) -> float:
        return self.proceeds_sol - self.cost_sol

    @property
    def pnl_pct(self) -> float:
        if self.cost_sol <= 0:
            return 0.0
        return self.pnl_sol / self.cost_sol

    @property
    def hold_seconds(self) -> float:
        return self.closed_at - self.opened_at
