"""Tests for large-material inventory, chunking and duplicate detection."""

from improvement.corpus_evaluator import CorpusEvaluator


def test_large_text_is_chunked_and_duplicate_is_detected(tmp_path):
    content = ("evidence-backed material\n" * 3000)
    first = tmp_path / "book.txt"
    second = tmp_path / "copy.md"
    first.write_text(content, encoding="utf-8")
    second.write_text(content, encoding="utf-8")

    report = CorpusEvaluator(chunk_characters=5000).evaluate(
        [str(first), str(second)]
    )

    assert report["total_files"] == 2
    assert report["total_chunks"] > 2
    assert report["duplicates"] == 1
    assert report["files"][1]["duplicate_of"] == str(first.resolve())


def test_unsupported_material_fails_explicitly(tmp_path):
    material = tmp_path / "book.bin"
    material.write_bytes(b"not a supported document")
    try:
        CorpusEvaluator().evaluate([str(material)])
    except ValueError as exc:
        assert "Unsupported material type" in str(exc)
    else:
        raise AssertionError("Unsupported material should not be accepted")
