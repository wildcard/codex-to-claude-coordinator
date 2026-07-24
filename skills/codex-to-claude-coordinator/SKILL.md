---
name: codex-to-claude-coordinator
description: Coordinate Codex-to-Claude and cross-harness delegation from session selection through validated handoff. Use for Claude Code, Claude Desktop, Cowork, or background-agent work that needs a multi-agent coordinator to start, resume, steer, monitor, stop, review, test, resolve questions, or report blockers and completion evidence.
---

# Codex to Claude Coordinator

Coordinate Claude work as an evidence-driven lifecycle. Use the portable
`coordination-core` skill for classification and envelopes, then resolve its
requested capability tier through this Claude adapter. Keep the assigned scope
explicit and distinguish local implementation readiness from external approval
or release.

## Apply Policy Precedence

Use this order:

1. Follow an explicit model choice from the user.
2. Classify the delegated work with `coordination-core`.
3. Probe which Claude workers and model controls are actually available.
4. Inspect any current, explicitly labeled Claude usage indicators.
5. Resolve the requested capability tier with the policy below.
6. Follow repository, workspace, and session-specific rules.

Before session creation, record the probe time, availability facts, requested
tier, selected worker, and reasoning effort. Before a later steer, inspect the
session's actual worker and model. Do not imply that a steer changed them unless
the adapter proves that the running session supports that operation. Start a
replacement session only when the continuity cost and remaining work justify it.

## Select the Model

Treat model choice and reasoning effort as independent. Map the portable
requested tier to Claude as follows:

| Requested tier | Model selection |
| --- | --- |
| Routine | Use Sonnet 5 when selectable; otherwise use the available default. |
| Strong | Use Opus when selectable; otherwise use Sonnet 5 or the available default. |
| Max | Use Fable only when selectable and an explicit Fable consumed meter is below 25%. Otherwise use Opus when selectable, then Sonnet 5 or the available default. |

Apply a percentage threshold only when the surface explicitly labels the
percentage as consumed usage for the named model. Do not substitute context
usage, a shared plan or weekly window, token counts, remaining percentage, or an
unlabeled bar. No verified Opus-specific percentage currently exists in this
project, so the former Opus-below-50% rule is not enforceable and is not used.

If a model-specific usage display is unavailable, stale, or ambiguous, do not
infer that Fable satisfies a threshold. A visible shared plan limit is an
availability warning, not an Opus-specific percentage. Model entitlement,
organization policy, version, and data-retention mode are availability facts
independent of quota.

Map portable effort to the closest control the target surface supports. Record
the requested tier, requested effort, actual resolved worker/model or `unknown`,
and exact visible usage facts. Do not expose credentials or unrelated account
details.

## Inspect Before Delegating

Before starting or steering:

1. Read the applicable project and repository instructions.
2. Inspect existing Claude sessions and transcripts for the same task, scoped to the target project. Prefer `claude agents --cwd <project> --json` and `claude logs <session-id>` when the installed Claude Code version supports them.
3. Reuse a relevant active session when continuity matters.
4. Create a new session only for genuinely separate work.
5. Probe Claude availability, inspect any relevant labeled usage, and resolve
   tier plus effort.
6. Identify the exact objective, owned files or responsibility, required evidence, and external-action boundary.

Do not enumerate or read unrelated project transcripts. Do not transfer private material from one project into another. Give Claude only the context required for the delegated task.

Treat raw `claude logs` output as private. Even a generic task can render account
identity, organization labels, absolute paths, and terminal chrome. Keep raw
logs outside the repository and admit only reviewed redacted derivatives through
`coordination-conformance`.

## Start a Session

Provide a bounded assignment that includes:

- the concrete outcome and definition of done;
- the repository or workspace and the exact responsibility;
- applicable house rules and commands;
- known prior attempts and mistakes to avoid;
- required tests, demo, or live evidence;
- review requirements;
- permission boundaries for pushes, pull requests, messages, publication, and other external actions;
- a reminder that other agents may be working in the same codebase and their changes must not be reverted.

Ask Claude to report its initial understanding, chosen approach, and any immediate blocking dependency. Answer questions that can be resolved from available evidence instead of leaving the session idle.

## Steer an Existing Session

Before every steer, read the actual session model and any relevant availability
change. Keep the running worker unless switching is supported or replacement is
explicitly justified. Then:

1. Read the latest transcript and terminal state.
2. Verify claims against the working tree, tests, pull request, or service state.
3. Give one concise next action with the relevant evidence.
4. Resolve questions directly when the answer is available.
5. Redirect repeated, speculative, or out-of-scope work.
6. Stop quota burn when the session is looping without new evidence.

Local setup trouble, an unanswered agent question, or unfinished local work is not automatically a stakeholder blocker. Classify a blocker as external only after reproducing it and exhausting safe in-scope alternatives.

## Enforce Review and Validation

Before any authorized push:

1. Require Claude to run `/review` when that command is installed.
2. Require a self-review of the exact diff.
3. Use available pull-request review agents when a pull request exists.
4. Address critical, major, and substantive minor findings.
5. Run the repository's required tests and targeted integration checks.
6. Verify the exact commit that will be pushed.
7. Capture reproducible demo or live end-to-end evidence when the task requires
   it.

If `/review` is unavailable, fail closed: record the missing capability and require an independent exact-diff review through an available reviewer agent or equivalent review command before any authorized push. Do not describe an ordinary self-review as `/review`.

After a pull request opens, keep review follow-ups append-only unless the repository workflow explicitly permits rewriting history.

Do not equate passing local tests with external completion. Track these separately:

- implementation complete;
- local validation complete;
- live end-to-end validation complete;
- review complete;
- approval complete;
- release or publication complete.

## Handle External Actions

Treat pushes, pull requests, releases, stakeholder messages, issue updates, and publication as externally visible actions. Perform them only when the user or applicable workflow has authorized them.

Approval always terminates at the human or other explicitly authorized principal. A coordinator may route an approval request but may not grant it on the user's behalf merely because a child agent requested it. Treat an expired or unanswered approval as denied.

Before reporting a blocker externally:

1. Retry the relevant path with current inputs.
2. Confirm the failure is not caused by local configuration.
3. State the smallest reproducible symptom.
4. State what is already working.
5. Name the required owner or dependency.
6. Give the next action that can continue meanwhile.

## Produce the Handoff

For each session, report:

- task and session identity;
- requested tier and effort, actual worker/model, and selection evidence;
- current commit or working-tree state;
- implemented outcome;
- review results;
- tests and demo evidence;
- live end-to-end state;
- real external blocker, if any;
- precise next action and owner.

Keep the summary factual and concise. Mark unknown or unverified state explicitly.
