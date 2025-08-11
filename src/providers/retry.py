"""Functional async retry utilities with exponential backoff.

Constraints:
- Functional Python only (no OOP)
- No list comprehensions
- No regex
"""
from typing import Any, Awaitable, Callable, Optional
import asyncio


def _min(a: float, b: float) -> float:
    if a < b:
        return a
    return b


async def _default_sleep(secs: float) -> None:
    await asyncio.sleep(secs)


async def async_retry(
    fn: Callable[[], Awaitable[Any]],
    max_attempts: int,
    base_delay: float,
    max_delay: float,
    classify_error_fn: Callable[[BaseException], str],
    sleep_fn: Optional[Callable[[float], Awaitable[None]]] = None,
) -> Any:
    if max_attempts < 1:
        max_attempts = 1

    attempt = 0
    delay = float(base_delay)
    last_exc: Optional[BaseException] = None

    while attempt < max_attempts:
        try:
            return await fn()
        except BaseException as e:  # noqa: BLE001 broad by design
            last_exc = e
            attempt = attempt + 1
            label = classify_error_fn(e)
            if label == "retryable" and attempt < max_attempts:
                if sleep_fn is None:
                    await _default_sleep(delay)
                else:
                    await sleep_fn(delay)
                delay = _min(delay * 2.0, max_delay)
                continue
            raise e

    # Should not reach here; re-raise last exception if present
    if last_exc is not None:
        raise last_exc
    return None
