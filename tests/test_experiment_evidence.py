import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE = ROOT / "skills" / "coordination-conformance"
SCRIPTS = CONFORMANCE / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validate_module = load_module("experiment_validate", SCRIPTS / "validate.py")
record_module = load_module("experiment_record", SCRIPTS / "record.py")
redact_module = load_module("experiment_redact", SCRIPTS / "redact.py")
summarize_module = load_module("experiment_summarize", SCRIPTS / "summarize.py")


class ExperimentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        evidence_dir = self.root / "evidence"
        evidence_dir.mkdir()
        self.evidence_path = evidence_dir / "panel.redacted.txt"
        self.evidence_path.write_text("generic evidence\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def evidence(self, **overrides):
        value = {
            "path": "evidence/panel.redacted.txt",
            "sha256": hashlib.sha256(self.evidence_path.read_bytes()).hexdigest(),
            "kind": "artifact",
            "redacted": True,
            "source": "redacted-derivative",
            "privacy_checked": True,
        }
        value.update(overrides)
        return value

    def record(self, **overrides):
        value = {
            "schema_version": "0.1",
            "observation_id": "obs-1",
            "experiment": "dispatch-behavior",
            "run_id": "local-test",
            "observed_at": "2026-07-23T12:00:00-07:00",
            "surface": "test-surface",
            "surface_version": "test",
            "account_class": "unknown",
            "host_platform": "macos",
            "operation": "start_session",
            "input_id": "fixture-read-only-v1",
            "observation": {"result": "pass"},
            "evidence_files": [self.evidence()],
            "evidence_class": "observed",
            "limitations": [],
        }
        value.update(overrides)
        return value

    def usage(self, **overrides):
        value = {
            "kind": "usage_signal",
            "result": "observed",
            "label_verbatim": "Weekly named model",
            "value_verbatim": "20%",
            "direction": "consumed",
            "scope": "model",
            "model_name_verbatim": "Named model",
            "window_start": None,
            "window_end": None,
            "reset_at": "2026-07-26T09:00:00-07:00",
            "captured_at": "2026-07-23T12:00:00-07:00",
            "freshness": "timestamped",
            "threshold_eligible": True,
        }
        value.update(overrides)
        return value

    def test_valid_record(self):
        self.assertEqual(validate_module.validate_record(self.record(), self.root), [])

    def test_missing_provenance_fails_closed(self):
        record = self.record()
        del record["evidence_class"]
        errors = validate_module.validate_record(record, self.root)
        self.assertTrue(any("missing top-level keys" in error for error in errors))

    def test_plan_meter_cannot_be_threshold_eligible(self):
        record = self.record(
            experiment="quota-signal-fidelity",
            operation="inspect_usage",
            observation=self.usage(scope="plan"),
        )
        errors = validate_module.validate_record(record, self.root)
        self.assertIn("threshold automation requires model scope", errors)

    def test_threshold_percentage_accepts_decimal_without_leading_zero(self):
        record = self.record(
            experiment="quota-signal-fidelity",
            operation="inspect_usage",
            observation=self.usage(value_verbatim="81.5%"),
        )
        self.assertEqual(validate_module.validate_record(record, self.root), [])

        for invalid in ("05%", "100.1%"):
            record["observation"]["value_verbatim"] = invalid
            errors = validate_module.validate_record(record, self.root)
            self.assertIn(
                "threshold automation requires an explicit percentage",
                errors,
            )

    def test_screenshot_requires_redacted_derivative(self):
        raw = self.root / "raw.png"
        raw.write_bytes(b"not a real image")
        record = self.record(
            evidence_files=[
                self.evidence(
                    path="raw.png",
                    sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                    kind="screenshot",
                    redacted=False,
                    source="product-export",
                )
            ]
        )
        errors = validate_module.validate_record(record, self.root)
        self.assertTrue(any("screenshots, transcripts, and logs" in e for e in errors))

    def test_transcript_requires_redacted_derivative(self):
        record = self.record(
            evidence_files=[
                self.evidence(
                    kind="transcript",
                    redacted=False,
                    source="product-export",
                )
            ]
        )
        errors = validate_module.validate_record(record, self.root)
        self.assertTrue(any("transcripts" in error for error in errors))

    def test_archive_is_not_a_successful_stop(self):
        record = self.record(
            operation="stop_session",
            observation={
                "result": "pass",
                "action": "archive",
                "terminal_state": "archived",
            },
        )
        errors = validate_module.validate_record(record, self.root)
        self.assertTrue(any("cannot pass stop_session" in error for error in errors))
        self.assertTrue(any("terminal worker state" in error for error in errors))

    def test_hash_mismatch_is_rejected(self):
        record = self.record(evidence_files=[self.evidence(sha256="0" * 64)])
        errors = validate_module.validate_record(record, self.root)
        self.assertTrue(any("sha256 does not match" in error for error in errors))

    def test_privacy_denylist_scans_record_and_text_evidence(self):
        record = self.record(surface="person@example.com")
        errors = validate_module.validate_record(record, self.root)
        self.assertTrue(any("email address" in error for error in errors))

        self.evidence_path.write_text("/Users/private-name/secret\n", encoding="utf-8")
        record = self.record(evidence_files=[self.evidence()])
        errors = validate_module.validate_record(record, self.root)
        self.assertTrue(any("macOS home path" in error for error in errors))

    def test_timestamp_order_is_append_only(self):
        later = self.record()
        earlier = self.record(
            observation_id="obs-2",
            observed_at="2026-07-23T11:59:00-07:00",
        )
        errors = validate_module.validate_stream([later, earlier], self.root)
        self.assertTrue(any("moved backwards" in error for error in errors))

    def test_recorder_builds_valid_evidence_record(self):
        record = record_module.build_record(
            run_id="local-test",
            experiment="dispatch-behavior",
            surface="test-surface",
            surface_version="test",
            account_class="unknown",
            operation="start_session",
            input_id="fixture-read-only-v1",
            observation={"result": "pass"},
            evidence_paths=[self.evidence_path],
            run_dir=self.root,
            observed_at="2026-07-23T12:00:00-07:00",
            privacy_checked=True,
        )
        self.assertEqual(validate_module.validate_record(record, self.root), [])

    def test_recorder_does_not_infer_privacy_review(self):
        record = record_module.build_record(
            run_id="local-test",
            experiment="dispatch-behavior",
            surface="test-surface",
            surface_version="test",
            account_class="unknown",
            operation="start_session",
            input_id="fixture-read-only-v1",
            observation={"result": "pass"},
            evidence_paths=[self.evidence_path],
            run_dir=self.root,
            observed_at="2026-07-23T12:00:00-07:00",
        )
        errors = validate_module.validate_record(record, self.root)
        self.assertTrue(any("privacy_checked must be true" in error for error in errors))

    def test_recorder_preserves_synthetic_artifact_source(self):
        synthetic = self.root / "evidence" / "fixture.json"
        synthetic.write_text('{"fixture": true}\n', encoding="utf-8")
        record = record_module.build_record(
            run_id="local-test",
            experiment="dispatch-behavior",
            surface="test-surface",
            surface_version="test",
            account_class="unknown",
            operation="start_session",
            input_id="fixture-read-only-v1",
            observation={"result": "pass"},
            evidence_paths=[synthetic],
            run_dir=self.root,
            observed_at="2026-07-23T12:00:00-07:00",
            privacy_checked=True,
            evidence_source="synthetic",
        )
        self.assertEqual(record["evidence_files"][0]["source"], "synthetic")
        self.assertEqual(validate_module.validate_record(record, self.root), [])

    def test_text_redactor_removes_common_identifiers(self):
        raw = (
            "person@example.com /Users/private-name/work "
            "access_token=secret-value"
        )
        redacted = redact_module.redact_text(raw)
        self.assertNotIn("person@example.com", redacted)
        self.assertNotIn("private-name", redacted)
        self.assertNotIn("secret-value", redacted)
        self.assertEqual(validate_module.privacy_errors(redacted), [])

    def test_image_redactor_removes_metadata_and_blacks_rectangle(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")
        raw = self.root / "raw.png"
        output = self.root / "panel.redacted.png"
        from PIL.PngImagePlugin import PngInfo

        image = Image.new("RGB", (8, 8), color=(255, 255, 255))
        metadata = PngInfo()
        metadata.add_text("author", "private")
        image.save(raw, pnginfo=metadata)
        redact_module.redact_file(raw, output, [(0, 0, 4, 4)])
        with Image.open(output) as result:
            self.assertEqual(result.getpixel((1, 1)), (0, 0, 0))
            self.assertFalse(result.getexif())
            self.assertNotIn("author", result.info)

    def test_capability_summary_preserves_unknown(self):
        manifest = summarize_module.summarize(
            [self.record()],
            "local-test",
            generated_at="2026-07-23T12:01:00-07:00",
        )
        self.assertEqual(manifest["capabilities"]["start_session"]["status"], "pass")
        self.assertEqual(
            manifest["capabilities"]["stop_session"]["status"], "unknown"
        )
        self.assertEqual(
            manifest["capabilities"]["stop_session"]["evidence_count"], 0
        )

    def test_capability_summary_uses_latest_timestamp(self):
        later = self.record(
            observation_id="obs-later",
            observed_at="2026-07-23T13:00:00-07:00",
            observation={"result": "fail"},
        )
        earlier = self.record(
            observation_id="obs-earlier",
            observed_at="2026-07-23T12:00:00-07:00",
            observation={"result": "pass"},
        )
        manifest = summarize_module.summarize(
            [later, earlier],
            "local-test",
            generated_at="2026-07-23T13:01:00-07:00",
        )
        self.assertEqual(manifest["capabilities"]["start_session"]["status"], "fail")

    def test_threshold_signal_can_pass_only_with_complete_evidence(self):
        record = self.record(
            experiment="quota-signal-fidelity",
            operation="inspect_usage",
            observation=self.usage(),
        )
        self.assertEqual(validate_module.validate_record(record, self.root), [])


if __name__ == "__main__":
    unittest.main()
