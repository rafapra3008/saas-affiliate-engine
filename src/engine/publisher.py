from pathlib import Path
from typing import Dict, Tuple

import markdown


def _slugify(text: str) -> str:
    import re

    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "tool"


def _parse_markdown_with_frontmatter(path: Path) -> Tuple[Dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    meta: Dict[str, str] = {}
    body_lines = []

    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            line = lines[i]
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip().strip('"')
            i += 1
        body_lines = lines[i + 1 :]
    else:
        body_lines = lines

    body = "\n".join(body_lines)
    return meta, body


def render_markdown_page(md_path: Path, out_root: str = "site") -> Path:
    meta, body_md = _parse_markdown_with_frontmatter(md_path)

    html_body = markdown.markdown(body_md)

    title = meta.get("title", meta.get("tool_name", "SaaS Tool"))
    subtitle = meta.get("subtitle", "")

    slug = _slugify(meta.get("tool_name", md_path.stem))
    out_dir = Path(out_root) / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.html"

    html = f"""<!DOCTYPE html>
<html lang="{meta.get('language', 'en')}">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="description" content="{subtitle}">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      padding: 2rem;
      max-width: 800px;
      line-height: 1.6;
    }}
    h1, h2, h3 {{
      margin-top: 1.5rem;
    }}
    .subtitle {{
      color: #555;
      margin-bottom: 1.5rem;
    }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="subtitle">{subtitle}</div>
  {html_body}
</body>
</html>
"""
    out_file.write_text(html, encoding="utf-8")
    print(f"[PUBLISH] HTML generato in: {out_file}")
    return out_file
