import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from urllib.parse import urlparse

from .collector import SaaSTool


@lru_cache(maxsize=1)
def _load_affiliates() -> dict:
    path = Path("config/affiliates.json")
    if not path.exists():
        print("[AFF] config/affiliates.json non trovato, uso homepage diretta.")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[AFF] Errore nel leggere affiliates.json: {exc}")
        return {}


def _domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower()
    

def get_affiliate_url(tool: SaaSTool) -> Optional[str]:
    """
    Ritorna l'URL di affiliazione per il tool, se presente.
    Altrimenti ritorna la homepage come fallback.
    """
    affiliates = _load_affiliates()
    domain = _domain_from_url(tool.homepage)
    if domain in affiliates:
        return affiliates[domain]
    return tool.homepage
