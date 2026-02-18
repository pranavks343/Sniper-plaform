from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any


class InMemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def get_or_set(self, key: str, factory: Callable[[], Any]) -> Any:
        if key in self._store:
            return self._store[key]
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            if key in self._store:
                return self._store[key]
            value = factory()
            self._store[key] = value
            return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)
