# Reduce-only is documented for perp orders, but a plain limit/market reduce-only order is not expressible through the SDK

Severity: normal
Area: SDK

## Steps to reproduce

1. Read the documented capability (`/docs/trading/perps-testnet/orders`, section "Order types"):

> "**Reduce-only** orders can only shrink a position, never open or flip one."

2. Inspect the public parameter type for a plain perp order (`dist/trade.d.ts`,
   `interface PlacePerpOrderParams`):

```ts
export interface PlacePerpOrderParams {
    pool: Address;
    isBid: boolean;
    price: bigint;
    quantity: bigint;
    expireTimestampNs?: bigint;
    orderType?: number;
    selfMatchingOption?: number;
    builder?: Address;
    builderFeeBpsTimes1k?: bigint;
    gas?: bigint;
}
```

3. Inspect the call the SDK builds (`dist/orders.js:1620-1630`) — the contract arguments are positional
   and the second one is hardcoded:

```js
args: [
    p.isBid,
    0n,                      // ← userData, hardcoded; no flag can be passed through it
    p.price,
    p.quantity,
    p.expireTimestampNs ?? Writer.farFutureNs(),
    p.orderType ?? 0,
    p.selfMatchingOption ?? 0,
    p.builder ?? Writer.ZERO_ADDRESS,
    p.builderFeeBpsTimes1k ?? 0n,
],
```

4. Search the package for `reduceOnly`:

```bash
grep -rn "reduceOnly" node_modules/@somnia-chain/markets-sdk/dist/*.d.ts
# dist/trade.d.ts:1393: export type PerpStopIntent = "reduceOnly" | "opening";
```

## Expected

Caveat added during re-verification (2026-10-20): the SDK does expose `reduceOrder`, `reduceOrders` and
`buildReduceOrders`, but those **shrink the quantity of an existing order in place** (documented in
`orders.d.ts` as "keeps the id and shrinks the order in place"); none of them sets a reduce-only /
close-only flag on a new order. The gap described here is the missing flag, not a missing function.

Either support `reduceOnly` for plain limit/market orders, or state explicitly in the documentation that
reduce-only is available only through TP/SL (i.e. through `placePerpStopOrder({ intent: "reduceOnly" })`).

## Actual

- `PlacePerpOrderParams` has no `reduceOnly` and no `userData` field.
- `perpOrderCall` hardcodes the contract's `userData` argument to `0n`, so a bit flag cannot be smuggled
  through it either.
- The contract's `placeOrder` ABI used by the SDK takes nine positional arguments with no reduce-only
  flag, and `ORDER_TYPE` is only `0 Normal | 1 FillOrKill | 2 ImmediateOrCancel | 3 PostOnly`.
- The only `reduceOnly` in the public SDK surface is `PerpStopIntent = "reduceOnly" | "opening"`, i.e.
  reduce-only exists **only** for conditional take-profit / stop-loss orders.

A builder therefore cannot send an ordinary reduce-only limit or market order through the SDK, although
the docs present reduce-only as an order-type property.

## Evidence

- `dist/trade.d.ts`, `interface PlacePerpOrderParams` — no `reduceOnly`, no `userData` (quoted above).
- `dist/orders.js:1622` — `0n` passed as `userData` unconditionally.
- `dist/trade.d.ts:1393` — `PerpStopIntent = "reduceOnly" | "opening"` (stops only).
- Docs `/docs/trading/perps-testnet/orders`: "Reduce-only orders can only shrink a position, never open
  or flip one."
- Reproduced by type inspection and by building a call with the SDK 0.32.1 (no wallet, no send):
  the produced calldata carries `userData = 0` and there is no field to change it.

## Environment

`@somnia-chain/markets-sdk` **0.32.1**, Node **24.14.1**, Hideki perps testnet (chain 50383). Read-only —
no wallet, no transactions.
