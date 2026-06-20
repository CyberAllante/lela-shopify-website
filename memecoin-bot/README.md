# Solana Meme-Coin Paper-Trading Bot

A **paper-trading (simulation) sniper bot** for Solana meme coins in the style of
[pump.fun](https://pump.fun): it watches for **newly launched tokens**, simulates
an **entry**, then automatically **exits at a profit target** — with stop-loss and
trailing-stop protection so paper losers get cut.

> ⚠️ **Paper mode only.** This bot **does not place real trades** and holds **no
> keys or funds**. It exists to design, test, and stress a strategy safely before
> any real money is ever involved. Live order execution is intentionally *not*
> implemented. Crypto trading — and meme coins especially — is extremely risky;
> most new launches go to zero. Nothing here is financial advice.

## Why "Ana + XRP" became this

You asked for a "solo Ana (Solana) and XRP" bot targeting pump.fun meme coins.
pump.fun is a **Solana-only** launchpad — XRP and SOL themselves don't trade
there — so the bot is built around the Solana meme-coin launch flow (detect new
coin → buy → take profit). The strategy and risk knobs are all config-driven, so
you can retune it without touching code.

## How it works

```
            ┌─────────────┐   new token     ┌────────────┐  should_enter?  ┌────────────┐
  pump.fun ─▶   MarketFeed  ├───────────────▶  Strategy   ├────────────────▶ PaperBroker │
 (or mock)  └─────────────┘   price ticks    └────────────┘   should_exit?  └─────┬──────┘
                   ▲                                                               │ fills
                   └───────────────── watch(mint) ────────────────────────────────┘
                                                                                   ▼
                                                                             Portfolio + trades.csv
```

- **Feed** — an async source of `new token` and `price tick` events.
  - `mock`: a fully offline synthetic market (no network/keys) so you can watch
    the strategy work immediately. Some tokens moon, most fade or rug.
  - `pumpportal`: the **live** pump.fun data stream via
    [PumpPortal's free WebSocket API](https://pumpportal.fun/data-api/real-time)
    (read-only; prices only).
- **Strategy** (`SniperStrategy`) — pure, unit-tested rules:
  - **Entry:** snipe a fresh launch if we have room (`max_open_positions`), cash,
    and the price is within an optional band.
  - **Exit:** close on **take-profit**, **stop-loss**, **trailing stop**, or
    **max hold time** — whichever fires first.
- **PaperBroker** — simulates fills with a configurable **fee** (~1% pump.fun-style)
  and **slippage**, debits/credits a paper SOL balance. This is the safety boundary.
- **Portfolio + trade log** — tracks open positions, realized P&L, win rate, and
  appends every closed trade to `trades.csv`.

## Quick start

```bash
cd memecoin-bot

# Optional but recommended (config file + live feed support):
pip install -r requirements.txt

# Run the offline demo for 30 seconds, then print a P&L summary:
python run.py --config config.yaml --runtime 30
```

The core (mock feed + paper broker) runs on the **standard library alone** —
`pip install` is only needed for `config.yaml` parsing (PyYAML) and the live feed
(`websockets`).

### Sample output

```
BUY  CBK    0.0500 SOL @ 4.561e-08 -> 1085181.16 tokens | open=2 | cash=0.8644 SOL
SELL CBK    take_profit   PROFIT +0.0233 SOL (+46.6%) | held 3s | cash=0.8877 SOL
SELL UQTG   trailing_stop LOSS   -0.0131 SOL (-26.1%) | held 5s | cash=0.9246 SOL
===== Paper Trading Summary =====
Closed trades : 4  (wins 1 / losses 3, win rate 25%)
Realized PnL  : -0.025367 SOL
```

## Using the live pump.fun feed (still paper trades!)

```bash
pip install websockets
python run.py --feed pumpportal --runtime 120
```

This connects to PumpPortal, reacts to **real** new launches and **real** prices,
but every buy/sell is still simulated against your paper balance. Nothing touches
a wallet.

## Configuration

Edit `config.yaml` (or override common knobs with env vars / CLI flags):

| Setting | Meaning | Default |
|---|---|---|
| `strategy.buy_amount_sol` | SOL spent per snipe | `0.05` |
| `strategy.take_profit_pct` | Exit target (`0.5` = +50%) | `0.5` |
| `strategy.stop_loss_pct` | Hard stop (`0.3` = −30%) | `0.3` |
| `strategy.trailing_stop_pct` | Trail from peak once green (`0` = off) | `0.25` |
| `strategy.max_hold_seconds` | Force-exit timer | `600` |
| `strategy.max_open_positions` | Concurrent position cap | `5` |
| `broker.starting_balance_sol` | Paper wallet size | `1.0` |
| `broker.fee_pct` / `broker.slippage_pct` | Simulated trade costs | `0.01` / `0.02` |
| `feed.source` | `mock` or `pumpportal` | `mock` |

Env overrides: `BOT_FEED_SOURCE`, `BOT_BUY_AMOUNT_SOL`, `BOT_TAKE_PROFIT_PCT`,
`BOT_STOP_LOSS_PCT`, `BOT_LOG_LEVEL`. CLI: `--feed`, `--runtime`, `--log-level`.

## Tests

```bash
pip install pytest
python -m pytest -q     # 20 tests: strategy rules, broker accounting, end-to-end smoke
```

## Project layout

```
memecoin-bot/
├── run.py                  # CLI entry point
├── config.yaml             # all tunable settings
├── requirements.txt
├── bot/
│   ├── config.py           # load + validate settings
│   ├── models.py           # TokenEvent, Position, ClosedTrade, ...
│   ├── bot.py              # orchestrator / event loop
│   ├── trade_log.py        # trades.csv writer
│   ├── feeds/              # mock + pumpportal (live) data sources
│   └── engine/             # paper_broker, portfolio, strategy
└── tests/
```

## Going live, later (what would be required)

Real execution is deliberately omitted. To trade for real you would need to add
a wallet/keypair, a Solana RPC, and a swap/transaction path (e.g. PumpPortal's
trade API or Jupiter) behind a new `LiveBroker` that mirrors `PaperBroker`'s
interface — plus hard spend caps, rate limiting, and a kill switch. **Validate a
configuration in paper mode first.** Meme coins are a high-loss environment; size
anything real at a level you can afford to lose entirely.
