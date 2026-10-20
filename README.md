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

## If you read only five

| # | Why it is first |
|---|---|
| [01](feedback/01-sdk-fetchorderbooks-joins-symbols-with-comma.md) | `fetchOrderbooks()` breaks every multi-symbol call in the shipped SDK — one line of code, 400 on every use |
| [06](feedback/06-sdk-buildplaceperporder-undefined-to-no-validation.md) | `buildPlacePerpOrder()` returns a signable transaction with `to: undefined` — money-moving path, no validation |
| [04](feedback/04-head-returns-400-although-head-is-allowed.md) | `HEAD` 400s on every endpoint while the server advertises `Allow: GET, HEAD` — every uptime monitor marks the API down |
| [05](feedback/05-limit-silently-ignored-on-tickers-and-orderbooks.md) | `limit` is validated on two endpoints and silently ignored on two others — same parameter, same API |
| [03](feedback/03-ws-rest-bridge-getorderbooks-invalid-request.md) | The WS REST-bridge `getOrderbooks` fails with `invalid_request` every time — the operation is unusable |

## Reports — 22 files (8 major, 14 normal)

### Major (01–08) — SDK/API behaviour first

| # | Area | Title |
|---|---|---|
| 01 | SDK | `fetchOrderbooks()` sends comma-joined symbols → every multi-symbol call fails with 400 |
| 02 | API | Perp markets are not exposed by the documented market list: `kind` undocumented, `kind=perp` empty everywhere |
| 03 | API | WebSocket REST-bridge: `getOrderbooks` always fails with `invalid_request` |
| 04 | API | `HEAD` returns 400 on every GET endpoint, although the server advertises `Allow: GET, HEAD` |
| 05 | API | `limit` is validated on `/trades` and `/candles` but silently ignored on `/tickers` and `/orderbooks` |
| 06 | SDK | `buildPlacePerpOrder` returns a signable transaction with `to: undefined` and accepts invalid enums and sizes |
| 07 | docs | Unknown symbols are not "silently skipped" — 400 `invalid_param` in a query, `404 market_not_found` in a path |
| 08 | docs | The perps testnet the bounty runs on (Hideki / "Tokyo") is missing from the documented environments |

### Normal (09–22) — docs and edge semantics

| # | Area | Title |
|---|---|---|
| 09 | docs | "All error responses use a consistent JSON format" is false for 404, 405, OPTIONS, 411 and a trailing slash |
| 10 | API | WS `subscription_failed` does not say which symbol was rejected — and the two docs pages disagree on its schema |
| 11 | API | Indexer: `perpStatus` / `perpRestricted` null for every registered perp market |
| 12 | docs | Indexer mark prices are 8–33 minutes stale, while the docs describe the figures as "live" |
| 13 | docs | `depth` is capped at 1000, but the maximum is not documented |
| 14 | docs | The 100-request rate limit is visible only in response headers |
| 15 | API | A duplicated symbol in repeated-key `symbols` returns 400 with an internal schema dump; `maxItems: 16` undocumented |
| 16 | API | Protected endpoints answer 401 without a `WWW-Authenticate` header |
| 17 | docs | Stop-order hold is "0.15 STT" in the app docs and "0.15 SOMI" in the bot kit |
| 18 | SDK | Reduce-only is documented for perp orders, but a plain limit/market reduce-only order is not expressible through the SDK |
| 19 | API | Public market metadata has no cache validators, and conditional requests are ignored |
| 20 | API | Collection responses come back in a different order each time; `offset` is accepted but never paginates |
| 21 | API | Auth and parameter validation run in a different order on REST and on WebSocket |
| 22 | docs | Error contracts do not match the wire: `context` undocumented on REST, WS bridge frames match neither documented shape |

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
  responses/output captured at the time of writing (2026-10-19 22:50 – 2026-10-20 07:40 UTC).
- Items 01–17 were executed against the live endpoints or against the published SDK sources; item 18 is
  a type/ABI inspection confirmed by building a call with SDK 0.32.1 (no wallet, nothing sent).
- Items 19–22 were added on 2026-10-20 and re-run three times each; 19–21 report wire behaviour, 22 compares
  the wire format with the published error pages (`/docs/developers/http-api/error-handling`,
  `/docs/developers/websocket-api/errors`, `/docs/developers/websocket-api/real-time-feed`).
- **Security issues are deliberately not in this repository** — per the bounty rules they go to
  `security@dreamdex.io`. No exploitable vulnerability was identified while preparing these reports.
- Duplicates were merged, not filed twice. Each of these files carries a second, related observation rather
  than a separate report: 04 also shows `TRACE → 405 Allow: GET, HEAD`; 07 also covers wrong-case and padded
  symbols and the 400-vs-404 split; 09 also covers the trailing-slash 404; 10 also covers the contradicting
  WS error schema; 15 also covers the empty-`symbols` case and the echoed value. The comma-symbols bug is
  filed once (SDK) rather than again as an API bug.
