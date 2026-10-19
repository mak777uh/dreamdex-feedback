# `depth` is capped at 1000, but the maximum is not documented

Severity: normal
Area: docs

## Steps to reproduce

```bash
curl -sS 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=SOMI:USDso&depth=1000'
curl -sS 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=SOMI:USDso&depth=1001'
```

## Expected

The Market Data page documents `depth` without stating a maximum (and without stating a default), so a
client cannot know the valid range without triggering an error.

## Actual

`depth=1001` returns **400**, and only the error body reveals the bound:

```json
{"description":"parameter \"depth\" in query has an error: number must be at most 1000\nSchema:\n  {\n    \"maximum\": 1000,\n    \"minimum\": 1,\n    \"type\": \"integer\"\n  }\n\nValue:\n  1001\n","name":"invalid_param","status":400}
```

`depth=1000` works.

## Evidence

- `depth=1001` → 400 with the schema shown above (2026-10-20 00:10 MSK)
- `depth=1000` → 200
- The Market Data page mentions `depth` but neither the maximum (1000) nor the default

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK.
