# Phase 1 — Tool Discovery

This document captures what I observed while running each modern CLI tool in isolation
before wiring them together inside `devkit`. For every tool I record:

1. **What it does** — a one-line summary.
2. **What surprised me** — something that was not obvious from the marketing.
3. **A use case I want to try** — how I plan to chain it into `devkit`.

---

## `gh` — GitHub CLI

**What it does.** `gh` exposes the entire GitHub surface (repos, issues, PRs, releases,
Actions runs, gists, search, raw REST/GraphQL) as a first-class CLI that inherits your
OAuth session after `gh auth login`.

Commands run:

```bash
gh repo list --limit 10
gh issue list --repo cli/cli
gh pr list --repo cli/cli --state open
gh issue list --json number,title,state,labels,assignees --limit 20
```

**Surprise.** `gh` is scriptable far beyond what the help page implies: every listing
command accepts `--json <fields>` and returns a clean array — no scraping, no
`--format=table` parsing. That is what turns `gh` from an interactive tool into a proper
API client.

**Use case for devkit.** Wrap `gh issue list --json ...` and render a Rich table coloured
by state and labels (`devkit gh issues`). Same pattern for PRs and Actions runs.

---

## `gh copilot` — AI command suggestions & explanations

**What it does.** A `gh` extension (`gh extension install github/gh-copilot`) that calls
GitHub Copilot to translate natural language into shell / git / gh commands
(`suggest`) or explain an existing command (`explain`).

Commands run:

```bash
gh copilot suggest 'find all python files modified in the last week'
gh copilot explain 'find . -name *.py -mtime -7 -exec wc -l {} +'
gh copilot suggest --target git 'undo my last commit but keep changes staged'
```

**Surprise.** `--target` (`shell`, `git`, `gh`) dramatically changes the answer quality.
Targeting `gh` for "create a release from the latest tag" produces a ready-to-paste
`gh release create` invocation instead of a generic bash explanation.

**Use case for devkit.** `devkit ai explain "<cmd>"` and `devkit ai suggest "<task>"`
wrap those two calls and render the output in a purple Rich panel so the answer stays
visually distinct from regular shell output.

---

## `gemini` — Google Gemini AI in your terminal

**What it does.** A pipe-friendly AI CLI. You can pass a prompt as a positional argument,
pipe code / diffs / logs into it on stdin, or attach a file with `--file`.

Commands run:

```bash
gemini 'Explain what a Makefile does in 3 sentences'
cat utils/gh.py | gemini 'Review this Python code for bugs and improvements'
gh pr diff 42 | gemini 'Summarize these code changes in plain English'
```

**Surprise.** Its stdin-first design makes it feel like `grep` or `jq` — you can drop it
into any shell pipeline. That is philosophically different from a chatbot UI and is
what makes it viable as a "review engine" for devkit.

**Use case for devkit.** Power `devkit ai review <pr>` and `devkit ai summarize <pr>` by
piping `gh pr diff` into Gemini with a structured prompt.

---

## `claude` — Anthropic Claude Code

**What it does.** An agentic coding CLI: it reads your repository as context, can edit
files, run commands, and chain multi-step actions. Usable one-shot
(`claude 'explain this repo'`), interactively (`claude`), or scripted
(`claude --no-interactive 'Add docstrings to utils/gh.py'`).

Commands run:

```bash
claude 'Summarize the purpose of this repository'
python main.py 2>&1 | claude 'Explain this error and suggest a fix'
claude --no-interactive 'Add docstrings to every function in utils/gh.py'
```

**Surprise.** Unlike Copilot or Gemini, Claude understands the *repo as a whole* — asking
it about "the main entry points" yields actually-correct answers for an unfamiliar code
base, because it navigates files itself. That makes it a natural fit for scaffolding a
feature from an issue description.

**Use case for devkit.** `devkit workflow feature-start --issue N` uses Claude to produce
a step-by-step implementation plan from the issue body. `devkit ai docstring <file>`
asks Claude to add docstrings directly.

---

## `warp` — AI-native terminal

**What it does.** A Rust-based terminal emulator with AI completions, block-based
output, and shareable workflows baked in. Not a CLI we call from Python; it is the
shell you run devkit inside.

