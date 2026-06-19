from pathlib import Path
import sys
import os


def get_builtin_templates_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "templates" / "apps"

    return Path(__file__).resolve().parents[1] / "templates" / "apps"


def get_user_templates_dir() -> Path:
    appdata = os.getenv("APPDATA")

    if appdata:
        return Path(appdata) / "ProgressiveNodeX" / "templates" / "apps"

    return Path.home() / ".progressivenodex" / "templates" / "apps"