# Project instructions

This repository develops a portable coordination skill with Codex as the first outer coordinator and Claude as the first delegated harness.

## Boundaries

- Keep examples, fixtures, transcripts, and documentation generic.
- Never copy private material or unrelated project history into this repository.
- Separate observed behavior, official documentation, and inference.
- Treat model names, quota meters, product surfaces, and permissions as versioned capabilities.
- Do not commit credentials, account identifiers, private transcripts, or machine-specific secrets.
- Do not push, publish, open pull requests, or send messages without explicit authorization.

## Development workflow

1. Start from a falsifiable research question.
2. Record authoritative sources and the date checked.
3. Build the smallest reproducible experiment that tests the question.
4. Capture inputs, outputs, model and harness versions, permissions, and limitations.
5. Review the exact diff and run the skill validator before committing.

## Canonical artifacts

- `skills/codex-to-claude-coordinator/` is the distributable skill.
- `skills/coordination-core/` is the vendor-neutral lifecycle contract.
- `skills/coordination-conformance/` is the evidence and capability test kit.
- `docs/architecture.md` defines the portable core and adapter boundary.
- `docs/harness-landscape.md` tracks evidence about candidate coordinators.
- `docs/research-roadmap.md` defines planned experiments and acceptance evidence.
- `docs/claude-advisor-protocol.md` defines how Claude advises this project without becoming an unreviewed source of truth.
