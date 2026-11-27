# Roadmap

This document outlines completed milestones and active development targets for ForexFactoryScrapper. Milestones are organized by version tags.

## Current Release

### v2.0.0
- [x] Multi-source economic calendar aggregation (ForexFactory, CryptoCraft, EnergyExch, MetalsMine).
- [x] Date-range multi-source bundle endpoint (`GET /api/bundle`).
- [x] Sitemap index discovery endpoint (`GET /api/forex/sitemaps`).
- [x] Interactive OpenAPI 3.0 schema and Swagger UI documentation (`GET /swagger`, `GET /openapi.json`).
- [x] Docker containerization and health probe endpoint (`GET /api/health`).
- [x] Continuous integration pipeline across Python 3.10, 3.11, and 3.12.

## Implemented, Pending Release

### v2.1.0 (Performance & Resilience)
- [x] Optional in-memory caching layer (TTL cache; Redis backend added in v2.3.0) for upstream responses with configurable TTL.
- [x] Configurable per-client rate limiting to prevent upstream blocking.
- [x] Health check probe metrics (upstream reachability latency, memory usage).

### v2.2.0 (Operations & Deployment)
- [x] Production-ready `docker-compose.yml` including reverse proxy and SSL termination.
- [x] Structured JSON logging middleware for integration with log aggregators.
- [x] Helm chart / Kubernetes deployment manifests.

### v2.3.0 (Observability & Security)
- [x] Prometheus `/metrics` endpoint (request count, latency histogram, cache hit ratio, rate-limit rejections).
- [x] Optional API key authentication for `/api/*` via `API_KEYS` environment variable.
- [x] Redis cache backend selectable with `CACHE_BACKEND=redis`, for sharing cache across replicas (deferred from v2.1.0).
- [x] CI job running `helm lint` and `helm template` against `deploy/helm/forexfactory-scrapper`.

## Planned Milestones

### v2.4.0 (API Surface & Throughput)
- [ ] Event filters on daily and bundle endpoints: `currency`, `impact`, and free-text `q`.
- [ ] CSV output via `?format=csv` for spreadsheet and BI imports.
- [ ] Concurrent per-day fetching in `/api/bundle` with a bounded worker pool.
- [ ] `ETag` and `Cache-Control` headers with conditional `GET` support.
- [ ] Retry with exponential backoff for transient upstream failures.

### v3.0.0 (Contract Hardening)
- [ ] Versioned routes under `/api/v1/` with the unversioned paths kept as deprecated aliases for one minor cycle.
- [ ] Consistent error envelope (`code`, `message`, `request_id`) across all endpoints.
- [ ] OpenAPI schema generated from route definitions and verified against responses in CI.
