#!/usr/bin/env python3
"""Audit prompts, skills, services, datasets and external-component claims."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]


def audit() -> Dict[str, Any]:
    required = [
        "CLAUDE.md",
        "README.md",
        "ARCHITECTURE.md",
        "docs/DOCUMENTATION_INDEX.md",
        "docs/PATCH_CATALOG.md",
        "scripts/validate_documentation_index.py",
        "agents/hermes/plugins/neurosymbolic-integration/plugin.yaml",
        "agents/hermes/plugins/neurosymbolic-integration/__init__.py",
        "knowledge-service/run_ingest.sh",
        "datasets/evaluation/manifest.json",
        "docs/audits/external-components.json",
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    shell_scripts = [
        ROOT / "knowledge-service/run_ingest.sh",
        ROOT / "scripts/verify_hermes_cli.sh",
        ROOT / "scripts/verify_hermes_autonomy.sh",
        ROOT / "scripts/verify_all.sh",
    ]
    shell_errors = []
    for script in shell_scripts:
        if not script.is_file():
            shell_errors.append(f"missing:{script.relative_to(ROOT)}")
            continue
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            shell_errors.append(
                f"{script.relative_to(ROOT)}:{result.stderr.strip()}"
            )

    critical_runtime = [
        ROOT / "agents/hermes/plugins/neurosymbolic-integration/hermes_integration.py",
        ROOT / "knowledge-service/run_ingest.sh",
        ROOT / "sharememory/hermes_memory/knowledge_broker.py",
    ]
    absolute_home_references = [
        str(path.relative_to(ROOT))
        for path in critical_runtime
        if re.search(r"/home/[^/\s]+/", path.read_text(encoding="utf-8"))
    ]
    manifest_path = ROOT / "datasets/evaluation/manifest.json"
    dataset_ready = False
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        dataset_ready = bool(
            manifest.get("quality", {}).get("ready_for_comparative_evaluation")
        )
    checks = {
        "required_assets": not missing,
        "shell_syntax": not shell_errors,
        "portable_runtime_paths": not absolute_home_references,
        "dataset_ready": dataset_ready,
    }
    return {
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "missing": missing,
        "shell_errors": shell_errors,
        "absolute_home_references": absolute_home_references,
    }


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
