"""Live pump.fun data feed via PumpPortal's free WebSocket API.

Docs: https://pumpportal.fun/data-api/real-time

This feed:
  * subscribes to `subscribeNewToken` to detect launches, and
  * subscribes to `subscribeTokenTrade` for each token we hold, deriving a
    SOL/token price from each trade's SOL and token amounts.

It is read-only: it never sends orders. All "buying" and "selling" happens in
the paper broker. Requires the optional `websockets` dependency.
"""

from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, Optional

from ..models import TokenEvent, TradeTick
from .base import FeedEvent, MarketFeed


class PumpPortalFeed(MarketFeed):
    def __init__(self, config):
        self.url = config.feed.pumpportal_url
        self._ws = None
        self._watched: set[str] = set()
        self._closed = False

    async def _ensure_connected(self):
        if self._ws is not None:
            return self._ws
        try:
            import websockets  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "The pumpportal feed requires the `websockets` package. "
                "Install it with `pip install websockets`, or use feed.source: mock."
            ) from exc
        self._ws = await websockets.connect(self.url, ping_interval=20)
        await self._ws.send(json.dumps({"method": "subscribeNewToken"}))
        return self._ws

    async def watch(self, mint: str) -> None:
        if mint in self._watched:
            return
        self._watched.add(mint)
        ws = await self._ensure_connected()
        await ws.send(json.dumps({"method": "subscribeTokenTrade", "keys": [mint]}))

    async def unwatch(self, mint: str) -> None:
        if mint not in self._watched:
            return
        self._watched.discard(mint)
        if self._ws is not None:
            await self._ws.send(
                json.dumps({"method": "unsubscribeTokenTrade", "keys": [mint]})
            )

    async def close(self) -> None:
        self._closed = True
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    @staticmethod
    def _price_from_trade(msg: dict) -> Optional[float]:
        # PumpPortal trade payloads include vSolInBondingCurve and
        # vTokensInBondingCurve; their ratio is the current SOL/token price.
        v_sol = msg.get("vSolInBondingCurve")
        v_tok = msg.get("vTokensInBondingCurve")
        if v_sol and v_tok:
            try:
                return float(v_sol) / float(v_tok)
            except (TypeError, ValueError, ZeroDivisionError):
                return None
        # Fallback: per-trade ratio of SOL to tokens exchanged.
        sol_amt = msg.get("solAmount")
        tok_amt = msg.get("tokenAmount")
        if sol_amt and tok_amt:
            try:
                return float(sol_amt) / float(tok_amt)
            except (TypeError, ValueError, ZeroDivisionError):
                return None
        return None

    async def stream(self) -> AsyncIterator[FeedEvent]:
        ws = await self._ensure_connected()
        while not self._closed:
            try:
                raw = await ws.recv()
            except Exception:  # pragma: no cover - reconnect on drop
                if self._closed:
                    break
                await asyncio.sleep(1.0)
                ws = await self._ensure_connected()
                continue

            try:
                msg = json.loads(raw)
            except (ValueError, TypeError):
                continue
            if not isinstance(msg, dict):
                continue

            tx_type = msg.get("txType")
            mint = msg.get("mint")

            if tx_type == "create" and mint:
                price = self._price_from_trade(msg)
                yield (
                    "new",
                    TokenEvent(
                        mint=mint,
                        symbol=msg.get("symbol") or mint[:6],
                        name=msg.get("name") or "",
                        price_sol=price,
                        source="pumpportal",
                    ),
                )
            elif tx_type in ("buy", "sell") and mint in self._watched:
                price = self._price_from_trade(msg)
                if price is not None:
                    yield ("tick", TradeTick(mint=mint, price_sol=price))
