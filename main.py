"""Dip-buy mean-reversion bot for the cbBTC/USDC 24h race (agent-fun/bars-replay/v1).

Strategy, in one paragraph: over the 1-minute closes, keep the 240-bar (4-hour)
simple moving average. When the close dips at least 0.5% below that average,
buy with all available cash. When the close recovers to at least 0.7% above
the average, sell the whole position. One position at most, long only, one
order per reply at most.

Why this shape: a full round trip costs about 26 bps in fees, slippage and
price impact, so a trade needs a swing clearly larger than that. Buying a
0.5% dip under a slow average and selling 0.7% above it targets a ~1.2%
round trip, and the slow average keeps the bot out of the market during
sustained slides instead of chasing every 1-minute wiggle. Fast trend
systems whipsaw on 1-minute noise and pay the round-trip cost dozens of
times; this one trades a handful of times a day.

Determinism: the average is an integer running sum divided once per bar
(IEEE float division, same order every run); no clock, no environment, no
randomness, no sets or dicts whose iteration order could vary. The bot
reads only the bars the harness sends it.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"

# Length of the moving average, in bars (240 minutes = 4 hours).
SMA_BARS = 240
# Buy when close < SMA * (10000 - BUY_BAND_BPS) / 10000  (0.5% under the average).
BUY_BAND_BPS = 50
# Sell when close >= SMA * (10000 + SELL_BAND_BPS) / 10000  (0.7% over the average).
SELL_BAND_BPS = 70
# Orders are capped at 1% past the close they were decided on; a fill past
# that is refused and the signal is simply re-sent on the next bar.
MAX_SLIPPAGE_BPS = 100


class DipBuyer:
    """The 240-bar SMA over closes, kept as an exact integer running sum."""

    def __init__(self):
        self.closes = []
        self.running_sum = 0

    def push(self, close):
        """Add a close; returns the SMA as a float once SMA_BARS closes are in."""
        self.closes.append(close)
        self.running_sum += close
        if len(self.closes) > SMA_BARS:
            self.running_sum -= self.closes.pop(0)
        if len(self.closes) < SMA_BARS:
            return None
        return self.running_sum / SMA_BARS

    def buy_signal(self, close, sma):
        return close * 10000 < sma * (10000 - BUY_BAND_BPS)

    def sell_signal(self, close, sma):
        return close * 10000 >= sma * (10000 + SELL_BAND_BPS)


STATE = DipBuyer()


def on_batch(state, batch):
    if state.warming_up:
        return []
    for bar in batch["bars"]:
        if bar["symbol"] != SYMBOL:
            continue
        close = int(bar["c"])
        sma = STATE.push(close)
        if sma is None:
            continue
        held = state.positions.get(SYMBOL)
        if held is not None:
            if STATE.sell_signal(close, sma):
                return [{
                    "side": "sell",
                    "symbol": SYMBOL,
                    "qty": held.qty,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                }]
        elif STATE.buy_signal(close, sma):
            cash = state.cash
            if cash >= int(state.hello["fees"]["min_notional_quote_units"]):
                return [{
                    "side": "buy",
                    "symbol": SYMBOL,
                    "notional_quote_units": cash,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                }]
    return []


makefun_bars.run(on_batch)
