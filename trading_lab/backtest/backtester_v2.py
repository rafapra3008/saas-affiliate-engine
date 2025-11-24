"""Backtester v2 – gestione long/short per Strategia 2.

Questa versione è pensata per lavorare con:
- segnali di ingresso separati: signal_long (0/1), signal_short (0/1)
- una sola posizione aperta alla volta (long OPPURE short)
- stop-loss basato su ATR moltiplicato per un fattore
- chiusura forzata dopo max_hold_days barre

NOTA: questo modulo è indipendente dal backtester v1 (long-only) e
non modifica in alcun modo la logica esistente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
import pandas as pd


@dataclass
class TradeRecordV2:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    side: str  # "long" o "short"
    entry_price: float
    exit_price: float
    hold_bars: int
    gross_return_pct: float
    net_return_pct: float
    pnl: float
    exit_reason: str  # "stop", "max_hold", "end_of_data"


@dataclass
class BacktestV2Result:
    equity_curve: pd.Series
    trades: List[TradeRecordV2]
    stats: Dict[str, Any]


def _compute_atr(data: pd.DataFrame, window: int) -> pd.Series:
    """Calcola ATR (Average True Range) standard.

    Richiede colonne: high, low, close.
    """

    high = data["high"].astype(float)
    low = data["low"].astype(float)
    close = data["close"].astype(float)

    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window, min_periods=window).mean()
    return atr


def run_backtest_long_short(
    data: pd.DataFrame,
    signal_long: pd.Series,
    signal_short: pd.Series,
    *,
    initial_capital: float = 10_000.0,
    commission_rate: float = 0.001,
    atr_window: int = 14,
    atr_stop_multiple: float = 2.0,
    max_hold_days: int = 60,
) -> BacktestV2Result:
    """Esegue un backtest long/short con ATR stop e max_hold_days.

    Parametri principali:
    - data: DataFrame con colonne open, high, low, close (daily)
    - signal_long: Serie 0/1, 1 = tentativo di ingresso long
    - signal_short: Serie 0/1, 1 = tentativo di ingresso short

    Regole operative (semplificate):
    - al massimo UNA posizione aperta (long o short)
    - se flat e arriva un segnale long => entra long
    - se flat e arriva un segnale short => entra short
    - se entrambi i segnali sono 1 nello stesso giorno => si IGNORA (nessun ingresso)
    - stop-loss iniziale = entry_price ± atr_stop_multiple * ATR_entry
    - uscita per:
        * stop colpito (usando high/low della barra)
        * superamento max_hold_days barre
        * ultima barra del dataset

    Nota: questo backtest usa un sizing implicito con capitale interamente investito
    ad ogni trade. I risultati sono quindi più adatti a confronti relativi tra
    configurazioni che a stime assolute di PnL.
    """

    if not data.index.equals(signal_long.index) or not data.index.equals(signal_short.index):
        raise ValueError("Gli indici di data, signal_long e signal_short devono coincidere.")

    close = data["close"].astype(float)
    high = data["high"].astype(float)
    low = data["low"].astype(float)

    atr = _compute_atr(data, atr_window)

    equity_index = data.index
    equity = pd.Series(index=equity_index, dtype="float64")
    equity.iloc[0] = float(initial_capital)
    current_equity = float(initial_capital)

    trades: List[TradeRecordV2] = []

    in_position = False
    side = None  # "long" o "short"
    entry_price = 0.0
    entry_idx = None
    entry_time: pd.Timestamp | None = None
    stop_price = None

    index_list = list(data.index)

    for i, ts in enumerate(index_list):
        price_close = close.iloc[i]
        price_high = high.iloc[i]
        price_low = low.iloc[i]

        # Se non abbiamo ancora ATR sufficiente, nessuna operatività
        if pd.isna(atr.iloc[i]):
            equity.iloc[i] = current_equity
            continue

        if in_position:
            hold_bars = i - entry_idx + 1
            exit_signal = False
            exit_reason = None
            exit_price = price_close

            # Controllo stop
            if side == "long" and stop_price is not None and price_low <= stop_price:
                exit_signal = True
                exit_reason = "stop"
                exit_price = float(stop_price)
            elif side == "short" and stop_price is not None and price_high >= stop_price:
                exit_signal = True
                exit_reason = "stop"
                exit_price = float(stop_price)

            # Controllo max_hold_days (in barre)
            if not exit_signal and hold_bars > max_hold_days:
                exit_signal = True
                exit_reason = "max_hold"
                exit_price = price_close

            # Controllo fine dati
            is_last_bar = i == len(index_list) - 1
            if not exit_signal and is_last_bar:
                exit_signal = True
                exit_reason = "end_of_data"
                exit_price = price_close

            if exit_signal:
                if side == "long":
                    gross_ret_pct = (exit_price - entry_price) / entry_price
                elif side == "short":
                    gross_ret_pct = (entry_price - exit_price) / entry_price
                else:
                    gross_ret_pct = 0.0

                # Commissioni: approssimiamo a 2 * commission_rate per trade
                net_ret_pct = gross_ret_pct - 2.0 * commission_rate

                pnl = current_equity * net_ret_pct
                current_equity += pnl

                record = TradeRecordV2(
                    entry_time=entry_time,
                    exit_time=ts,
                    side=side or "",
                    entry_price=float(entry_price),
                    exit_price=float(exit_price),
                    hold_bars=int(hold_bars),
                    gross_return_pct=float(gross_ret_pct * 100.0),
                    net_return_pct=float(net_ret_pct * 100.0),
                    pnl=float(pnl),
                    exit_reason=exit_reason or "",
                )
                trades.append(record)

                in_position = False
                side = None
                entry_price = 0.0
                entry_idx = None
                entry_time = None
                stop_price = None

        # Se siamo flat dopo eventuale uscita, valutiamo nuovi ingressi
        if not in_position:
            long_sig = bool(signal_long.iloc[i])
            short_sig = bool(signal_short.iloc[i])

            # Se arrivano entrambi i segnali, per semplicità non entriamo
            if long_sig and not short_sig:
                in_position = True
                side = "long"
                entry_price = price_close
                entry_idx = i
                entry_time = ts
                stop_price = entry_price - atr_stop_multiple * float(atr.iloc[i])

            elif short_sig and not long_sig:
                in_position = True
                side = "short"
                entry_price = price_close
                entry_idx = i
                entry_time = ts
                stop_price = entry_price + atr_stop_multiple * float(atr.iloc[i])

        equity.iloc[i] = current_equity

    # Calcolo statistiche di base
    if len(trades) == 0:
        stats = {
            "num_trades": 0,
            "total_return_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "win_rate_pct": None,
            "avg_net_return_pct": None,
        }
    else:
        total_return_pct = (current_equity / initial_capital - 1.0) * 100.0

        eq = equity.ffill().fillna(initial_capital)
        peak = eq.cummax()
        dd = (eq - peak) / peak
        max_drawdown_pct = float(dd.min() * 100.0)

        net_returns = np.array([t.net_return_pct for t in trades])
        wins = net_returns[net_returns > 0]
        win_rate_pct = float(len(wins) / len(net_returns) * 100.0)
        avg_net_return_pct = float(net_returns.mean())

        stats = {
            "num_trades": len(trades),
            "total_return_pct": float(total_return_pct),
            "max_drawdown_pct": float(max_drawdown_pct),
            "win_rate_pct": win_rate_pct,
            "avg_net_return_pct": avg_net_return_pct,
        }

    return BacktestV2Result(equity_curve=equity.ffill(), trades=trades, stats=stats)
