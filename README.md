# devkit – The Modern Developer's Command Hub

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> **AI-powered CLI orchestration**: Combine GitHub CLI, Claude, Gemini, Git, and more into one unified workflow.

`devkit` is a Python CLI that orchestrates multiple tools (`gh`, `git`, Claude, Gemini) for developers:

- **`devkit workflow feature-start`** — Create branch → push → draft PR → AI plan
- **`devkit ai review 42`** — Intelligent PR review
- **`devkit workflow daily-digest`** — PRs to review + assigned issues + CI status
- **`devkit doctor`** — Diagnose your toolchain

## Quick Start

```bash
git clone https://github.com/FeelTheFloww/devkit.git
cd devkit
pip install -e .
devkit doctor
```

## Core Commands

| Command | Purpose |
|---------|---------|
| `devkit doctor` | Check all required tools |
| `devkit gh issues` | List issues in a Rich table |
| `devkit ai review <pr>` | AI-powered PR review |
| `devkit ai commit` | Generate commit message |
| `devkit workflow feature-start <name> [--issue]` | Branch + PR + AI plan |
| `devkit workflow daily-digest` | Dashboard: PRs + issues + CI |
| `devkit config show/set` | Manage `~/.devkit/config.json` |

## Project Structure

```
devkit/
├── src/devkit/
│   ├── main.py              # CLI entry point
│   ├── config.py            # Config management
│   ├── commands/            # Command implementations
│   │   ├── ai.py            # devkit ai *
│   │   ├── github.py        # devkit gh *
│   │   ├── workflow.py      # devkit workflow *
│   │   ├── config_cmd.py    # devkit config *
│   │   └── doctor.py        # devkit doctor
│   └── utils/               # Shared utilities
│       ├── shell.py         # Subprocess orchestration
│       ├── gh.py            # GitHub CLI wrappers
│       ├── check.py         # Tool detection
│       └── display.py       # Rich terminal output
└── tests/                   # Test suite
```

## Architecture

**3-layer design:**
- **Commands** (`commands/`) — Typer CLI entry points for workflows
- **Utils** (`utils/`) — Subprocess wrappers, config, display, tool checks
- **Config** (`config.py`) — `~/.devkit/config.json` persistence

**Key design principles:**
- Every external tool called via `subprocess.run()` with proper error handling
- Type hints throughout (`from __future__ import annotations`)
- No global state — pass config/console as parameters
- Clear, actionable error messages

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| `git` | Version control | System package manager |
| `gh` | GitHub CLI | [cli.github.com](https://cli.github.com) |
| `claude` | AI review (default) | Windows: `irm https://claude.ai/install.ps1 \| iex` |
| `gemini` | AI review (optional) | `npm install -g @google/generative-ai-cli` |

**Environment variables:**
- `ANTHROPIC_API_KEY` for Claude
- `GOOGLE_API_KEY` for Gemini (optional)

## Development

```bash
pip install -e .
pip install pytest
pytest
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical design.

1. Create `src/devkit/commands/my_command.py`:
```python
import typer
from devkit.utils.display import console

app = typer.Typer(help="My commands")

@app.command()
def hello(name: str) -> None:
    """Greet someone."""
    console.print(f"[green]Hello, {name}![/green]")
```

2. Import in `src/devkit/main.py`:
```python
from devkit.commands import my_command
main.add_typer(my_command.app, name="my")
```

3. Add tests in `tests/test_my_command.py`

---

**For more details, see:**
- [ARCHITECTURE.md](ARCHITECTURE.md) — Technical design and decisions
- [CHANGELOG.md](CHANGELOG.md) — Version history
- [discovery.md](discovery.md) � Initial discovery document

## Documentation

Additional documentation (architecture, diagrams, cheat sheets — mostly in French) lives in [`docs/`](docs/). See [ARCHITECTURE.md](ARCHITECTURE.md) for the technical design and [CHANGELOG.md](CHANGELOG.md) for version history.

---

## 🗺️ Roadmap

- [ ] Plugin system for custom commands
- [ ] Test coverage and CI pipeline
- [ ] PyPI packaging and release automation
- [ ] Support for GitLab and Bitbucket backends

## License

[MIT](LICENSE)
