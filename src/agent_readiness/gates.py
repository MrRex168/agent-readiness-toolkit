"""Explicit, opt-in quality gates for scan reports."""
from __future__ import annotations

def gate_report(report: dict, min_score: int | None = None, require: tuple[str, ...] = ()) -> list[str]:
    """Return actionable gate failures. Unknown checks never count as passes."""
    if min_score is not None and not 0 <= min_score <= 100:
        raise ValueError("--min-score must be between 0 and 100")
    findings=report.get("findings",[])
    if not isinstance(findings,list):
        raise ValueError("Invalid report findings")
    indexed={}
    for item in findings:
        key=item.get("id")
        if not isinstance(key,str) or key in indexed or item.get("status") not in {"pass","fail","unknown"}:
            raise ValueError("Invalid or duplicate report finding")
        indexed[key]=item["status"]
    failures=[]
    score=report.get("score")
    if min_score is not None:
        if isinstance(score,bool) or not isinstance(score,(int,float)) or not 0 <= score <= 100:
            failures.append("Score is unavailable or invalid")
        elif score < min_score:
            failures.append(f"Score {score} is below minimum {min_score}")
    for key in require:
        status=indexed.get(key,"missing")
        if status!="pass":
            failures.append(f"Required check {key}: {status}")
    return failures
