"""`devkit config` — show, set, and reset `~/.devkit/config.json`.

The config sub-app is intentionally small: everything is JSON on disk, and the
commands here just present it nicely and persist changes.
"""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.panel import Panel
from rich.syntax import Syntax

from devkit.config import CONFIG_FILE, DEFAULTS, load_config, save_config
from devkit.utils.display import console

app = typer.Typer(help="Manage ~/.devkit/config.json")

_ALLOWED_AI_TOOLS = {"claude", "gemini", "copilot"}


@app.command("show")
def show() -> None:
    """Print the resolved configuration (defaults merged with overrides)."""
    cfg = load_config()
    body = json.dumps(cfg, indent=2)
    console.print(
        Panel(
            Syntax(body, "json", theme="ansi_dark", line_numbers=False),
            title=f"devkit config — {CONFIG_FILE}",
            border_style="cyan",
        )
    )


@app.command("path")
def path() -> None:
    """Print the absolute path of the config file."""
    console.print(str(CONFIG_FILE))


@app.command("set")
def set_value(
    key: str = typer.Argument(..., help="Config key to set"),
    value: str = typer.Argument(..., help="New value (parsed as JSON, falls back to string)"),
) -> None:
    """Set a single key in the config file.

    The value is parsed as JSON first (so `true`, `false`, numbers, and quoted
    strings all work). If JSON parsing fails, the raw string is stored.
    """
    if key not in DEFAULTS:
        console.print(
            f"[yellow]Warning:[/yellow] '{key}' is not a known key. "
            f"Known keys: {', '.join(DEFAULTS)}."
        )

    parsed: Any
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = value

    if key == "ai_tool" and isinstance(parsed, str) and parsed.lower() not in _ALLOWED_AI_TOOLS:
        console.print(
            f"[red]Invalid ai_tool:[/red] {parsed!r}. "
            f"Allowed values: {sorted(_ALLOWED_AI_TOOLS)}."
        )
        raise typer.Exit(code=1)

    cfg = load_config()
    cfg[key] = parsed
    save_config(cfg)
    console.print(f"[green]Saved[/green] {key} = {json.dumps(parsed)} to {CONFIG_FILE}")


@app.command("reset")
def reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip the confirmation prompt"),
) -> None:
    """Reset the config file to default values."""
    if not yes:
        confirm = typer.confirm(f"Overwrite {CONFIG_FILE} with defaults?")
        if not confirm:
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit()
    save_config(DEFAULTS.copy())
    console.print(f"[green]Reset[/green] {CONFIG_FILE} to defaults.")
