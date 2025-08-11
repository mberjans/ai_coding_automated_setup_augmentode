"""Functional rate limiting utilities: exponential backoff, circuit breaker, and token bucket.

Constraints:
- Functional Python only (no OOP)
- No list comprehensions
- No regex
"""
from typing import Any, Callable, Dict, List, Optional
import time as _time


class CircuitOpen(Exception):
    pass


def _now_default() -> float:
    return _time.time()


def new_state(window_seconds: int, threshold: int, cooldown_seconds: int, now_fn: Optional[Callable[[], float]] = None) -> Dict[str, Any]:
    state: Dict[str, Any] = {}
    state["window_seconds"] = int(window_seconds)
    state["threshold"] = int(threshold)
    state["cooldown_seconds"] = int(cooldown_seconds)
    state["failures"] = []  # type: List[float]
    state["opened_at"] = None  # type: Optional[float]
    if now_fn is None:
        state["now_fn"] = _now_default
    else:
        state["now_fn"] = now_fn
    return state


def _prune_old_failures(state: Dict[str, Any]) -> None:
    now = state["now_fn"]()
    window = state["window_seconds"]
    # Keep only failures within window
    new_failures: List[float] = []
    i = 0
    while i < len(state["failures"]):
        ts = state["failures"][i]
        if now - ts <= window:
            new_failures.append(ts)
        i = i + 1
    state["failures"] = new_failures


def _record_failure(state: Dict[str, Any]) -> None:
    _prune_old_failures(state)
    state["failures"].append(state["now_fn"]())


def _is_circuit_open(state: Dict[str, Any]) -> bool:
    # If opened_at is set and cooldown not passed, remain open
    if state["opened_at"] is not None:
        opened = state["opened_at"]
        if state["now_fn"]() - opened < state["cooldown_seconds"]:
            return True
        # cooldown passed; half-open (allow next call), reset opened_at
        state["opened_at"] = None
        return False
    # Do not open based solely on failures here; opening is evaluated after a failure is recorded.
    return False


def _evaluate_open_after_failure(state: Dict[str, Any]) -> None:
    # Decide whether to open the circuit after recording a failure
    _prune_old_failures(state)
    if state["opened_at"] is None and len(state["failures"]) >= state["threshold"]:
        state["opened_at"] = state["now_fn"]()


def _sleep(secs: float, sleep_fn: Optional[Callable[[float], None]]) -> None:
    if sleep_fn is None:
        _time.sleep(secs)
    else:
        sleep_fn(secs)


def _min(a: float, b: float) -> float:
    if a < b:
        return a
    return b


def call_with_rate_limit(
    fn: Callable[[], Any],
    max_retries: int,
    base_delay: float,
    max_delay: float,
    classify_error_fn: Callable[[BaseException], str],
    sleep_fn: Optional[Callable[[float], None]] = None,
    state: Optional[Dict[str, Any]] = None,
) -> Any:
    local_state = state
    if local_state is None:
        local_state = new_state(window_seconds=60, threshold=10, cooldown_seconds=30)

    # Circuit breaker check before attempting
    if _is_circuit_open(local_state):
        raise CircuitOpen("circuit open")

    attempt = 0
    delay = float(base_delay)
    while True:
        try:
            result = fn()
            # On success, clear failures window
            local_state["failures"] = []
            return result
        except BaseException as e:  # noqa: BLE001 intentional broad
            label = classify_error_fn(e)
            if label == "retryable" and attempt < max_retries:
                _record_failure(local_state)
                _evaluate_open_after_failure(local_state)
                # Backoff
                _sleep(delay, sleep_fn)
                # Next delay doubles but clamped to max_delay
                delay = _min(delay * 2.0, max_delay)
                attempt = attempt + 1
                # Even if circuit becomes open now, allow this call to continue retrying; next outer call will be blocked.
                continue
            # Non-retryable or retries exhausted: propagate without recording to avoid double-counting
            # Failures are accounted for on each retryable attempt before sleeping.
            raise e


# Optional token bucket utilities (for TICKET-023.02 completeness)

def new_bucket(capacity: int, refill_rate_per_sec: float, now_fn: Optional[Callable[[], float]] = None) -> Dict[str, Any]:
    b: Dict[str, Any] = {}
    b["capacity"] = int(capacity)
    b["refill_rate_per_sec"] = float(refill_rate_per_sec)
    b["tokens"] = float(capacity)
    b["updated_at"] = (_now_default() if now_fn is None else now_fn())
    b["now_fn"] = now_fn if now_fn is not None else _now_default
    return b


def _refill(bucket: Dict[str, Any]) -> None:
    now = bucket["now_fn"]()
    elapsed = now - bucket["updated_at"]
    if elapsed <= 0:
        return
    refill = elapsed * bucket["refill_rate_per_sec"]
    new_tokens = bucket["tokens"] + refill
    if new_tokens > bucket["capacity"]:
        new_tokens = float(bucket["capacity"])
    bucket["tokens"] = new_tokens
    bucket["updated_at"] = now


def allow(bucket: Dict[str, Any], tokens: float = 1.0) -> bool:
    _refill(bucket)
    if bucket["tokens"] >= tokens:
        bucket["tokens"] = bucket["tokens"] - tokens
        return True
    return False
