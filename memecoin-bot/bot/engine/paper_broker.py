"""Simulated broker.

Holds a SOL balance and executes buys/sells against quoted prices, applying a
fee and slippage so simulated fills resemble real pump.fun trades. No network,
no real funds -- this is the safety boundary of the whole project.
"""

from __future__ import annotations

import time

from ..models import ClosedTrade, ExitReason, Position


class InsufficientFunds(Exception):
    pass


class PaperBroker:
    def __init__(self, starting_balance_sol: float, fee_pct: float, slippage_pct: float):
        self.starting_balance_sol = starting_balance_sol
        self.balance_sol = starting_balance_sol
        self.fee_pct = fee_pct
        self.slippage_pct = slippage_pct

    def buy(self, mint: str, symbol: str, quoted_price_sol: float, spend_sol: float) -> Position:
        """Spend `spend_sol` to open a position at a slippage/fee-adjusted price."""
        if quoted_price_sol <= 0:
            raise ValueError("quoted_price_sol must be > 0")
        if spend_sol <= 0:
            raise ValueError("spend_sol must be > 0")
        if spend_sol > self.balance_sol + 1e-12:
            raise InsufficientFunds(
                f"Need {spend_sol:.6f} SOL but only {self.balance_sol:.6f} available"
            )

        # Buyers pay up: slippage pushes the effective price higher.
        fill_price = quoted_price_sol * (1.0 + self.slippage_pct)
        fee = spend_sol * self.fee_pct
        sol_for_tokens = spend_sol - fee
        token_amount = sol_for_tokens / fill_price

        self.balance_sol -= spend_sol
        return Position(
            mint=mint,
            symbol=symbol,
            entry_price_sol=fill_price,
            token_amount=token_amount,
            cost_sol=spend_sol,
        )

    def sell(self, position: Position, quoted_price_sol: float, reason: ExitReason) -> ClosedTrade:
        """Close `position` at a slippage/fee-adjusted price and bank the proceeds."""
        if quoted_price_sol <= 0:
            raise ValueError("quoted_price_sol must be > 0")

        # Sellers receive less: slippage pushes the effective price lower.
        fill_price = quoted_price_sol * (1.0 - self.slippage_pct)
        gross = position.token_amount * fill_price
        fee = gross * self.fee_pct
        proceeds = gross - fee

        self.balance_sol += proceeds
        return ClosedTrade(
            mint=position.mint,
            symbol=position.symbol,
            entry_price_sol=position.entry_price_sol,
            exit_price_sol=fill_price,
            token_amount=position.token_amount,
            cost_sol=position.cost_sol,
            proceeds_sol=proceeds,
            opened_at=position.opened_at,
            closed_at=time.time(),
            reason=reason,
        )
