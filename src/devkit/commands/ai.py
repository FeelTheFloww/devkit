from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path

import typer
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax

from devkit.config import load_config
from devkit.utils.check import require_tools
from devkit.utils.display import console
from devkit.utils.gh import gh, gh_json

app = typer.Typer(help="AI tools")

# Rough upper bound for diffs / files sent to an external AI binary as a
# positional argument. Long command lines fail on Windows cmd.exe and on some
# POSIX shells, so we truncate before calling the binary.
_MAX_PROMPT_CHARS = 6000


def _default_model() -> str:
    cfg = load_config()
    model = str(cfg.get("ai_tool", "claude")).strip().lower()
    return model if model in {"gemini", "claude", "copilot"} else "claude"


def _run_ai(model: str, prompt: str, *, non_interactive: bool = False) -> str:
    if model == "gemini":
        require_tools(["gemini"])
        args = ["gemini", prompt]
    else:
        require_tools(["claude"])
        args = ["claude"]
        if non_interactive:
            args.append("--no-interactive")
        args.append(prompt)

    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "AI command failed").strip()
        raise typer.BadParameter(details)
    return result.stdout.strip()


@app.command()
def explain(command: str = typer.Argument(..., help="Shell command to explain")) -> None:
    """Ask Copilot CLI to explain a shell command."""
    require_tools(["gh"])
    result = subprocess.run(
        ["gh", "copilot", "-p", f"explain {command}"],
        capture_output=True,
        text=True,
        check=False,
    )
    body = result.stdout.strip() or result.stderr.strip() or "No output"
    console.print(Panel(body, title="[purple]Copilot Explanation[/purple]", border_style="purple"))


@app.command()
def suggest(
    task: str = typer.Argument(..., help="Task to accomplish"),
    target: str = typer.Option("shell", help="Copilot target: shell, git, or gh"),
) -> None:
    """Ask Copilot CLI to suggest a command."""
    require_tools(["gh"])
    result = subprocess.run(
        ["gh", "copilot", "-p", f"suggest {task}"],
        capture_output=True,
        text=True,
        check=False,
    )
    body = result.stdout.strip() or result.stderr.strip() or "No output"
    console.print(Panel(body, title="[purple]Copilot Suggestion[/purple]", border_style="purple"))


@app.command()
def review(
    pr_number: int = typer.Argument(..., help="PR number to review"),
    model: str = typer.Option(None, help="AI tool: gemini or claude"),
) -> None:
    """AI-powered code review of a pull request."""
    require_tools(["gh"])
    model_name = (model or _default_model()).lower()

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task_id = progress.add_task("Fetching PR diff...", total=None)
        diff = gh("pr", "diff", str(pr_number))
        pr_info = gh_json("pr", "view", str(pr_number), "--json", "title,body")
        progress.update(task_id, description=f"Running {model_name} review...")
        prompt = (
            f'Review this PR titled "{pr_info.get("title", "")}". '
            "Focus on correctness, readability, risk, and missing tests.\n\n"
            f"PR body:\n{pr_info.get('body') or '(no body)'}\n\n"
            f"Diff:\n{diff[:_MAX_PROMPT_CHARS]}"
        )
        feedback = _run_ai(model_name, prompt)

    console.print(
        Panel(
            feedback or "No review output.",
            title=f"[cyan]AI Review - PR #{pr_number}[/cyan]",
            border_style="cyan",
        )
    )


@app.command()
def commit(model: str = typer.Option(None, help="AI tool: gemini or claude")) -> None:
    """Generate a conventional commit message from staged changes."""
    require_tools(["git"])
    model_name = (model or _default_model()).lower()

    # Verify we're in a git repository
    git_check = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
        check=False,
    )
    if git_check.returncode != 0:
        raise typer.BadParameter("Not in a git repository")

    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 and result.returncode != 1:
        # Exit code 1 means no changes, which is fine
        raise typer.BadParameter(f"git diff failed: {result.stderr or result.stdout}")
    
    diff = result.stdout
    if not diff.strip():
        console.print("[yellow]No staged changes.[/yellow]")
        raise typer.Exit()

    prompt = (
        "Write one concise conventional commit message for these staged changes. "
        "Return only the commit message line.\n\n"
        f"{diff[:3000]}"
    )
    suggested = _run_ai(model_name, prompt, non_interactive=True).splitlines()[0].strip()
    console.print(
        Panel(
            suggested or "No suggestion returned.",
            title="[green]Suggested Commit Message[/green]",
            border_style="green",
        )
    )

    if Confirm.ask("Use this message?", default=True):
        subprocess.run(["git", "commit", "-m", suggested], check=True)
    else:
        manual = Prompt.ask("Enter your commit message")
        subprocess.run(["git", "commit", "-m", manual], check=True)


