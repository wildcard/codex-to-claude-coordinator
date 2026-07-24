# Harness landscape

Status: authoritative-source audit
Last checked: 2026-07-23

This document answers the first research question: who else can perform the coordination role currently performed by Codex?

## Evidence summary

| Harness | Proven coordination surface | Current assessment |
| --- | --- | --- |
| Codex | Multiple project tasks, worktrees, subagents, handoff, and Codex-as-MCP workflows | Strong outer coordinator and reference adapter |
| Claude Code | Scoped JSON session inventory, logs, replies, stop, per-session models, worktree isolation, custom subagents, agent teams, hooks, permissions, and Agent SDK | Strong Claude-native coordinator inside its own execution boundary; agent view is a research preview |
| Claude Code + OpenAI Codex plugin | Official Codex app-server delegation, native review, background jobs, status, results, cancel, resume, and Claude-session transfer | Strong inverse adapter for Claude-to-Codex work; mid-turn steering, quota signals, and actual-model evidence remain gaps |
| Claude Desktop Cowork | Long-running tasks, connectors, browser control, and artifacts | Useful knowledge-work executor; programmable lifecycle parity remains unproven |
| Claude Dispatch | Cowork coordinator that decomposes outcomes into child Cowork or Code sessions, exposes status and transcripts, and forwards approvals | Strong Claude-native outer coordinator for Cowork and Code; no public programmatic API or model/quota controls documented |
| GitHub Copilot cloud agent | Issue-to-draft-PR execution, follow-up through review comments, custom agents, hooks, and skills | Strong GitHub-scoped executor; weaker for cross-app orchestration |
| Google Jules | REST API and CLI for session creation, listing, plan approval, interaction, status, and results | Strong candidate for a programmatic adapter |
| Cursor Background Agents | API for creating and managing remote agents plus follow-up prompts and status | Strong candidate; isolated remote execution has explicit security tradeoffs |
| OpenHands | Agent Server API for workspaces, conversations, messages, streams, confirmations, and model choice | Strong open and self-hostable adapter candidate |
| goose | Desktop, CLI, API, portable recipes, subagents, extension controls, and multiple model providers | Strong local, model-neutral experiment candidate |
| Devin | Commonly described as a managed coding-agent platform | Keep as a candidate until first-party lifecycle evidence is collected |

## Claude specifically

Claude can perform much of the role in two different ways:

1. **Claude Code-native:** a lead agent can assign work to subagents or agent teams, use hooks, and coordinate results.
2. **Agent SDK-controlled:** a custom controller can manage sessions, tools, permissions, hooks, and subagents programmatically.

Anthropic's official Dispatch guide confirms that Dispatch is a long-running Cowork agent. It runs child work as separate Cowork or Code sessions, exposes six task states and full transcripts, forwards permission requests to the human, and allows follow-up messages. Child tasks cannot create further Dispatch children.

The remaining gap is not general reasoning ability. Across Dispatch and Claude
Code, it is consistent product-level control over:

- all relevant desktop sessions;
- current per-model or plan quota meters;
- deterministic model switching before every start or steer across both products;
- cross-product transcript normalization;
- independent review evidence;
- consistent external-action approval boundaries.

Current Claude Code documentation materially strengthens its adapter case:
agent view can list scoped sessions as JSON, print logs, accept replies, stop a
session, and select or switch a model for individual background sessions.
Dispatch can already act as a Claude-native outer coordinator for Cowork and
Claude Code. It does not replace a cross-harness coordinator because its
documented routing boundary stops at those two surfaces and it exposes no public
lifecycle API or model/quota selection controls.

## Local Claude Code probe

Observed on Claude Code 2.1.216 on 2026-07-23:

- repository plugin validation and a leading
  `/codex-to-claude-coordinator:coordination-conformance` invocation succeeded
  in no-tools print mode;
- embedding `Use /plugin:skill` inside prose did not invoke the skill in that
  mode, and the worker correctly declined to invent the unread policy;
- `claude agents --cwd <project> --json --all` returned a project-scoped JSON
  inventory;
- a no-tools background task was created, listed as busy/working, and its
  expected generic result was readable through its scoped log;
- after producing the result, inventory showed `status=idle` while
  `state=working`; idle therefore was not terminal evidence;
- an explicit stop command was followed by `state=stopped`;
- the raw log rendered account identity and an absolute project path in its UI
  chrome, so it is not safe evidence until redacted.

