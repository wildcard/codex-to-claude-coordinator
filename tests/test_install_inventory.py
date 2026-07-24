import importlib.util
import json
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


inventory_module = load_module(
    "install_inventory_verifier",
    ROOT / "scripts" / "verify_install_inventory.py",
)


class InstallInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.install_root = Path(self.temp.name)
        self.inventory_path = self.install_root / "inventory.json"
        inventory = [
            {"name": skill_name, "agents": ["Claude Code", "Goose", "OpenHands"]}
            for skill_name in sorted(inventory_module.EXPECTED_SKILLS)
        ]
        self.inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

        for native_root in inventory_module.INSTALL_ROOT_AGENTS:
            for skill_name in inventory_module.EXPECTED_SKILLS:
                skill_path = self.install_root / native_root / skill_name / "SKILL.md"
                skill_path.parent.mkdir(parents=True, exist_ok=True)
                skill_path.write_text(f"# {skill_name}\n", encoding="utf-8")

        canonical = self.install_root / ".agents" / "skills"
        for relative in inventory_module.REQUIRED_SUPPORT_FILES:
            path = canonical / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_host_detection_labels_do_not_define_install_success(self):
        self.assertEqual(
            inventory_module.validate(self.inventory_path, self.install_root),
            [],
        )

    def test_missing_universal_root_fails_all_shared_harnesses(self):
        missing = (
            self.install_root
            / ".agents"
            / "skills"
            / "coordination-core"
            / "SKILL.md"
        )
        missing.unlink()
        errors = inventory_module.validate(self.inventory_path, self.install_root)
        self.assertTrue(
            any(
                "Codex, Cursor, GitHub Copilot" in error
                and "coordination-core" in error
                for error in errors
            )
        )

    def test_missing_distinct_root_inventory_label_fails(self):
        inventory = json.loads(self.inventory_path.read_text(encoding="utf-8"))
        inventory[0]["agents"] = ["Goose", "OpenHands"]
        self.inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
        errors = inventory_module.validate(self.inventory_path, self.install_root)
        self.assertTrue(
            any("missing distinct-root inventory agents" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
