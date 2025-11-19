import os
from pathlib import Path

from dotenv import load_dotenv


# Root del progetto = cartella che contiene "src" e ".env"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

# Carichiamo sempre lo .env esplicito
load_dotenv(ENV_PATH)


def get_env() -> str:
    return os.getenv("ENV", "dev")


def get_gemini_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "")
