"""Capture bounded, reviewable public-site evidence for opt-in GitHub Actions runs.

This is a fixed-target maintainer utility, not a generic URL fetcher.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import httpx

from agent_readiness.cli import get, guard
from agent_readiness.snapshot import snapshot_audit
from agent_readiness.review import make_template

TARGETS = (
    "https://www.python.org",
    "https://www.djangoproject.com",
    "https://www.wikipedia.org",
)
RESOURCES = {"index.html": "", "robots.txt": "/robots.txt", "sitemap.xml": "/sitemap.xml"}
MAX_BYTES = 1_000_000


def collect_one(url: str, root: Path, client: httpx.Client) -> dict:
    """Capture raw bytes from the same requests that will be audited offline."""
    if url not in TARGETS:
        raise ValueError("Only reviewed, fixed public targets are allowed")
    guard(url)
    folder = root / url.removeprefix("https://").replace(".", "_")
    folder.mkdir(parents=True, exist_ok=True)
    observed_at = datetime.now(timezone.utc).isoformat()
    record = {"target": url, "observed_at_utc": observed_at, "resources": {}, "status": "incomplete"}
    manifest = {"url": url, "sha256": {}}

    for filename, suffix in RESOURCES.items():
        resource_url = urljoin(url, suffix) if suffix else url
        # get() enforces HTTPS, public-IP checks, response size, no redirects and timeouts.
        body, detail = get(client, resource_url)
        item = {"url": resource_url, "result": detail}
        if isinstance(body, str):
            raw = body.encode("utf-8")
            if len(raw) > MAX_BYTES:
                item["result"] = "Decoded resource exceeds 1 MB"
            else:
                (folder / filename).write_bytes(raw)
                digest = hashlib.sha256(raw).hexdigest()
                manifest["sha256"][filename] = digest
                item["sha256"] = digest
                item["bytes"] = len(raw)
        record["resources"][filename] = item

    (folder / "collection.json").write_text(json.dumps(record, indent=2) + "\n")
    if not (folder / "index.html").is_file():
        record["status"] = "blocked"
        (folder / "collection.json").write_text(json.dumps(record, indent=2) + "\n")
        return record

    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    report = snapshot_audit(folder)
    (folder / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (folder / "review.json").write_text(json.dumps(make_template(report), indent=2) + "\n")
    record["status"] = "candidate"
    (folder / "collection.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main() -> None:
    root = Path("audit-results")
    root.mkdir(exist_ok=True)
    results = []
    with httpx.Client(timeout=httpx.Timeout(8, connect=4), trust_env=False) as client:
        for target in TARGETS:
            try:
                results.append(collect_one(target, root, client))
            except (OSError, ValueError, httpx.HTTPError) as exc:
                results.append({"target": target, "status": "error", "error": str(exc)})
    (root / "summary.json").write_text(json.dumps({
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "note": "Candidate observations only; independent review required. Raw evidence may be copyrighted.",
    }, indent=2) + "\n")
    print("Collected", sum(r["status"] == "candidate" for r in results), "candidate audit(s)")
    for item in results:
        print(item["target"], item["status"])


if __name__ == "__main__":
    main()
