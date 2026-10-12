# Agent Readiness Toolkit v0.1.0

**Draft release notes. Do not publish until release gates are satisfied.**

Agent Readiness Toolkit is a read-only Python CLI that checks observable machine-readability signals on websites and API documentation. It reports evidence and suggested fixes instead of claiming to predict AI-agent behavior.

## Try it

```bash
python -m pip install "git+https://github.com/MrRex168/agent-readiness-toolkit.git"
agent-readiness scan https://example.com
```

Or run the synthetic, network-free demo from a repository checkout:

```bash
agent-readiness snapshot examples/demo-site --output terminal
```

## Included

- Website and API evidence checks
- Terminal, JSON and Markdown reports
- CI score and required-check gates
- Before/after report comparison
- Offline snapshots with SHA-256 evidence fingerprints
- Independent review templates and benchmark agreement checks

## Important limits

Live URL scanning is **not suitable for multi-tenant hosted use** because DNS resolution is not pinned to the screened address. Results do not prove AI search ranking, agent compatibility or successful transactions. Real-world accuracy benchmarks remain pending independent review.

Python 3.10+; MIT licensed.
