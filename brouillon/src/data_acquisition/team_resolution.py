import json
from pathlib import Path
from .data_sources import RAW_DIR

OVERRIDES_PATH = RAW_DIR / "team_name_overrides.json"


def load_manual_overrides():
    if not OVERRIDES_PATH.exists():
        return {}
    try:
        return json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_manual_override(normalized_name: str, team_id: str):
    data = load_manual_overrides()
    data[normalized_name] = team_id
    OVERRIDES_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def resolve_with_overrides(normalized_name: str):
    data = load_manual_overrides()
    return data.get(normalized_name)
