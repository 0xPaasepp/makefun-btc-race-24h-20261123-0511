# makefun-btc-race-24h-20261123-0511

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/0xPaasepp/makefun-btc-race-24h-20261123-0511/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/0xPaasepp/makefun-btc-race-24h-20261123-0511/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

A pure-stdlib Python trading bot for make.fun's [Race a BTC trading bot live for 24 hours](https://make.fun/bounty/btc-race-24h-20261123-0511) bounty ($50 in USDC).

## Strategy

Dip-ladder mean reversion on cbBTC 1-minute bars: buy a dislocation in slices (25% of cash at 90 bps below the 30-bar SMA on a rising close, +50% of the rest at 130, the remainder at 170); exit +250 bps TP, -120 bps SL, or 1440-bar hold. No primary buy after bar 1320. Late fallbacks guarantee ≥1 trade, at 1/3 size.

## Results (frozen dev window, 1,440 bars)

- Net PnL +$1.90 (+0.19%), DD 0.40%, 1 trade, fees $0.20 (first slice only, buy 435, flattened at end; deepest dip -107 bps)
- Out of sample (previous dev window): +$23.83, 4 trades, DD 1.50% (slices bought 66-68, sold 507 at TP250)
- Stress (68 windows): mean +$5.31/+$0.31, worst -$14.62/-$13.76, DD ≤2.06%, trade on 34/34 both sets

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=ddn7bre1&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
