# Configuration

ForexFactoryScrapper loads settings through system environment variables or a local `.env` file via `python-dotenv`.

## Environment Variables

| Variable | Type | Default | Required | Description |
| :--- | :--- | :--- | :---: | :--- |
| `HOST` | String | `127.0.0.1` | No | Network interface address to bind HTTP listener (`0.0.0.0` in Docker). |
| `PORT` | Integer | `5000` | No | Port number for incoming HTTP connections. |
| `DEBUG` | Boolean | `False` | No | Enables Flask debug mode and reload on code changes. |
| `CORS_ORIGINS` | Comma-separated | `*` | No | Allowed CORS origin URLs. |
| `MAX_BUNDLE_DAYS` | Integer | `31` | No | Maximum allowed date span for the multi-source bundle endpoint. |
| `MAX_SITEMAP_PAGES` | Integer | `100` | No | Maximum allowed pages to crawl for the sitemaps endpoint. |
| `CACHE_TTL_SECONDS` | Integer | `0` | No | In-memory TTL cache for upstream responses. `0` disables caching. |
| `CACHE_MAX_ENTRIES` | Integer | `256` | No | Maximum cached upstream responses before eviction. |
| `RATE_LIMIT_PER_MINUTE` | Integer | `0` | No | Per-client request cap on `/api/*` (excluding `/api/health`). Exceeding it returns `429` with `Retry-After`. `0` disables. |
| `DOTENV_PATH` | String (Path) | None | No | Explicit file path to load environment variables from. |

## Example Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Default `.env` contents:

```ini
# Host and port for Flask HTTP API
HOST=127.0.0.1
PORT=5000

# Debug mode: True or False (keep False in production)
DEBUG=False

# Allowed CORS origins
CORS_ORIGINS=*

# Resource limits (Denial of Service prevention)
MAX_BUNDLE_DAYS=31
MAX_SITEMAP_PAGES=100
```
