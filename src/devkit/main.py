from __future__ import annotations

import typer
from rich.panel import Panel

from devkit.commands import ai, cache_cmd, config_cmd
from devkit.commands import doctor as doctor_module
from devkit.commands import github, workflow
from devkit.plugins import register_with
from devkit.utils.display import console

app = typer.Typer(
    name="devkit",
    help="AI-powered developer toolkit",
    rich_markup_mode="rich",
)

app.add_typer(github.app, name="gh", help="GitHub operations")
app.add_typer(ai.app, name="ai", help="AI tools (Copilot, Gemini, Claude)")
app.add_typer(workflow.app, name="workflow", help="End-to-end development workflows")
app.add_typer(config_cmd.app, name="config", help="Manage ~/.devkit/config.json")
app.add_typer(cache_cmd.app, name="cache", help="Manage AI response cache")
app.command("doctor", help="Diagnose the local toolchain and config")(doctor_module.doctor)

# Mount user-installed plugin commands under `devkit plugin <name>`.
register_with(app)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Print a welcome panel and the help text when run with no subcommand."""
    if ctx.invoked_subcommand is None:
        console.print(Panel("Welcome to [bold cyan]devkit[/bold cyan]", border_style="cyan"))
        console.print(ctx.get_help())


def run() -> None:
    """Entry point declared in pyproject.toml."""
    app()


if __name__ == "__main__":
    run()
