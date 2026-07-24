#!/usr/bin/env python3
"""Fail-closed launch checks for the distributable coordination bundle."""

from __future__ import annotations

import json
import re
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    "codex-to-claude-coordinator",
    "coordination-conformance",
    "coordination-core",
}
PRIVATE_LITERALS = (
    "kobik-private",
    "/Users/kobik",
    "sk-proj-",
    "sk-ant-",
    "ghp_",
    "BEGIN PRIVATE KEY",
)
REQUIRED_PLUGIN_KEYWORDS = {
    "codex",
    "claude",
    "claude-code",
    "multi-agent",
    "cross-harness",
}
EXPECTED_PILLOW_REQUIREMENT = "Pillow==11.3.0"


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening YAML delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing YAML delimiter") from exc

    result: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"unsupported frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip("\"'")
    return result


def yaml_scalar(path: Path, key: str) -> str | None:
    pattern = re.compile(rf"^\s*{re.escape(key)}:\s*[\"']?([^\"']+?)[\"']?\s*$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return None


def relative_markdown_links(path: Path) -> list[str]:
    lines: list[str] = []
    active_fence: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        fence = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)[0]
            if active_fence is None:
                active_fence = marker
            elif active_fence == marker:
                active_fence = None
            continue
        if active_fence is None:
            lines.append(line)
    targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", "\n".join(lines))
    return [
        target.split("#", 1)[0]
        for target in targets
        if target
        and not target.startswith(("#", "http://", "https://", "mailto:"))
    ]


def iter_package_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if (
            ".git" in relative.parts
            or "__pycache__" in relative.parts
            or relative.parts[:2] == ("experiments", "runs")
            or path.resolve() == Path(__file__).resolve()
        ):
            continue
        if path.suffix.lower() in {".json", ".md", ".py", ".txt", ".yaml", ".yml"}:
            yield path


