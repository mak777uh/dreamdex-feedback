# `limit` is validated on `/trades` and `/candles` but silently ignored on `/tickers` and `/orderbooks`

Severity: major
Area: API

## Steps to reproduce

```bash
# silently ignored: any value, including nonsense
curl -sS 'https://stg.api.dreamdex.io/v0/tickers?limit=1'
curl -sS -o /dev/null -w '%{http_code}\n' 'https://stg.api.dreamdex.io/v0/tickers?limit=abc'
curl -sS -o /dev/null -w '%{http_code}\n' 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=SOMI:USDso&limit=1'

# same parameter, validated strictly
curl -sS -o /dev/null -w '%{http_code}\n' 'https://stg.api.dreamdex.io/v0/markets/SOMI:USDso/trades?limit=abc'
curl -sS -o /dev/null -w '%{http_code}\n' 'https://stg.api.dreamdex.io/v0/markets/SOMI:USDso/candles?limit=abc'
```

## Expected

One parameter name behaves one way across the API. The error contract says invalid values produce
`invalid_param`, and `/trades` and `/candles` do exactly that — `limit=abc` → 400, `limit=0` → 400
("number must be at least 1"), `limit=10000` → 400 ("at most 1000").

## Actual

- `/v0/tickers?limit=1` → **200** with **all 3** tickers (limit ignored).
- `/v0/tickers?limit=abc` → **200** (invalid value accepted silently).
- `/v0/orderbooks?symbols=SOMI:USDso&limit=1` → **200** with the **full** book (limit ignored).
- `/v0/markets/SOMI:USDso/trades?limit=abc` → **400** `invalid_param`.
- `/v0/markets/SOMI:USDso/candles?limit=abc` → **400** `invalid_param`.

So the same `limit` is enforced on two endpoints and swallowed on two others, with no way for a client
to tell which behaviour it got.

## Evidence

| request | status | effect |
|---|---|---|
| `GET /v0/tickers?limit=1` | 200 | 3 symbols returned (no limiting) |
| `GET /v0/tickers?limit=abc` | 200 | accepted, no `invalid_param` |
| `GET /v0/orderbooks?symbols=SOMI:USDso&limit=1` | 200 | full book |
| `GET /v0/markets/SOMI:USDso/trades?limit=abc` | 400 | `invalid_param` |
| `GET /v0/markets/SOMI:USDso/candles?limit=abc` | 400 | `invalid_param` |

## Environment

Indexer `https://hideki-dev.smk.somnia.host/v1/graphql` (Hideki, chain **50383**); REST `https://stg.api.dreamdex.io/v0` (Shannon, chain 50312); mainnet `https://api.dreamdex.io/v0` (chain 5031). SDK `@somnia-chain/markets-sdk` **0.32.1**. No wallet, no auth. Client: `curl 8.x`. Captured 2026-10-19 22:50 UTC.

## Why it matters

A polling client that sets `limit=1` to keep payloads small gets the full payload instead — the request
looks successful, so nothing in logs reveals the mistake, and bandwidth/parse cost is silently several
times higher than intended. A typo (`limt`, `limit=abc`) also passes unnoticed on two endpoints and
fails loudly on two others, which makes the same client code behave differently depending on the route.
