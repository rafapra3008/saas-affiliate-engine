import json
import os
from pathlib import Path
from typing import Optional, List

from .collector import SaaSTool
from .affiliates import get_affiliate_url


def _slugify(text: str) -> str:
    import re

    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "tool"


def get_click_url(tool: SaaSTool) -> str:
    """
    Ritorna l'URL da usare nella CTA.

    Oggi:
      - se CLICK_BASE_URL è vuoto -> usa direttamente l'URL di affiliazione.
    Domani:
      - se CLICK_BASE_URL è impostato -> usa {CLICK_BASE_URL}/go/{slug}
        (pensato per un redirector sulla VM).
    """
    base = os.getenv("CLICK_BASE_URL", "").strip()
    affiliate_url = get_affiliate_url(tool)

    if base:
        base = base.rstrip("/")
        slug = _slugify(tool.name)
        return f"{base}/go/{slug}"

    return affiliate_url


def build_click_map(
    tools: List[SaaSTool],
    out_path: str = "config/click_map.json",
) -> Path:
    """
    Genera un file JSON slug -> affiliate_url.
    Il redirector lo userà per sapere dove mandare i click.
    """
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    mapping = {}
    for tool in tools:
        slug = _slugify(tool.name)
        mapping[slug] = get_affiliate_url(tool)

    path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    print(f"[CLICK_MAP] Salvato mapping in: {path}")
    return path
