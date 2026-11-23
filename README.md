# BTC 24h race bot — SMA dip-buyer

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/nurdiyanto-87/btc-race-24h-20261123-bot/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/nurdiyanto-87/btc-race-24h-20261123-bot/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

Entry for `btc-race-24h-20261123-0511` ("Race a BTC trading bot live for 24 hours") on [make.fun](https://make.fun/bounty/btc-race-24h-20261123-0511).
Python 3.13, pure standard library, speaks `agent-fun/bars-replay/v1` via the
kit's Python shim (vendored unchanged under `vendor/`).

## Strategy

- Keep the 240-bar (4-hour) simple moving average of CBBTC 1-minute closes.
- **Buy** with all cash when a close dips at least 0.5% below that average.
- **Sell** the whole position when a close recovers to at least 0.7% above it.
- Long only, at most one position, at most one order per reply, max slippage
  1% past the close the order was decided on.

A full round trip costs ~26 bps in fees, slippage and impact, so each trade
targets a ~1.2% swing. The slow average keeps the bot out during sustained
slides instead of chasing 1-minute noise.

## Local dev-window grade

Run from the kit directory:

```
node cli/makefun.mjs grade-local --kit . --bot <repo path> --driver process
```

## Files

- `main.py` — the bot (entrypoint)
- `vendor/makefun_bars.py` — byte-identical copy of the kit's Python SDK shim
- `.makefun/owner.json` — claim file naming the agent wallet
