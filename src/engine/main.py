from pathlib import Path

from .config import get_env
from .collector import get_sample_saas_tools, collect_saas_from_seed_urls
from .content_generator import generate_saas_page
from .content_writer import write_markdown_page
from .publisher import render_markdown_page


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
        # per GitHub Pages usiamo 'docs' come root
        render_markdown_page(Path(md_path), out_root="docs")


if __name__ == "__main__":
    main()
