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


---

## Piano dati ed exchange (Fase 0–1)

- Exchange target FUTURO per trading reale:
  - **Kraken**, mercato spot BTC (nessun derivato, nessuna leva).
  - Motivazioni: exchange regolato, reputazione solida, preparazione IPO, focus su sicurezza.

- Fonte dati storici per il laboratorio (backtest):
  - **Dati Binance BTCUSDT daily** (candele giornaliere) scaricati come file (CSV/ZIP) via HTTP.
  - Utilizzo SOLO offline:
    - i file vengono scaricati una volta,
    - salvati localmente,
    - il codice del lab legge solo da disco.
  - Nessun uso di chiavi API o polling continuo → nessun rischio di block IP per la VM.

- Strategia di coerenza:
  - Il lab cerca edge sul comportamento generale di BTC usando dati Binance.
  - Prima di passare a soldi veri su Kraken, la strategia verrà ri-testata su dati Kraken (quando disponibili) per verificare che l’edge non dipenda da dettagli specifici dell’exchange.


---

## Strategia 1 – BTC Daily Long-Only (baseline)

Obiettivo: avere una strategia semplice, spiegabile, da usare come baseline di confronto per esperimenti futuri (edge più avanzati).  
Non è l’obiettivo finale, ma il “controllo”.

### Universo

- Strumento: BTCUSDT (o BTCUSD) spot.
- Timeframe: candele daily (1D).
- Operatività: **solo long**, nessuno short, nessuna leva.

### Regole (bozza ad alto livello)

1. **Filtro di regime (trend filter)**
   - Calcoliamo una media mobile lunga (es. MA 100 o 150 giorni).
   - Regime “attivo” solo se:
     - prezzo di chiusura > MA lunga
     - e volatilità non è eccessiva (es. ATR su N giorni sotto una soglia relativa).

2. **Segnali di ingresso**
   - Possibili varianti (da testare):
     - **Breakout di massimo recente**: entra long se il close rompe il massimo degli ultimi M giorni e il filtro di regime è attivo.
     - oppure **pullback nel trend**: entra long se il prezzo rientra sopra una media media-più-corta dopo un piccolo ritracciamento.
   - Sempre 1 sola posizione aperta per volta (niente pyramiding in Fase 0–1).

3. **Gestione uscita**
   - Stop-loss iniziale basato su volatilità (es. multiplo di ATR sotto il prezzo di entrata).
   - Uscita per:
     - stop-loss toccato,
     - stop profit (take profit a X ATR sopra il prezzo d’ingresso),
     - o stop “di tempo” (es. chiudere dopo N giorni se non si è mosso abbastanza).

4. **Position sizing (in prospettiva reale)**
   - Risk per trade target: 0.25–0.5% del capitale.
   - Calcolo della size:
     - size = (capitale * risk_per_trade) / distanza_stop (in $).
   - In Fase 0–1 questa logica serve solo per calcolare l’equity simulata.

5. **Costi**
   - Commissioni realistiche per trade (es. 0.1% per lato).
   - Nessun slippage estremo (ma possiamo aggiungere un piccolo buffer, es. 0.01–0.05%).

### Cosa vogliamo misurare in backtest

Per questa strategia (e tutte le successive):

- numero di trade,
- profit/loss totale e per trade,
- max drawdown,
- % trade vincenti/perdenti,
- andamento dell’equity nel tempo (equity curve),
- performance separata per fasi di mercato (bull, bear, range).

L’edge non si considera “reale” se:
- dipende da parametri ultra-precisi,
- collassa appena cambiamo leggermente MA, ATR o soglie.

---

## Struttura del progetto `trading_lab/` (bozza)

Il Trading Lab sarà un mini-progetto Python separato (nuovo repo o sottocartella) con questa struttura logica:

- `trading_lab/`
  - `__init__.py`
  - `config.py`  
    - parametri globali (commissioni, risk per trade, percorsi dati, ecc.).
  - `data.py`  
    - funzioni per:
      - leggere file storici (es. CSV BTCUSDT daily da Binance),
      - pulire/normalizzare i dati (timezone, colonne, missing).
  - `strategies/`
    - `__init__.py`
    - `btc_trend_daily.py`  
      - implementazione della Strategia 1:
        - funzioni tipo `generate_signals(data, params)` → serie di segnali long/flat.
  - `backtest/`
    - `__init__.py`
    - `backtester.py`  
      - motore di backtest generico:
        - applica segnali al capitale,
        - simula entrate/uscite,
        - calcola PnL per trade, equity curve, drawdown.
  - `metrics/`
    - `__init__.py`
    - `report.py`  
      - calcolo KPI e produzione di piccoli report testuali (ed eventualmente grafici).
  - `notebooks/` (opzionale)
    - Jupyter notebook per esplorare dati, parametri, risultati.

