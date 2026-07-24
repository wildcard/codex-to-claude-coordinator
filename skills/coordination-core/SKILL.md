---
name: coordination-core
description: Orchestrate multi-agent work with portable task classification and evidence-driven lifecycle envelopes. Use when any coordinator or worker harness must assign, delegate, steer, supervise, stop, review, or hand off work without assuming a particular model, command, session UI, quota meter, or vendor.
---

# Coordination Core

Coordinate delegated work through a portable contract. Keep product commands,
model names, permission controls, and status strings in harness adapters.

## Classify Before Starting

1. Collect only observable inputs defined below and in
   [references/classification.md](references/classification.md).
2. Run `scripts/classify.py` with those inputs when tool access exists. In an
   instruction-only surface, apply the same rules below verbatim.
3. Treat difficulty, risk, duration, coordination shape, requested capability
   tier, and reasoning effort as independent outputs.
4. Ask the selected adapter to resolve the requested tier against capabilities
   it can prove. Record `unavailable` or `unknown`; never infer availability from
   an unlabeled or shared usage percentage.
5. Reclassify only when a mechanical input changes. Do not relabel work merely
   because an agent sounds confident or uncertain.

Use the version `0.1` rules exactly:

- `difficulty`: `hard` if work crosses systems or a prior attempt failed;
  otherwise `trivial` for at most one file group; otherwise `standard`.
- `risk`: `high` for an irreversible or external action; otherwise `elevated`
  when a plan gate is required; otherwise `low`.
- `duration`: map `small`, `medium`, or `large` expected tool calls to `short`,
  `medium`, or `long`.
- `coordination`: `team` for at least two independent subtasks that cross
  systems; otherwise `fan_out` for at least two; otherwise `single`.
- `requested_tier`: `max` for hard and long; otherwise `strong` for hard or
  elevated/high risk; otherwise `routine`.
- `reasoning_effort`: `high` for hard difficulty or high risk; `low` for
  trivial and low risk; otherwise `medium`.

Emit exactly those six field names and declared values. Do not invent synonyms
such as `low` difficulty, `coordination_shape`, or
`requested_capability_tier`. If neither the rules nor the helper are available,
report that classification is blocked instead of fabricating a result.

## Coordinate Through Envelopes

Read [references/protocol.md](references/protocol.md), then emit append-only
JSON Lines records conforming to `schemas/envelope.schema.json`.

- Start with one `assignment`.
- Accept worker `state`, `question`, `approval_request`, `evidence`, and
  `handoff` records.
- Send one concrete next action per `steer`.
- Route approval requests to a human. Only a human may emit
  `approval_decision`; a timeout is a denial.
- Request independent exact-change review with `review`.
- Close a requested stop only after a terminal worker `state`; archive or idle
  is not stop evidence.
- Verify evidence against the referenced artifact, diff, test output, or live
  system. Do not use an agent summary as proof.

Run `scripts/validate_envelope.py <events.jsonl>` before trusting a stream.

## Track Completion Separately

Maintain these ledger fields independently:

- implementation;
- local validation;
- live end-to-end validation;
- review;
- approval;
- release.

Use `pending`, `in_progress`, `done`, `blocked`, or `not_applicable`. Local
tests never imply live validation, approval, or release.

## Preserve Boundaries

- Scope reads and writes to the assignment.
- Keep events append-only and monotonically sequenced.
- Record the actual resolved worker identity or `unknown`, not merely the
  requested tier.
- Require a human decision for external actions.
- Mark unsupported adapter capabilities `unavailable`.
- Keep vendor policy in adapters so the core remains portable.
