import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = PROJECT_ROOT / "logs"
CLICKS_DIR = PROJECT_ROOT / "click_logs"


def load_run_logs():
    logs = []
    if not LOGS_DIR.exists():
        return logs

    for path in sorted(LOGS_DIR.glob("run-*.json")):
        try:
            with path.open("r", encoding="utf-8") as f:
                logs.append(json.load(f))
        except Exception as e:
            print(f"[WARN] Impossibile leggere log run {path}: {e}")
    return logs


def load_click_logs():
    total_clicks = 0
    by_slug = Counter()
    by_target = Counter()
    by_domain = Counter()

    if not CLICKS_DIR.exists():
        return total_clicks, by_slug, by_target, by_domain

    for path in sorted(CLICKS_DIR.glob("*.jsonl")):
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    total_clicks += 1

                    slug = rec.get("slug") or rec.get("slug_id")
                    if slug:
                        by_slug[slug] += 1

                    target = rec.get("target_url") or rec.get("url")
                    if target:
                        by_target[target] += 1
                        try:
                            domain = urlparse(target).netloc.lower()
                            if domain:
                                by_domain[domain] += 1
                        except Exception:
                            pass
        except Exception as e:
            print(f"[WARN] Impossibile leggere click log {path}: {e}")

    return total_clicks, by_slug, by_target, by_domain


def main():
    run_logs = load_run_logs()
    num_runs = len(run_logs)

    tools_total = 0
    pages_estimated = 0

    for log in run_logs:
        tools = log.get("num_tools") or 0

        languages = log.get("languages") or []
        if isinstance(languages, dict):
            languages = list(languages.keys())
        elif not isinstance(languages, (list, tuple)):
            languages = []

        try:
            tools_int = int(tools)
        except (TypeError, ValueError):
            tools_int = 0

        tools_total += tools_int
        pages_estimated += tools_int * max(1, len(languages))

    # Per ora consideriamo tutte le run come "success" a livello di conteggio
    success_runs = num_runs
    error_runs = 0

    total_clicks, by_slug, by_target, by_domain = load_click_logs()

    print("=== SaaS Affiliate Engine – Metrics snapshot ===\n")
    print(">> Run / generazione")
    print(f"- Run totali: {num_runs}")
    print(f"- Run con success (approx): {success_runs}")
    print(f"- Run con errori (approx): {error_runs}")
    print(f"- Tools processati totali (approx): {tools_total}")
    print(f"- Pagine generate stimate (tools x lingue): {pages_estimated}")
    print()
    print(">> Click affiliati (da redirector)")
    print(f"- Click totali registrati: {total_clicks}")

    if by_slug:
        print("- Top 5 slug per click:")
        for slug, count in by_slug.most_common(5):
            print(f"  • {slug}: {count} click")

    if by_target:
        print("- Top 5 URL target per click:")
        for url, count in by_target.most_common(5):
            print(f"  • {url}: {count} click")

    if by_domain:
        print("- Top domini (programmi affiliati) per click:")
        for dom, count in by_domain.most_common(10):
            print(f"  • {dom}: {count} click")

        focus_domains = [
            "www.mailerlite.com",
            "mailerlite.com",
            "systeme.io",
            "getresponse.com",
            "gr8.com",
        ]
        found_focus = False
        for dom in focus_domains:
            if dom in by_domain:
                if not found_focus:
                    print("\n  Focus programmi principali:")
                    found_focus = True
                print(f"  - {dom}: {by_domain[dom]} click")

    print("\nNota: questi numeri sono grezzi ma bastano per capire:")
    print("- quanto spesso gira il motore")
    print("- quante pagine stai producendo (stima)")
    print("- quali pagine e quali domini affiliati ricevono più click")
    print("\nPer analisi più avanzate (CTR, revenue, ML) serviranno poi dati aggiuntivi.")


if __name__ == "__main__":
    main()
