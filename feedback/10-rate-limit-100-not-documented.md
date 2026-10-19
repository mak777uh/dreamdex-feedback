# The 100-request rate limit is visible only in response headers, never in the docs

Severity: normal
Area: docs

## Steps to reproduce

```bash
curl -sS -D - -o /dev/null 'https://stg.api.dreamdex.io/v0/markets'
```

## Expected

The Error Handling / Market Data docs mention `429` as a possible answer but do not state the limit, so a
client cannot size its polling loop before hitting it.

## Actual

The effective limit is discoverable only from headers on every response:

```
x-ratelimit-limit: 100
x-ratelimit-remaining: 99
x-ratelimit-reset: 1792447915
```

No documentation page states 100, nor the size of the window, nor which endpoints share the budget.

## Evidence

- Response headers captured 2026-10-20 00:11 MSK from `GET /v0/markets`
- Docs search for a numeric limit: the value appears only in headers, not in the docs

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK.
