# v0.1.0 release checklist

This is a **release candidate checklist**, not evidence that the project has been published or validated against live sites.

## Automated gates

- [ ] Python 3.10, 3.11, 3.12 and 3.13 unit tests pass
- [ ] Wheel and source distribution build successfully
- [ ] Install the built wheel and run help for all six CLI commands (scan, compare, benchmark, review-template, snapshot, and top-level help)
- [ ] Offline snapshot, comparison and benchmark tests pass

## Manual gates

- [ ] Complete the [real-world validation protocol](real-world-validation.md) on at least three independently reviewed, permission-appropriate website evidence sets
- [ ] Save evidence hashes and document mismatches in `docs/benchmarking.md` workflow
- [ ] Confirm CLI JSON output and exit codes are useful for scripting
- [ ] Review README installation instructions and usage against the actual built wheel
- [ ] Review license, security limitations, supported Python versions, [changelog](../CHANGELOG.md) and [draft release notes](release-notes-v0.1.0.md)
- [ ] Decide whether remaining real-world false positives block release

## Security and claims

The live `scan` command **does not pin the HTTP connection to the validated DNS address**. Do not offer it as a multi-tenant hosted arbitrary-URL scanner. The offline `snapshot` command is preferable for reproducible third-party evidence review.

Readiness scores measure observable technical signals only. They do not prove that AI agents can find, understand or transact with a website.

## Suggested release steps

1. Merge the release-check PR after all CI jobs pass.
2. Complete and record manual benchmark reviews using [the validation protocol](real-world-validation.md).
3. Publish a GitHub release tagged `v0.1.0` only after reviewing the final release candidate.
4. Launch with a short, evidence-based demo and transparent limitations.
