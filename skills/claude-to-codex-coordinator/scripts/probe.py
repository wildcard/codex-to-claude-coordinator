#!/usr/bin/env python3
"""Privacy-safe prerequisite probe for the official Claude-to-Codex plugin."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from typing import Any


PLUGIN_ID = "codex@openai-codex"
MINIMUM_NODE = (18, 18, 0)


def run_command(argv: Sequence[str], timeout: int = 20) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            list(argv),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"returncode": None, "stdout": "", "stderr": ""}
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def first_line(value: str) -> str | None:
    return next((line.strip() for line in value.splitlines() if line.strip()), None)


def parse_node_version(value: str) -> tuple[int, int, int] | None:
    match = re.search(r"v?(\d+)\.(\d+)\.(\d+)", value)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def auth_method(value: str) -> str | None:
    lowered = value.lower()
    if "chatgpt" in lowered:
        return "chatgpt"
    if "api key" in lowered or "api-key" in lowered:
        return "api_key"
    return "configured" if value.strip() else None


def build_report(
    run: Callable[[Sequence[str], int], dict[str, Any]] = run_command,
    which: Callable[[str], str | None] = shutil.which,
) -> dict[str, Any]:
    node_available = which("node") is not None
    node_result = run(["node", "--version"], 10) if node_available else {}
    node_text = str(node_result.get("stdout", ""))
    node_version = parse_node_version(node_text)
    node_ok = (
        node_available
        and node_result.get("returncode") == 0
        and node_version is not None
        and node_version >= MINIMUM_NODE
    )

    claude_available = which("claude") is not None
    claude_version_result = (
        run(["claude", "--version"], 10) if claude_available else {}
    )
    claude_plugins_result = (
        run(["claude", "plugin", "list", "--json"], 20)
        if claude_available
        else {}
    )
    plugin_entry: dict[str, Any] = {}
    try:
        plugins = json.loads(str(claude_plugins_result.get("stdout", "")))
    except (json.JSONDecodeError, TypeError):
        plugins = []
    if isinstance(plugins, list):
        plugin_entry = next(
            (
                entry
                for entry in plugins
                if isinstance(entry, dict) and entry.get("id") == PLUGIN_ID
            ),
            {},
        )
    plugin_errors = plugin_entry.get("errors")
    error_count = len(plugin_errors) if isinstance(plugin_errors, list) else 0

    codex_available = which("codex") is not None
    codex_version_result = (
        run(["codex", "--version"], 10) if codex_available else {}
    )
    codex_auth_result = (
        run(["codex", "login", "status"], 20) if codex_available else {}
    )
    auth_text = " ".join(
        (
            str(codex_auth_result.get("stdout", "")),
            str(codex_auth_result.get("stderr", "")),
        )
    ).strip()
    authenticated = codex_auth_result.get("returncode") == 0

    plugin_ready = (
        bool(plugin_entry)
        and plugin_entry.get("enabled") is True
        and error_count == 0
    )
    codex_ready = (
        codex_available
        and codex_version_result.get("returncode") == 0
        and authenticated
    )

    return {
        "schema_version": "0.1",
        "ready": bool(node_ok and claude_available and plugin_ready and codex_ready),
        "node": {
            "available": node_available,
            "version": first_line(node_text),
            "meets_minimum": bool(node_ok),
        },
        "claude": {
            "available": claude_available,
            "version": first_line(
                str(claude_version_result.get("stdout", ""))
            ),
        },
        "codex": {
            "available": codex_available,
            "version": first_line(
                str(codex_version_result.get("stdout", ""))
            ),
            "authenticated": authenticated,
            "auth_method": auth_method(auth_text) if authenticated else None,
        },
        "plugin": {
            "id": PLUGIN_ID,
            "installed": bool(plugin_entry),
            "enabled": plugin_entry.get("enabled") is True,
            "version": plugin_entry.get("version"),
            "scope": plugin_entry.get("scope"),
            "error_count": error_count,
        },
        "privacy": {
            "raw_auth_output_included": False,
            "install_path_included": False,
        },
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
