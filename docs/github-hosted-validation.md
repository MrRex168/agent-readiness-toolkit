# Run the manual GitHub-hosted audit

This workflow is intended for maintainers who cannot run the CLI locally.

1. Open **Actions → manual-real-world-audit → Run workflow** on the default branch.
2. Wait for the run to finish.
3. Download the **real-world-audit-evidence** artifact from the run.
4. Upload the ZIP for independent review or inspect it yourself.

The workflow collects bounded HTML, robots.txt and sitemap evidence for three **fixed public targets**: `www.python.org`, `www.djangoproject.com` and `www.wikipedia.org`. There is no arbitrary URL input.

## Artifact layout

- `summary.json`: per-target status (`candidate`, `blocked` or `error`) and collection timestamp
- `<site>/collection.json`: resource URLs, retrieval outcomes, hashes and timestamp
- `<site>/index.html`, `robots.txt`, `sitemap.xml`: captured response bodies when available
- `<site>/manifest.json`: target URL and SHA-256 fingerprints
- `<site>/report.json`: offline audit of **the exact saved evidence**
- `<site>/review.json`: independent review worksheet with intentionally blank expectations

A blocked homepage does **not** create a misleading empty report. Optional unavailable resources remain unknown in offline audit results.

**Important:** These are candidate observations, not independently validated accuracy results. A reviewer must inspect the captured files, fill in expected statuses and document mismatches. The workflow does not automatically verify website claims or AI-agent success. Review [the validation protocol](real-world-validation.md) and [release gate issue](https://github.com/MrRex168/agent-readiness-toolkit/issues/17).

The ZIP contains third-party website content; keep it private unless redistribution is permitted. Artifacts are retained for seven days. The workflow is opt-in and does not run on push or pull request.

**Security limitation:** This collector uses the same trusted-CLI network layer as `scan`, which does not pin connections to DNS-screened IPs. Do not extend this workflow to arbitrary user-supplied URLs or offer it as a multi-tenant URL-fetching service.
