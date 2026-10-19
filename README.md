# dreamDEX Perps Builder Bounty — feedback

Reproducible reports against the dreamDEX perps testnet, prepared for the **dreamDEX Perps Builder
Bounty — Feedback track** ($40 per accepted critical/major, $15 per other accepted item; budget $1 500).

One issue per file, following the bounty's required template:

```markdown
# Short title
Severity: critical | major | normal
Area: API | SDK | docs | app | contracts

## Steps to reproduce
## Expected
## Actual
## Evidence
## Environment
```

## Reports — 18 files (8 major, 10 normal), ordered by expected acceptance value

### Major (01–08) — SDK/API behaviour first

| # | Area | Title |
|---|---|---|
| 01 | SDK | `fetchOrderbooks()` sends comma-joined symbols → every multi-symbol call fails with 400 |
| 02 | API | Perp markets are not exposed by the documented market list: `kind` undocumented, `kind=perp` empty everywhere |
| 03 | API | WebSocket REST-bridge: `getOrderbooks` always fails with `invalid_request` |
| 04 | API | `HEAD` returns 400 on every GET endpoint, although the server advertises `Allow: GET, HEAD` |
| 05 | API | `limit` is validated on `/trades` and `/candles` but silently ignored on `/tickers` and `/orderbooks` |
| 06 | SDK | `buildPlacePerpOrder` returns a signable transaction with `to: undefined` and accepts invalid enums and sizes |
| 07 | docs | Unknown symbols are not "silently skipped" — the API returns 400 `invalid_param` |
| 08 | docs | The perps testnet the bounty runs on (Hideki / "Tokyo") is missing from the documented environments |

### Normal (09–18) — docs and edge semantics

| # | Area | Title |
|---|---|---|
| 09 | docs | "All error responses use a consistent JSON format" is false for 404, 405, OPTIONS and 411 |
| 10 | API | WS `subscription_failed` does not say which symbol was rejected |
| 11 | API | Indexer: `perpStatus` / `perpRestricted` null for every registered perp market |
| 12 | docs | Indexer mark prices are 8–33 minutes stale, while the docs describe the figures as "live" |
| 13 | docs | `depth` is capped at 1000, but the maximum is not documented |
| 14 | docs | The 100-request rate limit is visible only in response headers |
| 15 | API | A duplicated symbol in repeated-key `symbols` returns 400 `duplicate items found` (schema dump) |
| 16 | API | Protected endpoints answer 401 without a `WWW-Authenticate` header |
| 17 | docs | Stop-order hold is "0.15 STT" in the app docs and "0.15 SOMI" in the bot kit |
| 18 | SDK | Reduce-only is documented for perp orders, but a plain limit/market reduce-only order is not expressible through the SDK |

## Environment used

- REST testnet: `https://stg.api.dreamdex.io/v0` — Somnia Shannon, chain **50312**
- REST mainnet: `https://api.dreamdex.io/v0` — chain **5031**
- Perps testnet: **Hideki, chain 50383** (`eth_chainId` → `0xc4cf`)
- WebSocket: `wss://stg.api.dreamdex.io/v0/ws/public`
- Indexer: `https://hideki-dev.smk.somnia.host/v1/graphql`
- SDK: `@somnia-chain/markets-sdk` **0.32.1** (`somnia-chain/dreamdex-bot-kit`), Node **24.14.1**
- Public endpoints only — no wallet, no API key, no transactions

## Notes

- Every `## Steps to reproduce` block contains the exact command or script; `## Evidence` quotes the
  responses/output captured at the time of writing (2026-10-19 22:50 – 2026-10-20 02:15 MSK).
- Items 01–17 were executed against the live endpoints or against the published SDK sources; item 18 is
  a type/ABI inspection confirmed by building a call with SDK 0.32.1 (no wallet, nothing sent).
- **Security issues are deliberately not in this repository** — per the bounty rules they go to
  `security@dreamdex.io`. No exploitable vulnerability was identified while preparing these reports.
- Duplicates were merged, not filed twice: the 404/405 item also carries the `OPTIONS` behaviour, and the
  comma-symbols bug is filed once (SDK) rather than again as an API bug.
