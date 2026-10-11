"""Scan gate behavior and CLI exit codes."""
from unittest.mock import patch
from typer.testing import CliRunner
from agent_readiness.cli import app
from agent_readiness.gates import gate_report

REPORT={"target":"https://example.com","profile":"website","score":80,
        "findings":[{"id":"title","status":"pass","evidence":"title present","fix":""},{"id":"sitemap","status":"fail","evidence":"missing sitemap","fix":"Publish sitemap"},{"id":"openapi","status":"unknown","evidence":"not advertised","fix":""}]}

def test_gate_defaults_are_opt_in():
    assert gate_report(REPORT)==[]

def test_minimum_score_fails():
    assert gate_report(REPORT,min_score=90)==["Score 80 is below minimum 90"]

def test_required_fail_or_unknown_never_pass():
    failures=gate_report(REPORT,require=("title","sitemap","openapi","missing"))
    assert len(failures)==3

def test_score_without_applicable_checks_is_not_pass():
    assert gate_report({**REPORT,"score":None},min_score=0)

def test_cli_passes_when_requirement_met():
    with patch("agent_readiness.cli.evaluate",return_value=REPORT):
        result=CliRunner().invoke(app,["scan","https://example.com","--min-score","80","--require","title"])
    assert result.exit_code==0, result.output

def test_cli_fails_when_requirement_missing():
    with patch("agent_readiness.cli.evaluate",return_value=REPORT):
        result=CliRunner().invoke(app,["scan","https://example.com","--require","sitemap"])
    assert result.exit_code==1
    assert "Scan gate failed" in result.output

def test_cli_json_is_available_on_gate_failure():
    with patch("agent_readiness.cli.evaluate",return_value=REPORT):
        result=CliRunner().invoke(app,["scan","https://example.com","--output","json","--min-score","90"])
    assert result.exit_code==1
    assert '"score": 80' in result.output
