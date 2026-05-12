from __future__ import annotations

import subprocess

import typer
from rich.prompt import Confirm, Prompt

from devkit.utils.check import require_tools, tool_available
from devkit.utils.display import console, info_panel, simple_table
from devkit.utils.gh import gh, gh_json

app = typer.Typer(help="GitHub operations")


def _maybe_add_repo(args: list[str], repo: str) -> list[str]:
    if repo:
        args.extend(["--repo", repo])
    return args


def _fzf_select(items: list[str], prompt: str = "Select > ") -> str:
    result = subprocess.run(
        ["fzf", f"--prompt={prompt}", "--height=40%", "--border"],
        input="\n".join(items),
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


@app.command()
def issues(
    repo: str = typer.Option("", help="owner/repo (default: current repo)"),
    limit: int = typer.Option(15, help="Max number of issues"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Select an issue with fzf and open it in the browser"),
) -> None:
    """List open issues in a rich table."""
    require_tools(["gh"] + (["fzf"] if interactive else []))

    args = ["issue", "list", "--json", "number,title,state,labels,assignees", "--limit", str(limit)]
    data = gh_json(*_maybe_add_repo(args, repo))

    table = simple_table(
        "Open Issues",
        [("#", "cyan"), ("Title", None), ("Labels", "magenta"), ("Assignees", "yellow"), ("State", "green")],
    )
    for issue in data:
        labels = ", ".join(label["name"] for label in issue.get("labels", [])) or "—"
        assignees = ", ".join(user["login"] for user in issue.get("assignees", [])) or "—"
        table.add_row(str(issue["number"]), issue["title"], labels, assignees, issue["state"])
    console.print(table)

    if interactive and data:
        lines = [f"#{item['number']} {item['title']}" for item in data]
        selected = _fzf_select(lines, prompt="Issue > ")
        if selected:
            issue_num = selected.split()[0].lstrip("#")
            cmd = ["issue", "view", issue_num, "--web"]
            if repo:
                cmd.extend(["--repo", repo])
            gh(*cmd)


@app.command("pr-summary")
def pr_summary(
    pr_number: int = typer.Argument(..., help="Pull request number"),
    repo: str = typer.Option("", help="owner/repo (default: current repo)"),
) -> None:
    """Show PR overview and changed files."""
    require_tools(["gh"])

    view_args = ["pr", "view", str(pr_number), "--json", "title,body,files,reviews,author,state,url,headRefName,baseRefName"]
    info = gh_json(*_maybe_add_repo(view_args, repo))

    summary_lines = [
        f"[bold]Title:[/bold] {info.get('title', '')}",
        f"[bold]State:[/bold] {info.get('state', '')}",
        f"[bold]Author:[/bold] {(info.get('author') or {}).get('login', 'unknown')}",
        f"[bold]Branch:[/bold] {info.get('headRefName', '')} → {info.get('baseRefName', '')}",
        f"[bold]URL:[/bold] {info.get('url', '')}",
        "",
        "[bold]Body[/bold]",
        info.get("body") or "(no body)",
    ]
    console.print(info_panel(f"PR #{pr_number}", "\n".join(summary_lines), border_style="cyan"))

    files_table = simple_table("Changed Files", [("Path", None), ("Additions", "green"), ("Deletions", "red")], border_style="blue")
    for file in info.get("files", []):
        files_table.add_row(file.get("path", ""), str(file.get("additions", 0)), str(file.get("deletions", 0)))
    console.print(files_table)

    reviews = info.get("reviews", [])
    if reviews:
        review_table = simple_table("Reviews", [("Author", None), ("State", "yellow")], border_style="magenta")
        for review in reviews:
            author = (review.get("author") or {}).get("login", "unknown")
            review_table.add_row(author, review.get("state", ""))
        console.print(review_table)


@app.command("start-feature")
def start_feature(
    name: str = typer.Argument(..., help="Feature branch name, preferably kebab-case"),
    fork: bool = typer.Option(False, help="Fork the current repository before creating the branch"),
) -> None:
    """Optionally fork the repo, then create and switch to a feature branch."""
    require_tools(["gh", "git"])

    branch = f"feature/{name}"
    if fork:
        console.print("[cyan]Forking repository...[/cyan]")
        gh("repo", "fork", "--clone=false")

    subprocess.run(["git", "checkout", "-b", branch], check=True)
    console.print(f"[green]Created and checked out branch:[/green] {branch}")


@app.command("open-pr")
def open_pr(
    title: str | None = typer.Option(None, help="PR title"),
    body: str | None = typer.Option(None, help="PR body"),
    draft: bool = typer.Option(False, help="Create as draft PR"),
    repo: str = typer.Option("", help="owner/repo (default: current repo)"),
) -> None:
    """Create a pull request, prompting for missing fields."""
    require_tools(["gh"])

    final_title = title or Prompt.ask("PR title")
    final_body = body if body is not None else Prompt.ask("PR body", default="")

    args = ["pr", "create", "--title", final_title, "--body", final_body]
    if draft:
        args.append("--draft")
    if repo:
        args.extend(["--repo", repo])

    url = gh(*args)
    console.print(info_panel("PR Created", url, border_style="green"))


@app.command("run-status")
def run_status(
    repo: str = typer.Option("", help="owner/repo (default: current repo)"),
    limit: int = typer.Option(10, help="Number of workflow runs to show"),
) -> None:
    """Show the latest CI workflow runs."""
    require_tools(["gh"])

    args = ["run", "list", "--limit", str(limit), "--json", "displayTitle,workflowName,status,conclusion,headBranch,url,createdAt"]
    data = gh_json(*_maybe_add_repo(args, repo))

    table = simple_table(
        "Workflow Runs",
        [("Workflow", None), ("Branch", "cyan"), ("Status", "yellow"), ("Conclusion", "magenta"), ("Created", None)],
        border_style="yellow",
    )
    for run in data:
        table.add_row(
            run.get("workflowName", ""),
            run.get("headBranch", ""),
            run.get("status", ""),
            run.get("conclusion") or "—",
            run.get("createdAt", ""),
        )
    console.print(table)


@app.command("repo-init")
def repo_init(public: bool = typer.Option(True, help="Create the GitHub repository as public")) -> None:
    """Create the devkit repository and clone it, matching the project brief."""
    require_tools(["gh"])
    visibility_flag = "--public" if public else "--private"
    gh("repo", "create", "devkit", visibility_flag, "--clone")
    console.print("[green]Repository created and cloned.[/green]")


@app.command("search")
def search(
    query: str = typer.Argument(..., help='GitHub search query, e.g. "is:open label:bug"'),
    kind: str = typer.Option(
        "issues",
        help='What to search: "issues", "prs", "repos", or "code"',
    ),
    limit: int = typer.Option(20, help="Max number of results"),
) -> None:
    """Search GitHub across issues, PRs, repos, or code (`gh search` wrapper)."""
    require_tools(["gh"])
    valid = {"issues", "prs", "repos", "code"}
    if kind not in valid:
        console.print(f"[red]--kind must be one of {sorted(valid)}[/red]")
        raise typer.Exit(code=1)

    fields_by_kind = {
        "issues": "number,title,repository,url,state,labels",
        "prs": "number,title,repository,url,state,author",
        "repos": "name,description,url,stargazersCount,language",
        "code": "path,repository,url",
    }
    args = ["search", kind, query, "--limit", str(limit), "--json", fields_by_kind[kind]]
    data = gh_json(*args)

    if not data:
        console.print(f"[yellow]No {kind} results for:[/yellow] {query}")
        return

    if kind in {"issues", "prs"}:
        table = simple_table(
            f"{kind.upper()} matching: {query}",
            [("#", "cyan"), ("Repo", "green"), ("Title", None), ("State", "yellow")],
        )
        for item in data:
            repo_name = (item.get("repository") or {}).get("nameWithOwner", "")
            table.add_row(
                str(item.get("number", "")),
                repo_name,
                item.get("title", ""),
                item.get("state", ""),
            )
        console.print(table)
    elif kind == "repos":
        table = simple_table(
            f"Repositories matching: {query}",
            [("Repo", "green"), ("Stars", "yellow"), ("Lang", "cyan"), ("Description", None)],
        )
        for item in data:
            table.add_row(
                item.get("name", ""),
                str(item.get("stargazersCount", 0)),
                item.get("language") or "-",
                (item.get("description") or "")[:60],
            )
        console.print(table)
    else:  # code
        table = simple_table(
            f"Code matching: {query}",
            [("Repo", "green"), ("Path", None), ("URL", "cyan")],
        )
        for item in data:
            repo_name = (item.get("repository") or {}).get("nameWithOwner", "")
            table.add_row(repo_name, item.get("path", ""), item.get("url", ""))
        console.print(table)


@app.command("stats")
def stats(
    repo: str = typer.Option("", help="owner/repo (default: current repo)"),
    days: int = typer.Option(30, help="Look-back window in days"),
) -> None:
    """Aggregate repo activity over the last N days: PRs merged, issues opened/closed."""
    require_tools(["gh"])

    # Resolve "current repo" if --repo not given.
    if not repo:
        try:
            view = gh_json("repo", "view", "--json", "nameWithOwner")
            repo = view.get("nameWithOwner", "")
        except Exception:
            repo = ""
    if not repo:
        console.print("[red]Could not determine current repo. Pass --repo owner/name.[/red]")
        raise typer.Exit(code=1)

    from datetime import datetime, timedelta, timezone

    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    prs_merged = gh_json(
        "search", "prs",
        f"repo:{repo} is:merged merged:>{since}",
        "--limit", "100",
        "--json", "number,author",
    )
    issues_opened = gh_json(
        "search", "issues",
        f"repo:{repo} is:issue created:>{since}",
        "--limit", "100",
        "--json", "number",
    )
    issues_closed = gh_json(
        "search", "issues",
        f"repo:{repo} is:issue closed:>{since}",
        "--limit", "100",
        "--json", "number",
    )

    # Top contributors by PRs merged
    from collections import Counter
    contributors = Counter(
        (pr.get("author") or {}).get("login", "unknown") for pr in prs_merged
    )

    summary = simple_table(
        f"Repo stats - {repo} (last {days} days)",
        [("Metric", "cyan"), ("Count", "yellow")],
    )
    summary.add_row("PRs merged", str(len(prs_merged)))
    summary.add_row("Issues opened", str(len(issues_opened)))
    summary.add_row("Issues closed", str(len(issues_closed)))
    console.print(summary)

    if contributors:
        top = simple_table(
            "Top contributors (by merged PRs)",
            [("Contributor", "green"), ("Merged PRs", "yellow")],
            border_style="blue",
        )
        for login, count in contributors.most_common(10):
            top.add_row(login, str(count))
        console.print(top)
