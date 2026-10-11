"""Snapshot evidence integrity and tampering checks."""
import hashlib
import json
import pytest
from agent_readiness.snapshot import snapshot_audit

HTML='<html lang="en"><head><title>Example</title></head><body><main>Hi</main></body></html>'

def setup(tmp_path):
    (tmp_path/"index.html").write_text(HTML)
    return tmp_path

def manifest(folder,sha256):
    (folder/"manifest.json").write_text(json.dumps({"url":"https://example.com","sha256":sha256}))

def test_verified_snapshot_returns_fingerprint(tmp_path):
    folder=setup(tmp_path)
    digest=hashlib.sha256((folder/"index.html").read_bytes()).hexdigest()
    manifest(folder,{"index.html":digest})
    report=snapshot_audit(folder)
    assert report["evidence_sha256"]["index.html"]==digest

def test_tampered_snapshot_rejected(tmp_path):
    folder=setup(tmp_path)
    digest=hashlib.sha256((folder/"index.html").read_bytes()).hexdigest()
    manifest(folder,{"index.html":digest})
    (folder/"index.html").write_text("changed")
    with pytest.raises(ValueError,match="mismatch"):
        snapshot_audit(folder)

def test_invalid_digest_rejected(tmp_path):
    folder=setup(tmp_path)
    manifest(folder,{"index.html":"invalid"})
    with pytest.raises(ValueError,match="Invalid SHA-256"):
        snapshot_audit(folder)

def test_checksum_for_missing_file_rejected(tmp_path):
    folder=setup(tmp_path)
    manifest(folder,{"robots.txt":"a"*64})
    with pytest.raises(ValueError,match="missing snapshot"):
        snapshot_audit(folder)

def test_unsupported_checksum_filename_rejected(tmp_path):
    folder=setup(tmp_path)
    manifest(folder,{"../../outside":"a"*64})
    with pytest.raises(ValueError,match="unsupported filename"):
        snapshot_audit(folder)

def test_symlink_rejected(tmp_path):
    folder=setup(tmp_path)
    manifest(folder,{})
    (folder/"robots.txt").symlink_to(folder/"index.html")
    with pytest.raises(ValueError,match="symlinks"):
        snapshot_audit(folder)

def test_legacy_manifest_without_checksums_still_works(tmp_path):
    folder=setup(tmp_path)
    (folder/"manifest.json").write_text('{"url":"https://example.com"}')
    report=snapshot_audit(folder)
    assert "index.html" in report["evidence_sha256"]
