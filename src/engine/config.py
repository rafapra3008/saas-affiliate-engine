import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


def get_env() -> str:
    return os.getenv("ENV", "dev")


def get_gemini_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "")


def get_telegram_bot_token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "")


def get_telegram_chat_id() -> str:
    return os.getenv("TELEGRAM_CHAT_ID", "")


def get_max_tools_per_run(default: int = 10) -> int:
    value = os.getenv("MAX_TOOLS_PER_RUN")
    if not value:
        return default
    try:
        n = int(value)
        return max(1, n)
    except ValueError:
        return default


def get_openai_compat_base_url() -> str:
    return os.getenv("OPENAI_COMPAT_BASE_URL", "")


def get_openai_compat_api_key() -> str:
    return os.getenv("OPENAI_COMPAT_API_KEY", "")


def get_openai_compat_model() -> str:
    return os.getenv("OPENAI_COMPAT_MODEL", "")
