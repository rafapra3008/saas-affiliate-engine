"""
Run config – Strategia 2 BTC Daily Long/Short con filtro di regime.

Questo script:
- carica i dati BTCUSD daily (multi-anni),
- genera segnali long/short della Strategia 2,
- esegue il backtest long+short con ATR stop e max_hold_days,
- stampa un piccolo report e i primi/ultimi trade.
"""

from trading_lab.data import load_btc_daily
from trading_lab.strategies.btc_trend_daily_v2 import (
    BTCTrendDailyV2Params,
    generate_signals_v2,
)
from trading_lab.backtest.backtester_v2 import run_backtest_long_short


def main() -> None:
    df = load_btc_daily()
    params = BTCTrendDailyV2Params()

    print("=== Strategia 2 BTC Daily Long/Short – Config di base ===")
    print("Parametri:", params)

    signal_long, signal_short = generate_signals_v2(df, params)

    result = run_backtest_long_short(
        df,
        signal_long,
        signal_short,
        initial_capital=10_000.0,
        commission_rate=0.001,
        atr_window=params.atr_window,
        atr_stop_multiple=params.atr_stop_multiple,
        max_hold_days=params.max_hold_days,
    )

    stats = result.stats
    print("\n=== Stats backtest v2 ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    trades = result.trades
    print(f"\nNumero trade: {len(trades)}")

    if trades:
        print("\nPrimi 5 trade:")
        for t in trades[:5]:
            print(t)

        print("\nUltimi 5 trade:")
        for t in trades[-5:]:
            print(t)


if __name__ == "__main__":
    main()
