# Metrics

Release Radar exposes Prometheus metrics at `/metrics`.

Current metrics:

| Metric | Type | Purpose |
|---|---|---|
| `release_radar_uptime_seconds` | Gauge | Reports process uptime. |
| `release_radar_http_requests_total` | Counter | Counts HTTP responses by method, normalized path, and status. |

Keep labels low-cardinality so dashboards and alert rules remain predictable under load.
