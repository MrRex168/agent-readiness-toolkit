# v0.1.0 three-site validation record

**Review date:** 2026-10-12 (UTC)  
**Evidence:** GitHub Actions `manual-real-world-audit #4`, archived artifact `real-world-audit-evidence` (not committed because it contains third-party website content).  
**Method:** Fixed-target GitHub-hosted collection, offline snapshot audit, SHA-256 integrity verification and manual comparison of findings against captured HTML, robots.txt, sitemap XML and collection metadata. See [protocol](real-world-validation.md).

| Site | Collection UTC | Score | Pass | Fail | Unknown |
|---|---|---:|---:|---:|---:|
| https://www.python.org | 08:10:46 | 87/100 | 6 | 1 | 0 |
| https://www.djangoproject.com | 08:10:47 | 60/100 | 5 | 2 | 0 |
| https://www.mozilla.org | 08:10:47 | 69/100 | 5 | 1 | 1 |

**Correction history:** Python.org's sitemap returned HTTP 404, which now counts as a failed check rather than unknown (PR #20). Its main landmark uses `role="main"`, now accepted alongside native `<main>` (PR #22). Mozilla's sitemap retrieval did not follow a redirect; its check remains **unknown**, not a verified failure.

## Review result

The latest 21 reported check statuses were consistent with the available captured evidence in this limited review (**21/21 observed agreement**). This is a small, non-random sample, **not** a statistical accuracy estimate or a measure of real AI-agent behavior. The review was performed against the same saved resources the scanner evaluated, not independently re-fetched website content. A separate external reviewer has not signed off.

## Evidence integrity

All **seven** captured resource files matched the SHA-256 hashes in their manifests. For traceability:

| Site | Captured resource | SHA-256 |
|---|---|---|
| Python.org | index.html | `e5835be9df0aac07e09398c999890aad4ae3b1c0d0a62f362300ad30d05c612c` |
| Python.org | robots.txt | `18cb4cd525df8528491845e76f3af26c29c6795d02ea8133974d3b341a2ddd9f` |
| Django | index.html | `06b0d27f869786a89a8350fb587bd8497d451a4cfd628f3cf3e3fc820432273b` |
| Django | robots.txt | `f584941ee39cc07ee18b15f3205ac289fa5f2ce328218f97b5b0dd2bce4e9f6e` |
| Django | sitemap.xml | `4012f5b64ffe0c587fce1f1e3bf851a7b8b6061096e4eecb3c10a27b9ff2decc` |
| Mozilla | index.html | `a6a4b137f9d9c5831b3391edc3419774d0aab0554ce90f97e9cb9f6cefbecf6b` |
| Mozilla | robots.txt | `cf0fd2842659297b0d6fce407bed86bf424ae6666051b881dbd72e871d687fe3` |

## Limits and release implications

- Fixed-target public-site evidence only; no API profile or agent-task outcome benchmark was performed.
- Redirects are not followed; a redirected sitemap is unknown. Missing source material does not establish a failure.
- Review worksheets were generated with blank expectations. This record documents the manual comparison; it does **not** claim that an external reviewer independently completed and signed those worksheets.
- Live URL fetching lacks connection-level DNS pinning. Do not deploy as an arbitrary-URL hosted scanner.
- The release checklist's build, packaging, install and CLI smoke gates must be verified separately before tagging `v0.1.0`.
