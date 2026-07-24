# Claude advisory: coordinator architecture

Date: 2026-07-23

Session: `Codex coordinator architecture assessment`

Scope: only this repository

Role: read-only architecture and product advisor

Model: Opus 4.8, medium effort
Usage basis: Fable's visible consumed meter was 75%, so Fable was ineligible; Opus was available. The visible `plan 81%` signal was not treated as an Opus-specific percentage.

## Independently accepted findings

- Dispatch is an official Cowork coordinator. It creates child Cowork or Code sessions, exposes per-task status and transcripts, forwards approvals, and permits follow-ups.
- Dispatch child tasks do not create further Dispatch children.
- Claude Code agent view exposes project-scoped session listing, status, logs, steering, stop, respawn, worktree behavior, model, effort, and permission defaults.
- Claude Code `/usage` includes approximate local-history figures and may show a cached plan-limit snapshot when rate limited. Shared subscription windows are not a substitute for a named model-specific meter.
- The portable artifact should own assignment, evidence, review, blocker, approval, and handoff semantics. Product commands, model aliases, transcript locations, and state strings belong in adapters.
- Approval must terminate at the human or another explicitly authorized principal.

## Advice retained as hypotheses

- Dispatch may cover most of the workflow for single-repository, Claude-only work.
- Keeping Codex outside Claude can provide useful review independence.
- A cross-harness conformance test will reveal more than prose comparisons.

These hypotheses need experiments before they become project claims.

## Changes influenced by the advisory session

- Confirmed Dispatch in the harness landscape.
- Added quota-signal fidelity as the first experiment.
- Tightened the skill so context and shared plan percentages cannot masquerade as per-model quota.
- Bound session inspection to the target project.
- Made `/review` capability-aware while retaining an independent-review gate.
- Added the invariant that coordinators route approvals but do not grant them.

## Primary sources rechecked independently

- [Dispatch guide](https://claude.com/docs/cowork/guide/dispatch)
- [Claude Code agent view](https://code.claude.com/docs/en/agent-view)
- [Claude Code costs and usage](https://code.claude.com/docs/en/costs)
- [Claude Code model configuration](https://code.claude.com/docs/en/model-config)
