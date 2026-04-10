import sys
import os
from pathlib import Path


def _frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_data_dir() -> Path:
    if _frozen():
        base = Path(os.environ.get("APPDATA", str(Path.home()))) / "GhostBudget"
    else:
        base = Path(__file__).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_locales_dir() -> Path:
    if _frozen():
        return Path(sys._MEIPASS) / "locales"
    return Path(__file__).parent / "locales"


def get_assets_dir() -> Path:
    if _frozen():
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).parent / "assets"


def get_credentials_file() -> Path:
    return get_data_dir() / "credentials.json"
