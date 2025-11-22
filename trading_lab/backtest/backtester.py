"""
Backtester generico (scheletro).

In Fase 0–1:
- prenderà dati OHLCV,
- segnali long/flat,
- simulerà trade con commissioni,
- calcolerà equity curve e drawdown.

Per ora contiene solo la firma della funzione principale.
"""

from dataclasses import dataclass
from typing import Dict, Any

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
) -> BacktestResult:
    """
    Placeholder del motore di backtest.

    Implementeremo la logica solo dopo aver fissato esattamente
    il formato di `data` e `signals`.
    """
    raise NotImplementedError("Backtester non ancora implementato.")
