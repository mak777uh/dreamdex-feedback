# WebSocket REST-bridge: `getOrderbooks` always fails with `invalid_request`

Severity: major
Area: API

## Steps to reproduce

Python (`websockets`) against the public feed:

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("wss://stg.api.dreamdex.io/v0/ws/public") as ws:
        await ws.send(json.dumps({"id": 1, "operation": "getMarkets"}))
        print(await ws.recv())
        await ws.send(json.dumps({"id": 2, "operation": "getOrderbooks",
                                  "params": {"symbols": ["SOMI:USDso"], "depth": 2}}))
        print(await ws.recv())

asyncio.run(main())
```

## Expected

The WebSocket docs state the feed "can also be used to call the HTTP API … same operations as OpenAPI".
`getOrderbooks` is one of those operations, so a single-symbol, integer-depth call should return the same
book as `GET /v0/orderbooks?symbols=SOMI:USDso&depth=2`.

## Actual

- `getMarkets` over WS works: `{"id":1,"status":200,"payload":{"markets":[…"kind":"spot"…]}}`
- `getOrderbooks` over WS always fails: `{"type":"error","errorName":"invalid_request","message":"invalid JSON request"}`

Reproduced with `params` as `{"symbols": ["SOMI:USDso"], "depth": 2}`. No array-parameter example exists
on the WebSocket page, although the HTTP page documents that array parameters must be sent as repeated
keys — a form that cannot be expressed in a JSON `params` object, which is the likely root cause.

## Evidence

- `getMarkets` → `{"id":1,"status":200,"payload":{"markets":[…]}}` (2026-10-20 01:35 MSK)
- `getOrderbooks` → `{"type":"error","errorName":"invalid_request","message":"invalid JSON request"}`
- The published feed docs promise "same operations as OpenAPI"; the HTTP docs demand repeated keys for
  `symbols`

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK.
