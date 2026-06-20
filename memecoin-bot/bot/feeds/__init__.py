"""Market data feeds."""

from .base import MarketFeed
from .mock import MockFeed

__all__ = ["MarketFeed", "MockFeed", "build_feed"]


def build_feed(config) -> MarketFeed:
    """Instantiate the configured feed.

    The pumpportal feed is imported lazily so the bot can run in mock mode
    without the optional `websockets` dependency installed.
    """
    source = config.feed.source
    if source == "mock":
        return MockFeed(config)
    if source == "pumpportal":
        from .pumpportal import PumpPortalFeed

        return PumpPortalFeed(config)
    raise ValueError(f"Unknown feed source: {source!r}")
