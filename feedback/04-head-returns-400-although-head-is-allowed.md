# HEAD returns 400 on every GET endpoint, although the server itself advertises `Allow: GET, HEAD`

Severity: major
Area: API

## Steps to reproduce

```bash
curl -sS -I 'https://stg.api.dreamdex.io/v0/markets'
curl -sS -I 'https://stg.api.dreamdex.io/v0/tickers'
curl -sS -I 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=SOMI:USDso'

# control: same URLs with GET
curl -sS -o /dev/null -w '%{http_code}\n' 'https://stg.api.dreamdex.io/v0/markets'
```

## Expected

`HEAD` must return the same status and headers as `GET`, without a body (RFC 9110 §9.3.2). The server
itself advertises HEAD as supported — its 405 response to a write method carries `allow: GET, HEAD`.

## Actual

All three endpoints answer HEAD with **400** and an error name reserved for malformed input:

```http
HTTP/1.1 400 Bad Request
content-type: application/json
error-name: bad_request
Content-Length: 71
```

The identical URLs answer GET with **200** and the expected payload, so the route exists and the method
is advertised — only the HEAD branch fails.

## Evidence

| request | status | error-name |
|---|---|---|
| `HEAD /v0/markets` | **400** | `bad_request` |
| `HEAD /v0/tickers` | **400** | `bad_request` |
| `HEAD /v0/orderbooks?symbols=SOMI:USDso` | **400** | `bad_request` |
| `GET /v0/markets` | 200 | — |
| `POST /v0/markets` (405) | 405 | body carries `allow: GET, HEAD` |

## Environment

Indexer `https://hideki-dev.smk.somnia.host/v1/graphql` (Hideki, chain **50383**); REST `https://stg.api.dreamdex.io/v0` (Shannon, chain 50312); mainnet `https://api.dreamdex.io/v0` (chain 5031). SDK `@somnia-chain/markets-sdk` **0.32.1**. No wallet, no auth. Client: `curl 8.x`. Captured 2026-10-19 22:50 UTC.

## Why it matters

HEAD is the cheap liveness probe: uptime monitors, load balancers, CDN and cache revalidation, and
crawlers all use it before a GET. Every one of them records this API as down (4xx) while it is healthy.
An integration that keeps a HEAD-based health check will retry or fail over on a perfectly working
endpoint.
