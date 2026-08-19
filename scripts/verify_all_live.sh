#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/verify_all.sh
bash scripts/verify_hermes_cli.sh
PYTHONPATH=.:./skilled python3 scripts/verify_claude_code_live.py
bash scripts/verify_hermes_autonomy.sh

echo "PASS: verificación integral, incluidas integraciones reales"
