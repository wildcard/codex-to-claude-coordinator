#!/usr/bin/env python3
"""Append one validated observation to a local experiment run."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from validate import load_records, validate_stream


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _platform_name() -> str:
    return {
        "Darwin": "macos",
        "Windows": "windows",
        "Linux": "linux",
    }.get(platform.system(), "unknown")


def _kind(path: Path) -> str:
    if path.suffix.lower() in IMAGE_SUFFIXES:
        return "screenshot"
    if "transcript" in path.name.lower():
        return "transcript"
    if "log" in path.name.lower() or path.suffix.lower() in {".log", ".jsonl"}:
        return "log"
    return "artifact"


def build_evidence(
    path: Path,
    run_dir: Path,
    *,
    privacy_checked: bool = False,
    evidence_source: str = "product-export",
) -> dict[str, Any]:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(run_dir.resolve())
    except ValueError as exc:
        raise ValueError("evidence must already be inside the run directory") from exc
    kind = _kind(path)
    redacted = ".redacted." in path.name
    if kind == "screenshot" and not redacted:
        raise ValueError("screenshots must be redacted derivatives")
    return {
        "path": relative.as_posix(),
        "sha256": _sha256(path),
        "kind": kind,
        "redacted": redacted,
        "source": "redacted-derivative" if redacted else evidence_source,
        "privacy_checked": privacy_checked,
    }


def build_record(
    *,
    run_id: str,
    experiment: str,
    surface: str,
    surface_version: str,
    account_class: str,
    operation: str,
    input_id: str,
    observation: dict[str, Any],
    evidence_paths: list[Path],
    run_dir: Path,
    evidence_class: str = "observed",
    limitations: list[str] | None = None,
    observed_at: str | None = None,
    privacy_checked: bool = False,
    evidence_source: str = "product-export",
) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "observation_id": f"obs-{uuid.uuid4().hex}",
        "experiment": experiment,
        "run_id": run_id,
        "observed_at": observed_at or datetime.now().astimezone().isoformat(),
        "surface": surface,
        "surface_version": surface_version,
        "account_class": account_class,
        "host_platform": _platform_name(),
        "operation": operation,
        "input_id": input_id,
        "observation": observation,
        "evidence_files": [
            build_evidence(
                path,
                run_dir,
                privacy_checked=privacy_checked,
                evidence_source=evidence_source,
            )
            for path in evidence_paths
        ],
        "evidence_class": evidence_class,
        "limitations": limitations or [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--surface", required=True)
    parser.add_argument("--surface-version", default="unknown")
    parser.add_argument(
        "--account-class",
        choices=("pro", "max", "team", "enterprise", "unknown"),
        default="unknown",
    )
    parser.add_argument("--operation", required=True)
    parser.add_argument("--input-id", required=True)
    parser.add_argument("--observation", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, action="append", default=[])
    parser.add_argument(
        "--evidence-source",
        choices=("product-export", "synthetic"),
        default="product-export",
        help="source for unredacted artifact evidence; redacted derivatives override it",
    )
    parser.add_argument(
        "--privacy-checked",
        action="store_true",
        help="confirm every evidence derivative was manually reviewed",
    )
    parser.add_argument("--limitation", action="append", default=[])
    parser.add_argument("--evidence-class", default="observed")
    args = parser.parse_args()

    try:
        observation = json.loads(args.observation.read_text(encoding="utf-8"))
        args.run_dir.mkdir(parents=True, exist_ok=True)
        record = build_record(
            run_id=args.run_id,
            experiment=args.experiment,
            surface=args.surface,
            surface_version=args.surface_version,
            account_class=args.account_class,
            operation=args.operation,
            input_id=args.input_id,
            observation=observation,
            evidence_paths=[
                path if path.is_absolute() else args.run_dir / path
                for path in args.evidence
            ],
            run_dir=args.run_dir,
            evidence_class=args.evidence_class,
            limitations=args.limitation,
            privacy_checked=args.privacy_checked,
            evidence_source=args.evidence_source,
        )
        output = args.run_dir / "observations.jsonl"
        existing = load_records(output) if output.exists() else []
        errors = validate_stream([*existing, record], args.run_dir)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        with output.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
