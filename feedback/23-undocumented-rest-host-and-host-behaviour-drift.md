# An undocumented REST host serves the perp market list, and its behaviour drifts from the documented hosts

Severity: major
Area: API

## Steps to reproduce

```bash
# the documented hosts
curl -sS 'https://stg.api.dreamdex.io/v0/markets?kind=perp'      # {"markets":[]}
curl -sS 'https://api.dreamdex.io/v0/markets?kind=perp'          # {"markets":[]}

# the host that actually serves perps
curl -sS 'https://api.testnet.dreamdex.io/v0/markets?kind=perp'  # 24 perp markets, ~19.5 KB
```

## Expected

Either the docs name the REST host that serves the perp testnet, or the documented hosts serve the same
list. A builder reading "Perps on Testnet" should not have to discover a host by guessing.

## Actual

`api.testnet.dreamdex.io` answers `GET /v0/markets?kind=perp` with **200 and 24 markets** whose
`"kind"` is `"perp"` (`ADA:USDso`, `AVAX:USDso`, `BNB:USDso`, `DOGE:USDso`, …). The two documented REST
hosts answer the identical request with **`200 {"markets":[]}`**.

The Perps (Testnet) page lists, under "Perps on Testnet for Developers": chain id **50383**, RPC
`https://api.hideki2.infra.testnet.somnia.network`, WebSocket
`wss://api.hideki2.infra.testnet.somnia.network/ws` and indexer
`https://hideki-dev.smk.somnia.host/v1/graphql` — **no REST host at all**. The only way to find
`api.testnet.dreamdex.io` is to guess it.

The `kind` query parameter is not documented either: nothing states that `/markets` accepts a filter,
or which values it takes. Without it the documented hosts return only the three spot markets, so a
client that follows the docs cannot see that a perp market exists.

## Host drift (one API, three deployments)

The undocumented host is not the documented host with more data — it is a different build. Measured the
same day, 2026-10-20:

| Probe | stg / mainnet | api.testnet.dreamdex.io |
|---|---|---|
| `HEAD /v0/markets` | **400** `bad_request`, while 405 advertises `Allow: GET, HEAD` | **200** |
| WS `getOrderbooks` | **`invalid_request`** (`invalid JSON request`) | **200** with the books |
| `GET /v0/tickers?limit=1` | `limit` silently ignored (3 symbols) | identical (ignored) |
| `x-ratelimit-limit` | **100** | **200** |
| `GET /v0/nope` | 404 **text/plain**, no `Error-Name` | 404 **JSON** |
| `POST /v0/markets` (405 case) | **405** with `Allow: GET, HEAD` | **404** |
| `symbols=somi:usdso` (wrong case) | **400** `invalid_param` | **200** (case-insensitive) |
| `symbols=A,B` (comma-joined) | **400** `invalid_param` | **200** |
| `GET /v0/portfolio` without a token | **400** `missing_field` | **401** `unauthorized` |
| `/tickers` order over 8 identical calls | 2 distinct orders | 1 order |

So the same client, same SDK and same paths produce different status codes, different error envelopes
and different acceptance rules depending on the host — and the host that behaves best is the one nobody
documents.

## Evidence

```
$ curl -sS 'https://api.testnet.dreamdex.io/v0/markets?kind=perp' | head -c 220
{"markets":[{"base":"0x…","baseDecimals":18,"contract":"0x…","kind":"perp","lotSize":"…",
$ curl -sS 'https://stg.api.dreamdex.io/v0/markets?kind=perp'
{"markets":[]}
```

Docs page captured 2026-10-20: `https://app.dreamdex.io/docs/developers/perps-testnet` — table of
Network / Chain ID / RPC / WebSocket / Indexer / Explorer, no REST base URL; the string
`api.testnet.dreamdex.io` does not occur on the page.

## Environment

Documented REST hosts `https://stg.api.dreamdex.io/v0` (Shannon, chain **50312**) and
`https://api.dreamdex.io/v0` (chain **5031**); undocumented host `https://api.testnet.dreamdex.io/v0`
(serves perp markets); perps chain **Hideki 50383** (`eth_chainId` → `0xc4cf`). SDK
`@somnia-chain/markets-sdk` **0.32.1**. Public endpoints only — no wallet, no API key, no transactions.
Client: `curl 8.x` / Python `urllib` / Python `websockets`. Captured 2026-10-20 11:30–12:00 UTC.

## Why it matters

A perps integration written against the documentation cannot list the perp markets at all: on the
documented hosts the list is empty, and the only host that fills it is unlisted. Finding it requires
guessing a hostname, and once found, the client silently inherits a different contract (status codes,
error envelope, rate limit, symbol casing) than the one it validated against — the kind of mismatch that
only shows up in production, on the wrong environment. Documenting the host and the `kind` parameter is
a one-paragraph fix that removes the guessing entirely.

_Note: the undocumented host was found during the 2026-10-20 re-verification of this feedback set; the
host-drift table above was measured in the same session._
