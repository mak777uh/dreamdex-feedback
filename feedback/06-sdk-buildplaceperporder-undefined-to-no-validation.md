# `buildPlacePerpOrder` returns a signable transaction with `to: undefined` and accepts invalid enums and sizes

Severity: major
Area: SDK

## Steps to reproduce

Minimal Node script — no wallet, no RPC, nothing sent. `@somnia-chain/markets-sdk@0.32.1`:

```bash
mkdir ddx-sdk && cd ddx-sdk && npm init -y
npm install @somnia-chain/markets-sdk@0.32.1 --ignore-scripts
```

```js
// test.mjs
import { buildPlacePerpOrder } from './node_modules/@somnia-chain/markets-sdk/dist/orders.js'

const w = { chain: { id: 50383 }, defaultGas: 10_000_000n }   // no signer, no provider
const POOL = '0xf71b619450bafe953f47b9b556416a3a67b443b5'
const base = { pool: POOL, isBid: true, price: 19_000_000_000_000_000_000n, quantity: 1_000_000_000_000_000_000n }

for (const [name, params] of [
  ['valid', base],
  ['off_tick_price (price=1)', { ...base, price: 1n }],
  ['below_min_qty (qty=1)', { ...base, quantity: 1n }],
  ['order_type_99', { ...base, orderType: 99 }],
  ['self_match_99', { ...base, selfMatchingOption: 99 }],
  ['builder_fee_no_builder', { ...base, builderFeeBpsTimes1k: 1000n }],
  ['missing_pool', { ...base, pool: undefined }],
]) {
  try {
    const { order } = await buildPlacePerpOrder(w, params)
    console.log(`${name.padEnd(26)} OK    to=${String(order?.to)}`)
  } catch (e) {
    console.log(`${name.padEnd(26)} ERR   ${e.constructor?.name}: ${String(e.message).slice(0, 60)}`)
  }
}
```

## Expected

The build-only verb exists so a caller can "pre-sign, batch, relay, or simulate" the call before
sending it. Before handing back a signable transaction it should reject what the contract will reject —
or at least what makes the transaction unusable:

- a missing `pool` (the transaction would have no recipient),
- `orderType` outside the documented enum 0..3 and `selfMatchingOption` outside 0..1,
- `builderFeeBpsTimes1k != 0` while `builder == address(0)` (the contract's own rule),
- a price that is not a multiple of `tickSize`, and a quantity below `minQuantity` or not a multiple of
  `lotSize` — the docs state all of these as contract requirements.

## Actual

The only validation in `perpOrderCall` (`dist/orders.js:1611-1613`) is:

```js
if (p.price <= 0n || p.quantity <= 0n) {
    throw new InvalidInputError("price and quantity must be > 0");
}
```

Everything else passes straight into the calldata. Output of the script above, verbatim:

```
valid                      OK    to=0xf71b619450…   gas=undefined
zero_price                 ERR   InvalidInputError: price and quantity must be > 0
zero_qty                   ERR   InvalidInputError: price and quantity must be > 0
off_tick_price (price=1)   OK    to=0xf71b619450…   gas=undefined
below_min_qty (qty=1)      OK    to=0xf71b619450…   gas=undefined
order_type_99              OK    to=0xf71b619450…   gas=undefined
self_match_99              OK    to=0xf71b619450…   gas=undefined
builder_fee_no_builder     OK    to=0xf71b619450…   gas=undefined
missing_pool               OK    to=undefined       gas=undefined
missing_pool -> order.to === undefined : true
```

So the SDK returns a **signable transaction with `to: undefined`** and accepts invalid enum values and
sizes without an error. A builder following the documented build → sign → relay flow discovers the
mistake only when the transaction is broadcast — i.e. after paying gas for a transaction that cannot
succeed.

The calldata also confirms the arguments are positional with `userData` hardcoded to `0n`
(`dist/orders.js:1622`):

```
0x4e978373
  000…001              isBid = true
  000…000              userData = 0n   (hardcoded, no way to set a flag)
  000…0107ad8f556c6c   price
  000…0de0b6b3a7640000 quantity
  …
```

## Evidence

- SDK `@somnia-chain/markets-sdk@0.32.1`, `dist/orders.js:1610-1633` (`perpOrderCall`) and
  `dist/orders.js:1683-1689` (`buildPlacePerpOrder`): the call object is
  `{ address: p.pool, abi, functionName: "placeOrder", args: [...], gas }` — `address` is whatever
  `p.pool` is, including `undefined`.
- Script output above (2026-10-20 02:05 UTC), Node v24.14.1, no signer and no network calls.
- Contract requirements being skipped are documented in `/docs/developers/contracts/types`
  (`price` "must be a multiple of tickSize"; `quantity` "must be >= minQuantity and a multiple of
  lotSize"; `builderFeeBpsTimes1k` "Must be 0 when builder is address(0)") and `OrderType` 0..3,
  `SelfMatchingOption` 0..1.

## Environment

`@somnia-chain/markets-sdk` **0.32.1** (npm), Node **24.14.1**, perp pool
`0xf71b619450bafe953f47b9b556416a3a67b443b5` (Hideki, chain 50383). No wallet, no key, no transactions.

## Why it matters

`buildPlacePerpOrder` is the SDK path for anyone who pre-signs, batches, relays or simulates perp orders
— exactly the "builder" audience of this programme. Because validation is deferred to the chain, every
malformed order costs gas and shows up as an opaque revert instead of a client-side error. The
`to: undefined` case is worse: the returned transaction cannot be sent at all, yet nothing in the API
signals it.
