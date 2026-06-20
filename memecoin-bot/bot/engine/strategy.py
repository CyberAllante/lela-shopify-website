"""Entry and exit decision logic.

The strategy is deliberately simple and rule-based so it is easy to test and
reason about:

  ENTRY  -- snipe a freshly launched token if we have room and cash, and its
            initial price is within the configured band.
  EXIT   -- close a position when ANY of these fire:
              * take-profit target hit
              * stop-loss breached
              * trailing stop triggered (price fell X% from its peak)
              * max hold time exceeded

Pure decision functions (no I/O) keep the trading rules unit-testable.
"""

from __future__ import annotations

from typing import Optional

from ..config import StrategyConfig
from ..models import ExitReason, Position, TokenEvent


class SniperStrategy:
    def __init__(self, config: StrategyConfig):
        self.cfg = config

    def should_enter(
        self,
        event: TokenEvent,
        open_count: int,
        balance_sol: float,
        already_held: bool,
    ) -> bool:
        """Decide whether to open a position in a newly launched token."""
        if already_held:
            return False
        if event.price_sol is None or event.price_sol <= 0:
            return False  # need a price to size the trade
        if open_count >= self.cfg.max_open_positions:
            return False
        if balance_sol < self.cfg.buy_amount_sol:
            return False
        if not (self.cfg.min_entry_price_sol <= event.price_sol <= self.cfg.max_entry_price_sol):
            return False
        return True

    def check_exit(
        self,
        position: Position,
        current_price_sol: float,
        now: Optional[float] = None,
    ) -> Optional[ExitReason]:
        """Return the reason to exit, or None to keep holding.

        Note: this also updates the position's trailing peak as a side effect,
        which is the natural place to track it as prices stream in.
        """
        # Update the running peak for the trailing stop.
        if current_price_sol > position.peak_price_sol:
            position.peak_price_sol = current_price_sol

        ret = position.unrealized_pct(current_price_sol)

        # Take profit.
        if ret >= self.cfg.take_profit_pct:
            return ExitReason.TAKE_PROFIT

        # Hard stop loss.
        if ret <= -self.cfg.stop_loss_pct:
            return ExitReason.STOP_LOSS

        # Trailing stop: only meaningful once we're up off entry a bit and the
        # trailing stop is enabled.
        if self.cfg.trailing_stop_pct > 0 and position.peak_price_sol > position.entry_price_sol:
            drawdown_from_peak = (
                position.peak_price_sol - current_price_sol
            ) / position.peak_price_sol
            if drawdown_from_peak >= self.cfg.trailing_stop_pct:
                return ExitReason.TRAILING_STOP

        # Time-based exit.
        if position.age_seconds(now) >= self.cfg.max_hold_seconds:
            return ExitReason.MAX_HOLD

        return None
