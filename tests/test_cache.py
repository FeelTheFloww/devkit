"""Tests for the disk-backed AI response cache."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

import devkit.utils.cache as cache_module


@pytest.fixture()
def temp_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect CACHE_DIR to a throwaway location."""
    fake = tmp_path / "cache"
    monkeypatch.setattr(cache_module, "CACHE_DIR", fake)
    return fake


def test_get_returns_none_when_empty(temp_cache: Path) -> None:
    assert cache_module.get("claude", "hello") is None


def test_put_then_get_round_trip(temp_cache: Path) -> None:
    cache_module.put("claude", "hello", "hi there")
    assert cache_module.get("claude", "hello") == "hi there"


def test_different_models_produce_different_keys(temp_cache: Path) -> None:
    cache_module.put("claude", "x", "from-claude")
    cache_module.put("gemini", "x", "from-gemini")
    assert cache_module.get("claude", "x") == "from-claude"
    assert cache_module.get("gemini", "x") == "from-gemini"


def test_expired_entries_return_none(temp_cache: Path) -> None:
    cache_module.put("claude", "old", "stale")
    # Force-rewrite with an old timestamp
    path = temp_cache / f"{cache_module._key('claude', 'old')}.json"
    import json
    payload = json.loads(path.read_text())
    payload["ts"] = time.time() - 10_000
    path.write_text(json.dumps(payload))
    assert cache_module.get("claude", "old", ttl=60) is None


def test_clear_removes_all_entries(temp_cache: Path) -> None:
    cache_module.put("claude", "a", "1")
    cache_module.put("claude", "b", "2")
    assert cache_module.stats()["count"] == 2
    removed = cache_module.clear()
    assert removed == 2
    assert cache_module.stats()["count"] == 0


def test_cached_or_compute_calls_compute_once(temp_cache: Path) -> None:
    calls = {"n": 0}

    def compute() -> str:
        calls["n"] += 1
        return "result"

    a = cache_module.cached_or_compute("claude", "p", compute)
    b = cache_module.cached_or_compute("claude", "p", compute)
    assert a == b == "result"
    assert calls["n"] == 1  # second call hit the cache


def test_cached_or_compute_skips_cache_when_disabled(temp_cache: Path) -> None:
    calls = {"n": 0}

    def compute() -> str:
        calls["n"] += 1
        return f"call-{calls['n']}"

    cache_module.cached_or_compute("claude", "p", compute, use_cache=False)
    cache_module.cached_or_compute("claude", "p", compute, use_cache=False)
    assert calls["n"] == 2


def test_get_handles_corrupt_json(temp_cache: Path) -> None:
    path = temp_cache / f"{cache_module._key('claude', 'x')}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not json {")
    assert cache_module.get("claude", "x") is None


def test_stats_on_empty_cache(temp_cache: Path) -> None:
    s = cache_module.stats()
    assert s == {"count": 0, "total_bytes": 0, "oldest_age_s": 0}
