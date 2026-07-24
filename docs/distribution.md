# Distribution plan

Status: public 0.2 four-skill package is directly installable; search refresh remains pending
Last checked: 2026-07-24

## Source of truth

Keep each capability in an Agent Skills-compatible `skills/<name>/` directory.
The portable `coordination-core` skill must remain usable without either plugin
manifest. Harness packaging points at that source tree; it does not fork the
skill content.

Versioned releases should contain:

- all four skill directories, including referenced schemas and scripts;
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

Before each public update, replace the repository slug with the candidate
checkout and run the command in a temporary Git repository. Confirm that all
four skills are discovered, their references and scripts are copied, and the
validator tests still pass from the installed location. Repeat the command
against the public source after pushing.

skills.sh search is telemetry-backed. A public Git source does not appear in
`npx skills find` merely because it exists. After publishing, run a normal
remote installation with telemetry enabled, then verify both broad and
owner-scoped searches:

```sh
npx skills find "codex claude coordinator"
npx skills find coordinator --owner wildcard
```

The current public package passes remote installation and has canonical
skills.sh pages. Its original three skills have populated detail documents, and
the registry audit backend has accepted the new inverse adapter, but the search
API has not yet returned the package and the inverse detail document has not
populated. Treat page availability, direct installation, registry audit, and
search inclusion as separate observations. The README badge reports observed
registry telemetry; it is not proof that search indexing has completed.

The CLI can also project one skill into a temporary, single-run prompt without
installing it:

```sh
npx skills use wildcard/codex-to-claude-coordinator@coordination-core
```

The local equivalent, also reproduced against the published package, is
`npx skills use . --skill coordination-core`. It includes the skill instructions
and a temporary path containing its referenced support files.

## Claude Code marketplace

The repository is both the marketplace root and the single plugin source.
Before each release:

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

The reverse adapter depends on OpenAI's separate official marketplace plugin:

```text
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

Do not vendor its runtime or silently enable its optional stop-review gate.
Test the adapter skill through:

```text
/codex-to-claude-coordinator:claude-to-codex-coordinator
```

The plugin version in `.claude-plugin/plugin.json` must change for every
versioned release. Keep that version synchronized with the marketplace metadata
and plugin entry. A release candidate must prove that cached installation
contains all referenced files; plugins cannot depend on paths outside their
copied directory.

## Codex

Codex discovers repository skills under `.agents/skills` and user skills under
`$HOME/.agents/skills`. The `skills` CLI maps the source package into the
selected scope. The repository also contains a Codex plugin manifest so the same
four skills can be distributed together through Codex plugin surfaces.

## Release gate

Publication remains a human-approved external action. A release candidate is
ready for approval only when:

1. portable unit tests pass;
2. all four skills validate;
3. both plugin manifests validate;
4. local Claude plugin loading succeeds;
5. local Codex skill discovery succeeds;
6. no private transcripts, account details, raw screenshots, credentials, or
   machine-specific paths appear in the package;
7. the compatibility report labels documented, observed, inferred, and unknown
   claims separately.
8. `scripts/verify_launch.py` passes;
9. an isolated `skills` CLI rehearsal installs all four skills for Codex and
   the other named harnesses;
10. the public origin revision, direct remote installation, registry page and
    audit state, and `skills find` inclusion are recorded as separate external
    gates.

## Primary references

- [skills.sh documentation](https://www.skills.sh/docs)
- [Claude Code marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces)
- [Codex skill documentation](https://developers.openai.com/codex/skills)
- [OpenAI Codex plugin for Claude Code](https://github.com/openai/codex-plugin-cc)
