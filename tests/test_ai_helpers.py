"""Tests for the non-AI helpers inside devkit.commands.ai."""

from __future__ import annotations

import pytest

from devkit.commands.ai import _default_model, _strip_code_fence
import devkit.commands.ai as ai_module


def test_strip_code_fence_plain_text() -> None:
    assert _strip_code_fence("def f():\n    pass") == "def f():\n    pass"


def test_strip_code_fence_removes_python_fence() -> None:
    wrapped = "```python\ndef f():\n    pass\n```"
    assert _strip_code_fence(wrapped) == "def f():\n    pass"


def test_strip_code_fence_removes_plain_fence() -> None:
    wrapped = "```\nhello\n```"
    assert _strip_code_fence(wrapped) == "hello"


def test_strip_code_fence_handles_whitespace() -> None:
    wrapped = "\n\n```python\nprint('x')\n```\n\n"
    assert _strip_code_fence(wrapped) == "print('x')"


def test_default_model_uses_config_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai_module, "load_config", lambda: {"ai_tool": "gemini"})
    assert _default_model() == "gemini"


def test_default_model_falls_back_to_claude_for_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ai_module, "load_config", lambda: {"ai_tool": "bogus"})
    assert _default_model() == "claude"


def test_default_model_handles_missing_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ai_module, "load_config", lambda: {})
    assert _default_model() == "claude"
