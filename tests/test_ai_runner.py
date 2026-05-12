"""Tests for the unified AI runner with cache + fallback."""

from __future__ import annotations

from pathlib import Path

import pytest

import devkit.utils.ai_runner as ai_runner
import devkit.utils.cache as cache_module


@pytest.fixture(autouse=True)
def _isolated_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each test gets a fresh cache dir so they can't pollute each other."""
    monkeypatch.setattr(cache_module, "CACHE_DIR", tmp_path / "cache")


def test_truncate_short_prompt_unchanged() -> None:
    assert ai_runner.truncate_prompt("hello") == "hello"


def test_truncate_long_prompt_marks_cut() -> None:
    big = "x" * 10_000
    out = ai_runner.truncate_prompt(big, limit=100)
    assert len(out) > 100  # marker adds chars
    assert "[truncated" in out


def test_run_ai_uses_cache_for_repeated_prompts(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"n": 0}

    def fake_call_one(model: str, prompt: str, *, non_interactive: bool) -> str:
        calls["n"] += 1
        return f"answer-{calls['n']}"

    monkeypatch.setattr(ai_runner, "_call_one", fake_call_one)

    first = ai_runner.run_ai("hi", preferred="claude")
    second = ai_runner.run_ai("hi", preferred="claude")

    assert first.response == "answer-1"
    assert second.response == "answer-1"
    assert second.cached is True
    assert calls["n"] == 1


def test_run_ai_falls_back_when_preferred_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_call_one(model: str, prompt: str, *, non_interactive: bool) -> str:
        if model == "claude":
            raise ai_runner.AIError("claude is broken")
        return f"from-{model}"

    monkeypatch.setattr(ai_runner, "_call_one", fake_call_one)

    result = ai_runner.run_ai("hi", preferred="claude", use_cache=False)
    assert result.model == "gemini"
    assert result.response == "from-gemini"


def test_run_ai_raises_when_all_backends_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_call_one(model: str, prompt: str, *, non_interactive: bool) -> str:
        raise ai_runner.AIError(f"{model} down")

    monkeypatch.setattr(ai_runner, "_call_one", fake_call_one)

    with pytest.raises(ai_runner.AIError) as exc:
        ai_runner.run_ai("hi", preferred="claude", use_cache=False)
    assert "All AI backends failed" in str(exc.value)


def test_run_ai_no_fallback_does_not_try_others(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_models: list[str] = []

    def fake_call_one(model: str, prompt: str, *, non_interactive: bool) -> str:
        seen_models.append(model)
        raise ai_runner.AIError("nope")

    monkeypatch.setattr(ai_runner, "_call_one", fake_call_one)

    with pytest.raises(ai_runner.AIError):
        ai_runner.run_ai("hi", preferred="claude", use_cache=False, fallback=False)
    assert seen_models == ["claude"]
