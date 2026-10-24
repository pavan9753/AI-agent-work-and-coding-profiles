from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "sample_tickets.csv"
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "ticket_classifier.joblib"
METRICS_PATH = ARTIFACT_DIR / "evaluation.json"
MAX_TICKET_CHARS = 4_000

load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class AppSettings:
    model_name: str
    has_openai_key: bool


def get_settings() -> AppSettings:
    import os

    return AppSettings(
        model_name=os.getenv("OPENAI_MODEL", "gpt-6-astra"),
        has_openai_key=bool(os.getenv("OPENAI_API_KEY", "").strip()),
    )
