from __future__ import annotations

import subprocess

import typer
from rich.panel import Panel
from rich.table import Table

from devkit.config import load_config
from devkit.utils.check import require_tools
from devkit.utils.display import console
from devkit.utils.gh import gh, gh_json

app = typer.Typer(help="End-to-end development workflows")


@app.command("feature-start")
def feature_start(
    name: str = typer.Argument(..., help="Feature name in kebab-case"),
    issue: int | None = typer.Option(None, help="Issue number to link"),
) -> None:
    """Create a feature branch, push it, open a draft PR, and optionally ask AI for an implementation plan."""
    cfg = load_config()
    ai_tool = str(cfg.get("ai_tool", "claude")).lower()

    base_tools = ["git", "gh"]
    if issue:
        base_tools.append("gemini" if ai_tool == "gemini" else "claude")
    require_tools(base_tools)

    console.rule("[bold]Starting Feature[/bold]")

    branch = f"feature/{name}"
    try:
        subprocess.run(["git", "checkout", "-b", branch], check=True)
        console.print(f"[green]Created branch:[/green] {branch}")
    except subprocess.CalledProcessError:
        console.print("[red]Error: Could not create branch.[/red]")
        console.print("[yellow]Make sure you're in a Git repository (run 'git init' if needed)[/yellow]")
        raise typer.Exit(1)

    try:
        subprocess.run(["git", "push", "-u", "origin", branch], check=True)
        console.print(f"[green]Pushed branch:[/green] {branch}")
    except subprocess.CalledProcessError:
        console.print("[red]Error: Could not push branch to remote.[/red]")
        console.print("[yellow]Make sure 'origin' remote is configured (run 'git remote add origin <url>')[/yellow]")
        raise typer.Exit(1)

    pr_title = name.replace("-", " ").title()
    pr_args = ["pr", "create", "--draft", "--title", pr_title, "--body", ""]
    if issue is not None:
        pr_args = ["pr", "create", "--draft", "--title", pr_title, "--body", f"Closes #{issue}"]
    
    try:
        pr_url = gh(*pr_args)
        console.print(f"[green]Draft PR:[/green] {pr_url}")
    except RuntimeError as e:
        console.print("[red]Error: Could not create Pull Request on GitHub.[/red]")
        if "known GitHub host" in str(e):
            console.print("[yellow]Your remote is not a GitHub repository.[/yellow]")
            console.print("[yellow]Make sure you've set up a GitHub remote: git remote set-url origin <github-url>[/yellow]")
        else:
            console.print(f"[yellow]Details: {str(e)[:200]}[/yellow]")
        raise typer.Exit(1)

    if issue is not None:
        issue_info = gh_json("issue", "view", str(issue), "--json", "title,body")
        prompt = (
            "I'm starting work on this GitHub issue. "
            "Create a step-by-step implementation plan.\n\n"
            f"Title: {issue_info.get('title', '')}\n\n"
            f"Body:\n{issue_info.get('body') or '(no body)'}"
        )
        ai_cmd = (
            ["gemini", prompt] if ai_tool == "gemini" else ["claude", "--no-interactive", prompt]
        )
        result = subprocess.run(ai_cmd, capture_output=True, text=True, check=False)
        output = result.stdout.strip() or result.stderr.strip() or "No AI plan returned."
        console.print(
            Panel(output, title="[cyan]AI Implementation Plan[/cyan]", border_style="cyan")
        )

    console.rule("[green]Ready to code![/green]")