@app.command()
def summarize(
    pr_number: int = typer.Argument(..., help="PR number to summarize"),
    model: str = typer.Option(None, help="AI tool: gemini or claude"),
    repo: str = typer.Option("", help="owner/repo (default: current repo)"),
) -> None:
    """Summarize a pull request in plain English for a non-technical reader."""
    require_tools(["gh"])
    model_name = (model or _default_model()).lower()

    view_args = ["pr", "view", str(pr_number), "--json", "title,body,author,headRefName,baseRefName"]
    diff_args = ["pr", "diff", str(pr_number)]
    if repo:
        view_args.extend(["--repo", repo])
        diff_args.extend(["--repo", repo])

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task_id = progress.add_task("Fetching PR metadata...", total=None)
        info = gh_json(*view_args)
        progress.update(task_id, description="Fetching PR diff...")
        diff = gh(*diff_args)
        progress.update(task_id, description=f"Summarizing with {model_name}...")
        prompt = (
            "Summarize the following GitHub pull request in plain English "
            "for a non-technical reader. "
            "Produce at most 5 short bullet points, each under 20 words. "
            "Return only the bullets, no preface.\n\n"
            f"Title: {info.get('title', '')}\n"
            f"Author: {(info.get('author') or {}).get('login', 'unknown')}\n"
            f"Body:\n{info.get('body') or '(no body)'}\n\n"
            f"Diff:\n{diff[:_MAX_PROMPT_CHARS]}"
        )
        summary = _run_ai(model_name, prompt)

    header = (
        f"[bold]{info.get('title', '')}[/bold]\n"
        f"[dim]by {(info.get('author') or {}).get('login', 'unknown')} - "
        f"{info.get('headRefName', '')} -> {info.get('baseRefName', '')}[/dim]\n\n"
    )
    console.print(
        Panel(
            header + (summary or "No summary returned."),
            title=f"[cyan]PR #{pr_number} - plain English[/cyan]",
            border_style="cyan",
        )
    )


@app.command()
def docstring(
    file: Path = typer.Argument(..., help="Python file to add docstrings to"),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Overwrite the file with the AI-generated version (default: preview only)",
    ),
    model: str = typer.Option(None, help="AI tool: gemini or claude"),
) -> None:
    """Generate Google-style docstrings for every function in a Python file."""
    if not file.exists():
        console.print(f"[red]File not found:[/red] {file}")
        raise typer.Exit(code=1)
    if file.suffix != ".py":
        console.print(f"[red]Expected a .py file, got:[/red] {file.suffix}")
        raise typer.Exit(code=1)

    model_name = (model or _default_model()).lower()
    source = file.read_text(encoding="utf-8")
    if len(source) > _MAX_PROMPT_CHARS:
        console.print(
            f"[yellow]File is large ({len(source)} chars). Truncating to "
            f"{_MAX_PROMPT_CHARS} chars before sending to {model_name}.[/yellow]"
        )
        source_for_prompt = source[:_MAX_PROMPT_CHARS]
    else:
        source_for_prompt = source

    prompt = (
        "Rewrite the following Python file so that every function and class has a "
        "concise Google-style docstring. Preserve the exact behaviour, existing "
        "imports, type hints, and formatting. Return only the complete rewritten "
        "Python source - no markdown fences, no commentary.\n\n"
        f"```python\n{source_for_prompt}\n```"
    )

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        progress.add_task(f"Asking {model_name} for docstrings...", total=None)
        result = _run_ai(model_name, prompt, non_interactive=True)

    cleaned = _strip_code_fence(result)
    if not cleaned.strip():
        console.print("[red]AI returned no content.[/red]")
        raise typer.Exit(code=1)

    console.print(
        Panel(
            Syntax(cleaned, "python", line_numbers=True, theme="ansi_dark"),
            title=f"[cyan]Docstring preview - {file.name}[/cyan]",
            border_style="cyan",
        )
    )

    if apply:
        backup = file.with_suffix(file.suffix + ".bak")
        backup.write_text(source, encoding="utf-8")
        file.write_text(cleaned, encoding="utf-8")
        console.print(
            f"[green]Applied.[/green] Backup written to [cyan]{backup}[/cyan]."
        )
    else:
        console.print(
            "[yellow]Preview only.[/yellow] Pass [cyan]--apply[/cyan] to overwrite the file."
        )


