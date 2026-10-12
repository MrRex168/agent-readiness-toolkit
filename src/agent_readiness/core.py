"""Read-only audit checks and evidence-based scoring."""
from __future__ import annotations
import json
from typing import Callable
from urllib.parse import urljoin, urlsplit
import httpx
from bs4 import BeautifulSoup
from .validators import sitemap_valid, jsonld_types
from .robots import robots_evidence
from .openapi import openapi_evidence

def evaluate(url: str, profile: str = "website", api_url: str | None = None, client: httpx.Client | None = None, *, fetch: Callable[[str], tuple[str | bool | None, str]] | None = None) -> dict:
    from .cli import guard, get
    if profile not in {"website", "api"}:
        raise ValueError("profile must be website or api")
    if fetch is None:
        guard(url)
    if api_url and urlsplit(guard(api_url) if fetch is None else api_url).hostname != urlsplit(url).hostname:
        raise ValueError("API URL must share the website hostname")
    own = fetch is None and client is None
    if fetch is None:
        client = client or httpx.Client(timeout=httpx.Timeout(8, connect=4), trust_env=False)
        fetch = lambda target: get(client, target)
    findings = []
    def check(key, value, weight, evidence, fix):
        findings.append({"id":key, "status":"unknown" if value is None else "pass" if value else "fail",
                         "weight":weight, "evidence":evidence, "fix":"" if value else fix})
    try:
        html, detail = fetch(url)
        if not isinstance(html, str):
            raise ValueError("Root HTML unavailable: " + detail)
        soup = BeautifulSoup(html, "html.parser")
        check("title", bool(soup.title and soup.title.get_text(strip=True)), 10, url, "Add descriptive title")
        desc = soup.find("meta", attrs={"name":"description"})
        check("description", bool(desc and desc.get("content", "").strip()), 10, url, "Add accurate meta description")
        check("language", bool(soup.html and soup.html.get("lang")), 5, url, "Set html lang")
        check("main", soup.find("main") is not None, 10, url, "Add main landmark")
        for path, weight, key in [("/robots.txt",10,"robots"),("/sitemap.xml",10,"sitemap")]:
            target = urljoin(url,path)
            body, status = fetch(target)
            if body is None:
                value, evidence = None, status
            elif body is False:
                value, evidence = False, status
            elif key == "robots":
                value, evidence = robots_evidence(body)
            else:
                value, evidence = sitemap_valid(body), "Valid sitemap XML" if sitemap_valid(body) else "Invalid sitemap XML"
            check(key, value, weight, target + ": " + evidence, "Publish a valid " + path)
        valid, types = jsonld_types([s.string or s.get_text() for s in soup.find_all("script", attrs={"type":"application/ld+json"})])
        check("jsonld",valid,20,url+": "+str(types),"Add accurate JSON-LD describing the business")
        if profile == "api":
            if not api_url:
                links = [urljoin(url,e["href"]) for e in soup.find_all("link",href=True) if "openapi" in e["href"].lower()]
                api_url = next((x for x in links if urlsplit(x).hostname == urlsplit(url).hostname),None)
            if not api_url:
                check("openapi",None,25,"No advertised specification","Provide --api-url to validate an API")
            else:
                body,status = fetch(api_url)
                if body is None:
                    check("openapi",None,25,api_url+": "+status,"Make the document accessible")
                else:
                    ok, evidence = openapi_evidence(body) if isinstance(body,str) else (False,status)
                    check("openapi",ok,25,api_url+": "+evidence,"Publish a structurally valid OpenAPI JSON document")
        denominator=sum(x["weight"] for x in findings if x["status"]!="unknown")
        numerator=sum(x["weight"] for x in findings if x["status"]=="pass")
        return {"target":url,"profile":profile,"score":round(numerator*100/denominator) if denominator else None,
                "score_basis":{"passed_weight":numerator,"applicable_weight":denominator},
                "findings":findings,"disclaimer":"Observable technical signals only; not a guarantee of agent discoverability or preference."}
    finally:
        if own:
            client.close()
