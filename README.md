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

## Reports — 11 files (5 major, 6 normal), ordered by expected acceptance value

| # | Area | Severity | Title |
|---|---|---|---|
| 01 | SDK | **major** | SDK `fetchOrderbooks()` sends comma-joined symbols → every multi-symbol call fails with 400 |
| 02 | API | **major** | Perp markets are not exposed by the documented market list: `kind` undocumented, `kind=perp` empty everywhere |
| 03 | API | **major** | WebSocket REST-bridge: `getOrderbooks` always fails with `invalid_request` |
| 04 | docs | **major** | Docs: unknown symbols are not "silently skipped" — the API returns 400 `invalid_param` |
| 05 | docs | **major** | The perps testnet the bounty runs on (Hideki / "Tokyo") is missing from the documented environments |
| 06 | docs | normal | "All error responses use a consistent JSON format" is false for 404 and 405 |
| 07 | API | normal | WS `subscription_failed` does not say which symbol was rejected |
| 08 | API | normal | Indexer: `perpStatus` / `perpRestricted` null for every registered perp market |
| 09 | docs | normal | `depth` is capped at 1000, but the maximum is not documented |
| 10 | docs | normal | The 100-request rate limit is visible only in response headers |
| 11 | docs | normal | Stop-order hold is "0.15 STT" in the app docs and "0.15 SOMI" in the bot kit |

## Environment used

- REST testnet: `https://stg.api.dreamdex.io/v0` — Somnia Shannon, chain **50312**
- REST mainnet: `https://api.dreamdex.io/v0` — chain **5031**
- Perps testnet: **Hideki, chain 50383** (`eth_chainId` → `0xc4cf`)
- WebSocket: `wss://stg.api.dreamdex.io/v0/ws/public`
- Indexer: `https://hideki-dev.smk.somnia.host/v1/graphql`
- SDK: `@somnia-chain/markets-sdk` **0.32.1** (`somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`)
- Public endpoints only — no wallet, no API key, no transactions

## Notes

- Every `## Steps to reproduce` block contains the exact command, and `## Evidence` quotes the responses
  captured at the time of writing (2026-10-19 23:50 – 2026-10-20 01:40 MSK).
- Nothing here was inferred from reading code alone: items 01–10 were executed against the live testnet
  (item 11 compares two published texts).
- **Security issues are deliberately not in this repository** — per the bounty rules they go to
  `security@dreamdex.io`. No exploitable vulnerability was identified while preparing these reports.
