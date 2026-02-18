"""
WebSocket Manager
Manages persistent WebSocket connections to broker market data feeds.
Handles reconnection with exponential backoff, heartbeat, and subscription management.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator
from typing import Any, Callable

logger = logging.getLogger("sniper.data.ws")

TickCallback = Callable[[dict], None]


class WebSocketManager:
    """
    Async WebSocket manager for market data streaming.

    Features:
    - Auto-reconnect with exponential backoff (max 60s)
    - Heartbeat / ping-pong to detect stale connections
    - Subscription management (add/remove symbols dynamically)
    - Publishes ticks to registered callbacks

    Requires: websockets package (pip install websockets)
    """

    MAX_BACKOFF_S  = 60.0
    HEARTBEAT_S    = 20.0
    CONNECT_TIMEOUT = 10.0

    def __init__(self, url: str, token: str | None = None) -> None:
        self._url     = url
        self._token   = token
        self._subs:   set[str] = set()
        self._cbs:    list[TickCallback] = []
        self._ws:     Any = None
        self._running = False
        self._backoff = 1.0
        self._stats   = {"connects": 0, "ticks": 0, "errors": 0}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def subscribe(self, *symbols: str) -> None:
        for s in symbols:
            self._subs.add(s.upper())

    def unsubscribe(self, *symbols: str) -> None:
        for s in symbols:
            self._subs.discard(s.upper())

    def on_tick(self, callback: TickCallback) -> None:
        self._cbs.append(callback)

    async def run(self) -> None:
        """Main loop — connects and streams until stopped."""
        self._running = True
        while self._running:
            try:
                await self._connect_and_stream()
                self._backoff = 1.0    # reset on clean disconnect
            except Exception as exc:
                self._stats["errors"] += 1
                logger.warning("WS error: %s — reconnecting in %.1fs", exc, self._backoff)
                await asyncio.sleep(self._backoff)
                self._backoff = min(self._backoff * 2, self.MAX_BACKOFF_S)

    async def stop(self) -> None:
        self._running = False
        if self._ws:
            await self._ws.close()

    def stats(self) -> dict:
        return dict(self._stats)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    async def _connect_and_stream(self) -> None:
        try:
            import websockets  # type: ignore
        except ImportError:
            logger.error("websockets package not installed. pip install websockets")
            await asyncio.sleep(30)
            return

        headers = {"Authorization": f"Bearer {self._token}"} if self._token else {}
        async with websockets.connect(
            self._url,
            additional_headers=headers,
            open_timeout=self.CONNECT_TIMEOUT,
        ) as ws:
            self._ws = ws
            self._stats["connects"] += 1
            self._backoff = 1.0
            logger.info("WS connected to %s", self._url)

            await self._send_subscriptions(ws)
            heartbeat_task = asyncio.create_task(self._heartbeat(ws))

            try:
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                        await self._handle_message(msg)
                    except Exception as exc:
                        logger.debug("Parse error: %s", exc)
            finally:
                heartbeat_task.cancel()

    async def _send_subscriptions(self, ws: Any) -> None:
        if self._subs:
            msg = json.dumps({"type": "subscribe", "symbols": list(self._subs)})
            await ws.send(msg)

    async def _heartbeat(self, ws: Any) -> None:
        while True:
            await asyncio.sleep(self.HEARTBEAT_S)
            try:
                await ws.ping()
            except Exception:
                break

    async def _handle_message(self, msg: dict) -> None:
        msg_type = msg.get("type", "tick")
        if msg_type in ("tick", "quote", "trade"):
            self._stats["ticks"] += 1
            for cb in self._cbs:
                try:
                    cb(msg)
                except Exception as exc:
                    logger.debug("Tick callback error: %s", exc)
