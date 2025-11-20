import os
import time
from pathlib import Path
from typing import List, Tuple, Dict

from urllib.parse import urlparse

from .config import get_env, get_max_tools_per_run
from .collector import get_sample_saas_tools, collect_saas_from_seed_urls, SaaSTool
from .content_generator import generate_saas_page
from .content_writer import write_markdown_page
from .publisher import render_markdown_page
from .run_logger import start_run, end_run
from .affiliates import get_affiliate_url
from .click_urls import get_click_url, build_click_map
from .notifier import send_run_notification


def _slugify(text: str) -> str:
    import re

    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "tool"


LANG_CONFIG: List[Tuple[str, str, str]] = [
    ("en", "English", "docs"),
    ("it", "Italiano", "docs/it"),
    ("pt", "Português", "docs/pt"),
]


def _get_domain(url: str) -> str:
    return urlparse(url).netloc.lower()


def categorize_tool(tool: SaaSTool) -> str:
    """
    Restituisce una categoria logica in base al dominio.
    """
    domain = _get_domain(tool.homepage)

    email_domains = [
        "mailerlite.com",
        "convertkit.com",
        "getresponse.com",
        "aweber.com",
        "mailchimp.com",
        "brevo.com",
        "sendinblue.com",
    ]
    funnel_domains = [
        "systeme.io",
        "clickfunnels.com",
        "kajabi.com",
        "teachable.com",
        "thinkific.com",
        "kartra.com",
    ]
    website_domains = [
        "webflow.com",
        "ghost.org",
        "wordpress.com",
        "wix.com",
        "squarespace.com",
        "framer.com",
    ]

    if domain in email_domains:
        return "email"
    if domain in funnel_domains:
        return "funnel"
    if domain in website_domains:
        return "website"

    return "other"


CATEGORY_LABELS: Dict[str, str] = {
    "email": "Email marketing & newsletter",
    "funnel": "Funnels, automazione & corsi",
    "website": "Websites, hosting & publishing",
    "other": "Altro SaaS utile",
}


def build_index_html(tools: List[SaaSTool], out_root: str = "docs") -> Path:
    root = Path(out_root)
    root.mkdir(parents=True, exist_ok=True)

    # Raggruppa per categoria
    grouped: Dict[str, List[SaaSTool]] = {"email": [], "funnel": [], "website": [], "other": []}
    for tool in tools:
        cat = categorize_tool(tool)
        grouped.setdefault(cat, []).append(tool)

    sections = []
    # Indice categorie
    nav_items = []
    for cat_key in ["email", "funnel", "website", "other"]:
        label = CATEGORY_LABELS[cat_key]
        nav_items.append(f'<li><a href="#{cat_key}">{label}</a></li>')
    nav_html = "<ul>" + "".join(nav_items) + "</ul>"

    for cat_key in ["email", "funnel", "website", "other"]:
        label = CATEGORY_LABELS[cat_key]
        tools_in_cat = grouped.get(cat_key, [])
        if not tools_in_cat:
            continue

        items = []
        for tool in tools_in_cat:
            slug = _slugify(tool.name)
            # Link per ogni lingua
            lang_links = []
            for code, _, prefix_root in LANG_CONFIG:
                if prefix_root == "docs":
                    path = f"{slug}/"
                else:
                    prefix = prefix_root.split("/", 1)[1]
                    path = f"{prefix}/{slug}/"
                lang_links.append(f'<a href="{path}">{code.upper()}</a>')
            lang_html = " | ".join(lang_links)
            items.append(f"<li>{tool.name} – {lang_html}</li>")

        section_html = f'<h2 id="{cat_key}">{label}</h2><ul>{"".join(items)}</ul>'
        sections.append(section_html)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SaaS Affiliate Engine</title>
  <meta name="description" content="Auto-generated SaaS product pages for tools used to build online businesses.">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <h1>SaaS Affiliate Engine</h1>
  <p>Auto-generated pages for SaaS tools (EN/IT/PT) used to build and grow online businesses.</p>

  <h2>Categorie</h2>
  {nav_html}

  {''.join(sections)}
