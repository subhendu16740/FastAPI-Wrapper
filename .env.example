# Crypto API Framework

FastAPI wrapper around CoinGecko that returns filtered JSON payloads for downstream consumers.

## Endpoints
- `GET /price/{coin_id}` -> compact summary (price, market cap, 24h change, homepage)
- `GET /chart/{coin_id}?days=7` -> simplified list of {timestamp_ms, price} for last N days
- `GET /trending/` -> trending coins
- `GET /health` -> health check
- `GET /docs-json` -> raw OpenAPI JSON
- `GET /docs` -> Swagger UI (interactive)

## Run locally
1. (Optional) create `.env` from `.env.example`.
2. With Python:
