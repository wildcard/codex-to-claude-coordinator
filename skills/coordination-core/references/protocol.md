# Coordination envelope protocol

## Transport

Use an append-only JSON Lines stream. Every record carries:

- `schema_version`;
- globally unique `event_id`;
- stable `task_id`;
- monotonically increasing `seq`;
- RFC 3339 `emitted_at`;
- `emitter`: `coordinator`, `worker`, or `human`;
- `type`;
- type-specific `body`.

## Envelope types

| Type | Emitter | Purpose |
| --- | --- | --- |
| `assignment` | coordinator | Outcome, definition of done, scope, evidence, permissions, requested tier, and effort |
| `state` | worker | Lifecycle state, six-field completion ledger, session reference, and actual worker |
| `question` | worker | One steering question, recommended default, and blocking flag |
| `steer` | coordinator | Exactly one next action with evidence and target paths |
| `approval_request` | worker | Consequential action requiring human authority |
| `approval_decision` | human | Explicit approval or denial; never coordinator-authored |
| `evidence` | worker | Artifact, change, test, review, transcript, or live result reference |
| `review` | coordinator | Independent review request over an exact change reference |
| `stop` | coordinator | Graceful or cancelling stop request |
| `handoff` | worker | Terminal provenance, ledger, review, blocker, and next action |

## Invariants

- Sequence numbers strictly increase within one task stream.
- A steer target must remain inside the assignment scope.
- Only a human emits an approval decision.
- A stop closes only through a terminal worker state.
- A handoff records the actual worker or `unknown`.
- Evidence classes distinguish immutable, observed, rendered, and unavailable
  sources.
- Completion fields do not imply one another.
