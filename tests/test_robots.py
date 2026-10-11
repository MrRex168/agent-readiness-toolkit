"""Offline robots.txt evidence checks."""
import pytest
from agent_readiness.robots import robots_evidence

@pytest.mark.parametrize("body",[
    "User-agent: *\nDisallow: /private",
    "User-agent: Googlebot\nAllow: /",
    "# Comment\nUser-agent: *\nSitemap: https://example.com/sitemap.xml",
    "USER-AGENT: *\nDisallow:",
    "User-agent: *\nUnknown-Extension: value",
])
def test_valid_robots_groups(body):
    ok, evidence = robots_evidence(body)
    assert ok and "User-agent" in evidence

@pytest.mark.parametrize("body",[
    "",
    "# no directives",
    "User-agent:",
    "Disallow: /private",
    "User-agent *",
    "User-agent: *\nInvalid line",
])
def test_invalid_robots_groups(body):
    ok, evidence = robots_evidence(body)
    assert not ok and evidence

def test_does_not_claim_crawl_permission():
    ok, evidence = robots_evidence("User-agent: *\nDisallow: /")
    assert ok
    assert "allowed" not in evidence.lower()
