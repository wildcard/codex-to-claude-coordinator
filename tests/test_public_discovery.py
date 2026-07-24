import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_public_discovery.py"
SPEC = importlib.util.spec_from_file_location("check_public_discovery", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PublicDiscoveryTests(unittest.TestCase):
    def test_frontmatter_description_reads_published_metadata(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "claude-to-codex-coordinator"
            / "SKILL.md"
        )
        self.assertTrue(
            MODULE.frontmatter_description(path).startswith(
                "Coordinate Claude Code-to-Codex delegation"
            )
        )

    @mock.patch.object(MODULE, "fetch_text")
    def test_skills_sh_search_requires_every_expected_skill(self, fetch_text):
        fetch_text.return_value = json.dumps(
            {
                "skills": [
                    {
                        "source": MODULE.SOURCE,
                        "skillId": skill,
                    }
                    for skill in MODULE.SKILLS[:-1]
                ]
            }
        )
        result = MODULE.check_skills_sh_search()
        self.assertEqual(result.state, "pending")
        self.assertIn(MODULE.SKILLS[-1], result.detail)

    @mock.patch.object(MODULE.subprocess, "run")
    def test_github_search_requires_repository_match(self, run):
        run.return_value = subprocess.CompletedProcess(
            [],
            0,
            stdout=json.dumps(
                [
                    {
                        "repo": MODULE.SOURCE,
                        "skillName": skill,
                        "path": f"skills/{skill}/SKILL.md",
                    }
                    for skill in MODULE.SKILLS
                ]
            ),
            stderr="",
        )
        result = MODULE.check_github_skill_search()
        self.assertEqual(result.state, "pass")


if __name__ == "__main__":
    unittest.main()
