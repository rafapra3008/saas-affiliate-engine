"""
Strategia 2 – BTC Daily Long/Short con filtro di regime.

Obiettivo concettuale (design, non ancora implementato):

- Identificare il regime di mercato BTCUSD (bull vs bear) usando una MA molto lunga
  e/o la posizione del prezzo rispetto ai massimi/minimi multi-anno.

- In regime BULL (mercato che tende a salire):
    - comportarsi in modo simile alla Strategia 1:
        - filtro di regime: prezzo sopra la MA lunga
        - segnali LONG su breakout sopra il massimo recente
        - gestione del rischio con stop ATR + max_hold_days

- In regime BEAR (mercato che tende a scendere):
    - opzione conservativa: stare FLAT (nessuna posizione)
    - opzione aggressiva (versione completa di Strategia 2):
        - filtro di regime: prezzo sotto la MA lunga
        - segnali SHORT su breakdown sotto il minimo recente
        - gestione del rischio con stop ATR sopra il prezzo + max_hold_days

- Obiettivo del laboratorio:
    - valutare se la combinazione long/short con filtro di regime
      produce un profilo rischio/rendimento più robusto rispetto
      alla sola Strategia 1 long-only.

NOTA IMPORTANTE:
- Questo file contiene solo la struttura e i parametri della Strategia 2.
- La logica di generazione segnali/posizioni sarà implementata in
  una fase successiva, dopo ulteriore ragionamento e test.
"""

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import pandas as pd

from ..data import load_btc_daily


@dataclass
class BTCTrendDailyV2Params:
    """Parametri di alto livello per la Strategia 2.

    Questa versione è solo la definizione dei parametri.
    I valori di default sono placeholder ragionevoli e
    potranno essere rivisti dopo i primi esperimenti.
    """

    # Filtro di regime (bull/bear)
    regime_ma_window: int = 200  # MA molto lunga per definire il regime
    regime_threshold_up: float = 0.0  # placeholder per eventuale offset (es. +x% sopra MA)
    regime_threshold_down: float = 0.0  # placeholder per offset sotto MA

    # Componenti LONG (in regime bull)
    long_ma_window: int = 200
    long_breakout_lookback: int = 40

    # Componenti SHORT (in regime bear)
    short_ma_window: int = 200
    short_breakdown_lookback: int = 40

    # Rischio / gestione posizione (comune a long e short)
    atr_window: int = 14
    atr_stop_multiple: float = 2.0
    max_hold_days: int = 60


def _ensure_params(params: BTCTrendDailyV2Params | Dict[str, Any]) -> BTCTrendDailyV2Params:
    if isinstance(params, BTCTrendDailyV2Params):
        return params
    if isinstance(params, dict):
        return BTCTrendDailyV2Params(**params)
    raise TypeError(f"Tipo params non supportato per Strategia 2: {type(params)}")


def compute_regime(
    data: pd.DataFrame, params: BTCTrendDailyV2Params | Dict[str, Any]
) -> pd.Series:
    """Calcola il regime di mercato (bull/bear) usando una MA lunga.

    Regola attuale (semplice, ma espandibile):
    - calcola una media mobile a `regime_ma_window` sul close
    - definisci due livelli:
        up_level   = MA * (1 + regime_threshold_up)
        down_level = MA * (1 + regime_threshold_down)
    - regime = +1 (bull) se close > up_level
      regime = -1 (bear) se close < down_level
      regime =  0 altrimenti (zona neutra)

    Nota: threshold_up / threshold_down sono pensati come offset percentuali
    (es. +0.02 = +2% sopra MA). Per ora i default sono 0, quindi il criterio
    si riduce a close rispetto alla MA pura.
    """

    p = _ensure_params(params)

    close = data["close"].astype(float)
    ma = close.rolling(window=p.regime_ma_window, min_periods=p.regime_ma_window).mean()

    up_level = ma * (1 + float(p.regime_threshold_up))
    down_level = ma * (1 + float(p.regime_threshold_down))

    regime = pd.Series(0, index=data.index, dtype="int8")
    regime[close > up_level] = 1
    regime[close < down_level] = -1

    return regime


