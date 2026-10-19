# Indexer mark prices are 8–33 minutes stale, while the docs describe the market figures as "live"

Severity: normal
Area: docs

## Steps to reproduce

1. Read `markPriceUpdatedAt` and `lastPrice` for every registered perp market:

```bash
curl -sS -X POST -H 'Content-Type: application/json' \
  --data '{"query":"{ Market(where: {perpRegistered: {_eq: true}}, limit: 30) { id markPrice markPriceUpdatedAt indexPrice lastPrice } }"}' \
  https://hideki-dev.smk.somnia.host/v1/graphql
```

2. In the same moment, read the platform's other feed:

```bash
curl -sS 'https://stg.api.dreamdex.io/v0/tickers'
```

3. Repeat both after 6–7 minutes and compare `markPriceUpdatedAt` with wall-clock time.

## Expected

`markPriceUpdatedAt` should be close to now for an actively traded market, or the documentation should
state the refresh cadence of the mark price, so a consumer knows how stale a trigger or liquidation
estimate can be.

## Actual

Measured 2026-10-19, window **22:20:41 → 22:27:28 UTC (407 s)**, 21 perp markets:

| Metric | Value |
|---|---|
| markets whose `markPriceUpdatedAt` advanced during 6.8 min | **0 of 21** |
| lag at 22:27:28 — worst | **1995 s (33.2 min)** |
| lag at 22:27:28 — median | **767 s (12.8 min)** |
| lag at 22:27:28 — freshest | **491 s (8.2 min)** |
| spot REST `/v0/tickers` timestamp at the same instant | **1.1 s behind now** |

So every perp market's mark price was at least ~8 minutes old, the worst was 33 minutes old, and none
was recomputed during the observation window — while the spot feed on the same venue was fresh to within
a second.

The perps overview page says of its market table: "These figures are read from the **live markets** and
can be retuned at any time." Nothing in the docs states how often `markPrice` is recomputed, and the
SDK's health/risk helpers (`getPerpHealthSnapshot`, `getMaxPerpOrderSize`) read exactly this value.

## Evidence

Captured 2026-10-20 (UTC), raw snapshots kept in the same series as below:

```
22:16:27Z  worst lag ~59 min   freshest ~96 s
22:20:41Z  worst 26 min        median ~6 min
22:27:28Z  worst 1995 s (33.2 min)   median 767 s   freshest 491 s
21 markets: markPriceUpdatedAt advanced during 407 s window → 0
spot /v0/tickers timestamp lag at 22:27:28Z → -1.1 s
```

Example rows at 22:27:28Z:

```json
{"id":"0xb483ec1fb34996638677c20ab087b16f1896fa53","markPrice":"104475473684242500000","markPriceUpdatedAt":"1792446854","lastPrice":"105100000000000000000"}
```

(`markPriceUpdatedAt` is a **string of Unix seconds** — another detail the docs do not state; a client
that treats it as milliseconds reads the value as 1970.)

## Environment

Indexer `https://hideki-dev.smk.somnia.host/v1/graphql` (Hideki, chain **50383**); REST
`https://stg.api.dreamdex.io/v0` (Shannon, chain 50312); SDK `@somnia-chain/markets-sdk` **0.32.1**.
No wallet, no auth. Client: `curl 8.x`.

## Why it matters

A perps bot uses the mark price for TP/SL triggers, liquidation distance and sizing. The data carries its
own timestamp, so the staleness is detectable — but nothing in the docs tells a builder what cadence to
expect, and the "live markets" wording invites the assumption that a mark is seconds old. A 30-minute-old
mark on a volatile market is the difference between a stop that fires and one that does not.
