# OpenAI codex-plugin-cc adapter reference

Last checked: 2026-07-23

## Source boundary

Authoritative source:
[openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc).
The inspected source revision was
`db52e28f4d9ded852ab3942cea316258ae4ef346` (`v1.0.6`).

The official plugin is the runtime adapter. This project supplies the portable
classification, evidence ledger, approval boundary, and coordinator policy. Do
not copy the upstream Node runtime into this skill or treat upstream behavior
as portable core behavior.

## Installation

In Claude Code:

```text
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

The plugin requires Node.js 18.18 or later and a working, authenticated Codex
CLI. It uses the local Codex CLI, authentication, configuration, repository
checkout, and machine environment.

Do not enable `/codex:setup --enable-review-gate` by default. The upstream
documentation warns that the gate can create a long-running Claude/Codex loop
and consume usage quickly.

## Runtime architecture

The upstream package separates:

1. Claude slash commands and a thin `codex-rescue` forwarding subagent;
2. a deterministic `codex-companion.mjs` command surface;
3. a shared Codex app-server broker;
4. repository-scoped job state and logs under Claude plugin data;
5. native Codex threads and turns that can be resumed or interrupted.

The broker streams `turn/start`, `review/start`, and compact operations through
one shared app-server process. Cancellation attempts `turn/interrupt` before
terminating the worker process. Background work stores queued, running,
completed, failed, or cancelled records and caps retained job history.

Claude `SessionStart` and `SessionEnd` hooks attach jobs to the current Claude
session and clean that session's job artifacts. A separate `Stop` hook implements
the optional review gate.

## Adapter capability map

| Portable operation | Official surface | Assessment |
| --- | --- | --- |
| `inspect_capabilities` | `/codex:setup`, plugin inventory | Available |
| `inspect_usage` | No named-model consumed-percentage API | Unavailable |
| `list_sessions` | `/codex:status`; Codex thread state is indirect | Partial |
| `start_session` | `/codex:rescue --fresh` | Available |
| `read_session` | `/codex:status`, `/codex:result` | Available |
| `steer_session` | `/codex:rescue --resume` after a turn | Partial; no arbitrary mid-turn steer |
| `stop_session` | `/codex:cancel` | Available for active jobs |
| `collect_changes` | Result payload plus independent working-tree inspection | Partial |
| `collect_review` | `/codex:review`, `/codex:adversarial-review` | Available |
| transcript handoff | `/codex:transfer` | Available with an explicit privacy gate |
| model selection | `--model`; configured default when omitted | Available as requested input |
| actual model evidence | Not exposed by normal job result/status output | Unknown |
| reasoning effort | `--effort none|minimal|low|medium|high|xhigh` | Available as requested input |

## Command behavior

- `/codex:review` uses the built-in reviewer and is read-only. It selects
  uncommitted changes or a base-branch diff.
- `/codex:adversarial-review` is read-only and accepts extra focus text for
  design and assumption challenges.
- `/codex:rescue` delegates through the `codex-rescue` subagent. `--fresh`
  starts independently; `--resume` continues the latest eligible task thread
  for the current Claude session.
- `/codex:status` and `/codex:result` expose tracked background state and stored
  output.
- `/codex:cancel` interrupts an active turn when possible and marks the job
  cancelled.
- `/codex:transfer` imports the current Claude JSONL transcript through Codex's
  external-agent session importer and returns a resumable Codex thread.

The forwarding layer deliberately returns Codex output without paraphrase.
That is a useful evidence-preservation boundary, but it is not independent
verification. The outer coordinator must still inspect the diff, tests, and
review state before declaring completion.

## Model and permission policy

The upstream rescue agent leaves model and effort unset unless the user
explicitly chooses them. Preserve that behavior. A portable capability tier is
an intent, not a Codex model alias.

The rescue agent defaults to a write-capable Codex task unless the request
explicitly asks for read-only work. Every assignment must therefore state one
of:

- `review-only` or `read-only`, with no edits;
- `workspace-write`, with exact owned files and validation;
- an explicitly authorized external action, which remains a separate human
  gate.

The optional stop review gate is a review control, not an approval authority.
Upstream tests show it does not block when Codex is unavailable. Treat its
evidence as supplemental and fail closed through the portable ledger when an
independent review is required.

## Privacy boundary

Treat the following as private runtime material:

- raw `/codex:setup` output, which can include account labels;
- plugin job files and logs;
- Claude transcripts selected for `/codex:transfer`;
- absolute install and project paths;
- Codex authentication and provider configuration.

The probe script intentionally emits none of those values.

## Local observation

Observed on 2026-07-23:

- Claude Code `2.1.218` installed `codex@openai-codex` `1.0.6`;
- Codex CLI `0.145.0` was available and authenticated through the existing
  ChatGPT login;
- `/codex:setup` reported ready with the review gate disabled;
- a fresh `/codex:rescue --wait --fresh` read-only task delegated through Codex
  app server and returned the expected first heading from the active
  repository;
- no repository files changed;
- the upstream source suite passed all 91 tests.

This observation proves a bounded Claude-to-Codex delegation path on this
machine. It does not prove arbitrary mid-turn steering, model-resolution
telemetry, quota introspection, or safe transcript transfer for every project.
