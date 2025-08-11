import types

import pytest

# Target API to be implemented in src/providers/rate_limit.py
# Functional style only; no OOP, no list comprehensions, no regex.
from src.providers import rate_limit as rl


class HttpError(Exception):
    def __init__(self, status):
        super().__init__(str(status))
        self.status = status


def _classify(err):
    # Classifier used by tests to label retryable conditions
    if isinstance(err, HttpError):
        if err.status == 429:
            return "retryable"
        if 500 <= err.status <= 599:
            return "retryable"
        return "fatal"
    return "fatal"


def test_exponential_backoff_on_429_until_success():
    calls = {"n": 0}

    def fn():
        if calls["n"] < 2:
            calls["n"] = calls["n"] + 1
            raise HttpError(429)
        return "ok"

    delays = []

    def sleep_fn(secs):
        delays.append(secs)

    # State for circuit breaker not tripping in this test
    state = rl.new_state(window_seconds=60, threshold=99, cooldown_seconds=30)

    result = rl.call_with_rate_limit(
        fn,
        max_retries=5,
        base_delay=0.1,
        max_delay=1.0,
        classify_error_fn=_classify,
        sleep_fn=sleep_fn,
        state=state,
    )

    assert result == "ok"
    # Expect at least two sleeps with exponential pattern
    assert len(delays) >= 2
    assert delays[0] == pytest.approx(0.1, rel=0.01, abs=0.01)
    assert delays[1] == pytest.approx(0.2, rel=0.01, abs=0.01)


def test_circuit_breaker_trips_after_threshold_and_blocks_until_cooldown():
    now = {"t": 1000.0}

    def now_fn():
        return now["t"]

    state = rl.new_state(window_seconds=60, threshold=3, cooldown_seconds=30, now_fn=now_fn)

    def always_500():
        raise HttpError(500)

    def sleep_fn(_):
        # advance artificial time by 1 second per backoff to accumulate failures within window
        now["t"] = now["t"] + 1.0

    # Exhaust retries to accumulate failures; expect raise after retries
    with pytest.raises(HttpError):
        rl.call_with_rate_limit(
            always_500,
            max_retries=2,
            base_delay=0.01,
            max_delay=0.02,
            classify_error_fn=_classify,
            sleep_fn=sleep_fn,
            state=state,
        )

    # More failures to cross threshold and open circuit
    with pytest.raises(HttpError):
        rl.call_with_rate_limit(
            always_500,
            max_retries=2,
            base_delay=0.01,
            max_delay=0.02,
            classify_error_fn=_classify,
            sleep_fn=sleep_fn,
            state=state,
        )

    # Now the circuit should be open; next call should raise CircuitOpen immediately without invoking fn
    # Track invocation count
    called = {"n": 0}

    def count_fn():
        called["n"] = called["n"] + 1
        raise HttpError(500)

    with pytest.raises(rl.CircuitOpen):
        rl.call_with_rate_limit(
            count_fn,
            max_retries=1,
            base_delay=0.01,
            max_delay=0.02,
            classify_error_fn=_classify,
            sleep_fn=sleep_fn,
            state=state,
        )

    assert called["n"] == 0

    # Advance time beyond cooldown to allow half-open trial
    now["t"] = now["t"] + 31.0

    # After cooldown, we should attempt the function again (and then fail)
    with pytest.raises(HttpError):
        rl.call_with_rate_limit(
            count_fn,
            max_retries=0,
            base_delay=0.01,
            max_delay=0.02,
            classify_error_fn=_classify,
            sleep_fn=sleep_fn,
            state=state,
        )
    assert called["n"] == 1