The local capability manifest marks `inspect_capabilities`, `list_sessions`,
`start_session`, `read_session`, and `stop_session` as passing. It keeps
`steer_session`, `inspect_usage`, `collect_changes`, and `collect_review`
unknown. The evidence bundle remains under ignored `experiments/runs/`; no
identifiers or raw transcript are committed.

A later plugin run on Claude Code `2.1.218` reproduced the portable
classification fixture with all tools disabled after the exact version `0.1`
rules were moved into the main skill. Before that change, the same tool-less
surface invented invalid field names and values instead of reading supporting
files. This establishes an important packaging rule: a skill that must work on
instruction-only surfaces needs its minimal decision contract in `SKILL.md`;
supporting scripts remain the deterministic verifier, not the only copy of the
rules.

## Local cross-harness skill probe

Observed on 2026-07-23:

- Codex CLI `0.146.0-alpha.3` with GPT-5.6 Sol loaded the isolated
  `coordination-core` skill explicitly and through an implicit description
  match, read its support files, ran its classifier, and returned the expected
  six-field output under a read-only sandbox.
- goose `1.37.0` listed all three isolated skills from `.agents/skills`.
- goose's interactive `/skills coordination-core` command used its
  `load_skill` mechanism to load the skill, reference, script, and schema and
  returned the same expected classification.
- a headless goose natural-language request attempted the separate
  `summon.load` surface and could not resolve the skill. Smart-approval mode
  also cannot service a headless approval prompt.

The finding is narrower than “goose fully supports the adapter.” Portable skill
content and explicit interactive invocation passed. Unattended implicit
invocation remains unknown, and autonomous permission mode is not an acceptable
workaround outside a disposable sandbox.

## Local Claude-to-Codex probe