def generate_signals_v2(
    data: pd.DataFrame, params: BTCTrendDailyV2Params | Dict[str, Any]
) -> Tuple[pd.Series, pd.Series]:
    """Genera segnali long e short per la Strategia 2.

    OUTPUT ATTESO (quando sarà implementata):
    - signal_long: Serie 0/1, 1 = proposta di ingresso LONG in quella data
    - signal_short: Serie 0/1, 1 = proposta di ingresso SHORT in quella data

    Regole attuali (versione iniziale):
    - calcolo del regime (bull/bear) via [compute_regime](cci:1://file:///Users/rafapra/Downloads/Windsurf/saas_affiliate_engine/trading_lab/strategies/btc_trend_daily_v2.py:76:0-107:17)
    - segnali long solo in bull regime, con breakout verso l'alto
      rispetto al massimo recente
    - segnali short solo in bear regime, con breakdown verso il basso
      rispetto al minimo recente

    Nota: questa funzione genera solo le Serie di segnali di ingresso
    (0/1). L'integrazione con il backtester e la gestione operativa
    (ATR stop, max_hold_days, ecc.) è delegata ad altri moduli.
    """

    p = _ensure_params(params)

    close = data["close"].astype(float)

    # Regime bull/bear
    regime = compute_regime(data, p)

    # Componenti LONG (in regime bull)
    long_ma = close.rolling(
        window=p.long_ma_window,
        min_periods=p.long_ma_window,
    ).mean()
    long_high = close.rolling(
        window=p.long_breakout_lookback,
        min_periods=p.long_breakout_lookback,
    ).max()

    # breakout rispetto al massimo recente (escludendo la barra corrente)
    long_breakout_level = long_high.shift(1)

    signal_long = (
        (regime == 1)
        & (close > long_ma)
        & (long_breakout_level.notna())
        & (close > long_breakout_level)
    )

    # Componenti SHORT (in regime bear)
    short_ma = close.rolling(
        window=p.short_ma_window,
        min_periods=p.short_ma_window,
    ).mean()
    short_low = close.rolling(
        window=p.short_breakdown_lookback,
        min_periods=p.short_breakdown_lookback,
    ).min()

    # breakdown rispetto al minimo recente (escludendo la barra corrente)
    short_breakdown_level = short_low.shift(1)

    signal_short = (
        (regime == -1)
        & (close < short_ma)
        & (short_breakdown_level.notna())
        & (close < short_breakdown_level)
    )

    # Cast esplicito a int8 (0/1)
    signal_long = signal_long.astype("int8")
    signal_short = signal_short.astype("int8")

    return signal_long, signal_short


if __name__ == "__main__":
    # Placeholder di test manuale: carica dati e mostra solo informazioni di base.
    df = load_btc_daily()
    params = BTCTrendDailyV2Params()
    regime = compute_regime(df, params)

    regime_ma = df["close"].astype(float).rolling(
        window=params.regime_ma_window, min_periods=params.regime_ma_window
    ).mean()

    preview = pd.DataFrame(
        {
            "close": df["close"],
            "regime_ma": regime_ma,
            "regime": regime,
        }
    ).tail(10)

    print("[STRAT_V2] Parametri iniziali:", params)
    print("[STRAT_V2] Ultime 10 righe con regime bull/bear:")
    print(preview)
    # Statistiche semplici sul regime su tutto il periodo
    regime_counts = regime.value_counts().sort_index()
    label_map = {-1: "bear", 0: "neutro", 1: "bull"}

    print("[STRAT_V2] Giorni per regime (tutto il periodo):")
    for k, v in regime_counts.items():
        label = label_map.get(int(k), str(k))
        print(f"  regime={int(k):2d} ({label:6s}): {int(v)} giorni")

    # Statistiche annuali del regime
    df_regime = pd.DataFrame({"regime": regime})
    df_regime["year"] = df_regime.index.year

    yearly = pd.crosstab(df_regime["year"], df_regime["regime"]).astype(int)

    print("[STRAT_V2] Giorni per regime per anno:")
    print(yearly)

    # Generazione segnali long/short (versione iniziale)
    signal_long, signal_short = generate_signals_v2(df, params)
    print("[STRAT_V2] Num segnali LONG:", int(signal_long.sum()))
    print("[STRAT_V2] Num segnali SHORT:", int(signal_short.sum()))

    signals_preview = pd.DataFrame(
        {
            "regime": regime,
            "signal_long": signal_long,
            "signal_short": signal_short,
        }
    ).tail(10)

    print("[STRAT_V2] Ultime 10 righe con segnali:")
    print(signals_preview)
