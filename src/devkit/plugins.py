"""Lightweight plugin and hook system for devkit.

There are two ways third parties can extend devkit:

1. **Hooks** — drop a Python file into ``~/.devkit/hooks/`` that defines
   well-known callables (``pre_commit``, ``post_pr_open``, ``pre_review``).
   Each callable receives a context dict and may mutate it.

2. **Plugin commands** — drop a Python file into ``~/.devkit/plugins/`` that
   exposes a Typer ``app`` (``app = typer.Typer(...)``). It will be mounted
   under ``devkit plugin <plugin-name>``.

The discovery mechanism deliberately uses raw ``importlib`` rather than
entry points so users can prototype a plugin without packaging.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, Callable

import typer

PLUGINS_DIR = Path.home() / ".devkit" / "plugins"
HOOKS_DIR = Path.home() / ".devkit" / "hooks"

KNOWN_HOOKS = ("pre_commit", "post_pr_open", "pre_review", "post_feature_start")


def _import_module_from(path: Path):
    """Import a Python file as a fresh module without polluting ``sys.path``."""
    spec = importlib.util.spec_from_file_location(f"devkit_user_{path.stem}", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # pragma: no cover - depends on user code
        # We swallow the error so a single broken plugin doesn't crash devkit;
        # the doctor command surfaces these problems instead.
        sys.stderr.write(f"[devkit] Failed to load {path.name}: {exc}\n")
        return None
    return module


def discover_plugins() -> list[tuple[str, typer.Typer]]:
    """Yield ``(name, Typer app)`` tuples for every plugin file."""
    if not PLUGINS_DIR.exists():
        return []
    found: list[tuple[str, typer.Typer]] = []
    for path in sorted(PLUGINS_DIR.glob("*.py")):
        module = _import_module_from(path)
        if module is None:
            continue
        app = getattr(module, "app", None)
        if isinstance(app, typer.Typer):
            found.append((path.stem, app))
    return found


def discover_hooks() -> dict[str, list[Callable[[dict[str, Any]], None]]]:
    """Return ``{hook_name: [callables...]}`` for every hook file."""
    bag: dict[str, list[Callable[[dict[str, Any]], None]]] = {h: [] for h in KNOWN_HOOKS}
    if not HOOKS_DIR.exists():
        return bag
    for path in sorted(HOOKS_DIR.glob("*.py")):
        module = _import_module_from(path)
        if module is None:
            continue
        for hook_name in KNOWN_HOOKS:
            fn = getattr(module, hook_name, None)
            if callable(fn) and not inspect.isclass(fn):
                bag[hook_name].append(fn)
    return bag


def fire(hook_name: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run every registered callable for ``hook_name``.

    The context dict is passed to each hook in registration order; hooks may
    add or mutate keys. Returns the (possibly mutated) context.
    """
    ctx = context if context is not None else {}
    for fn in discover_hooks().get(hook_name, []):
        try:
            fn(ctx)
        except Exception as exc:  # pragma: no cover - depends on user code
            sys.stderr.write(f"[devkit] Hook {hook_name} ({fn.__name__}) raised: {exc}\n")
    return ctx


def register_with(app: typer.Typer) -> int:
    """Mount every discovered plugin Typer app under the root ``app``.

    Returns the number of plugins mounted.
    """
    plugin_app = typer.Typer(help="User-installed plugin commands")
    plugins = discover_plugins()
    for name, sub in plugins:
        plugin_app.add_typer(sub, name=name, help=f"Plugin: {name}")
    if plugins:
        app.add_typer(plugin_app, name="plugin", help="User-installed plugins")
    return len(plugins)
