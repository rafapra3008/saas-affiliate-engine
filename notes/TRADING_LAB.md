# Trading Lab – Fase 0–1 (design, nessun soldo reale)

## Missione

Costruire e far operare un sistema di trading sempre attivo, disciplinato, antifragile, che:
- massimizza la correttezza decisionale,
- minimizza il rischio,
- persegue rendimenti composti stabili nel tempo,

con questa gerarchia:

1. Non perdere soldi.
2. Poi guadagnare soldi.
3. Solo dopo usare Machine Learning per ottimizzare strategie e miglioramenti costanti.

Obiettivo mentale a lungo termine: progressi verso massimo profit/giorno in modo realistico e responsabile.

---

## Principi di base

- **Sistematico, non discrezionale**: ogni decisione deve essere descrivibile come regola di codice.
- **Gestione del rischio prima del profitto**:
  - limite di rischio per trade,
  - limite di drawdown per strategia,
  - limite di perdita totale (sistema spento se superato).
- **Antifragilità**:
  - sistema progettato per sopravvivere a fasi di mercato difficili,
  - preferenza per strategie che degradano lentamente, non che esplodono.
- **Ricerca di edge, non copia-incolla**:
  - evitare le strategie “troppo ovvie” senza filtri (es. MA crossover grezzo),
  - lavorare su filtri di regime, volatilità, struttura del mercato.
- **Tutto tracciato**:
  - log completo di segnali, trade, PnL simulato,
  - possibilità di analizzare ex post dove e perché il sistema ha guadagnato/perso.

---

## Vincoli Fase 0–1 (laboratorio)

- **Nessun trade reale**:
  - solo backtest su dati storici,
  - solo paper-trading su dati live.
- **Capitale mentale di riferimento (per il futuro)**:
  - envelope iniziale: fino a 2.000–5.000 €,
  - ma usato solo se le fasi laboratorio mostrano edge stabile.
- **Rischio per trade (quando andremo sul reale)**:
  - target: 0.25–0.5% del capitale per posizione.
- **Drawdown massimo accettabile (per strategia)**:
  - se DD massimo supera una soglia (es. 10–15%), la strategia viene sospesa e rivalutata.

---

## Scelte iniziali del campo di gioco

### Mercato

- **Mercato principale Fase 0–1**: BTC spot (BTC-USD / BTC-USDT).
- Motivi:
  - 24/7, alta liquidità, lunga storia,
  - facile accesso a dati storici,
  - possibilità di partire **solo long spot** (niente leva, niente derivati).

Nota sugli exchange e API:
- in Fase 0–1 useremo **principalmente dati storici offline** (es. data dump / CSV),
- accesso alle API in tempo reale verrà progettato con attenzione a:
  - limiti di rate (rate limit),
  - possibili block IP sulle VM,
  - uso di pochi endpoint stabili (no polling folle).
- La scelta dell’exchange operativo (Binance, Coinbase, Kraken, ecc.) verrà fissata SOLO dopo la fase di ricerca e dopo aver valutato costi, affidabilità, limiti IP.

### Timeframe

- **Timeframe principale Fase 0–1**: daily (1D).
- Motivazioni:
  - meno rumore, meno impatto di spread e fee,
  - meno trade → più facile analizzare ogni decisione,
  - compatibile con l’idea di “anche 1 trade a settimana”, ma con la possibilità di cogliere opportunità quando emergono.

In futuro, quando la pipeline sarà robusta, potranno essere aggiunti timeframe 4H / 1H, ma non prima.

---

## Architettura concettuale del sistema

Moduli logici:

1. **Data Layer (`data/`)**
   - Download e update dei dati OHLCV BTC daily.
   - Normalizzazione (timezone, missing data, split, ecc.).
   - Cache locale (file CSV/Parquet) per evitare chiamate ripetute alle API.

