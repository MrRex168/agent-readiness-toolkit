"""Offline benchmark scoring against manually reviewed audit expectations."""
from __future__ import annotations
import json
from pathlib import Path
import typer

app = typer.Typer(add_completion=False)
STATUSES = {"pass","fail","unknown"}

def assess(report: dict, expectations: dict) -> dict:
    """Compare findings against human-reviewed expected statuses."""
    if report.get("target") != expectations.get("target") or report.get("profile") != expectations.get("profile"):
        raise ValueError("Benchmark target/profile mismatch")
    observed={}
    for finding in report.get("findings",[]):
        key=finding.get("id")
        if not isinstance(key,str) or key in observed or finding.get("status") not in STATUSES:
            raise ValueError("Invalid or duplicate finding")
        observed[key]=finding["status"]
    expected=expectations.get("expected")
    if not isinstance(expected,dict) or not expected:
        raise ValueError("Benchmark must contain non-empty expected status mapping")
    outcomes=[]
    for key,status in sorted(expected.items()):
        if status not in STATUSES:
            raise ValueError(f"Invalid expected status for {key}")
        actual=observed.get(key,"missing")
        outcomes.append({"check":key,"expected":status,"actual":actual,"match":actual==status})
    correct=sum(x["match"] for x in outcomes)
    return {"target":report["target"],"profile":report["profile"],"correct":correct,
            "total":len(outcomes),"accuracy":round(correct/len(outcomes)*100,1),"outcomes":outcomes,
            "note":"Agreement with reviewed expectations, not proof of AI-agent success."}

@app.command("benchmark")
def benchmark_command(report: Path, reference: Path, output: str = "terminal", min_accuracy: float | None = None):
    """Evaluate a saved audit report against manually reviewed expectations."""
    try:
        if min_accuracy is not None and (not 0 <= min_accuracy <= 100 or min_accuracy != min_accuracy):
            raise ValueError("--min-accuracy must be between 0 and 100")
        for path in (report,reference):
            if path.stat().st_size > 2_000_000:
                raise ValueError("File exceeds 2 MB")
        result=assess(json.loads(report.read_text()),json.loads(reference.read_text()))
    except (OSError,ValueError,KeyError,TypeError) as exc:
        typer.echo(f"Benchmark error: {exc}",err=True)
        raise typer.Exit(2) from exc
    if output=="json":
        typer.echo(json.dumps(result,indent=2))
    elif output=="terminal":
        typer.echo(f"Agreement: {result['correct']}/{result['total']} ({result['accuracy']}%)")
        for item in result["outcomes"]:
            if not item["match"]:
                typer.echo(f"MISMATCH {item['check']}: expected {item['expected']}, got {item['actual']}")
    else:
        raise typer.BadParameter("output must be terminal or json")
    if min_accuracy is not None and result["accuracy"] < min_accuracy:
        typer.echo(f"Benchmark gate failed: {result['accuracy']}% below {min_accuracy}% minimum", err=True)
        raise typer.Exit(1)