OpenAI's official
[`codex-plugin-cc`](https://github.com/openai/codex-plugin-cc) is the inverse of
this project's first adapter: Claude Code coordinates Codex through the local
Codex CLI and app server. Source revision
`db52e28f4d9ded852ab3942cea316258ae4ef346` (`v1.0.6`) exposes:

- read-only native and adversarial review commands;
- a thin `codex-rescue` forwarding subagent for investigation and
  implementation;
- fresh and resumed Codex task threads;
- foreground and repository-scoped background jobs;
- status, stored results, cancel, and Claude-session transfer;
- session lifecycle hooks and an optional stop-time review gate;
- explicit model and effort inputs, while leaving both unset by default.

Observed on Claude Code `2.1.218` and Codex CLI `0.145.0` on 2026-07-23:

- the official plugin installed and enabled at version `1.0.6`;
- the setup command reported Codex ready using the existing authentication and
  left the optional review gate disabled;
- a fresh read-only rescue task returned the expected first heading from the
  active repository with no file changes;
- the upstream package passed all 91 source tests;
- the setup surface can expose an account label, so raw setup output is private
  runtime material and was not admitted to this repository.

The adapter can steer between completed turns through resume and can cancel an
active turn. It does not document arbitrary mid-turn instruction injection, a
named-model quota percentage, or a normal job field proving the actual resolved
model. These remain partial, unavailable, and unknown respectively.

## Audit disposition

The table below is the first-party documentation audit. It remains distinct from
the authenticated local probe above: “documented” is not “locally reproduced.”

| Harness | First-party lifecycle facts verified | Still unknown or overstated |
| --- | --- | --- |
| Codex | Subagents and isolated worktrees are documented | Cross-product quota normalization is not established |
| Claude Code + OpenAI Codex plugin | Review, rescue, background jobs, resume, status, result, cancel, transfer, app-server reuse, and explicit model/effort flags are implemented in OpenAI's public repository | Mid-turn steer, named-model quota, and actual resolved-model evidence |
| Claude Dispatch | Cowork/Code routing, child states and transcripts, follow-ups, and forwarded approvals are documented | Public API, model control, quota inspection, and stop semantics |
| Claude Code | Agent view documents scoped JSON inventory, logs, reply/attach, stop, background persistence, and per-session model control; Agent SDK documents sessions, permissions, hooks, and subagents | Account quota is not documented as a fresh named-model consumed percentage |
| GitHub Copilot cloud agent | Branch-based background work, ephemeral Actions environment, tests, iteration, and optional pull requests are documented | General cross-app session control and model-specific quota facts |
| Google Jules | REST creation, get/list, plan approval, activity interaction, and outputs are documented | Portable permission equivalence and immutable event provenance |
| Cursor Background Agents | API creation/management and follow-ups plus isolated remote execution are documented | The canonical docs URL currently redirects in a generic fetch; security includes auto-run and repository write access |
| OpenHands | Conversation messages, run/pause, confirmation states, status, and persistence are documented | Hosted-service parity with the self-hosted SDK and immutable audit guarantees |
| goose | Local multi-provider execution, recipes, and subagent controls are documented in the project repository | Stable public lifecycle API and conformance behavior need a version-pinned run |

The audit found no first-party basis for converting an unlabeled, shared, plan,
weekly, context, token, or cost signal into model-specific consumed quota.
Experiment 1 therefore starts from `unknown`, not `unavailable`, and requires
positive evidence before enabling threshold automation.

## Primary sources

### OpenAI

- [Codex worktrees](https://developers.openai.com/codex/environments/git-worktrees)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex as an MCP server](https://developers.openai.com/codex/mcp-server)
- [Codex `AGENTS.md`](https://developers.openai.com/codex/agent-configuration/agents-md)
- [OpenAI Codex plugin for Claude Code](https://github.com/openai/codex-plugin-cc)

### Anthropic

- [Claude Code overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Claude Code custom subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [Claude Code hooks](https://docs.anthropic.com/en/docs/claude-code/hooks-guide)
- [Claude Agent SDK](https://docs.anthropic.com/en/docs/claude-code/sdk)
- [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code settings](https://docs.anthropic.com/en/docs/claude-code/settings)
- [Claude in Chrome and Cowork](https://support.anthropic.com/en/articles/12012173-getting-started-with-claude-for-chrome)
- [Claude Opus 4.6 product update describing agent teams](https://www.anthropic.com/news/claude-opus-4-6)
- [Claude Dispatch guide](https://claude.com/docs/cowork/guide/dispatch)
- [Dispatch and computer use announcement](https://claude.com/blog/dispatch-and-computer-use)
- [Claude Code agent view](https://code.claude.com/docs/en/agent-view)
- [Claude Code usage and costs](https://code.claude.com/docs/en/costs)
- [Claude Code model configuration](https://code.claude.com/docs/en/model-config)

The local `Dispatch Beta` label and the public guide now corroborate each other. Treat implementation details beyond the guide as unverified until reproduced.

### GitHub

- [GitHub Copilot cloud agent](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent)
- [GitHub Copilot custom agents](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents)
- [GitHub Copilot agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Third-party coding agents on GitHub](https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents)

### Google

- [Jules getting started](https://jules.google/docs/)
- [Jules task lifecycle](https://jules.google/docs/running-tasks/)
- [Jules REST API](https://jules.google/docs/api/reference/)
- [Jules CLI](https://jules.google/docs/cli/reference/)

### Cursor

- [Cursor Background Agents](https://docs.cursor.com/background-agent)
- [Cursor Background Agents API](https://docs.cursor.com/background-agent/api/overview)

### OpenHands

- [OpenHands Agent Server](https://docs.openhands.dev/sdk/arch/agent-server)
- [OpenHands conversation API](https://docs.openhands.dev/sdk/api-reference/openhands.sdk.conversation)

### goose

- [goose overview](https://block.github.io/goose/index.html)
- [goose subagents](https://goose-docs.ai/docs/guides/context-engineering/subagents/)
- [goose recipes](https://goose-docs.ai/docs/guides/recipes/)
- [goose Agent Skills](https://goose-docs.ai/docs/guides/context-engineering/using-skills/)
- [goose permission modes](https://goose-docs.ai/docs/guides/goose-permissions/)
- [goose CLI providers](https://goose-docs.ai/docs/guides/cli-providers/)

## Research gaps

- Run the implementation-ready protocols in
  [Experiment 0 and 1 protocols](experiments-0-1.md).
- Find a supported API or export for Claude Desktop session inventory and usage meters.
- Collect first-party Devin lifecycle and steering documentation.
- Determine which adapters can expose immutable audit events rather than rendered summaries.
- Test unattended Agent Skills invocation in GitHub Copilot, Cursor, OpenHands,
  and goose; Codex and explicit interactive goose invocation now pass the
  portable classification fixture.
