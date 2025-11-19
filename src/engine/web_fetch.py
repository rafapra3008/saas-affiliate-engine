from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SaaS-Affiliate-Engine/0.1; +https://example.com/bot)"
}


def fetch_html(url: str, timeout: int = 10) -> Optional[str]:
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        if resp.status_code != 200:
            print(f"[WARN] HTTP {resp.status_code} per {url}")
            return None
        return resp.text
    except Exception as exc:
        print(f"[ERROR] Fetch fallito per {url}: {exc}")
        return None


def extract_basic_info(html: str, url: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    # Nome = title della pagina (tagliato se troppo lungo)
    title = url
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    if len(title) > 80:
        title = title[:77] + "..."

    # Lingua stimata da <html lang="...">
    language = "en"
    if soup.html and soup.html.get("lang"):
        language = soup.html.get("lang").split("-")[0].lower()

    info: Dict[str, str] = {
        "name": title,
        "category": "unknown",
        "language": language,
    }
    return info
