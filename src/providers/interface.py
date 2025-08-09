from typing import Any, Dict


class ProviderError(Exception):
    pass


class AuthError(ProviderError):
    pass


class RateLimitError(ProviderError):
    pass


class TransientError(ProviderError):
    pass


class PermanentError(ProviderError):
    pass


REQUIRED_METHODS = [
    "prepare_prompt",
    "call",
]


def _is_callable(value: Any) -> bool:
    try:
        return callable(value)
    except Exception:
        return False


def is_valid_client(client: Dict[str, Any]) -> bool:
    if not isinstance(client, dict):
        return False
    # Check required methods are present and callable
    for name in REQUIRED_METHODS:
        if name not in client:
            return False
        fn = client.get(name)
        if not _is_callable(fn):
            return False
    return True


def require_client(client: Dict[str, Any]) -> Dict[str, Any]:
    if not is_valid_client(client):
        raise ProviderError("Invalid provider client: missing required callable methods")
    return client
