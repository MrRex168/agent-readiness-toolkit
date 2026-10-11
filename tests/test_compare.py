"""Deterministic comparison tests."""
import pytest
from agent_readiness.compare import compare

def report(score, findings, target="https://example.com", profile="website"):
    return {"target":target,"profile":profile,"score":score,
            "findings":[{"id":k,"status":v,"evidence":"fixture"} for k,v in findings.items()]}

def test_fixed_and_regressed():
    old=report(50,{"title":"fail","robots":"pass"})
    new=report(70,{"title":"pass","robots":"fail"})
    result=compare(old,new)
    assert result["delta"]==20
    assert {x["kind"] for x in result["changes"]}=={"fixed","regressed"}

def test_unknown_is_not_claimed_as_fix():
    result=compare(report(50,{"openapi":"unknown"}),report(50,{"openapi":"pass"}))
    assert result["changes"][0]["kind"]=="changed"

def test_same_report_has_no_changes():
    item=report(100,{"title":"pass"})
    assert compare(item,item)["changes"]==[]

def test_mismatch_rejected():
    with pytest.raises(ValueError):
        compare(report(50,{}),report(50,{},target="https://different.com"))

def test_duplicate_check_rejected():
    item=report(50,{"title":"pass"})
    item["findings"].append(item["findings"][0])
    with pytest.raises(ValueError):
        compare(item,report(60,{}))

def test_missing_check_is_changed_not_regression():
    result=compare(report(50,{"title":"pass"}),report(50,{}))
    assert result["changes"][0]["kind"]=="changed"
