from importlib import import_module

def test_interface_errors_and_contract():
    mod = import_module("src.providers.interface")

    # Error hierarchy exists
    assert hasattr(mod, "ProviderError")
    assert hasattr(mod, "AuthError")
    assert hasattr(mod, "RateLimitError")
    assert hasattr(mod, "TransientError")
    assert hasattr(mod, "PermanentError")

    # Required method names for a provider client (functional interface)
    assert hasattr(mod, "REQUIRED_METHODS")
    assert isinstance(mod.REQUIRED_METHODS, list)
    assert "prepare_prompt" in mod.REQUIRED_METHODS
    assert "call" in mod.REQUIRED_METHODS

    # Validator helpers for functional provider clients
    assert hasattr(mod, "is_valid_client")
    assert hasattr(mod, "require_client")

    # Validate correct shape
    good = {
        "prepare_prompt": lambda task, index, attempt_id: {"plan": "", "tickets": "", "checklist": ""},
        "call": lambda provider, model, prompt_bundle, params: {
            "plan": "# plan", "tickets": "# tickets", "checklist": "# checklist", "meta": {}
        },
    }
    assert mod.is_valid_client(good) is True

    # Missing method -> invalid
    bad_missing = {"prepare_prompt": lambda a, b, c: None}
    assert mod.is_valid_client(bad_missing) is False

    # Non-callable -> invalid
    bad_noncallable = {"prepare_prompt": 123, "call": 456}
    assert mod.is_valid_client(bad_noncallable) is False

    # require_client should raise ProviderError for invalid client
    raised = False
    try:
        mod.require_client(bad_missing)
    except Exception as e:
        raised = isinstance(e, mod.ProviderError)
    assert raised is True
