"""
Backtester generico (prima versione).

Assunzioni per Fase 0–1:
- dati: DataFrame con almeno colonne 'open' e 'close', indice datetime (daily).
- signals: Serie con 0/1 (1 = segnale di ingresso long quel giorno).
- Solo una posizione alla volta (long-only, no leva).
- Entrata: al prezzo di OPEN del giorno successivo al segnale (se esiste).
- Uscita: dopo un numero massimo di giorni (max_hold_days) al prezzo di CLOSE.
- Commissioni: percentuale per lato applicata su entrata e uscita.

Questo è un modello semplice per iniziare: l'obiettivo è avere una equity curve con cui
ragionare, non ancora la strategia finale.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

import pandas as pd


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: pd.DataFrame
    stats: Dict[str, Any]


def run_backtest(
    data: pd.DataFrame,
    signals: pd.Series,
    initial_capital: float = 10000.0,
    commission_rate: float = 0.001,
    max_hold_days: int = 60,
) -> BacktestResult:
    """
    Esegue un backtest molto semplice basato su segnali di ENTRATA (1) / no-signal (0).

    Regole:
    - Se non siamo in posizione e c'è segnale=1 in una data T,
      entriamo long all'OPEN del giorno T+1 (se esiste).
    - Manteniamo la posizione per al massimo `max_hold_days` giorni di trading.
    - Usciamo al CLOSE del giorno di uscita.
    - Niente stop dinamici per ora, solo tempo massimo.
    - Commissione: percentuale per lato su valore nozionale (open e close).
    """

    if "open" not in data.columns or "close" not in data.columns:
        raise ValueError("Il DataFrame dati deve contenere colonne 'open' e 'close'.")

    # Allineiamo signals a data
    data = data.sort_index()
    signals = signals.reindex(data.index).fillna(0).astype(int)

    equity_index = data.index
    equity_values = []
    capital = initial_capital

    trades_records = []

    in_position = False
    entry_time: Optional[pd.Timestamp] = None
    entry_price: Optional[float] = None
    capital_before_entry: Optional[float] = None
    hold_days = 0

    for i, current_time in enumerate(equity_index):
        price_open = float(data.loc[current_time, "open"])
        price_close = float(data.loc[current_time, "close"])

        # Gestione della posizione aperta
        if in_position:
            hold_days += 1

            is_last_bar = i == len(equity_index) - 1
            exit_now = False

            if hold_days >= max_hold_days:
                exit_now = True
            if is_last_bar:
                exit_now = True

            if exit_now and entry_time is not None and entry_price is not None and capital_before_entry is not None:
                # Round-trip commissione: entrata + uscita
                gross_return = (price_close - entry_price) / entry_price
                net_return = gross_return - (2 * commission_rate)
                pnl = capital_before_entry * net_return
                capital_after = capital_before_entry + pnl

                trades_records.append(
                    {
                        "entry_time": entry_time,
                        "exit_time": current_time,
                        "entry_price": entry_price,
                        "exit_price": price_close,
                        "gross_return": gross_return,
                        "net_return": net_return,
                        "pnl": pnl,
                        "capital_before": capital_before_entry,
                        "capital_after": capital_after,
                        "hold_days": hold_days,
                    }
                )

                capital = capital_after
                in_position = False
                entry_time = None
                entry_price = None
                capital_before_entry = None
                hold_days = 0

        # Possibile nuova entrata (solo se flat)
        if not in_position and signals.loc[current_time] == 1:
            # entriamo all'OPEN del giorno successivo, se esiste
            if i < len(equity_index) - 1:
                next_time = equity_index[i + 1]
                next_open = float(data.loc[next_time, "open"])
                entry_time = next_time
                entry_price = next_open
                capital_before_entry = capital
                in_position = True
                hold_days = 0

        equity_values.append(capital)

    equity_curve = pd.Series(equity_values, index=equity_index, name="equity")

    trades_df = pd.DataFrame(trades_records)
    trades_df = trades_df.sort_values("entry_time") if not trades_df.empty else trades_df

    stats: Dict[str, Any] = {
        "initial_capital": initial_capital,
        "final_capital": float(equity_curve.iloc[-1]),
        "total_return_pct": float((equity_curve.iloc[-1] / initial_capital - 1.0) * 100),
        "num_trades": int(len(trades_df)),
    }

    if len(trades_df) > 0:
        wins = trades_df[trades_df["net_return"] > 0]
        stats["win_rate_pct"] = float(len(wins) / len(trades_df) * 100)
        stats["avg_net_return_pct"] = float(trades_df["net_return"].mean() * 100)
        # Max drawdown semplice
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        stats["max_drawdown_pct"] = float(drawdown.min() * 100)
    else:
        stats["win_rate_pct"] = None
        stats["avg_net_return_pct"] = None
        stats["max_drawdown_pct"] = None

    return BacktestResult(equity_curve=equity_curve, trades=trades_df, stats=stats)


if __name__ == "__main__":
    # Mini pipeline completa: dati Kraken -> segnali Strategia 1 -> backtest -> report
    from trading_lab.data import load_btc_daily_csv
    from trading_lab.strategies.btc_trend_daily import BTCTrendDailyParams, generate_signals
    from trading_lab.metrics.report import print_basic_report

    df = load_btc_daily_csv()
    params = BTCTrendDailyParams()
    signals = generate_signals(df, params)

    result = run_backtest(df, signals, initial_capital=10000.0, commission_rate=0.001, max_hold_days=params.max_hold_days)
    print_basic_report(result)
