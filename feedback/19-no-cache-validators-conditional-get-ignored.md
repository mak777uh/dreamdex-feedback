# Public market metadata is served without cache validators, and conditional requests are ignored

Severity: normal
Area: API

## Steps to reproduce

```bash
# what the response actually carries
curl -sS -D - -o /dev/null 'https://stg.api.dreamdex.io/v0/markets'

# a conditional request with a validator and a date far in the past
curl -sS -H 'If-None-Match: "abc"' \
        -H 'If-Modified-Since: Wed, 01 Jan 2020 00:00:00 GMT' \
        -D - -o /dev/null 'https://stg.api.dreamdex.io/v0/markets'
```

## Expected

A documented rule for one of the two behaviours:

- either the market metadata is cacheable — then `Cache-Control` / `ETag` / `Last-Modified` are present and a
  conditional `GET` with a matching validator answers `304 Not Modified` with no body;
- or it is explicitly uncacheable — then `Cache-Control: no-store` says so, and the conditional request is
  answered predictably instead of silently with a full `200`.

## Actual

`/markets` and `/orderbooks` return no caching metadata at all — no `Cache-Control`, `ETag`,
`Last-Modified`, `Age` or `Expires` (the only related header is `vary: Origin`):

```
$ curl -sS -D - -o /dev/null https://stg.api.dreamdex.io/v0/markets
HTTP/1.1 200 OK
content-type: application/json
vary: Origin
content-length: 1075
```

A conditional request is not honoured: it returns **200 with the full 1075-byte body**, byte-identical to the
unconditional response, so both validators are ignored rather than rejected.

## Evidence

| request | status | body |
|---|---|---|
| `GET /v0/markets` | 200 | 1075 B |
| `GET /v0/markets` (If-None-Match + If-Modified-Since) | **200** | 1075 B — full body, no `304` |
| `GET /v0/orderbooks?symbols=SOMI:USDso&depth=1` | 200 | no cache-related headers |

Captured 2026-10-20 07:05-07:40 UTC (10:05-10:40 MSK) on the perps testnet.

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK `@somnia-chain/markets-sdk` **0.32.1**. Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `urllib`.

## Why it matters

The fields in `/markets` — `tickSize`, `lotSize`, `minQuantity`, token addresses, decimals — change when a
market is listed, not per request; only prices are volatile, and they are on `/tickers`. Without a validator
a client has no way to reuse them, so every process re-downloads the same 1075 bytes on every start and every
refresh, spending the documented 100-request budget on data that did not change. A `304` path is the cheapest
possible win: the server sends headers only, the client keeps parsing the cached payload.

Secondary, same area: because no header states the caching policy, intermediaries are free to make up their
own — some caches will keep `/markets` for minutes, others never; clients cannot tell which server they talked to.
