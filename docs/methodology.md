# Scoring v0.1

Weights: page title (10), meta description (10), document language (5), semantic main (10), robots.txt (10), sitemap.xml (10), parseable JSON-LD (20), OpenAPI JSON (25, only for API profile).

Score = 100 × sum(passed weights) / sum(passed + failed weights). Unknown observations are excluded. Results expose the raw denominator and check evidence. Missing optional agent protocols are not penalized.

The scanner detects basic structural signals, not comprehensive Schema.org or OpenAPI semantics, AI recommendation ranking, or checkout capability. Security warning: DNS validation is followed by a second HTTP-client resolution; do not expose this version as a hosted arbitrary-URL scanner without connection-level IP pinning.
