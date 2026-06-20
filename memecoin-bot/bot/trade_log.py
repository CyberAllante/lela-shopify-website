"""Append closed trades to a CSV file for later analysis."""

from __future__ import annotations

import csv
import os
from typing import Optional

from .models import ClosedTrade

_FIELDS = [
    "closed_at",
    "mint",
    "symbol",
    "reason",
    "entry_price_sol",
    "exit_price_sol",
    "token_amount",
    "cost_sol",
    "proceeds_sol",
    "pnl_sol",
    "pnl_pct",
    "hold_seconds",
]


class TradeLog:
    def __init__(self, path: Optional[str]):
        self.path = path
        if self.path and not os.path.exists(self.path):
            with open(self.path, "w", newline="", encoding="utf-8") as fh:
                csv.writer(fh).writerow(_FIELDS)

    def record(self, trade: ClosedTrade) -> None:
        if not self.path:
            return
        with open(self.path, "a", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(
                [
                    f"{trade.closed_at:.3f}",
                    trade.mint,
                    trade.symbol,
                    trade.reason.value,
                    f"{trade.entry_price_sol:.12f}",
                    f"{trade.exit_price_sol:.12f}",
                    f"{trade.token_amount:.6f}",
                    f"{trade.cost_sol:.6f}",
                    f"{trade.proceeds_sol:.6f}",
                    f"{trade.pnl_sol:.6f}",
                    f"{trade.pnl_pct:.4f}",
                    f"{trade.hold_seconds:.1f}",
                ]
            )
