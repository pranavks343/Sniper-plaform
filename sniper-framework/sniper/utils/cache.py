"""
Caching Layer
In-memory TTL cache for market data and computed features.
Optionally backed by Redis for distributed caching.
"""
from __future__ import annotations

import json
import logging
import time
from threading import RLock
from typing import Any

logger = logging.getLogger("sniper.utils.cache")


class Cache:
    """
    Two-tier cache:
    1. In-memory LRU-style with TTL (always available, zero-dependency)
    2. Redis backend (optional — if redis_url provided)

    Usage:
        cache = Cache(ttl_s=60, max_size=1000)
        cache.set("regime:NIFTY", {"regime": "TRENDING"})
        val = cache.get("regime:NIFTY")

    With Redis:
        cache = Cache(ttl_s=60, redis_url="redis://localhost:6379/0")
    """

    def __init__(
        self,
        ttl_s:     float = 60.0,
        max_size:  int   = 10_000,
        redis_url: str | None = None,
    ) -> None:
        self._ttl      = ttl_s
        self._max_size = max_size
        self._store:   dict[str, tuple[Any, float]] = {}   # key → (value, expires_at)
        self._lock     = RLock()
        self._redis    = self._connect_redis(redis_url) if redis_url else None
        self._hits     = 0
        self._misses   = 0

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def get(self, key: str) -> Any | None:
        """Return cached value or None if missing/expired."""
        # Try Redis first
        if self._redis:
            try:
                raw = self._redis.get(key)
                if raw is not None:
                    self._hits += 1
                    return json.loads(raw)
            except Exception as exc:
                logger.debug("Redis get failed: %s", exc)

        # In-memory
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self._misses += 1
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                self._misses += 1
                return None
            self._hits += 1
            return value

    def set(self, key: str, value: Any, ttl_s: float | None = None) -> None:
        """Cache value with optional per-entry TTL override."""
        ttl = ttl_s if ttl_s is not None else self._ttl
        expires_at = time.monotonic() + ttl

        # Redis
        if self._redis:
            try:
                self._redis.setex(key, int(ttl), json.dumps(value, default=str))
            except Exception as exc:
                logger.debug("Redis set failed: %s", exc)

        # In-memory
        with self._lock:
            if len(self._store) >= self._max_size:
                self._evict()
            self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)
        if self._redis:
            try:
                self._redis.delete(key)
            except Exception:
                pass

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
        if self._redis:
            try:
                self._redis.flushdb()
            except Exception:
                pass

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "hits":      self._hits,
            "misses":    self._misses,
            "hit_rate":  round(self._hits / max(total, 1), 3),
            "size":      len(self._store),
            "redis":     self._redis is not None,
        }

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _evict(self) -> None:
        """Remove all expired entries; if still full, drop oldest 10%."""
        now = time.monotonic()
        expired = [k for k, (_, exp) in self._store.items() if now > exp]
        for k in expired:
            del self._store[k]

        if len(self._store) >= self._max_size:
            # Drop oldest 10% by expiry time
            sorted_keys = sorted(self._store, key=lambda k: self._store[k][1])
            for k in sorted_keys[:max(1, self._max_size // 10)]:
                del self._store[k]

    @staticmethod
    def _connect_redis(url: str) -> Any | None:
        try:
            import redis  # type: ignore

            r = redis.from_url(url, decode_responses=True, socket_timeout=2)
            r.ping()
            logger.info("Redis cache connected: %s", url)
            return r
        except Exception as exc:
            logger.warning("Redis unavailable (%s) — using in-memory cache only", exc)
            return None
