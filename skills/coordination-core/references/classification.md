# Classification reference

## Inputs

| Input | Type | Meaning |
| --- | --- | --- |
| `files_in_scope` | non-negative integer | Number of explicitly owned files or path groups |
| `crosses_systems` | boolean | More than one package, service, product, or execution boundary |
| `prior_attempt_failed` | boolean | A relevant attempt failed with current inputs |
| `plan_required` | boolean | The coordinator requires a plan gate before edits |
| `external_actions_requested` | string array | Requested pushes, publications, messages, releases, or comparable actions |
| `reversible` | boolean | Every requested write is locally recoverable |
| `expected_tool_calls` | `small`, `medium`, or `large` | Pre-start estimate bucket |
| `independent_subtasks` | non-negative integer | Non-overlapping work partitions |

## Rules

| Axis | Values | Mechanical rule |
| --- | --- | --- |
| Difficulty | `trivial`, `standard`, `hard` | `hard` if work crosses systems or a prior attempt failed; `trivial` if at most one file group and neither condition holds; otherwise `standard` |
| Risk | `low`, `elevated`, `high` | `high` for any irreversible or external action; otherwise `elevated` when a plan gate is required; otherwise `low` |
| Duration | `short`, `medium`, `long` | Map directly from the tool-call estimate |
| Coordination | `single`, `fan_out`, `team` | `team` for at least two independent subtasks crossing systems; otherwise `fan_out` for at least two; otherwise `single` |
| Requested tier | `routine`, `strong`, `max` | `max` for hard and long; otherwise `strong` for hard or elevated/high risk; otherwise `routine` |
| Effort | `low`, `medium`, `high` | `high` for hard difficulty or high risk; `low` for trivial/low; otherwise `medium` |

The requested tier describes capability intent. The adapter resolves it to a
currently available worker. Reasoning effort is not a synonym for tier: axes
can diverge, and an adapter must preserve both outputs instead of deriving one
from the other.
