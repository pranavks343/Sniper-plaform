"""
Retry Decorator
Exponential backoff with jitter for transient failures (network, broker API, etc.)
"""
from __future__ import annotations

import asyncio
import functools
import logging
import random
import time
from typing import Callable, Type

logger = logging.getLogger("sniper.utils.retry")


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, attempts: int, last_error: Exception) -> None:
        super().__init__(f"All {attempts} retry attempts failed. Last error: {last_error}")
        self.last_error = last_error
        self.attempts   = attempts


def retry(
    max_attempts:   int   = 3,
    base_delay_s:   float = 1.0,
    max_delay_s:    float = 60.0,
    backoff_factor: float = 2.0,
    jitter:         bool  = True,
    exceptions:     tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator that retries a function on failure with exponential backoff.

    Works on both sync and async functions.

    Args:
        max_attempts:   Total number of attempts (including the first)
        base_delay_s:   Initial delay between retries
        max_delay_s:    Maximum delay cap
        backoff_factor: Multiplier applied each retry
        jitter:         Add random jitter to delay (prevents thundering herd)
        exceptions:     Only retry on these exception types

    Example:
        @retry(max_attempts=5, base_delay_s=0.5, exceptions=(ConnectionError,))
        def place_order(order_id):
            ...
    """
    def decorator(fn: Callable) -> Callable:
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                delay = base_delay_s
                last_exc: Exception | None = None
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await fn(*args, **kwargs)
                    except exceptions as exc:
                        last_exc = exc
                        if attempt == max_attempts:
                            break
                        sleep = min(delay, max_delay_s)
                        if jitter:
                            sleep *= (0.5 + random.random())
                        logger.warning(
                            "Retry %d/%d for %s after %.2fs — %s",
                            attempt, max_attempts, fn.__name__, sleep, exc,
                        )
                        await asyncio.sleep(sleep)
                        delay *= backoff_factor
                raise RetryError(max_attempts, last_exc or Exception("Unknown"))
            return async_wrapper
        else:
            @functools.wraps(fn)
            def sync_wrapper(*args, **kwargs):
                delay = base_delay_s
                last_exc: Exception | None = None
                for attempt in range(1, max_attempts + 1):
                    try:
                        return fn(*args, **kwargs)
                    except exceptions as exc:
                        last_exc = exc
                        if attempt == max_attempts:
                            break
                        sleep = min(delay, max_delay_s)
                        if jitter:
                            sleep *= (0.5 + random.random())
                        logger.warning(
                            "Retry %d/%d for %s after %.2fs — %s",
                            attempt, max_attempts, fn.__name__, sleep, exc,
                        )
                        time.sleep(sleep)
                        delay *= backoff_factor
                raise RetryError(max_attempts, last_exc or Exception("Unknown"))
            return sync_wrapper
    return decorator
