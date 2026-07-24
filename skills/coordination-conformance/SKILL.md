---
name: coordination-conformance
description: Test and compare agent-harness coordination capabilities with privacy-safe evidence. Use to record, redact, validate, and summarize whether Codex, Claude, Cursor, Copilot, Goose, OpenHands, or another coordinator or worker can start, steer, inspect, stop, review, preserve scope, expose usage, or produce a trustworthy handoff.
---

# Coordination Conformance

Test harness capabilities through local, privacy-safe evidence. Read
[references/evidence-policy.md](references/evidence-policy.md) before collecting
authenticated product observations.

## Prepare the Run

1. Define one falsifiable capability question and exact harmless input.
2. Use a disposable fixture with no credentials, personal data, remotes,
   connectors, or unrelated transcripts.
3. Create a run directory outside the installed skill. Keep raw captures outside
   the repository.
4. Record unsupported, unobserved, and untested behavior distinctly.

## Redact and Record

Run `scripts/redact.py` before admitting screenshots, transcripts, or logs.
Image evidence requires an opaque rectangle and a `.redacted` derivative.
Image redaction requires Python 3.9 or newer and the dependency in
`requirements.txt`; text redaction, recording, validation, and summarization use
only the Python standard library.

Build an observation body as JSON, then use `scripts/record.py` to append it.
The recorder hashes evidence, rejects raw screenshots, scans text for common
identifiers and secret patterns, and keeps timestamps append-only. Pass
`--privacy-checked` only after manually inspecting every derivative; the recorder
does not infer that review. Use `--evidence-source synthetic` for harmless
generated fixture artifacts; redacted evidence is always recorded as a
`redacted-derivative`.

## Validate and Summarize

Run:

```sh
scripts/validate.py <observations.jsonl> --root <run-directory>
scripts/summarize.py <observations.jsonl> --run-id <run-id> --root <run-directory>
```

Trust a capability only when its operation has a passing observation and
traceable evidence. The summarizer preserves missing operations as `unknown`;
it never converts absence into `unavailable` or support.

For quota-like signals, set `threshold_eligible` only when the value has explicit
model scope, consumed direction, a percentage, reset or window semantics, and
known freshness. For stop behavior, archive or idle never passes without a
terminal worker state.

## Preserve the Boundary

- Do not automate consequential approval prompts.
- Do not retain raw screenshots in the repository.
- Do not accept absolute or traversing evidence paths.
- Do not record account identifiers or machine-specific home paths.
- Do not collapse per-operation results into one compatibility score.
- Keep vendor-specific inputs and expected states in the experiment plan, not
  in this skill's reusable policy.
