"""
Funzioni di reportistica per i risultati di backtest.
"""

from typing import Any

from trading_lab.backtest.backtester import BacktestResult


def print_basic_report(result: BacktestResult) -> None:
    """
    Stampa un report testuale minimo per un BacktestResult.
    """
    stats = result.stats

    print("=== Backtest Report ===")
    print(f"- Capitale iniziale: {stats.get('initial_capital'):.2f}")
    print(f"- Capitale finale:   {stats.get('final_capital'):.2f}")
    print(f"- Rendimento totale: {stats.get('total_return_pct'):.2f}%")
    print(f"- N. trade:          {stats.get('num_trades')}")

    if stats.get("win_rate_pct") is not None:
        print(f"- Win rate:          {stats['win_rate_pct']:.2f}%")
        print(f"- Rendimento medio trade: {stats['avg_net_return_pct']:.4f}%")
        print(f"- Max drawdown:      {stats['max_drawdown_pct']:.2f}%")
    else:
        print("- Nessun trade eseguito.")

    print()
    print("Ultimi valori equity curve:")
    print(result.equity_curve.tail(5))
