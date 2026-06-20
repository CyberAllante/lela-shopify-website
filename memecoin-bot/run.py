#!/usr/bin/env python3
"""Command-line entry point for the Solana meme-coin paper-trading bot.

Examples:
    python run.py                       # mock feed, default config
    python run.py --config config.yaml  # load settings from YAML
    python run.py --runtime 30          # run for 30 seconds then report
    python run.py --feed pumpportal     # use the live pump.fun data stream
"""

from __future__ import annotations

import argparse
import asyncio
import signal

from bot.bot import TradingBot
from bot.config import Config
from bot.logging_setup import setup_logging


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Solana meme-coin paper-trading sniper bot")
    p.add_argument("--config", help="Path to a YAML config file", default=None)
    p.add_argument(
        "--feed",
        choices=["mock", "pumpportal"],
        help="Override the data feed source",
    )
    p.add_argument(
        "--runtime",
        type=float,
        default=None,
        help="Stop after N seconds (useful for demos/CI). Default: run until Ctrl-C.",
    )
    p.add_argument("--log-level", default=None, help="DEBUG, INFO, WARNING, ...")
    return p.parse_args()


async def _main() -> None:
    args = parse_args()
    config = Config.load(args.config)
    if args.feed:
        config.feed.source = args.feed
    if args.log_level:
        config.log_level = args.log_level
    config.validate()

    logger = setup_logging(config.log_level)
    bot = TradingBot(config, logger)

    # Graceful shutdown on Ctrl-C / SIGTERM so we still print the summary.
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, bot.request_stop)
        except (NotImplementedError, RuntimeError):  # pragma: no cover (e.g. Windows)
            pass

    await bot.run(max_runtime_s=args.runtime)


def main() -> None:
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
