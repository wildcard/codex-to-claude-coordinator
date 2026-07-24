# Research roadmap

Status: planned
Last checked: 2026-07-23

## Experiment 0: Claude Dispatch discovery

Question: Does the observed `Dispatch Beta` surface behave like the official Dispatch guide?

Method:

1. Inspect the surface and record only product-visible labels and controls.
2. Create a harmless repository-reading task with no external writes.
3. Capture session creation, steering, status, stop, permissions, and result behavior.
4. Check whether it can select models, expose usage, and coordinate Claude Code sessions.
5. Compare the observed behavior with the [official Dispatch guide](https://claude.com/docs/cowork/guide/dispatch).

Acceptance evidence:

- dated screenshots or structured notes;
- exact task lifecycle;
- permission prompts;
- a list of supported and missing adapter operations;
- explicit separation between observed behavior and inference.

Known documented baseline:

- one Dispatch conversation can create multiple child Cowork or Code sessions;
- child tasks do not create further Dispatch children;
- each child exposes status and a transcript;
- permission requests are forwarded to the human and auto-denied after ten minutes;
- follow-up messages are supported;
- no public lifecycle API or model-selection surface is documented.

## Experiment 1: quota-signal fidelity

Question: Can the requested Fable and Opus thresholds be measured from a reliable model-specific signal?

Method:

1. Record every visible usage meter and its exact label.
2. Compare Claude Desktop, Claude Code `/usage`, and another authenticated device.
3. Separate context, shared plan or weekly, model-specific, and API-cost signals.
4. Recheck after known model usage.
5. Record staleness and rate-limit behavior.

Acceptance evidence:

- no inferred or relabeled meter;
- screenshots or exported values with timestamps;
- agreement or disagreement across surfaces;
- a decision on whether thresholds can be automated or must remain availability fallbacks.

## Experiment 2: Claude-native self-coordination

Question: Can a Claude Code lead agent enforce the same workflow using agent teams or subagents?

Method:

1. Build a fixture repository with one implementation task and one review task.
2. Give the lead agent a scoped worker and reviewer.
3. Require review, tests, and a structured handoff.
4. Inject one local setup failure and one real external dependency failure.
5. Check whether it classifies the two correctly and avoids unauthorized publication.

Acceptance evidence:

- complete transcript or event log;
- isolated diffs for each worker;
- test output;
- review findings and fixes;
- blocker classifications;
- no external write.

## Experiment 3: Claude Agent SDK controller

Question: Can a programmatic controller replace UI-based Claude coordination?

Method:

1. Start and resume a session through the Agent SDK.
2. attach hooks for permissions, validation, and audit events;
3. run a subagent and collect its result;
4. interrupt and steer the session;
5. verify what model and quota information is actually exposed.

Acceptance evidence:

- executable minimal controller;
- redacted event log;
- capability manifest;
- deterministic stop and resume;
- documented gaps for usage and model selection.

## Experiment 4: cross-harness conformance

Question: Which other harness can satisfy the same portable adapter contract?

Start with OpenHands or Jules because both expose documented session APIs. Run the same bounded fixture against:

1. Codex;
2. Claude Code or Agent SDK;
3. one external harness.

Score:

- start and steer;
- status and transcript;
- isolation;
- review and tests;
- stop and resume;
- permission boundary;
- model and quota facts;
- immutable provenance.

## Planned deliverables

- JSON Schema for the capability manifest.
- A transcript and evidence redaction policy.
- A conformance fixture repository.
- Codex-to-Claude adapter notes.
- Claude-native adapter prototype.
- One non-Claude adapter prototype.
- Versioned, non-hardcoded model-resolution policy.
