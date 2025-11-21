from typing import Dict, Optional

from .collector import SaaSTool
from .llm_backend import generate_saas_page_text


def generate_saas_page(
    tool: SaaSTool,
    language: str = "en",
    affiliate_url: Optional[str] = None,
) -> Dict[str, str]:
    target_url = affiliate_url or tool.homepage

    prompt = f"""
You are writing a short but high-converting affiliate review page for a SaaS tool.

Tool name: {tool.name}
Category: {tool.category}
Homepage: {tool.homepage}
Main language of the tool: {tool.main_language}
Affiliate URL (for main call-to-action link): {target_url}

Language for the output: {language}

GOAL:
- Convince a reader who is already somewhat interested in SaaS / online business tools
  to seriously consider trying this specific tool using the Affiliate URL above.

CONSTRAINTS:
- Use the Affiliate URL ABOVE as the ONLY external link.
- Do NOT invent other external URLs (no competitors, no random blogs).
- You may include the Affiliate URL multiple times, e.g. in buttons or text links.
- The tone should be clear, honest, and practical (no hype).

Return three parts, clearly separated with markers:

[TITLE]
A short, compelling title (1 line) that mentions the main benefit or use case.

[SUBTITLE]
A 1–2 sentence subtitle that explains who this tool is for and why it matters.

[BODY]
A markdown body structured with clear sections, for example:

### Who is this for?
Explain the ideal users (e.g. solopreneurs, small businesses, creators, agencies).

### Main use cases
Bullet points with concrete scenarios (newsletters, launches, funnels, automations, etc.).

### Key features
Bullet list of the most important features, focusing on outcomes (what changes for the user).

### Pricing overview
High-level pricing explanation (free plan if available, what you unlock by paying).
Do not invent exact price numbers if you are not sure; stay qualitative (e.g. "affordable", "scales with your list").

### Pros and cons
Two short bullet lists with honest pros and realistic cons/limitations.

### Why choose this tool over other options?
1–2 short paragraphs that position this tool vs. generic alternatives (without naming competitors).

### Call to action
End with a short, strong call to action that includes a markdown link using the Affiliate URL,
for example: [Try TOOL_NAME with this link](AFFILIATE_URL).

Make sure the body is concise (not more than ~700–800 words) but rich enough to be useful.
Use headings, bullet points, and short paragraphs to keep it readable.
"""

    text = generate_saas_page_text(prompt)

    title = ""
    subtitle = ""
    body = ""

    current = None
    for line in text.splitlines():
        l = line.strip()
        if l == "[TITLE]":
            current = "title"
            continue
        if l == "[SUBTITLE]":
            current = "subtitle"
            continue
        if l == "[BODY]":
            current = "body"
            continue

        if current == "title":
            title += line + "\n"
        elif current == "subtitle":
            subtitle += line + "\n"
        elif current == "body":
            body += line + "\n"

    return {
        "title": title.strip(),
        "subtitle": subtitle.strip(),
        "body_markdown": body.strip(),
    }
