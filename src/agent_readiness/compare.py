"""Compare two saved JSON audit reports. No network requests required."""
from __future__ import annotations
import json
from pathlib import Path
import typer

app = typer.Typer(add_completion=False)

def compare(before: dict, after: dict) -> dict:
    if before.get("target") != after.get("target") or before.get("profile") != after.get("profile"):
        raise ValueError("Reports must have the same target and profile")
    def indexed(report):
        entries = report.get("findings")
        if not isinstance(entries, list):
            raise ValueError("Invalid report: findings must be a list")
        result = {}
        for item in entries:
            key = item.get("id")
            if not isinstance(key,str) or key in result or item.get("status") not in {"pass","fail","unknown"}:
                raise ValueError("Invalid or duplicate check identifier/status")
            result[key] = item
        return result
    old, new = indexed(before), indexed(after)
    changes=[]
    for key in sorted(old.keys() | new.keys()):
        a,b=old.get(key),new.get(key)
        prior=a["status"] if a else "missing"
        current=b["status"] if b else "missing"
        if prior == current:
            continue
        kind = ("fixed" if prior=="fail" and current=="pass"
                else "regressed" if prior=="pass" and current=="fail"
                else "changed")
        changes.append({"id":key,"before":prior,"after":current,"kind":kind,
                        "evidence":b.get("evidence","") if b else ""})
    oldscore, newscore=before.get("score"),after.get("score")
    delta=newscore-oldscore if isinstance(oldscore,(int,float)) and isinstance(newscore,(int,float)) else None
    return {"target":before["target"],"profile":before["profile"],
            "before_score":oldscore,"after_score":newscore,"delta":delta,
            "changes":changes,"warning":"Score changes may reflect changed applicability; inspect individual findings."}

@app.command()
def reports(before: Path, after: Path, output: str = "terminal"):
    """Compare two saved JSON reports from the same website and profile."""
    try:
        if before.stat().st_size>2_000_000 or after.stat().st_size>2_000_000:
            raise ValueError("Report exceeds 2 MB")
        result=compare(json.loads(before.read_text()),json.loads(after.read_text()))
    except (OSError,ValueError,KeyError,TypeError) as exc:
        typer.echo(f"Comparison error: {exc}",err=True)
        raise typer.Exit(2) from exc
    if output=="json":
        typer.echo(json.dumps(result,indent=2))
    elif output=="markdown":
        lines=[f"# Audit comparison: {result['target']}",f"Score: {result['before_score']} → {result['after_score']} (Δ {result['delta']})",
               "","| Check | Before | After | Classification |","|---|---|---|---|"]
        for item in result["changes"]:
            lines.append("| "+" | ".join(str(item[k]).replace("|","\\|") for k in ("id","before","after","kind"))+" |")
        typer.echo("\n".join(lines))
    elif output=="terminal":
        typer.echo(f"Score: {result['before_score']} -> {result['after_score']} (delta {result['delta']})")
        for item in result["changes"]:
            typer.echo(f"{item['kind']:10} {item['id']}: {item['before']} -> {item['after']}")
        if not result["changes"]:
            typer.echo("No check status changes.")
    else:
        raise typer.BadParameter("output must be terminal, json or markdown")
