# The perps testnet the bounty runs on (Hideki / "Tokyo") is missing from the documented environments

Severity: major
Area: docs

## Steps to reproduce

1. Bounty page: "a developer program for dreamDEX perps on **Somnia Tokyo testnet**"; the MVP track
   requires "real perps orders on **Somnia Tokyo testnet**".
2. App route: `https://app.testnet.dreamdex.io/trade/perp/tokyo/SOMI:USDso` (200).
3. Docs environment table: `https://app.dreamdex.io/docs/developers/http-api`.
4. Search the docs for "tokyo"; ask the perps RPC for its chain id:

```bash
curl -sS -X POST -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","id":1,"method":"eth_chainId","params":[]}' \
  https://api.hideki2.infra.testnet.somnia.network
```

## Expected

The environment table should list the network the bounty and the app use (name, chain ID, REST base URL,
WebSocket URL), as it does for the other two environments.

## Actual

The table has exactly two rows — Mainnet (Somnia) **5031** and Testnet (Somnia **Shannon**) **50312**.
"tokyo" appears **0 times** in the eight documentation pages checked (HTTP API overview, authentication,
market data, trading, error handling, Perps orders, Perps funding, Libraries), case-insensitive, source
included.

The perps testnet actually used by the app and required by the bounty answers `eth_chainId` with
**`0xc4cf` = 50383** (Hideki) — a chain that appears nowhere in the HTTP API base-URL table. The
documented testnet (Shannon, `stg.api.dreamdex.io`) returns `{"markets":[]}` for `?kind=perp`, so it does
not serve the perps markets the programme asks builders to trade.

## Evidence

- Docs table (verbatim): "Mainnet (Somnia) 5031 https://api.dreamdex.io/v0 … Testnet (Somnia Shannon)
  50312 https://stg.api.dreamdex.io/v0 …"
- `grep -i tokyo` over the eight saved docs pages → 0 matches
- `eth_chainId` on `api.hideki2.infra.testnet.somnia.network` → `0xc4cf` (50383)
- `GET https://stg.api.dreamdex.io/v0/markets?kind=perp` → `200 {"markets":[]}`
- App route `/trade/perp/tokyo/…` → 200

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK.
