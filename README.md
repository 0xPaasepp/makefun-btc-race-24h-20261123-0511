# makefun-btc-race-24h-20261123-0511

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/0xPaasepp/makefun-btc-race-24h-20261123-0511/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/0xPaasepp/makefun-btc-race-24h-20261123-0511/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

A pure-stdlib Python trading bot for make.fun's [Race a BTC trading bot live for 24 hours](https://make.fun/bounty/btc-race-24h-20261123-0511) bounty ($50 in USDC).

## Strategy

Dip-buy mean reversion on cbBTC 1-minute bars: buy a deep dislocation (140 bps below the 30-bar SMA) once it stops falling (rising close); exit +200 bps TP, -100 bps SL, or 1440-bar hold. No primary buy after bar 1320. Late fallbacks guarantee ≥1 trade, at 1/3 size with a stall exit.

## Results (frozen dev window, 1,440 bars)

- Net PnL +$4.05 (+0.41%), DD 0.08%, 2 trades, fees $0.27 (fallback trade, buy 1291 / sell 1328; primary never fires, deepest dip -107 bps)
- Out of sample (previous dev window): +$18.33, 2 trades, DD 1.50%
- Stress (68 windows): mean +$3.02/+$0.72, worst -$13.70/-$14.65, DD ≤2.02%, trade on 34/34 both sets

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=ddn7bre1&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
