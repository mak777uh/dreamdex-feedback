# Docs: unknown market symbols are not "silently skipped" — the API returns 400 `invalid_param`

Severity: major
Area: docs

## Steps to reproduce

```bash
curl -sS -i 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=NOPE:USDso'
curl -sS -i 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=SOMI:USDso,WETH:USDso'
curl -sS -i 'https://stg.api.dreamdex.io/v0/tickers?symbols=NOPE:USDso'
```

## Expected

The Market Data page's array-serialisation warning says, verbatim:

> "Unknown or malformed symbols are **silently skipped** rather than erroring, so a serialization
> mismatch shows up as an **empty `[]`** rather than a 4xx."

So an unknown symbol (including the comma-joined mistake the docs use as their example) should return
`200` with an empty result.

## Actual

Every unknown symbol produces **HTTP 400**:

```json
{"context":{"invalid_symbols":["NOPE:USDso"]},"description":"unknown market symbols: NOPE:USDso","name":"invalid_param","status":400}
```

The exact example the docs call "silently skipped … response is []" also returns 400:

```json
{"context":{"invalid_symbols":["SOMI:USDso,WETH:USDso"]},"description":"unknown market symbols: SOMI:USDso,WETH:USDso","name":"invalid_param","status":400}
```

Same for `/tickers?symbols=NOPE:USDso` → 400.

## Evidence

- `GET /v0/orderbooks?symbols=NOPE:USDso` → 400, `invalid_symbols: ["NOPE:USDso"]`
- `GET /v0/orderbooks?symbols=SOMI:USDso,WETH:USDso` → 400, `invalid_symbols: ["SOMI:USDso,WETH:USDso"]`
- `GET /v0/tickers?symbols=NOPE:USDso` → 400, same shape
- Control: repeated-key form → 200 with both books

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK.

## Why it matters

Integrations written to the documented contract treat "unknown symbol" as an empty result and ignore a
serialisation bug; the API now fails loudly, so the documented error handling is wrong for the single
most common configuration error.
