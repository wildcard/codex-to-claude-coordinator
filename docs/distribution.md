# Distribution plan

Status: local packaging validated; nothing published
Last checked: 2026-07-23

## Source of truth

Keep each capability in an Agent Skills-compatible `skills/<name>/` directory.
The portable `coordination-core` skill must remain usable without either plugin
manifest. Harness packaging points at that source tree; it does not fork the
skill content.

Versioned releases should contain:

- all three skill directories, including referenced schemas and scripts;
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`;
- `.codex-plugin/plugin.json`;
- tests and the evidence-backed compatibility report;
- a changelog entry describing protocol or policy migrations.

## skills.sh

skills.sh installs skills from public Git repositories with the `skills` CLI.
The release target is:

```sh
npx skills add wildcard/codex-to-claude-coordinator \
  --skill '*' \
  --agent codex claude-code cursor github-copilot goose openhands \
  -y
```

Before publishing, replace the repository slug with the release-candidate
checkout and run the command in a temporary Git repository. Confirm that all
three skills are discovered, their references and scripts are copied, and the
validator tests still pass from the installed location.

skills.sh search is telemetry-backed. A public Git source does not appear in
`npx skills find` merely because it exists. After an approved release, one
normal remote installation with telemetry enabled is needed for indexing. Then
verify both broad and owner-scoped searches:

```sh
npx skills find "codex claude coordinator"
npx skills find coordinator --owner wildcard
```

Do not add an install-count badge until the public source is stable.

The CLI can also project one skill into a temporary, single-run prompt without
installing it:

```sh
npx skills use wildcard/codex-to-claude-coordinator@coordination-core
```

The local equivalent, reproduced against the release candidate, is
`npx skills use . --skill coordination-core`. It includes the skill instructions
and a temporary path containing its referenced support files.

## Claude Code marketplace

The repository is both the marketplace root and the single plugin source.
Before an approved release:

```sh
claude plugin validate --strict .
claude --plugin-dir .
```

After the repository is public and tagged, the intended marketplace flow is:

```text
/plugin marketplace add wildcard/codex-to-claude-coordinator
/plugin install codex-to-claude-coordinator@codex-to-claude-coordinator
/reload-plugins
```

Claude plugin skills are namespaced. Test the portable core directly with:

```text
/codex-to-claude-coordinator:coordination-core
```

The plugin version in `.claude-plugin/plugin.json` must change for every
versioned release. A release candidate must prove that cached installation
contains all referenced files; plugins cannot depend on paths outside their
copied directory.

## Codex

Codex discovers repository skills under `.agents/skills` and user skills under
`$HOME/.agents/skills`. The `skills` CLI maps the source package into the
selected scope. The repository also contains a Codex plugin manifest so the same
three skills can be distributed together through Codex plugin surfaces.

## Release gate

Publication remains a human-approved external action. A release candidate is
ready for approval only when:

1. portable unit tests pass;
2. all three skills validate;
3. both plugin manifests validate;
4. local Claude plugin loading succeeds;
5. local Codex skill discovery succeeds;
6. no private transcripts, account details, raw screenshots, credentials, or
   machine-specific paths appear in the package;
7. the compatibility report labels documented, observed, inferred, and unknown
   claims separately.
8. `scripts/verify_launch.py` passes;
9. an isolated `skills` CLI rehearsal installs all three skills for Codex and
   the other named harnesses;
10. publication and skills.sh indexing remain explicit external gates until
    observed.

## Primary references

- [skills.sh documentation](https://www.skills.sh/docs)
- [Claude Code marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces)
- [Codex skill documentation](https://developers.openai.com/codex/skills)
