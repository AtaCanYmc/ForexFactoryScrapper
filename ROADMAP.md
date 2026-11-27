# Roadmap

This file tracks capability scope, not release tags. Release Please assigns version numbers from Conventional Commits and keeps `version.txt`, the Helm chart, and `src/openapi_spec.py` in sync.

Current stable release: `2.1.0`.

## Shipped in 2.1.0

### Data and API

- [x] Multi-source economic calendar aggregation for ForexFactory, CryptoCraft, EnergyExch, and MetalsMine.
- [x] Date-range bundle endpoint at `GET /api/bundle` with a per-source breakdown.
- [x] Sitemap discovery endpoint at `GET /api/forex/sitemaps`.
- [x] Per-source daily endpoints with `limit` and `offset` pagination.
- [x] Date, source, and pagination validation before any upstream call.
- [x] OpenAPI 3.0.0 document, Swagger UI at `/swagger`, and `/openapi.json`.
- [x] Optional API key authentication on `/api/*` with `X-API-Key` or `Authorization: Bearer`.
- [x] CORS configuration, security headers, and `X-Request-ID` correlation.
- [x] Bruno collection with offline contract assertions for success and error paths.

### Resilience and operations

- [x] TTL cache with a per-process memory backend and a shared Redis backend.
- [x] Per-client sliding-window rate limit with `Retry-After`.
- [x] Health endpoint with optional upstream latency and process memory probe.
- [x] Prometheus `/metrics` with request counters, latency histogram, cache hit ratio, and rate-limit rejections.
- [x] JSON access logs and trusted proxy hop support.
- [x] Non-root Docker image, Docker Compose with Caddy TLS, and a Helm chart.
- [x] CI on Python 3.10, 3.11, and 3.12 with lint, bandit, pytest, Helm lint and render, and offline Bruno requests.
- [x] Documentation and governance gate for required files, README wording, and internal links.

## Planned

### 2.4.0: API surface and throughput

- [ ] Event filters on daily and bundle endpoints: `currency`, `impact`, and free-text `q`.
- [ ] CSV output via `?format=csv`.
- [ ] Concurrent per-day fetching in `/api/bundle` with a bounded worker pool.
- [ ] `ETag` and `Cache-Control` headers with conditional `GET` support.
- [ ] Retry with exponential backoff for transient upstream failures.

### 3.0.0: Contract hardening

- [ ] Versioned routes under `/api/v1/`, with unversioned paths kept as deprecated aliases for one minor cycle.
- [ ] Consistent error envelope with `code`, `message`, and `request_id` across every endpoint.
- [ ] OpenAPI schema generated from route definitions and verified against responses in CI.

## Ordering

Security fixes and upstream parser breakage come first. Contract stability and observability come next. New API surface follows. Items move into a release when the implementation, tests, and OpenAPI document land together.
