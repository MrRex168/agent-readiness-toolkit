import pytest
from agent_readiness.cli import guard

@pytest.mark.parametrize("url", [
    "http://example.com", "https://127.0.0.1", "https://localhost",
    "https://example.com:8443", "https://u:p@example.com"
])
def test_blocks_unsafe_targets(url):
    with pytest.raises(ValueError):
        guard(url)
