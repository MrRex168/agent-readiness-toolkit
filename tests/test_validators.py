from agent_readiness.validators import sitemap_valid, jsonld_types

def test_sitemap_index_with_namespace():
    xml='<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap/></sitemapindex>'
    assert sitemap_valid(xml)

def test_urlset_without_namespace():
    assert sitemap_valid("<urlset><url/></urlset>")

def test_invalid_sitemap_rejected():
    assert not sitemap_valid("<html><urlset></urlset></html>")
    assert not sitemap_valid("<urlset")
    assert not sitemap_valid('<urlset xmlns="https://example.com/wrong"/>')

def test_jsonld_graph_inherits_context():
    body='{"@context":"https://schema.org","@graph":[{"@type":"Organization"},{"@type":"WebSite"}]}'
    valid, types=jsonld_types([body])
    assert valid and types==["Organization","WebSite"]

def test_json_without_context_is_not_jsonld():
    assert jsonld_types(['{"@type":"Organization"}'])==(False,[])

def test_untyped_jsonld_is_not_entity():
    assert jsonld_types(['{"@context":"https://schema.org","name":"Acme"}'])==(False,[])

def test_malformed_script_does_not_hide_valid_script():
    assert jsonld_types(["{bad", '{"@context":"https://schema.org","@type":"Product"}'])==(True,["Product"])
