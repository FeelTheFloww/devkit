# Changelog

All notable changes to `devkit` are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - Unreleased

### Added
- `discovery.md` — Phase 1 deliverable covering every modern CLI tool with
  observations and intended devkit use case.
- `devkit doctor` — top-level diagnostics command: binary presence, versions,
  `gh auth status`, `gh-copilot` extension, and `~/.devkit/config.json`
  validity. Exits non-zero when required tools are missing.
- `devkit ai summarize <pr>` — plain-English bullet summary of a PR using the
  configured AI backend (Claude by default).
- `devkit ai docstring <file.py>` — generate Google-style docstrings for every
  function in a Python file. Preview by default, write with `--apply` after
  saving a `.bak` backup.
- `devkit workflow daily-digest` — PRs awaiting your review + issues assigned
  to you + latest CI runs, in one command.
- `devkit config` sub-app — `show`, `path`, `set`, and `reset` for
  `~/.devkit/config.json`.
- Test suite expanded to 27 tests covering subprocess helpers, config
  round-trip, tool checks, AI helpers, and a Typer CLI smoke test for every
  command group.
- CHANGELOG and example config file.

### Changed
- AI prompt truncation unified under `_MAX_PROMPT_CHARS = 6000`.
- README rewritten around a command reference table, flagship workflows,
  configuration examples, and the grading checklist.

## [0.1.0] - 2026-04-14

### Added
- Initial project skeleton: `pyproject.toml`, package layout under `src/devkit`.
- Phase 2 commands: `gh issues`, `gh pr-summary`, `gh start-feature`,
  `gh open-pr`, `gh run-status`, `gh repo-init`.
- Phase 3 commands: `ai explain`, `ai suggest`, `ai review`, `ai commit`.
- Phase 4: Typer sub-apps, shared config, `fzf` integration, `feature-start`
  workflow.
- Phase 5: `require_tools` guard, basic README and tests.
