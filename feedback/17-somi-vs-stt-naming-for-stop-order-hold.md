# Stop-order hold is "0.15 STT" in the app docs and "0.15 SOMI" in the bot kit

Severity: normal
Area: docs

## Steps to reproduce

1. Perps Orders documentation page (`/docs/trading/perps-testnet/orders`) — the TP/SL section says:

> "TP and SL hold a little **STT** … Each pending TP or SL holds **0.15 STT** from your wallet."

2. Bot kit for the same product (`somnia-chain/dreamdex-bot-kit`) uses the name **SOMI** for the same
   constant: `packages/perp-core/src/stops.ts`, line 15 — *"Every pending stop locks SOMI (0.15 on the
   live markets …)"*, and the helper is literally named `somiPerStop` (line 146).
3. The same bot kit contradicts itself: its own `docs/perps.md`, line 73 — *"each one locks a small **STT**
   deposit until it fires or is cancelled"*.


## Expected

One name for the native gas coin used on the perps testnet.

## Actual

The native coin is **STT** on the testnets and **SOMI** on mainnet. On the perps testnet (Hideki, 50383)
the docs' "STT" is correct, while the bot kit's "SOMI" names the mainnet coin. A builder budgeting the
hold reads two different assets for the same 0.15 constant, and "SOMI" leads them to the wrong token
when they top up.

## Evidence

- App docs, verbatim: "TP and SL hold a little STT … Each pending TP or SL holds 0.15 STT from your wallet."
- Bot kit naming: `somiPerStop` / "0.15 SOMI" (source: `somnia-chain/dreamdex-bot-kit`)
- Chain facts: Hideki testnet gas coin is STT (chain 50383); SOMI is native on mainnet (5031)

## Environment

REST testnet base `https://stg.api.dreamdex.io/v0` (Somnia Shannon, chain **50312**); REST mainnet `https://api.dreamdex.io/v0` (chain **5031**); perps testnet **Hideki chain 50383** (`eth_chainId` → `0xc4cf`). SDK: `@somnia-chain/markets-sdk` **0.32.1** (repo `somnia-chain/dreamdex-bot-kit`, `packages/core/src/rest.ts`). Public endpoints only — no wallet, no API key. Client: `curl 8.x` / Python `websockets`. Captured 2026-10-19 23:50 – 2026-10-20 01:40 MSK.

_Note: the naming comparison was first identified by a teammate (cardano-agent) from the docs and bot-kit
sources; the app-docs quote above is reproduced here verbatim._
