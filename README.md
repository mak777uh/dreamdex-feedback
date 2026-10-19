# dreamDEX Perps Builder Bounty — feedback

Reproducible reports against the dreamDEX perps testnet (Somnia Tokyo) HTTP API and documentation,
prepared for the **dreamDEX Perps Builder Bounty — Feedback track**.

Each report lives in `feedback/` as its own Markdown file, following the bounty's required template:

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

## Environment used

- REST testnet base: `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain 50312, per docs)
- REST mainnet base: `https://api.dreamdex.io/v0` (Somnia, chain 5031)
- App: `https://app.testnet.dreamdex.io`
- Auth: public endpoints only — no wallet, no API key
- Client: `curl 8.x`

## Reports

| # | Area | Severity | Title |
|---|---|---|---|
| 01 | docs | major | Unknown market symbols return HTTP 400, not an empty list as documented |
| 02 | API | major | Perpetual markets are unreachable: `kind` is undocumented and `kind=perp` is empty everywhere |
| 03 | docs | major | The perps testnet the bounty runs on ("Tokyo") is not in the documented environments |

## Reproducing

Every report is self-contained: the `## Steps to reproduce` section contains the exact `curl` calls,
and `## Evidence` quotes the response bodies captured at the time of writing. Nothing in this repo was
generated from imagination — each item was executed against the live testnet.

Security issues are deliberately **not** in this repository; per the bounty rules they go to
`security@dreamdex.io`.
