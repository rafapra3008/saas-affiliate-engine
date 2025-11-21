# Project Constitution – SaaS Affiliate Engine

## Visione
Costruire un motore automatizzato che:
- raccoglie informazioni su SaaS per chi costruisce business online
- genera contenuti multilingua (EN/IT/PT)
- pubblica siti statici automatici
- massimizza profitto/giorno nel lungo termine con rischio minimo di perdita di capitale diretto.

## Principi
- Automazione prima di tutto: la VM lavora, l'umano supervisiona solo.
- No trading/speculazione con capitale proprio.
- Niente attività illegali o chiaramente tossiche (frodi, spam massivo, hacking).
- “Grigio intelligente”: scraping controllato, tanti micro-siti, SEO aggressiva ma pulita.
- Iterazioni piccole, continue, misurabili.

## Modello di business (v0)
- Monetizzazione tramite:
  - programmi di affiliazione SaaS (hosting, email marketing, funnel, tool AI, ecc.)
  - potenziale estensione futura a mini-tools/API proprietarie.
- Asset principale: portafoglio di micro-siti statici generati dal motore.

## Stack tecnico (v0)
- Linguaggio: Python 3.
- Librerie chiave:
  - requests, beautifulsoup4 (scraping leggero)
  - google-generativeai (Gemini) per generazione contenuti
  - markdown (render HTML da .md)
  - python-dotenv (config .env)
- Hosting:
  - Codice: GitHub (repo: saas_affiliate_engine).
  - Sito: GitHub Pages, branch main, cartella /docs.

## Architettura (v0)
- Collector:
  - legge seed URLs da data/seed_urls.txt
  - fetcha HTML e ne estrae info base (titolo, lingua)
- Content Generator:
  - usa Gemini per generare pagine affiliate-style in EN/IT/PT
- Content Writer:
  - salva pagine in markdown con frontmatter (title, subtitle, tool_name, homepage, language)
- Publisher:
  - converte .md in HTML statico
  - genera struttura docs/<lang>/slug/index.html
  - genera docs/index.html con link a tutte le pagine
- Run Logger:
  - salva log JSON di ogni run in logs/run-YYYYMMDD-HHMMSS.json

## Metriche prioritarie (v0)
1. Numero di tool supportati (seed URLs unici).
2. Numero di pagine generate per lingua.
3. Frequenza dei run e durata (sec).
4. In futuro: click su link affiliati e revenue per pagina.

## Roadmap ad alto livello
- Fase 1 (IN CORSO):
  - Motore base EN/IT/PT + sito statico online (GitHub Pages).
  - Logging di base dei run.
- Fase 2 (NEXT):
  - Integrare link di affiliazione reali e tracking click.
  - Aggiungere Telegram alert per errori run / stato sistema.
- Fase 3:
  - Aumentare il numero di seed in modo sistematico (liste da directory pubbliche, ecc.).
  - Aggiungere primi modelli di scoring per priorità tool/pagine.
- Fase 4:
  - ML più avanzato (scelta keyword, layout, copy A/B).
  - Portafoglio di più domini/micro-siti gestiti dallo stesso motore.

## Vincoli utente
- Niente telefono / call con clienti.
- Minimo contatto umano diretto.
- Budget iniziale target: <= 500€ nei primi 3 mesi, ma si parte quasi a costo zero.
- Lingue operative: EN, IT, PT (priorità per i contenuti).

## Roadmap settimanale (bozza)

- **Settimana 1 – Stabilizzazione base**
  - Mettere in piedi il motore SaaS affiliate.
  - Sistemare gestione segreti (`.env` fuori da Git, chiavi ruotate).
  - Attivare logging run + notifiche Telegram + sitemap.

- **Settimana 2 – Espansione contenuti**
  - Ampliare seed SaaS mirati (email, funnel, hosting, produttività).
  - Raffinare prompt per contenuti più “SEO-friendly”.
  - Integrare e verificare i principali link di affiliazione reali.

- **Settimana 3 – Robustezza LLM**
  - Testare e valutare provider LLM alternativi (es. Qwen via OpenAI-compatible).
  - Attivare fallback reale in produzione solo dopo test controllati.
  - Monitorare costi per chiamata e qualità output.

- **Settimana 4 – Metriche e primi esperimenti ML**
  - Definire e tracciare metriche: pagine indicizzate, click affiliati, CTR, revenue/giorno.
  - Introdurre piccoli esperimenti di ottimizzazione (A/B su prompt, selezione tool, priorità seed).
  - Preparare terreno per usare ML sul loop di miglioramento (scelta tool, scoring contenuti, ecc.).

