"""Pure, offline validators for common machine-readable website signals."""
from __future__ import annotations
import json
import xml.etree.ElementTree as ET

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

def sitemap_valid(body: str) -> bool:
    """Accept URL sets and sitemap indexes, with or without XML namespaces."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return False
    local = root.tag.rsplit("}", 1)[-1]
    if local not in {"urlset", "sitemapindex"}:
        return False
    if root.tag.startswith("{") and root.tag.split("}", 1)[0][1:] != SITEMAP_NS:
        return False
    return True

def jsonld_types(texts: list[str]) -> tuple[bool,list[str]]:
    """Require a JSON-LD context and at least one typed entity."""
    types: set[str] = set()
    def walk(node, context=None):
        if isinstance(node,list):
            for value in node:
                walk(value,context)
        elif isinstance(node,dict):
            context=node.get("@context",context)
            entity_type=node.get("@type")
            if context and entity_type:
                for item in entity_type if isinstance(entity_type,list) else [entity_type]:
                    if isinstance(item,str) and item.strip():
                        types.add(item)
            if "@graph" in node:
                walk(node["@graph"],context)
    for text in texts:
        try:
            walk(json.loads(text))
        except (ValueError,TypeError):
            continue
    return bool(types), sorted(types)
