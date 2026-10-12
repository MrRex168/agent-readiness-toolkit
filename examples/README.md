# Reproducible demo

All evidence here is **synthetic**. No real website was scanned and no external network access is needed.

Run from the repository root after installing the package:

```bash
agent-readiness snapshot examples/demo-before --output json > before.json
agent-readiness snapshot examples/demo-site --output json > after.json
agent-readiness compare before.json after.json
```

The before snapshot intentionally omits the page language, meta description, main landmark, structured data, robots.txt and sitemap.xml. Missing optional files are **unknown**, not failures. The complete after snapshot supplies those files.

Use `agent-readiness snapshot examples/demo-site --output terminal` to see individual check evidence.

A higher score does **not** prove an AI agent will prefer the site. This demo exercises deterministic signal checks and comparison behavior.
