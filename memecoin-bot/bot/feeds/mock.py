"""Synthetic, fully-offline market feed.

Generates a stream of fake token launches and then random-walks each token's
price with the occasional pump or rug so you can watch the strategy take
profit, stop out, and trail in a realistic-feeling way -- without any network
access, API keys, or real money.
"""

from __future__ import annotations

import asyncio
import random
import string
from typing import AsyncIterator, Dict

from ..models import TokenEvent, TradeTick
from .base import FeedEvent, MarketFeed


class _MockToken:
    def __init__(self, mint: str, symbol: str, price: float, rng: random.Random):
        self.mint = mint
        self.symbol = symbol
        self.price = price
        self._rng = rng
        # Each token gets a hidden "destiny": some moon, most fade/rug.
        roll = rng.random()
        if roll < 0.25:
            self.drift = rng.uniform(0.04, 0.12)  # runner
        elif roll < 0.45:
            self.drift = rng.uniform(0.0, 0.04)  # slow grind
        else:
            self.drift = rng.uniform(-0.10, 0.0)  # fader / rug
        self.vol = rng.uniform(0.05, 0.20)

    def next_price(self) -> float:
        # Geometric random walk so price stays positive.
        shock = self._rng.gauss(self.drift, self.vol)
        self.price = max(self.price * (1.0 + shock), 1e-12)
        return self.price


class MockFeed(MarketFeed):
    def __init__(self, config):
        self.cfg = config.feed
        self._rng = random.Random(self.cfg.mock_seed)
        self._tokens: Dict[str, _MockToken] = {}
        self._watched: set[str] = set()
        self._closed = False

    def _random_symbol(self) -> str:
        n = self._rng.randint(3, 5)
        return "".join(self._rng.choice(string.ascii_uppercase) for _ in range(n))

    def _new_token(self) -> TokenEvent:
        mint = "".join(self._rng.choice(string.hexdigits.lower()) for _ in range(44))
        symbol = self._random_symbol()
        price = self._rng.uniform(1e-8, 5e-7)  # tiny SOL/token, like a fresh launch
        self._tokens[mint] = _MockToken(mint, symbol, price, self._rng)
        return TokenEvent(
            mint=mint,
            symbol=symbol,
            name=f"{symbol} Coin",
            price_sol=price,
            source="mock",
        )

    async def watch(self, mint: str) -> None:
        self._watched.add(mint)

    async def unwatch(self, mint: str) -> None:
        self._watched.discard(mint)

    async def close(self) -> None:
        self._closed = True

    async def stream(self) -> AsyncIterator[FeedEvent]:
        new_interval = self.cfg.mock_new_token_interval_s
        tick_interval = self.cfg.mock_tick_interval_s
        time_to_new = 0.0

        while not self._closed:
            # Emit a price tick for every watched token.
            for mint in list(self._watched):
                tok = self._tokens.get(mint)
                if tok is None:
                    continue
                yield ("tick", TradeTick(mint=mint, price_sol=tok.next_price()))

            # Periodically launch a brand-new token.
            time_to_new -= tick_interval
            if time_to_new <= 0:
                yield ("new", self._new_token())
                time_to_new = new_interval

            await asyncio.sleep(tick_interval)
