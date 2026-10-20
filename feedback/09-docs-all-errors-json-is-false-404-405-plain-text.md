# Docs: "all error responses use a consistent JSON format" is false for 404 and 405

Severity: normal
Area: docs

Status: reproduces on **stg** and **mainnet** as of 2026-10-20 (404 and a trailing slash return `text/plain`, a bodyless POST returns 411 HTML). On `api.testnet.dreamdex.io` both are JSON 404 and POST answers 404 rather than 405, so the phrase "all errors are JSON" is still false there for other reasons.

## Steps to reproduce

```bash
curl -sS -i 'https://stg.api.dreamdex.io/v0/nope'
curl -sS -i -X POST -H 'Content-Type: application/json' --data '{}' 'https://stg.api.dreamdex.io/v0/markets'
curl -sS -i -X POST 'https://stg.api.dreamdex.io/v0/markets'   # no body at all
curl -sS -i -X OPTIONS 'https://stg.api.dreamdex.io/v0/markets'   # no Origin header
curl -sS -i 'https://stg.api.dreamdex.io/v0/markets/'            # trailing slash on a real route
```

## Expected

The Error Handling page states that all error responses share one JSON format (with `name`, `description`,
`status`) and an `Error-Name` header.

## Actual

- Unknown path → **404** with `content-type: text/plain; charset=utf-8`, body `404 page not found`,
  **no `Error-Name` header**.
- Wrong method (with a JSON body) → **405** with `content-type: text/plain; charset=utf-8`,
  `allow: GET, HEAD`, **no JSON body and no `Error-Name`**.
- Wrong method without a body → **411 Length Required** returning an **HTML** page.
- OPTIONS without an Origin header → **405** with content-type: text/plain; charset=utf-8,
  again without JSON or Error-Name. (A genuine CORS preflight, with Origin, correctly returns 204
  and the ccess-control-* headers.)
- A trailing slash on a real route (`/v0/markets/`) → **404** with `content-type: text/plain; charset=utf-8`,
  body `404 page not found` — the router is strict, the client gets no hint that the route exists one slash
  to the left, and the error escapes the JSON envelope like the two cases above.

Known routes do return the documented JSON (e.g. `GET /v0/markets/NOPE:USDso` → `market_not_found`), so
the inconsistency is limited to routing-level errors — exactly the class a client's global error handler
sees first.

## Evidence

```
HTTP/1.1 404 Not Found
content-type: text/plain; charset=utf-8

404 page not found
```
```
HTTP/1.1 405 Method Not Allowed
allow: GET, HEAD
content-type: text/plain; charset=utf-8
```
```
HTTP/1.1 404 Not Found
content-type: text/plain; charset=utf-8

404 page not found          <- GET /v0/markets/  (trailing slash)
```
```
HTTP/1.0 411 Length Required
Content-Type: text/html; charset=UTF-8
`
`
HTTP/1.1 405 Method Not Allowed
allow: GET, HEAD
content-type: text/plain; charset=utf-8
```

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK.
