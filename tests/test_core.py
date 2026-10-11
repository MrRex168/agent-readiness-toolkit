"""Offline fixtures for scoring and applicability."""
import json
from unittest.mock import patch
import httpx
from agent_readiness.core import evaluate

HTML = '<html lang="en"><head><title>Acme</title><meta name="description" content="Acme"><script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Acme"}</script></head><body><main>Hi</main></body></html>'

def client_for(html=HTML, api=None, robots=200):
    def handler(request):
        p=request.url.path
        if p=="/":
            return httpx.Response(200,text=html,headers={"content-type":"text/html"})
        if p=="/robots.txt":
            return httpx.Response(robots,text="User-agent: *" if robots==200 else "")
        if p=="/sitemap.xml":
            return httpx.Response(200,text="<urlset></urlset>")
        if p=="/openapi.json":
            return httpx.Response(200,text=json.dumps(api or {}))
        return httpx.Response(404)
    return httpx.Client(transport=httpx.MockTransport(handler))

@patch("agent_readiness.cli.guard",side_effect=lambda x:x)
def test_good_site(mock):
    with client_for() as client:
        result=evaluate("https://example.com",client=client)
    assert result["score"]==100
    assert all(x["status"]=="pass" for x in result["findings"])

@patch("agent_readiness.cli.guard",side_effect=lambda x:x)
def test_missing_jsonld(mock):
    with client_for("<html><body>Hello</body></html>") as client:
        result=evaluate("https://example.com",client=client)
    assert result["score"]<100
    assert next(x for x in result["findings"] if x["id"]=="jsonld")["fix"]

@patch("agent_readiness.cli.guard",side_effect=lambda x:x)
def test_api_unknown_not_failure(mock):
    with client_for() as client:
        result=evaluate("https://example.com",profile="api",client=client)
    assert result["score"]==100
    assert next(x for x in result["findings"] if x["id"]=="openapi")["status"]=="unknown"

@patch("agent_readiness.cli.guard",side_effect=lambda x:x)
def test_valid_api(mock):
    spec={"openapi":"3.1.0","info":{"title":"API","version":"1"},"paths":{}}
    with client_for(api=spec) as client:
        result=evaluate("https://example.com",profile="api",api_url="https://example.com/openapi.json",client=client)
    assert result["score"]==100

@patch("agent_readiness.cli.guard",side_effect=lambda x:x)
def test_missing_robots_reduces_score(mock):
    with client_for(robots=404) as client:
        result=evaluate("https://example.com",client=client)
    assert result["score"]<100
