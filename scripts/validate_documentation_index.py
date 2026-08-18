#!/usr/bin/env python3
"""Validate the documentation inventory, local links and patch catalog."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs/DOCUMENTATION_INDEX.md"
PATCH_CATALOG = ROOT / "docs/PATCH_CATALOG.md"
ALLOWED_STATES = {"Vigente", "Parcial", "Histórico", "Reemplazado", "Pendiente"}
PATCH_STATES = {"Pendiente", "Aplicado", "Reemplazado", "Obsoleto", "Solo respaldo"}
IGNORED_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".adoc"}
REQUIRED_NON_MARKDOWN = {
    ".claude/settings.json",
    ".claude/.mcp.json",
    ".mcp.json",
    "agents/hermes/config/config.yaml",
    "agents/hermes/plugins/neurosymbolic-integration/plugin.yaml",
    "skilled/reasoning/config.yaml",
    "src/reasoning/policies/safety.yaml",
    "docs/audits/external-components.json",
}


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_index() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    headers: list[str] | None = None
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        cells = _cells(line) if line.lstrip().startswith("|") else []
        if cells and cells[0] == "Documento":
            headers = cells
        elif headers and len(cells) == len(headers) and not all(set(c) <= {"-", ":"} for c in cells):
            row = dict(zip(headers, cells))
            row["Ruta"] = row["Ruta"].strip("`")
            rows.append(row)
    return rows


def parse_patch_catalog() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    headers: list[str] | None = None
    for line in PATCH_CATALOG.read_text(encoding="utf-8").splitlines():
        cells = _cells(line) if line.lstrip().startswith("|") else []
        if cells and cells[0] == "Parche o colección":
            headers = cells
        elif headers and len(cells) == len(headers) and not all(set(c) <= {"-", ":"} for c in cells):
            row = dict(zip(headers, cells))
            row["Ruta"] = row["Ruta"].strip("`")
            rows.append(row)
    return rows


def _covered(path: str, registered: set[str]) -> bool:
    for item in registered:
        target = ROOT / item
        if path == item or (target.is_dir() and path.startswith(item.rstrip("/") + "/")):
            return True
    return False


def _discover_documents() -> set[str]:
    result: set[str] = set(REQUIRED_NON_MARKDOWN)
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in DOC_EXTENSIONS:
            result.add(path.relative_to(ROOT).as_posix())
    return result


def _local_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text)


def validate() -> dict[str, object]:
    errors: list[str] = []
    if not INDEX.is_file() or not PATCH_CATALOG.is_file():
        return {"status": "failed", "errors": ["missing master index or patch catalog"]}

    rows = parse_index()
    paths = [row["Ruta"] for row in rows]
    duplicates = sorted({path for path in paths if paths.count(path) > 1})
    errors.extend(f"duplicate index entry: {path}" for path in duplicates)

    required_fields = {"Documento", "Ruta", "Descripción", "Área relacionada", "Cuándo consultarlo", "Cuándo actualizarlo", "Fuente principal", "Estado", "Sustituye o es sustituido por", "Última verificación"}
    for row in rows:
        path = row.get("Ruta", "")
        missing = sorted(field for field in required_fields if not row.get(field))
        if missing:
            errors.append(f"missing fields for {path}: {', '.join(missing)}")
        if row.get("Estado") not in ALLOWED_STATES:
            errors.append(f"invalid status for {path}: {row.get('Estado')}")
        if not (ROOT / path).exists():
            errors.append(f"indexed path does not exist: {path}")

    registered = set(paths)
    for path in sorted(_discover_documents()):
        if not _covered(path, registered):
            errors.append(f"relevant document is not indexed: {path}")

    # Broken links are actionable in current documents. Historical snapshots
    # remain immutable and are explicitly marked as such in the index.
    for row in rows:
        path = ROOT / row["Ruta"]
        if row.get("Estado") != "Vigente" or not path.is_file() or path.suffix.lower() != ".md":
            continue
        for raw in _local_links(path):
            link = raw.split()[0].strip("<>")
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_text = link.split("#", 1)[0]
            if not target_text:
                continue
            target = ROOT / target_text.lstrip("/") if target_text.startswith("/") else path.parent / target_text
            if not target.resolve().exists():
                errors.append(f"broken internal link in {path.relative_to(ROOT)}: {link}")

    patch_rows = parse_patch_catalog()
    patch_paths = [row["Ruta"] for row in patch_rows]
    for path in sorted({path for path in patch_paths if patch_paths.count(path) > 1}):
        errors.append(f"duplicate patch entry: {path}")
    for row in patch_rows:
        path = row["Ruta"]
        if not (ROOT / path).exists():
            errors.append(f"patch path does not exist: {path}")
        if row.get("Estado") not in PATCH_STATES:
            errors.append(f"invalid patch status for {path}: {row.get('Estado')}")
        for field in ("Problema o finalidad", "Componente", "Evidencia y versión", "Dependencias y riesgos"):
            if not row.get(field):
                errors.append(f"missing patch field {field}: {path}")

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    scripts = package.get("scripts", {})
    for source in (ROOT / "README.md", ROOT / "CLAUDE.md", ROOT / "ARCHITECTURE.md"):
        for command in re.findall(r"npm run ([a-zA-Z0-9:_-]+)", source.read_text(encoding="utf-8")):
            if command not in scripts:
                errors.append(f"nonexistent npm command in {source.relative_to(ROOT)}: {command}")

    critical_paths = [
        ROOT / "src/ingest.py",
        ROOT / "knowledge-service/run_ingest.sh",
        ROOT / "agents/hermes/plugins/neurosymbolic-integration/hermes_integration.py",
        ROOT / "sharememory/hermes_memory/knowledge_broker.py",
    ]
    for path in critical_paths:
        if path.is_file() and re.search(r"/home/[A-Za-z0-9._-]+/", path.read_text(encoding="utf-8")):
            errors.append(f"critical absolute home reference: {path.relative_to(ROOT)}")

    return {
        "status": "passed" if not errors else "failed",
        "indexed_entries": len(rows),
        "discovered_documents": len(_discover_documents()),
        "patch_entries": len(patch_rows),
        "errors": errors,
    }


def main() -> int:
    report = validate()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
