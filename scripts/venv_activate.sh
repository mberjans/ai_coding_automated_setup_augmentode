#!/usr/bin/env bash
set -euo pipefail

if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  echo ".venv not found. Run scripts/venv_create.sh first." >&2
  exit 1
fi
