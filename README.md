# Agent Readiness Toolkit

**Audit what's actually machine-readable and discoverable on your website or API.**

Evidence-based open-source CLI for developers, API teams and technical SEO practitioners. It reports observed signals, gives actionable fixes, and avoids penalizing websites simply for not using optional emerging agent protocols.

## Quick start

Requires Python 3.10+.

```bash
python -m pip install .
agent-readiness scan https://example.com
agent-readiness scan https://example.com --output json
agent-readiness scan https://example.com --output markdown
agent-readiness scan https://api.example.com --profile api --api-url https://api.example.com/openapi.json
```

## What v0.1 checks

- Page title, meta description, language and semantic main element
- robots.txt, sitemap.xml and parseable JSON-LD
- API profile: explicit same-host OpenAPI JSON documents with essential keys
- Each check includes status, evidence and a proposed fix
- Weighted score with unknown checks excluded from the denominator

**Not guaranteed:** AI search ranking, model inclusion, agent preference, commerce compatibility or successful transactions. A missing MCP server, llms.txt or agent payment protocol does not automatically count as a failure.

## Security limitations

Only public HTTPS targets on port 443; no redirects, read-only GET requests, 1 MB response cap, timeouts and public-IP DNS screening. **Not yet suitable as a multi-tenant hosted URL scanning service:** the HTTP client's second DNS lookup is not pinned to the validated IP, leaving possible DNS-rebinding risk. Use only in a trusted developer environment until hardened.

## Development

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

## Scope

The initial checks validate surface signals, not comprehensive Schema.org semantic correctness or full OpenAPI conformance. Next improvements: stronger tests, safe pinned-IP resolution, deeper OpenAPI validation, product and policy consistency, and before/after report comparison.

MIT licensed. See [methodology](docs/methodology.md).

## Compare before and after

Save JSON reports, make your website changes, then compare:

```bash
agent-readiness scan https://example.com --output json > before.json
# Deploy your changes
agent-readiness scan https://example.com --output json > after.json
agent-readiness compare before.json after.json
agent-readiness compare before.json after.json --output markdown
```

Comparison labels failed-to-passed checks as **fixed**, passed-to-failed checks as **regressed**, and changes involving unknown or missing checks as **changed**. The comparison is offline and requires matching target URLs and profiles. A score delta is not a substitute for reviewing the check-level evidence.
