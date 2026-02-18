"""
Async Event Bus — pub/sub for all trading events.

Event types:
    TICK        — raw market tick received
    BAR         — OHLCV bar closed
    SIGNAL      — strategy generated a signal
    ORDER       — order submitted to broker
    FILL        — order partially/fully filled
    BREACH      — risk limit breached
    REGIME      — regime change detected
    BREAKER     — circuit breaker activated/deactivated
    SHUTDOWN    — system shutting down
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable

logger = logging.getLogger("sniper.events")


class EventType(str, Enum):
    TICK     = "TICK"
    BAR      = "BAR"
    SIGNAL   = "SIGNAL"
    ORDER    = "ORDER"
    FILL     = "FILL"
    BREACH   = "BREACH"
    REGIME   = "REGIME"
    BREAKER  = "BREAKER"
    SHUTDOWN = "SHUTDOWN"


@dataclass
class Event:
    type: EventType
    data: dict[str, Any]
    ts: datetime = field(default_factory=datetime.utcnow)
    source: str = "system"


Handler = Callable[[Event], Awaitable[None]]


class EventBus:
    """
    Asyncio-based pub/sub event bus.

    Usage:
        bus = EventBus()

        @bus.subscribe(EventType.SIGNAL)
        async def on_signal(event: Event):
            ...

        await bus.publish(Event(type=EventType.SIGNAL, data={...}))
    """

    def __init__(self, max_queue_size: int = 10_000) -> None:
        self._handlers: dict[EventType, list[Handler]] = {e: [] for e in EventType}
        self._queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=max_queue_size)
        self._running = False
        self._stats: dict[str, int] = {e.value: 0 for e in EventType}

    # ------------------------------------------------------------------
    # Subscribe
    # ------------------------------------------------------------------

    def subscribe(self, *event_types: EventType) -> Callable[[Handler], Handler]:
        """Decorator to register a coroutine handler for one or more event types."""
        def decorator(fn: Handler) -> Handler:
            for et in event_types:
                self._handlers[et].append(fn)
                logger.debug("Subscribed %s → %s", fn.__name__, et.value)
            return fn
        return decorator

    def unsubscribe(self, event_type: EventType, handler: Handler) -> None:
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    # ------------------------------------------------------------------
    # Publish
    # ------------------------------------------------------------------

    async def publish(self, event: Event) -> None:
        """Enqueue event for dispatch."""
        try:
            await asyncio.wait_for(self._queue.put(event), timeout=0.1)
            self._stats[event.type.value] = self._stats.get(event.type.value, 0) + 1
        except asyncio.TimeoutError:
            logger.warning("EventBus queue full — dropped %s event", event.type.value)

    def publish_sync(self, event: Event) -> None:
        """Thread-safe synchronous publish (for non-async callers)."""
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning("EventBus queue full — dropped %s event", event.type.value)

    # ------------------------------------------------------------------
    # Run loop
    # ------------------------------------------------------------------

    async def run(self) -> None:
        """Process events from the queue until shutdown."""
        self._running = True
        logger.info("EventBus started")
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._dispatch(event)
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                logger.exception("EventBus dispatch error: %s", exc)

    async def stop(self) -> None:
        self._running = False
        await self.publish(Event(type=EventType.SHUTDOWN, data={}, source="event_bus"))
        logger.info("EventBus stopped")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _dispatch(self, event: Event) -> None:
        handlers = self._handlers.get(event.type, [])
        if not handlers:
            return
        tasks = [asyncio.create_task(h(event)) for h in handlers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                logger.error("Handler error for %s: %s", event.type.value, r)

    def stats(self) -> dict[str, int]:
        return dict(self._stats)
