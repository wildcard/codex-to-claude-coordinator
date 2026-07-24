# Architecture: portable coordinator with harness adapters

Status: portable core 0.1 implemented; bidirectional adapters remain experimental
Last checked: 2026-07-23

## Goal

Separate the coordination policy from any one agent product. Codex remains the first outer coordinator and Claude remains the first delegated harness, but the same evidence and safety gates should be testable against other systems.

## Portable core

The portable core should own:

- task classification and model-tier intent;
- session lifecycle state;
- scope, ownership, and external-action boundaries;
- evidence requirements;
- review and test gates;
- blocker classification;
- final handoff schema;
- audit events and provenance.

It should not assume that a provider exposes model quota, worktrees, pull requests, transcripts, or permission controls.

## Adapter contract

Each harness adapter should declare its supported capabilities and implement only the operations it can prove.

```text
inspect_capabilities() -> capability manifest
inspect_usage() -> observed usage facts | unavailable
list_sessions(scope) -> session summaries
start_session(task, scope, model_intent, permissions) -> session reference
read_session(session_ref, cursor?) -> events and status
steer_session(session_ref, instruction) -> accepted event
stop_session(session_ref) -> terminal or stopping state
collect_changes(session_ref) -> commit, diff, or artifact references
collect_review(session_ref) -> review evidence
```

Capabilities should include:

- session creation;
- follow-up steering;
- status and transcript retrieval;
- model selection;
- quota visibility;
- isolated workspace or worktree;
- permission and external-action controls;
- review hooks or agents;
- test execution;
- stop or cancel;
- resumability;
- artifact and commit provenance.

Unsupported capabilities must return `unavailable`, not a guessed value.

## Policy layers

1. **User policy:** explicit preferences and overrides, including quota thresholds.
2. **Portable workflow:** task scope, evidence, reviews, blockers, and handoff.
3. **Harness adapter:** product-specific UI, API, CLI, and permission behavior.
4. **Project policy:** repository instructions and validation commands.

The current Fable, Opus, and Sonnet resolution belongs to the user-policy and
Claude-adapter layers. The portable core emits `routine`, `strong`, or `max`
capability intent plus a separate `low`, `medium`, or `high` reasoning effort.
An adapter resolves both against controls it can prove.

## Protocol boundary

The portable transport is an append-only JSON Lines stream. A coordinator and
worker do not need a bidirectional product integration; they need a shared,
scoped channel that can carry:

- assignment and worker state;
- one blocking question and one concrete steer;
- approval request and human-authored decision;
- evidence and exact-change review;
- stop request followed by a terminal state;
- final handoff with actual worker provenance.

This supports file-drop, standard input/output, a local socket, an SDK event
stream, or a product API without changing lifecycle semantics. The transport
must never manufacture an approval decision or treat archive, idle, or a
rendered summary as terminal proof.

## Plugin projections

The repository keeps one source skill tree and thin harness packaging:

```text
.claude-plugin/       # Claude Code plugin and marketplace metadata
.codex-plugin/        # Codex plugin metadata
skills/
  coordination-core/  # portable classifier, schemas, protocol, validators
  coordination-conformance/
                       # evidence recorder, redactor, capability manifest
  codex-to-claude-coordinator/
                       # Claude-specific adapter policy
  claude-to-codex-coordinator/
                       # official codex-plugin-cc adapter policy and probe
```

Agent Skills-compatible harnesses should consume the portable skill unchanged
where possible. Product commands, status names, transcript locations, model
aliases, and usage meters belong in an adapter reference or script. A new
adapter should declare a capability manifest and pass the same protocol tests
before gaining convenience commands or UI automation.

The intended expansion order is:

1. Codex coordinator to Claude Code worker;
2. Claude Code coordinator to Codex through OpenAI's official
   `codex-plugin-cc`;
3. Claude Dispatch and Claude Code-native coordinators to Claude Code workers;
4. Claude Agent SDK as a programmatic adapter;
5. Codex to Jules or OpenHands as the first non-Claude worker;
6. Cursor as coordinator or worker after the portable contract is stable.

The reverse adapter demonstrates why the core and transport must stay separate.
OpenAI's plugin provides a thin Claude forwarding agent, a deterministic Node
runtime, a shared Codex app-server broker, repository-scoped job state, and
native Codex threads. This project does not reimplement that transport. It adds
classification, scope, permission, evidence, review, and handoff policy around
the officially maintained runtime.

## Evidence model

Every claim should carry one of:

- `official-doc`: supported by a linked first-party source;
- `observed`: reproduced in a dated local experiment;
- `advisor`: proposed by an agent and awaiting independent verification;
- `inference`: reasoned from evidence but not directly documented;
- `unknown`: not yet verified.

This prevents an agent's fluent recommendation from silently becoming product truth.

## Initial conclusion

Claude can coordinate internal Claude Code work through subagents, agent teams,
hooks, background agents, Dispatch, and the Agent SDK. That does not prove it
can replace a cross-harness coordinator that normalizes sessions, evidence,
model controls, and human approval across products. Claude-native coordination
is therefore a first-class adapter and experiment, not an assumed replacement.
