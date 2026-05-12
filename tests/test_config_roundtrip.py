"""Round-trip tests for devkit.config using a temp HOME."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import devkit.config as cfg_module


@pytest.fixture()
def temp_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point CONFIG_FILE at a throwaway location for the duration of one test."""
    fake = tmp_path / ".devkit" / "config.json"
    monkeypatch.setattr(cfg_module, "CONFIG_FILE", fake)
    return fake


def test_load_returns_defaults_when_file_missing(temp_config: Path) -> None:
    loaded = cfg_module.load_config()
    assert loaded == cfg_module.DEFAULTS


def test_save_then_load_merges_with_defaults(temp_config: Path) -> None:
    cfg_module.save_config({"ai_tool": "gemini", "default_repo": "me/myrepo"})
    loaded = cfg_module.load_config()
    assert loaded["ai_tool"] == "gemini"
    assert loaded["default_repo"] == "me/myrepo"
    # Unspecified keys should fall back to defaults.
    assert loaded["theme"] == cfg_module.DEFAULTS["theme"]
    assert loaded["show_spinner"] is True


def test_load_survives_invalid_json(temp_config: Path) -> None:
    temp_config.parent.mkdir(parents=True, exist_ok=True)
    temp_config.write_text("{not valid", encoding="utf-8")
    loaded = cfg_module.load_config()
    assert loaded == cfg_module.DEFAULTS


def test_save_creates_parent_directory(temp_config: Path) -> None:
    assert not temp_config.parent.exists()
    cfg_module.save_config({"ai_tool": "claude"})
    assert temp_config.parent.is_dir()
    written = json.loads(temp_config.read_text(encoding="utf-8"))
    assert written["ai_tool"] == "claude"
