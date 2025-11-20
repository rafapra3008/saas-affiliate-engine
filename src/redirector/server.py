import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

CLICK_MAP_PATH = Path("config/click_map.json")
CLICK_LOG_DIR = Path("click_logs")

app = FastAPI(title="SaaS Affiliate Redirector")


@lru_cache(maxsize=1)
def load_click_map() -> Dict[str, str]:
    if not CLICK_MAP_PATH.exists():
        print(f"[REDIR] click_map non trovato: {CLICK_MAP_PATH}")
        return {}
    try:
        return json.loads(CLICK_MAP_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[REDIR] Errore nella lettura di click_map: {exc}")
        return {}


def log_click(slug: str, target: str, request: Request) -> None:
    CLICK_LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.time()
    ts_str = time.strftime("%Y%m%d", time.gmtime(ts))
    file_path = CLICK_LOG_DIR / f"clicks-{ts_str}.jsonl"

    entry: Dict[str, Any] = {
        "ts": ts,
        "slug": slug,
        "target": target,
        "client_host": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer"),
    }

    with file_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"[REDIR] Click loggato: {entry}")


@app.get("/go/{slug}")
async def go(slug: str, request: Request):
    mapping = load_click_map()
    target = mapping.get(slug)
    if not target:
        raise HTTPException(status_code=404, detail="Slug non trovato")

    log_click(slug, target, request)
    return RedirectResponse(url=target, status_code=302)
