"""Tests for the plugin / hook discovery system."""

from __future__ import annotations

from pathlib import Path

import pytest
import typer

import devkit.plugins as plugins_module


@pytest.fixture()
def temp_plugin_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    plugins_dir = tmp_path / "plugins"
    hooks_dir = tmp_path / "hooks"
    monkeypatch.setattr(plugins_module, "PLUGINS_DIR", plugins_dir)
    monkeypatch.setattr(plugins_module, "HOOKS_DIR", hooks_dir)
    return plugins_dir, hooks_dir


def test_discover_plugins_returns_empty_when_dir_missing(
    temp_plugin_dirs: tuple[Path, Path],
) -> None:
    assert plugins_module.discover_plugins() == []


def test_discover_plugins_finds_typer_app(
    temp_plugin_dirs: tuple[Path, Path],
) -> None:
    plugins_dir, _ = temp_plugin_dirs
    plugins_dir.mkdir(parents=True, exist_ok=True)
    (plugins_dir / "demo.py").write_text(
        "import typer\napp = typer.Typer()\n"
        "@app.command()\ndef hi(): print('hi')\n"
    )
    found = plugins_module.discover_plugins()
    assert len(found) == 1
    name, app = found[0]
    assert name == "demo"
    assert isinstance(app, typer.Typer)


def test_discover_plugins_skips_files_without_app(
    temp_plugin_dirs: tuple[Path, Path],
) -> None:
    plugins_dir, _ = temp_plugin_dirs
    plugins_dir.mkdir(parents=True, exist_ok=True)
    (plugins_dir / "noop.py").write_text("# nothing here\n")
    assert plugins_module.discover_plugins() == []


def test_fire_runs_registered_hooks(temp_plugin_dirs: tuple[Path, Path]) -> None:
    _, hooks_dir = temp_plugin_dirs
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / "log.py").write_text(
        "def pre_commit(ctx):\n"
        "    ctx['was_called'] = True\n"
        "    ctx['original_message'] = ctx.get('message')\n"
    )
    result = plugins_module.fire("pre_commit", {"message": "feat: x"})
    assert result["was_called"] is True
    assert result["original_message"] == "feat: x"


def test_fire_with_no_hooks_returns_context(
    temp_plugin_dirs: tuple[Path, Path],
) -> None:
    result = plugins_module.fire("post_pr_open", {"url": "u"})
    assert result == {"url": "u"}


def test_register_with_mounts_plugins(
    temp_plugin_dirs: tuple[Path, Path],
) -> None:
    plugins_dir, _ = temp_plugin_dirs
    plugins_dir.mkdir(parents=True, exist_ok=True)
    (plugins_dir / "myplug.py").write_text(
        "import typer\napp = typer.Typer()\n"
        "@app.command()\ndef hi(): print('hi')\n"
    )
    root = typer.Typer()
    n = plugins_module.register_with(root)
    assert n == 1
