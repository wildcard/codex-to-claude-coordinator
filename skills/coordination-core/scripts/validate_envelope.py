#!/usr/bin/env python3
"""Validate portable coordination envelopes and JSON Lines streams."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePath
from typing import Any, Iterable


TOP_KEYS = {
    "schema_version",
    "event_id",
    "task_id",
    "seq",
    "emitted_at",
    "emitter",
    "type",
    "body",
}
EMITTERS = {"coordinator", "worker", "human"}
TYPES = {
    "assignment",
    "state",
    "question",
    "steer",
    "approval_request",
    "approval_decision",
    "evidence",
    "review",
    "stop",
    "handoff",
}
LEDGER_KEYS = {
    "implementation",
    "local_validation",
    "live_e2e",
    "review",
    "approval",
    "release",
}
LEDGER_VALUES = {"pending", "in_progress", "done", "blocked", "not_applicable"}
TERMINAL_STATES = {"completed", "failed", "stopped"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _require(body: dict[str, Any], fields: set[str], errors: list[str]) -> None:
    missing = fields - body.keys()
    if missing:
        errors.append(f"body missing: {', '.join(sorted(missing))}")


def _valid_time(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _valid_string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _validate_ledger(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("ledger must be an object")
        return
    if set(value) != LEDGER_KEYS:
        errors.append("ledger must contain exactly the six completion fields")
    if any(status not in LEDGER_VALUES for status in value.values()):
        errors.append("ledger contains an invalid status")


def validate_envelope(event: Any) -> list[str]:
    if not isinstance(event, dict):
        return ["envelope must be an object"]
    errors: list[str] = []
    if set(event) != TOP_KEYS:
        missing = TOP_KEYS - event.keys()
        extra = event.keys() - TOP_KEYS
        if missing:
            errors.append(f"missing top-level keys: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"unknown top-level keys: {', '.join(sorted(extra))}")
        return errors

    if event["schema_version"] != "0.1":
        errors.append("schema_version must be 0.1")
    for key in ("event_id", "task_id"):
        if not isinstance(event[key], str) or not event[key].strip():
            errors.append(f"{key} must be a non-empty string")
    if (
        not isinstance(event["seq"], int)
        or isinstance(event["seq"], bool)
        or event["seq"] < 0
    ):
        errors.append("seq must be a non-negative integer")
    if not _valid_time(event["emitted_at"]):
        errors.append("emitted_at must be an RFC 3339 timestamp with offset")
    if event["emitter"] not in EMITTERS:
        errors.append("emitter is invalid")
    if event["type"] not in TYPES:
        errors.append("type is invalid")
    if not isinstance(event["body"], dict):
        errors.append("body must be an object")
        return errors
    if errors:
        return errors

    emitter = event["emitter"]
    kind = event["type"]
    body = event["body"]

    expected_emitter = {
        "assignment": "coordinator",
        "state": "worker",
        "question": "worker",
        "steer": "coordinator",
        "approval_request": "worker",
        "approval_decision": "human",
        "evidence": "worker",
        "review": "coordinator",
        "stop": "coordinator",
        "handoff": "worker",
    }[kind]
    if emitter != expected_emitter:
        errors.append(f"{kind} must be emitted by {expected_emitter}")

    required = {
        "assignment": {
            "outcome",
            "definition_of_done",
            "owned_paths",
            "required_evidence",
            "permission_boundary",
            "requested_tier",
            "reasoning_effort",
        },
        "state": {"lifecycle_state", "ledger", "session_ref", "actual_worker"},
        "question": {"question", "recommended_action", "blocking"},
        "steer": {"instruction", "evidence_refs", "target_paths"},
        "approval_request": {"action", "reason", "reversible", "expires_at"},
        "approval_decision": {"request_event_id", "decision"},
        "evidence": {"kind", "ref", "result", "evidence_class"},
        "review": {"change_ref", "independent_required"},
        "stop": {"reason", "mode"},
        "handoff": {
            "actual_worker",
            "ledger",
            "commit",
            "review_result",
            "blocker",
            "next_action",
        },
    }[kind]
    _require(body, required, errors)
    if errors:
        return errors

    if kind == "assignment":
        if not _valid_string_list(body["definition_of_done"], nonempty=True):
            errors.append("definition_of_done must be a non-empty string array")
        if not _valid_string_list(body["owned_paths"], nonempty=True):
            errors.append("owned_paths must be a non-empty string array")
        if not _valid_string_list(body["required_evidence"]):
            errors.append("required_evidence must be a string array")
        if body["requested_tier"] not in {"routine", "strong", "max"}:
            errors.append("requested_tier is invalid")
        if body["reasoning_effort"] not in {"low", "medium", "high"}:
            errors.append("reasoning_effort is invalid")
        boundary = body["permission_boundary"]
        boundary_keys = {"push", "pull_request", "publish", "message"}
        if not isinstance(boundary, dict) or set(boundary) != boundary_keys:
            errors.append("permission_boundary must contain four external-action fields")
        elif any(value not in {"forbidden", "ask", "authorized"} for value in boundary.values()):
            errors.append("permission_boundary contains an invalid decision")

    elif kind == "state":
        if body["lifecycle_state"] not in {
            "working",
            "needs_input",
            "idle",
            *TERMINAL_STATES,
        }:
            errors.append("lifecycle_state is invalid")
        _validate_ledger(body["ledger"], errors)

    elif kind == "question":
        if not isinstance(body["blocking"], bool):
            errors.append("blocking must be a boolean")

    elif kind == "steer":
        if not _valid_string_list(body["evidence_refs"]):
            errors.append("evidence_refs must be a string array")
        if not _valid_string_list(body["target_paths"]):
            errors.append("target_paths must be a string array")

    elif kind == "approval_request":
        if not isinstance(body["reversible"], bool):
            errors.append("reversible must be a boolean")
        if body["expires_at"] is not None and not _valid_time(body["expires_at"]):
            errors.append("expires_at must be null or an RFC 3339 timestamp")

    elif kind == "approval_decision":
        if body["decision"] not in {"approve", "deny"}:
            errors.append("approval decision must be approve or deny")

    elif kind == "evidence":
        if body["result"] not in {"pass", "fail", "observed", "unavailable"}:
            errors.append("evidence result is invalid")
        if body["evidence_class"] not in {
            "immutable",
            "observed",
            "rendered",
            "unavailable",
        }:
            errors.append("evidence_class is invalid")
        if "sha256" in body and not SHA256_RE.fullmatch(str(body["sha256"])):
            errors.append("sha256 must be 64 lowercase hexadecimal characters")

    elif kind == "review":
        if body["independent_required"] is not True:
            errors.append("independent_required must be true")

    elif kind == "stop":
        if body["mode"] not in {"graceful", "cancel"}:
            errors.append("stop mode is invalid")

    elif kind == "handoff":
        _validate_ledger(body["ledger"], errors)
        if body["commit"] is not None and not isinstance(body["commit"], str):
            errors.append("commit must be a string or null")
        if body["blocker"] is not None:
            blocker_keys = {"symptom", "working", "owner", "parallel_action"}
            if not isinstance(body["blocker"], dict) or set(body["blocker"]) != blocker_keys:
                errors.append("blocker must be null or contain the four blocker fields")
            elif any(
                not isinstance(value, str) or not value.strip()
                for value in body["blocker"].values()
            ):
                errors.append("blocker fields must be non-empty strings")

    for key, value in body.items():
        if key in {"expires_at", "commit", "blocker"} and value is None:
            continue
        if key in {"ledger", "permission_boundary"}:
            continue
        if isinstance(value, str) and not value.strip():
            errors.append(f"body.{key} must not be blank")
    return errors


def _inside(path: str, roots: list[str]) -> bool:
    candidate = PurePath(path)
    if ".." in candidate.parts:
        return False
    for root in roots:
        root_path = PurePath(root)
        if ".." in root_path.parts or candidate.is_absolute() != root_path.is_absolute():
            continue
        try:
            candidate.relative_to(root_path)
            return True
        except ValueError:
            pass
    return False


def validate_stream(events: Iterable[Any]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    tasks: dict[str, dict[str, Any]] = {}

    for index, event in enumerate(events, start=1):
        event_errors = validate_envelope(event)
        errors.extend(f"record {index}: {item}" for item in event_errors)
        if event_errors:
            continue
        if event["event_id"] in seen_ids:
            errors.append(f"record {index}: duplicate event_id")
        seen_ids.add(event["event_id"])

        task = tasks.setdefault(
            event["task_id"],
            {"last_seq": -1, "owned_paths": [], "open_stop": False},
        )
        if event["seq"] <= task["last_seq"]:
            errors.append(f"record {index}: seq must strictly increase")
        task["last_seq"] = event["seq"]

        if event["type"] == "assignment":
            if task["owned_paths"]:
                errors.append(f"record {index}: task already has an assignment")
            task["owned_paths"] = event["body"]["owned_paths"]
            if any(".." in PurePath(path).parts for path in task["owned_paths"]):
                errors.append(f"record {index}: owned_paths must not contain traversal")
        elif not task["owned_paths"]:
            errors.append(f"record {index}: assignment must precede other events")

        if event["type"] == "steer":
            for target in event["body"]["target_paths"]:
                if not _inside(target, task["owned_paths"]):
                    errors.append(f"record {index}: steer target is outside assignment scope")
        elif event["type"] == "stop":
            task["open_stop"] = True
        elif (
            event["type"] == "state"
            and task["open_stop"]
            and event["body"]["lifecycle_state"] in TERMINAL_STATES
        ):
            task["open_stop"] = False

    for task_id, task in tasks.items():
        if task["open_stop"]:
            errors.append(f"task {task_id}: stop lacks a later terminal state")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON object/array or JSON Lines file")
    args = parser.parse_args()
    try:
        raw = Path(args.input).read_text(encoding="utf-8")
        try:
            parsed = json.loads(raw)
            events = parsed if isinstance(parsed, list) else [parsed]
        except json.JSONDecodeError:
            events = [json.loads(line) for line in raw.splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    errors = validate_stream(events)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid: {len(events)} envelope(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
