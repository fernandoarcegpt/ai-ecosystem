#!/usr/bin/env python3
"""Persistent knowledge broker and repository ingester for Hermes.

The broker stores searchable memories in JSON/payload files and can ingest:

* PDFs from ``data/raw`` directories.
* Source code, documentation and configuration from projects owned by the user.
* Configuration files only from external/third-party projects.

Ownership can be declared with any of these mechanisms:

1. ``--own-project /path/to/project`` (repeatable).
2. ``HERMES_OWN_PROJECTS`` (colon-separated paths).
3. A ``.hermes-own-project`` marker in a project directory.
4. The directory containing this script, when it lives inside the ecosystem root.

Secrets are redacted from configuration files before indexing. Virtual
environments, dependency folders, build outputs, VCS data, caches and the
broker's own memory directory are ignored.

Examples
--------
Index the default ecosystem::

    python3 knowledge_broker.py ingest

Declare additional owned projects::

    python3 knowledge_broker.py ingest \
        --own-project /home/fernando/ai-ecosystem/hermes \
        --own-project /home/fernando/ai-ecosystem/sharememory

Search indexed knowledge::

    python3 knowledge_broker.py search "authentication"

Environment variables
---------------------
HERMES_MEMORY_DIR
    Memory directory. Defaults to
    /home/fernando/ai-ecosystem/sharememory/hermes_memory

HERMES_PROJECT_ROOT
    Ecosystem root. Defaults to /home/fernando/ai-ecosystem

HERMES_OWN_PROJECTS
    Colon-separated owned project paths.

HERMES_PDF_ROOTS
    Colon-separated PDF roots. Defaults are discovered ``data/raw`` folders
    under the ecosystem root and owned projects.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Literal, Optional, Sequence, Set, Tuple


DEFAULT_PROJECT_ROOT = Path("/home/fernando/ai-ecosystem")
DEFAULT_MEMORY_DIR = DEFAULT_PROJECT_ROOT / "sharememory" / "hermes_memory"

# Directories that normally contain generated, vendored, cached or private data.
IGNORED_DIR_NAMES: Set[str] = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".cache",
    ".next",
    ".nuxt",
    ".parcel-cache",
    ".turbo",
    ".yarn",
    "__pycache__",
    "node_modules",
    "vendor",
    "vendors",
    "third_party",
    "third-party",
    "site-packages",
    "dist",
    "build",
    "out",
    "target",
    "coverage",
    "htmlcov",
    "logs",
    "tmp",
    "temp",
    "venv",
    ".venv",
    "env",
    ".envdir",
}

# Exact files that are useful as project configuration/manifests.
CONFIG_EXACT_NAMES: Set[str] = {
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "tox.ini",
    "noxfile.py",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-prod.txt",
    "pipfile",
    "pipfile.lock",
    "package.json",
    "composer.json",
    "cargo.toml",
    "go.mod",
    "go.sum",
    "gemfile",
    "rakefile",
    "makefile",
    "cmakelists.txt",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "procfile",
    "manifest.json",
    "app.json",
    "tsconfig.json",
    "jsconfig.json",
    "eslint.config.js",
    "eslint.config.mjs",
    "prettier.config.js",
    "prettier.config.mjs",
    ".editorconfig",
    ".gitignore",
    ".dockerignore",
    ".npmrc.example",
    ".env.example",
    ".env.sample",
    ".env.template",
}

CONFIG_NAME_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"^requirements(?:[-_.].+)?\.txt$", re.IGNORECASE),
    re.compile(r"^(?:config|settings|application|appsettings)(?:[-_.].+)?\.(?:json|ya?ml|toml|ini|cfg|conf|properties)$", re.IGNORECASE),
    re.compile(r"^docker-compose(?:[-_.].+)?\.ya?ml$", re.IGNORECASE),
    re.compile(r"^(?:tsconfig|jsconfig)(?:[-_.].+)?\.json$", re.IGNORECASE),
    re.compile(r"^\.env\.(?:example|sample|template|dist)$", re.IGNORECASE),
    re.compile(r"^dockerfile(?:[-_.].+)?$", re.IGNORECASE),
)

# Lock files are usually huge/noisy. Pipfile.lock is retained above because it
# can be the only Python dependency declaration in some projects.
IGNORED_FILE_NAMES: Set[str] = {
    "package-lock.json",
    "npm-shrinkwrap.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "cargo.lock",
    ".ds_store",
}

CONFIG_DIR_NAMES: Set[str] = {
    ".github",
    ".circleci",
    "config",
    "configs",
    ".config",
    "configuration",
    "deploy",
    "deployment",
    "deployments",
    "infra",
    "infrastructure",
    "ops",
    "k8s",
    "kubernetes",
    "helm",
    "ansible",
    "terraform",
    "nginx",
    "systemd",
}

CONFIG_EXTENSIONS: Set[str] = {
    ".json", ".jsonc", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".conf", ".properties", ".service", ".socket", ".timer", ".tf",
    ".tfvars",
}

CODE_EXTENSIONS: Set[str] = {
    ".py", ".pyi", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx",
    ".sh", ".bash", ".zsh", ".fish", ".sql", ".go", ".rs", ".java",
    ".kt", ".kts", ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp",
    ".cs", ".php", ".rb", ".swift", ".scala", ".lua", ".r", ".dart",
    ".vue", ".svelte",
}

DOCUMENT_EXTENSIONS: Set[str] = {
    ".md", ".mdx", ".rst", ".txt", ".adoc",
}

# Files whose content should never be indexed, even in owned projects.
PRIVATE_FILE_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"^\.env$", re.IGNORECASE),
    re.compile(r"^\.env\.(?!example$|sample$|template$|dist$).+$", re.IGNORECASE),
    re.compile(r".*\.(?:pem|key|p12|pfx|jks|keystore)$", re.IGNORECASE),
    re.compile(r"^(?:id_rsa|id_ed25519)(?:\.pub)?$", re.IGNORECASE),
    re.compile(r"^(?:credentials|secrets?)(?:[-_.].*)?\.(?:json|ya?ml|toml|ini|cfg|conf)$", re.IGNORECASE),
)

SECRET_KEY_PATTERN = re.compile(
    r"(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|"
    r"private[_-]?key|client[_-]?secret|credential|authorization|bearer)",
    re.IGNORECASE,
)

# Redacts common key/value formats while preserving the surrounding config.
KEY_VALUE_SECRET_RE = re.compile(
    r"""(?ix)
    ^
    (?P<prefix>\s*["']?[\w.\-]*(?:
        password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|
        private[_-]?key|client[_-]?secret|credential|authorization
    )[\w.\-]*["']?\s*(?:=|:)\s*)
    (?P<value>.+?)
    (?P<suffix>\s*,?\s*(?:\#.*)?$)
    """
)

BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}")
URL_CREDENTIAL_RE = re.compile(
    r"(?P<scheme>[a-z][a-z0-9+.-]*://)"
    r"(?P<user>[^/\s:@]+):(?P<password>[^/\s@]+)@",
    re.IGNORECASE,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def _split_env_paths(value: Optional[str]) -> List[Path]:
    if not value:
        return []
    return [Path(part).expanduser() for part in value.split(os.pathsep) if part.strip()]


class KnowledgeBroker:
    """OKF-style persistent memory store with safe concurrent writes."""

    def __init__(self, memory_dir: Optional[str] = None):
        selected = memory_dir or os.getenv("HERMES_MEMORY_DIR") or str(DEFAULT_MEMORY_DIR)
        self.memory_dir = Path(selected).expanduser().resolve()
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.memory_file = self.memory_dir / "memory.json"
        self.lock_file = self.memory_dir / "memory.lock"
        self.payloads_dir = self.memory_dir / "payloads"
        self.payloads_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _transaction(self, mode: Literal["r", "w"] = "r"):
        """Acquire a shared read lock or exclusive write lock."""
        lock_f = open(self.lock_file, "a+", encoding="utf-8")
        try:
            if mode == "r":
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_SH)
            else:
                start = time.monotonic()
                while time.monotonic() - start < 5:
                    try:
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except (OSError, BlockingIOError):
                        time.sleep(0.01)
                else:
                    raise TimeoutError("Could not acquire exclusive lock after 5 seconds")
            yield
        finally:
            try:
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            lock_f.close()

    def _load_memory_unlocked(self) -> Dict[str, Any]:
        if not self.memory_file.exists():
            return {}
        try:
            with self.memory_file.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            return loaded if isinstance(loaded, dict) else {}
        except (json.JSONDecodeError, OSError):
            # Preserve the damaged file for inspection instead of overwriting it.
            if self.memory_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                backup = self.memory_file.with_name(f"memory.corrupt-{timestamp}.json")
                try:
                    shutil.copy2(self.memory_file, backup)
                except OSError:
                    pass
            return {}

    def _save_memory_unlocked(self, data: Dict[str, Any]) -> None:
        """Atomically replace memory.json. Caller must hold a write lock."""
        fd, temp_name = tempfile.mkstemp(
            prefix="memory-",
            suffix=".tmp",
            dir=str(self.memory_dir),
            text=True,
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self.memory_file)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def _content_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _generate_deterministic_id(
        self,
        content: str,
        identity_key: Optional[str] = None,
    ) -> str:
        material = f"{identity_key}\0{content}" if identity_key else content
        return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _is_long_content(content: str) -> bool:
        return len(content) > 500

    @staticmethod
    def _extract_short_summary(content: str) -> str:
        normalized = " ".join(content.split())
        return normalized[:497] + "..." if len(normalized) > 500 else normalized

    def _store_long_content(self, content: str, entry_id: str) -> str:
        """Atomically write a payload and return its path relative to memory_dir."""
        target = self.payloads_dir / f"{entry_id}.md"
        fd, temp_name = tempfile.mkstemp(
            prefix=f"{entry_id}-",
            suffix=".tmp",
            dir=str(self.payloads_dir),
            text=True,
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, target)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise
        return str(target.relative_to(self.memory_dir))

    def _load_payload(self, entry: Dict[str, Any]) -> Optional[str]:
        relative = entry.get("payload_file")
        if not relative:
            return None
        payload_path = (self.memory_dir / relative).resolve()
        if not _is_relative_to(payload_path, self.payloads_dir):
            return None
        try:
            return payload_path.read_text(encoding="utf-8")
        except OSError:
            return None

    @staticmethod
    def _cleanup_expired(entries: Dict[str, Any]) -> bool:
        """Mark expired active entries as archived without deleting history."""
        now = datetime.now(timezone.utc)
        changed = False
        for entry in entries.values():
            if entry.get("status", "active") != "active":
                continue
            expires_at = entry.get("expires_at")
            if not expires_at:
                continue
            try:
                expires_dt = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
                if expires_dt <= now:
                    entry["status"] = "archived"
                    entry["archived_at"] = _utc_now()
                    changed = True
            except (TypeError, ValueError):
                # Invalid expiration metadata does not destroy the entry.
                continue
        return changed

    @staticmethod
    def _merge_metadata(
        existing: Dict[str, Any],
        incoming: Optional[Dict[str, Any]],
        source: str,
        tags: Optional[Sequence[str]],
        content_hash: str,
    ) -> Dict[str, Any]:
        merged = dict(existing or {})
        if incoming:
            merged.update(incoming)
        merged["source"] = source
        merged["content_hash"] = content_hash
        merged.setdefault("created_at", _utc_now())
        merged["updated_at"] = _utc_now()
        if tags is not None:
            merged["tags"] = sorted(set(tags))
        else:
            merged.setdefault("tags", [])
        return merged

    def store(
        self,
        content: str,
        entry_type: str = "fact",
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: str = "system",
        identity_key: Optional[str] = None,
        supersede_same_source: bool = False,
    ) -> Dict[str, Any]:
        """Store content and optionally version entries sharing a source identity.

        ``identity_key`` makes IDs stable per source as well as content. This is
        useful for repository files because identical files in different projects
        should remain distinct.

        When ``supersede_same_source`` is true, older active entries with the
        same ``metadata.source_key`` are marked superseded.
        """
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content must be a non-empty string")

        content_hash = self._content_hash(content)
        entry_id = self._generate_deterministic_id(content, identity_key=identity_key)
        now = _utc_now()

        with self._transaction("w"):
            entries = self._load_memory_unlocked()
            self._cleanup_expired(entries)

            existing = entries.get(entry_id)
            if existing and existing.get("metadata", {}).get("content_hash") == content_hash:
                existing["timestamp"] = now
                existing["status"] = "active"
                existing["metadata"] = self._merge_metadata(
                    existing.get("metadata", {}),
                    metadata,
                    source,
                    tags,
                    content_hash,
                )
                if expires_at:
                    existing["expires_at"] = expires_at
                elif "expires_at" in existing:
                    existing.pop("expires_at", None)
                self._save_memory_unlocked(entries)
                return existing

            source_key = (metadata or {}).get("source_key")
            if supersede_same_source and source_key:
                for old_id, old_entry in entries.items():
                    if old_id == entry_id or old_entry.get("status", "active") != "active":
                        continue
                    if old_entry.get("metadata", {}).get("source_key") == source_key:
                        old_entry["status"] = "superseded"
                        old_entry["superseded_at"] = now
                        old_entry["superseded_by"] = entry_id

            final_metadata = self._merge_metadata(
                {},
                metadata,
                source,
                tags,
                content_hash,
            )
            entry: Dict[str, Any] = {
                "id": entry_id,
                "type": entry_type,
                "content": content,
                "metadata": final_metadata,
                "timestamp": now,
                "status": "active",
            }
            if expires_at:
                entry["expires_at"] = expires_at

            if self._is_long_content(content):
                entry["payload_file"] = self._store_long_content(content, entry_id)
                entry["content"] = self._extract_short_summary(content)

            entries[entry_id] = entry
            self._save_memory_unlocked(entries)
            return entry

    def cleanup_expired(self) -> int:
        """Persist expiration changes and return the number newly archived."""
        with self._transaction("w"):
            entries = self._load_memory_unlocked()
            before = sum(1 for e in entries.values() if e.get("status") == "archived")
            changed = self._cleanup_expired(entries)
            after = sum(1 for e in entries.values() if e.get("status") == "archived")
            if changed:
                self._save_memory_unlocked(entries)
            return after - before

    def retrieve(
        self,
        entry_id: str,
        include_inactive: bool = False,
    ) -> Optional[Dict[str, Any]]:
        with self._transaction("r"):
            entries = self._load_memory_unlocked()
        self._cleanup_expired(entries)
        entry = entries.get(entry_id)
        if not entry:
            return None
        if not include_inactive and entry.get("status", "active") != "active":
            return None
        return entry

    def retrieve_full_content(
        self,
        entry_id: str,
        include_inactive: bool = False,
    ) -> Optional[str]:
        entry = self.retrieve(entry_id, include_inactive=include_inactive)
        if not entry:
            return None
        return self._load_payload(entry) or entry.get("content")

    def search(
        self,
        query: Optional[str] = None,
        entry_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        include_archived: bool = False,
        include_superseded: bool = False,
        limit: int = 20,
        case_sensitive: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search memory using literal text and metadata filters."""
        with self._transaction("r"):
            entries = self._load_memory_unlocked()
        self._cleanup_expired(entries)

        query_cmp = query if case_sensitive or query is None else query.casefold()
        results: List[Dict[str, Any]] = []

        for entry in sorted(
            entries.values(),
            key=lambda item: item.get("timestamp", ""),
            reverse=True,
        ):
            status = entry.get("status", "active")
            if status == "archived" and not include_archived:
                continue
            if status == "superseded" and not include_superseded:
                continue
            if status not in {"active", "archived", "superseded"}:
                continue

            if entry_type and entry.get("type") != entry_type:
                continue
            if source and entry.get("metadata", {}).get("source") != source:
                continue
            if tags:
                entry_tags = set(entry.get("metadata", {}).get("tags", []))
                if not set(tags).issubset(entry_tags):
                    continue

            if query_cmp:
                searchable = self._load_payload(entry) or entry.get("content", "")
                haystack = searchable if case_sensitive else searchable.casefold()
                metadata_text = json.dumps(
                    entry.get("metadata", {}),
                    ensure_ascii=False,
                    default=str,
                )
                if not case_sensitive:
                    metadata_text = metadata_text.casefold()
                if query_cmp not in haystack and query_cmp not in metadata_text:
                    continue

            results.append(entry)
            if len(results) >= max(1, limit):
                break

        return results

    def delete(self, entry_id: str) -> bool:
        """Logically delete an entry by marking it superseded."""
        with self._transaction("w"):
            entries = self._load_memory_unlocked()
            if entry_id not in entries:
                return False
            entries[entry_id]["status"] = "superseded"
            entries[entry_id]["superseded_at"] = _utc_now()
            self._save_memory_unlocked(entries)
            return True

    def mark_missing_sources(
        self,
        source_keys_seen: Set[str],
        root_key: str,
    ) -> int:
        """Supersede active ingested files beneath root_key that disappeared."""
        changed = 0
        with self._transaction("w"):
            entries = self._load_memory_unlocked()
            for entry in entries.values():
                metadata = entry.get("metadata", {})
                source_key = metadata.get("source_key")
                if (
                    entry.get("status", "active") == "active"
                    and metadata.get("ingested_by") == "repository_ingester"
                    and isinstance(source_key, str)
                    and source_key.startswith(root_key)
                    and source_key not in source_keys_seen
                ):
                    entry["status"] = "superseded"
                    entry["superseded_at"] = _utc_now()
                    entry["superseded_reason"] = "source_missing"
                    changed += 1
            if changed:
                self._save_memory_unlocked(entries)
        return changed

    def get_stats(self) -> Dict[str, Any]:
        with self._transaction("r"):
            entries = self._load_memory_unlocked()
        self._cleanup_expired(entries)

        stats: Dict[str, Any] = {
            "total": len(entries),
            "by_type": {},
            "by_status": {"active": 0, "archived": 0, "superseded": 0},
            "by_file_kind": {},
        }
        for entry in entries.values():
            entry_type = entry.get("type", "unknown")
            stats["by_type"][entry_type] = stats["by_type"].get(entry_type, 0) + 1

            status = entry.get("status", "active")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            kind = entry.get("metadata", {}).get("file_kind")
            if kind:
                stats["by_file_kind"][kind] = stats["by_file_kind"].get(kind, 0) + 1
        return stats

    def list_keys(self, include_inactive: bool = False) -> List[str]:
        with self._transaction("r"):
            entries = self._load_memory_unlocked()
        self._cleanup_expired(entries)
        if include_inactive:
            return list(entries.keys())
        return [
            key
            for key, entry in entries.items()
            if entry.get("status", "active") == "active"
        ]


class RepositoryIngester:
    """Ingest PDFs, owned source code and safe project configuration."""

    def __init__(
        self,
        broker: KnowledgeBroker,
        project_root: Optional[Path] = None,
        own_projects: Optional[Sequence[Path]] = None,
        pdf_roots: Optional[Sequence[Path]] = None,
        max_text_bytes: int = 2_000_000,
        max_pdf_bytes: int = 100_000_000,
        redact_secrets: bool = True,
    ):
        root_env = os.getenv("HERMES_PROJECT_ROOT")
        self.project_root = (
            project_root
            or (Path(root_env).expanduser() if root_env else DEFAULT_PROJECT_ROOT)
        ).resolve()
        self.broker = broker
        self.max_text_bytes = max_text_bytes
        self.max_pdf_bytes = max_pdf_bytes
        self.redact_secrets = redact_secrets

        declared = list(own_projects or [])
        declared.extend(_split_env_paths(os.getenv("HERMES_OWN_PROJECTS")))

        script_dir = Path(__file__).resolve().parent
        if _is_relative_to(script_dir, self.project_root):
            declared.append(script_dir)

        # Immediate children with a marker are owned projects.
        if self.project_root.exists():
            for child in self.project_root.iterdir():
                if child.is_dir() and (child / ".hermes-own-project").exists():
                    declared.append(child)

        self.own_projects = self._normalize_roots(declared)

        declared_pdf_roots = list(pdf_roots or [])
        declared_pdf_roots.extend(_split_env_paths(os.getenv("HERMES_PDF_ROOTS")))
        if not declared_pdf_roots:
            declared_pdf_roots.extend(self._discover_default_pdf_roots())
        self.pdf_roots = self._normalize_roots(declared_pdf_roots)

        self._seen_source_keys: Set[str] = set()

    @staticmethod
    def _normalize_roots(paths: Iterable[Path]) -> List[Path]:
        unique: List[Path] = []
        seen: Set[str] = set()
        for path in paths:
            resolved = Path(path).expanduser().resolve()
            key = str(resolved)
            if key not in seen:
                unique.append(resolved)
                seen.add(key)
        return unique

    def _discover_default_pdf_roots(self) -> List[Path]:
        candidates = [self.project_root / "data" / "raw"]
        candidates.extend(root / "data" / "raw" for root in self.own_projects)

        # Discover shallow data/raw directories without descending into vendors.
        if self.project_root.exists():
            try:
                for child in self.project_root.iterdir():
                    if not child.is_dir() or child.name in IGNORED_DIR_NAMES:
                        continue
                    candidate = child / "data" / "raw"
                    if candidate.exists():
                        candidates.append(candidate)
            except OSError:
                pass
        return candidates

    def _is_ignored_dir(self, directory: Path) -> bool:
        name = directory.name.lower()
        if name in IGNORED_DIR_NAMES:
            return True
        if _is_relative_to(directory, self.broker.memory_dir):
            return True
        return False

    @staticmethod
    def _is_private_file(path: Path) -> bool:
        return any(pattern.match(path.name) for pattern in PRIVATE_FILE_PATTERNS)

    def _is_config_file(self, path: Path) -> bool:
        lower_name = path.name.lower()
        if lower_name in IGNORED_FILE_NAMES:
            return False
        if lower_name in CONFIG_EXACT_NAMES:
            return True
        if any(pattern.match(path.name) for pattern in CONFIG_NAME_PATTERNS):
            return True

        # Arbitrarily named YAML/JSON/TOML/etc. files are considered config only
        # when they live in a conventional configuration/operations directory.
        try:
            relative_parts = [
                part.lower()
                for part in path.resolve().relative_to(self.project_root).parts[:-1]
            ]
        except ValueError:
            relative_parts = [part.lower() for part in path.parts[:-1]]

        return (
            path.suffix.lower() in CONFIG_EXTENSIONS
            and any(part in CONFIG_DIR_NAMES for part in relative_parts)
        )

    @staticmethod
    def _is_code_file(path: Path) -> bool:
        return path.suffix.lower() in CODE_EXTENSIONS

    @staticmethod
    def _is_document_file(path: Path) -> bool:
        return path.suffix.lower() in DOCUMENT_EXTENSIONS

    def _is_owned_path(self, path: Path) -> bool:
        return any(_is_relative_to(path, root) for root in self.own_projects)

    def _project_name(self, path: Path) -> str:
        for root in sorted(self.own_projects, key=lambda item: len(item.parts), reverse=True):
            if _is_relative_to(path, root):
                return root.name
        try:
            return path.relative_to(self.project_root).parts[0]
        except (ValueError, IndexError):
            return path.parent.name

    def _source_key(self, path: Path) -> str:
        resolved = path.resolve()
        try:
            relative = resolved.relative_to(self.project_root)
            return f"repo:{relative.as_posix()}"
        except ValueError:
            return f"file:{resolved.as_posix()}"

    def _walk_files(self, root: Path) -> Iterator[Path]:
        if not root.exists() or not root.is_dir():
            return
        for current, dirnames, filenames in os.walk(root):
            current_path = Path(current)
            dirnames[:] = [
                name
                for name in dirnames
                if not self._is_ignored_dir(current_path / name)
            ]
            for filename in filenames:
                yield current_path / filename

    @staticmethod
    def _looks_binary(path: Path) -> bool:
        try:
            with path.open("rb") as f:
                chunk = f.read(8192)
            return b"\x00" in chunk
        except OSError:
            return True

    def _read_text(self, path: Path) -> Tuple[Optional[str], Optional[str]]:
        try:
            size = path.stat().st_size
        except OSError as exc:
            return None, f"stat_error:{exc}"

        if size > self.max_text_bytes:
            return None, "text_too_large"
        if self._looks_binary(path):
            return None, "binary_file"

        encodings = ("utf-8", "utf-8-sig", "latin-1")
        for encoding in encodings:
            try:
                return path.read_text(encoding=encoding), None
            except UnicodeDecodeError:
                continue
            except OSError as exc:
                return None, f"read_error:{exc}"
        return None, "decode_error"

    @staticmethod
    def _extract_pdf_with_python(path: Path) -> Tuple[Optional[str], Optional[str]]:
        reader_cls = None
        try:
            from pypdf import PdfReader  # type: ignore
            reader_cls = PdfReader
        except ImportError:
            try:
                from PyPDF2 import PdfReader  # type: ignore
                reader_cls = PdfReader
            except ImportError:
                return None, "missing_pypdf"

        try:
            reader = reader_cls(str(path))
            pages: List[str] = []
            for number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                pages.append(f"\n\n--- PAGE {number} ---\n{text.strip()}")
            combined = "".join(pages).strip()
            if not combined:
                return None, "pdf_without_extractable_text"
            return combined, None
        except Exception as exc:
            return None, f"pdf_parse_error:{type(exc).__name__}:{exc}"

    @staticmethod
    def _extract_pdf_with_pdftotext(path: Path) -> Tuple[Optional[str], Optional[str]]:
        executable = shutil.which("pdftotext")
        if not executable:
            return None, "missing_pdftotext"
        try:
            result = subprocess.run(
                [executable, "-layout", str(path), "-"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return None, f"pdftotext_error:{exc}"

        if result.returncode != 0:
            error = result.stderr.decode("utf-8", errors="replace").strip()
            return None, f"pdftotext_failed:{error[:300]}"
        text = result.stdout.decode("utf-8", errors="replace").strip()
        if not text:
            return None, "pdf_without_extractable_text"
        return text, None

    def _read_pdf(self, path: Path) -> Tuple[Optional[str], Optional[str]]:
        try:
            if path.stat().st_size > self.max_pdf_bytes:
                return None, "pdf_too_large"
        except OSError as exc:
            return None, f"stat_error:{exc}"

        text, error = self._extract_pdf_with_python(path)
        if text:
            return text, None

        fallback_text, fallback_error = self._extract_pdf_with_pdftotext(path)
        if fallback_text:
            return fallback_text, None

        return None, f"{error};{fallback_error}"

    @staticmethod
    def _is_placeholder_secret(value: Any) -> bool:
        if value is None:
            return True
        if not isinstance(value, str):
            return False
        normalized = value.strip().casefold()
        if normalized in {
            "", "null", "none", "~", '""', "''", "<empty>", "<redacted>",
            "changeme", "example", "placeholder", "your-value-here",
        }:
            return True
        return (
            (value.strip().startswith("${") and value.strip().endswith("}"))
            or (value.strip().startswith("{{") and value.strip().endswith("}}"))
            or value.strip().startswith("env:")
        )

    @classmethod
    def _redact_json_value(cls, value: Any) -> Tuple[Any, int]:
        redactions = 0
        if isinstance(value, dict):
            output: Dict[str, Any] = {}
            for key, child in value.items():
                if SECRET_KEY_PATTERN.search(str(key)) and not cls._is_placeholder_secret(child):
                    output[key] = "<REDACTED>"
                    redactions += 1
                else:
                    output[key], child_count = cls._redact_json_value(child)
                    redactions += child_count
            return output, redactions
        if isinstance(value, list):
            output_list: List[Any] = []
            for child in value:
                redacted_child, child_count = cls._redact_json_value(child)
                output_list.append(redacted_child)
                redactions += child_count
            return output_list, redactions
        if isinstance(value, str):
            redacted = value
            redacted, bearer_count = BEARER_RE.subn("Bearer <REDACTED>", redacted)
            redactions += bearer_count
            redacted, url_count = URL_CREDENTIAL_RE.subn(
                lambda m: f"{m.group('scheme')}{m.group('user')}:<REDACTED>@",
                redacted,
            )
            redactions += url_count
            return redacted, redactions
        return value, redactions

    @classmethod
    def _redact_config_secrets(cls, content: str) -> Tuple[str, int]:
        # JSON is parsed recursively so secrets are redacted even in minified or
        # single-line files such as package.json.
        try:
            parsed = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            parsed = None

        if parsed is not None:
            redacted_json, count = cls._redact_json_value(parsed)
            return (
                json.dumps(redacted_json, indent=2, ensure_ascii=False) + "\n",
                count,
            )

        redactions = 0
        output_lines: List[str] = []
        for line in content.splitlines():
            match = KEY_VALUE_SECRET_RE.match(line)
            if match:
                value = match.group("value").strip().rstrip(",")
                if not cls._is_placeholder_secret(value.strip("\"'")):
                    line = (
                        match.group("prefix")
                        + '"<REDACTED>"'
                        + match.group("suffix")
                    )
                    redactions += 1

            line, bearer_count = BEARER_RE.subn("Bearer <REDACTED>", line)
            redactions += bearer_count
            line, url_count = URL_CREDENTIAL_RE.subn(
                lambda m: f"{m.group('scheme')}{m.group('user')}:<REDACTED>@",
                line,
            )
            redactions += url_count
            output_lines.append(line)

        suffix = "\n" if content.endswith("\n") else ""
        return "\n".join(output_lines) + suffix, redactions

    @staticmethod
    def _file_sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as file_obj:
            for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _ingest_content(
        self,
        path: Path,
        content: str,
        file_kind: Literal["pdf", "code", "config", "documentation"],
        ownership: Literal["owned", "external", "raw_data"],
        redactions: int = 0,
    ) -> Dict[str, Any]:
        stat = path.stat()
        source_key = self._source_key(path)
        self._seen_source_keys.add(source_key)

        tags = [
            "ingested",
            file_kind,
            ownership,
            self._project_name(path),
        ]
        metadata: Dict[str, Any] = {
            "source_key": source_key,
            "source_path": str(path.resolve()),
            "project_root": str(self.project_root),
            "project": self._project_name(path),
            "file_kind": file_kind,
            "ownership": ownership,
            "extension": path.suffix.lower(),
            "size_bytes": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "file_sha256": self._file_sha256(path),
            "ingested_at": _utc_now(),
            "ingested_by": "repository_ingester",
            "redactions": redactions,
        }
        entry_type = {
            "pdf": "document",
            "code": "source_code",
            "config": "configuration",
            "documentation": "documentation",
        }[file_kind]

        return self.broker.store(
            content=content,
            entry_type=entry_type,
            metadata=metadata,
            tags=tags,
            source="repository-indexer",
            identity_key=source_key,
            supersede_same_source=True,
        )

    def _ingest_pdf_roots(
        self,
        report: Dict[str, Any],
        processed_paths: Set[Path],
    ) -> None:
        for root in self.pdf_roots:
            if not root.exists():
                report["missing_roots"].append(str(root))
                continue
            for path in self._walk_files(root):
                resolved = path.resolve()
                if resolved in processed_paths:
                    continue
                if path.suffix.lower() != ".pdf":
                    continue
                processed_paths.add(resolved)

                text, error = self._read_pdf(path)
                if not text:
                    report["skipped"].append({"path": str(path), "reason": error})
                    continue

                try:
                    self._ingest_content(
                        path,
                        text,
                        file_kind="pdf",
                        ownership="raw_data",
                    )
                    report["ingested"]["pdf"] += 1
                except OSError as exc:
                    report["errors"].append({"path": str(path), "error": str(exc)})

    def _ingest_repository(
        self,
        report: Dict[str, Any],
        processed_paths: Set[Path],
    ) -> None:
        if not self.project_root.exists():
            report["missing_roots"].append(str(self.project_root))
            return

        for path in self._walk_files(self.project_root):
            resolved = path.resolve()
            if resolved in processed_paths:
                continue
            if self._is_private_file(path):
                report["skipped"].append({"path": str(path), "reason": "private_file"})
                continue

            owned = self._is_owned_path(path)
            file_kind: Optional[Literal["code", "config", "documentation"]] = None

            if self._is_config_file(path):
                file_kind = "config"
            elif owned and self._is_code_file(path):
                file_kind = "code"
            elif owned and self._is_document_file(path):
                file_kind = "documentation"
            else:
                # This is the key policy: external project source code is ignored.
                continue

            processed_paths.add(resolved)
            content, error = self._read_text(path)
            if content is None:
                report["skipped"].append({"path": str(path), "reason": error})
                continue
            if not content.strip():
                report["skipped"].append({"path": str(path), "reason": "empty_file"})
                continue

            redactions = 0
            if file_kind == "config" and self.redact_secrets:
                content, redactions = self._redact_config_secrets(content)

            try:
                self._ingest_content(
                    path,
                    content,
                    file_kind=file_kind,
                    ownership="owned" if owned else "external",
                    redactions=redactions,
                )
                report["ingested"][file_kind] += 1
                report["redactions"] += redactions
            except OSError as exc:
                report["errors"].append({"path": str(path), "error": str(exc)})

    def ingest(self, prune_missing: bool = False) -> Dict[str, Any]:
        """Run a complete ingestion and return a machine-readable report."""
        started = time.monotonic()
        self._seen_source_keys.clear()
        report: Dict[str, Any] = {
            "project_root": str(self.project_root),
            "memory_dir": str(self.broker.memory_dir),
            "own_projects": [str(path) for path in self.own_projects],
            "pdf_roots": [str(path) for path in self.pdf_roots],
            "ingested": {
                "pdf": 0,
                "code": 0,
                "config": 0,
                "documentation": 0,
            },
            "redactions": 0,
            "superseded_missing": 0,
            "missing_roots": [],
            "skipped": [],
            "errors": [],
        }
        processed_paths: Set[Path] = set()

        self._ingest_pdf_roots(report, processed_paths)
        self._ingest_repository(report, processed_paths)

        if prune_missing:
            root_key = "repo:"
            report["superseded_missing"] = self.broker.mark_missing_sources(
                self._seen_source_keys,
                root_key=root_key,
            )

        report["duration_seconds"] = round(time.monotonic() - started, 3)
        report["active_source_keys_seen"] = len(self._seen_source_keys)
        return report


def _path_list(values: Optional[Sequence[str]]) -> List[Path]:
    return [Path(value).expanduser() for value in (values or [])]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Hermes persistent memory and repository knowledge ingester."
    )
    parser.add_argument(
        "--memory-dir",
        default=os.getenv("HERMES_MEMORY_DIR"),
        help="Memory directory (or HERMES_MEMORY_DIR).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest PDFs, owned code/docs and safe configs.",
    )
    ingest_parser.add_argument(
        "--project-root",
        default=os.getenv("HERMES_PROJECT_ROOT", str(DEFAULT_PROJECT_ROOT)),
    )
    ingest_parser.add_argument(
        "--own-project",
        action="append",
        default=[],
        help="Owned project path; repeat for multiple projects.",
    )
    ingest_parser.add_argument(
        "--pdf-root",
        action="append",
        default=[],
        help="PDF root; repeat for multiple roots.",
    )
    ingest_parser.add_argument(
        "--max-text-mb",
        type=float,
        default=2.0,
        help="Maximum text/config/code file size in MiB.",
    )
    ingest_parser.add_argument(
        "--max-pdf-mb",
        type=float,
        default=100.0,
        help="Maximum PDF size in MiB.",
    )
    ingest_parser.add_argument(
        "--no-redact-secrets",
        action="store_true",
        help="Disable config secret redaction (not recommended).",
    )
    ingest_parser.add_argument(
        "--prune-missing",
        action="store_true",
        help="Supersede indexed repository files that no longer exist.",
    )

    search_parser = subparsers.add_parser("search", help="Search stored knowledge.")
    search_parser.add_argument("query", nargs="?", default=None)
    search_parser.add_argument("--type", dest="entry_type")
    search_parser.add_argument("--tag", action="append", default=[])
    search_parser.add_argument("--source")
    search_parser.add_argument("--limit", type=int, default=20)
    search_parser.add_argument("--include-archived", action="store_true")
    search_parser.add_argument("--include-superseded", action="store_true")
    search_parser.add_argument("--case-sensitive", action="store_true")
    search_parser.add_argument("--full", action="store_true")

    subparsers.add_parser("stats", help="Show memory statistics.")
    subparsers.add_parser("cleanup", help="Persist expiration cleanup.")

    return parser


def _print_search_results(
    broker: KnowledgeBroker,
    results: Sequence[Dict[str, Any]],
    full: bool,
) -> None:
    serializable: List[Dict[str, Any]] = []
    for entry in results:
        item = dict(entry)
        if full:
            item["content"] = broker.retrieve_full_content(
                entry["id"],
                include_inactive=True,
            )
        serializable.append(item)
    print(json.dumps(serializable, indent=2, ensure_ascii=False, default=str))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    broker = KnowledgeBroker(memory_dir=args.memory_dir)

    if args.command == "ingest":
        ingester = RepositoryIngester(
            broker=broker,
            project_root=Path(args.project_root),
            own_projects=_path_list(args.own_project),
            pdf_roots=_path_list(args.pdf_root) or None,
            max_text_bytes=max(1, int(args.max_text_mb * 1024 * 1024)),
            max_pdf_bytes=max(1, int(args.max_pdf_mb * 1024 * 1024)),
            redact_secrets=not args.no_redact_secrets,
        )
        report = ingester.ingest(prune_missing=args.prune_missing)
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
        return 1 if report["errors"] else 0

    if args.command == "search":
        results = broker.search(
            query=args.query,
            entry_type=args.entry_type,
            tags=args.tag or None,
            source=args.source,
            include_archived=args.include_archived,
            include_superseded=args.include_superseded,
            limit=args.limit,
            case_sensitive=args.case_sensitive,
        )
        _print_search_results(broker, results, full=args.full)
        return 0

    if args.command == "stats":
        print(json.dumps(broker.get_stats(), indent=2, ensure_ascii=False))
        return 0

    if args.command == "cleanup":
        count = broker.cleanup_expired()
        print(json.dumps({"newly_archived": count}, indent=2))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
