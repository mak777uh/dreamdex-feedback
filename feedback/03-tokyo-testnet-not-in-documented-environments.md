# The perps testnet the bounty runs on ("Tokyo") is not in the documented environments

Severity: major
Area: docs

## Steps to reproduce

1. Open the bounty page and note the network the programme targets:
   "The Perps Builder Bounty is a developer program for dreamDEX perps on **Somnia Tokyo testnet**."
   The MVP track requires that "Your MVP places real perps orders on **Somnia Tokyo testnet**."
2. Open `https://app.testnet.dreamdex.io` and look at the trade route the app itself uses:
   `/trade/perp/tokyo/<SYMBOL>` (e.g. `/trade/perp/tokyo/SOMI:USDso`).
3. Read the docs' environment table on
   `https://app.dreamdex.io/docs/developers/http-api` and search the docs for "tokyo".

## Expected

The environment table should list the network the bounty and the app use, with its chain ID, REST base
URL and WebSocket URL — the same three columns it provides for the other two environments.

## Actual

The table has exactly two rows:

| Environment | Chain ID | REST base URL | WebSocket public feed |
|---|---|---|---|
| Mainnet (Somnia) | 5031 | `https://api.dreamdex.io/v0` | `wss://api.dreamdex.io/v0/ws/public` |
| Testnet (Somnia **Shannon**) | 50312 | `https://stg.api.dreamdex.io/v0` | `wss://stg.api.dreamdex.io/v0/ws/public` |

"Tokyo" is absent. In the eight documentation pages checked (HTTP API overview, authentication, market
data, trading, error handling, Perps orders, Perps funding, Libraries) the string **"tokyo" does not
occur at all** — zero matches, case-insensitive, including page source.

The documented testnet ("Shannon", `stg.api.dreamdex.io`) answers
`GET /v0/markets?kind=perp` with `{"markets":[]}`, so it does not expose the perps markets the bounty
asks builders to trade. The environment that does serve them is only reachable through the app route
name `/trade/perp/tokyo/...`.

## Evidence

- Bounty text: "perps on Somnia Tokyo testnet" (DoraHacks page, captured 2026-10-19).
- App route: `https://app.testnet.dreamdex.io/trade/perp/tokyo/SOMI:USDso` returns `200`.
- Docs table row set (verbatim from `/docs/developers/http-api`): "Mainnet (Somnia) 5031
  https://api.dreamdex.io/v0 … Testnet (Somnia Shannon) 50312 https://stg.api.dreamdex.io/v0 …".
- `grep -i tokyo` over the eight saved docs pages: 0 matches.
- `GET https://stg.api.dreamdex.io/v0/markets?kind=perp` → `200 {"markets":[]}` (2026-10-20 00:02 MSK).

## Environment

Docs: `https://app.dreamdex.io/docs/*`. App: `https://app.testnet.dreamdex.io`. Chain IDs per the docs'
own table: 5031 (mainnet), 50312 (Shannon testnet).

## Why it matters

A builder following the bounty description looks for "Somnia Tokyo testnet" in the docs, does not find
it, and the only documented testnet has no perps markets. The practical result is that the first
onboarding step — point an SDK at the right chain and list the perps markets — cannot be completed from
public documentation. Either the table should gain a Tokyo row (chain ID, REST and WS base URLs), or the
bounty text should name the environment the docs actually describe.
