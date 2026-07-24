#!/usr/bin/env python3
"""Validate privacy-safe coordination experiment observations."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePath
from typing import Any, Iterable


TOP_KEYS = {
    "schema_version",
    "observation_id",
    "experiment",
    "run_id",
    "observed_at",
    "surface",
    "surface_version",
    "account_class",
    "host_platform",
    "operation",
    "input_id",
    "observation",
    "evidence_files",
    "evidence_class",
    "limitations",
}
EVIDENCE_KEYS = {
    "path",
    "sha256",
    "kind",
    "redacted",
    "source",
    "privacy_checked",
}
EXPERIMENT_RE = re.compile(r"^[a-z][a-z0-9-]*$")
ACCOUNT_CLASSES = {"pro", "max", "team", "enterprise", "unknown"}
PLATFORMS = {"macos", "windows", "linux", "unknown"}
EVIDENCE_CLASSES = {
    "official-doc",
    "observed",
    "advisor",
    "inference",
    "unknown",
}
EVIDENCE_KINDS = {"screenshot", "transcript", "artifact", "log"}
EVIDENCE_SOURCES = {"redacted-derivative", "product-export", "synthetic"}
RESULTS = {"pass", "fail", "unavailable", "not_tested", "observed"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RUN_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
OPERATION_RE = re.compile(r"^[a-z][a-z0-9_]*$")
PERCENT_RE = re.compile(r"^(?:100(?:\.0+)?|(?:0|[1-9][0-9]?)(?:\.[0-9]+)?)%$")
PRIVACY_PATTERNS = (
    ("email address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    ("macOS home path", re.compile(r"/Users/[^/\s]+/")),
    ("Unix home path", re.compile(r"/home/[^/\s]+/")),
    ("Windows home path", re.compile(r"[A-Z]:\\Users\\[^\\\s]+\\", re.I)),
    ("secret-like value", re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b")),
    (
        "credential assignment",
        re.compile(r"\b(?:api[_-]?key|access[_-]?token)\s*[:=]\s*\S+", re.I),
    ),
)


def _valid_time(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _strings(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_strings(item)


def privacy_errors(value: Any, prefix: str = "record") -> list[str]:
    errors: list[str] = []
    for text in _walk_strings(value):
        for label, pattern in PRIVACY_PATTERNS:
            if pattern.search(text):
                errors.append(f"{prefix} contains a {label}")
    return sorted(set(errors))


def _safe_relative(path: str) -> bool:
    candidate = PurePath(path)
    return not candidate.is_absolute() and ".." not in candidate.parts


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_usage(observation: dict[str, Any], errors: list[str]) -> None:
    fields = {
        "kind",
        "result",
        "label_verbatim",
        "value_verbatim",
        "direction",
        "scope",
        "model_name_verbatim",
        "window_start",
        "window_end",
        "reset_at",
        "captured_at",
        "freshness",
        "threshold_eligible",
    }
    missing = fields - observation.keys()
    if missing:
        errors.append(f"usage observation missing: {', '.join(sorted(missing))}")
        return
    if observation["result"] not in RESULTS:
        errors.append("usage result is invalid")
    if observation["direction"] not in {"consumed", "remaining", "unknown"}:
        errors.append("usage direction is invalid")
    if observation["scope"] not in {
        "model",
        "plan",
        "weekly",
        "session",
        "context",
        "api-cost",
        "unknown",
    }:
        errors.append("usage scope is invalid")
    if observation["freshness"] not in {"live", "timestamped", "unknown"}:
        errors.append("usage freshness is invalid")
    if not isinstance(observation["threshold_eligible"], bool):
        errors.append("threshold_eligible must be a boolean")
        return
    if not _valid_time(observation["captured_at"]):
        errors.append("captured_at must be an RFC 3339 timestamp with offset")
    for key in ("window_start", "window_end", "reset_at"):
        if observation[key] is not None and not _valid_time(observation[key]):
            errors.append(f"{key} must be null or an RFC 3339 timestamp")

    if observation["threshold_eligible"]:
        if observation["scope"] != "model":
            errors.append("threshold automation requires model scope")
        if observation["direction"] != "consumed":
            errors.append("threshold automation requires consumed direction")
        if not isinstance(observation["model_name_verbatim"], str) or not observation[
            "model_name_verbatim"
        ].strip():
            errors.append("threshold automation requires an explicit model name")
        if not isinstance(observation["value_verbatim"], str) or not PERCENT_RE.fullmatch(
            observation["value_verbatim"]
        ):
            errors.append("threshold automation requires an explicit percentage")
        if observation["reset_at"] is None and observation["window_end"] is None:
            errors.append("threshold automation requires reset or window semantics")
        if observation["freshness"] == "unknown":
            errors.append("threshold automation requires known freshness")


def _validate_dispatch_stop(observation: dict[str, Any], errors: list[str]) -> None:
    result = observation.get("result")
    if result not in RESULTS:
        errors.append("stop result is invalid")
        return
    if result == "pass":
        if observation.get("action") not in {"stop", "cancel"}:
            errors.append("archive or other controls cannot pass stop_session")
        if observation.get("terminal_state") not in {
            "completed",
            "failed",
            "stopped",
        }:
            errors.append("stop_session pass requires a terminal worker state")


def validate_record(record: Any, root: Path | None = None) -> list[str]:
    if not isinstance(record, dict):
        return ["record must be an object"]
    errors: list[str] = []
    if set(record) != TOP_KEYS:
        missing = TOP_KEYS - record.keys()
        extra = record.keys() - TOP_KEYS
        if missing:
            errors.append(f"missing top-level keys: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"unknown top-level keys: {', '.join(sorted(extra))}")
        return errors

    if record["schema_version"] != "0.1":
        errors.append("schema_version must be 0.1")
    for key in ("observation_id", "surface", "surface_version", "input_id"):
        if not isinstance(record[key], str) or not record[key].strip():
            errors.append(f"{key} must be a non-empty string")
    if not isinstance(record["experiment"], str) or not EXPERIMENT_RE.fullmatch(
        record["experiment"]
    ):
        errors.append("experiment must be a lower-case slug")
    if not isinstance(record["run_id"], str) or not RUN_ID_RE.fullmatch(
        record["run_id"]
    ):
        errors.append("run_id must be a lower-case local identifier")
    if not _valid_time(record["observed_at"]):
        errors.append("observed_at must be an RFC 3339 timestamp with offset")
    if record["account_class"] not in ACCOUNT_CLASSES:
        errors.append("account_class is invalid")
    if record["host_platform"] not in PLATFORMS:
        errors.append("host_platform is invalid")
    if not isinstance(record["operation"], str) or not OPERATION_RE.fullmatch(
        record["operation"]
    ):
        errors.append("operation must be lower-case snake_case")
    if record["evidence_class"] not in EVIDENCE_CLASSES:
        errors.append("evidence_class is invalid")
    if not _strings(record["limitations"]):
        errors.append("limitations must be a string array")
    if not isinstance(record["observation"], dict):
        errors.append("observation must be an object")
        return errors
    if not isinstance(record["evidence_files"], list):
        errors.append("evidence_files must be an array")
        return errors

    errors.extend(privacy_errors(record))
    for index, evidence in enumerate(record["evidence_files"]):
        prefix = f"evidence_files[{index}]"
        if not isinstance(evidence, dict) or set(evidence) != EVIDENCE_KEYS:
            errors.append(f"{prefix} must contain exactly the evidence fields")
            continue
        path = evidence["path"]
        if not isinstance(path, str) or not path.strip() or not _safe_relative(path):
            errors.append(f"{prefix}.path must be a safe relative path")
            continue
        if not isinstance(evidence["sha256"], str) or not SHA256_RE.fullmatch(
            evidence["sha256"]
        ):
            errors.append(f"{prefix}.sha256 is invalid")
        if evidence["kind"] not in EVIDENCE_KINDS:
            errors.append(f"{prefix}.kind is invalid")
        if not isinstance(evidence["redacted"], bool):
            errors.append(f"{prefix}.redacted must be a boolean")
        if evidence["source"] not in EVIDENCE_SOURCES:
            errors.append(f"{prefix}.source is invalid")
        if evidence["privacy_checked"] is not True:
            errors.append(f"{prefix}.privacy_checked must be true")
        if evidence["kind"] in {"screenshot", "transcript", "log"}:
            if evidence["redacted"] is not True:
                errors.append(
                    f"{prefix}: screenshots, transcripts, and logs require "
                    "a redacted derivative"
                )
            if ".redacted." not in PurePath(path).name:
                errors.append(
                    f"{prefix}: private evidence path must identify "
                    "a redacted derivative"
                )
            if evidence["source"] != "redacted-derivative":
                errors.append(
                    f"{prefix}: private evidence source must be redacted-derivative"
                )

        if root is not None:
            candidate = root / path
            if not candidate.is_file():
                errors.append(f"{prefix}: evidence file does not exist")
            else:
                actual = _file_sha256(candidate)
                if actual != evidence["sha256"]:
                    errors.append(f"{prefix}: sha256 does not match evidence file")
                if evidence["kind"] in {"transcript", "artifact", "log"}:
                    try:
                        content = candidate.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        content = ""
                    errors.extend(privacy_errors(content, prefix))

    observation = record["observation"]
    if observation.get("kind") == "usage_signal":
        _validate_usage(observation, errors)
    if record["operation"] == "stop_session":
        _validate_dispatch_stop(observation, errors)

    result = observation.get("result")
    if (
        record["evidence_class"] == "observed"
        and result not in {"unavailable", "not_tested"}
        and not record["evidence_files"]
    ):
        errors.append("observed product behavior requires an evidence file")
    if record["operation"] == "collect_changes" and result == "pass" and not record[
        "evidence_files"
    ]:
        errors.append("collect_changes pass requires artifact evidence")
    return errors


def validate_stream(records: Iterable[Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    last_time: dict[str, datetime] = {}
    for index, record in enumerate(records, start=1):
        record_errors = validate_record(record, root)
        errors.extend(f"record {index}: {error}" for error in record_errors)
        if record_errors or not isinstance(record, dict):
            continue
        observation_id = record["observation_id"]
        if observation_id in seen_ids:
            errors.append(f"record {index}: duplicate observation_id")
        seen_ids.add(observation_id)
        observed_at = datetime.fromisoformat(record["observed_at"].replace("Z", "+00:00"))
        run_id = record["run_id"]
        if run_id in last_time and observed_at < last_time[run_id]:
            errors.append(f"record {index}: observed_at moved backwards within run")
        last_time[run_id] = observed_at
    return errors


def load_records(path: Path) -> list[Any]:
    raw = path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        return [json.loads(line) for line in raw.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON, JSON array, or JSON Lines file")
    parser.add_argument("--root", type=Path, help="root for relative evidence paths")
    args = parser.parse_args()
    try:
        records = load_records(args.input)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    errors = validate_stream(records, args.root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid: {len(records)} observation(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
