"""Dip-buy bot for agent-fun/bars-replay/v1 (make.fun btc-race-24h-20261123-0511).

Buy cbBTC only after a deep dislocation has stopped falling, ride the
snap-back, never chase a rally. Primary: buy at -140 bps vs the 30-bar SMA
on a rising close; exit +200 bps TP, -100 bps SL, or 1440-bar hold; no
primary buy after bar 1320 (flattened almost at once, paying a full round
trip for ~nothing). 1-min noise is ~8 bps, a full round trip costs ~26 bps,
so only a real dislocation pays. Late fallbacks (only if never traded):
from bar 1200 a -40 bps dip, 1350 any -25 bps dip, 1380 a +40 bps uptrend --
ONE-THIRD size, exits +120/-60/240 bars, plus a stall exit (+30 bps after
120 bars). They guarantee the race's >=1-trade guardrail on a quiet
window. One position max; 30-bar cooldown after exits; hold counted from
the first held batch. Pure stdlib, deterministic, no clock/network/files.

Verified (kit fill model, real protocol driver, python3 -P -s): dev
+$4.05 (+0.41%), DD 0.08%, 2 trades -- a 1/3-size fallback trade (buy
batch 1291, sell 1328); the primary never fires on this quiet up window
(deepest dip -107 bps). Previous race's dev window (out of sample):
+$18.33, 2 trades, DD 1.50%. 68 stress windows: mean +$3.02/+$0.72,
worst -$13.70/-$14.65, DD <=2.02%, trade on 34/34 both sets.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"

# Tuned on dev; stress-tested on 68 windows + prev dev.
SMA_BARS = 30
DIP_BPS = 140
TAKE_PROFIT_BPS = 200
STOP_LOSS_BPS = 100
MAX_HOLD_BARS = 1440
PRIMARY_CUTOFF_BAR = 1320
COOLDOWN_BARS = 30
FB_TAKE_PROFIT_BPS = 120
FB_STOP_LOSS_BPS = 60
FB_MAX_HOLD_BARS = 240
STALL_BARS = 120
STALL_BPS = 30
MAX_SLIPPAGE_BPS = 300
FALLBACK_BAR = 1200
FALLBACK_DIP_BPS = 40
LAST_RESORT_BAR = 1350
LAST_RESORT_DIP_BPS = 25
TREND_BAR = 1380
TREND_BPS = 40  # revised 50 -> 40: 3 stress windows never traded at 50
FALLBACK_SIZE = 0.33

BPS = 10_000


class Bot:
    def __init__(self):
        self.closes = []
        self.entry_seq = -1
        self.cool_until = -1
        self.ever_traded = False
        self.mode = 1

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
            # Entry price from cost (fees included: a touch above the fill).
            entry_px = holding.cost * 10 ** 13 // (qty * 10 ** 6)
            move_bps = (close - entry_px) * BPS // entry_px
            if self.mode == 1:
                tp, sl, hold = TAKE_PROFIT_BPS, STOP_LOSS_BPS, MAX_HOLD_BARS
            else:
                tp, sl, hold = FB_TAKE_PROFIT_BPS, FB_STOP_LOSS_BPS, FB_MAX_HOLD_BARS
            # Fallback stall exit: still under +30 bps after 120 bars
            # is a dead dip. Mode 1 never gets it (a real winner ground
            # 400+ bars before TP on the previous window).
            stall = (
                self.mode == 2
                and state.seq - self.entry_seq >= STALL_BARS
                and move_bps < STALL_BPS
            )
            if (
                move_bps >= tp
                or move_bps <= -sl
                or stall
                or state.seq - self.entry_seq >= hold
            ):
                self.cool_until = state.seq + COOLDOWN_BARS
                self.entry_seq = -1
                return [
                    {
                        "side": "sell",
                        "symbol": SYMBOL,
                        "qty": qty,
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
        if dip_bps <= -DIP_BPS and rising and seq <= PRIMARY_CUTOFF_BAR:
            buy = True
            self.mode = 1
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
            notional = state.cash if self.mode == 1 else int(state.cash * FALLBACK_SIZE)
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
