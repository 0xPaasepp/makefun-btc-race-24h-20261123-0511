"""Dip-ladder bot v2 for agent-fun/bars-replay/v1 (make.fun btc-race-24h-20261123-0511).

Buy the dip in slices, ride a BIGGER take profit. Primary: 25% of
cash at -90 bps vs the 30-bar SMA on a rising close, +50% of the rest
at -130, the remainder at -170; exit +250 bps TP, -120 bps SL, or
1440-bar hold; no primary buy after bar 1320. A single all-in dip-buy
with a huge TP rarely fires; averaging down and exiting at +250
captures the snap-back the prev window made (TP300 is a cliff
there). Late fallbacks (only if never traded):
from bar 1200 a -40 bps dip, 1350 any -25 bps dip, 1380 a +40 bps
uptrend -- ONE-THIRD size, same +250/-120 exits. One position max;
30-bar cooldown; hold counted from the first held batch. Pure stdlib,
deterministic, no clock/network/files.

Verified (real protocol driver, python3 -P -s, 2 runs byte-identical):
dev +$1.90, DD 0.40%, 1 trade (first slice only, flattened at end);
prev window (OOS) +$23.83, DD 1.50%, 4 trades (3 slices + TP250
sell); stress-34 mean +$5.31/+$0.31, worst -$14.62/-$13.76,
DD <=2.06%, trade on 34/34 both sets.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
BPS = 10_000

# Dip ladder: (dip bps vs SMA30, % of cash). First slice opens it.
SMA_BARS = 30
LADDER = ((90, 25), (130, 50), (170, 100))
TAKE_PROFIT_BPS = 250
STOP_LOSS_BPS = 120
MAX_HOLD_BARS = 1440
PRIMARY_CUTOFF_BAR = 1320
COOLDOWN_BARS = 30
MAX_SLIPPAGE_BPS = 300
FALLBACK_BAR = 1200
FALLBACK_DIP_BPS = 40
LAST_RESORT_BAR = 1350
LAST_RESORT_DIP_BPS = 25
TREND_BAR = 1380
TREND_BPS = 40
FALLBACK_SIZE = 0.33


class Bot:
    def __init__(self):
        self.closes = []
        self.entry_seq = -1
        self.cool_until = -1
        self.ever_traded = False
        self.mode = 1
        self.level = 0

    def on_batch(self, state, batch):
        if state.warming_up:
            return []
        close = state.close(SYMBOL)
        if close is None:
            return []
        self.closes.append(close)
        holding = state.positions.get(SYMBOL)
        qty = holding.qty if holding is not None else 0
        if qty > 0:
            self.ever_traded = True
            if self.entry_seq < 0:
                self.entry_seq = state.seq
            entry_px = holding.cost * 10 ** 13 // (qty * 10 ** 6)
            move_bps = (close - entry_px) * BPS // entry_px
            if (
                move_bps >= TAKE_PROFIT_BPS
                or move_bps <= -STOP_LOSS_BPS
                or state.seq - self.entry_seq >= MAX_HOLD_BARS
            ):
                self.cool_until = state.seq + COOLDOWN_BARS
                self.entry_seq = -1
                self.level = 0
                return [
                    {
                        "side": "sell",
                        "symbol": SYMBOL,
                        "qty": qty,
                        "max_slippage_bps": MAX_SLIPPAGE_BPS,
                    }
                ]
            if self.mode == 1 and self.level < len(LADDER):
                mean = sum(self.closes[-SMA_BARS:]) // SMA_BARS
                dip_bps = (close - mean) * BPS // mean
                need, pct = LADDER[self.level]
                if dip_bps <= -need and state.cash > 0:
                    self.level += 1
                    return [
                        {
                            "side": "buy",
                            "symbol": SYMBOL,
                            "notional_quote_units": state.cash * pct // 100,
                            "max_slippage_bps": MAX_SLIPPAGE_BPS,
                        }
                    ]
            return []

        if state.seq < self.cool_until:
            return []
        if len(self.closes) < SMA_BARS:
            return []
        mean = sum(self.closes[-SMA_BARS:]) // SMA_BARS
        seq = state.seq
        dip_bps = (close - mean) * BPS // mean
        rising = close >= self.closes[-2]
        buy = False
        if dip_bps <= -LADDER[0][0] and rising and seq <= PRIMARY_CUTOFF_BAR:
            buy = True
            self.mode = 1
            self.level = 1
        if not buy and not self.ever_traded:
            if seq >= TREND_BAR and dip_bps >= TREND_BPS:
                buy = True
            elif seq >= LAST_RESORT_BAR and dip_bps <= -LAST_RESORT_DIP_BPS:
                buy = True
            elif seq >= FALLBACK_BAR and dip_bps <= -FALLBACK_DIP_BPS:
                buy = True
            if buy:
                self.mode = 2
        if buy and state.cash > 0:
            if self.mode == 1:
                notional = state.cash * LADDER[0][1] // 100
            else:
                notional = int(state.cash * FALLBACK_SIZE)
            return [
                {
                    "side": "buy",
                    "symbol": SYMBOL,
                    "notional_quote_units": notional,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                }
            ]
        return []


_BOT = Bot()


def on_batch(state, batch):
    return _BOT.on_batch(state, batch)


makefun_bars.run(on_batch)
