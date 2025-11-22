"""
Funzioni di reportistica per i risultati di backtest.
"""

from typing import Any, Dict

import pandas as pd

from trading_lab.backtest.backtester import BacktestResult


def _format_pct(x: float | None) -> str:
    if x is None:
        return "n/a"
    return f"{x:.2f}%"


def print_basic_report(result: BacktestResult) -> None:
    """
    Stampa un report testuale minimo per un BacktestResult,
    includendo un log sintetico dei singoli trade.
    """
    stats: Dict[str, Any] = result.stats

    print("=== Backtest Report ===")
    print(f"- Capitale iniziale: {stats.get('initial_capital', 0):.2f}")
    print(f"- Capitale finale:   {stats.get('final_capital', 0):.2f}")
    print(f"- Rendimento totale: {_format_pct(stats.get('total_return_pct'))}")
    print(f"- N. trade:          {stats.get('num_trades')}")

    if stats.get("win_rate_pct") is not None:
        print(f"- Win rate:          {_format_pct(stats['win_rate_pct'])}")
        print(f"- Rendimento medio trade: {_format_pct(stats['avg_net_return_pct'])}")
        print(f"- Max drawdown:      {_format_pct(stats['max_drawdown_pct'])}")
    else:
        print("- Nessun trade eseguito.")

    trades = result.trades
    if trades is None or trades.empty:
        print("\n[Nessun trade da mostrare]")
        print("\nUltimi valori equity curve:")
        print(result.equity_curve.tail(5))
        return

    trades = trades.copy()
    trades["net_return_pct"] = trades["net_return"] * 100.0
    trades["pnl"] = trades["pnl"].round(2)

    cols = [
        "entry_time",
        "exit_time",
        "hold_days",
        "net_return_pct",
        "pnl",
        "entry_price",
        "exit_price",
    ]

    print("\n--- Trade log (prime 5 operazioni) ---")
    print(
        trades[cols]
        .head(5)
        .to_string(
            index=False,
            formatters={
                "net_return_pct": lambda x: f"{x:.2f}%",
                "pnl": lambda x: f"{x:.2f}",
                "entry_price": lambda x: f"{x:.2f}",
                "exit_price": lambda x: f"{x:.2f}",
            },
        )
    )

    print("\n--- Trade log (ultime 5 operazioni) ---")
    print(
        trades[cols]
        .tail(5)
        .to_string(
            index=False,
            formatters={
                "net_return_pct": lambda x: f"{x:.2f}%",
                "pnl": lambda x: f"{x:.2f}",
                "entry_price": lambda x: f"{x:.2f}",
                "exit_price": lambda x: f"{x:.2f}",
            },
        )
    )

    # Best / worst trade per net_return
    best = trades.loc[trades["net_return"].idxmax()]
    worst = trades.loc[trades["net_return"].idxmin()]

    print("\n--- Miglior / Peggior trade (per rendimento %) ---")
    print(
        f"Miglior trade: {best['entry_time']} -> {best['exit_time']}, "
        f"ret={best['net_return_pct']:.2f}%, pnl={best['pnl']:.2f}"
    )
    print(
        f"Peggior trade: {worst['entry_time']} -> {worst['exit_time']}, "
        f"ret={worst['net_return_pct']:.2f}%, pnl={worst['pnl']:.2f}"
    )

    print("\nUltimi valori equity curve:")
    print(result.equity_curve.tail(5))
