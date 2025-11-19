from typing import Dict

import google.generativeai as genai

from .collector import SaaSTool
from .config import get_gemini_api_key


def _get_model():
    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY non configurata nel .env")
    genai.configure(api_key=api_key)
    # Usa un modello che sappiamo esistere e supportare generateContent
    return genai.GenerativeModel("models/gemini-flash-latest")


def generate_saas_page(tool: SaaSTool, language: str = "en") -> Dict[str, str]:
    model = _get_model()

    prompt = f"""
Generate a concise affiliate-style product page for this SaaS tool.

Tool name: {tool.name}
Category: {tool.category}
Homepage: {tool.homepage}
Main language: {tool.main_language}

Language for the output: {language}

Return three parts, clearly separated with markers:

[TITLE]
A short, compelling title.

[SUBTITLE]
A 1–2 sentence subtitle.

[BODY]
A markdown body with:
- who this tool is for
- main use cases
- key features
- pricing overview (high-level)
- a short call to action.
"""

    response = model.generate_content(prompt)
    text = response.text or ""

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
