---
name: claude-to-codex-coordinator
description: Coordinate Claude Code-to-Codex delegation through OpenAI's official codex-plugin-cc runtime. Use when Claude should ask Codex to review, investigate, implement, resume, transfer a Claude session, run in the background, report status or results, or cancel work while preserving scope, permissions, model intent, and evidence.
---

# Claude to Codex Coordinator

Use `coordination-core` for classification and lifecycle envelopes, then map
the result to OpenAI's official `codex@openai-codex` Claude Code plugin. Keep
the portable contract independent of the plugin's commands and state strings.

Read
[references/openai-codex-plugin-cc.md](references/openai-codex-plugin-cc.md)
before installing, upgrading, transferring a transcript, enabling the stop
review gate, or relying on a specific command or runtime behavior.

## Probe Before Delegating

When loaded as this Claude Code plugin, run:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/skills/claude-to-codex-coordinator/scripts/probe.py"
```

In another skills-compatible harness, resolve `scripts/probe.py` from the
installed directory that contains this `SKILL.md`; never resolve it from the
active project's working directory.

The probe reports only sanitized availability facts. It omits install paths and
raw authentication output. Stop and resolve any false prerequisite before
delegating.

Do not copy raw `/codex:setup` output into a repository or handoff. It can
contain account labels. Do not enable the optional stop review gate during
setup unless the user explicitly requests it and will monitor the resulting
Claude/Codex loop.

## Resolve the Assignment

1. Apply the portable six-axis classifier.
2. Record whether the task is review-only or write-capable.
3. State the repository scope, definition of done, required tests, evidence,
   and external-action boundary.
4. Preserve an explicit user model or effort choice.
5. Otherwise leave `--model` and `--effort` unset so the Codex configuration
   remains authoritative.
6. Record the requested tier and effort even when the adapter cannot prove the
   actual resolved model.

Do not map `routine`, `strong`, or `max` to a concrete Codex model without a
separate, versioned capability mapping. The plugin accepts explicit model and
effort flags, but its normal result and status surfaces do not prove the actual
resolved model. Record that field as `unknown` unless positive runtime evidence
is available.

## Choose the Official Operation

| Intent | Claude Code operation |
| --- | --- |
| Verify setup | `/codex:setup` |
| Read-only implementation review | `/codex:review` |
| Challenge design and assumptions | `/codex:adversarial-review` |
| Investigate or implement | `/codex:rescue` |
| Continue the same completed rescue thread | `/codex:rescue --resume` |
| Force an independent thread | `/codex:rescue --fresh` |
| Inspect active or recent work | `/codex:status` |
| Read a finished result | `/codex:result` |
| Stop an active job | `/codex:cancel` |
| Import the current Claude session into Codex | `/codex:transfer` |

Use `--background` for long or multi-step work and `--wait` for a small bounded
task. Always state read-only intent explicitly when edits are not authorized;
the upstream rescue subagent otherwise defaults to a write-capable Codex run.

Treat resume as between-turn follow-up steering. The official plugin does not
expose arbitrary mid-turn steering. Cancel the active turn and start or resume a
later turn when direction must change.

## Supervise the Job

1. Preserve the Codex output verbatim at the plugin boundary.
2. Treat that output as worker evidence, not completion proof.
3. For background work, inspect `/codex:status`, then `/codex:result` after a
   terminal state.
4. Verify claimed edits against the working tree and run the required tests.
5. Use `/codex:review` or an independent reviewer for the exact diff.
6. Route one concrete follow-up through `--resume` only when continuity is
   useful.
7. Use `/codex:cancel` when the run is looping, out of scope, or no longer
   authorized.

Keep implementation, local validation, live validation, review, human
approval, and release as separate ledger states. The plugin may edit the local
workspace; it does not grant permission to push, open a pull request, publish,
send a message, or perform another external action.

## Protect Transcript Boundaries

`/codex:transfer` imports a Claude transcript from the active Claude projects
directory into a persistent Codex thread. Use it only when the user explicitly
wants that session transferred and the transcript belongs to the active
project. Never transfer an unrelated session, raw credential, or private
cross-project history.

The plugin's repository-scoped job state and logs are runtime evidence. Keep
raw files outside the distributable package and admit only reviewed, redacted
derivatives through `coordination-conformance`.

## Produce the Handoff

Report:

- Claude session and Codex job or thread identifiers when safely available;
- requested tier and effort, requested model flags, and actual model or
  `unknown`;
- review-only or write-capable mode;
- repository scope and current working-tree or commit state;
- status, result, touched files, tests, and review evidence;
- whether the run was fresh, resumed, cancelled, or transferred;
- remaining approval or external-action gates;
- the precise next action and owner.
