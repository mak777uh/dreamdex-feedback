# Documented error contracts do not match the wire: `context` is undocumented on REST, and WS bridge frames match neither documented WS shape

Severity: normal
Area: docs

## Steps to reproduce

```bash
# REST: a 400 whose body carries a field the documented schema does not have
curl -sS -i 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=UNKNOWN&depth=1'

# REST: an Error-Name value outside the documented table
curl -sS -I 'https://stg.api.dreamdex.io/v0/markets'
```

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("wss://stg.api.dreamdex.io/v0/ws/public") as ws:
        await ws.send(json.dumps({"id": 1, "operation": "getPortfolio", "bearerToken": "garbage"}))
        print(await ws.recv())

asyncio.run(main())
```

## Expected

Three published contracts should describe the frames actually sent:

1. Error Handling: the error object is `{status, name, description}` plus an `Error-Name` header, and its
   table lists every name the server produces.
2. WebSocket Errors → Protocol Errors: an error is
   `{"type": "error", "errorName": "...", "message": "...", "id": 1}`, and its `errorName` table lists the
   protocol-level names (`invalid_request`, `unknown_operation`, `invalid_parameters`, `too_many_requests`,
   `internal_error`).
3. WebSocket Errors → Subscription Errors: flat envelope, names `unknown_channel`, `subscription_failed`,
   `unsubscribe_failed`, `not_subscribed`.

## Actual

**1. REST sends an undocumented `context` object.** Symbol-validation errors carry the offending values in a
structured field that the documented schema does not contain:

```json
{"context":{"invalid_symbols":["UNKNOWN"]},
 "description":"unknown market symbols: UNKNOWN",
 "name":"invalid_param","status":400}
```

It is not a one-off: the same `context.invalid_symbols` shape comes back for a wrong-case symbol, for a padded
symbol (`[" SOMI:USDso "]`) and for a comma-joined one — it is the API's general convention for "these items in
your request were rejected".

**2. `Error-Name: bad_request` is not in the documented table.** The HEAD responses carry
`error-name: bad_request`; the published name table has no such value.

**3. WS REST-bridge errors use a fourth shape.** A failed bridged REST call returns:

```json
{"id":1,"status":401,"errorName":"unauthorized",
 "payload":{"description":"invalid or expired token","name":"unauthorized","status":401}}
```

This is not the documented Protocol Error `{"type": "error", "errorName", "message", "id"}` — there is no
`type`, no `message`, and two fields the protocol-error section does not describe (`status`, `payload`). The
`errorName` values (`unauthorized`, `invalid_order_id`) are taken from the **REST** name table and are absent
from the WS `errorName` table, so a client validating WS errors against the documented enumeration rejects a
correct frame.

## Evidence

```
$ curl -sS 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=UNKNOWN&depth=1'
{"context":{"invalid_symbols":["UNKNOWN"]},"description":"unknown market symbols: UNKNOWN","name":"invalid_param","status":400}

$ curl -sS -I 'https://stg.api.dreamdex.io/v0/markets'
HTTP/1.1 400 Bad Request
error-name: bad_request
content-type: application/json
content-length: 71

$ websockets → {"id":1,"operation":"getPortfolio","bearerToken":"garbage"}
{"id":1,"status":401,"errorName":"unauthorized","payload":{"description":"invalid or expired token","name":"unauthorized","status":401}}
```

Cross-checked against `https://app.dreamdex.io/docs/developers/http-api/error-handling` and
`https://app.dreamdex.io/docs/developers/websocket-api/errors` on 2026-10-20.

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); WS `wss://stg.api.dreamdex.io/v0/ws/public`; perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK `@somnia-chain/markets-sdk` **0.32.1**. Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-20 07:05-07:40 UTC (10:05-10:40 MSK).

## Why it matters

A client generated from the published schema — or an OpenAPI-generated DTO — deserialises
`status`/`name`/`description` and **drops `context`**, which is the only part of the payload that says *which*
symbols were rejected. The information the server bothered to compute is filtered out by the contract, so the
integration falls back to regex-parsing the human-readable `description`.

The WS half breaks the opposite way: a client that trusts the documented protocol-error envelope reads
`frame["message"]` and gets nothing, because the text lives under `payload.description` — and if it validates
`errorName` against the documented WS list, `unauthorized` and `invalid_order_id` look like unknown errors,
usually routed to the default branch ("unexpected — reconnect"), which is the wrong reaction to an expired token.
