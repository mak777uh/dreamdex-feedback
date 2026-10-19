# Perpetual markets are unreachable through the documented market list: `kind` is undocumented and `kind=perp` is empty everywhere

Severity: major
Area: API

## Steps to reproduce

1. Follow the Market Data docs and list markets:

```bash
curl -sS 'https://stg.api.dreamdex.io/v0/markets'
```

2. Now ask for perpetual markets explicitly, on testnet and mainnet:

```bash
curl -sS 'https://stg.api.dreamdex.io/v0/markets?kind=perp'
curl -sS 'https://api.dreamdex.io/v0/markets?kind=perp'
curl -sS 'https://api.dreamdex.io/v0/markets?kind=all'
```

3. Try the misspelled value to see the schema the API itself publishes:

```bash
curl -sS 'https://stg.api.dreamdex.io/v0/markets?kind=perps'
```

## Expected

The bounty is a **perps** builder programme, so a builder should be able to enumerate the perpetual
markets from the public API — or at minimum read in the docs how perps markets are exposed.

## Actual

- `GET /v0/markets` returns **three spot markets only** (testnet); every item has `"kind": "spot"`.
  On mainnet it returns four spot markets, also `"kind": "spot"` and nothing else.
- `GET /v0/markets?kind=perp` → `200 {"markets":[]}` **on both testnet and mainnet**.
- `GET /v0/markets?kind=all` returns the same spot-only set as the default call.
- `GET /v0/markets?kind=perps` → `400 invalid_param`, and the error body embeds the parameter schema:

```json
{"description":"parameter \"kind\" in query has an error: value is not one of the allowed values [\"spot\",\"perp\",\"all\"] …","name":"invalid_param","status":400}
```

So the API advertises `perp` as a valid value, documents `"description": "Market class to filter an
enumerating endpoint by. Defaults to `spot`…"`, and then returns an empty array for it everywhere.

- The **Market Data documentation page does not mention `kind` at all** (zero occurrences). A reader
  following the docs sees `GET /v0/markets` and has no way to know that (a) the list is filtered to
  spot by default and (b) a `kind` parameter exists.

## Evidence

Captured 2026-10-20 00:02 MSK:

- `stg …/v0/markets` → `200`, 3 items, `kind: "spot"` (`SOMI:USDso`, `WBTC:USDso`, `WETH:USDso`)
- `api …/v0/markets` → `200`, 4 items, all `kind: "spot"`
- `stg …/v0/markets?kind=perp` → `200 {"markets":[]}`
- `api …/v0/markets?kind=perp` → `200 {"markets":[]}`
- `stg …/v0/markets?kind=perps` → `400`, body contains the full `kind` schema with enum
  `["spot","perp","all"]` and `"default": "spot"`

## Environment

REST base `https://stg.api.dreamdex.io/v0` (Shannon testnet, chain 50312) and
`https://api.dreamdex.io/v0` (Somnia mainnet, chain 5031). No auth. `curl 8.x`.

## Why it matters

For a perps-focused builder programme this is the first thing a developer tries: list the markets they
are supposed to trade. The documented call returns spot only, the parameter that would change that is
undocumented, and even when discovered it returns nothing. A bot cannot discover perps markets,
tick sizes or lot sizes through the public API at all, which blocks the "build a perps bot" track
before any order is placed.
