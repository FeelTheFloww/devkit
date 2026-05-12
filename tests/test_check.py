"""Tests for devkit.utils.check."""

from __future__ import annotations

import pytest

from devkit.utils import check


def test_tool_available_finds_python() -> None:
    # `python` is always on PATH in CI and on the dev machine.
    assert check.tool_available("python") is True


def test_tool_available_returns_false_for_garbage() -> None:
    assert check.tool_available("definitely-not-a-real-binary-xyz") is False


def test_require_tools_passes_when_available() -> None:
    # Should not raise.
    check.require_tools(["python"])


def test_require_tools_exits_when_missing(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc:
        check.require_tools(["definitely-not-a-real-binary-xyz"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Missing required tools" in captured.err
