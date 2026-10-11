"""CLI quality gate tests using saved, deterministic reports."""
import json
from typer.testing import CliRunner
from agent_readiness.cli import app

def files(tmp_path):
    report={"target":"https://example.com","profile":"website","findings":[{"id":"title","status":"pass"},{"id":"robots","status":"fail"}]}
    reference={"target":"https://example.com","profile":"website","expected":{"title":"pass","robots":"pass"}}
    a,b=tmp_path/"report.json",tmp_path/"reference.json"
    a.write_text(json.dumps(report))
    b.write_text(json.dumps(reference))
    return a,b

def test_gate_passes_at_threshold(tmp_path):
    a,b=files(tmp_path)
    result=CliRunner().invoke(app,["benchmark",str(a),str(b),"--min-accuracy","50"])
    assert result.exit_code==0, result.output

def test_gate_fails_below_threshold(tmp_path):
    a,b=files(tmp_path)
    result=CliRunner().invoke(app,["benchmark",str(a),str(b),"--min-accuracy","95"])
    assert result.exit_code==1
    assert "gate failed" in result.output.lower()

def test_json_output_still_fails_gate(tmp_path):
    a,b=files(tmp_path)
    result=CliRunner().invoke(app,["benchmark",str(a),str(b),"--output","json","--min-accuracy","95"])
    assert result.exit_code==1
    assert '"accuracy": 50.0' in result.output

def test_invalid_threshold_is_usage_error(tmp_path):
    a,b=files(tmp_path)
    result=CliRunner().invoke(app,["benchmark",str(a),str(b),"--min-accuracy","101"])
    assert result.exit_code==2

def test_default_mode_does_not_fail_for_mismatch(tmp_path):
    a,b=files(tmp_path)
    result=CliRunner().invoke(app,["benchmark",str(a),str(b)])
    assert result.exit_code==0
