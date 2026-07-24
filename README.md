# Codex to Claude Coordinator

[![skills.sh](https://skills.sh/b/wildcard/codex-to-claude-coordinator)](https://skills.sh/wildcard/codex-to-claude-coordinator)

A bidirectional cross-harness plugin, distributable skills, and research
project for coordinating agent work from delegation through reviewed, tested
handoff.

It provides a repeatable process for:

- resolving a portable capability tier and reasoning effort to an available
  Claude worker using explicit evidence;
- starting or reusing the right Claude session;
- delegating Claude Code work back to Codex through OpenAI's official
  `codex-plugin-cc`;
- steering stalled work without losing project boundaries;
- requiring `/review`, self-review, available pull-request review agents, tests, and demos;
- separating local readiness from approval, release, and other external gates;
- reporting real blockers and precise next actions.

Codex is the first coordinator and Claude is the first delegated harness, but
the supported path is now bidirectional. The portable `coordination-core` skill
contains no vendor commands or model names; `coordination-conformance` records
and validates capability evidence; `codex-to-claude-coordinator` adapts Codex
to Claude; and `claude-to-codex-coordinator` composes the same lifecycle with
OpenAI's official Claude Code plugin.

## Discover

- [Complete package on skills.sh](https://skills.sh/wildcard/codex-to-claude-coordinator)
- [`codex-to-claude-coordinator`](https://skills.sh/wildcard/codex-to-claude-coordinator/codex-to-claude-coordinator)
- [`claude-to-codex-coordinator`](https://skills.sh/wildcard/codex-to-claude-coordinator/claude-to-codex-coordinator)
- [`coordination-core`](https://skills.sh/wildcard/codex-to-claude-coordinator/coordination-core)
- [`coordination-conformance`](https://skills.sh/wildcard/codex-to-claude-coordinator/coordination-conformance)

## Model and effort policy

An explicit user model choice always wins. Otherwise, classify the task into
six independent axes using the portable core: difficulty, risk, duration,
coordination shape, requested capability tier, and reasoning effort.

The Claude adapter maps requested tiers as follows:

| Requested tier | Selection |
| --- | --- |
| Routine | Sonnet 5 |
| Strong | Opus when selectable; otherwise Sonnet 5 |
| Max | Fable only when selectable and an explicit Fable consumed meter is below 25%; otherwise Opus, then Sonnet 5 |

Model availability is probed before session creation. Shared, stale, or
unlabeled usage bars never become per-model percentages. A steer keeps the
session's actual model unless the adapter proves that it can switch; otherwise
the coordinator may start a replacement session. Effort is selected separately.

The Claude-to-Codex adapter records the same tier and effort intent but leaves
the official plugin's `--model` and `--effort` flags unset unless the user
explicitly selects them. The configured Codex default remains authoritative,
and the actual resolved model stays `unknown` unless the runtime exposes it.

## Install

Install the complete skill set into a project for Codex:

```sh
npx skills add wildcard/codex-to-claude-coordinator \
  --skill '*' \
  --agent codex \
  -y
```

Add `-g` for a CLI-managed user-level install. For direct authoring, Codex's
official locations are repository `.agents/skills` and user
`$HOME/.agents/skills`.

Install the same source for several skills-compatible harnesses:

```sh
npx skills add wildcard/codex-to-claude-coordinator \
  --skill '*' \
  --agent codex claude-code cursor github-copilot goose openhands \
  -y
```

Install for every agent recognized by the current `skills` CLI:

```sh
npx skills add wildcard/codex-to-claude-coordinator --all
```

The `0.2` package contains all four skills, including the bidirectional
`claude-to-codex-coordinator` adapter.

For Claude Code plugin development, validate and load the repository directly:

```sh
claude plugin validate --strict .
claude --plugin-dir .
```

To persist a local checkout in Claude Code without publishing it:

```sh
claude plugin marketplace add /path/to/codex-to-claude-coordinator --scope user
claude plugin install \
  codex-to-claude-coordinator@codex-to-claude-coordinator \
  --scope user
```

Start a fresh Claude Code session after installing. This local marketplace
registration is machine-local and does not publish the candidate.

Marketplace publication remains approval-gated. Restart or reload a harness if
a newly installed skill does not appear immediately.

To give Claude Code the official runtime that delegates back to Codex:

```text
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

This repository does not vendor that runtime. It supplies the coordinator
policy and evidence contract around the official plugin.

## Use

Invoke the skill explicitly:

```text
Use $codex-to-claude-coordinator to delegate and supervise this task in Claude.
```

It also activates for requests to start, steer, monitor, or audit Claude sessions.

Coordinate in the reverse direction:

```text
Use $claude-to-codex-coordinator to delegate and supervise this Codex task from Claude Code.
```

When loaded as a Claude Code plugin, invoke it as:

```text
/codex-to-claude-coordinator:claude-to-codex-coordinator
```

The adapter then selects an official operation such as `/codex:rescue`,
`/codex:status`, `/codex:result`, or `/codex:cancel`.

Use the portable core without a vendor adapter:

```text
Use $coordination-core to classify this task and create a coordination envelope stream.
```

When the repository is loaded as a Claude Code plugin, invoke the same skill
through its plugin namespace:

```text
/codex-to-claude-coordinator:coordination-core
```

Test a harness capability without inferring missing support:

```text
Use $coordination-conformance to record and validate this local experiment.
```

Generate a one-run prompt and temporary support-file bundle without installing
the skill:

```sh
npx skills use wildcard/codex-to-claude-coordinator@coordination-core
```

The remote form uses the current public package. For a local checkout, use
`npx skills use . --skill coordination-core`.

## Privacy

Keep delegated context scoped to the active task. Do not copy credentials,
unrelated transcripts, raw plugin setup output, or private project material
into a different project or published artifact. Use `/codex:transfer` only for
an explicitly authorized transcript from the active project.

## Research

- [Portable architecture](docs/architecture.md)
- [Distribution plan](docs/distribution.md)
- [Launch readiness](docs/launch-readiness.md)
- [Harness landscape](docs/harness-landscape.md)
- [Research roadmap](docs/research-roadmap.md)
- [Claude advisor protocol](docs/claude-advisor-protocol.md)
- [First Claude advisory memo](docs/claude-advisory-2026-07-23.md)
- [Changelog](CHANGELOG.md)

## License

MIT
