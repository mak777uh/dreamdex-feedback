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

## Reports — 22 submitted (8 major, 14 normal)

`feedback/` contains exactly the 22 submitted files. The one closed item (08) lives in `feedback/_closed/`
with a `Status: no longer reproduces as of 2026-10-20` line and is not part of the submission. Item 23 was
added during the 2026-10-20 re-verification.

| Area | Major | Normal | Total |
|---|---|---|---|
| API — REST `/v0`, WebSocket bridge, indexer | 5 | 7 | 12 |
| SDK (`@somnia-chain/markets-sdk` 0.32.1) | 2 | 1 | 3 |
| Docs | 1 | 6 | 7 |
| **Total** | **8** | **14** | **22** |

Every item was re-checked on 2026-10-20 against three hosts — `stg.api.dreamdex.io`, `api.testnet.dreamdex.io`,
`api.dreamdex.io` — plus SDK `@somnia-chain/markets-sdk` 0.32.1, the public WebSocket and the Hideki indexer.
Where a behaviour depends on the host, the report names the host instead of claiming it on "both networks".
Result of that pass: 13 items reproduce as written, 8 reproduce but are host-specific (01, 03, 04, 09, 13, 14,
20, 21), one is closed (08), and one is new (23).

### Major (01–07, 23) — SDK/API behaviour first

| # | Area | Title |
|---|---|---|
| 01 | SDK | SDK `fetchOrderbooks()` sends comma-joined symbols, but the API requires repeated keys — every multi-symbol call fails with 400 |
| 02 | API | Perp markets are missing from every documented REST host; the only host that serves them is undocumented |
| 03 | API | WebSocket REST-bridge: `getOrderbooks` always fails with `invalid_request` |
| 04 | API | HEAD returns 400 on every GET endpoint, although the server itself advertises `Allow: GET, HEAD` |
| 05 | API | `limit` is validated on `/trades` and `/candles` but silently ignored on `/tickers` and `/orderbooks` |
| 06 | SDK | `buildPlacePerpOrder` returns a signable transaction with `to: undefined` and accepts invalid enums and sizes |
| 07 | docs | Docs: unknown market symbols are not "silently skipped" — and the same bad symbol is a 400 in a query but a 404 in a path |
| 23 | API | An undocumented REST host serves the perp market list, and its behaviour drifts from the documented hosts |

### Closed (not submitted)

| # | Area | Title |
|---|---|---|
| [08](feedback/_closed/08-hideki-tokyo-perps-testnet-not-in-documented-environments.md) | docs | The perps testnet (Hideki) was missing from the documented environments — **no longer reproduces as of 2026-10-20**, the docs now list Hideki, chain 50383, RPC, WS and indexer |

### Normal (09–22) — docs and edge semantics

| # | Area | Title |
|---|---|---|
| 09 | docs | Docs: "all error responses use a consistent JSON format" is false for 404 and 405 |
| 10 | API | WebSocket `subscription_failed` does not say which symbol was rejected |
| 11 | API | Indexer: `perpStatus`, `perpRestricted` and `perpStatusUpdatedAt` are null for every registered perp market |
| 12 | docs | Indexer mark prices are 8–33 minutes stale, while the docs describe the market figures as "live" |
| 13 | docs | `depth` above 1000 is rejected, but the maximum is not documented |
| 14 | docs | The request rate limit is visible only in response headers and differs by host (100 vs 200), never in the docs |
| 15 | API | A duplicated symbol in repeated-key `symbols` returns 400 `duplicate items found` (with an OpenAPI schema dump) |
| 16 | API | Protected endpoints answer 401 without a `WWW-Authenticate` header |
| 17 | docs | Stop-order hold is "0.15 STT" in the app docs and "0.15 SOMI" in the bot kit |
| 18 | SDK | Reduce-only is documented for perp orders, but a plain limit/market reduce-only order is not expressible through the SDK |
| 19 | API | Public market metadata is served without cache validators, and conditional requests are ignored |
| 20 | API | Collection responses come back in a different order each time, and `offset` is accepted but never paginates |
| 21 | API | Authentication and parameter validation run in a different order on REST and on WebSocket |
| 22 | docs | Documented error contracts do not match the wire: `context` is undocumented on REST, and WS bridge frames match neither documented WS shape |

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
