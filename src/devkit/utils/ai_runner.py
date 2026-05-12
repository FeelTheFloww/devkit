"""Single entry point for calling AI CLI binaries.

This module owns:

* the list of supported backends (``claude``, ``gemini``, ``copilot``),
* the fallback chain (``claude`` -> ``gemini`` if claude is missing),
* prompt-length truncation (long prompts blow up command-line length on
  Windows and produce poor responses anyway),
* the integration with :mod:`devkit.utils.cache`.

Every command in :mod:`devkit.commands.ai` and
:mod:`devkit.commands.workflow` should go through :func:`run_ai` rather than
spawning ``subprocess`` directly. This keeps fallback logic in one place.

About Copilot
-------------
``gh copilot`` is invoked as ``gh copilot suggest --target shell <prompt>``.
It's purpose-built for **shell-command** suggestions — using it to "review a
PR" returns nonsense. Copilot is therefore *opt-in*: it has to be requested
explicitly via ``--model copilot``. The default fallback chain stays
``(claude, gemini)`` to avoid surprises.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass

from devkit.utils.cache import cached_or_compute

MAX_PROMPT_CHARS = 6000

#: All AI backends devkit knows how to drive.
SUPPORTED_MODELS = ("claude", "gemini", "copilot")

#: Backends devkit auto-falls-back to when the preferred one is missing.
#: Copilot is *not* in this chain because it's specialised for shell commands
#: (using it to summarise a PR would produce garbage). Users can still pass
#: ``--model copilot`` explicitly.
DEFAULT_FALLBACK_CHAIN = ("claude", "gemini")


class AIError(RuntimeError):
    """Raised when no AI backend can be reached or all backends fail."""


@dataclass(frozen=True)
class AIResult:
    model: str
    response: str
    cached: bool


def truncate_prompt(prompt: str, *, limit: int = MAX_PROMPT_CHARS) -> str:
    """Trim a prompt to ``limit`` chars, tagging the cut point."""
    if len(prompt) <= limit:
        return prompt
    return prompt[:limit] + f"\n\n... [truncated {len(prompt) - limit} chars]"


def _backend_args(model: str, prompt: str, *, non_interactive: bool) -> list[str]:
    """Translate a (model, prompt) pair into the actual subprocess argv."""
    if model == "claude":
        args = ["claude"]
        if non_interactive:
            args.append("--no-interactive")
        args.append(prompt)
        return args
    if model == "gemini":
        return ["gemini", prompt]
    if model == "copilot":
        # `gh copilot suggest` returns a shell-command suggestion. We use
        # --target shell as the most general option; for explanation tasks
        # callers should use `gh copilot explain` directly.
        return ["gh", "copilot", "suggest", "--target", "shell", prompt]
    raise AIError(f"Unknown AI backend: {model}")


def _binary_for(model: str) -> str:
    """Return the executable name `shutil.which` should look for."""
    return "gh" if model == "copilot" else model


def _call_one(model: str, prompt: str, *, non_interactive: bool) -> str:
    args = _backend_args(model, prompt, non_interactive=non_interactive)
    binary = _binary_for(model)
    resolved = shutil.which(binary)
    if not resolved:
        raise AIError(f"{binary} not installed")
    # On Windows, npm installs shims like `claude.cmd`. `shutil.which()` finds
    # them (it honours PATHEXT) but `subprocess.run(["claude", ...])` without
    # `shell=True` does not search PATHEXT and fails with "file not found".
    # Replacing args[0] with the resolved path and using shell=True on Windows
    # ensures proper execution.
    args[0] = resolved
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
        shell=(os.name == 'nt'),
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "command failed").strip()
        raise AIError(f"{model} failed: {details}")
    return result.stdout.strip()


def run_ai(
    prompt: str,
    *,
    preferred: str = "claude",
    non_interactive: bool = False,
    use_cache: bool = True,
    fallback: bool = True,
) -> AIResult:
    """Call the preferred backend; fall back to the next one on failure.

    Parameters
    ----------
    prompt:
        The full prompt sent to the AI binary. Will be truncated to
        :data:`MAX_PROMPT_CHARS`.
    preferred:
        ``"claude"``, ``"gemini"``, or ``"copilot"`` -- tried first.
    non_interactive:
        Adds ``--no-interactive`` for Claude (no effect for Gemini/Copilot).
    use_cache:
        Look up / store responses in :mod:`devkit.utils.cache`.
    fallback:
        If the preferred backend is missing or fails, try the others
        from :data:`DEFAULT_FALLBACK_CHAIN`. Copilot is never auto-tried;
        it must be requested explicitly.

    Returns
    -------
    AIResult
        Includes the *actual* model that produced the response and a
        ``cached`` flag.

    Raises
    ------
    AIError
        If every candidate backend fails.
    """
    prompt = truncate_prompt(prompt)
    candidates = [preferred]
    if fallback:
        for model in DEFAULT_FALLBACK_CHAIN:
            if model not in candidates:
                candidates.append(model)

    last_error: str | None = None
    for model in candidates:
        # Cache lookup BEFORE invoking subprocess.
        if use_cache:
            from devkit.utils.cache import get as cache_get
            cached = cache_get(model, prompt)
            if cached is not None:
                return AIResult(model=model, response=cached, cached=True)

        try:
            response = cached_or_compute(
                model,
                prompt,
                lambda m=model: _call_one(m, prompt, non_interactive=non_interactive),
                use_cache=use_cache,
            )
            return AIResult(model=model, response=response, cached=False)
        except AIError as exc:
            last_error = str(exc)
            continue

    raise AIError(
        f"All AI backends failed (tried {', '.join(candidates)}): {last_error}"
    )
