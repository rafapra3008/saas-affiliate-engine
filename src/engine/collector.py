from dataclasses import dataclass
from pathlib import Path
from typing import List

from .web_fetch import fetch_html, extract_basic_info


@dataclass
class SaaSTool:
    name: str
    category: str
    homepage: str
    pricing_page: str
    has_free_plan: bool
    main_language: str  # es. "en", "it", "pt"


def get_sample_saas_tools() -> List[SaaSTool]:
    """
    Stub iniziale:
    lasciamo questo come esempio statico.
    """
    return [
        SaaSTool(
            name="MailBlaster",
            category="Email marketing",
            homepage="https://example.com/mailblaster",
            pricing_page="https://example.com/mailblaster/pricing",
            has_free_plan=True,
            main_language="en",
        ),
        SaaSTool(
            name="FunnelPro",
            category="Sales funnels",
            homepage="https://example.com/funnelpro",
            pricing_page="https://example.com/funnelpro/pricing",
            has_free_plan=False,
            main_language="en",
        ),
        SaaSTool(
            name="ContasPro",
            category="Billing & Invoicing",
            homepage="https://example.com/contaspro",
            pricing_page="https://example.com/contaspro/pricing",
            has_free_plan=True,
            main_language="pt",
        ),
    ]


def _load_seed_urls(seed_file: str = "data/seed_urls.txt") -> List[str]:
    path = Path(seed_file)
    if not path.exists():
        print(f"[WARN] Seed file non trovato: {seed_file}")
        return []

    urls: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def collect_saas_from_seed_urls(seed_file: str = "data/seed_urls.txt") -> List[SaaSTool]:
    urls = _load_seed_urls(seed_file)
    tools: List[SaaSTool] = []

    for url in urls:
        html = fetch_html(url)
        if html is None:
            continue

        info = extract_basic_info(html, url)
        tool = SaaSTool(
            name=info["name"],
            category=info["category"],
            homepage=url,
            pricing_page=url,  # per ora usiamo la stessa URL
            has_free_plan=False,  # TBD: in futuro lo dedurremo dal contenuto
            main_language=info["language"],
        )
        tools.append(tool)

    return tools
