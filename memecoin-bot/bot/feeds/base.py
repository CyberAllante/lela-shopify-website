"""Feed interface.

A feed is an async source of two kinds of events:

  * new token launches  -> TokenEvent
  * price ticks for tracked tokens -> TradeTick

Concrete feeds yield `("new", TokenEvent)` or `("tick", TradeTick)` tuples from
their `stream()` async generator. The engine subscribes to price ticks for a
token via `watch()` once it has opened a position.
"""

from __future__ import annotations

import abc
from typing import AsyncIterator, Tuple, Union

from ..models import TokenEvent, TradeTick

FeedEvent = Tuple[str, Union[TokenEvent, TradeTick]]


class MarketFeed(abc.ABC):
    @abc.abstractmethod
    async def stream(self) -> AsyncIterator[FeedEvent]:
        """Yield ("new", TokenEvent) and ("tick", TradeTick) events."""
        raise NotImplementedError
        # The `yield` below makes this an async generator for type checkers.
        yield  # type: ignore[unreachable]

    async def watch(self, mint: str) -> None:
        """Begin streaming price ticks for `mint`. No-op for feeds that
        already broadcast all ticks (like the mock feed)."""
        return None

    async def unwatch(self, mint: str) -> None:
        """Stop streaming price ticks for `mint`."""
        return None

    async def close(self) -> None:
        """Release any resources (sockets, tasks)."""
        return None
