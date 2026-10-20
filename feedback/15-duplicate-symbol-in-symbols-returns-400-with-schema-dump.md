# A duplicated symbol in repeated-key `symbols` returns 400 `duplicate items found` (with an OpenAPI schema dump)

Severity: normal
Area: API

## Steps to reproduce

```bash
curl -sS -i 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=SOMI:USDso&symbols=SOMI:USDso'
curl -sS -i 'https://stg.api.dreamdex.io/v0/tickers?symbols=SOMI:USDso&symbols=SOMI:USDso'

# related: an empty value on the same parameter
curl -sS -i 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=&depth=1'
```

## Expected

The docs prescribe repeated keys for multiple symbols (`?symbols=A&symbols=B`). A duplicated entry is an
ordinary consequence of merging watchlists, so either the server de-duplicates and returns one book, or
the docs state that the array must contain unique items (and how many items it accepts).

## Actual

```http
HTTP/1.1 400 Bad Request
content-type: application/json
error-name: invalid_param
```

```json
{"description":"parameter \"symbols\" in query has an error: duplicate items found\nSchema:\n  {\n    \"example\": [\n      \"SOMI:USDso\",\n      \"WETH:USDso\"\n    ],\n    \"items\": {\n      \"$ref\": \"#/components/schemas/Symbol\"\n    },\n    \"maxItems\": 16,\n    \"type\": \"array\",\n    \"uniqueItems\": true\n  }","name":"invalid_param","status":400}
```

The error body is the only place where `uniqueItems: true` and `maxItems: 16` are revealed — neither is
in the market-data documentation. The same body also echoes the offending value:

```
Value:
  [
    "SOMI:USDso",
    "SOMI:USDso"
  ]
```

So one 400 response pastes the internal JSON schema **and** the request value into a human-readable
`description`, while the error object has no structured field for either.

**The same parameter has three different failure shapes.** Absent is silently accepted (the endpoint works
without `symbols`), empty is `invalid_param` ("empty value is not allowed") rather than `missing_field`, and
duplicated is `invalid_param` with the schema dump — three different contracts for one parameter, none of them
documented.

## Evidence

- `GET /v0/orderbooks?symbols=SOMI:USDso&symbols=SOMI:USDso` → 400 `duplicate items found`,
  schema embedded in `description` shows `"maxItems": 16, "uniqueItems": true`, and the offending value is
  echoed in a `Value:` block
- Same for `/v0/tickers` with a duplicated symbol
- `GET /v0/orderbooks?symbols=&depth=1` → 400 `invalid_param` "empty value is not allowed" (not `missing_field`)
- Control: two *different* symbols in repeated keys → 200 with both books

## Environment

Indexer `https://hideki-dev.smk.somnia.host/v1/graphql` (Hideki, chain **50383**); REST `https://stg.api.dreamdex.io/v0` (Shannon, chain 50312); mainnet `https://api.dreamdex.io/v0` (chain 5031). SDK `@somnia-chain/markets-sdk` **0.32.1**. No wallet, no auth. Client: `curl 8.x`. Captured 2026-10-19 22:50 UTC.
