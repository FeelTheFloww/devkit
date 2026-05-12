from __future__ import annotations

import shutil
from collections.abc import Iterable

from devkit.utils.display import err_console

TOOL_HINTS: dict[str, str] = {
    "gh": "Install GitHub CLI from https://cli.github.com and run `gh auth login`.",
    "git": "Install Git and make sure it is available in your PATH.",
    "fzf": "Install fzf and make sure it is available in your PATH.",
    "bat": "Install bat and make sure it is available in your PATH.",
    "delta": "Install git-delta and make sure it is available in your PATH.",
    "gemini": "Install Gemini CLI and authenticate it before using AI review commands.",
    "claude": "Install Claude Code / Claude CLI and authenticate it before using AI review commands.",
}


def require_tools(tools: Iterable[str]) -> None:
    missing = [tool for tool in tools if not shutil.which(tool)]
    if not missing:
        return

    err_console.print("[red]Missing required tools:[/red]")
    for tool in missing:
        hint = TOOL_HINTS.get(tool, "Install this tool and retry.")
        err_console.print(f"  [cyan]{tool}[/cyan] — {hint}")
    raise SystemExit(1)


def tool_available(name: str) -> bool:
    return shutil.which(name) is not None
