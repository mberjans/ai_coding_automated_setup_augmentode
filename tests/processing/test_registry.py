# TICKET-005.04: Failing tests for registry mapping

from typing import Callable


def _all_formats():
    return [
        "txt",
        "md",
        "docx",
        "xlsx",
        "csv",
        "tsv",
        "pdf",
        "pptx",
        "png",
        "jpeg",
        "svg",
    ]


def test_registry_contains_all_formats_expect_callables():
    from src.processing import registry

    reg = registry.get_registry()
    for fmt in _all_formats():
        assert fmt in reg
        parser = reg[fmt]
        assert callable(parser)


def test_resolve_known_returns_callable():
    from src.processing import registry

    for fmt in _all_formats():
        func = registry.resolve(fmt)
        assert callable(func)


def test_resolve_unknown_returns_none():
    from src.processing import registry

    assert registry.resolve("zip") is None
    assert registry.resolve("jpg") is None  # detection normalizes jpg -> jpeg
