"""Evidence-based, read-only website auditor."""
from __future__ import annotations
import ipaddress
import json
import socket
from urllib.parse import urljoin, urlsplit

import httpx
import typer
from bs4 import BeautifulSoup
from .core import evaluate

app = typer.Typer(add_completion=False)


def guard(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("Only public HTTPS hosts on port 443 without credentials are supported")
    host = parsed.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith((".local", ".localhost", ".internal", ".test")):
        raise ValueError("Local hosts are not supported")
    try:
        ips = [ipaddress.ip_address(host)]
    except ValueError:
        ips = [ipaddress.ip_address(record[4][0]) for record in socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)]
    if not ips or any(not ip.is_global for ip in ips):
        raise ValueError("Non-public IP address blocked")
    return url


def get(client: httpx.Client, url: str):
    try:
        # Revalidation is a defense-in-depth check, not DNS pinning.
        # This CLI must not be exposed as a multi-tenant URL fetcher.
        with client.stream("GET", guard(url), follow_redirects=False) as r:
            if r.is_redirect:
                return None, "Redirect was not followed"
            data = bytearray()
            for chunk in r.iter_bytes():
                data.extend(chunk)
                if len(data) > 1_000_000:
                    return None, "Response too large"
            if r.status_code != 200:
                return False, f"HTTP {r.status_code}"
            return bytes(data).decode(r.encoding or "utf-8", errors="replace"), "HTTP 200"
    except (httpx.HTTPError, ValueError, OSError) as exc:
        return None, str(exc)


def audit(url: str, profile: str = "website", api_url: str | None = None, client: httpx.Client | None = None) -> dict:
    guard(url)
    if profile not in ("website", "api"):
        raise ValueError("Profile must be website or api")
    if api_url and urlsplit(guard(api_url)).hostname != urlsplit(url).hostname:
        raise ValueError("API document must be on the same hostname")
    owns = client is None
    client = client or httpx.Client(timeout=httpx.Timeout(8, connect=4), trust_env=False)
    checks = []
    def add(name, status, weight, evidence, fix):
        checks.append({"id": name, "status": "unknown" if status is None else "pass" if status else "fail",
                       "weight": weight, "evidence": evidence, "fix": "" if status else fix})
    try:
        html, evidence = get(client, url)
        if not isinstance(html, str):
            raise ValueError("Root HTML was not inspectable: " + evidence)
        soup = BeautifulSoup(html, "html.parser")
        add("page_title", bool(soup.title and soup.title.get_text(strip=True)), 10, url, "Add a descriptive title")
        description = soup.find("meta", attrs={"name":"description"})
        add("description", bool(description and description.get("content", "").strip()), 10, url, "Add meta description")
        add("html_language", bool(soup.html and soup.html.get("lang")), 5, url, "Set html lang")
        add("semantic_main", soup.find("main") is not None, 10, url, "Add a main landmark")
        for path, weight, needle, name in [("/robots.txt", 10, "user-agent:", "robots_txt"),
                                           ("/sitemap.xml", 10, "<urlset", "sitemap")]:
            target = urljoin(url, path)
            body, why = get(client, target)
            add(name, None if body is None else (isinstance(body, str) and needle in body.lower()), weight,
                f"{target}: {why}", f"Publish valid {path}")
        valid = False
        types = []
        for script in soup.find_all("script", attrs={"type":"application/ld+json"}):
            try:
                item = json.loads(script.string or script.get_text())
                valid = isinstance(item, (dict, list))
                if isinstance(item, dict):
                    types.append(str(item.get("@type", "")))
            except (ValueError, TypeError):
                continue
        add("structured_data", valid, 20, f"{url}: parsed types={types}", "Add accurate JSON-LD for relevant entities")
        if profile == "api":
            if not api_url:
                links = [urljoin(url, link["href"]) for link in soup.find_all("link", href=True)
                         if "openapi" in link["href"].lower()]
                api_url = next((link for link in links if urlsplit(link).hostname == urlsplit(url).hostname), None)
            if not api_url:
                add("openapi_document", None, 25, "No OpenAPI document explicitly advertised", "Supply --api-url")
            else:
                body, why = get(client, api_url)
                if body is None:
                    add("openapi_document", None, 25, f"{api_url}: {why}", "Make advertised spec accessible")
                else:
                    try:
                        document = json.loads(body)
                        valid_api = isinstance(document, dict) and ("openapi" in document or "swagger" in document) and isinstance(document.get("info"), dict) and isinstance(document.get("paths"), dict)
                    except ValueError:
                        valid_api = False
                    add("openapi_document", valid_api, 25, f"{api_url}: {why}", "Provide valid OpenAPI JSON containing info and paths")
        eligible = sum(c["weight"] for c in checks if c["status"] != "unknown")
        passed = sum(c["weight"] for c in checks if c["status"] == "pass")
        return {"target": url, "profile": profile, "score": round(passed*100/eligible) if eligible else None,
                "score_basis": {"passed_weight": passed, "applicable_weight": eligible}, "findings": checks,
                "disclaimer": "Technical indicators only; not evidence of AI ranking, agent preference, or transaction success"}
    finally:
        if owns:
            client.close()


@app.command()
def scan(url: str, profile: str = "website", api_url: str = "", output: str = "terminal"):
    """Scan public HTTPS website or explicitly advertised API."""
    if output not in ("terminal", "json", "markdown"):
        raise typer.BadParameter("output must be terminal, json or markdown")
    try:
        report = evaluate(url, profile, api_url or None)
    except (ValueError, OSError) as exc:
        typer.echo(f"Audit error: {exc}", err=True)
        raise typer.Exit(2) from exc
    if output == "json":
        typer.echo(json.dumps(report, indent=2))
    elif output == "markdown":
        lines = [f"# Agent Readiness: {url}", f"Score: {report['score']}/100", "",
                 "| Check | Status | Evidence | Fix |", "|---|---|---|---|"]
        for f in report["findings"]:
            lines.append("| " + " | ".join(str(f[key]).replace("|", "\\|") for key in ("id", "status", "evidence", "fix")) + " |")
        typer.echo("\n".join(lines))
    else:
        typer.echo(f"Agent Readiness: {report['score']}/100")
        for f in report["findings"]:
            typer.echo(f"  {f['status']:7} {f['id']:20} {f['evidence']}")

if __name__ == "__main__":
    app()
