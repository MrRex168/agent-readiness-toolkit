"""Network guard regression tests. No external DNS/network required."""
import socket
from unittest.mock import patch
import pytest
from agent_readiness.cli import guard

def fake_dns(ip):
    return [(socket.AF_INET,socket.SOCK_STREAM,6,"",(ip,443))]

@pytest.mark.parametrize("ip",["127.0.0.1","10.0.0.2","192.168.1.2","169.254.169.254","0.0.0.0"])
def test_dns_blocks_nonpublic_addresses(ip):
    with patch("agent_readiness.cli.socket.getaddrinfo",return_value=fake_dns(ip)):
        with pytest.raises(ValueError):
            guard("https://example.com")

def test_dns_allows_public_address():
    with patch("agent_readiness.cli.socket.getaddrinfo",return_value=fake_dns("8.8.8.8")):
        assert guard("https://example.com")=="https://example.com"

def test_dns_rejects_mixed_public_and_private():
    with patch("agent_readiness.cli.socket.getaddrinfo",return_value=fake_dns("8.8.8.8")+fake_dns("127.0.0.1")):
        with pytest.raises(ValueError):
            guard("https://example.com")
