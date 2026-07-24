#!/usr/bin/env python3
"""Summarize observed adapter operations without inferring absent capabilities."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from validate import load_records, validate_stream


ADAPTER_OPERATIONS = (
    "inspect_capabilities",
    "inspect_usage",
    "list_sessions",
    "start_session",
    "read_session",
    "steer_session",
    "stop_session",
    "collect_changes",
    "collect_review",
)
STATUSES = {"pass", "fail", "unavailable", "not_tested"}


def summarize(
    records: list[dict[str, Any]],
    run_id: str,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    selected = [record for record in records if record.get("run_id") == run_id]
    if not selected:
        raise ValueError(f"run_id not found: {run_id}")
    surfaces = {record["surface"] for record in selected}
    surface = next(iter(surfaces)) if len(surfaces) == 1 else "multiple"
    capabilities: dict[str, Any] = {}
    for operation in ADAPTER_OPERATIONS:
        observations = [record for record in selected if record["operation"] == operation]
        if not observations:
            capabilities[operation] = {
                "status": "unknown",
                "evidence_count": 0,
                "limitations": ["no observation recorded"],
            }
            continue
        latest = max(
            observations,
            key=lambda record: datetime.fromisoformat(
                record["observed_at"].replace("Z", "+00:00")
            ),
        )
        status = latest["observation"].get("result")
        if status not in STATUSES:
            status = "unknown"
        capabilities[operation] = {
            "status": status,
            "evidence_count": sum(
                len(record["evidence_files"]) for record in observations
            ),
            "limitations": sorted(
                {
                    limitation
                    for record in observations
                    for limitation in record["limitations"]
                }
            ),
        }
    return {
        "schema_version": "0.1",
        "generated_at": generated_at or datetime.now().astimezone().isoformat(),
        "run_id": run_id,
        "surface": surface,
        "capabilities": capabilities,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    try:
        records = load_records(args.input)
        errors = validate_stream(records, args.root)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        manifest = summarize(records, args.run_id)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
