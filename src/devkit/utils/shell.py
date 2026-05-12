from __future__ import annotations

import json
import subprocess
from typing import Any


def run_cmd(
    args: list[str],
    *,
    input_text: str | None = None,
    check: bool = True,
) -> str:
    try:
        result = subprocess.run(
            args,
            input=input_text,
            capture_output=True,
            text=True,
            check=check,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"Command not found: {args[0]}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        details = stderr or stdout or "command failed"
        raise RuntimeError(f"{' '.join(args)} -> {details}") from exc
    return result.stdout.strip()


def run_json(args: list[str]) -> Any:
    raw = run_cmd(args)
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Expected JSON output from: {' '.join(args)}") from exc
