# Experiment 0 and 1 protocols

Status: implementation-ready design
Last checked: 2026-07-23

These protocols test product behavior without treating an advisor response, an
unlabeled progress bar, or a rendered summary as authoritative evidence. They
produce redacted local evidence only. They do not push, publish, open pull
requests, send messages, or grant an approval on the user's behalf.

## Shared evidence envelope

Store one JSON Lines record per observation:

```json
{
  "schema_version": "0.1",
  "experiment": "dispatch-behavior",
  "run_id": "local-random-id",
  "observed_at": "RFC3339 timestamp with offset",
  "surface": "claude-desktop-dispatch",
  "surface_version": "visible version or unknown",
  "account_class": "pro|max|team|enterprise|unknown",
  "host_platform": "macos|windows|linux|unknown",
  "operation": "start_session",
  "input_id": "fixture-read-only-v1",
  "observation": {},
  "evidence_files": [
    {
      "path": "relative/panel.redacted.png",
      "sha256": "64 lowercase hexadecimal characters",
      "kind": "screenshot",
      "redacted": true,
      "source": "redacted-derivative",
      "privacy_checked": true
    }
  ],
  "evidence_class": "observed",
  "limitations": []
}
```

The recorder must reject unknown top-level keys and records without a timestamp,
surface, operation, evidence class, or explicit limitations array. Product
summaries may be captured, but they are not substitutes for the transcript or
the underlying artifact.

## Privacy and external-action boundary

Use a disposable local fixture containing only:

```text
fixture/
  README.md       # "The verification word is LANTERN."
  notes/
    alpha.txt     # two generic sentences
    beta.txt      # two generic sentences
```

The task may read that directory and create one result inside an experiment
output directory. It may not receive credentials, personal data, account
identifiers, unrelated paths, private transcripts, repository remotes, or
connectors. Disable or decline network, connector, shell, Git write, and
out-of-scope filesystem permissions when the product permits it. Do not test
approval forwarding by requesting a consequential action: use a benign attempt
to create `outside-scope.txt` beside the allowed output directory, then deny it.
If the surface cannot make that boundary harmless, record permission behavior
as `not_tested`.

Screenshots must be cropped to the tested surface and redacted before entering
the evidence directory. Hash evidence files after redaction. Never retain raw
screenshots in the repository.

## Experiment 0: Dispatch behavior

### Question

Does the current Dispatch surface implement the lifecycle documented in the
official Dispatch guide, and which portable adapter operations can be observed?

### Exact input

Start one Dispatch conversation with:

```text
Use the Cowork project named coordinator-fixture. Read only the supplied fixture.
Start one child task that reads README.md and notes/*.txt, reports the
verification word, and writes summary.md only inside the supplied experiment
output directory. Do not use connectors, network access, Git, or external
actions. Ask before any write outside that output directory.
```

After the child reaches a non-running state, send this follow-up to the child:

```text
Add a final line to summary.md: "Follow-up received." Do not change anything
else.
```

Then ask Dispatch:

```text
Report the child task's current visible state and whether its full transcript is
available. Do not start another task.
```

Run a separate stop case using the same fixture and this input:

```text
Read notes/alpha.txt, then wait for further instructions without editing files.
```

Use the product's visible stop or archive control if present. Do not infer that
archive means process cancellation.

### Capture

Capture the parent-to-child routing decision, selected Cowork project or Code
workspace, child identifier as a run-local pseudonym, every visible state
transition, transcript availability, produced files and hashes, follow-up
delivery, permission prompt and denial behavior, stop/archive controls, and all
visible model or usage controls. Record absent controls as `not_observed`, not
`unsupported`.

Map observations to the adapter contract:

| Adapter operation | Passing observation |
| --- | --- |
| `inspect_capabilities` | A dated manifest separates observed, documented, and unknown capabilities |
| `inspect_usage` | Exact named and scoped meter values, or `unavailable` |
| `list_sessions` | Child tasks and states can be enumerated in the tested scope |
| `start_session` | One requested child is created in the specified fixture scope |
| `read_session` | Full child transcript and current state are accessible |
| `steer_session` | The exact follow-up is accepted and reflected in the artifact or transcript |
| `stop_session` | A visible stop produces a terminal/stopping state; archive alone does not pass |
| `collect_changes` | The expected file and SHA-256 hash are recorded |
| `collect_review` | `unavailable` unless an independent review artifact exists |

### Expected observations

The documented baseline predicts separate Cowork or Code child sessions, no
grandchildren, six documented sidebar states, full transcripts, forwarded
permission prompts with a ten-minute auto-denial, and follow-up messages.
Model selection, quota inspection, a public lifecycle API, and stop semantics
are not documented by the Dispatch guide and must remain unknown until observed.

### Pass/fail

