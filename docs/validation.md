# Audit validation matrix

This suite uses **synthetic, deterministic HTTP fixtures**. It does not claim to have audited external websites or measured real-world agent performance.

| Scenario | Expected evidence | Why it matters |
| --- | --- | --- |
| Well-formed business site | All applicable website checks pass | Baseline |
| Missing title, description and typed JSON-LD | Three corresponding failures | Avoid silent false passes |
| XML sitemap index | Sitemap passes | Avoid false failure on legitimate index format |
| HTML pretending to be a sitemap | Sitemap fails | Reject misleading file names |
| JSON-LD without a typed entity | Structured data fails | Do not award points for irrelevant JSON |
| Explicit OpenAPI JSON | API check passes | Support declared API documentation |
| API profile without an advertised spec | API check unknown | Do not confuse absent evidence with verified failure |
| Explicit invalid API spec | API check fails | Flag invalid evidence |

## How to run

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

## Known gaps and future validation

- Current OpenAPI validation checks essential JSON keys, not full OpenAPI conformance.
- Robots.txt validation checks basic directive syntax and User-agent groups. It does not evaluate bot-specific crawl permissions or implement a complete robots exclusion parser.
- Synthetic fixtures cannot establish accuracy against live websites.
- The scanner's DNS preflight does not pin the validated address at connection time. **Do not expose arbitrary URL scanning as a public service.**
- Next: curated, manually reviewed live audit cases with permission and evidence snapshots; keep them separate from deterministic CI tests.
