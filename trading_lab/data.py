"""
Funzioni di caricamento dati per il Trading Lab.

Fase 0–1:
- usiamo dati storici BTCUSD daily dall'endpoint pubblico di Kraken,
- niente chiavi API, una sola richiesta HTTP,
- salviamo i dati in CSV locale per riutilizzarli senza stressare l'API.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from .config import DATA_DIR


KRAKEN_OHLC_URL = "https://api.kraken.com/0/public/OHLC"


def download_btcusd_daily_csv(
    filename: str = "BTCUSD_daily_kraken.csv",
    interval_minutes: int = 1440,
    data_dir: Optional[str] = None,
) -> Path:
    """
    Scarica candele daily BTCUSD da Kraken (endpoint pubblico) e le salva in CSV.

    Kraken OHLC:
    - pair: XXBTZUSD
    - interval: 1440 (minuti) = 1 giorno
    """
    base = Path(data_dir or DATA_DIR)
    base.mkdir(parents=True, exist_ok=True)
    path = base / filename

    params = {
        "pair": "XXBTZUSD",
        "interval": interval_minutes,
    }
    resp = requests.get(KRAKEN_OHLC_URL, params=params, timeout=30)
    resp.raise_for_status()
    raw = resp.json()

    if raw.get("error"):
        raise RuntimeError(f"Errore Kraken OHLC: {raw['error']}")

    result = raw.get("result", {})
    # La chiave del pair è qualcosa tipo "XXBTZUSD"
    pair_keys = [k for k in result.keys() if k != "last"]
    if not pair_keys:
        raise RuntimeError(f"Nessun dato OHLC trovato nella risposta Kraken: {result.keys()}")
    pair_key = pair_keys[0]
    rows = result[pair_key]

    # Struttura OHLC Kraken:
    # [time, open, high, low, close, vwap, volume, count]
    df = pd.DataFrame(
        rows,
        columns=["time", "open", "high", "low", "close", "vwap", "volume", "count"],
    )

    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    for col in ["open", "high", "low", "close", "vwap", "volume"]:
        df[col] = df[col].astype(float)
    df["count"] = df["count"].astype(int)

    df = df.set_index("time").sort_index()

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path)
    print(f"[DATA] Scaricate {len(df)} candele daily BTCUSD da Kraken in {path}")
    return path


def load_btc_daily_csv(
    filename: str = "BTCUSD_daily_kraken.csv",
    data_dir: Optional[str] = None,
) -> pd.DataFrame:
    """
    Carica dati BTC daily da CSV locale.
    Se il file non esiste, lo scarica automaticamente da Kraken prima.
    """
    base = Path(data_dir or DATA_DIR)
    path = base / filename
    if not path.exists():
        print(f"[DATA] File {path} non trovato, scarico da Kraken...")
        download_btcusd_daily_csv(filename=filename, data_dir=data_dir)

    df = pd.read_csv(path, index_col="time", parse_dates=["time"])
    return df


if __name__ == "__main__":
    df = load_btc_daily_csv()
    print(df.head())
    print(f"[DATA] Righe totali: {len(df)}")
