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

## Planned Milestones

### v2.1.0 (Performance & Resilience)
- [ ] Optional in-memory caching layer (Redis or TTLCache) for upstream responses with configurable TTL.
- [ ] Configurable per-client rate limiting to prevent upstream blocking.
- [ ] Health check probe metrics (upstream reachability latency, memory usage).

### v2.2.0 (Operations & Deployment)
- [ ] Production-ready `docker-compose.yml` including reverse proxy and SSL termination.
- [ ] Structured JSON logging middleware for integration with log aggregators.
- [ ] Helm chart / Kubernetes deployment manifests.
