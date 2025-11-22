"""
Backtester generico (con stop basato su ATR, prima versione).

Assunzioni Fase 0–1:
- dati: DataFrame con almeno colonne 'open', 'high', 'low', 'close', indice datetime (daily).
- signals: Serie con 0/1 (1 = segnale di ingresso long quel giorno).
- Solo una posizione alla volta (long-only, no leva).

Regole:
- Entrata: al prezzo di OPEN del giorno successivo al segnale (se esiste).
- Stop-loss: prezzo di entrata - (atr_stop_multiple * ATR) calcolato sul giorno di entrata.
- Uscita:
  - se il minimo della candela scende sotto lo stop → si esce a stop,
  - oppure dopo max_hold_days al prezzo di CLOSE,
  - oppure sull’ultima barra disponibile.
- Commissioni: percentuale per lato su entrata e uscita.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

import pandas as pd


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: pd.DataFrame
    stats: Dict[str, Any]


def _compute_atr(data: pd.DataFrame, window: int) -> pd.Series:
    """
    Calcola un ATR semplice (media mobile del True Range).
    """
    high = data["high"].astype(float)
    low = data["low"].astype(float)
    close = data["close"].astype(float)

    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window, min_periods=window).mean()
    atr.name = "atr"
    return atr


def run_backtest(
    data: pd.DataFrame,
    signals: pd.Series,
    initial_capital: float = 10000.0,
    commission_rate: float = 0.001,
    max_hold_days: int = 60,
    atr_window: Optional[int] = None,
    atr_stop_multiple: Optional[float] = None,
) -> BacktestResult:
    """
    Esegue un backtest basato su segnali di ENTRATA (1) / no-signal (0),
    con possibilità di stop-loss basato su ATR.

    Regole:
    - Se non siamo in posizione e c'è segnale=1 a data T,
      entriamo long all'OPEN di T+1 (se esiste).
    - Stop iniziale (se configurato): entry_price - atr_stop_multiple * ATR(T+1).
    - Durante la posizione:
      - se il LOW della barra corrente scende sotto lo stop → chiusura a stop,
      - altrimenti, se superiamo max_hold_days o è l'ultima barra → chiusura a CLOSE.
    """

    required_cols = {"open", "high", "low", "close"}
    if not required_cols.issubset(set(data.columns)):
        raise ValueError(f"Il DataFrame dati deve contenere le colonne: {required_cols}")

    data = data.sort_index()
    signals = signals.reindex(data.index).fillna(0).astype(int)

    equity_index = data.index
    equity_values = []
    capital = initial_capital

    # ATR opzionale
    atr: Optional[pd.Series] = None
    if atr_window is not None and atr_window > 0:
        atr = _compute_atr(data, atr_window)

    trades_records = []

    in_position = False
    entry_time: Optional[pd.Timestamp] = None
    entry_price: Optional[float] = None
    capital_before_entry: Optional[float] = None
    entry_stop_price: Optional[float] = None
    hold_days = 0

    for i, current_time in enumerate(equity_index):
        price_open = float(data.loc[current_time, "open"])
        price_close = float(data.loc[current_time, "close"])

        # Gestione posizione aperta
        if in_position:
            hold_days += 1
            is_last_bar = i == len(equity_index) - 1

            hit_stop = False
            stop_exit_price: Optional[float] = None

            if entry_stop_price is not None:
                low_price = float(data.loc[current_time, "low"])
                if low_price <= entry_stop_price:
                    hit_stop = True
                    stop_exit_price = entry_stop_price

            time_exit = hold_days >= max_hold_days or is_last_bar

            if (hit_stop or time_exit) and entry_time is not None and entry_price is not None and capital_before_entry is not None:
                exit_price = stop_exit_price if hit_stop else price_close

                gross_return = (exit_price - entry_price) / entry_price
                net_return = gross_return - (2 * commission_rate)
                pnl = capital_before_entry * net_return
                capital_after = capital_before_entry + pnl

                trades_records.append(
                    {
                        "entry_time": entry_time,
                        "exit_time": current_time,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "stop_price": entry_stop_price,
                        "gross_return": gross_return,
                        "net_return": net_return,
                        "pnl": pnl,
                        "capital_before": capital_before_entry,
                        "capital_after": capital_after,
                        "hold_days": hold_days,
                        "exit_reason": "stop" if hit_stop else "time_or_last",
                    }
                )

                capital = capital_after
                in_position = False
                entry_time = None
                entry_price = None
                capital_before_entry = None
                entry_stop_price = None
                hold_days = 0

        # Possibile nuova entrata (solo se flat)
        if not in_position and signals.loc[current_time] == 1:
            if i < len(equity_index) - 1:
                next_time = equity_index[i + 1]
                next_open = float(data.loc[next_time, "open"])
                entry_time = next_time
                entry_price = next_open
                capital_before_entry = capital
                in_position = True
                hold_days = 0

                # Calcolo stop iniziale basato su ATR (se disponibile)
                entry_stop_price = None
                if atr is not None and atr_stop_multiple is not None and atr_stop_multiple > 0:
                    atr_val = float(atr.loc[next_time]) if pd.notna(atr.loc[next_time]) else None
                    if atr_val is not None:
                        entry_stop_price = entry_price - atr_stop_multiple * atr_val

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

        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        stats["max_drawdown_pct"] = float(drawdown.min() * 100)
    else:
        stats["win_rate_pct"] = None
        stats["avg_net_return_pct"] = None
        stats["max_drawdown_pct"] = None

    return BacktestResult(equity_curve=equity_curve, trades=trades_df, stats=stats)


if __name__ == "__main__":
    from trading_lab.data import load_btc_daily_csv
    from trading_lab.strategies.btc_trend_daily import BTCTrendDailyParams, generate_signals
    from trading_lab.metrics.report import print_basic_report

    df = load_btc_daily_csv()
    params = BTCTrendDailyParams()
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
    print_basic_report(result)
