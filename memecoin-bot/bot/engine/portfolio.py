"""Tracks open positions and a history of closed trades, plus summary stats."""

from __future__ import annotations

from typing import Dict, List, Optional

from ..models import ClosedTrade, Position


class Portfolio:
    def __init__(self) -> None:
        self._open: Dict[str, Position] = {}
        self.closed: List[ClosedTrade] = []

    @property
    def open_positions(self) -> List[Position]:
        return list(self._open.values())

    @property
    def open_count(self) -> int:
        return len(self._open)

    def has(self, mint: str) -> bool:
        return mint in self._open

    def get(self, mint: str) -> Optional[Position]:
        return self._open.get(mint)

    def add(self, position: Position) -> None:
        self._open[position.mint] = position

    def remove(self, mint: str) -> Optional[Position]:
        return self._open.pop(mint, None)

    def record_close(self, trade: ClosedTrade) -> None:
        self.closed.append(trade)

    # ----- reporting -----------------------------------------------------

    @property
    def realized_pnl_sol(self) -> float:
        return sum(t.pnl_sol for t in self.closed)

    @property
    def wins(self) -> int:
        return sum(1 for t in self.closed if t.pnl_sol > 0)

    @property
    def losses(self) -> int:
        return sum(1 for t in self.closed if t.pnl_sol <= 0)

    @property
    def win_rate(self) -> float:
        if not self.closed:
            return 0.0
        return self.wins / len(self.closed)

    def summary(self, balance_sol: float, starting_balance_sol: float) -> str:
        total = len(self.closed)
        equity = balance_sol  # open positions are excluded; they're marked at cost
        lines = [
            "===== Paper Trading Summary =====",
            f"Closed trades : {total}  (wins {self.wins} / losses {self.losses}, "
            f"win rate {self.win_rate:.0%})",
            f"Realized PnL  : {self.realized_pnl_sol:+.6f} SOL",
            f"Open positions: {self.open_count}",
            f"Cash balance  : {balance_sol:.6f} SOL "
            f"(started {starting_balance_sol:.6f} SOL)",
            f"Net change    : {equity - starting_balance_sol:+.6f} SOL "
            f"({(equity / starting_balance_sol - 1) * 100:+.2f}% of starting cash)",
        ]
        return "\n".join(lines)
