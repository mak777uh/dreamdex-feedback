# Protected endpoints answer 401 without a `WWW-Authenticate` header

Severity: normal
Area: API

## Steps to reproduce

```bash
curl -sS -i 'https://stg.api.dreamdex.io/v0/orders'
curl -sS -i 'https://stg.api.dreamdex.io/v0/trades'
```

## Expected

A 401 response carries `WWW-Authenticate` naming the scheme, so a client (or a generic HTTP library, a
retry middleware, a browser) can discover how to authenticate — RFC 9110 §15.5.2 requires the header for
401.

## Actual

Both endpoints return a correct JSON error, but no `WWW-Authenticate`:

```http
HTTP/1.1 401 Unauthorized
content-type: application/json
error-name: unauthorized
Content-Length: 77

{"description":"authentication required","name":"unauthorized","status":401}
```

## Evidence

- `GET /v0/orders` → 401, `error-name: unauthorized`, **no `www-authenticate`**
- `GET /v0/trades` → 401, same shape
- Authentication docs describe a bearer token / SIWE flow, but nothing in the response advertises it

## Environment

Indexer `https://hideki-dev.smk.somnia.host/v1/graphql` (Hideki, chain **50383**); REST `https://stg.api.dreamdex.io/v0` (Shannon, chain 50312); mainnet `https://api.dreamdex.io/v0` (chain 5031). SDK `@somnia-chain/markets-sdk` **0.32.1**. No wallet, no auth. Client: `curl 8.x`. Captured 2026-10-19 22:50 UTC.
