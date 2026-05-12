"""Tests for the subprocess helpers in devkit.utils.shell."""

from __future__ import annotations

import pytest

from devkit.utils.shell import run_cmd, run_json


def test_run_cmd_returns_stripped_stdout() -> None:
    out = run_cmd(["python", "-c", "print('hello')"])
    assert out == "hello"


def test_run_cmd_raises_on_failure() -> None:
    with pytest.raises(RuntimeError) as exc:
        run_cmd(["python", "-c", "import sys; sys.exit(7)"])
    # The exception text should include the failing command.
    assert "python" in str(exc.value)


def test_run_cmd_missing_binary_raises() -> None:
    with pytest.raises(RuntimeError) as exc:
        run_cmd(["definitely-not-a-real-binary-xyz"])
    assert "Command not found" in str(exc.value)


def test_run_json_parses_valid_output() -> None:
    data = run_json(["python", "-c", "print('[1, 2, 3]')"])
    assert data == [1, 2, 3]


def test_run_json_returns_empty_list_on_empty_stdout() -> None:
    data = run_json(["python", "-c", "pass"])
    assert data == []


def test_run_json_raises_on_invalid_json() -> None:
    with pytest.raises(RuntimeError) as exc:
        run_json(["python", "-c", "print('not json')"])
    assert "Expected JSON" in str(exc.value)
