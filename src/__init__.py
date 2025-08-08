import os
import sys
import warnings


def _path_starts_with(base, value):
    if base is None:
        return False
    if value is None:
        return False
    base_str = str(base)
    value_str = str(value)
    if len(value_str) < len(base_str):
        return False
    return value_str[: len(base_str)] == base_str


def _detect_local_venv_prefix():
    root = os.path.abspath(os.getcwd())
    dot = os.path.join(root, ".venv")
    plain = os.path.join(root, "venv")
    prefix = sys.prefix

    if _path_starts_with(dot, prefix):
        return True
    if _path_starts_with(plain, prefix):
        return True
    return False


def _warn_if_not_local_venv():
    if not _detect_local_venv_prefix():
        warnings.warn(
            "Not running inside local project venv (.venv/ or venv/). For isolation, activate the local venv.",
            RuntimeWarning,
        )


_warn_if_not_local_venv()