In Fase 0–1:
- useremo solo i dati storici locali,
- nessuna chiamata API live,
- nessuna integrazione con exchange reale.


---

## Strategia 1 – BTC Daily Long-Only (baseline)

Obiettivo: avere una strategia semplice, spiegabile, da usare come baseline di confronto per esperimenti futuri (edge più avanzati).  
Non è l’obiettivo finale, ma il “controllo”.

### Universo

- Strumento: BTCUSDT (o BTCUSD) spot.
- Timeframe: candele daily (1D).
- Operatività: **solo long**, nessuno short, nessuna leva.

### Regole (bozza ad alto livello)

1. **Filtro di regime (trend filter)**
   - Calcoliamo una media mobile lunga (es. MA 100 o 150 giorni).
   - Regime “attivo” solo se:
     - prezzo di chiusura > MA lunga
     - e la volatilità non è eccessiva (es. ATR su N giorni sotto una soglia relativa).

2. **Segnali di ingresso**
   - Possibili varianti (da testare):
     - **Breakout di massimo recente**: entra long se il close rompe il massimo degli ultimi M giorni e il filtro di regime è attivo.
     - oppure **pullback nel trend**: entra long se il prezzo rientra sopra una media più corta dopo un piccolo ritracciamento.
   - Sempre 1 sola posizione aperta per volta (niente pyramiding in Fase 0–1).

3. **Gestione uscita**
   - Stop-loss iniziale basato su volatilità (es. multiplo di ATR sotto il prezzo di entrata).
   - Uscita per:
     - stop-loss toccato,
     - take profit (multiplo ATR sopra l’ingresso),
     - oppure stop “di tempo” (chiudere dopo N giorni se non si muove abbastanza).

4. **Position sizing (per il futuro reale)**
   - Rischio per trade target: 0.25–0.5% del capitale.
   - Size = (capitale * risk_per_trade) / distanza_stop ($).
   - In Fase 0–1 serve solo per simulare l’equity curve.

5. **Costi**
   - Commissioni realistiche per trade (es. 0.1% per lato).
   - Eventuale piccolo slippage aggiuntivo (es. 0.01–0.05%).

### Cosa vogliamo misurare in backtest

- numero di trade,
- profit/loss totale e per trade,
- max drawdown,
- % trade vincenti/perdenti,
- equity curve nel tempo,
- performance per fasi di mercato (bull, bear, range).

Un edge non è accettato se:
- funziona solo con parametri ultra-precisi,
- collassa appena cambiamo leggermente MA, ATR o soglie.

---

## Struttura del progetto `trading_lab/` (bozza)

Il Trading Lab sarà un mini-progetto Python (nuovo repo o sottocartella) con struttura logica:

- `trading_lab/`
  - `__init__.py`
  - `config.py`  
    - parametri globali: commissioni, risk per trade, percorsi dati, ecc.
  - `data.py`  
    - lettura file storici (es. CSV BTCUSDT daily da Binance),
    - pulizia/normalizzazione dati.
  - `strategies/`
    - `__init__.py`
    - `btc_trend_daily.py`  
      - implementazione Strategia 1:
        - `generate_signals(data, params)` → segnali long/flat.
  - `backtest/`
    - `__init__.py`
    - `backtester.py`  
      - motore di backtest generico:
        - applica segnali,
        - simula entrate/uscite,
        - calcola PnL, equity curve, drawdown.
  - `metrics/`
    - `__init__.py`
    - `report.py`  
      - calcolo KPI e produzione di report testuali/grafici.
  - `notebooks/` (opzionale)
    - notebook per esplorare dati, parametri, risultati.

In Fase 0–1:
- uso SOLO dati storici locali (Binance BTCUSDT daily),
- nessuna chiamata API live,
- nessuna operazione reale sugli exchange.

