# Unknown market symbols return HTTP 400, not an empty list as documented

Severity: major
Area: docs

## Steps to reproduce

1. Call the testnet order books endpoint with a symbol that does not exist (and, separately, with the
   comma-joined form that the docs use as the "wrong" example):

```bash
curl -sS -i 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=NOPE:USDso'
curl -sS -i 'https://stg.api.dreamdex.io/v0/orderbooks?symbols=SOMI:USDso,WETH:USDso'
```

2. Call the tickers endpoint the same way:

```bash
curl -sS -i 'https://stg.api.dreamdex.io/v0/tickers?symbols=NOPE:USDso'
```

## Expected

The Market Data page states, in the array-serialisation warning:

> "Unknown or malformed symbols are **silently skipped** rather than erroring, so a serialization
> mismatch shows up as an **empty `[]`** rather than a 4xx."

So both requests are expected to return `200` with an empty result for the unknown symbol
(`{"orderbooks":[]}` / `{"symbols":[]}`), and the documented comma-joined mistake should yield `[]`.

## Actual

Both requests return **HTTP 400** with `invalid_param`:

```json
{"context":{"invalid_symbols":["NOPE:USDso"]},"description":"unknown market symbols: NOPE:USDso","name":"invalid_param","status":400}
```

The exact example the docs call "silently skipped … response is []" returns 400 as well:

```json
{"context":{"invalid_symbols":["SOMI:USDso,WETH:USDso"]},"description":"unknown market symbols: SOMI:USDso,WETH:USDso","name":"invalid_param","status":400}
```

The repeated-key form does work (`?symbols=SOMI:USDso&symbols=WETH:USDso` → 200), so the failure is not
in the endpoint itself but in the documented contract.

## Evidence

Raw responses captured 2026-10-19 23:58 MSK:

- `GET https://stg.api.dreamdex.io/v0/orderbooks?symbols=NOPE:USDso` → `400`
  `{"context":{"invalid_symbols":["NOPE:USDso"]},"description":"unknown market symbols: NOPE:USDso",…}`
- `GET https://stg.api.dreamdex.io/v0/orderbooks?symbols=SOMI:USDso,WETH:USDso` → `400`
  `{"context":{"invalid_symbols":["SOMI:USDso,WETH:USDso"]},…}`
- `GET https://stg.api.dreamdex.io/v0/tickers?symbols=NOPE:USDso` → `400`, same shape
- Control: `GET …/orderbooks?symbols=SOMI:USDso&symbols=WETH:USDso` → `200` with both books

## Environment

REST base `https://stg.api.dreamdex.io/v0` (Somnia Shannon testnet, chain 50312). No auth required.
`curl 8.x`, no SDK.

## Why it matters

An integration written to the documented behaviour will treat a serialisation mistake as "no data"
and silently continue (the docs explicitly tell developers to expect `[]`), while the API now throws
`400`. Error handling built from the docs is therefore wrong in the most common failure mode — a typo
or a repeated-key mismatch in the `symbols` parameter — and bots can stall or skip markets instead of
surfacing the configuration error.
