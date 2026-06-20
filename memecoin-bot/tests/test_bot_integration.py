"""End-to-end smoke test: run the bot against the mock feed for a moment."""

import asyncio

from bot.bot import TradingBot
from bot.config import Config


def test_bot_runs_against_mock_feed_and_trades(tmp_path):
    cfg = Config.load()  # defaults: mock feed
    cfg.trade_log_csv = str(tmp_path / "trades.csv")
    # Speed the synthetic market way up so plenty happens in a short window.
    cfg.feed.mock_new_token_interval_s = 0.05
    cfg.feed.mock_tick_interval_s = 0.02
    cfg.strategy.max_hold_seconds = 0.5
    cfg.validate()

    bot = TradingBot(cfg)
    asyncio.run(bot.run(max_runtime_s=2.0))

    # The bot should have opened and closed at least one position, and the
    # paper balance must remain a finite, sane number.
    assert len(bot.portfolio.closed) >= 1
    assert bot.broker.balance_sol >= 0
    # Every closed trade should have a recorded exit reason.
    assert all(t.reason is not None for t in bot.portfolio.closed)
