from __future__ import annotations

from typing import Any

from devkit.utils.shell import run_cmd, run_json


def gh(*args: str) -> str:
    return run_cmd(["gh", *args])


def gh_json(*args: str) -> Any:
    return run_json(["gh", *args])
