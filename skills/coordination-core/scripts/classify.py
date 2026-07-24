#!/usr/bin/env python3
"""Classify agent work into six independent, vendor-neutral axes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_KEYS = {
    "files_in_scope",
    "crosses_systems",
    "prior_attempt_failed",
    "plan_required",
    "external_actions_requested",
    "reversible",
    "expected_tool_calls",
    "independent_subtasks",
}


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_inputs(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["input must be an object"]

    errors: list[str] = []
    missing = EXPECTED_KEYS - data.keys()
    extra = data.keys() - EXPECTED_KEYS
    if missing:
        errors.append(f"missing keys: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"unknown keys: {', '.join(sorted(extra))}")
    if errors:
        return errors

    if not _is_int(data["files_in_scope"]) or data["files_in_scope"] < 0:
        errors.append("files_in_scope must be a non-negative integer")
    for key in (
        "crosses_systems",
        "prior_attempt_failed",
        "plan_required",
        "reversible",
    ):
        if not isinstance(data[key], bool):
            errors.append(f"{key} must be a boolean")
    actions = data["external_actions_requested"]
    if not isinstance(actions, list) or not all(
        isinstance(item, str) and item.strip() for item in actions
    ):
        errors.append("external_actions_requested must be an array of non-empty strings")
    if data["expected_tool_calls"] not in {"small", "medium", "large"}:
        errors.append("expected_tool_calls must be small, medium, or large")
    if not _is_int(data["independent_subtasks"]) or data["independent_subtasks"] < 0:
        errors.append("independent_subtasks must be a non-negative integer")
    return errors


def classify(data: dict[str, Any]) -> dict[str, str]:
    errors = validate_inputs(data)
    if errors:
        raise ValueError("; ".join(errors))

    if data["crosses_systems"] or data["prior_attempt_failed"]:
        difficulty = "hard"
    elif data["files_in_scope"] <= 1:
        difficulty = "trivial"
    else:
        difficulty = "standard"

    if not data["reversible"] or data["external_actions_requested"]:
        risk = "high"
    elif data["plan_required"]:
        risk = "elevated"
    else:
        risk = "low"

    duration = {
        "small": "short",
        "medium": "medium",
        "large": "long",
    }[data["expected_tool_calls"]]

    if data["independent_subtasks"] >= 2 and data["crosses_systems"]:
        coordination = "team"
    elif data["independent_subtasks"] >= 2:
        coordination = "fan_out"
    else:
        coordination = "single"

    if difficulty == "hard" and duration == "long":
        requested_tier = "max"
    elif difficulty == "hard" or risk in {"elevated", "high"}:
        requested_tier = "strong"
    else:
        requested_tier = "routine"

    if difficulty == "hard" or risk == "high":
        reasoning_effort = "high"
    elif difficulty == "trivial" and risk == "low":
        reasoning_effort = "low"
    else:
        reasoning_effort = "medium"

    return {
        "difficulty": difficulty,
        "risk": risk,
        "duration": duration,
        "coordination": coordination,
        "requested_tier": requested_tier,
        "reasoning_effort": reasoning_effort,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="JSON file; omit to read stdin")
    args = parser.parse_args()

    try:
        raw = Path(args.input).read_text() if args.input else sys.stdin.read()
        result = classify(json.loads(raw))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
