from typing import Optional

import google.generativeai as genai
import requests

from .config import (
    get_gemini_api_key,
    get_openai_compat_api_key,
    get_openai_compat_base_url,
    get_openai_compat_model,
)


GEMINI_MODEL_NAME = "models/gemini-flash-latest"


def _has_openai_compat_config() -> bool:
    return bool(
        get_openai_compat_base_url()
        and get_openai_compat_api_key()
        and get_openai_compat_model()
    )


def _generate_with_gemini(prompt: str) -> Optional[str]:
    api_key = get_gemini_api_key()
    if not api_key:
        print("[LLM] GEMINI_API_KEY non configurata, salto Gemini.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(prompt)
        text = getattr(response, "text", None)
        if text:
            print("[LLM] Risposta generata con Gemini.")
            return text
        print("[LLM] Gemini ha risposto senza testo, provo fallback se disponibile.")
        return None
    except Exception as e:
        print(f"[LLM] Errore da Gemini, provo fallback se disponibile: {e}")
        return None


def _generate_with_openai_compat(prompt: str) -> Optional[str]:
    if not _has_openai_compat_config():
        print("[LLM] Config OpenAI-compat mancante, nessun fallback disponibile.")
        return None

    base_url = get_openai_compat_base_url().rstrip("/")
    api_key = get_openai_compat_api_key()
    model_name = get_openai_compat_model()

    url = f"{base_url}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            print("[LLM] Fallback OpenAI-compat: nessuna choice nella risposta.")
            return None
        content = choices[0].get("message", {}).get("content")
        if content:
            print("[LLM] Risposta generata con provider OpenAI-compat.")
            return content
        print("[LLM] Fallback OpenAI-compat: content vuoto.")
        return None
    except Exception as e:
        print(f"[LLM] Errore chiamando provider OpenAI-compat: {e}")
        return None


def generate_saas_page_text(prompt: str) -> str:
    """
    Tenta nell'ordine:
    1. Gemini (se configurato e funzionante)
    2. Provider OpenAI-compat (se configurato)
    """
    text = _generate_with_gemini(prompt)
    if text:
        return text

    text = _generate_with_openai_compat(prompt)
    if text:
        return text

    raise RuntimeError(
        "LLM generation failed: né Gemini né il provider OpenAI-compat sono disponibili o funzionanti."
    )
