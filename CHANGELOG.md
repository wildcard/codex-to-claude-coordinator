# Changelog

All notable changes to the public coordination package are recorded here.

## Unreleased

- Split the vendor-neutral coordination lifecycle from the Codex-to-Claude
  adapter.
- Add deterministic task classification, lifecycle envelopes, schemas, and
  validators.
- Add a privacy-safe conformance kit for harness and usage-signal experiments.
- Package the three skills for Codex, Claude Code, the `skills` CLI, and other
  Agent Skills-compatible harnesses.
- Add Experiment 0 and Experiment 1 protocols, launch verification, isolated
  install checks, and continuous integration.
- Make the version `0.1` classifier contract self-contained for instruction-only
  harnesses while retaining its reference, schema, and executable validator.
- Replace inferred per-model quota percentages with explicit availability and
  labeled-signal evidence.
- Align Codex starter prompts with the plugin manifest contract, strengthen
  cross-harness discovery keywords, and refresh the Pillow redaction dependency
  while retaining Python 3.9 compatibility.
- Harden synthetic evidence provenance, decimal percentage validation, blocker
  fields, UTF-8 package checks, link parsing, and timestamp-based summaries.
- Document the reproducible namespaced Claude plugin invocation separately from
  nondeterministic plain-English activation.
