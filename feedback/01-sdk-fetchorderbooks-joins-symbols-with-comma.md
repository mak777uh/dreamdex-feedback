# SDK `fetchOrderbooks()` sends comma-joined symbols, but the API requires repeated keys — every multi-symbol call fails with 400

Severity: major
Area: SDK

## Steps to reproduce

1. Call the documented REST method with more than one symbol. The SDK builds the query like this
   (`somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`, line 72–73):

```ts
async fetchOrderbooks(symbols: string[], depth = 5): Promise<unknown> {
  const q = encodeURIComponent(symbols.join(","));
  return this.request("GET", `/orderbooks?symbols=${q}&depth=${depth}`, { auth: false });
}
```

```ts
await rest.fetchOrderbooks(["SOMI:USDso", "WBTC:USDso"]);
```

2. Equivalent request without the SDK:

```bash
curl -sS -i 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=SOMI:USDso,WBTC:USDso'
```

3. Control — the form the docs require (repeated keys):

```bash
curl -sS -i 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=SOMI:USDso&symbols=WBTC:USDso'
```

## Expected

Two order books returned in one call (the docs' own "correct" form). `fetchOrderbooks()` is the only
order-book helper in the SDK, so a bot that watches two markets is expected to work.

## Actual

- `symbols.join(",")` percent-encodes the comma into a single parameter value, which the API rejects:

```json
{"context":{"invalid_symbols":["SOMI:USDso,WBTC:USDso"]},"description":"unknown market symbols: SOMI:USDso,WBTC:USDso","name":"invalid_param","status":400}
```

- The repeated-key form works and returns both books (`200`, `orderbooks: […]`), so the endpoint itself is
  fine — the SDK's serialisation is not. Any `fetchOrderbooks()` call with two or more symbols fails; only
  the single-symbol case works.

## Evidence

- SDK source: `packages/core/src/rest.ts:72` — `const q = encodeURIComponent(symbols.join(","));`
- `GET /v0/orderbooks?symbols=SOMI:USDso,WBTC:USDso` → **400** `invalid_param`
  (`invalid_symbols: ["SOMI:USDso,WBTC:USDso"]`)
- `GET /v0/orderbooks?symbols=SOMI:USDso&symbols=WBTC:USDso` → **200**, both books present
- Same failure shape for `?symbols=NOPE:USDso` (single unknown symbol) → 400

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK.

## Why it matters

The helper is the documented way to read several books at once; as shipped it can only ever read one.
A trading bot (the MVP track) that watches more than one perps/spot market hits a 400 on its first call
and has to re-implement query serialisation itself.