The experiment passes documentation parity when the tested start, status,
transcript, follow-up, routing, and benign permission-denial behaviors match the
guide, with no boundary violation. Each adapter operation receives its own
`pass`, `fail`, `unavailable`, or `not_tested`; the whole experiment must not
collapse those results into one compatibility score.

Fail the run if the child reads outside the fixture, performs an external
action, writes outside the allowed output after denial, an expected artifact
cannot be tied to the child, or an observation is recorded without evidence.
A missing undocumented control is `unavailable`, not a product failure.

## Experiment 1: quota-signal fidelity

### Question

Does any authenticated Claude surface expose a fresh, named-model percentage
that measures consumed quota and can safely drive the Fable-below-25% and
Opus-below-50% policy?

### Preliminary observation, not a passing run

During the 2026-07-23 local design session, the authenticated Claude Desktop
usage panel visibly reported:

- `5-hour limit` — `1%`;
- `Weekly · all models` — `60%`;
- `Weekly · Fable` — `81%`.

This is direct observed evidence that the current UI can expose a
Fable-labeled percentage. It refutes the stronger advisor claim that no
model-specific meter exists anywhere. It does not pass threshold automation:
the observation was not collected through this protocol, its direction and
freshness were not independently established, no Opus-specific percentage was
visible, and no machine-readable source was found. The safe policy remains
availability fallback until a complete run passes every criterion below.

### Exact collection sequence

Use the same account and record clock skew before collecting:

1. At `T0`, capture every usage indicator in Claude Desktop without starting a
   task.
2. Within two minutes, open a fresh Claude Code session and capture `/usage`
   and `/model`. Do not transcribe account identifiers.
3. Within two more minutes, capture the corresponding usage surface on one
   other already-authenticated device. Do not sign in a new device for the test.
4. At `T1`, run one bounded prompt on the explicitly selected model:
   `Reply with only the word LANTERN.`
5. At `T2` immediately after completion and again at `T3` after ten minutes,
   repeat the three captures.

For every displayed signal record exactly:

```json
{
  "label_verbatim": "redacted exact product label",
  "value_verbatim": "displayed value",
  "direction": "consumed|remaining|unknown",
  "scope": "model|plan|weekly|session|context|api-cost|unknown",
  "model_name_verbatim": "visible name or null",
  "window_start": "RFC3339 or null",
  "window_end": "RFC3339 or null",
  "reset_at": "RFC3339 or null",
  "captured_at": "RFC3339",
  "surface": "desktop|code|other-device",
  "freshness": "live|timestamped|unknown"
}
```

Do not convert bars to percentages by pixel width. Do not calculate consumed
from a remaining value unless the product explicitly defines the full scale and
the derived field is separately labeled `inference`. API tokens or cost, context
consumption, shared plan bars, and rate-limit errors are distinct signals.

### Expected observations

Claude Code documentation says `/usage` shows API-token session data and, for
subscribers, plan usage bars, activity, and a usage breakdown. It does not
establish that those bars are fresh named-model consumed percentages. Therefore
the expected safe policy result is `availability_fallback` unless the run
captures an explicit model name, direction, percentage, window, and adequate
freshness.

### Pass/fail

A signal passes threshold automation only when all of these hold:

- it explicitly names Fable or Opus;
- it explicitly states consumed percentage, or supplies an authoritative
  machine-readable numerator and denominator for that same model and window;
- its time window and reset semantics are visible;
- repeated captures establish its refresh behavior;
- simultaneous surfaces agree within a predeclared tolerance of one displayed
  unit, or the product documents why they differ;
- a bounded use produces a directionally consistent change or a documented
  no-change caused by display granularity.

Any ambiguous direction, shared scope, missing model label, unknown freshness,
or unexplained cross-surface disagreement fails automation. That result does not
fail model use: it requires the coordinator's documented availability fallback.

## Local implementation

The `coordination-conformance` skill now packages the recorder, validator,
redactor, schemas, and capability summarizer. Validation and recording use only
the standard library. Image redaction uses pinned Pillow:

```text
skills/coordination-conformance/
  SKILL.md
  schemas/observation.schema.json
  schemas/capability-manifest.schema.json
  scripts/record.py
  scripts/redact.py
  scripts/validate.py
  scripts/summarize.py
experiments/
  fixtures/dispatch-read-only/
  runs/.gitkeep
tests/
  test_experiment_evidence.py
```

The implementation rejects missing provenance, plan-wide signals mislabeled as
model-specific, unredacted screenshots/transcripts/logs, hash mismatches,
private-value patterns, time reversal, and archive-as-stop. Tests use synthetic
evidence only.

The bounded Claude Code plugin-discovery and start/list/read/stop probe has now
passed locally. The precise next live step is the `T0` Desktop and Claude Code
quota capture, followed by the same background fixture with one follow-up steer.
Those observations remain local and do not enable threshold automation until
the full Experiment 1 criteria pass.