def _strip_code_fence(text: str) -> str:
    """Remove a leading ```python / trailing ``` fence if the model emitted one."""
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines)


@app.command()
def changelog(
    since: str = typer.Option("HEAD~20..HEAD", help="Git rev range, e.g. v1.0..HEAD"),
    model: str = typer.Option(None, help="AI tool: gemini or claude"),
) -> None:
    """Generate a Keep-a-Changelog formatted changelog from git log."""
    from devkit.utils.ai_runner import run_ai, AIError

    require_tools(["git"])
    model_name = (model or _default_model()).lower()

    log = subprocess.check_output(
        ["git", "log", "--pretty=format:%s%n%b%n---END---", since],
        text=True,
    )
    if not log.strip():
        console.print(f"[yellow]No commits in range:[/yellow] {since}")
        raise typer.Exit()

    prompt = (
        "Convert this git log into a Keep a Changelog Markdown section. "
        "Group commits under headings: ### Added / ### Changed / ### Fixed / "
        "### Removed. Use concise bullets. Skip merge commits and trivial chores. "
        "Return only the Markdown.\n\n"
        f"{log}"
    )
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        progress.add_task(f"Asking {model_name} for changelog...", total=None)
        try:
            result = run_ai(prompt, preferred=model_name, non_interactive=True)
        except AIError as exc:
            console.print(f"[red]AI failed:[/red] {exc}")
            raise typer.Exit(code=1)

    cached_marker = "  [dim](cached)[/dim]" if result.cached else ""
    console.print(
        Panel(
            result.response or "(no output)",
            title=f"[green]Changelog ({result.model}){cached_marker}[/green]",
            border_style="green",
        )
    )


@app.command("test-gen")
def test_gen(
    file: Path = typer.Argument(..., help="Python source file to generate tests for"),
    output: Path = typer.Option(None, "--output", "-o", help="Where to write the test file (default: tests/test_<name>.py)"),
    model: str = typer.Option(None, help="AI tool: gemini or claude"),
) -> None:
    """Generate a pytest test module for a given Python source file."""
    from devkit.utils.ai_runner import run_ai, AIError, truncate_prompt

    if not file.exists() or file.suffix != ".py":
        console.print(f"[red]Need a .py file, got:[/red] {file}")
        raise typer.Exit(code=1)

    model_name = (model or _default_model()).lower()
    source = file.read_text(encoding="utf-8")
    target = output or Path("tests") / f"test_{file.stem}.py"

    prompt = truncate_prompt(
        "Write a pytest test module for the following Python source. "
        "Use plain `def test_*` functions, monkeypatch for I/O, and cover the "
        "happy path plus one error case per public function. "
        "Return only the test file content - no markdown fences, no preamble.\n\n"
        f"```python\n{source}\n```"
    )

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        progress.add_task(f"Generating tests with {model_name}...", total=None)
        try:
            result = run_ai(prompt, preferred=model_name, non_interactive=True)
        except AIError as exc:
            console.print(f"[red]AI failed:[/red] {exc}")
            raise typer.Exit(code=1)

    cleaned = _strip_code_fence(result.response)
    if not cleaned.strip():
        console.print("[red]AI returned no content.[/red]")
        raise typer.Exit(code=1)

    console.print(
        Panel(
            Syntax(cleaned[:1500], "python", line_numbers=True, theme="ansi_dark"),
            title=f"[cyan]Tests preview - {target}[/cyan]",
            border_style="cyan",
        )
    )
    if Confirm.ask(f"Write to {target}?", default=True):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(cleaned, encoding="utf-8")
        console.print(f"[green]Wrote[/green] {target}")
    else:
        console.print("[yellow]Skipped write.[/yellow]")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask the AI"),
    model: str = typer.Option(None, help="AI tool: gemini or claude"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip the response cache"),
) -> None:
    """One-shot Q&A — uses cache + multi-AI fallback."""
    from devkit.utils.ai_runner import run_ai, AIError

    model_name = (model or _default_model()).lower()
    try:
        result = run_ai(
            question,
            preferred=model_name,
            non_interactive=True,
            use_cache=not no_cache,
        )
    except AIError as exc:
        console.print(f"[red]AI failed:[/red] {exc}")
        raise typer.Exit(code=1)

    label = f"[cyan]{result.model}[/cyan]" + ("  [dim](cached)[/dim]" if result.cached else "")
    console.print(Panel(result.response or "(no answer)", title=label, border_style="cyan"))
