"""Offline website snapshot audit. Never creates an HTTP client."""
from __future__ import annotations
import json
import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit, urljoin
import typer
from .core import evaluate

MAX_BYTES = 1_000_000

def snapshot_audit(directory: Path, *, profile: str = "website") -> dict:
    manifest_path = directory / "manifest.json"
    if manifest_path.stat().st_size > MAX_BYTES:
        raise ValueError("Manifest exceeds 1 MB")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    url = manifest.get("url")
    if not isinstance(url,str) or urlsplit(url).scheme != "https" or not urlsplit(url).hostname:
        raise ValueError("Manifest must declare a valid HTTPS URL")
    checksums = manifest.get("sha256", {})
    if not isinstance(checksums, dict):
        raise ValueError("sha256 must be a filename-to-digest mapping")
    files = {"index.html":url, "robots.txt":urljoin(url,"/robots.txt"),
             "sitemap.xml":urljoin(url,"/sitemap.xml")}
    api_url = manifest.get("api_url")
    if api_url is not None:
        if not isinstance(api_url,str) or urlsplit(api_url).scheme != "https" or urlsplit(api_url).hostname != urlsplit(url).hostname:
            raise ValueError("api_url must be HTTPS on the same hostname")
        files["openapi.json"] = api_url
    if any(name not in files for name in checksums):
        raise ValueError("sha256 contains an unsupported filename")
    evidence={}
    fingerprints={}
    for filename,target in files.items():
        path=directory / filename
        if path.is_symlink():
            raise ValueError(f"Snapshot symlinks are not allowed: {filename}")
        if not path.is_file():
            evidence[target]=(None,"Not supplied in snapshot")
            continue
        if path.stat().st_size > MAX_BYTES:
            evidence[target]=(None,"Snapshot file exceeds 1 MB")
            continue
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        expected = checksums.get(filename)
        if expected is not None:
            if not isinstance(expected,str) or not re.fullmatch(r"[a-fA-F0-9]{64}",expected):
                raise ValueError(f"Invalid SHA-256 digest for {filename}")
            if digest != expected.lower():
                raise ValueError(f"SHA-256 mismatch for {filename}")
        fingerprints[filename] = digest
        evidence[target]=(raw.decode("utf-8",errors="replace"),"Local snapshot: "+filename)
    if any(name not in fingerprints for name in checksums):
        raise ValueError("Checksum declared for missing snapshot file")
    if not isinstance(evidence[url][0],str):
        raise ValueError("Snapshot must include index.html")
    result=evaluate(url,profile,api_url,fetch=lambda target:evidence.get(target,(None,"Not supplied in snapshot")))
    result["source"]="offline_snapshot"
    result["evidence_sha256"]=fingerprints
    result["disclaimer"] += " Snapshot evidence may be stale or incomplete."
    return result

def snapshot_command(directory: Path, profile: str = "website", output: str = "json"):
    """Audit saved evidence without network access."""
    if output not in {"json","terminal"}:
        raise typer.BadParameter("output must be json or terminal")
    try:
        result=snapshot_audit(directory,profile=profile)
    except (OSError,ValueError,TypeError,KeyError) as exc:
        typer.echo(f"Snapshot error: {exc}",err=True)
        raise typer.Exit(2) from exc
    if output=="json":
        typer.echo(json.dumps(result,indent=2))
    else:
        typer.echo(f"Snapshot score: {result['score']}/100")
        for item in result["findings"]:
            typer.echo(f"{item['status']:7} {item['id']}: {item['evidence']}")
