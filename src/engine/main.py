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


def build_index_html(tools: List[SaaSTool], out_root: str = "docs") -> Path:
    root = Path(out_root)
    root.mkdir(parents=True, exist_ok=True)

    items = []
    for tool in tools:
        slug = _slugify(tool.name)
        items.append(f'<li><a href="{slug}/">{tool.name}</a></li>')

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
  <ul>
    {''.join(items)}
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

        print("[GEN] Generazione pagina con Gemini...")
        page = generate_saas_page(tool, language=tool.main_language or "en")

        print("[WRITE] Salvataggio markdown...")
        md_path = write_markdown_page(tool, page, out_dir="content")

        print("[PUBLISH] Generazione HTML...")
        render_markdown_page(Path(md_path), out_root="docs")

    if web_tools:
        build_index_html(web_tools, out_root="docs")


if __name__ == "__main__":
    main()
