from __future__ import annotations

import asyncio
import fnmatch
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _json_ready(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_ready(v) for v in value]
    if isinstance(value, tuple):
        return [_json_ready(v) for v in value]
    return _json_default(value)


class ConvexBus:
    def __init__(self, convex_url: str, convex_deploy_key: str = '') -> None:
        self.convex_url = (convex_url or '').strip().rstrip('/')
        self.convex_deploy_key = (convex_deploy_key or '').strip()
        self._client: httpx.AsyncClient | None = None
        self._connected = False
        self._next_subscriber_id = 0
        self._subscribers: dict[int, tuple[list[str], asyncio.Queue[dict[str, Any]]]] = {}
        self._subscribers_lock = asyncio.Lock()
        self._snapshots: dict[str, dict[str, Any]] = {}

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def convex_enabled(self) -> bool:
        return bool(self.convex_url)

    async def connect(self) -> None:
        if self.connected:
            return
        if self.convex_enabled:
            self._client = httpx.AsyncClient(base_url=self.convex_url, timeout=5.0)
            logger.info('convex bus connected (persistence enabled)')
        else:
            logger.warning('CONVEX_URL is empty; using in-memory event bus only (no persistence)')
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False
        client = self._client
        self._client = None
        if client is not None:
            try:
                await client.aclose()
            except Exception:
                logger.warning('error while closing convex client', exc_info=True)
        async with self._subscribers_lock:
            self._subscribers.clear()

    async def publish(self, channel: str, payload: dict[str, Any]) -> bool:
        if not self.connected:
            return False
        normalized = _json_ready(payload)
        await self._fan_out(channel, normalized)
        if self.convex_enabled:
            await self._persist_event(channel, normalized)
        return True

    async def publish_event(self, channel: str, event: str, data: dict[str, Any]) -> bool:
        payload = {'event': event, 'data': data}
        return await self.publish(channel, payload)

    async def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> bool:
        if not self.connected:
            return False
        normalized = _json_ready(value)
        if not isinstance(normalized, dict):
            normalized = {'value': normalized}
        self._snapshots[key] = normalized
        if self.convex_enabled:
            expires_at = None
            if ttl_seconds is not None:
                expires_at = (datetime.now(tz=timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat()
            await self._mutation(
                'events:upsertSnapshot',
                {
                    'key': key,
                    'value': normalized,
                    'expiresAt': expires_at,
                },
            )
        return True

    async def subscribe(self, patterns: list[str]):
        if not self.connected:
            raise RuntimeError('convex bus is not connected')

        normalized_patterns = [p for p in patterns if p] or ['*']
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=512)

        async with self._subscribers_lock:
            subscriber_id = self._next_subscriber_id
            self._next_subscriber_id += 1
            self._subscribers[subscriber_id] = (normalized_patterns, queue)

        try:
            while True:
                payload = await queue.get()
                yield payload
        finally:
            async with self._subscribers_lock:
                self._subscribers.pop(subscriber_id, None)

    async def _fan_out(self, channel: str, payload: dict[str, Any]) -> None:
        async with self._subscribers_lock:
            subscribers = list(self._subscribers.values())

        for patterns, queue in subscribers:
            if not any(fnmatch.fnmatch(channel, pattern) for pattern in patterns):
                continue
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                # Queue stayed full due to concurrent puts; dropping oldest is acceptable for streaming UI.
                pass

    async def _persist_event(self, channel: str, payload: dict[str, Any]) -> None:
        await self._mutation(
            'events:ingestEvent',
            {
                'channel': channel,
                'event': str(payload.get('event') or channel),
                'data': payload.get('data', {}),
                'timestamp': datetime.now(tz=timezone.utc).isoformat(),
            },
        )

    async def _mutation(self, path: str, args: dict[str, Any]) -> bool:
        if self._client is None:
            return False
        headers: dict[str, str] = {}
        if self.convex_deploy_key:
            headers['Authorization'] = f'Convex {self.convex_deploy_key}'
        try:
            response = await self._client.post(
                '/api/mutation',
                json={'path': path, 'args': _json_ready(args)},
                headers=headers,
            )
            if response.is_error:
                logger.warning(
                    'convex mutation failed path=%s status=%s body=%s',
                    path,
                    response.status_code,
                    response.text[:300],
                )
                return False
            return True
        except Exception:
            logger.warning('convex mutation request failed path=%s', path, exc_info=True)
            return False

    def publish_event_nowait(self, channel: str, event: str, data: dict[str, Any]) -> None:
        self._schedule(self.publish_event(channel, event, data))

    def set_json_nowait(self, key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> None:
        self._schedule(self.set_json(key, value, ttl_seconds=ttl_seconds))

    def _schedule(self, task) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(task)
