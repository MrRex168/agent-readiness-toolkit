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
from .compare import reports as compare_reports
app.command("compare")(compare_reports)
from .benchmark import benchmark_command
app.command("benchmark")(benchmark_command)


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
    """Backward-compatible alias for the single audit engine.

    New integrations should import evaluate from agent_readiness.core.
    """
    return evaluate(url, profile, api_url, client)


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
