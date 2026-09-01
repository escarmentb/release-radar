# Health Probes

Release Radar separates liveness and readiness checks:

- `/health/live` confirms the process can answer requests.
- `/health/ready` confirms the service should receive traffic.
- `HEAD` requests can be used by lightweight probes that do not need response bodies.

Kubernetes probes should keep short timeouts and avoid depending on downstream monitoring systems.
