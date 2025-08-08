import os
import sys
import site
from pathlib import Path


def _starts_with(base, value):
    if base is None:
        return False
    if value is None:
        return False
    base_str = str(base)
    value_str = str(value)
    if len(value_str) < len(base_str):
        return False
    return value_str[: len(base_str)] == base_str


def test_venv_marker_file_exists():
    marker_dot = Path('.venv/.project_venv')
    marker_plain = Path('venv/.project_venv')
    exists = marker_dot.exists() or marker_plain.exists()
    assert exists, "Expected venv marker file at .venv/.project_venv or venv/.project_venv"


def test_python_uses_local_venv_prefix():
    project_root = os.path.abspath(os.getcwd())
    local_dot = os.path.join(project_root, '.venv')
    local_plain = os.path.join(project_root, 'venv')
    prefix = sys.prefix

    ok = False
    if _starts_with(local_dot, prefix):
        ok = True
    if not ok and _starts_with(local_plain, prefix):
        ok = True

    assert ok, f"sys.prefix not inside local venv: {prefix}"


def test_global_site_packages_not_used():
    project_root = os.path.abspath(os.getcwd())
    local_dot = os.path.join(project_root, '.venv')
    local_plain = os.path.join(project_root, 'venv')

    packages = site.getsitepackages()

    has_local = False
    for p in packages:
        if _starts_with(local_dot, p):
            has_local = True
        if _starts_with(local_plain, p):
            has_local = True
    assert has_local, f"site-packages does not point to local venv: {packages}"
