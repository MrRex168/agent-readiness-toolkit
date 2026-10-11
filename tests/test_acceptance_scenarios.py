"""Offline acceptance scenarios for website and API audits."""
from __future__ import annotations
import json
from unittest.mock import patch
import httpx
import pytest
from agent_readiness.core import evaluate

BASE = '<html lang="en"><head><title>Example Co</title><meta name="description" content="Services"><script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Example Co"}</script></head><body><main>Services</main></body></html>'
SPEC = {"openapi":"3.1.0","info":{"title":"Example API","version":"1.0"},"paths":{"/items":{"get":{"responses":{"200":{"description":"ok"}}}}}}

def fixture_client(*,html=BASE,robots="User-agent: *\\nAllow: /",sitemap='<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>',spec=SPEC):
    def respond(request):
        value={"/":html,"/robots.txt":robots,"/sitemap.xml":sitemap,"/openapi.json":json.dumps(spec)}.get(request.url.path)
        return httpx.Response(200,text=value) if value is not None else httpx.Response(404)
    return httpx.Client(transport=httpx.MockTransport(respond),trust_env=False)

@pytest.fixture(autouse=True)
def no_real_dns():
    with patch("agent_readiness.cli.guard",side_effect=lambda value:value):
        yield

def statuses(result):
    return {f["id"]:f["status"] for f in result["findings"]}

def test_complete_business_site():
    with fixture_client() as client:
        result=evaluate("https://example.com",client=client)
    assert result["score"]==100
    assert all(value=="pass" for value in statuses(result).values())

def test_missing_metadata_is_observable_failure():
    with fixture_client(html="<html><body><main>Visible text</main></body></html>") as client:
        result=evaluate("https://example.com",client=client)
    assert statuses(result)["title"]=="fail"
    assert statuses(result)["description"]=="fail"
    assert statuses(result)["jsonld"]=="fail"

def test_sitemap_index_is_not_false_failure():
    with fixture_client(sitemap='<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>') as client:
        result=evaluate("https://example.com",client=client)
    assert statuses(result)["sitemap"]=="pass"

def test_invalid_sitemap_fails():
    with fixture_client(sitemap="<html>not a sitemap</html>") as client:
        result=evaluate("https://example.com",client=client)
    assert statuses(result)["sitemap"]=="fail"

def test_untyped_jsonld_fails():
    html=BASE.replace('"@type":"Organization",',"")
    with fixture_client(html=html) as client:
        result=evaluate("https://example.com",client=client)
    assert statuses(result)["jsonld"]=="fail"

def test_api_with_spec():
    with fixture_client() as client:
        result=evaluate("https://example.com",profile="api",api_url="https://example.com/openapi.json",client=client)
    assert statuses(result)["openapi"]=="pass"
    assert result["score"]==100

def test_api_without_advertised_spec_is_unknown():
    with fixture_client() as client:
        result=evaluate("https://example.com",profile="api",client=client)
    assert statuses(result)["openapi"]=="unknown"
    assert result["score"]==100

def test_invalid_api_spec_fails():
    with fixture_client(spec={"message":"not OpenAPI"}) as client:
        result=evaluate("https://example.com",profile="api",api_url="https://example.com/openapi.json",client=client)
    assert statuses(result)["openapi"]=="fail"

def test_no_live_http_ever_needed():
    with fixture_client() as client:
        result=evaluate("https://example.com",client=client)
    assert result["target"]=="https://example.com"
