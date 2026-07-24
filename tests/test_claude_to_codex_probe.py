import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE = (
    ROOT
    / "skills"
    / "claude-to-codex-coordinator"
    / "scripts"
    / "probe.py"
)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


probe_module = load_module("claude_to_codex_probe", PROBE)


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.outputs = {
            ("node", "--version"): (0, "v24.1.0\n", ""),
            ("claude", "--version"): (0, "2.1.218 (Claude Code)\n", ""),
            (
                "claude",
                "plugin",
                "list",
                "--json",
            ): (
                0,
                '[{"id":"codex@openai-codex","version":"1.0.6",'
                '"scope":"user","enabled":true}]',
                "",
            ),
            ("codex", "--version"): (0, "codex-cli 0.145.0\n", ""),
            ("codex", "login", "status"): (
                0,
                "Logged in using ChatGPT as private@example.test\n",
                "",
            ),
        }

    def fake_run(self, argv, timeout):
        returncode, stdout, stderr = self.outputs[tuple(argv)]
        return {
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr,
        }

    @staticmethod
    def which(name):
        return f"/fixture/{name}"

    def test_ready_report_omits_identity_and_paths(self):
        report = probe_module.build_report(run=self.fake_run, which=self.which)
        self.assertTrue(report["ready"])
        self.assertEqual(report["codex"]["auth_method"], "chatgpt")
        serialized = str(report)
        self.assertNotIn("private@example.test", serialized)
        self.assertNotIn("/fixture/", serialized)
        self.assertFalse(report["privacy"]["raw_auth_output_included"])
        self.assertFalse(report["privacy"]["install_path_included"])

    def test_disabled_plugin_fails_closed(self):
        self.outputs[("claude", "plugin", "list", "--json")] = (
            0,
            '[{"id":"codex@openai-codex","version":"1.0.6",'
            '"scope":"user","enabled":false}]',
            "",
        )
        report = probe_module.build_report(run=self.fake_run, which=self.which)
        self.assertFalse(report["ready"])
        self.assertFalse(report["plugin"]["enabled"])

    def test_old_node_fails_closed(self):
        self.outputs[("node", "--version")] = (0, "v18.17.9\n", "")
        report = probe_module.build_report(run=self.fake_run, which=self.which)
        self.assertFalse(report["ready"])
        self.assertFalse(report["node"]["meets_minimum"])

    def test_skill_resolves_probe_from_packaged_root(self):
        skill_text = (PROBE.parents[1] / "SKILL.md").read_text()
        expected = (
            '${CLAUDE_PLUGIN_ROOT}/skills/'
            "claude-to-codex-coordinator/scripts/probe.py"
        )
        self.assertIn(expected, skill_text)
        self.assertNotIn("python3 scripts/probe.py", skill_text)


if __name__ == "__main__":
    unittest.main()
