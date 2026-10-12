"""Bounded evidence collector regression tests."""
import json
from unittest.mock import patch

from scripts.collect_validation_evidence import collect_one


class FakeClient:
    pass


def test_capture_success_creates_reviewable_snapshot(tmp_path):
    responses = {
        "https://www.python.org": ('<html lang="en"><head><title>Python</title></head><body><main>Hi</main></body></html>',"HTTP 200"),
        "https://www.python.org/robots.txt": ("User-agent: *\nAllow: /","HTTP 200"),
        "https://www.python.org/sitemap.xml": ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>',"HTTP 200"),
    }
    with patch("scripts.collect_validation_evidence.guard",side_effect=lambda u:u), patch("scripts.collect_validation_evidence.get",side_effect=lambda client,url:responses[url]):
        result=collect_one("https://www.python.org",tmp_path,FakeClient())
    folder=tmp_path/"www_python_org"
    assert result["status"]=="candidate"
    assert (folder/"index.html").exists()
    assert (folder/"report.json").exists()
    assert json.loads((folder/"review.json").read_text())["expected"]["title"] is None
    assert len(json.loads((folder/"manifest.json").read_text())["sha256"])==3


def test_blocked_homepage_creates_no_empty_report(tmp_path):
    with patch("scripts.collect_validation_evidence.guard",side_effect=lambda u:u), patch("scripts.collect_validation_evidence.get",return_value=(False,"HTTP 403")):
        result=collect_one("https://www.wikipedia.org",tmp_path,FakeClient())
    folder=tmp_path/"www_wikipedia_org"
    assert result["status"]=="blocked"
    assert not (folder/"report.json").exists()
    assert not (folder/"manifest.json").exists()
    assert json.loads((folder/"collection.json").read_text())["resources"]["index.html"]["result"]=="HTTP 403"


def test_arbitrary_target_rejected(tmp_path):
    import pytest
    with pytest.raises(ValueError,match="fixed public targets"):
        collect_one("https://untrusted.example",tmp_path,FakeClient())
