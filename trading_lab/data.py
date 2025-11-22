"""
Funzioni di caricamento dati per il Trading Lab.

Fase 0–1:
- useremo file storici locali (es. CSV BTCUSDT daily scaricati da Binance)
- nessuna chiamata API live in questo modulo.
"""

from pathlib import Path
from typing import Optional

import pandas as pd

from .config import DATA_DIR


def load_btc_daily_csv(filename: str = "BTCUSDT_daily.csv", data_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Carica dati daily di BTC da un file CSV locale.

    Atteso formato tipo Binance: timestamp/OPEN/HIGH/LOW/CLOSE/VOLUME (adatteremo in base al file reale).
    Per ora è solo uno scheletro: lo completeremo quando avremo il CSV reale.
    """
    base = Path(data_dir or DATA_DIR)
    path = base / filename
    if not path.exists():
        raise FileNotFoundError(f"Dati BTC daily non trovati in: {path}")

    # Placeholder: lettura grezza, il parsing reale dipenderà dalle colonne del CSV che scaricheremo.
    df = pd.read_csv(path)
    return df
