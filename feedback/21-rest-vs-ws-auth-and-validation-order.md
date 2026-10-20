# Authentication and parameter validation run in a different order on REST and on WebSocket

Severity: normal
Area: API

Status: reproduces on **stg** as of 2026-10-20 (REST `/portfolio` without a token → `400 missing_field`, WS `getPortfolio` → `401`). On `api.testnet.dreamdex.io` REST also answers 401 without a token, so the two transports agree there and the mismatch is host-specific.

## Steps to reproduce

```bash
# REST: private endpoint, no token, no timeframe
curl -sS -i 'https://stg.api.dreamdex.io/v0/portfolio'

# REST: same endpoint, valid timeframe, garbage token
curl -sS -i -H 'Authorization: Bearer garbage' 'https://stg.api.dreamdex.io/v0/portfolio?timeframe=1d'

# REST: another private endpoint, no token, garbage order id
curl -sS -i 'https://stg.api.dreamdex.io/v0/markets/SOMI:USDso/orders/x'
```

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("wss://stg.api.dreamdex.io/v0/ws/public") as ws:
        for req in (
            {"id": 1, "operation": "getPortfolio", "bearerToken": "garbage"},
            {"id": 2, "operation": "getMarketSymbolOrder",
             "params": {"symbol": "SOMI:USDso", "id": "x"}, "bearerToken": "garbage"},
        ):
            await ws.send(json.dumps(req))
            print(await ws.recv())

asyncio.run(main())
```

## Expected

A private operation checks the credential **before** it examines the parameters, on both transports, so:

- an unauthenticated caller gets `401 unauthorized` and learns nothing about the request schema;
- a `400` always means "you are authenticated, and this field is wrong", which is what lets a client decide
  whether to re-authenticate or to fix its request.

## Actual

The order flips between transports, and inside one transport between operations.

**REST `/portfolio` validates parameters first, then the token:**

```http
GET /v0/portfolio                  (no timeframe, no Authorization)
HTTP/1.1 400 Bad Request
{"description":"Query argument timeframe is required...","name":"missing_field","status":400}
```
```http
GET /v0/portfolio?timeframe=1d      (Authorization: Bearer garbage)
HTTP/1.1 401 Unauthorized
{"description":"authentication required","name":"unauthorized","status":401}
```

**WS `getPortfolio` validates the token first — same operation, opposite order:**

```json
{"id":1,"status":401,"errorName":"unauthorized","payload":{"description":"invalid or expired token","name":"unauthorized","status":401}}
```

**REST `/markets/{symbol}/orders/{id}` validates the token first — and here WS is the one that checks the
parameter first:**

```http
GET /v0/markets/SOMI:USDso/orders/x   (no token)
HTTP/1.1 401 Unauthorized             → unauthorized
```
```json
{"id":2,"status":400,"errorName":"invalid_order_id","payload":{"description":"invalid order ID: x","name":"invalid_order_id","status":400}}
```

So for the same two operations the transports disagree in *opposite* directions:

| operation | REST | WebSocket |
|---|---|---|
| portfolio | `params → auth` (`400 missing_field`) | `auth → params` (`401`) |
| order by id | `auth → params` (`401`) | `params → auth` (`400 invalid_order_id`) |

## Evidence

| probe | status | error name |
|---|---|---|
| REST `/v0/portfolio` (no token, no timeframe) | **400** | `missing_field` (timeframe) |
| REST `/v0/portfolio?timeframe=1d` (garbage token) | **401** | `unauthorized` |
| WS `getPortfolio` (garbage token) | **401** | `unauthorized` — no parameter complaint |
| REST `/v0/markets/SOMI:USDso/orders/x` (no token) | **401** | `unauthorized` |
| WS `getMarketSymbolOrder` (garbage token, `id: "x"`) | **400** | `invalid_order_id` |

Captured 2026-10-20 07:05-07:40 UTC on the perps testnet, over `curl 8.x` and Python `websockets`; three runs,
stable.

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); WS `wss://stg.api.dreamdex.io/v0/ws/public`; perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK `@somnia-chain/markets-sdk` **0.32.1**. Public endpoints only — no wallet, no API key.

## Why it matters

The status code stops being a decision input. A `400` can mean "bad token" (WS, order by id) or "missing
`timeframe`" (REST, portfolio), so a client cannot write one retry hook that re-authenticates on `401` and
gives up on `400` — the WS order path never emits `401`, so a reconnect loop driven by `401` will spin forever
on an expired token that is reported as an invalid order id.

In the other direction, an unauthenticated `GET /v0/portfolio` answers `400 missing_field` and thereby
confirms to a stranger that the endpoint takes a `timeframe` argument — the parameter schema is disclosed
before the credential is checked.

Because the two transports disagree, an SDK author must hard-code a per-operation, per-transport validation
order to mirror the server — the kind of coupling a published error contract exists to remove.
