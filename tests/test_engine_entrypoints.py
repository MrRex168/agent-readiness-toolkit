"""The public audit alias and CLI must use the same engine."""
from unittest.mock import patch
from typer.testing import CliRunner
from agent_readiness.cli import app, audit
from agent_readiness.core import evaluate

def test_legacy_audit_delegates_to_core():
    expected={"target":"https://example.com","score":90,"findings":[]}
    with patch("agent_readiness.cli.evaluate",return_value=expected) as mocked:
        result=audit("https://example.com",profile="api",api_url="https://example.com/openapi.json")
    assert result is expected
    mocked.assert_called_once_with("https://example.com","api","https://example.com/openapi.json",None)

def test_scan_cli_uses_canonical_evaluator():
    expected={"target":"https://example.com","profile":"website","score":90,
              "findings":[{"id":"title","status":"pass","evidence":"found","fix":""}]}
    with patch("agent_readiness.cli.evaluate",return_value=expected) as mocked:
        result=CliRunner().invoke(app,["scan","https://example.com","--output","json"])
    assert result.exit_code==0, result.output
    assert '"score": 90' in result.output
    mocked.assert_called_once_with("https://example.com","website",None)

def test_alias_preserves_client_identity():
    sentinel=object()
    with patch("agent_readiness.cli.evaluate",return_value={}) as mocked:
        audit("https://example.com",client=sentinel)
    assert mocked.call_args.args[-1] is sentinel
