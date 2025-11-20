from pathlib import Path
from typing import Dict, Optional

from .collector import SaaSTool


def _slugify(text: str) -> str:
    import re

    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "tool"


def write_markdown_page(
    tool: SaaSTool,
    page: Dict[str, str],
    out_dir: str = "content",
    page_language: Optional[str] = None,
    affiliate_url: Optional[str] = None,
    click_url: Optional[str] = None,
) -> Path:
    """
    Scrive una pagina markdown con una frontmatter semplice + info affiliazione.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    slug = _slugify(tool.name)
    file_path = out_path / f"{slug}.md"

    title = page.get("title", tool.name)
    subtitle = page.get("subtitle", "")
    body = page.get("body_markdown", "")

    title_s = title.replace('"', "'")
    subtitle_s = subtitle.replace('"', "'")
    tool_name_s = tool.name.replace('"', "'")
    language = page_language or tool.main_language or "en"

    affiliate_s = (affiliate_url or tool.homepage).replace('"', "'")
    click_s = (click_url or affiliate_s).replace('"', "'")

    frontmatter = [
        "---",
        f'title: "{title_s}"',
        f'subtitle: "{subtitle_s}"',
        f'tool_name: "{tool_name_s}"',
        f'homepage: "{tool.homepage}"',
        f'language: "{language}"',
        f'affiliate_url: "{affiliate_s}"',
        f'click_url: "{click_s}"',
        "---",
        "",
    ]

    content = "\n".join(frontmatter) + body + "\n"
    file_path.write_text(content, encoding="utf-8")

    print(f"[WRITE] Pagina salvata in: {file_path}")
    return file_path
