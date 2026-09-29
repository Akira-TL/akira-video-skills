#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

skiloom validate . --json
git diff --check
./scripts/list-skills.sh >/dev/null
