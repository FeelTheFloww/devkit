"""Disk-backed cache for AI prompt responses.

AI calls are slow (1-30s) and not free. The cache stores responses keyed by a
SHA-256 hash of the (model, prompt) tuple. Cache lives in
``~/.devkit/cache/`` so it survives between sessions but is local-only.

Usage::

    from devkit.utils.cache import cached_or_compute

    response = cached_or_compute("claude", prompt, lambda: call_claude(prompt))

The cache silently skips on any I/O error (it's a perf optimisation, not a
source of truth) and exposes ``clear()`` for the ``devkit cache clear``
command.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Callable

CACHE_DIR = Path.home() / ".devkit" / "cache"
DEFAULT_TTL_SECONDS = 24 * 3600  # 1 day


def _key(model: str, prompt: str) -> str:
    """Return the SHA-256 hex digest used as the cache filename."""
    h = hashlib.sha256()
    h.update(model.encode("utf-8"))
    h.update(b"\0")
    h.update(prompt.encode("utf-8"))
    return h.hexdigest()


def _path_for(model: str, prompt: str) -> Path:
    return CACHE_DIR / f"{_key(model, prompt)}.json"


def get(model: str, prompt: str, *, ttl: int = DEFAULT_TTL_SECONDS) -> str | None:
    """Return cached response or ``None`` if missing / expired / corrupt."""
    path = _path_for(model, prompt)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if time.time() - payload.get("ts", 0) > ttl:
        return None
    response = payload.get("response")
    return response if isinstance(response, str) else None


def put(model: str, prompt: str, response: str) -> None:
    """Persist ``response`` for the given (model, prompt). Best-effort."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = _path_for(model, prompt)
        path.write_text(
            json.dumps({"ts": time.time(), "model": model, "response": response}),
            encoding="utf-8",
        )
    except OSError:
        # Cache failure must never break a real command.
        pass


def cached_or_compute(
    model: str,
    prompt: str,
    compute: Callable[[], str],
    *,
    ttl: int = DEFAULT_TTL_SECONDS,
    use_cache: bool = True,
) -> str:
    """Look up the cache; on miss, call ``compute()`` and store the result."""
    if use_cache:
        cached = get(model, prompt, ttl=ttl)
        if cached is not None:
            return cached
    response = compute()
    if use_cache and response:
        put(model, prompt, response)
    return response


def clear() -> int:
    """Delete all cached entries. Returns the number of files removed."""
    if not CACHE_DIR.exists():
        return 0
    removed = 0
    for path in CACHE_DIR.glob("*.json"):
        try:
            path.unlink()
            removed += 1
        except OSError:
            pass
    return removed


def stats() -> dict:
    """Return ``{count, total_bytes, oldest_age_s}`` for the cache."""
    if not CACHE_DIR.exists():
        return {"count": 0, "total_bytes": 0, "oldest_age_s": 0}
    files = list(CACHE_DIR.glob("*.json"))
    total = sum(p.stat().st_size for p in files)
    if files:
        oldest = min(p.stat().st_mtime for p in files)
        oldest_age = int(time.time() - oldest)
    else:
        oldest_age = 0
    return {"count": len(files), "total_bytes": total, "oldest_age_s": oldest_age}
