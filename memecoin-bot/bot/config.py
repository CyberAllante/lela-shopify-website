"""Configuration loading and validation.

Settings come from a YAML file (see config.yaml) with optional overrides from
environment variables. Everything has a sensible, conservative default so the
bot is safe to run in paper mode out of the box.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - yaml is optional for defaults
    yaml = None


@dataclass
class StrategyConfig:
    # SOL spent per new-coin entry.
    buy_amount_sol: float = 0.05
    # Take profit once unrealized return reaches this fraction (0.5 == +50%).
    take_profit_pct: float = 0.5
    # Hard stop loss (0.3 == -30%).
    stop_loss_pct: float = 0.3
    # Trailing stop: exit if price falls this fraction below the peak.
    # Set to 0 to disable.
    trailing_stop_pct: float = 0.25
    # Force-exit a position after this many seconds regardless of price.
    max_hold_seconds: float = 600.0
    # Don't open a new position if we already hold this many.
    max_open_positions: int = 5
    # Skip entries whose initial price is outside this band (SOL/token).
    min_entry_price_sol: float = 0.0
    max_entry_price_sol: float = float("inf")


@dataclass
class BrokerConfig:
    # Starting paper balance in SOL.
    starting_balance_sol: float = 1.0
    # Per-trade fee as a fraction (pump.fun charges ~1%).
    fee_pct: float = 0.01
    # Simulated slippage applied to fills as a fraction.
    slippage_pct: float = 0.02


@dataclass
class FeedConfig:
    # "mock" runs fully offline with a synthetic market.
    # "pumpportal" connects to the real pump.fun data stream.
    source: str = "mock"
    pumpportal_url: str = "wss://pumpportal.fun/api/data"
    # Mock-feed knobs.
    mock_new_token_interval_s: float = 2.0
    mock_tick_interval_s: float = 0.5
    mock_seed: Optional[int] = 42


@dataclass
class Config:
    mode: str = "paper"  # only "paper" is supported; live trading is intentionally absent
    log_level: str = "INFO"
    trade_log_csv: str = "trades.csv"
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    broker: BrokerConfig = field(default_factory=BrokerConfig)
    feed: FeedConfig = field(default_factory=FeedConfig)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        data: Dict[str, Any] = {}
        if path and os.path.exists(path):
            if yaml is None:
                raise RuntimeError(
                    "PyYAML is required to read a config file. Install it with "
                    "`pip install pyyaml` or run without a config path to use defaults."
                )
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}

        cfg = cls(
            mode=data.get("mode", "paper"),
            log_level=data.get("log_level", "INFO"),
            trade_log_csv=data.get("trade_log_csv", "trades.csv"),
            strategy=StrategyConfig(**(data.get("strategy") or {})),
            broker=BrokerConfig(**(data.get("broker") or {})),
            feed=FeedConfig(**(data.get("feed") or {})),
        )
        cfg._apply_env_overrides()
        cfg.validate()
        return cfg

    def _apply_env_overrides(self) -> None:
        # A handful of the most commonly tweaked knobs can be set via env vars,
        # which is convenient for CI and quick experiments.
        env = os.environ
        if "BOT_FEED_SOURCE" in env:
            self.feed.source = env["BOT_FEED_SOURCE"]
        if "BOT_BUY_AMOUNT_SOL" in env:
            self.strategy.buy_amount_sol = float(env["BOT_BUY_AMOUNT_SOL"])
        if "BOT_TAKE_PROFIT_PCT" in env:
            self.strategy.take_profit_pct = float(env["BOT_TAKE_PROFIT_PCT"])
        if "BOT_STOP_LOSS_PCT" in env:
            self.strategy.stop_loss_pct = float(env["BOT_STOP_LOSS_PCT"])
        if "BOT_LOG_LEVEL" in env:
            self.log_level = env["BOT_LOG_LEVEL"]

    def validate(self) -> None:
        errors: List[str] = []
        if self.mode != "paper":
            errors.append(
                f"mode must be 'paper' (live trading is not implemented), got {self.mode!r}"
            )
        s = self.strategy
        if s.buy_amount_sol <= 0:
            errors.append("strategy.buy_amount_sol must be > 0")
        if not (0 < s.take_profit_pct):
            errors.append("strategy.take_profit_pct must be > 0")
        if not (0 < s.stop_loss_pct < 1):
            errors.append("strategy.stop_loss_pct must be between 0 and 1")
        if s.trailing_stop_pct < 0 or s.trailing_stop_pct >= 1:
            errors.append("strategy.trailing_stop_pct must be in [0, 1)")
        if s.max_open_positions < 1:
            errors.append("strategy.max_open_positions must be >= 1")
        if self.broker.starting_balance_sol <= 0:
            errors.append("broker.starting_balance_sol must be > 0")
        if not (0 <= self.broker.fee_pct < 1):
            errors.append("broker.fee_pct must be in [0, 1)")
        if not (0 <= self.broker.slippage_pct < 1):
            errors.append("broker.slippage_pct must be in [0, 1)")
        if self.feed.source not in ("mock", "pumpportal"):
            errors.append("feed.source must be 'mock' or 'pumpportal'")
        if errors:
            raise ValueError("Invalid config:\n  - " + "\n  - ".join(errors))
