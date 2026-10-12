# Changelog

## [Unreleased]

### v0.1.0 release candidate

- Evidence-based website and API audit CLI with explicit pass, fail and unknown statuses
- Website checks for title, description, language, main landmark, robots.txt, XML sitemap and typed JSON-LD
- Lightweight OpenAPI 3.x and Swagger 2.0 JSON structural evidence checks
- JSON, Markdown and terminal scan reports, with optional CI scan gates
- Offline before/after report comparison and human-reviewed benchmark agreement gates
- Offline snapshot audits with optional SHA-256 integrity checks
- Independent review template generator and reproducible synthetic before/after demo
- Automated tests across Python 3.10–3.13 and built-wheel smoke checks

### Known limitations

- Live scanning is for trusted local CLI use only. DNS screening is not connection-level DNS pinning and is not sufficient for multi-tenant URL fetching.
- Results assess observable technical signals, not AI-agent discovery, ranking, successful task completion or full Schema.org/OpenAPI conformance.
- No manually reviewed real-world accuracy benchmark has been published yet.
- YAML OpenAPI specifications are not supported.

The v0.1.0 GitHub release and tag should be created **only after** the manual release gates are completed.
