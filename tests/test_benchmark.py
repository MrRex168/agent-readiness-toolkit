"""Offline benchmark agreement tests."""
import pytest
from agent_readiness.benchmark import assess

REPORT={"target":"https://example.com","profile":"website",
        "findings":[{"id":"title","status":"pass"},{"id":"robots","status":"fail"},{"id":"jsonld","status":"unknown"}]}
REFERENCE={"target":"https://example.com","profile":"website",
           "expected":{"title":"pass","robots":"pass","jsonld":"unknown"}}

def test_counts_mismatches():
    result=assess(REPORT,REFERENCE)
    assert result["correct"]==2
    assert result["total"]==3
    assert result["accuracy"]==66.7
    assert [x["check"] for x in result["outcomes"] if not x["match"]]==["robots"]

def test_missing_check_is_not_silently_ignored():
    reference={**REFERENCE,"expected":{"missing_check":"pass"}}
    result=assess(REPORT,reference)
    assert result["accuracy"]==0
    assert result["outcomes"][0]["actual"]=="missing"

def test_target_mismatch_fails():
    with pytest.raises(ValueError):
        assess(REPORT,{**REFERENCE,"target":"https://other.example"})

def test_invalid_reference_fails():
    with pytest.raises(ValueError):
        assess(REPORT,{**REFERENCE,"expected":{"title":"maybe"}})

def test_duplicate_report_finding_fails():
    with pytest.raises(ValueError):
        assess({**REPORT,"findings":REPORT["findings"]*2},REFERENCE)

def test_empty_reference_fails():
    with pytest.raises(ValueError):
        assess(REPORT,{**REFERENCE,"expected":{}})
