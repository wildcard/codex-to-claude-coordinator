# Local conformance experiments

This directory records privacy-safe observations for the protocols in
`docs/experiments-0-1.md`. It does not automate Claude, grant permissions, or
retain raw screenshots.

## Fixtures

- Use `fixtures/classification-read-only/` to test unchanged skill discovery,
  invocation, supporting files, permissions, and exact output before trying a
  lifecycle adapter.
- Use `fixtures/dispatch-read-only/` for Dispatch and session-lifecycle runs.
  Copy it to a disposable directory before a live run and permit writes only in
  that run's output directory.

## Redact evidence

Images require at least one opaque rectangle and a `.redacted` output name:

```sh
python3 skills/coordination-conformance/scripts/redact.py \
  /path/outside/repo/raw.png \
  experiments/runs/local-example/evidence/panel.redacted.png \
  --rect 0,0,400,80
```

Text files are rewritten with common account, home-path, and secret patterns
replaced:

```sh
python3 skills/coordination-conformance/scripts/redact.py \
  /path/outside/repo/raw.txt \
  experiments/runs/local-example/evidence/log.redacted.txt
```

Keep raw inputs outside this repository and delete them through the user's
normal secure workflow after verifying the derivative.

## Record and validate

Prepare an observation body as JSON, then append a record:

```sh
python3 skills/coordination-conformance/scripts/record.py \
  --run-dir experiments/runs/local-example \
  --run-id local-example \
  --experiment quota-signal-fidelity \
  --surface claude-desktop \
  --operation inspect_usage \
  --input-id quota-read-v1 \
  --observation observation.json \
  --evidence evidence/panel.redacted.png \
  --privacy-checked

python3 skills/coordination-conformance/scripts/validate.py \
  experiments/runs/local-example/observations.jsonl \
  --root experiments/runs/local-example
```

Generate a per-operation capability manifest without converting missing evidence
into support:

```sh
python3 skills/coordination-conformance/scripts/summarize.py \
  experiments/runs/local-example/observations.jsonl \
  --run-id local-example
```

`experiments/runs/` is ignored except for `.gitkeep`. Commit only synthetic test
fixtures and deliberately reviewed, redacted evidence.