**Surprise.** "Blocks" (each command and its output grouped as a copy-pasteable unit)
are more useful than the AI features — they turn the terminal into something closer to
a notebook.

**Use case for devkit.** When demoing devkit, record a Warp session: the block-based
output makes it easy to share individual command/result pairs.

---

## `fzf` — Fuzzy finder for any list

**What it does.** Reads lines from stdin, shows a full-screen fuzzy search UI, writes
the picked line to stdout. It turns any newline-separated list into an interactive
picker.

Commands run:

```bash
ls | fzf
git log --oneline | fzf
```

**Surprise.** It is one of the fastest ways to build a "pick one" UX in a shell script —
no need for `dialog`, `whiptail`, or a TUI library. A one-liner replaces hundreds of
lines of custom menu code.

**Use case for devkit.** `devkit gh issues --interactive` pipes formatted issue lines
into `fzf` and opens the selected issue with `gh issue view --web`.

---

## `bat` — `cat` replacement with syntax highlighting

**What it does.** Drop-in `cat` replacement with syntax highlighting, line numbers,
git-aware gutter markers, and paging.

Commands run:

```bash
bat --list-themes
bat --theme=GitHub README.md
```

**Surprise.** `bat` cooperates with pagers and CIs automatically: piped output strips
colour, interactive output paginates with `less`. You can use the same command in a
Makefile and in a terminal session without surprises.

**Use case for devkit.** When a devkit command needs to show a code snippet (for
example, a piece of the diff being reviewed), shelling out to `bat` preserves
highlighting for free.

---

## `delta` (`git-delta`) — Better git diff viewer

**What it does.** A pager for `git diff` / `git show` that adds syntax highlighting,
side-by-side layout, and readable hunk headers. Configured once in `~/.gitconfig` and
`git diff` is transformed.

Commands run:

```bash
git diff HEAD~1 | delta
```

**Surprise.** Side-by-side view (`--side-by-side`) transforms review ergonomics: wide
diffs become readable even in a 120-column terminal. Delta is the closest to a GitHub
PR diff view you can get in a TTY.

**Use case for devkit.** `devkit gh pr-summary` can `gh pr diff | delta` when the user
passes `--raw` to see the raw diff locally before calling the AI review.

---

## `lazygit` — Terminal UI for git

**What it does.** A full-screen TUI that exposes the git workflow — staging hunks,
rebasing, cherry-picking, resolving conflicts — with keyboard shortcuts instead of
memorised commands.

**Surprise.** Interactive rebasing is actually enjoyable in `lazygit`: you pick up a
commit with one key, move it with another, squash with another. The learning cliff of
`git rebase -i` vanishes.

**Use case for devkit.** Not wrapped, but recommended in the README as the escape
hatch when a devkit workflow hits a git edge case. A possible future command:
`devkit git ui` that shells into `lazygit` directly.

---

## `atuin` — Shell history with search and sync

**What it does.** Replaces your shell history with a SQLite-backed store, adds
`Ctrl-R` fuzzy search, and can optionally sync across machines.

**Surprise.** It records exit codes, durations, and working directories for every
command. Asking "what long-running commands did I run in this repo that failed last
week?" becomes a single SQL query.

**Use case for devkit.** A future `devkit history review` could read the atuin DB and
surface the most common `gh` / `git` commands the user re-runs, suggesting devkit
shortcuts for them.

---

## Summary — how these tools compose in devkit

| Layer | Tool(s) | Role in devkit |
| --- | --- | --- |
| Data access | `gh` | Structured JSON source of truth for GitHub |
| AI reasoning | `gh copilot`, `gemini`, `claude` | Three complementary AI surfaces (shell, stdin, agentic) |
| Interactivity | `fzf` | Picker UX for lists returned by `gh` |
| Presentation | `bat`, `delta`, `rich` | Syntax highlighting for diffs and code snippets |
| Ergonomics | `warp`, `lazygit`, `atuin` | The shell you run devkit in, not wrapped directly |

The instinct this phase was meant to build: **every line of JSON from `gh` is a
potential input to `fzf`, and every diff is a potential input to Gemini or Claude.**
That is the composability that `devkit` is going to materialise in later phases.
