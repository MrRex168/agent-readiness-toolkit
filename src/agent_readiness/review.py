"""Create a blank human-review worksheet from a saved audit report."""
from __future__ import annotations
import json
from pathlib import Path
import typer

MAX_BYTES = 2_000_000

def make_template(report: dict) -> dict:
    if not isinstance(report,dict):
        raise ValueError("Report must be an object")
    if not isinstance(report.get("target"),str) or not report["target"] or report.get("profile") not in {"website","api"}:
        raise ValueError("Report requires target and supported profile")
    findings=report.get("findings")
    if not isinstance(findings,list) or not findings:
        raise ValueError("Report requires non-empty findings")
    checks={}
    for finding in findings:
        if not isinstance(finding,dict):
            raise ValueError("Invalid finding")
        key=finding.get("id")
        if not isinstance(key,str) or not key or key in checks:
            raise ValueError("Invalid or duplicate finding ID")
        checks[key]=None
    return {
        "target":report["target"],"profile":report["profile"],
        "expected":checks,
        "_review_instructions":"Replace each null with pass, fail or unknown after independent evidence review. Remove this field if desired.",
        "_review_notes":"Record reviewer, date, evidence source and any disagreements outside this template. Never copy observed statuses without review."
    }

def review_template_command(report: Path):
    """Generate a blank reference for independent benchmark review."""
    try:
        if report.stat().st_size > MAX_BYTES:
            raise ValueError("Report exceeds 2 MB")
        template=make_template(json.loads(report.read_text(encoding="utf-8")))
    except (OSError,ValueError,TypeError) as exc:
        typer.echo(f"Review template error: {exc}",err=True)
        raise typer.Exit(2) from exc
    typer.echo(json.dumps(template,indent=2))
