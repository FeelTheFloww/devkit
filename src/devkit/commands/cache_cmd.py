"""`devkit cache` — inspect and clear the AI response cache."""

from __future__ import annotations

import typer
from rich.panel import Panel

from devkit.utils import cache as cache_module
from devkit.utils.display import console

app = typer.Typer(help="Manage the AI response cache (~/.devkit/cache/)")


def _human_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _human_age(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    return f"{seconds // 86400}d"


@app.command("info")
def info() -> None:
    """Show cache directory, entry count, and total size."""
    s = cache_module.stats()
    body = (
        f"[bold]Path:[/bold] {cache_module.CACHE_DIR}\n"
        f"[bold]Entries:[/bold] {s['count']}\n"
        f"[bold]Size:[/bold] {_human_bytes(s['total_bytes'])}\n"
        f"[bold]Oldest entry:[/bold] {_human_age(s['oldest_age_s']) if s['count'] else '-'}"
    )
    console.print(Panel(body, title="AI cache", border_style="cyan"))


@app.command("clear")
def clear(yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")) -> None:
    """Delete every cached AI response."""
    if not yes and not typer.confirm("Delete all cached AI responses?"):
        console.print("[yellow]Aborted.[/yellow]")
        raise typer.Exit()
    removed = cache_module.clear()
    console.print(f"[green]Deleted {removed} cache entries.[/green]")
