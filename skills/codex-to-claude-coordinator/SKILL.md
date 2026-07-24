---
name: codex-to-claude-coordinator
description: Coordinate Claude Desktop and Claude Code delegation from session selection through validated handoff. Use whenever starting, resuming, steering, monitoring, or auditing Claude work; choosing a Claude model from visible quota usage; reviewing transcripts; resolving agent questions; enforcing review and test gates; or reporting blockers and completion evidence.
---

# Codex to Claude Coordinator

Coordinate Claude work as an evidence-driven lifecycle. Recheck model usage before every new session and every steer, keep the assigned scope explicit, and distinguish local implementation readiness from external approval or release.

## Apply Policy Precedence

Use this order:

1. Follow an explicit model choice from the user.
2. Inspect the current visible Claude model-usage indicators.
3. Classify the delegated work as simple, tricky, or complex.
4. Select the model with the policy below.
5. Follow repository, workspace, and session-specific rules.

Never reuse a stale quota reading for a later start or steer. Inspect again immediately before acting. If the current Claude session cannot change models after it starts, record that constraint and either continue with the current model or start a replacement session; never claim that a steer changed an immutable session model.

## Select the Model

Interpret each threshold as the percentage of quota already consumed, not the percentage remaining. Apply a model threshold only when the visible surface explicitly labels that percentage for the named model. Do not substitute context usage, a shared plan or weekly window, token counts, or an unlabeled progress bar.

| Work class | Model selection |
| --- | --- |
| Simple | Use Sonnet 5. |
| Tricky | Default to Opus. Use Sonnet 5 if Opus is unavailable or its consumed usage is 50% or higher. Do not use Fable for merely tricky work. |
| Complex | Use Fable only when it is available and its consumed usage is below 25%. Otherwise use Opus when it is available and its consumed usage is below 50%. Otherwise use Sonnet 5. |

Treat work as:

- Simple when it is bounded, low-risk, easily verified, and needs little architectural judgment.
- Tricky when it crosses files or systems, requires debugging or careful judgment, or has meaningful review risk.
- Complex when it requires substantial architecture, research synthesis, ambiguous tradeoffs, or coordinated multi-stage execution.

If the model-specific usage display is unavailable, stale, or ambiguous, do not infer that Fable is eligible. Use Opus for tricky or complex work when Opus availability is clear; otherwise use Sonnet 5. Treat a visible shared plan limit as an availability warning, not as Opus's model-specific consumed percentage.

Record the selected model, work class, and the visible usage facts in the coordination notes. Do not expose credentials or unrelated account details.

## Inspect Before Delegating

Before starting or steering:

1. Read the applicable project and repository instructions.
2. Inspect existing Claude sessions and transcripts for the same task, scoped to the target project. Prefer `claude agents --cwd <project> --json` and `claude logs <session-id>` when the installed Claude Code version supports them.
3. Reuse a relevant active session when continuity matters.
4. Create a new session only for genuinely separate work.
5. Inspect current Claude usage and apply the model policy.
6. Identify the exact objective, owned files or responsibility, required evidence, and external-action boundary.

Do not enumerate or read unrelated project transcripts. Do not transfer private material from one project into another. Give Claude only the context required for the delegated task.

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

Before every steer, inspect current usage again and select the eligible model. Then:

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
7. Capture reproducible demo or live end-to-end evidence when the task requires it.

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
- selected model, work class, and quota basis;
- current commit or working-tree state;
- implemented outcome;
- review results;
- tests and demo evidence;
- live end-to-end state;
- real external blocker, if any;
- precise next action and owner.

Keep the summary factual and concise. Mark unknown or unverified state explicitly.
