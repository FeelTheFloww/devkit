"""Smoke tests for the Typer CLI: every subcommand exposes --help cleanly."""

from __future__ import annotations

from typer.testing import CliRunner

from devkit.main import app

runner = CliRunner()


def test_root_help_lists_all_groups() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for group in ("doctor", "gh", "ai", "workflow", "config", "cache"):
        assert group in result.stdout


def test_gh_help_lists_all_commands() -> None:
    result = runner.invoke(app, ["gh", "--help"])
    assert result.exit_code == 0
    for cmd in ("issues", "pr-summary", "start-feature", "open-pr", "run-status", "search", "stats"):
        assert cmd in result.stdout


def test_ai_help_lists_all_commands() -> None:
    result = runner.invoke(app, ["ai", "--help"])
    assert result.exit_code == 0
    for cmd in ("explain", "suggest", "review", "commit", "summarize", "docstring", "changelog", "test-gen", "ask"):
        assert cmd in result.stdout


def test_workflow_help_lists_all_commands() -> None:
    result = runner.invoke(app, ["workflow", "--help"])
    assert result.exit_code == 0
    for cmd in ("feature-start", "daily-digest", "ship"):
        assert cmd in result.stdout


def test_config_help_lists_all_commands() -> None:
    result = runner.invoke(app, ["config", "--help"])
    assert result.exit_code == 0
    for cmd in ("show", "set", "reset", "path"):
        assert cmd in result.stdout


def test_cache_help_lists_all_commands() -> None:
    result = runner.invoke(app, ["cache", "--help"])
    assert result.exit_code == 0
    for cmd in ("info", "clear"):
        assert cmd in result.stdout
