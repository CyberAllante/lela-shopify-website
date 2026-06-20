#!/usr/bin/env python3
"""Live web dashboard for the paper-trading bot.

Runs the bot in a background thread (its own asyncio loop) and serves a small,
auto-refreshing dashboard plus a JSON state endpoint -- all on the Python
standard library, no web framework required.

    python web/server.py                       # mock feed, http://localhost:8000
    python web/server.py --feed pumpportal      # live pump.fun data
    python web/server.py --port 9000 --config config.yaml

This is a read-only window into the paper bot. It places no real trades.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Allow running both as `python web/server.py` and `python -m web.server`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.bot import TradingBot  # noqa: E402
from bot.config import Config  # noqa: E402
from bot.logging_setup import setup_logging  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))


class BotRunner:
    """Owns the bot and the background event loop it runs on."""

    def __init__(self, config: Config):
        self.config = config
        self.bot = TradingBot(config, setup_logging(config.log_level))
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.bot.run())
        finally:
            loop.close()

    def stop(self) -> None:
        self.bot.request_stop()

    def snapshot(self) -> dict:
        return self.bot.snapshot()


def make_handler(runner: BotRunner):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, content_type: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802 (stdlib naming)
            if self.path.split("?")[0] in ("/", "/index.html"):
                with open(os.path.join(_HERE, "index.html"), "rb") as fh:
                    self._send(200, fh.read(), "text/html; charset=utf-8")
            elif self.path.split("?")[0] == "/api/state":
                body = json.dumps(runner.snapshot()).encode("utf-8")
                self._send(200, body, "application/json")
            else:
                self._send(404, b"not found", "text/plain")

        def log_message(self, *args):  # silence per-request console noise
            return

    return Handler


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Web dashboard for the paper-trading bot")
    p.add_argument("--config", default=None, help="Path to a YAML config file")
    p.add_argument("--feed", choices=["mock", "pumpportal"], help="Override data feed")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    config = Config.load(args.config)
    if args.feed:
        config.feed.source = args.feed
    config.validate()

    runner = BotRunner(config)
    runner.start()

    server = ThreadingHTTPServer((args.host, args.port), make_handler(runner))
    url = f"http://{args.host}:{args.port}"
    print(f"\n  Dashboard live at {url}  (feed={config.feed.source})")
    print("  Press Ctrl-C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        runner.stop()
        server.shutdown()


if __name__ == "__main__":
    main()
