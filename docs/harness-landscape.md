# Harness landscape

Status: initial evidence map
Last checked: 2026-07-23

This document answers the first research question: who else can perform the coordination role currently performed by Codex?

## Evidence summary

| Harness | Proven coordination surface | Current assessment |
| --- | --- | --- |
| Codex | Multiple project tasks, worktrees, subagents, handoff, and Codex-as-MCP workflows | Strong outer coordinator and reference adapter |
| Claude Code | Custom subagents, agent teams, background agents, hooks, sessions, permissions, and Agent SDK | Strong Claude-native coordinator inside its own execution boundary |
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

The remaining gap is not general reasoning ability. It is product-level control over:

- all relevant desktop sessions;
- current per-model or plan quota meters;
- deterministic model switching before every start or steer;
- cross-product transcript normalization;
- independent review evidence;
- consistent external-action approval boundaries.

Dispatch can already act as a Claude-native outer coordinator for Cowork and Claude Code. It does not replace a cross-harness coordinator because its documented routing boundary stops at those two surfaces and it exposes no public lifecycle API or model/quota selection controls.

## Primary sources

### OpenAI

- [Codex worktrees](https://developers.openai.com/codex/environments/git-worktrees)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex as an MCP server](https://developers.openai.com/codex/mcp-server)
- [Codex `AGENTS.md`](https://developers.openai.com/codex/agent-configuration/agents-md)

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

## Research gaps

- Reproduce the documented Claude Desktop Dispatch workflow and compare observed states to the guide.
- Find a supported API or export for Claude Desktop session inventory and usage meters.
- Collect first-party Devin lifecycle and steering documentation.
- Determine which adapters can expose immutable audit events rather than rendered summaries.
- Test whether the Agent Skills package is accepted unchanged by Claude, Copilot, goose, and other compatible systems.
