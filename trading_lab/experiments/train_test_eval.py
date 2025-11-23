"""
Train/Test evaluation per Strategia 1 – BTC Daily Long-Only.
"""

from itertools import product

import pandas as pd

from trading_lab.data import load_btc_daily
from trading_lab.strategies.btc_trend_daily import BTCTrendDailyParams, generate_signals
from trading_lab.backtest.backtester import run_backtest


def _run_backtest_with_params(df: pd.DataFrame, params: BTCTrendDailyParams) -> dict:
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
    return {
        "num_trades": stats.get("num_trades"),
        "total_return_pct": stats.get("total_return_pct"),
        "max_drawdown_pct": stats.get("max_drawdown_pct"),
        "win_rate_pct": stats.get("win_rate_pct"),
        "avg_net_return_pct": stats.get("avg_net_return_pct"),
    }


def run_train_test_evaluation() -> pd.DataFrame:
    df = load_btc_daily()

    n = len(df)
    split_idx = int(n * 0.6)
    df_train = df.iloc[:split_idx].copy()
    df_test = df.iloc[split_idx:].copy()

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

        train_stats = _run_backtest_with_params(df_train, params)
        test_stats = _run_backtest_with_params(df_test, params)

        row = {
            "ma_long": ma_long,
            "breakout_lookback": breakout_lb,
            "atr_stop_multiple": atr_stop_mult,
            "train_num_trades": train_stats["num_trades"],
            "train_total_return_pct": train_stats["total_return_pct"],
            "train_max_drawdown_pct": train_stats["max_drawdown_pct"],
            "train_win_rate_pct": train_stats["win_rate_pct"],
            "train_avg_net_return_pct": train_stats["avg_net_return_pct"],
            "test_num_trades": test_stats["num_trades"],
            "test_total_return_pct": test_stats["total_return_pct"],
            "test_max_drawdown_pct": test_stats["max_drawdown_pct"],
            "test_win_rate_pct": test_stats["win_rate_pct"],
            "test_avg_net_return_pct": test_stats["avg_net_return_pct"],
        }

        if row["train_max_drawdown_pct"] not in (None, 0):
            row["train_return_over_dd"] = row["train_total_return_pct"] / abs(
                row["train_max_drawdown_pct"]
            )
        else:
            row["train_return_over_dd"] = None

        if row["test_max_drawdown_pct"] not in (None, 0):
            row["test_return_over_dd"] = row["test_total_return_pct"] / abs(
                row["test_max_drawdown_pct"]
            )
        else:
            row["test_return_over_dd"] = None

        rows.append(row)

    df_res = pd.DataFrame(rows)
    return df_res


def main() -> None:
    df_res = run_train_test_evaluation()

    print("=== Train/Test evaluation – Strategia 1 BTC Daily Long-Only ===")

    print("\nTop 10 per return/drawdown sul TRAIN:")
    print(
        df_res.sort_values("train_return_over_dd", ascending=False)
        .head(10)
        .to_string(
            index=False,
            formatters={
                "train_total_return_pct": "{:.2f}".format,
                "train_max_drawdown_pct": "{:.2f}".format,
                "train_return_over_dd": "{:.3f}".format,
                "test_total_return_pct": "{:.2f}".format,
                "test_max_drawdown_pct": "{:.2f}".format,
                "test_return_over_dd": "{:.3f}".format,
            },
        )
    )

    print("\n(Colonne test_* mostrano come gli stessi parametri si comportano sul periodo TEST.)")


if __name__ == "__main__":
    main()
