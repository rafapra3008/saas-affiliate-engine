from pathlib import Path
from typing import List

from .config import get_env
from .collector import get_sample_saas_tools, collect_saas_from_seed_urls, SaaSTool
from .content_generator import generate_saas_page
from .content_writer import write_markdown_page
from .publisher import render_markdown_page


def _slugify(text: str) -> str:
    import re

    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "tool"


def build_index_html(tools: List[SaaSTool], out_root: str = "docs", second_lang_code: str = "it") -> Path:
    root = Path(out_root)
    root.mkdir(parents=True, exist_ok=True)

    items_en = []
    items_it = []
    for tool in tools:
        slug = _slugify(tool.name)
        items_en.append(f'<li><a href="{slug}/">{tool.name} (EN)</a></li>')
        items_it.append(f'<li><a href="{second_lang_code}/{slug}/">{tool.name} ({second_lang_code.upper()})</a></li>')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SaaS Affiliate Engine</title>
  <meta name="description" content="Auto-generated SaaS product pages.">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <h1>SaaS Affiliate Engine</h1>
  <p>Auto-generated pages for SaaS tools.</p>

  <h2>English</h2>
  <ul>
    {''.join(items_en)}
  </ul>

  <h2>Italiano</h2>
  <ul>
    {''.join(items_it)}
  </ul>
</body>
</html>
"""
    out_file = root / "index.html"
    out_file.write_text(html, encoding="utf-8")
    print(f"[INDEX] Generato index.html in: {out_file}")
    return out_file


def main():
    env = get_env()
    print(f"SaaS Affiliate Engine v0.1 - ENV={env}")

    sample_tools = get_sample_saas_tools()
    print(f"[STUB] Tools statici: {len(sample_tools)}")
    for tool in sample_tools:
        print(f"- {tool.name} | {tool.category} | free_plan={tool.has_free_plan}")

    print("\n[WEB] Raccolta da seed URLs...")
    web_tools = collect_saas_from_seed_urls()
    print(f"[WEB] Tools raccolti dal web: {len(web_tools)}")

    for idx, tool in enumerate(web_tools, start=1):
        print(f"\n=== TOOL {idx}/{len(web_tools)} ===")
        print(f"- {tool.name} | lang={tool.main_language} | url={tool.homepage}")

        # EN
        print("[GEN][EN] Generazione pagina EN...")
        page_en = generate_saas_page(tool, language="en")
        print("[WRITE][EN] Salvataggio markdown EN...")
        md_en = write_markdown_page(tool, page_en, out_dir="content_en", page_language="en")
        print("[PUBLISH][EN] Generazione HTML EN...")
        render_markdown_page(Path(md_en), out_root="docs")

        # IT
        print("[GEN][IT] Generazione pagina IT...")
        page_it = generate_saas_page(tool, language="it")
        print("[WRITE][IT] Salvataggio markdown IT...")
        md_it = write_markdown_page(tool, page_it, out_dir="content_it", page_language="it")
        print("[PUBLISH][IT] Generazione HTML IT...")
        render_markdown_page(Path(md_it), out_root="docs/it")

    if web_tools:
        build_index_html(web_tools, out_root="docs", second_lang_code="it")


if __name__ == "__main__":
    main()