2. **Strategy Layer (`strategies/`)**
   - Collezione di strategie candidate, ognuna con:
     - funzione `generate_signals(data)` → segnali long/flat (per ora),
     - parametri espliciti (niente magia nascosta),
     - regole di ingresso/uscita chiare.

3. **Execution Simulator / Backtester (`backtest/`)**
   - Simula l’applicazione delle strategie ai dati storici:
     - commissioni realistiche,
     - eventuale slippage,
     - ribilanciamento del capitale,
     - gestione di multiple strategie (in futuro).

4. **Metrics & Analytics (`metrics/`)**
   - KPI principali:
     - equity curve,
     - max drawdown,
     - profit factor,
     - percentuale trade vincenti,
     - distribution PnL per trade / per mese.
   - Report leggibili (testo + grafici, in futuro).

5. **Paper-Trading Engine (`paper_engine/`)**
   - Applica in tempo quasi-reale le stesse regole sui dati live,
   - nessun ordine reale inviato all’exchange,
   - log di:
     - segnali,
     - “trade virtuali”,
     - PnL simulato.

---

## Famiglie di strategie da esplorare in Fase 0–1

Obiettivo: evitare di essere “ancora un bot MA crossover” e cercare un edge reale.

1. **Trend-following daily semplificato**
   - Idee:
     - trend filter (es. prezzo sopra media lunga / regime risk-on),
     - ingressi su breakout di range o ritorno verso la media dopo pullback.
   - Solo long spot, con stop-loss legati a volatilità.

2. **Breakout di volatilità / range**
   - Identificare giorni/zone in cui BTC esce da un range compresso,
   - evitare i falsi breakout con filtri di volume / volatilità.

3. **Filtri di regime di mercato**
   - Separare almeno:
     - fasi trend-up,
     - fasi range/alta volatilità,
   - applicare strategie diverse o ridurre size nei regimi peggiori.

Tutto questo SEMPRE con backtest + analisi statistica, non a sentimento.

---

## Protocollo di esperimento (Fase 0–1)

Per ogni strategia candidata:

1. **Definizione chiara**
   - regole di ingresso/uscita,
   - parametri espliciti,
   - ipotesi sul perché dovrebbe avere edge.

2. **Backtest su storico**
   - periodo di test chiaro (es. ultimi N anni),
   - split tra:
     - periodo di sviluppo (in-sample),
     - periodo di valutazione (out-of-sample),
   - controllo del rischio:
     - drawdown massimo,
     - numero trade,
     - PnL per trade.

3. **Test di robustezza**
   - piccoli cambi dei parametri,
   - variare leggermente i costi di transazione,
   - controllare che la strategia non collassi appena esce dai parametri “perfetti”.

4. **Paper-trading**
   - se supera i test:
     - attivazione in paper-trading live (nessun ordine reale),
     - monitoraggio per almeno alcune settimane.

5. **Decisione**
   - Se dopo paper-trading:
     - l’equity curve è coerente con quella del backtest,
     - il rischio è sotto controllo,
   - allora la strategia viene marcata come “CANDIDATA PER REAL MONEY” (fase successiva).
   - In caso contrario → archivio come esperimento fallito (ma documentato).

---

## Cosa NON facciamo (esplicitamente)

- Nessun trading discrezionale guidato da emozioni.
- Nessun uso di leva o derivati in Fase 0–1.
- Nessun “martingale”, nessun raddoppio dopo le perdite.
- Nessuna strategia che non possiamo spiegare a parole semplici.

---

## Next Steps (da discutere)

1. Scegliere il provider di dati storici per BTC daily:
   - data dump pubblico (es. Binance, altri),
   - o API con caching locale per evitare problemi di IP/block.
2. Definire la **prima strategia concreta**:
   - probabilmente un trend-following daily long-only con filtro di regime.
3. Implementare il primo scheletro di codice del Trading Lab in un progetto dedicato (separato dal motore affiliate) o in una sottocartella di questo repo.

