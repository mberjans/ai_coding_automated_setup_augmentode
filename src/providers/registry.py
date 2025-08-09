from typing import Any, Dict

from . import interface as iface

_REGISTRY: Dict[str, Dict[str, Any]] = {}


def clear_registry() -> None:
    # test helper to reset state
    keys = list(_REGISTRY.keys())
    for k in keys:
        del _REGISTRY[k]


def register_provider(name: str, client: Dict[str, Any]) -> None:
    if not isinstance(name, str) or name == "":
        raise iface.ProviderError("Provider name must be a non-empty string")
    # Validate functional client shape
    iface.require_client(client)
    _REGISTRY[name] = client


def get_provider(name: str) -> Dict[str, Any]:
    if name in _REGISTRY:
        return _REGISTRY[name]
    raise iface.ProviderError("Unknown provider: " + str(name))
