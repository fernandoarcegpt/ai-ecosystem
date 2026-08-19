from scripts.validate_documentation_index import validate


def test_documentation_index_is_complete_and_consistent():
    report = validate()
    assert report["status"] == "passed", report["errors"]
