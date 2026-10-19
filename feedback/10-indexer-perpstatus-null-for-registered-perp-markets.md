# Indexer: `perpStatus`, `perpRestricted` and `perpStatusUpdatedAt` are null for every registered perp market

Severity: normal
Area: API

## Steps to reproduce

```bash
curl -sS -X POST -H 'Content-Type: application/json' \
  --data '{"query":"{ Market(where: {perpRegistered: {_eq: true}}, limit: 5) { id perpRegistered perpStatus perpRestricted perpStatusUpdatedAt } }"}' \
  https://hideki-dev.smk.somnia.host/v1/graphql
```

## Expected

The docs describe perp market status fields (`perpStatus`, `perpRestricted`) so an indexer consumer can
tell whether a market is active, halted or close-only. The type really does expose these fields
(`__type(name: "Market")` lists `perpStatus`, `perpRestricted`, `perpStatusUpdatedAt`, `perpRegistered`).

## Actual

Every registered perp market returns `perpRegistered: true` with all three status fields **null**:

```json
{"data":{"Market":[
  {"id":"0xf71b619450bafe953f47b9b556416a3a67b443b5","perpRegistered":true,"perpStatus":null,"perpRestricted":null,"perpStatusUpdatedAt":null},
  … four more identical rows …
]}}
```

A consumer cannot distinguish an active market from a halted or close-only one; only `perpRegistered`
carries information.

## Evidence

- Introspection confirms the fields exist: `perpStatus`, `perpRestricted`, `perpStatusUpdatedAt`,
  `perpRegistered` (104 fields on `Market`)
- The filtered query above returns 5 rows, all `perpRegistered: true`, all statuses null
  (2026-10-20 01:36 MSK)

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK. Indexer: `https://hideki-dev.smk.somnia.host/v1/graphql` (Hideki, 50383).
