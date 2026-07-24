import importlib.util
import itertools
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "coordination-core" / "scripts"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


classify_module = load_module("coordination_classify", SCRIPTS / "classify.py")
envelope_module = load_module(
    "coordination_envelope", SCRIPTS / "validate_envelope.py"
)


def ledger(value="pending"):
    return {key: value for key in envelope_module.LEDGER_KEYS}


def event(seq, kind, emitter, body, event_id=None):
    return {
        "schema_version": "0.1",
        "event_id": event_id or f"event-{seq}",
        "task_id": "task-1",
        "seq": seq,
        "emitted_at": f"2026-07-23T12:{seq:02d}:00-07:00",
        "emitter": emitter,
        "type": kind,
        "body": body,
    }


def assignment(seq=0):
    return event(
        seq,
        "assignment",
        "coordinator",
        {
            "outcome": "Produce a tested local artifact",
            "definition_of_done": ["Targeted tests pass"],
            "owned_paths": ["workspace/owned"],
            "required_evidence": ["test output"],
            "permission_boundary": {
                "push": "forbidden",
                "pull_request": "forbidden",
                "publish": "forbidden",
                "message": "forbidden",
            },
            "requested_tier": "strong",
            "reasoning_effort": "medium",
        },
    )


class ClassificationTests(unittest.TestCase):
    def base(self):
        return {
            "files_in_scope": 1,
            "crosses_systems": False,
            "prior_attempt_failed": False,
            "plan_required": False,
            "external_actions_requested": [],
            "reversible": True,
            "expected_tool_calls": "small",
            "independent_subtasks": 1,
        }

    def test_total_over_representative_cross_product(self):
        seen = set()
        for values in itertools.product(
            (0, 1, 3),
            (False, True),
            (False, True),
            (False, True),
            ((), ("publish",)),
            (False, True),
            ("small", "medium", "large"),
            (0, 1, 2),
        ):
            data = dict(
                zip(
                    (
                        "files_in_scope",
                        "crosses_systems",
                        "prior_attempt_failed",
                        "plan_required",
                        "external_actions_requested",
                        "reversible",
                        "expected_tool_calls",
                        "independent_subtasks",
                    ),
                    values,
                )
            )
            data["external_actions_requested"] = list(
                data["external_actions_requested"]
            )
            result = classify_module.classify(data)
            self.assertEqual(
                set(result),
                {
                    "difficulty",
                    "risk",
                    "duration",
                    "coordination",
                    "requested_tier",
                    "reasoning_effort",
                },
            )
            seen.add(tuple(sorted(result.items())))
        self.assertGreater(len(seen), 6)

    def test_tier_and_effort_are_independent(self):
        data = self.base()
        data["reversible"] = False
        result = classify_module.classify(data)
        self.assertEqual(result["difficulty"], "trivial")
        self.assertEqual(result["requested_tier"], "strong")
        self.assertEqual(result["reasoning_effort"], "high")

    def test_portable_runtime_fixture(self):
        fixture = ROOT / "experiments" / "fixtures" / "classification-read-only"
        input_data = json.loads((fixture / "input.json").read_text(encoding="utf-8"))
        expected = json.loads((fixture / "expected.json").read_text(encoding="utf-8"))
        self.assertEqual(classify_module.classify(input_data), expected)

    def test_instruction_only_contract_exposes_schema_vocabulary(self):
        skill_text = (ROOT / "skills" / "coordination-core" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        schema = json.loads(
            (
                ROOT
                / "skills"
                / "coordination-core"
                / "schemas"
                / "classification.schema.json"
            ).read_text(encoding="utf-8")
        )
        for field, definition in schema["properties"].items():
            self.assertIn(f"`{field}`", skill_text)
            for value in definition["enum"]:
                self.assertIn(f"`{value}`", skill_text)

    def test_invalid_input_fails_closed(self):
        data = self.base()
        data["quota_percent"] = 10
        with self.assertRaisesRegex(ValueError, "unknown keys"):
            classify_module.classify(data)

    def test_portable_core_contains_no_vendor_policy(self):
        core = ROOT / "skills" / "coordination-core"
        forbidden = (
            "fable",
            "opus",
            "sonnet",
            "claude",
            "codex",
            "cursor",
            "/review",
        )
        for path in core.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".py", ".json"}:
                continue
            text = path.read_text().lower()
            for term in forbidden:
                self.assertNotIn(term, text, f"{term!r} leaked into {path}")


