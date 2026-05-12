from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_FILE = Path.home() / ".devkit" / "config.json"
DEFAULTS: dict[str, Any] = {
    "ai_tool": "claude",
    "default_repo": "",
    "theme": "dark",
    "show_spinner": True,
}


def load_config() -> dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {**DEFAULTS, **data}
        except json.JSONDecodeError:
            return DEFAULTS.copy()
    return DEFAULTS.copy()


def save_config(cfg: dict[str, Any]) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