</body>
</html>
"""
    out_file = root / "index.html"
    out_file.write_text(html, encoding="utf-8")
    print(f"[INDEX] Generato index.html in: {out_file}")
    return out_file


def build_sitemap(tools: List[SaaSTool], out_root: str = "docs") -> Path:
    """
    Genera un sitemap.xml semplice con tutte le pagine per lingua.
    Usa SITE_BASE_URL se impostato nello .env, altrimenti usa path relativi.
    """
    root = Path(out_root)
    root.mkdir(parents=True, exist_ok=True)

    base_url = os.getenv("SITE_BASE_URL", "").rstrip("/")
    urls = []

    for tool in tools:
        slug = _slugify(tool.name)
        for code, _, prefix_root in LANG_CONFIG:
            if prefix_root == "docs":
                path = f"{slug}/"
            else:
                prefix = prefix_root.split("/", 1)[1]
                path = f"{prefix}/{slug}/"

            if base_url:
                loc = f"{base_url}/{path}"
            else:
                loc = f"/{path}"

            urls.append(f"<url><loc>{loc}</loc></url>")

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
""" + "\n".join(urls) + "\n</urlset>\n"

    out_file = root / "sitemap.xml"
    out_file.write_text(xml, encoding="utf-8")
    print(f"[SITEMAP] Generato sitemap.xml in: {out_file}")
    return out_file


def main():
    run_start = start_run()
    env = get_env()
    web_tools: List[SaaSTool] = []
    success = False
    error_message: str | None = None

    try:
        sample_tools = get_sample_saas_tools()
        print(f"SaaS Affiliate Engine v0.1 - ENV={env}")
        print(f"[STUB] Tools statici: {len(sample_tools)}")
        for tool in sample_tools:
            print(f"- {tool.name} | {tool.category} | free_plan={tool.has_free_plan}")

        print("\n[WEB] Raccolta da seed URLs...")
        web_tools_all = collect_saas_from_seed_urls()
        max_tools = get_max_tools_per_run()
        if len(web_tools_all) > max_tools:
            print(f"[LIMIT] Ho raccolto {len(web_tools_all)} tools, ma ne processerò solo {max_tools}.")
            web_tools = web_tools_all[:max_tools]
        else:
            web_tools = web_tools_all
        print(f"[WEB] Tools processati in questo run: {len(web_tools)}")

        for idx, tool in enumerate(web_tools, start=1):
            print(f"\n=== TOOL {idx}/{len(web_tools)} ===")
            print(f"- {tool.name} | lang={tool.main_language} | url={tool.homepage}")

            affiliate_url = get_affiliate_url(tool)
            click_url = get_click_url(tool)
            print(f"[AFF] URL affiliazione: {affiliate_url}")
            print(f"[CLICK] URL usato nella CTA: {click_url}")

            for code, label, out_root in LANG_CONFIG:
                print(f"[GEN][{code.upper()}] Generazione pagina {label}...")
                page = generate_saas_page(tool, language=code, affiliate_url=click_url)

                out_dir = f"content_{code}"
                print(f"[WRITE][{code.upper()}] Salvataggio markdown in {out_dir}...")
                md_path = write_markdown_page(
                    tool,
                    page,
                    out_dir=out_dir,
                    page_language=code,
                    affiliate_url=affiliate_url,
                    click_url=click_url,
                )

                print(f"[PUBLISH][{code.upper()}] Generazione HTML in {out_root}...")
                render_markdown_page(Path(md_path), out_root=out_root)

        if web_tools:
            build_index_html(web_tools, out_root="docs")
            build_click_map(web_tools, out_path="config/click_map.json")
            build_sitemap(web_tools, out_root="docs")

        success = True

    except Exception as exc:
        error_message = repr(exc)
        print(f"[ERROR] Eccezione durante il run: {error_message}")
        raise

    finally:
        language_codes = [code for code, _, _ in LANG_CONFIG]
        end_run(
            start_ts=run_start,
            num_tools=len(web_tools),
            languages=language_codes,
            extra={"env": env},
            out_dir="logs",
        )

        duration_sec = time.time() - run_start
        try:
            send_run_notification(
                success=success,
                num_tools=len(web_tools),
                languages=language_codes,
                duration_sec=duration_sec,
                env=env,
                error_message=error_message,
            )
        except Exception as notify_exc:
            print(f"[TEL] Errore nell'invio notifica (blocco finally): {notify_exc}")


if __name__ == "__main__":
    main()
