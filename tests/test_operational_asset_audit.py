"""The operational documentation, skills and service entrypoints stay valid."""

from scripts.audit_operational_assets import audit


def test_operational_asset_audit_passes():
    report = audit()
    assert report["status"] == "passed", report
