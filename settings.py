import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent
ENV_FILE = ROOT_DIR / ".env"

if ENV_FILE.exists():
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if sep:
            os.environ.setdefault(key.strip(), value.strip())


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int(value: str | None, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class Settings:
    app_title: str = os.getenv("APP_TITLE", "Price Tracker API")
    mongo_uri: str = os.getenv("MONGO_URI", "")
    scheduler_interval_minutes: int = _int(os.getenv("SCHEDULER_INTERVAL_MINUTES"), 600)
    playwright_headless: bool = _bool(os.getenv("PLAYWRIGHT_HEADLESS"), True)
    playwright_timeout_ms: int = _int(os.getenv("PLAYWRIGHT_TIMEOUT_MS"), 60000)


settings = Settings()

if not settings.mongo_uri:
    raise RuntimeError("MONGO_URI must be set in environment or .env")
