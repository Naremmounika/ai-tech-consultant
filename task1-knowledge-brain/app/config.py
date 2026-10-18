import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

APP_NAME = "Knowledge Brain"
APP_VERSION = "1.1.0"

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
).rstrip("/")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b",
)

HELP_CENTER_SITEMAP = os.getenv(
    "HELP_CENTER_SITEMAP",
    "https://support.brilliantdirectories.com/support/sitemap.xml",
)

MIN_SIMILARITY_SCORE = float(
    os.getenv("MIN_SIMILARITY_SCORE", "0.08")
)

MIN_QUERY_COVERAGE = float(
    os.getenv("MIN_QUERY_COVERAGE", "0.45")
)

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = DATA_DIR / "knowledge_index.json"