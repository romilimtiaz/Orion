import os
from pathlib import Path

def load_dotenv(path: str = ".env"):
    """Minimal .env loader that sets os.environ for KEY=VALUE lines."""
    env_path = Path(path)
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ[key] = value


def get_model_overrides(defaults: dict) -> dict:
    """Override model config from environment variables if present."""
    overrides = defaults.copy()
    overrides["router"] = os.environ.get("ORION_MODEL_ROUTER", overrides.get("router"))
    overrides["chat"] = os.environ.get("ORION_MODEL_CHAT", overrides.get("chat"))
    overrides["email"] = os.environ.get("ORION_MODEL_EMAIL", overrides.get("email"))
    overrides["fallback"] = os.environ.get("ORION_MODEL_FALLBACK", overrides.get("fallback"))
    return overrides
