#!/usr/bin/env python3
"""
Basic Memory Utilities for Hermes Agent Memory System.
Provides simple in-memory storage and retrieval operations.
"""

import os
import json
import hashlib
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class BasicMemory:
    """Simple key-value memory store with persistence."""

    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            memory_dir = os.getenv("HERMES_MEMORY_DIR", "/home/fernando/ai-ecosystem/sharememory/hermes_memory")
        self.memory_dir = Path(memory_dir)
        # Keep the legacy key/value format separate from KnowledgeBroker's
        # structured memory.json. Older BasicMemory files are migrated only
        # when their schema is unambiguously key/value.
        self.memory_file = self.memory_dir / "basic_memory.json"
        self.legacy_memory_file = self.memory_dir / "memory.json"
        self._ensure_dir()
        self._load()

    def _ensure_dir(self):
        """Ensure memory directory exists."""
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def _load(self):
        """Load memory from disk."""
        if not self.memory_file.exists() and self.legacy_memory_file.exists():
            try:
                with self.legacy_memory_file.open("r", encoding="utf-8") as handle:
                    legacy = json.load(handle)
                if isinstance(legacy, dict) and all(
                    isinstance(entry, dict)
                    and entry.get("key") == key
                    and "value" in entry
                    for key, entry in legacy.items()
                ):
                    self._data = legacy
                    self._save()
                    return
            except (json.JSONDecodeError, OSError, TypeError):
                pass
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._data = {}
        else:
            self._data = {}

    def _save(self):
        """Save memory to disk."""
        fd, temp_name = tempfile.mkstemp(
            prefix="basic-memory-",
            suffix=".tmp",
            dir=str(self.memory_dir),
            text=True,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self._data, handle, indent=2, default=str)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.memory_file)
        except Exception:
            Path(temp_name).unlink(missing_ok=True)
            raise

    def store(self, key: str, value: Any, tags: List[str] = None) -> Dict[str, Any]:
        """Store a value with optional tags."""
        entry = {
            "key": key,
            "value": value,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
            "hash": hashlib.sha256(str(value).encode()).hexdigest()[:12]
        }
        self._data[key] = entry
        self._save()
        return entry

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        entry = self._data.get(key)
        return entry["value"] if entry else None

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memory by query string."""
        results = []
        query_lower = query.lower()
        for key, entry in self._data.items():
            if query_lower in key.lower() or query_lower in str(entry.get("value", "")).lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    def delete(self, key: str) -> bool:
        """Delete a key from memory."""
        if key in self._data:
            del self._data[key]
            self._save()
            return True
        return False

    def list_keys(self) -> List[str]:
        """List all keys in memory."""
        return list(self._data.keys())


def generate_id(content: str) -> str:
    """Generate a unique ID from content hash."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def content_hash(content: str) -> str:
    """Generate hash for content verification."""
    return hashlib.sha256(content.encode()).hexdigest()


if __name__ == "__main__":
    # Simple test
    mem = BasicMemory()
    mem.store("test_key", {"data": "test_value"}, tags=["test"])
    print(f"Stored: {mem.retrieve('test_key')}")
    print(f"Keys: {mem.list_keys()}")
