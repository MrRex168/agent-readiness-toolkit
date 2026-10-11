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
- robots.txt, XML sitemap URL sets/indexes and typed JSON-LD with a context
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

## Audit accuracy

Sitemap checks parse XML and recognize both `urlset` and `sitemapindex` roots, including the standard sitemap namespace. JSON-LD checks require a context and at least one typed entity, including entities nested in an `@graph`. This is **not** a full Schema.org validation: it checks structural evidence, not whether claims are accurate or complete.

## Reproducible validation

The [validation matrix](docs/validation.md) documents deterministic website and API scenarios, expected results, and current accuracy limitations. Run `python -m pytest -q` to verify behavior without accessing external websites.

## Python integration

Use `agent_readiness.core.evaluate(url, profile="website")` as the canonical Python entrypoint. The older `agent_readiness.cli.audit(...)` function remains as a compatibility alias and delegates to the same engine. The CLI `scan` command also uses `evaluate`.

## Benchmark audit accuracy

Compare a saved JSON report against manually reviewed expected check statuses:

```bash
agent-readiness benchmark report.json reference.json
agent-readiness benchmark report.json reference.json --output json
```

See [benchmarking methodology](docs/benchmarking.md). This measures agreement with human-reviewed expectations; no live benchmark results are claimed yet.

## CI benchmark gate

Use a reviewed reference file to fail CI when check-level agreement falls below a chosen threshold:

```bash
agent-readiness benchmark report.json reference.json --min-accuracy 95
```

Exit code `0` means the gate passed, `1` means agreement fell below the threshold, and `2` means invalid input. Without `--min-accuracy`, the command reports mismatches without failing the build. The gate measures agreement with **your reviewed expectations**, not actual agent performance.

## CI scan gates

Optionally fail a pipeline when a scan score is too low or a required check does not pass:

```bash
agent-readiness scan https://example.com --min-score 80
agent-readiness scan https://example.com --require sitemap --require jsonld
agent-readiness scan https://example.com --output json --min-score 80 > report.json
```

Exit code `0` means all configured gates pass, `1` means a gate fails, and `2` means an invalid scan or input. Without gate options, scans remain reporting-only. Required checks with `unknown` or missing status do **not** pass. Use this only from a trusted environment: DNS-rebinding protection is not implemented for arbitrary hosted URL scanning.
