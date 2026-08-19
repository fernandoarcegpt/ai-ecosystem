"""Deterministic inventory and chunk evaluation for large local materials."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Iterable, List


TEXT_SUFFIXES = {".txt", ".md", ".rst", ".adoc"}


class CorpusEvaluator:
    """Measure readable material without sending its contents to a model."""

    def __init__(self, chunk_characters: int = 12000):
        if chunk_characters < 1000:
            raise ValueError("chunk_characters must be at least 1000")
        self.chunk_characters = chunk_characters

    @staticmethod
    def _read(path: Path) -> str:
        if path.suffix.lower() in TEXT_SUFFIXES:
            return path.read_text(encoding="utf-8", errors="replace")
        if path.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise RuntimeError("pypdf is required to evaluate PDF files") from exc
            return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        raise ValueError(f"Unsupported material type: {path.suffix or '<none>'}")

    def evaluate(self, paths: Iterable[str]) -> Dict[str, Any]:
        files: List[Dict[str, Any]] = []
        seen_hashes: Dict[str, str] = {}
        for raw_path in paths:
            path = Path(raw_path).expanduser().resolve()
            text = self._read(path)
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            chunks = [
                text[index : index + self.chunk_characters]
                for index in range(0, len(text), self.chunk_characters)
            ]
            files.append(
                {
                    "path": str(path),
                    "sha256": digest,
                    "characters": len(text),
                    "words": len(text.split()),
                    "chunks": len(chunks),
                    "empty_chunks": sum(not chunk.strip() for chunk in chunks),
                    "duplicate_of": seen_hashes.get(digest),
                }
            )
            seen_hashes.setdefault(digest, str(path))
        return {
            "files": files,
            "total_files": len(files),
            "total_characters": sum(item["characters"] for item in files),
            "total_chunks": sum(item["chunks"] for item in files),
            "duplicates": sum(item["duplicate_of"] is not None for item in files),
        }


__all__ = ["CorpusEvaluator", "TEXT_SUFFIXES"]
