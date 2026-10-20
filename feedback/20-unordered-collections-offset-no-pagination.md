# Collection responses come back in a different order each time, and `offset` is accepted but never paginates

Severity: normal
Area: API

## Steps to reproduce

```bash
# same request, repeated
for i in $(seq 1 12); do
  curl -sS 'https://stg.api.dreamdex.io/v0/tickers' | jq -c '[.symbols[].symbol]'
done

# paging parameter
for o in 0 1 2 5; do
  curl -sS "https://stg.api.dreamdex.io/v0/markets?offset=$o" | jq -c '[.markets[].symbol]'
done
```

Python equivalent used for the numbers below (12 runs per endpoint):

```python
import collections, json, urllib.request

def symbols(path, key):
    with urllib.request.urlopen("https://stg.api.dreamdex.io/v0" + path) as r:
        return " -> ".join(m["symbol"] for m in json.loads(r.read())[key])

seen = collections.Counter(symbols("/tickers", "symbols") for _ in range(12))
print(seen)
```

## Expected

One of:

- a documented sort order (e.g. by `symbol`), so two identical requests return an identical array; or
- a documented statement that the order is unspecified — and then no `offset`/paging parameter is offered,
  because a page index is meaningless over an unordered collection.

## Actual

**The order rotates between responses.** 12 identical `GET /v0/tickers` requests produced three different
orders:

```
8x  SOMI:USDso -> WBTC:USDso -> WETH:USDso
2x  WBTC:USDso -> WETH:USDso -> SOMI:USDso
2x  WETH:USDso -> SOMI:USDso -> WBTC:USDso
```

`/v0/markets` does the same, less often: 2 distinct orders in 12 runs (11x `SOMI, WBTC, WETH`, 1x
`WETH, SOMI, WBTC`). The orders are rotations of one another, which is the signature of iterating a hash map
whose iteration order is not fixed.

**`offset` has no effect.** `offset=0..5` all return `200` with the same complete list; so does `offset=abc`.
The parameter is not rejected and not applied. The same holds for arbitrary unknown parameters — `?foo=bar`
and `?page=2` are answered `200` with the full payload, so the API does not validate query keys it does not
implement.

## Evidence

| request | status | result |
|---|---|---|
| `GET /v0/tickers` × 12 | 200 × 12 | 3 distinct orders (8/2/2) |
| `GET /v0/markets` × 12 | 200 × 12 | 2 distinct orders (11/1) |
| `GET /v0/markets?offset=0..2,5` | 200 | full list every time, order still varies |
| `GET /v0/markets?offset=abc` | 200 | accepted, no `invalid_param` |
| `GET /v0/markets?foo=bar`, `?page=2` | 200 | unknown params silently ignored |

No sorting or pagination parameter appears in the market-data documentation.

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK `@somnia-chain/markets-sdk` **0.32.1**. Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `urllib`. Captured 2026-10-20 07:05-07:40 UTC (10:05-10:40 MSK).

## Why it matters

Clients that watch the market list compare arrays between polls: "is there a new market?", "did my watchlist
change?". With an unstable order, every rotation looks like a set of changes — a monitor fires on
`WETH, SOMI, WBTC` arriving after `SOMI, WBTC, WETH` even though the set is identical, and a naive diff keyed
by index produces delete+create pairs. A UI with a stable key will just reorder its rows under the user.

The `offset` half is a silent trap for the opposite reason: a developer who assumes standard pagination
(`offset`/`limit`) gets the whole list back on every "page" and de-duplicates nothing, while `limit` is
separately ignored on the same endpoints (see the dedicated `limit` report). Neither parameter ever fails,
so the mistake never surfaces in a test.
