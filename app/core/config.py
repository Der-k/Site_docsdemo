"""Settings. Leaf module: imports nothing from the app."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


def _load_dotenv(path):
    """Minimal .env loader (no extra dependency). Real environment variables win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(BASE_DIR / ".env")


class Settings:
    app_name = "AAEMI SiteLog"
    base_dir = BASE_DIR
    data_file = Path(os.getenv("DATA_FILE", BASE_DIR / "app" / "data" / "demo_data.json"))
    secret_key = os.getenv("SECRET_KEY", "demo-secret-change-me")
    demo_user = {"name": "Tendai Moyo", "role": "HSE Manager"}
    expiry_window_days = 30
    # Shared password gate. Empty means no gate (fine for local use). Set it on any public deployment.
    demo_password = os.getenv("DEMO_PASSWORD", "")
    https_only = os.getenv("HTTPS_ONLY", "") == "1"  # secure session cookie; set on the hosted site
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
    groq_model = os.getenv("GROQ_MODEL") or os.getenv("MODEL_NAME") or "openai/gpt-oss-120b"
    # "groq" when a key is set, otherwise "demo". Set ASSISTANT_PROVIDER=demo to force the offline demo assistant.
    assistant_provider = os.getenv("ASSISTANT_PROVIDER") or ("groq" if groq_api_key else "demo")


settings = Settings()
