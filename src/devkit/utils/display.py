from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
err_console = Console(stderr=True)


def info_panel(title: str, body: str, border_style: str = "cyan") -> Panel:
    return Panel(body or "(empty)", title=title, border_style=border_style)


def simple_table(title: str, columns: list[tuple[str, str | None]], border_style: str = "green") -> Table:
    table = Table(title=title, border_style=border_style, show_lines=False)
    for header, style in columns:
        if style:
            table.add_column(header, style=style)
        else:
            table.add_column(header)
    return table
