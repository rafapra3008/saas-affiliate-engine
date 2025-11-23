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


def generate_signals_v2(
    data: pd.DataFrame, params: BTCTrendDailyV2Params | Dict[str, Any]
) -> Tuple[pd.Series, pd.Series]:
    """Genera segnali long e short per la Strategia 2.

    OUTPUT ATTESO (quando sarà implementata):
    - signal_long: Serie 0/1, 1 = proposta di ingresso LONG in quella data
    - signal_short: Serie 0/1, 1 = proposta di ingresso SHORT in quella data

    Regole previste (da implementare):
    - calcolo del regime (bull/bear) via MA lunga e soglie
    - segnali long solo in bull regime, con breakout verso l'alto
    - segnali short solo in bear regime, con breakdown verso il basso

    Al momento questa funzione non è implementata: serve solo
    come placeholder per fissare l'interfaccia.
    """
    _ = _ensure_params(params)
    raise NotImplementedError("Strategia 2 (generate_signals_v2) non è ancora implementata.")


if __name__ == "__main__":
    # Placeholder di test manuale: carica dati e mostra solo informazioni di base.
    df = load_btc_daily()
    print(df.tail())

    params = BTCTrendDailyV2Params()
    print("[STRAT_V2] Parametri iniziali:", params)
    print("[STRAT_V2] La generazione dei segnali non è ancora implementata.")
