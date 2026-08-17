#!/usr/bin/env python3
"""
Basic Memory Utilities for Hermes Agent Memory System.
Provides simple in-memory storage and retrieval operations.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class BasicMemory:
    """Simple key-value memory store with persistence."""

    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            memory_dir = os.getenv("HERMES_MEMORY_DIR", "/home/fernando/ai-ecosystem/sharememory/hermes_memory")
        self.memory_dir = Path(memory_dir)
        self.memory_file = self.memory_dir / "memory.json"
        self._ensure_dir()
        self._load()

    def _ensure_dir(self):
        """Ensure memory directory exists."""
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def _load(self):
        """Load memory from disk."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._data = {}
        else:
            self._data = {}

    def _save(self):
        """Save memory to disk."""
        with open(self.memory_file, 'w') as f:
            json.dump(self._data, f, indent=2, default=str)

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