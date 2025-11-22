"""
Strategia 1 – BTC Daily Long-Only (baseline).

Questo modulo conterrà:
- definizione dei parametri della strategia
- funzione generate_signals(data, params)

Per ora è solo uno scheletro (nessuna logica implementata).
"""

from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd


@dataclass
class BTCTrendDailyParams:
    ma_long_window: int = 150
    breakout_lookback: int = 20
    atr_window: int = 14
    atr_stop_multiple: float = 2.0
    atr_take_multiple: float = 3.0
    max_hold_days: int = 60


def generate_signals(data: pd.DataFrame, params: BTCTrendDailyParams | Dict[str, Any]) -> pd.Series:
    """
    Placeholder: genererà i segnali long/flat per la strategia 1.

    Per ora solleva NotImplementedError per ricordarci che va implementata
    solo dopo aver definito con precisione il formato dei dati e le regole.
    """
    raise NotImplementedError("Strategia BTCTrendDaily non ancora implementata.")
