# Architecture: portable coordinator with harness adapters

Status: initial design
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

The current Fable, Opus, and Sonnet thresholds belong to the user-policy layer. The portable core should express capability tiers such as `simple`, `tricky`, and `complex`, while the Claude adapter resolves those tiers to currently available model names.

## Evidence model

Every claim should carry one of:

- `official-doc`: supported by a linked first-party source;
- `observed`: reproduced in a dated local experiment;
- `advisor`: proposed by an agent and awaiting independent verification;
- `inference`: reasoned from evidence but not directly documented;
- `unknown`: not yet verified.

This prevents an agent's fluent recommendation from silently becoming product truth.

## Initial conclusion

Claude can coordinate internal Claude Code work through subagents, agent teams, hooks, background agents, and the Agent SDK. That does not yet prove it can replace an outer coordinator that inventories desktop sessions, reads account quota, changes models, validates cross-harness state, and controls external-action approvals. The architecture therefore supports Claude-native coordination as an adapter and experiment, not as an assumed replacement.
