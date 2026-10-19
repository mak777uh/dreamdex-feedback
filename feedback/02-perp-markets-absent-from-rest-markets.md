# Perp markets are not exposed by the documented market list: `kind` is undocumented and `kind=perp` is empty everywhere

Severity: major
Area: API

## Steps to reproduce

```bash
curl -sS 'https://stg.api.dreamdex.io/v0/markets'
curl -sS 'https://stg.api.dreamdex.io/v0/markets?kind=perp'
curl -sS 'https://api.dreamdex.io/v0/markets?kind=perp'
curl -sS 'https://stg.api.dreamdex.io/v0/markets?kind=all'
curl -sS 'https://stg.api.dreamdex.io/v0/markets?kind=perps'   # note the typo — the 400 leaks the schema
```

## Expected

The bounty is a **perps** builder programme and the Order Types docs say to "read the live values per
market from `GET /v0/markets`", so perp markets (symbol, tick size, lot size, min quantity) should be
enumerable through that endpoint.

## Actual

- `GET /v0/markets` (testnet) → **3 spot markets**, every item `"kind": "spot"`.
  Mainnet → **4 spot markets**, also `"kind": "spot"` only.
- `GET /v0/markets?kind=perp` → **`200 {"markets":[]}` on both testnet and mainnet**.
- `GET /v0/markets?kind=all` → same spot-only set as the default call.
- `GET /v0/markets?kind=perps` → **400**, and the error body publishes the parameter schema the docs omit:

```json
{"description":"parameter \"kind\" in query has an error: value is not one of the allowed values [\"spot\",\"perp\",\"all\"]\nSchema:\n  {\n    \"default\": \"spot\", …","name":"invalid_param","status":400}
```

- The Market Data documentation page does **not mention `kind` at all** (0 occurrences), so a reader has
  no way to learn that the list is spot-filtered by default. Perp market data only exists in the SDK
  (`listPerpMarkets`) and the Hideki indexer, neither of which the HTTP docs point to.

## Evidence

- `stg …/v0/markets` → 200, items: `SOMI:USDso`, `WBTC:USDso`, `WETH:USDso` (all `kind: "spot"`)
- `api …/v0/markets` → 200, 4 items, all `kind: "spot"`
- `stg …/v0/markets?kind=perp` → `200 {"markets":[]}`; same on mainnet
- `stg …/v0/markets?kind=perps` → `400 invalid_param`, body contains enum `["spot","perp","all"]`,
  `"default": "spot"`
- Control: `stg …/v0/orderbooks?symbols=SOMI:USDso&symbols=WETH:USDso` → 200 (endpoint works)

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK.
