"""Independent benchmark review template tests."""
import json
import pytest
from typer.testing import CliRunner
from agent_readiness.cli import app
from agent_readiness.review import make_template
from agent_readiness.benchmark import assess

REPORT={"target":"https://example.com","profile":"website","findings":[
    {"id":"title","status":"pass"},{"id":"sitemap","status":"fail"},{"id":"robots","status":"unknown"}]}

def test_template_does_not_leak_observed_statuses():
    template=make_template(REPORT)
    assert template["expected"]=={"title":None,"sitemap":None,"robots":None}
    assert template["target"]==REPORT["target"]

def test_unreviewed_template_fails_benchmark():
    with pytest.raises(ValueError,match="Invalid expected status"):
        assess(REPORT,make_template(REPORT))

def test_reviewed_template_is_accepted():
    template=make_template(REPORT)
    template["expected"]={"title":"pass","sitemap":"fail","robots":"unknown"}
    assert assess(REPORT,template)["accuracy"]==100

def test_duplicate_finding_is_rejected():
    report={**REPORT,"findings":REPORT["findings"]+[REPORT["findings"][0]]}
    with pytest.raises(ValueError,match="duplicate"):
        make_template(report)

def test_invalid_report_rejected():
    with pytest.raises(ValueError,match="non-empty findings"):
        make_template({"target":"https://example.com","profile":"website","findings":[]})

def test_cli_generates_template(tmp_path):
    file=tmp_path/"report.json"
    file.write_text(json.dumps(REPORT))
    result=CliRunner().invoke(app,["review-template",str(file)])
    assert result.exit_code==0, result.output
    assert json.loads(result.output)["expected"]["title"] is None

def test_cli_missing_file_exit_2(tmp_path):
    result=CliRunner().invoke(app,["review-template",str(tmp_path/"missing.json")])
    assert result.exit_code==2
