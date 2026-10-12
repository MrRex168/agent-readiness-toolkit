"""Regression coverage for native and ARIA main landmarks."""
import pytest
from agent_readiness.core import evaluate

@pytest.mark.parametrize("markup,expected",[
    ("<main>Content</main>","pass"),
    ('<div role="main">Content</div>',"pass"),
    ('<section role="MAIN">Content</section>',"pass"),
    ('<div role="navigation">Content</div>',"fail"),
    ('<div role="domain">Content</div>',"fail"),
    ('<div data-role="main">Content</div>',"fail"),
])
def test_main_landmark_recognition(markup,expected):
    html=f'<html lang="en"><head><title>Test</title></head><body>{markup}</body></html>'
    def fetch(url):
        if url=="https://example.com":
            return html,"HTTP 200"
        return None,"Not supplied"
    report=evaluate("https://example.com",fetch=fetch)
    finding=next(item for item in report["findings"] if item["id"]=="main")
    assert finding["status"]==expected

def test_role_main_earns_landmark_weight():
    html='<html><head><title>Example</title></head><body><div role="main">Content</div></body></html>'
    def fetch(url):
        return (html,"HTTP 200") if url=="https://example.com" else (None,"Not supplied")
    report=evaluate("https://example.com",fetch=fetch)
    assert report["score_basis"]["passed_weight"]==20
