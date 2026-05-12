"""`devkit doctor` — diagnose the local Modern CLI toolchain.

The goal of this command is to answer, in one shot, the question
"is my machine ready to run all devkit workflows end to end?".
It checks:

* whether each external binary is installed,
* the version reported by each binary (when the `--version` flag is
  supported),
* whether `gh` is authenticated,
* whether a `~/.devkit/config.json` file exists and is valid JSON,
* which AI backend devkit will use by default.

The output is a Rich table that groups tools by role so the user
immediately sees what is missing and what to install.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass

import typer
from rich.panel import Panel
from rich.table import Table

from devkit.config import CONFIG_FILE, load_config
from devkit.utils.check import TOOL_HINTS
from devkit.utils.display import console


@dataclass(frozen=True)
class ToolSpec:
    name: str
    role: str
    required: bool
    version_flag: tuple[str, ...] = ("--version",)


TOOLS: tuple[ToolSpec, ...] = (
    ToolSpec("git", "version control", required=True),
    ToolSpec("gh", "GitHub API", required=True),
    ToolSpec("python", "runtime", required=True),
    ToolSpec("fzf", "interactive picker", required=False),
    ToolSpec("bat", "syntax highlighting", required=False),
    ToolSpec("delta", "diff viewer", required=False),
    ToolSpec("lazygit", "git TUI", required=False),
    ToolSpec("atuin", "shell history", required=False),
    ToolSpec("gemini", "AI backend", required=False),
    ToolSpec("claude", "AI backend", required=False),
)


def _probe_version(tool: ToolSpec) -> str:
    """Return the first line of `<tool> --version` or an empty string."""
    try:
        result = subprocess.run(
            [tool.name, *tool.version_flag],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    output = (result.stdout or result.stderr or "").strip().splitlines()
    return output[0] if output else ""


def _gh_auth_status() -> tuple[bool, str]:
    """Return `(ok, message)` describing `gh auth status`."""
    if not shutil.which("gh"):
        return False, "gh not installed"
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )
    output = (result.stderr or result.stdout or "").strip()
    first_line = output.splitlines()[0] if output else ""
    return result.returncode == 0, first_line or "unknown state"


def _gh_copilot_installed() -> bool:
    if not shutil.which("gh"):
        return False
    result = subprocess.run(
        ["gh", "extension", "list"],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )
    return "copilot" in (result.stdout or "").lower()


def _config_status() -> tuple[bool, str]:
    if not CONFIG_FILE.exists():
        return False, f"not found ({CONFIG_FILE})"
    try:
        json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc.msg}"
    return True, str(CONFIG_FILE)


def doctor() -> None:
    """Report the health of the local modern-CLI toolchain."""
    table = Table(title="devkit doctor", border_style="cyan", show_lines=False)
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Role", style="magenta")
    table.add_column("Required", style="yellow")
    table.add_column("Status")
    table.add_column("Version / hint")

    missing_required: list[str] = []
    for tool in TOOLS:
        path = shutil.which(tool.name)
        if path:
            version = _probe_version(tool) or "(no --version)"
            table.add_row(
                tool.name,
                tool.role,
                "yes" if tool.required else "no",
                "[green]ok[/green]",
                version,
            )
        else:
            hint = TOOL_HINTS.get(tool.name, "install and retry")
            table.add_row(
                tool.name,
                tool.role,
                "yes" if tool.required else "no",
                "[red]missing[/red]" if tool.required else "[yellow]missing[/yellow]",
                hint,
            )
            if tool.required:
                missing_required.append(tool.name)

    console.print(table)

    # gh-specific checks
    auth_ok, auth_msg = _gh_auth_status()
    copilot_ok = _gh_copilot_installed()
    gh_table = Table(title="GitHub CLI", border_style="green")
    gh_table.add_column("Check")
    gh_table.add_column("Status")
    gh_table.add_column("Detail")
    gh_table.add_row(
        "gh auth status",
        "[green]ok[/green]" if auth_ok else "[red]failed[/red]",
        auth_msg,
    )
    gh_table.add_row(
        "gh-copilot extension",
        "[green]installed[/green]" if copilot_ok else "[yellow]missing[/yellow]",
        "gh extension install github/gh-copilot" if not copilot_ok else "",
    )
    console.print(gh_table)

    # Config file
    cfg_ok, cfg_msg = _config_status()
    cfg = load_config()
    config_body = (
        f"[bold]File:[/bold] {cfg_msg}\n"
        f"[bold]Valid:[/bold] {'yes' if cfg_ok else 'no'}\n"
        f"[bold]AI tool:[/bold] {cfg.get('ai_tool')}\n"
        f"[bold]Default repo:[/bold] {cfg.get('default_repo') or '(not set)'}\n"
        f"[bold]Theme:[/bold] {cfg.get('theme')}"
    )
    console.print(
        Panel(
            config_body,
            title="~/.devkit/config.json",
            border_style="green" if cfg_ok else "yellow",
        )
    )

    # Final verdict
    if missing_required:
        console.print(
            Panel(
                "[red]Missing required tools:[/red] " + ", ".join(missing_required),
                title="Verdict",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)

    console.print(
        Panel(
            "[green]All required tools are installed.[/green]\n"
            "Optional tools marked 'missing' are only needed for specific commands.",
            title="Verdict",
            border_style="green",
        )
    )
