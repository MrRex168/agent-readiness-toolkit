"""OpenAPI structural evidence regression cases."""
import json
import pytest
from agent_readiness.openapi import openapi_evidence

def spec(**updates):
    value={"openapi":"3.1.0","info":{"title":"Example","version":"1"},"paths":{"/items":{"get":{"responses":{"200":{"description":"OK"}}}}}}
    value.update(updates)
    return json.dumps(value)

def test_valid_openapi_3():
    valid,evidence=openapi_evidence(spec())
    assert valid and "OpenAPI 3.1.0" in evidence

def test_valid_swagger_2():
    valid,evidence=openapi_evidence(json.dumps({"swagger":"2.0","info":{"title":"Legacy","version":"1"},"paths":{}}))
    assert valid and "Swagger 2.0" in evidence

@pytest.mark.parametrize("body,reason",[
    ("not json","Not valid JSON"),
    ('[]',"JSON object"),
    (spec(openapi="garbage"),"version"),
    (spec(openapi="4.0.0"),"version"),
    (spec(info={"title":"Example"}),"info.title"),
    (spec(info={"title":"","version":"1"}),"info.title"),
    (spec(paths=[]),"paths"),
    (spec(paths={"items":{"get":{}}}),"begin with"),
    (spec(paths={"/items":{"get":"invalid"}}),"must be an object"),
])
def test_invalid_spec_fails_with_reason(body,reason):
    valid,evidence=openapi_evidence(body)
    assert not valid
    assert reason in evidence

def test_empty_paths_is_valid_structural_evidence():
    assert openapi_evidence(spec(paths={}))[0]
