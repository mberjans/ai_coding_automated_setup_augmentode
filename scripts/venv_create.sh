#!/usr/bin/env bash
set -euo pipefail

# Create local venv in .venv/
python3 -m venv .venv

# Create marker file
mkdir -p .venv
: > .venv/.project_venv

echo "Local venv created at .venv/ and marker file written to .venv/.project_venv"
