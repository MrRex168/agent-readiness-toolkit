"""Conservative robots.txt syntax checks; not a crawler permission engine."""
from __future__ import annotations

def robots_evidence(body: str) -> tuple[bool, str]:
    """Validate that robots.txt has at least one user-agent group.

    This checks basic syntax, not whether a particular bot may crawl a URL.
    """
    if not body.strip():
        return False, "Empty robots.txt"
    agents = 0
    rules = 0
    seen_agent = False
    for raw in body.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            return False, f"Malformed directive: {line[:80]}"
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if not value:
                return False, "Empty User-agent directive"
            agents += 1
            seen_agent = True
        elif key in {"allow", "disallow"}:
            if not seen_agent:
                return False, f"{key} directive before any User-agent"
            rules += 1
        elif key in {"sitemap", "host", "crawl-delay", "clean-param", "request-rate"}:
            pass  # Common extensions and sitemap metadata.
        else:
            # Unknown extension directives are allowed by the protocol.
            pass
    if not agents:
        return False, "No User-agent group found"
    return True, f"{agents} User-agent directive(s), {rules} allow/disallow rule(s)"
