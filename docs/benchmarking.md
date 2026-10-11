# Benchmarking real-world audit findings

The benchmark command measures **agreement with manually reviewed expectations**. It does not independently establish that the reviewer is correct or that AI agents can use the website.

## Workflow

1. Run `agent-readiness scan https://example.com --output json > report.json` in a trusted local environment.
2. Inspect the website's actual HTML, robots.txt, sitemap, JSON-LD and (if applicable) API specification.
3. Record manually verified expected statuses in `reference.json`:

```json
{
  "target": "https://example.com",
  "profile": "website",
  "expected": {
    "title": "pass",
    "description": "pass",
    "robots": "pass",
    "sitemap": "unknown",
    "jsonld": "fail"
  }
}
```

4. Run `agent-readiness benchmark report.json reference.json` or add `--output json`.
5. Review each mismatch and attach evidence before modifying a validator.

The example reference is illustrative, **not a verified assessment of example.com**.

## Suggested benchmark sample

Start with 5–10 publicly accessible, low-risk websites: a small business, a SaaS landing page, documentation, a content site and an API documentation site. Obtain permission where appropriate and avoid scanning sensitive targets. Save observation date, source URLs, screenshots or redacted excerpts, and reviewer notes outside the machine-readable expectation file.

Do not publish claims of accuracy until manually reviewed cases exist. A benchmark score measures agreement on the selected checks and sample, not real-world agent discoverability.
