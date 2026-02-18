"""In-memory rate limiting middleware by IP and path prefix."""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


def get_client_ip(request: Request) -> str:
    """Prefer X-Forwarded-For when behind a proxy."""
    forwarded = request.headers.get('x-forwarded-for')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if request.client else '0.0.0.0'


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limit by client IP. Limits are (path_prefix, requests per minute).
    First matching prefix wins.
    """

    def __init__(
        self,
        app,
        rules: list[tuple[str, int]] | None = None,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.rules = rules or [
            ('/api/v1/auth', 15),
            ('/api/v1/ai', 30),
            ('/api/v1', 120),
        ]
        self.window = window_seconds
        self._store: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    def _limit_for_path(self, path: str) -> tuple[str, int] | None:
        for prefix, limit in self.rules:
            if path.startswith(prefix):
                return (prefix, limit)
        return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        matched = self._limit_for_path(path)
        if matched is None:
            return await call_next(request)

        prefix, limit = matched
        ip = get_client_ip(request)
        key = prefix
        now = time.monotonic()
        cutoff = now - self.window

        timestamps = self._store[ip][key]
        timestamps[:] = [t for t in timestamps if t > cutoff]
        if len(timestamps) >= limit:
            return JSONResponse(
                status_code=429,
                content={'detail': 'Too many requests. Please try again later.'},
            )
        timestamps.append(now)

        return await call_next(request)
