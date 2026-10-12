# Run the manual GitHub-hosted audit

This workflow is intended for maintainers who cannot run the CLI locally.

1. Open **Actions → manual-real-world-audit → Run workflow** on the default branch.
2. Wait for the run to finish.
3. Download the **real-world-audit-candidates** artifact from the run.
4. Inspect each JSON report and its corresponding `.review.json` worksheet.

The workflow scans three **fixed public website targets**: `www.python.org`, `www.djangoproject.com` and `www.wikipedia.org`. There is no arbitrary URL input. Failed scans do not count as completed benchmark cases.

**Important:** These are candidate scan reports, **not independently validated benchmark evidence**. The scanner reports status and URL evidence, but does not archive the original response bodies. An independent reviewer must inspect the actual HTML and other resources, verify every status and record the collection date and any mismatches before completing the worksheets. Use [the validation protocol](real-world-validation.md) and [release gate issue](https://github.com/MrRex168/agent-readiness-toolkit/issues/17).

The workflow is opt-in and does not run on push or pull request. The live scanner's DNS-rebinding limitation still applies: do not expand this to accept arbitrary user-supplied targets or offer it as a hosted URL-fetching service. Running these fixed domains in GitHub Actions does not constitute connection-level DNS pinning.

If GitHub-hosted outbound access fails, treat the case as unavailable, not as a failed website readiness check.
