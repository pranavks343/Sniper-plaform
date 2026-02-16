from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable


class WebSocketManager:
    def __init__(self) -> None:
        self._tick_callbacks: list[Callable[[dict], Awaitable[None] | None]] = []
        self._order_callbacks: list[Callable[[dict], Awaitable[None] | None]] = []
        self._running = False

    async def connect(self, symbols: list[str]) -> None:
        _ = symbols
        self._running = True

    def on_tick(self, callback: Callable[[dict], Awaitable[None] | None]) -> None:
        self._tick_callbacks.append(callback)

    def on_order_update(self, callback: Callable[[dict], Awaitable[None] | None]) -> None:
        self._order_callbacks.append(callback)

    async def emit_tick(self, tick: dict) -> None:
        for callback in self._tick_callbacks:
            value = callback(tick)
            if asyncio.iscoroutine(value):
                await value

    async def emit_order_update(self, update: dict) -> None:
        for callback in self._order_callbacks:
            value = callback(update)
            if asyncio.iscoroutine(value):
                await value

    async def disconnect(self) -> None:
        self._running = False
