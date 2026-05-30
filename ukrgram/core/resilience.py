"""Resilience helpers: automatic retry/backoff for Telegram API calls."""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from telethon.errors import FloodWaitError, ServerError

from ukrgram.utils.logger import get_logger

_LOGGER = get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def retry_on_flood(
    *,
    max_retries: int = 3,
    max_wait_seconds: int = 300,
    backoff_base: float = 2.0,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Decorate an async Telegram call with FloodWait and transient-error retries.

    On :class:`~telethon.errors.FloodWaitError` the wrapper sleeps for the
    server-mandated cooldown (plus a small buffer) and retries. Transient server
    and connection errors are retried with exponential backoff.

    Args:
        max_retries: Maximum number of retries before re-raising.
        max_wait_seconds: Upper bound on a single FloodWait sleep; longer waits
            are re-raised instead of being slept through.
        backoff_base: Base of the exponential backoff for transient errors.

    Returns:
        A decorator wrapping an async callable with retry behavior.
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except FloodWaitError as exc:
                    wait_seconds = int(exc.seconds) + 1
                    if wait_seconds > max_wait_seconds or attempt >= max_retries:
                        _LOGGER.error(
                            "FloodWait of %ss exceeds limit or retries exhausted; re-raising.",
                            wait_seconds,
                        )
                        raise
                    attempt += 1
                    _LOGGER.warning(
                        "FloodWait: sleeping %ss before retry %d/%d.",
                        wait_seconds,
                        attempt,
                        max_retries,
                    )
                    await asyncio.sleep(wait_seconds)
                except (ServerError, ConnectionError, asyncio.TimeoutError) as exc:
                    if attempt >= max_retries:
                        _LOGGER.error("Transient error after %d retries: %s", attempt, exc)
                        raise
                    delay = backoff_base**attempt
                    attempt += 1
                    _LOGGER.warning(
                        "Transient error (%s); backing off %.1fs before retry %d/%d.",
                        type(exc).__name__,
                        delay,
                        attempt,
                        max_retries,
                    )
                    await asyncio.sleep(delay)

        return wrapper

    return decorator
