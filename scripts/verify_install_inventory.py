#!/usr/bin/env python3
"""Verify an isolated skills CLI installation for the supported launch set."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EXPECTED_SKILLS = {
    "claude-to-codex-coordinator",
    "codex-to-claude-coordinator",
    "coordination-conformance",
    "coordination-core",
}
INSTALL_ROOT_AGENTS = {
    ".agents/skills": ("Codex", "Cursor", "GitHub Copilot"),
    ".claude/skills": ("Claude Code",),
    ".goose/skills": ("Goose",),
    ".openhands/skills": ("OpenHands",),
}
REQUIRED_DISTINCT_ROOT_LABELS = {"Claude Code", "Goose", "OpenHands"}
REQUIRED_SUPPORT_FILES = (
    "coordination-core/scripts/classify.py",
    "coordination-core/schemas/envelope.schema.json",
    "coordination-conformance/scripts/validate.py",
    "coordination-conformance/references/evidence-policy.md",
    "codex-to-claude-coordinator/agents/openai.yaml",
    "claude-to-codex-coordinator/scripts/probe.py",
    "claude-to-codex-coordinator/references/openai-codex-plugin-cc.md",
)


def validate(inventory_path: Path, install_root: Path) -> list[str]:
    errors: list[str] = []
    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid inventory: {exc}"]
    if not isinstance(inventory, list):
        return ["inventory must be a JSON array"]

    entries = {
        entry.get("name"): entry for entry in inventory if isinstance(entry, dict)
    }
    if set(entries) != EXPECTED_SKILLS:
        errors.append(
            f"inventory mismatch: expected {sorted(EXPECTED_SKILLS)}, "
            f"found {sorted(entries)}"
        )
    for skill_name in sorted(EXPECTED_SKILLS):
        agents = entries.get(skill_name, {}).get("agents")
        if not isinstance(agents, list) or not all(
            isinstance(agent, str) for agent in agents
        ):
            errors.append(f"{skill_name}: inventory agents must be a string array")
        else:
            missing_labels = REQUIRED_DISTINCT_ROOT_LABELS - set(agents)
            if missing_labels:
                errors.append(
                    f"{skill_name}: missing distinct-root inventory agents "
                    f"{sorted(missing_labels)}"
                )
        for native_root, agent_names in INSTALL_ROOT_AGENTS.items():
            skill_file = install_root / native_root / skill_name / "SKILL.md"
            if not skill_file.is_file():
                errors.append(
                    f"{skill_name}: missing native install "
                    f"{skill_file.relative_to(install_root)} for "
                    f"{', '.join(agent_names)}"
                )

    canonical = install_root / ".agents" / "skills"
    for relative in REQUIRED_SUPPORT_FILES:
        if not (canonical / relative).is_file():
            errors.append(f"copied install is missing support file {relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--install-root", type=Path, required=True)
    args = parser.parse_args()
    errors = validate(args.inventory.resolve(), args.install_root.resolve())
    if errors:
        print("Install inventory verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Install inventory verification passed: 4 skills across Codex, "
        "Claude Code, Cursor, GitHub Copilot, Goose, and OpenHands."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
