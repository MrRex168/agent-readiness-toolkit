"""End-to-end CLI demo using checked-in synthetic evidence."""
import json
from pathlib import Path
from typer.testing import CliRunner
from agent_readiness.cli import app

ROOT = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()

def test_demo_before_after_and_compare(tmp_path):
    paths=[]
    for label,folder in (("before","demo-before"),("after","demo-site")):
        result=RUNNER.invoke(app,["snapshot",str(ROOT/"examples"/folder),"--output","json"])
        assert result.exit_code==0, result.output
        report=json.loads(result.output)
        assert report["source"]=="offline_snapshot"
        assert report["target"]=="https://demo.example.com"
        path=tmp_path/f"{label}.json"
        path.write_text(result.output)
        paths.append((report,path))
    before,after=paths[0][0],paths[1][0]
    assert before["score"]<after["score"]
    assert after["score"]==100
    result=RUNNER.invoke(app,["compare",str(paths[0][1]),str(paths[1][1]),"--output","json"])
    assert result.exit_code==0, result.output
    comparison=json.loads(result.output)
    assert comparison["delta"]>0
    assert any(change["kind"]=="fixed" for change in comparison["changes"])
    assert any(change["kind"]=="changed" for change in comparison["changes"])

def test_demo_snapshot_terminal_output():
    result=RUNNER.invoke(app,["snapshot",str(ROOT/"examples"/"demo-site"),"--output","terminal"])
    assert result.exit_code==0, result.output
    assert "Snapshot score: 100/100" in result.output
