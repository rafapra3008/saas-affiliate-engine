from typing import List

import requests

from .config import get_telegram_bot_token, get_telegram_chat_id


def send_run_notification(
    success: bool,
    num_tools: int,
    languages: List[str],
    duration_sec: float,
    env: str,
    error_message: str | None = None,
) -> None:
    token = get_telegram_bot_token()
    chat_id = get_telegram_chat_id()

    if not token or not chat_id:
        print("[TEL] Token o chat_id non configurati, salto notifica.")
        return

    status = "✅ SUCCESSO" if success else "❌ ERRORE"
    langs = ", ".join(languages)
    duration_str = f"{duration_sec:.1f}s"

    text_lines = [
        f"{status} – SaaS Affiliate Engine",
        f"Env: {env}",
        f"Tools: {num_tools}",
        f"Lingue: {langs}",
        f"Durata: {duration_str}",
    ]
    if error_message:
        text_lines.append(f"Errore: {error_message[:200]}")

    text = "\n".join(text_lines)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code != 200:
            print(f"[TEL] Notifica fallita, HTTP {resp.status_code}: {resp.text[:200]}")
        else:
            print("[TEL] Notifica Telegram inviata.")
    except Exception as exc:
        print(f"[TEL] Errore nell'invio notifica: {exc}")
