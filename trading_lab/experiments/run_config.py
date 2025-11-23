"""
Esegue un backtest singolo della Strategia 1 su BTCUSD daily
con una configurazione di parametri specifica, mostrando:

- report base
- trade log completo
- P&L aggregato per anno
"""

import pandas as pd

from trading_lab.data import load_btc_daily
from trading_lab.strategies.btc_trend_daily import BTCTrendDailyParams, generate_signals
from trading_lab.backtest.backtester import run_backtest
from trading_lab.metrics.report import print_basic_report


def run_single_config(params: BTCTrendDailyParams) -> None:
    df = load_btc_daily()
    print(f"[INFO] Dati caricati: {len(df)} barre daily da {df.index.min()} a {df.index.max()}")

    signals = generate_signals(df, params)
    print(f"[INFO] Segnali long totali: {int(signals.sum())}")

    result = run_backtest(
        df,
        signals,
        initial_capital=10000.0,
        commission_rate=0.001,
        max_hold_days=params.max_hold_days,
        atr_window=params.atr_window,
        atr_stop_multiple=params.atr_stop_multiple,
    )

    print_basic_report(result)

    trades = result.trades
    if trades is None or trades.empty:
        print("[INFO] Nessun trade nella configurazione selezionata.")
        return

    print("\n=== Trade log completo ===")
    trades_to_print = trades.copy()
    trades_to_print["net_return_pct"] = trades_to_print["net_return"] * 100.0
    trades_to_print["pnl"] = trades_to_print["pnl"].round(2)

    cols = [
        "entry_time",
        "exit_time",
        "hold_days",
        "net_return_pct",
        "pnl",
        "entry_price",
        "exit_price",
        "exit_reason",
    ]

    print(
        trades_to_print[cols].to_string(
            index=False,
            formatters={
                "net_return_pct": lambda x: f"{x:.2f}%",
                "pnl": lambda x: f"{x:.2f}",
                "entry_price": lambda x: f"{x:.2f}",
                "exit_price": lambda x: f"{x:.2f}",
            },
        )
    )

    print("\n=== P&L per anno (basato su exit_time) ===")
    trades_yearly = trades.copy()
    trades_yearly["year"] = trades_yearly["exit_time"].dt.year
    yearly = trades_yearly.groupby("year")["pnl"].agg(["sum", "count"]).rename(
        columns={"sum": "pnl_sum", "count": "num_trades"}
    )
    yearly["pnl_sum"] = yearly["pnl_sum"].round(2)
    print(yearly)


if __name__ == "__main__":
    # Configurazione scelta (robusta su train/test multi-anno)
    params = BTCTrendDailyParams(
        ma_long_window=200,
        breakout_lookback=40,
        atr_window=14,
        atr_stop_multiple=2.0,
        max_hold_days=60,
    )
    print(f"[CONFIG] {params}")
    run_single_config(params)
