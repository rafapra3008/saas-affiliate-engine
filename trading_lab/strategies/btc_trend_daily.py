"""
Strategia 1 – BTC Daily Long-Only (baseline).

Per ora:
- calcoliamo una media mobile lunga
- usiamo un breakout di massimo recente
- generiamo una Serie di segnali (1 = segnale long, 0 = nessun segnale)

La gestione della posizione completa (hold/exit) verrà fatta dal backtester.
"""

from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd

from ..data import load_btc_daily_csv


@dataclass
class BTCTrendDailyParams:
    ma_long_window: int = 150
    breakout_lookback: int = 20
    atr_window: int = 14  # non ancora usato
    atr_stop_multiple: float = 2.0  # non ancora usato
    atr_take_multiple: float = 3.0  # non ancora usato
    max_hold_days: int = 60  # non ancora usato


def _ensure_params(params: BTCTrendDailyParams | Dict[str, Any]) -> BTCTrendDailyParams:
    if isinstance(params, BTCTrendDailyParams):
        return params
    if isinstance(params, dict):
        return BTCTrendDailyParams(**params)
    raise TypeError(f"Tipo params non supportato: {type(params)}")


def generate_signals(data: pd.DataFrame, params: BTCTrendDailyParams | Dict[str, Any]) -> pd.Series:
    """
    Genera una Serie di segnali long (1) / no-signal (0) basata su:

    - filtro di regime: close > MA lunga
    - ingresso: breakout sopra il massimo degli ultimi N giorni (escluso il giorno corrente)

    NOTA:
    - questa funzione NON gestisce ancora stop o take profit,
      restituisce solo i punti di ingresso suggeriti.
    """
    p = _ensure_params(params)

    if "close" not in data.columns:
        raise ValueError("Il DataFrame deve contenere una colonna 'close'.")

    close = data["close"].astype(float)

    ma_long = close.rolling(p.ma_long_window, min_periods=p.ma_long_window).mean()
    regime = close > ma_long

    # Breakout del massimo recente (escludendo la barra corrente)
    recent_high = close.rolling(p.breakout_lookback, min_periods=p.breakout_lookback).max().shift(1)

    entry_long = regime & (close > recent_high)

    signals = entry_long.astype(int)
    signals.name = "signal_long"

    return signals


if __name__ == "__main__":
    # Mini test manuale: carica dati da Kraken, calcola segnali, stampa riassunto
    df = load_btc_daily_csv()
    print(df.tail())

    params = BTCTrendDailyParams()
    signals = generate_signals(df, params)

    total_signals = int(signals.sum())
    print(f"[STRAT] Segnali long totali: {total_signals}")
    print("[STRAT] Ultimi 10 segnali non-zero:")
    print(signals[signals != 0].tail(10))
