import json
from pathlib import Path

_LOCALES_DIR = Path(__file__).parent / "locales"
_CONFIG_PATH = Path(__file__).parent / "data" / "config.json"
_DEFAULT_LANG = "en"

_current_lang: str = _DEFAULT_LANG
_strings: dict[str, str] = {}


def init() -> None:
    """Load language from saved config (defaults to 'en')."""
    lang = _DEFAULT_LANG
    if _CONFIG_PATH.exists():
        try:
            config = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            lang = config.get("language", _DEFAULT_LANG)
        except Exception:
            pass
    load_language(lang)


def load_language(lang: str) -> None:
    """Switch active language and persist the choice."""
    global _current_lang, _strings
    locale_file = _LOCALES_DIR / f"{lang}.json"
    if not locale_file.exists():
        locale_file = _LOCALES_DIR / f"{_DEFAULT_LANG}.json"
        lang = _DEFAULT_LANG
    _strings = json.loads(locale_file.read_text(encoding="utf-8"))
    _current_lang = lang
    _save_config()


def t(key: str, **kwargs) -> str:
    """Return the translated string for key; falls back to the key itself."""
    value = _strings.get(key, key)
    if kwargs:
        try:
            value = value.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return value


def get_current_language() -> str:
    return _current_lang


def _save_config() -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing: dict = {}
    if _CONFIG_PATH.exists():
        try:
            existing = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    existing["language"] = _current_lang
    _CONFIG_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")
