"""
Funzioni di caricamento dati per il Trading Lab.

1) Kraken OHLC (BTCUSD daily) via API pubblica
2) CSV esterno multi-anno intraday stile Binance, aggregato a daily
"""

from pathlib import Path
from typing import Optional, Tuple, List

import pandas as pd
import requests

from .config import DATA_DIR


KRAKEN_OHLC_URL = "https://api.kraken.com/0/public/OHLC"


# ----------------------------------------------------------------------
# Sorgente 1: Kraken (daily limitato)
# ----------------------------------------------------------------------


def _fetch_kraken_ohlc_chunk(
    interval_minutes: int = 1440,
    since: Optional[int] = None,
) -> Tuple[pd.DataFrame, Optional[int]]:
    params = {
        "pair": "XXBTZUSD",
        "interval": interval_minutes,
    }
    if since is not None:
        params["since"] = since

    resp = requests.get(KRAKEN_OHLC_URL, params=params, timeout=30)
    resp.raise_for_status()
    raw = resp.json()

    if raw.get("error"):
        raise RuntimeError(f"Errore Kraken OHLC: {raw['error']}")

    result = raw.get("result", {})
    pair_keys = [k for k in result.keys() if k != "last"]
    if not pair_keys:
        raise RuntimeError(f"Nessun dato OHLC trovato nella risposta Kraken: {result.keys()}")
    pair_key = pair_keys[0]
    rows = result[pair_key]
    last = result.get("last")

    df = pd.DataFrame(
        rows,
        columns=["time", "open", "high", "low", "close", "vwap", "volume", "count"],
    )

    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    for col in ["open", "high", "low", "close", "vwap", "volume"]:
        df[col] = df[col].astype(float)
    df["count"] = df["count"].astype(int)

    return df, int(last) if last is not None else None


def download_btcusd_daily_csv(
    filename: str = "BTCUSD_daily_kraken.csv",
    interval_minutes: int = 1440,
    data_dir: Optional[str] = None,
    full_history: bool = False,
    max_loops: int = 20,
) -> Path:
    base = Path(data_dir or DATA_DIR)
    base.mkdir(parents=True, exist_ok=True)
    path = base / filename

    if not full_history:
        df, _ = _fetch_kraken_ohlc_chunk(interval_minutes=interval_minutes)
        df = df.set_index("time").sort_index()
        df.to_csv(path)
        print(f"[DATA] Scaricate {len(df)} candele daily BTCUSD da Kraken in {path}")
        return path

    all_chunks: List[pd.DataFrame] = []
    since: Optional[int] = None
    last_seen: Optional[int] = None

    for loop_idx in range(max_loops):
        df_chunk, new_last = _fetch_kraken_ohlc_chunk(interval_minutes=interval_minutes, since=since)
        if df_chunk.empty:
            print(f"[DATA] Chunk {loop_idx} vuoto, mi fermo.")
            break

        all_chunks.append(df_chunk)
        print(f"[DATA] Chunk {loop_idx} – righe: {len(df_chunk)}, last={new_last}")

        if new_last is None or new_last == last_seen:
            print("[DATA] Nessun avanzamento di 'last', mi fermo.")
            break

        last_seen = new_last
        since = new_last

    if not all_chunks:
        raise RuntimeError("Nessun dato scaricato in modalità full_history da Kraken.")

    df_all = pd.concat(all_chunks, ignore_index=True)
    df_all = df_all.drop_duplicates(subset=["time"]).set_index("time").sort_index()

    df_all.to_csv(path)
    print(f"[DATA] Scaricate {len(df_all)} candele daily BTCUSD (full_history) in {path}")
    return path


def load_btc_daily_kraken(
    filename: str = "BTCUSD_daily_kraken.csv",
    data_dir: Optional[str] = None,
) -> pd.DataFrame:
    base = Path(data_dir or DATA_DIR)
    path = base / filename
    if not path.exists():
        print(f"[DATA] File {path} non trovato, scarico da Kraken (finestra recente)...")
        download_btcusd_daily_csv(filename=filename, data_dir=data_dir, full_history=False)

    df = pd.read_csv(path, index_col="time", parse_dates=["time"])
    return df


# ----------------------------------------------------------------------
# Sorgente 2: CSV esterno intraday aggregato a daily
# ----------------------------------------------------------------------


def load_btc_external_daily_csv(
    filename: str = "BTCUSD_daily_external.csv",
    data_dir: Optional[str] = None,
) -> pd.DataFrame:
    """
    Carica dati BTCUSD da CSV intraday stile Binance e li aggrega a daily.

    Header atteso:
    Open time,Open,High,Low,Close,Volume,Close time,...

    Restituisce DataFrame daily con indice datetime (UTC) e colonne:
    open, high, low, close, volume.
    """
    base = Path(data_dir or DATA_DIR)
    path = base / filename
    if not path.exists():
        raise FileNotFoundError(f"CSV esterno non trovato in: {path}")

    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    if "Open time" not in df.columns:
        raise ValueError(f"Colonna 'Open time' mancante nel CSV: colonne={df.columns}")

    df["Open time"] = df["Open time"].astype(str).str.strip()
    df = df[df["Open time"].notna()]
    df["Open time"] = pd.to_datetime(df["Open time"], utc=True, errors="coerce")
    df = df[df["Open time"].notna()]

    rename_map = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    for k in rename_map:
        if k not in df.columns:
            raise ValueError(f"Colonna '{k}' mancante nel CSV esterno.")

    df = df.rename(columns=rename_map)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    # Aggregazione a daily: usiamo la data (UTC) di 'Open time'
    df["date"] = df["Open time"].dt.floor("D")
    grouped = df.groupby("date")

    df_daily = grouped.agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    ).sort_index()

    df_daily.index = pd.to_datetime(df_daily.index, utc=True)
    df_daily.index.name = "time"

    return df_daily


def load_btc_daily() -> pd.DataFrame:
    """
    Loader principale per gli esperimenti.

    - Se il CSV esterno multi-anno è presente, usa quello (aggregato a daily).
    - Altrimenti ripiega sui dati Kraken disponibili.
    """
    base = Path(DATA_DIR)
    external_path = base / "BTCUSD_daily_external.csv"
    if external_path.exists():
        print("[DATA] Uso CSV esterno BTCUSD_daily_external.csv (aggregato a daily)")
        return load_btc_external_daily_csv()

    print("[DATA] CSV esterno non trovato, uso dati Kraken.")
    return load_btc_daily_kraken()


if __name__ == "__main__":
    df_ext = load_btc_daily()
    print(df_ext.head())
    print(df_ext.tail())
    print(f"[DATA] Righe totali (daily): {len(df_ext)}")
