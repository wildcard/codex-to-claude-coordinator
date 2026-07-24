# Codex to Claude Coordinator

A distributable Codex skill and research project for coordinating Claude Desktop and Claude Code work from delegation through reviewed, tested handoff.

It provides a repeatable process for:

- choosing Fable, Opus, or Sonnet 5 from task complexity and current visible usage;
- starting or reusing the right Claude session;
- steering stalled work without losing project boundaries;
- requiring `/review`, self-review, available pull-request review agents, tests, and demos;
- separating local readiness from approval, release, and other external gates;
- reporting real blockers and precise next actions.

Codex is the first coordinator and Claude is the first delegated harness. The project is also testing whether Claude can coordinate the same lifecycle itself and whether the workflow can be adapted to other frontier agent harnesses.

## Model policy

An explicit user model choice always wins. Otherwise:

| Work | Selection |
| --- | --- |
| Simple | Sonnet 5 |
| Tricky | Opus by default; Sonnet 5 when Opus is unavailable or has reached 50% consumed usage |
| Complex | Fable only below 25% consumed usage; otherwise Opus below 50%; otherwise Sonnet 5 |

The coordinator rechecks the visible usage indicators before every new session and every steer. If the indicator is unavailable or ambiguous, it does not assume Fable eligibility.

## Install

Copy the skill package into your user-level Codex skills directory:

```sh
mkdir -p ~/.codex/skills
cp -R skills/codex-to-claude-coordinator ~/.codex/skills/
```

Restart or reload Codex if the skill does not appear immediately.

## Use

Invoke the skill explicitly:

```text
Use $codex-to-claude-coordinator to delegate and supervise this task in Claude.
```

It also activates for requests to start, steer, monitor, or audit Claude sessions.

## Privacy

Keep delegated context scoped to the active task. Do not copy credentials, unrelated transcripts, or private project material into a different project or published artifact.

## Research

- [Portable architecture](docs/architecture.md)
- [Harness landscape](docs/harness-landscape.md)
- [Research roadmap](docs/research-roadmap.md)
- [Claude advisor protocol](docs/claude-advisor-protocol.md)
- [First Claude advisory memo](docs/claude-advisory-2026-07-23.md)

## License

MIT
