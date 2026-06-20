import json
import os
from pathlib import Path
from typing import Any


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api/v1"


def get_pnx_config_dir() -> Path:
    appdata = os.getenv("APPDATA")

    if appdata:
        return Path(appdata) / "ProgressiveNodeX"

    return Path.home() / ".progressivenodex"


def get_auth_file() -> Path:
    return get_pnx_config_dir() / "auth.json"


def get_default_api_base_url() -> str:
    return os.getenv("PNX_MARKETPLACE_API", DEFAULT_API_BASE_URL).rstrip("/")


def load_auth() -> dict[str, Any]:
    auth_file = get_auth_file()

    if not auth_file.exists():
        return {}

    try:
        return json.loads(auth_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_auth(
    access_token: str,
    username: str | None = None,
    api_base_url: str | None = None,
) -> None:
    config_dir = get_pnx_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "access_token": access_token,
        "username": username,
        "api_base_url": (api_base_url or get_default_api_base_url()).rstrip("/"),
    }

    get_auth_file().write_text(
        json.dumps(data, indent=4),
        encoding="utf-8",
    )


def clear_auth() -> None:
    auth_file = get_auth_file()

    if auth_file.exists():
        auth_file.unlink()


def get_access_token() -> str | None:
    return load_auth().get("access_token")


def get_api_base_url() -> str:
    stored_url = load_auth().get("api_base_url")

    if stored_url:
        return str(stored_url).rstrip("/")

    return get_default_api_base_url()