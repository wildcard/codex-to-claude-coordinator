#!/usr/bin/env python3
"""Check public skill discovery without treating direct install as search proof."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER = "wildcard"
REPOSITORY = "codex-to-claude-coordinator"
SOURCE = f"{OWNER}/{REPOSITORY}"
SKILLS = (
    "claude-to-codex-coordinator",
    "codex-to-claude-coordinator",
    "coordination-conformance",
    "coordination-core",
)


@dataclass(frozen=True)
class Check:
    surface: str
    state: str
    detail: str


def frontmatter_description(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path}: missing frontmatter")
    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    raise ValueError(f"{path}: missing description")


def fetch_text(url: str, timeout: float = 20.0) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "codex-to-claude-coordinator-discovery-check/0.2"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def check_skills_sh_details() -> Check:
    missing: list[str] = []
    for skill in SKILLS:
        url = f"https://www.skills.sh/{SOURCE}/{skill}"
        try:
            html = fetch_text(url)
            description = frontmatter_description(ROOT / "skills" / skill / "SKILL.md")
        except (OSError, ValueError, urllib.error.URLError) as exc:
            missing.append(f"{skill} ({exc})")
            continue
        if description[:32] not in html:
            missing.append(skill)
    if missing:
        return Check(
            "skills.sh detail documents",
            "pending",
            "missing populated descriptions: " + ", ".join(missing),
        )
    return Check(
        "skills.sh detail documents",
        "pass",
        "all four pages contain their published descriptions",
    )


def check_skills_sh_search() -> Check:
    query = urllib.parse.urlencode({"q": "coordinator", "owner": OWNER})
    try:
        payload = json.loads(fetch_text(f"https://skills.sh/api/search?{query}"))
    except (json.JSONDecodeError, OSError, urllib.error.URLError) as exc:
        return Check("skills.sh search API", "unknown", str(exc))

    found = {
        item.get("skillId") or item.get("name")
        for item in payload.get("skills", [])
        if item.get("source") == SOURCE
    }
    missing = sorted(set(SKILLS) - found)
    if missing:
        return Check(
            "skills.sh search API",
            "pending",
            "missing indexed skills: " + ", ".join(missing),
        )
    return Check(
        "skills.sh search API",
        "pass",
        "owner-scoped coordinator search returns all four skills",
    )


def check_github_skill_search() -> Check:
    try:
        result = subprocess.run(
            [
                "gh",
                "skill",
                "search",
                "coordinator",
                "--owner",
                OWNER,
                "--limit",
                "50",
                "--json",
                "skillName,repo,path",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return Check("GitHub skill search", "unknown", str(exc))
    if result.returncode:
        return Check(
            "GitHub skill search",
            "unknown",
            result.stderr.strip() or f"gh exited {result.returncode}",
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return Check("GitHub skill search", "unknown", str(exc))

    found = {
        item.get("skillName") for item in payload if item.get("repo") == SOURCE
    }
    missing = sorted(set(SKILLS) - found)
    if missing:
        return Check(
            "GitHub skill search",
            "pending",
            "missing indexed skills: " + ", ".join(missing),
        )
    return Check(
        "GitHub skill search",
        "pass",
        "owner-scoped search returns all four skills",
    )


def run_checks() -> list[Check]:
    return [
        check_skills_sh_details(),
        check_skills_sh_search(),
        check_github_skill_search(),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()
    checks = run_checks()
    if args.json:
        print(json.dumps([asdict(check) for check in checks], indent=2))
    else:
        for check in checks:
            print(f"{check.state.upper():7} {check.surface}: {check.detail}")
    return 0 if all(check.state == "pass" for check in checks) else 2


if __name__ == "__main__":
    sys.exit(main())
