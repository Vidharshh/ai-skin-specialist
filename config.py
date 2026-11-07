"""Load environment-based settings once for the application."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    deepgram_api_key: str
    whisper_model: str
    groq_model: str
    deepgram_tts_model: str
    minimax_api_key: str
    minimax_base_url: str
    minimax_model: str
    backend_api_url: str


settings = Settings(
    groq_api_key=os.getenv("GROQ_API_KEY", ""),
    deepgram_api_key=os.getenv("DEEPGRAM_API_KEY", ""),
    whisper_model=os.getenv("WHISPER_MODEL", "whisper-large-v3"),
    groq_model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    deepgram_tts_model=os.getenv("DEEPGRAM_TTS_MODEL", "aura-2-thalia-en"),
    minimax_api_key=os.getenv("MINIMAX_API_KEY", ""),
    minimax_base_url=os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io/anthropic"),
    minimax_model=os.getenv("MINIMAX_MODEL", "MiniMax-M3"),
    backend_api_url=os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/"),
)
