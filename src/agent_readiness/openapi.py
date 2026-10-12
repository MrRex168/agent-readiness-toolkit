"""Lightweight OpenAPI evidence validation, not full specification conformance."""
from __future__ import annotations
import json
import re

METHODS = {"get","put","post","delete","options","head","patch","trace"}

def openapi_evidence(body: str) -> tuple[bool,str]:
    try:
        doc = json.loads(body)
    except (ValueError,TypeError):
        return False,"Not valid JSON"
    if not isinstance(doc,dict):
        return False,"OpenAPI document must be a JSON object"
    version = doc.get("openapi")
    swagger = doc.get("swagger")
    if isinstance(version,str) and re.fullmatch(r"3\.\d+\.\d+(?:[-+][A-Za-z0-9.\-]+)?",version):
        family="OpenAPI "+version
    elif swagger=="2.0":
        family="Swagger 2.0"
    else:
        return False,"Missing or unsupported OpenAPI/Swagger version"
    info=doc.get("info")
    if not isinstance(info,dict) or not all(isinstance(info.get(k),str) and info[k].strip() for k in ("title","version")):
        return False,"info.title and info.version must be non-empty strings"
    paths=doc.get("paths")
    if not isinstance(paths,dict):
        return False,"paths must be an object"
    for path, item in paths.items():
        if not isinstance(path,str) or not path.startswith("/"):
            return False,"Path keys must begin with /"
        if not isinstance(item,dict):
            return False,f"Path {path} must be an object"
        for key, operation in item.items():
            if key.lower() in METHODS and not isinstance(operation,dict):
                return False,f"Operation {key.upper()} {path} must be an object"
    return True,f"{family}; {len(paths)} path(s); info.title={info['title'][:80]}"
