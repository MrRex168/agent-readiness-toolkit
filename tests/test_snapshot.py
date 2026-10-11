"""Offline snapshot end-to-end tests; external networking is forbidden."""
import json
from unittest.mock import patch
from typer.testing import CliRunner
from agent_readiness.cli import app
from agent_readiness.snapshot import snapshot_audit

HTML='<html lang="en"><head><title>Example</title><meta name="description" content="Example"><script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization"}</script></head><body><main>Content</main></body></html>'

def setup(tmp_path,with_robots=True):
    (tmp_path/"manifest.json").write_text(json.dumps({"url":"https://example.com"}))
    (tmp_path/"index.html").write_text(HTML)
    (tmp_path/"sitemap.xml").write_text("<urlset/>")
    if with_robots:
        (tmp_path/"robots.txt").write_text("User-agent: *\nDisallow:")
    return tmp_path

def test_snapshot_is_offline_and_scores_complete_site(tmp_path):
    folder=setup(tmp_path)
    with patch("socket.getaddrinfo",side_effect=AssertionError("DNS attempted")), patch("httpx.Client",side_effect=AssertionError("Network client attempted")):
        result=snapshot_audit(folder)
    assert result["source"]=="offline_snapshot"
    assert result["score"]==100

def test_missing_snapshot_evidence_is_unknown(tmp_path):
    result=snapshot_audit(setup(tmp_path,False))
    robots=next(x for x in result["findings"] if x["id"]=="robots")
    assert robots["status"]=="unknown"
    assert result["score"]==100

def test_cli_outputs_valid_json(tmp_path):
    folder=setup(tmp_path)
    result=CliRunner().invoke(app,["snapshot",str(folder)])
    assert result.exit_code==0, result.output
    assert json.loads(result.output)["source"]=="offline_snapshot"

def test_missing_index_is_rejected(tmp_path):
    folder=setup(tmp_path)
    (folder/"index.html").unlink()
    result=CliRunner().invoke(app,["snapshot",str(folder)])
    assert result.exit_code==2

def test_api_without_spec_is_unknown(tmp_path):
    folder=setup(tmp_path)
    result=snapshot_audit(folder,profile="api")
    assert next(x for x in result["findings"] if x["id"]=="openapi")["status"]=="unknown"
