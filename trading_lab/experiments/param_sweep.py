"""
Param sweep semplice per Strategia 1 – BTC Daily Long-Only.

Obiettivo:
- variare alcuni parametri chiave
- confrontare rendimento totale, max drawdown, n. trade
- NON fare overfitting, solo capire se ci sono zone di parametri "sensate".
"""

from itertools import product

import pandas as pd

from trading_lab.data import load_btc_daily_csv
from trading_lab.strategies.btc_trend_daily import BTCTrendDailyParams, generate_signals
from trading_lab.backtest.backtester import run_backtest


def run_param_sweep() -> pd.DataFrame:
    df = load_btc_daily_csv()

    ma_long_values = [100, 150, 200]
    breakout_values = [20, 40]
    atr_stop_values = [1.5, 2.0, 2.5]

    rows = []

    for ma_long, breakout_lb, atr_stop_mult in product(
        ma_long_values, breakout_values, atr_stop_values
    ):
        params = BTCTrendDailyParams(
            ma_long_window=ma_long,
            breakout_lookback=breakout_lb,
            atr_window=14,
            atr_stop_multiple=atr_stop_mult,
            max_hold_days=60,
        )

        signals = generate_signals(df, params)
        result = run_backtest(
            df,
            signals,
            initial_capital=10000.0,
            commission_rate=0.001,
            max_hold_days=params.max_hold_days,
            atr_window=params.atr_window,
            atr_stop_multiple=params.atr_stop_multiple,
        )

        stats = result.stats
        rows.append(
            {
                "ma_long": ma_long,
                "breakout_lookback": breakout_lb,
                "atr_stop_multiple": atr_stop_mult,
                "num_trades": stats.get("num_trades"),
                "total_return_pct": stats.get("total_return_pct"),
                "max_drawdown_pct": stats.get("max_drawdown_pct"),
                "win_rate_pct": stats.get("win_rate_pct"),
                "avg_net_return_pct": stats.get("avg_net_return_pct"),
            }
        )

    df_res = pd.DataFrame(rows)
    # rapporto rendimento / drawdown (assoluto) come metrica grezza di qualità
    df_res["return_over_dd"] = df_res["total_return_pct"] / df_res["max_drawdown_pct"].abs()

    return df_res


def main() -> None:
    df_res = run_param_sweep()

    print("=== Param sweep Strategia 1 – BTC Daily Long-Only ===")
    print("\nTop 10 per rendimento totale:")
    print(
        df_res.sort_values("total_return_pct", ascending=False)
        .head(10)
        .to_string(index=False, formatters={"total_return_pct": "{:.2f}".format,
                                            "max_drawdown_pct": "{:.2f}".format,
                                            "return_over_dd": "{:.3f}".format})
    )

    print("\nTop 10 per rapporto rendimento / drawdown:")
    print(
        df_res.sort_values("return_over_dd", ascending=False)
        .head(10)
        .to_string(index=False, formatters={"total_return_pct": "{:.2f}".format,
                                            "max_drawdown_pct": "{:.2f}".format,
                                            "return_over_dd": "{:.3f}".format})
    )


if __name__ == "__main__":
    main()