class EnvelopeTests(unittest.TestCase):
    def test_valid_assignment(self):
        self.assertEqual(envelope_module.validate_envelope(assignment()), [])

    def test_coordinator_cannot_decide_approval(self):
        decision = event(
            1,
            "approval_decision",
            "coordinator",
            {"request_event_id": "request-1", "decision": "approve"},
        )
        self.assertIn(
            "approval_decision must be emitted by human",
            envelope_module.validate_envelope(decision),
        )

    def test_steer_outside_scope_is_rejected(self):
        steer = event(
            1,
            "steer",
            "coordinator",
            {
                "instruction": "Change one file",
                "evidence_refs": [],
                "target_paths": ["workspace/other/file.txt"],
            },
        )
        errors = envelope_module.validate_stream([assignment(), steer])
        self.assertTrue(any("outside assignment scope" in error for error in errors))

    def test_steer_path_traversal_is_rejected(self):
        steer = event(
            1,
            "steer",
            "coordinator",
            {
                "instruction": "Escape the owned directory",
                "evidence_refs": [],
                "target_paths": ["workspace/owned/../other/file.txt"],
            },
        )
        errors = envelope_module.validate_stream([assignment(), steer])
        self.assertTrue(any("outside assignment scope" in error for error in errors))

    def test_stop_requires_later_terminal_state(self):
        stop = event(
            1,
            "stop",
            "coordinator",
            {"reason": "No new evidence", "mode": "graceful"},
        )
        idle = event(
            2,
            "state",
            "worker",
            {
                "lifecycle_state": "idle",
                "ledger": ledger(),
                "session_ref": "session-1",
                "actual_worker": "unknown",
            },
        )
        errors = envelope_module.validate_stream([assignment(), stop, idle])
        self.assertTrue(any("stop lacks a later terminal state" in error for error in errors))

        stopped = json.loads(json.dumps(idle))
        stopped["seq"] = 3
        stopped["event_id"] = "event-3"
        stopped["emitted_at"] = "2026-07-23T12:03:00-07:00"
        stopped["body"]["lifecycle_state"] = "stopped"
        self.assertEqual(
            envelope_module.validate_stream([assignment(), stop, idle, stopped]),
            [],
        )

    def test_handoff_requires_actual_worker(self):
        handoff = event(
            1,
            "handoff",
            "worker",
            {
                "ledger": ledger("done"),
                "commit": None,
                "review_result": "unavailable",
                "blocker": None,
                "next_action": "Review locally",
            },
        )
        self.assertIn(
            "body missing: actual_worker",
            envelope_module.validate_envelope(handoff),
        )

    def test_handoff_rejects_blank_blocker_fields(self):
        handoff = event(
            1,
            "handoff",
            "worker",
            {
                "actual_worker": "worker-1",
                "ledger": ledger("blocked"),
                "commit": None,
                "review_result": "unavailable",
                "blocker": {
                    "symptom": " ",
                    "working": "Local validation passes",
                    "owner": "human",
                    "parallel_action": "Document the remaining gate",
                },
                "next_action": "Request the missing authority",
            },
        )
        self.assertIn(
            "blocker fields must be non-empty strings",
            envelope_module.validate_envelope(handoff),
        )

    def test_sequence_is_append_only(self):
        duplicate = assignment()
        duplicate["event_id"] = "event-other"
        errors = envelope_module.validate_stream([assignment(), duplicate])
        self.assertTrue(any("seq must strictly increase" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
