#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

npm test
PYTHONPATH=.:./skilled python3 scripts/audit_operational_assets.py

generated="$(mktemp -d "${TMPDIR:-/tmp}/ai-ecosystem-dataset.XXXXXX")"
trap 'rm -rf -- "$generated"' EXIT
PYTHONPATH=.:./skilled python3 scripts/build_evaluation_dataset.py "$generated" >/dev/null
diff -ru datasets/evaluation "$generated"

echo "PASS: suite, activos operativos y dataset reproducible"
