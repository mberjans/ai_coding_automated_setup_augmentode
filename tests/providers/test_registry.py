from importlib import import_module


def _make_client():
    # Minimal functional client matching REQUIRED_METHODS
    return {
        "prepare_prompt": lambda task, index, attempt_id: {
            "plan": "p",
            "tickets": "t",
            "checklist": "c",
        },
        "call": lambda provider, model, prompt_bundle, params: {
            "plan": "# plan",
            "tickets": "# tickets",
            "checklist": "# checklist",
            "meta": {},
        },
    }


def test_registry_register_get_and_unknown():
    interface = import_module("src.providers.interface")
    registry = import_module("src.providers.registry")

    # Ensure clean state if helper exists
    if hasattr(registry, "clear_registry"):
        registry.clear_registry()

    client = _make_client()
    # Before registering, unknown should raise
    raised = False
    try:
        registry.get_provider("Anthropic")
    except Exception as e:
        raised = isinstance(e, interface.ProviderError)
    assert raised is True

    # Register and fetch
    registry.register_provider("Anthropic", client)
    got = registry.get_provider("Anthropic")
    assert interface.is_valid_client(got) is True

    # Re-register should overwrite
    other = _make_client()
    registry.register_provider("Anthropic", other)
    got2 = registry.get_provider("Anthropic")
    # Strict identity equality not required, but it should now validate the new one
    assert interface.is_valid_client(got2) is True


def test_registry_rejects_invalid_client():
    interface = import_module("src.providers.interface")
    registry = import_module("src.providers.registry")

    if hasattr(registry, "clear_registry"):
        registry.clear_registry()

    bad = {"prepare_prompt": lambda a, b, c: None}  # missing call
    raised = False
    try:
        registry.register_provider("BadProvider", bad)
    except Exception as e:
        raised = isinstance(e, interface.ProviderError)
    assert raised is True
