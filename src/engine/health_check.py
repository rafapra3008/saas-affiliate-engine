import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def check_file_exists(rel_path: str) -> bool:
    path = PROJECT_ROOT / rel_path
    if not path.exists():
        print(f"[HC][FAIL] File mancante: {rel_path}")
        return False
    print(f"[HC][OK] File presente: {rel_path}")
    return True


def check_recent_run_logs(days: int = 2) -> bool:
    logs_dir = PROJECT_ROOT / "logs"
    if not logs_dir.exists():
        print("[HC][FAIL] Cartella logs non esiste.")
        return False

    now = time.time()
    threshold = now - days * 86400
    recent_found = False

    for log_file in sorted(logs_dir.glob("run-*.json")):
        mtime = log_file.stat().st_mtime
        if mtime >= threshold:
            recent_found = True
            print(f"[HC][OK] Log recente: {log_file.name}")
            break

    if not recent_found:
        print(f"[HC][WARN] Nessun log run negli ultimi {days} giorni.")
    return recent_found


def main():
    ok = True
    ok &= check_file_exists("docs/index.html")
    ok &= check_file_exists("config/click_map.json")
    check_recent_run_logs(days=2)

    if ok:
        print("[HC] Health check COMPLETATO (base OK).")
    else:
        print("[HC] Health check COMPLETATO con problemi.")


if __name__ == "__main__":
    main()