@app.command("daily-digest")
def daily_digest(
    repo: str = typer.Option("", help="owner/repo (default: current repo)"),
    limit: int = typer.Option(10, help="Max items per section"),
) -> None:
    """Show a daily developer digest: PRs needing review, assigned issues, latest CI runs.

    This is the command to run with your morning coffee - it gathers the three
    lists you usually open three browser tabs for, and renders them in one view.
    """
    require_tools(["gh"])

    console.rule("[bold]Daily Digest[/bold]")

    me = _current_user()

    # 1. PRs awaiting my review
    search_args = [
        "search",
        "prs",
        f"is:open review-requested:{me}",
        "--limit",
        str(limit),
        "--json",
        "number,title,repository,url,author",
    ]
    review_prs = gh_json(*search_args)
    review_table = Table(title=f"PRs awaiting review from @{me}", border_style="magenta")
    review_table.add_column("#", style="cyan", no_wrap=True)
    review_table.add_column("Repo", style="green")
    review_table.add_column("Title")
    review_table.add_column("Author", style="yellow")
    for item in review_prs:
        repo_name = (item.get("repository") or {}).get("nameWithOwner", "")
        author = (item.get("author") or {}).get("login", "unknown")
        review_table.add_row(
            str(item.get("number", "")), repo_name, item.get("title", ""), author
        )
    if review_prs:
        console.print(review_table)
    else:
        console.print(
            Panel(
                f"No PRs need review from @{me}. [green]Inbox zero.[/green]",
                border_style="magenta",
            )
        )

    # 2. Issues assigned to me
    assigned_args = [
        "search",
        "issues",
        f"is:open assignee:{me}",
        "--limit",
        str(limit),
        "--json",
        "number,title,repository,url",
    ]
    assigned = gh_json(*assigned_args)
    issue_table = Table(title=f"Issues assigned to @{me}", border_style="yellow")
    issue_table.add_column("#", style="cyan", no_wrap=True)
    issue_table.add_column("Repo", style="green")
    issue_table.add_column("Title")
    for item in assigned:
        repo_name = (item.get("repository") or {}).get("nameWithOwner", "")
        issue_table.add_row(str(item.get("number", "")), repo_name, item.get("title", ""))
    if assigned:
        console.print(issue_table)
    else:
        console.print(Panel(f"No open issues assigned to @{me}.", border_style="yellow"))

    # 3. Latest CI runs in the current repo
    run_args = [
        "run",
        "list",
        "--limit",
        str(limit),
        "--json",
        "displayTitle,workflowName,status,conclusion,headBranch,createdAt",
    ]
    if repo:
        run_args.extend(["--repo", repo])
    runs = gh_json(*run_args)
    run_table = Table(title="Latest CI runs (current repo)", border_style="blue")
    run_table.add_column("Workflow", style="cyan")
    run_table.add_column("Branch", style="green")
    run_table.add_column("Status", style="yellow")
    run_table.add_column("Conclusion")
    for run in runs:
        conclusion = run.get("conclusion") or "-"
        if conclusion == "success":
            styled = f"[green]{conclusion}[/green]"
        elif conclusion == "failure":
            styled = f"[red]{conclusion}[/red]"
        else:
            styled = conclusion
        run_table.add_row(
            run.get("workflowName", ""),
            run.get("headBranch", ""),
            run.get("status", ""),
            styled,
        )
    if runs:
        console.print(run_table)
    else:
        console.print(Panel("No recent workflow runs.", border_style="blue"))

    console.rule("[green]End of digest[/green]")


def _current_user() -> str:
    """Return the authenticated GitHub login via `gh api user`."""
    try:
        user = gh_json("api", "user", "--jq", ".login")
    except Exception:  # pragma: no cover - depends on gh state
        return "@me"
    if isinstance(user, str):
        return user
    return "@me"


@app.command("ship")
def ship(
    title: str | None = typer.Option(None, help="PR title (default: AI-generated from diff)"),
    draft: bool = typer.Option(False, help="Open the PR as draft"),
    skip_tests: bool = typer.Option(False, help="Skip running pytest before pushing"),
    skip_review: bool = typer.Option(False, help="Skip the AI self-review step"),
) -> None:
    """End-to-end ship workflow: tests -> AI commit -> push -> AI summary -> open PR.

    The "send-it" command. Runs the local test suite, generates a commit
    message from the staged diff with AI, pushes the branch, asks the AI for
    a one-paragraph PR description, then opens the PR.
    """
    from devkit.utils.ai_runner import run_ai, AIError
    from devkit.plugins import fire as fire_hook

    cfg = load_config()
    ai_tool = str(cfg.get("ai_tool", "claude")).lower()
    require_tools(["git", "gh"])

    console.rule("[bold]Shipping[/bold]")

    # 1. Run the test suite (unless --skip-tests).
    if not skip_tests:
        console.print("[cyan]Running pytest...[/cyan]")
        result = subprocess.run(["pytest", "-x", "--tb=short"], check=False)
        if result.returncode != 0:
            console.print("[red]Tests failed. Aborting ship.[/red]")
            raise typer.Exit(code=1)
        console.print("[green]Tests passed.[/green]")

    # 2. Stage everything not yet staged, then build a commit message.
    diff_staged = subprocess.check_output(["git", "diff", "--staged"], text=True)
    if not diff_staged.strip():
        subprocess.run(["git", "add", "-u"], check=False)
        diff_staged = subprocess.check_output(["git", "diff", "--staged"], text=True)

    commit_msg = "chore: update"
    if diff_staged.strip():
        prompt = (
            "Write one concise conventional commit subject line for these "
            "staged changes. Return only the subject line.\n\n"
            f"{diff_staged[:3000]}"
        )
        try:
            res = run_ai(prompt, preferred=ai_tool, non_interactive=True)
            commit_msg = res.response.splitlines()[0].strip() or commit_msg
        except AIError:
            pass
        fire_hook("pre_commit", {"message": commit_msg})
        subprocess.run(["git", "commit", "-m", commit_msg], check=False)
        console.print(f"[green]Committed:[/green] {commit_msg}")
    else:
        console.print("[yellow]Nothing to commit.[/yellow]")

    # 3. Push the current branch.
    branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
    ).strip()
    subprocess.run(["git", "push", "-u", "origin", branch], check=True)
    console.print(f"[green]Pushed[/green] {branch}")

    # 4. Generate a PR body via AI.
    body = ""
    if not skip_review:
        has_main = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", "refs/heads/main"],
            check=False,
        ).returncode == 0
        log_since_main = ""
        if has_main:
            log_since_main = subprocess.check_output(
                ["git", "log", "main..HEAD", "--pretty=format:%s%n%b%n---END---"],
                text=True,
                stderr=subprocess.DEVNULL,
            )

        prompt = (
            "Write a 3-paragraph GitHub PR description for these commits. "
            "Sections: ## What / ## Why / ## How to test. Markdown only.\n\n"
            f"{log_since_main or diff_staged[:3000]}"
        )
        try:
            res = run_ai(prompt, preferred=ai_tool, non_interactive=True)
            body = res.response
        except AIError as exc:
            console.print(f"[yellow]AI description skipped:[/yellow] {exc}")

    # 5. Open the PR.
    pr_title = title or commit_msg
    pr_args = ["pr", "create", "--title", pr_title, "--body", body or "(generated by devkit ship)"]
    if draft:
        pr_args.append("--draft")
    url = gh(*pr_args)
    fire_hook("post_pr_open", {"url": url, "branch": branch, "title": pr_title})

    console.rule("[green]Shipped![/green]")
    console.print(Panel(url, title="[green]Pull Request[/green]", border_style="green"))


