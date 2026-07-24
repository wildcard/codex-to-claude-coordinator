# Research roadmap

Status: active
Last checked: 2026-07-23

## Experiment 0: Claude Dispatch discovery

Implementation protocol: [Experiment 0 and 1 protocols](experiments-0-1.md#experiment-0-dispatch-behavior).

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

Implementation protocol: [Experiment 0 and 1 protocols](experiments-0-1.md#experiment-1-quota-signal-fidelity).

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

## Experiment 4: inverse Claude-to-Codex coordination

Question: Can Claude Code coordinate Codex through OpenAI's official plugin
while preserving the portable lifecycle and evidence boundaries?

Method:

1. Install and probe `codex@openai-codex` without enabling the stop-review gate.
2. Run one fresh read-only task and verify the result against the repository.
3. Run one background task through status, result, and cancel.
4. Resume a completed task with one delta instruction.
5. Record requested model and effort separately from the actual resolved model.
6. Test transcript transfer only with an explicit privacy-approved synthetic
   Claude session.

Acceptance evidence:

- privacy-safe prerequisite report;
- fresh and resumed Codex thread identifiers;
- background state transitions and deterministic cancellation;
- exact working-tree and test evidence;
- explicit `unknown` for any model or quota fact the runtime does not expose;
- no cross-project transcript or unauthorized external action.

The first read-only fresh-task probe passes. Background lifecycle, resume,
cancel, and synthetic transfer remain to be recorded through
`coordination-conformance`.

## Experiment 5: cross-harness conformance

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

Use `experiments/fixtures/classification-read-only/` as the first zero-write
runtime check before granting a harness access to the implementation fixture.
Record skill listing, explicit load, implicit match, support-file access,
permission behavior, and output equality as separate observations.

The first goose run exposed a meaningful distinction: the interactive
`/skills` path loaded the portable skill, while a headless natural-language run
misrouted to `summon.load`. A future goose adapter should use the documented
skills surface explicitly and must not switch to autonomous permission mode
outside a disposable sandbox.

## Planned deliverables

- JSON Schema for the capability manifest. **Implemented locally.**
- A transcript and evidence redaction policy. **Implemented locally.**
- A conformance fixture repository. **Implemented locally.**
- Codex-to-Claude adapter notes.
- Claude-to-Codex official-plugin adapter. **Implemented locally.**
- Claude-native adapter prototype.
- One non-Claude adapter prototype.
- Versioned, non-hardcoded model-resolution policy.

## Four-week implementation cadence

### Week 1: portable contract

- stabilize the six-axis classifier;
- stabilize the append-only envelope schema and validator;
- add negative tests for scope escape, coordinator-authored approval, inferred
  worker identity, and archive-as-stop;
- keep the portable skill free of vendor names and commands.

Exit criterion: both plugin manifests and all three skills validate, and the
portable unit suite is green.

### Week 2: evidence recorder and model resolver

- implement the redacted Experiment 0/1 recorder;
- run quota-signal fidelity without consequential actions;
- encode Claude model aliases and availability probes in an adapter reference;
- keep threshold automation disabled unless Experiment 1 passes.

Exit criterion: one privacy-checked local evidence bundle and a deterministic
availability fallback.

### Week 3: Claude adapters

- implement the smallest Claude Code headless or Agent SDK controller;
- validate the official Claude-to-Codex app-server adapter;
- run the Dispatch behavior protocol;
- map official and observed lifecycle states to the portable ledger;
- verify stop, resume, approval routing, and actual-worker provenance.

Exit criterion: one Claude Code run and one Dispatch run validate against the
same envelope protocol.

### Week 4: bake-off and distribution rehearsal

- run one fixed fixture through Codex-to-Claude, Claude-native-to-Claude, and one
  non-Claude adapter;
- compare completion accuracy, human approvals, steers, wall time, and escaped
  defects;
- test local installation in Codex and Claude without publishing;
- prepare, but do not submit, skills.sh and Claude marketplace release assets.

Exit criterion: a versioned evidence report identifies the default pairing and
the next adapter on measured behavior, not product claims.

## Next bake-offs

1. **Codex to Claude Code versus Dispatch to Claude Code.** Same fixture,
   acceptance tests, permissions, and evidence ledger.
2. **Codex to Jules or OpenHands.** Tests whether the portable protocol survives
   outside the Claude family.
3. **Cursor to Codex or Claude.** Defer until coordinator and worker roles can be
   configured independently without changing the core schema.

## Current progress

- Week 1 exit criterion is met locally.
- The Week 2 recorder, redactor, schema, and capability summarizer are
  implemented.
- Claude Code plugin discovery and the scoped start/list/read/stop lifecycle were
  reproduced on version 2.1.216.
- Codex explicit and implicit runtime invocation passed the portable
  classification fixture; explicit interactive goose invocation also passed.
- The official Claude-to-Codex plugin is installed and its fresh read-only
  rescue path passes; the privacy-safe adapter and prerequisite probe are
  implemented locally.
- Quota fidelity, live Dispatch behavior, steering, review collection, and
  change collection remain untested. The reverse adapter's background,
  resume/cancel, and synthetic transfer cases also remain to be recorded.
  Headless implicit goose invocation remains unproven.
- The next bounded run is Experiment 1 `T0` capture, followed by the same
  background fixture with one follow-up steer.
