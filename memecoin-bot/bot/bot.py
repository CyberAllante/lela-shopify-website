"""The orchestrator: wires the feed, strategy, broker and portfolio together.

Event loop:
  * On a "new" token  -> ask the strategy whether to enter; if so, paper-buy and
    start watching that token's price.
  * On a "tick"       -> if we hold the token, ask the strategy whether to exit;
    if so, paper-sell, log it, and stop watching.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from .config import Config
from .engine import PaperBroker, Portfolio, SniperStrategy
from .engine.paper_broker import InsufficientFunds
from .feeds import build_feed
from .models import ExitReason, TokenEvent, TradeTick
from .trade_log import TradeLog


class TradingBot:
    def __init__(self, config: Config, logger: Optional[logging.Logger] = None):
        self.cfg = config
        self.log = logger or logging.getLogger("memecoin-bot")
        self.broker = PaperBroker(
            starting_balance_sol=config.broker.starting_balance_sol,
            fee_pct=config.broker.fee_pct,
            slippage_pct=config.broker.slippage_pct,
        )
        self.portfolio = Portfolio()
        self.strategy = SniperStrategy(config.strategy)
        self.feed = build_feed(config)
        self.trade_log = TradeLog(config.trade_log_csv)
        self._stop = asyncio.Event()

    def request_stop(self) -> None:
        self._stop.set()

    def snapshot(self) -> dict:
        """A JSON-serialisable view of live state for the web dashboard."""
        pf = self.portfolio
        start = self.cfg.broker.starting_balance_sol
        cash = self.broker.balance_sol

        open_positions = []
        open_value = 0.0
        for p in pf.open_positions:
            mark = p.last_price_sol or p.entry_price_sol
            value = p.token_amount * mark
            open_value += value
            open_positions.append(
                {
                    "symbol": p.symbol,
                    "mint": p.mint,
                    "entry_price_sol": p.entry_price_sol,
                    "last_price_sol": mark,
                    "token_amount": p.token_amount,
                    "cost_sol": p.cost_sol,
                    "value_sol": value,
                    "unrealized_pct": p.unrealized_pct(mark) * 100,
                    "age_seconds": p.age_seconds(),
                }
            )

        recent = []
        for t in reversed(pf.closed[-25:]):
            recent.append(
                {
                    "symbol": t.symbol,
                    "reason": t.reason.value,
                    "pnl_sol": t.pnl_sol,
                    "pnl_pct": t.pnl_pct * 100,
                    "hold_seconds": t.hold_seconds,
                    "closed_at": t.closed_at,
                }
            )

        equity = cash + open_value
        return {
            "running": not self._stop.is_set(),
            "feed": self.cfg.feed.source,
            "config": {
                "buy_amount_sol": self.cfg.strategy.buy_amount_sol,
                "take_profit_pct": self.cfg.strategy.take_profit_pct * 100,
                "stop_loss_pct": self.cfg.strategy.stop_loss_pct * 100,
                "trailing_stop_pct": self.cfg.strategy.trailing_stop_pct * 100,
                "max_hold_seconds": self.cfg.strategy.max_hold_seconds,
                "max_open_positions": self.cfg.strategy.max_open_positions,
            },
            "starting_balance_sol": start,
            "cash_sol": cash,
            "open_value_sol": open_value,
            "equity_sol": equity,
            "realized_pnl_sol": pf.realized_pnl_sol,
            "net_change_sol": equity - start,
            "net_change_pct": (equity / start - 1) * 100 if start else 0.0,
            "closed_count": len(pf.closed),
            "wins": pf.wins,
            "losses": pf.losses,
            "win_rate_pct": pf.win_rate * 100,
            "open_positions": open_positions,
            "recent_trades": recent,
        }

    async def run(self, max_runtime_s: Optional[float] = None) -> None:
        self.log.info(
            "Starting PAPER bot | feed=%s | start balance=%.4f SOL | "
            "buy=%.4f SOL | TP=%.0f%% SL=%.0f%% trail=%.0f%%",
            self.cfg.feed.source,
            self.cfg.broker.starting_balance_sol,
            self.cfg.strategy.buy_amount_sol,
            self.cfg.strategy.take_profit_pct * 100,
            self.cfg.strategy.stop_loss_pct * 100,
            self.cfg.strategy.trailing_stop_pct * 100,
        )

        deadline_task = None
        if max_runtime_s is not None:
            deadline_task = asyncio.create_task(self._deadline(max_runtime_s))

        try:
            async for kind, payload in self.feed.stream():
                if self._stop.is_set():
                    break
                if kind == "new":
                    await self._on_new_token(payload)  # type: ignore[arg-type]
                elif kind == "tick":
                    await self._on_tick(payload)  # type: ignore[arg-type]
        finally:
            if deadline_task is not None:
                deadline_task.cancel()
            await self._shutdown()

    async def _deadline(self, seconds: float) -> None:
        try:
            await asyncio.sleep(seconds)
            self.log.info("Max runtime reached (%.0fs); stopping.", seconds)
            self.request_stop()
        except asyncio.CancelledError:
            pass

    async def _on_new_token(self, event: TokenEvent) -> None:
        enter = self.strategy.should_enter(
            event,
            open_count=self.portfolio.open_count,
            balance_sol=self.broker.balance_sol,
            already_held=self.portfolio.has(event.mint),
        )
        if not enter:
            self.log.debug("Skip new token %s (%s)", event.symbol, event.mint[:8])
            return

        try:
            position = self.broker.buy(
                mint=event.mint,
                symbol=event.symbol,
                quoted_price_sol=event.price_sol,  # type: ignore[arg-type]
                spend_sol=self.cfg.strategy.buy_amount_sol,
            )
        except (InsufficientFunds, ValueError) as exc:
            self.log.warning("Buy rejected for %s: %s", event.symbol, exc)
            return

        self.portfolio.add(position)
        await self.feed.watch(event.mint)
        self.log.info(
            "BUY  %-6s %.4f SOL @ %.3e -> %.2f tokens | open=%d | cash=%.4f SOL",
            event.symbol,
            position.cost_sol,
            position.entry_price_sol,
            position.token_amount,
            self.portfolio.open_count,
            self.broker.balance_sol,
        )

    async def _on_tick(self, tick: TradeTick) -> None:
        position = self.portfolio.get(tick.mint)
        if position is None:
            return

        position.last_price_sol = tick.price_sol
        reason = self.strategy.check_exit(position, tick.price_sol)
        if reason is None:
            return

        trade = self.broker.sell(position, tick.price_sol, reason)
        self.portfolio.remove(tick.mint)
        self.portfolio.record_close(trade)
        self.trade_log.record(trade)
        await self.feed.unwatch(tick.mint)

        emoji = "PROFIT" if trade.pnl_sol > 0 else "LOSS  "
        self.log.info(
            "SELL %-6s %-13s %s %+.4f SOL (%+.1f%%) | held %.0fs | cash=%.4f SOL",
            trade.symbol,
            reason.value,
            emoji,
            trade.pnl_sol,
            trade.pnl_pct * 100,
            trade.hold_seconds,
            self.broker.balance_sol,
        )

    async def _shutdown(self) -> None:
        # Mark any still-open positions to nothing realized; report them as held.
        await self.feed.close()
        self.log.info(
            "\n%s",
            self.portfolio.summary(
                self.broker.balance_sol, self.cfg.broker.starting_balance_sol
            ),
        )
        if self.portfolio.open_count:
            self.log.info(
                "Note: %d position(s) still open at shutdown (value not realized).",
                self.portfolio.open_count,
            )
