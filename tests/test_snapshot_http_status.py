"""Regression tests for confirmed HTTP failures in saved evidence."""
import json
import pytest
from agent_readiness.snapshot import snapshot_audit
from scripts.collect_validation_evidence import collect_one
from unittest.mock import patch

HTML = '<html lang="en"><head><title>Example</title><meta name="description" content="Example"><script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization"}</script></head><body><main>Hi</main></body></html>'

def setup(tmp_path, statuses=None):
    (tmp_path/"index.html").write_text(HTML)
    manifest={"url":"https://example.com"}
    if statuses is not None:
        manifest["http_status"]=statuses
    (tmp_path/"manifest.json").write_text(json.dumps(manifest))
    return tmp_path

def finding(report, key):
    return next(x for x in report["findings"] if x["id"]==key)

def test_http_404_is_fail_and_changes_denominator(tmp_path):
    report=snapshot_audit(setup(tmp_path,{"sitemap.xml":404}))
    assert finding(report,"sitemap")["status"]=="fail"
    assert "HTTP 404" in finding(report,"sitemap")["evidence"]
    assert report["score_basis"]["applicable_weight"]==65

def test_missing_optional_file_without_status_is_unknown(tmp_path):
    report=snapshot_audit(setup(tmp_path))
    assert finding(report,"sitemap")["status"]=="unknown"

@pytest.mark.parametrize("value",[True,200,302,600,"404",None])
def test_invalid_status_rejected(tmp_path,value):
    with pytest.raises(ValueError,match="HTTP 4xx or 5xx"):
        snapshot_audit(setup(tmp_path,{"sitemap.xml":value}))

def test_unknown_resource_key_rejected(tmp_path):
    with pytest.raises(ValueError,match="http_status"):
        snapshot_audit(setup(tmp_path,{"../../bad":404}))

def test_conflicting_file_and_http_failure_rejected(tmp_path):
    folder=setup(tmp_path,{"sitemap.xml":404})
    (folder/"sitemap.xml").write_text("<urlset/>")
    with pytest.raises(ValueError,match="Conflicting"):
        snapshot_audit(folder)

def test_collector_preserves_404_and_avoids_false_unknown(tmp_path):
    url="https://www.python.org"
    responses={
        url:(HTML,"HTTP 200"),
        url+"/robots.txt":("User-agent: *\nAllow: /","HTTP 200"),
        url+"/sitemap.xml":(False,"HTTP 404"),
    }
    with patch("scripts.collect_validation_evidence.guard",side_effect=lambda u:u),patch("scripts.collect_validation_evidence.get",side_effect=lambda client,target:responses[target]):
        result=collect_one(url,tmp_path,object())
    assert result["status"]=="candidate"
    folder=tmp_path/"www_python_org"
    manifest=json.loads((folder/"manifest.json").read_text())
    assert manifest["http_status"]=={"sitemap.xml":404}
    report=json.loads((folder/"report.json").read_text())
    assert finding(report,"sitemap")["status"]=="fail"
    assert "HTTP 404" in finding(report,"sitemap")["evidence"]
    assert not (folder/"sitemap.xml").exists()