@app.command("ship")
def ship(
    title: str | None = typer.Option(None, help="PR title (default: AI-generated from diff)"),
    draft: bool = typer.Option(False, help="Open the PR as draft"),
    skip_tests: bool = typer.Option(False, help="Skip running pytest before pushing"),
    skip_review: bool = typer.Option(False, help="Skip the AI self-review step"),
) -> None:
    """End-to-end ship workflow: tests -> AI commit -> push -> AI summary -> open PR."""
    from devkit.utils.ai_runner import run_ai, AIError
    from devkit.plugins import fire as fire_hook

    cfg = load_config()
    ai_tool = str(cfg.get("ai_tool", "claude")).lower()
    require_tools(["git", "gh"])

    console.rule("[bold]Shipping[/bold]")

    if not skip_tests:
        console.print("[cyan]Running pytest...[/cyan]")
        result = subprocess.run(["pytest", "-x", "--tb=short"], check=False)
        if result.returncode != 0:
            console.print("[red]Tests failed. Aborting ship.[/red]")
            raise typer.Exit(code=1)
        console.print("[green]Tests passed.[/green]")

    diff_staged = subprocess.check_output(["git", "diff", "--staged"], text=True)
    if not diff_staged.strip():
        subprocess.run(["git", "add", "-u"], check=False)
        diff_staged = subprocess.check_output(["git", "diff", "--staged"], text=True)

    commit_msg = "chore: update"
    if diff_staged.strip():
        prompt = (
            "Write one concise conventional commit subject line for these "
            "staged changes. Return only the subject line.\n\n"
            f"{diff_staged[:3000]}"
        )
        try:
            res = run_ai(prompt, preferred=ai_tool, non_interactive=True)
            commit_msg = res.response.splitlines()[0].strip() or commit_msg
        except AIError:
            pass
        fire_hook("pre_commit", {"message": commit_msg})
        subprocess.run(["git", "commit", "-m", commit_msg], check=False)
        console.print(f"[green]Committed:[/green] {commit_msg}")
    else:
        console.print("[yellow]Nothing to commit.[/yellow]")

    branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
    ).strip()
    subprocess.run(["git", "push", "-u", "origin", branch], check=True)
    console.print(f"[green]Pushed[/green] {branch}")

    body = ""
    if not skip_review:
        has_main = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", "refs/heads/main"],
            check=False,
        ).returncode == 0
        log_since_main = ""
        if has_main:
            log_since_main = subprocess.check_output(
                ["git", "log", "main..HEAD", "--pretty=format:%s%n%b%n---END---"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
        prompt = (
            "Write a 3-paragraph GitHub PR description for these commits. "
            "Sections: ## What / ## Why / ## How to test. Markdown only.\n\n"
            f"{log_since_main or diff_staged[:3000]}"
        )
        try:
            res = run_ai(prompt, preferred=ai_tool, non_interactive=True)
            body = res.response
        except AIError as exc:
            console.print(f"[yellow]AI description skipped:[/yellow] {exc}")

    pr_title = title or commit_msg
    pr_args = ["pr", "create", "--title", pr_title, "--body", body or "(generated by devkit ship)"]
    if draft:
        pr_args.append("--draft")
    url = gh(*pr_args)
    fire_hook("post_pr_open", {"url": url, "branch": branch, "title": pr_title})

    console.rule("[green]Shipped![/green]")
    console.print(Panel(url, title="[green]Pull Request[/green]", border_style="green"))
