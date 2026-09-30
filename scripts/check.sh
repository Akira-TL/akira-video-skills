#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

skiloom validate . --json
uv run python -m unittest discover -s tests
git diff --check
./scripts/list-skills.sh >/dev/null
