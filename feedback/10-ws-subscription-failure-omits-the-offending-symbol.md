# WebSocket `subscription_failed` does not say which symbol was rejected

Severity: normal
Area: API

## Steps to reproduce

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("wss://stg.api.dreamdex.io/v0/ws/public") as ws:
        await ws.send(json.dumps({"id": 3, "operation": "subscribe", "channel": "orderbook",
                                  "params": {"symbols": ["SOMI:USDso", "BTC-PERP"]}}))
        for _ in range(3):
            print(await ws.recv())

asyncio.run(main())
```

## Expected

A subscription error that names the offending symbol (or at least the rejected parameter), so a client
subscribing to several markets can drop the bad one and keep the rest.

## Actual

```json
{"type":"error","errorName":"subscription_failed","message":"subscription failed to channel: orderbook"}
```

The message names only the channel: "orderbook". With more than one symbol in the request there is no way
to tell which symbol was rejected, and the connection stays open with no snapshot for any of them.

**The two documentation pages also contradict each other about this frame.** Real-Time Feed documents
`error:error` with `channel` as a **required** field (constraint `"error"`), alongside `type: "error"` and
`message` — no `errorName` at all. The Errors page says the opposite, in bold: "The envelope is flat - there
is **no** `channel` field on a subscription error", and shows
`{"type": "error", "errorName": "unknown_channel", "message": "..."}`.

The live frame follows the Errors page — it has `errorName`, and no `channel` — so a client generated from the
Real-Time Feed schema drops the only field that identifies the failure.

## Evidence

- Live frame captured 2026-10-20 01:35 MSK and re-captured 03:1x MSK from `wss://stg.api.dreamdex.io/v0/ws/public`
- Contrast: on the same connection `{"id":1,"operation":"getMarkets"}` returns a normal 200 payload, so
  the socket and protocol are healthy
- Docs cross-check: `https://app.dreamdex.io/docs/developers/websocket-api/real-time-feed` (`error:error`:
  `channel` required) vs `https://app.dreamdex.io/docs/developers/websocket-api/errors` (flat, no `channel`)

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK.
