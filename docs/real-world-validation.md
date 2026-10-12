# First real-world validation study

**Status: Not yet performed.** This protocol is a guide for collecting real evidence, not a benchmark result.

## Minimum sample

Review three permission-appropriate public sites representing different categories, for example a business homepage, documentation site and SaaS website. Expand to five or ten if the first three expose inconsistent behavior. Avoid authentication, personal data, sensitive services or targets that prohibit automated requests.

## Evidence collection

For each site, record a UTC observation date, target URL, site category, reviewer and collection method. In a trusted local environment, save the actual HTML as `index.html`, and optionally save `robots.txt` and `sitemap.xml` from the same host. Save `manifest.json` with the HTTPS target URL. If reviewing an API, provide a same-host OpenAPI JSON URL and `openapi.json`.

The saved files must represent the actual resources, not a hand-edited idealized website. Preserve raw evidence privately if license, copyright or privacy concerns prevent redistribution. Do not commit third-party page content without appropriate permission.

```bash
agent-readiness snapshot ./site-evidence --output json > report.json
agent-readiness review-template report.json > reference.json
```

Inspect each check independently against the captured files. Replace every `null` in `reference.json` with `pass`, `fail` or `unknown`. Do not copy the scanner's observed answers into the reference without verification. Record a reason and evidence pointer for every disagreement.

```bash
agent-readiness benchmark report.json reference.json --output json > benchmark.json
```

## Report the results

For each site, record:
- Category and date of evidence collection
- Number of checks independently reviewed
- Matching checks, mismatches and agreement percentage
- Each mismatch's observed status, expected status, evidence and suspected root cause
- Limitations, inaccessible evidence and any excluded checks

Publish an aggregate only after documenting the number of sites and checks, sampling method and any unresolved mismatches. Agreement with reviewers is not a measure of AI-agent success.

## Release decision

A maintainer should review all mismatches before the first release. Critical false passes should be corrected or prominently disclosed. Keep the v0.1.0 release on hold if evidence cannot be independently reviewed.