def git_tracked_run_evidence() -> list[str]:
    if not (ROOT / ".git").exists():
        return []
    result = subprocess.run(
        ["git", "ls-files", "--", "experiments/runs"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        line
        for line in result.stdout.splitlines()
        if line and line != "experiments/runs/.gitkeep"
    ]


def check() -> list[str]:
    errors: list[str] = []
    package_text: dict[Path, str] = {}
    encoding_failed = False
    for path in iter_package_text_files():
        try:
            package_text[path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: is not valid UTF-8: {exc}")
            encoding_failed = True
    if encoding_failed:
        return errors

    skill_root = ROOT / "skills"
    actual_skills = {
        path.parent.name for path in skill_root.glob("*/SKILL.md") if path.is_file()
    }
    if actual_skills != EXPECTED_SKILLS:
        errors.append(
            f"skill set mismatch: expected {sorted(EXPECTED_SKILLS)}, "
            f"found {sorted(actual_skills)}"
        )

    for skill_name in sorted(EXPECTED_SKILLS):
        directory = skill_root / skill_name
        skill_path = directory / "SKILL.md"
        metadata_path = directory / "agents" / "openai.yaml"
        if not skill_path.is_file():
            errors.append(f"{skill_name}: missing SKILL.md")
            continue
        try:
            metadata = parse_frontmatter(skill_path)
        except ValueError as exc:
            errors.append(f"{skill_name}: {exc}")
            continue

        if metadata.get("name") != skill_name:
            errors.append(
                f"{skill_name}: frontmatter name must match its directory name"
            )
        description = metadata.get("description", "")
        if len(description) < 80:
            errors.append(f"{skill_name}: description is too short for reliable discovery")
        if not re.search(
            r"\b(coordinat|delegat|orchestrat|harness|multi-agent)", description, re.I
        ):
            errors.append(f"{skill_name}: description lacks a discovery trigger")

        if not metadata_path.is_file():
            errors.append(f"{skill_name}: missing agents/openai.yaml")
        else:
            prompt = yaml_scalar(metadata_path, "default_prompt")
            if not prompt or f"${skill_name}" not in prompt:
                errors.append(
                    f"{skill_name}: default_prompt must explicitly invoke ${skill_name}"
                )

        for target in relative_markdown_links(skill_path):
            if not (directory / target).is_file():
                errors.append(f"{skill_name}: broken relative link {target!r}")

        for script in (directory / "scripts").glob("*.py"):
            source = script.read_text(encoding="utf-8")
            try:
                compile(source, str(script), "exec")
            except SyntaxError as exc:
                errors.append(f"{script.relative_to(ROOT)}: {exc}")
            if not script.stat().st_mode & stat.S_IXUSR:
                errors.append(f"{script.relative_to(ROOT)}: script is not executable")

    codex_manifest_path = ROOT / ".codex-plugin" / "plugin.json"
    claude_manifest_path = ROOT / ".claude-plugin" / "plugin.json"
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    manifests: dict[str, dict] = {}
    for label, path in (
        ("Codex plugin", codex_manifest_path),
        ("Claude plugin", claude_manifest_path),
        ("Claude marketplace", marketplace_path),
    ):
        try:
            manifests[label] = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            errors.append(f"{label}: invalid or missing JSON: {exc}")

    codex_manifest = manifests.get("Codex plugin", {})
    claude_manifest = manifests.get("Claude plugin", {})
    marketplace = manifests.get("Claude marketplace", {})
    if codex_manifest.get("name") != "codex-to-claude-coordinator":
        errors.append("Codex plugin: unexpected name")
    if claude_manifest.get("name") != "codex-to-claude-coordinator":
        errors.append("Claude plugin: unexpected name")
    if codex_manifest.get("version") != claude_manifest.get("version"):
        errors.append("plugin manifest versions are not synchronized")
    if codex_manifest.get("skills") != "./skills/":
        errors.append("Codex plugin: skills must point to ./skills/")
    if claude_manifest.get("skills") != ["./skills/"]:
        errors.append("Claude plugin: skills must point to [\"./skills/\"]")
    for label, manifest in (
        ("Codex plugin", codex_manifest),
        ("Claude plugin", claude_manifest),
    ):
        keywords = manifest.get("keywords")
        if not isinstance(keywords, list) or not REQUIRED_PLUGIN_KEYWORDS.issubset(
            keywords
        ):
            errors.append(
                f"{label}: keywords must include "
                + ", ".join(sorted(REQUIRED_PLUGIN_KEYWORDS))
            )

    starter_prompts = codex_manifest.get("interface", {}).get("defaultPrompt")
    if (
        not isinstance(starter_prompts, list)
        or not 1 <= len(starter_prompts) <= 3
        or not all(
            isinstance(prompt, str)
            and 1 <= len(prompt) <= 128
            and bool(prompt.strip())
            for prompt in starter_prompts
        )
    ):
        errors.append(
            "Codex plugin: interface.defaultPrompt must contain 1-3 "
            "non-empty strings of at most 128 characters"
        )

    plugins = marketplace.get("plugins", [])
    if (
        marketplace.get("name") != "codex-to-claude-coordinator"
        or len(plugins) != 1
        or plugins[0].get("source") != "./"
    ):
        errors.append("Claude marketplace must expose this repository as one plugin")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required_readme_fragments = (
        "npx skills add wildcard/codex-to-claude-coordinator",
        "--agent codex",
        "/codex-to-claude-coordinator:coordination-core",
        "docs/launch-readiness.md",
    )
    for fragment in required_readme_fragments:
        if fragment not in readme:
            errors.append(f"README is missing launch instruction {fragment!r}")
    changelog = ROOT / "CHANGELOG.md"
    if not changelog.is_file() or "## Unreleased" not in changelog.read_text(
        encoding="utf-8"
    ):
        errors.append("CHANGELOG.md must contain an Unreleased release entry")

    requirements_path = (
        ROOT / "skills" / "coordination-conformance" / "requirements.txt"
    )
    try:
        requirements = {
            line.strip()
            for line in requirements_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
    except FileNotFoundError:
        errors.append("coordination-conformance: missing requirements.txt")
    else:
        if EXPECTED_PILLOW_REQUIREMENT not in requirements:
            errors.append(
                "coordination-conformance: Pillow must be pinned to "
                f"{EXPECTED_PILLOW_REQUIREMENT}"
            )

    tracked_evidence = git_tracked_run_evidence()
    if tracked_evidence:
        errors.append(
            "raw experiment run evidence is tracked: " + ", ".join(tracked_evidence)
        )

    for path, text in package_text.items():
        for literal in PRIVATE_LITERALS:
            if literal.lower() in text.lower():
                errors.append(
                    f"{path.relative_to(ROOT)}: contains private literal {literal!r}"
                )
        if re.search(r"\b(?:TODO|FIXME)\b", text):
            errors.append(f"{path.relative_to(ROOT)}: contains TODO or FIXME")

    return errors


def main() -> int:
    errors = check()
    if errors:
        print("Launch verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Launch verification passed: 3 skills, synchronized manifests, "
        "complete references, executable scripts, and privacy boundary."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
