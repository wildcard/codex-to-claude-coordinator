import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


launch_module = load_module("launch_verifier", ROOT / "scripts" / "verify_launch.py")


class LaunchVerifierTests(unittest.TestCase):
    def test_relative_links_ignore_fenced_examples(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "SKILL.md"
            path.write_text(
                "[real](references/real.md)\n"
                "```md\n"
                "[example](not-a-package-file.md)\n"
                "```\n",
                encoding="utf-8",
            )
            self.assertEqual(
                launch_module.relative_markdown_links(path),
                ["references/real.md"],
            )


if __name__ == "__main__":
    unittest.main()
