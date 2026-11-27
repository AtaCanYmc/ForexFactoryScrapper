# API Reference

This document outlines all public endpoints, parameter constraints, and schema structures.

## Endpoints

| Method | Path | Required Parameters | Optional Parameters | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | None | None | HTML landing page with quick navigation links. |
| `GET` | `/api/hello` | None | None | Basic sanity check endpoint. |
| `GET` | `/api/health` | None | None | Service health check. Add `?probe=true` for upstream latency (ms) and peak memory (MB). |
| `GET` | `/api/forex/daily` | `day`, `month`, `year` | `limit`, `offset` | ForexFactory economic calendar events for a specific day. |
| `GET` | `/api/cryptocraft/daily` | `day`, `month`, `year` | `limit`, `offset` | CryptoCraft calendar events for a specific day. |
| `GET` | `/api/energyexch/daily` | `day`, `month`, `year` | `limit`, `offset` | EnergyExch calendar events for a specific day. |
| `GET` | `/api/metalsmine/daily` | `day`, `month`, `year` | `limit`, `offset` | MetalsMine calendar events for a specific day. |
| `GET` | `/api/bundle` | `start_date`, `end_date` | `sources`, `limit`, `offset` | Aggregated economic events across selected platforms for a date range. |
| `GET` | `/api/forex/sitemaps` | None | `start_date`, `end_date`, `max_pages`, `limit`, `offset` | Paginated sitemap URLs retrieved from ForexFactory. |
| `GET` | `/swagger` | None | None | Swagger UI documentation console. |
| `GET` | `/openapi.json` | None | None | Raw OpenAPI 3.0 schema definition. |

## Daily Events Endpoints

Available endpoints:
- `GET /api/forex/daily`
- `GET /api/cryptocraft/daily`
- `GET /api/energyexch/daily`
- `GET /api/metalsmine/daily`

### Query Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `day` | Integer | Yes | Calendar day of month (1-31). |
| `month` | Integer | Yes | Calendar month (1-12). |
| `year` | Integer | Yes | Four-digit calendar year. |
| `limit` | Integer | No | Maximum number of records to return. Must be non-negative. |
| `offset` | Integer | No | Number of records to skip for pagination. Must be non-negative. |

### Response Schema

```json
{
  "total": 14,
  "offset": 0,
  "limit": 10,
  "results": [
    {
      "id": "138542",
      "date": "2026-05-20",
      "time": "8:30am",
      "currency": "USD",
      "impact": "High",
      "event": "CPI m/m",
      "actual": "0.3%",
      "forecast": "0.2%",
      "previous": "0.4%"
    }
  ]
}
```

## Multi-Source Bundle Endpoint

Path: `GET /api/bundle`

### Query Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `start_date` | String (`YYYY-MM-DD`) | Required | Start date of query range (inclusive). |
| `end_date` | String (`YYYY-MM-DD`) | Required | End date of query range (inclusive). |
| `sources` | Comma-separated string | `forex` | Target sources: `forex`, `crypto`, `metal`, `energy`. |
| `limit` | Integer | None | Maximum total records to return. |
| `offset` | Integer | `0` | Number of records to skip across aggregated results. |

### Example Request

```bash
curl "http://localhost:5000/api/bundle?sources=forex,crypto&start_date=2026-05-20&end_date=2026-05-21&limit=25"
```

## Sitemap Endpoint

Path: `GET /api/forex/sitemaps`

### Query Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `start_date` | String (`YYYY-MM-DD`) | None | Filter sitemaps with `lastmod` on or after this date. |
| `end_date` | String (`YYYY-MM-DD`) | None | Filter sitemaps with `lastmod` on or before this date. |
| `max_pages` | Integer | `10` | Maximum child sitemaps to parse. Must be positive integer. |
| `limit` | Integer | None | Pagination size for URL list. |
| `offset` | Integer | `0` | Pagination offset. |
