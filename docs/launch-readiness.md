# Launch readiness

Status: public 0.2 four-skill release; new inverse-skill search indexing pending
Last checked: 2026-07-24
Release payload commit: `cbbf8afd132c0ef093148afc8aeded3043f2a34e`

This page separates a valid package from a published and discoverable release.
Public source and direct installation do not imply that a marketplace or the
skills.sh search index has ingested the same revision.

## Release evidence

| Requirement | Evidence | State |
| --- | --- | --- |
| Four Agent Skills packages | Local and public `npx skills add ... --list` runs discover `claude-to-codex-coordinator`, `codex-to-claude-coordinator`, `coordination-conformance`, and `coordination-core` | Pass |
| Codex-compatible metadata | Every skill has matching frontmatter and `agents/openai.yaml`; `scripts/verify_launch.py` checks explicit `$skill-name` prompts | Pass |
| Portable behavior | Unit tests cover classification, lifecycle envelopes, privacy, usage-signal eligibility, and stop semantics | Pass |
| Python runtime range | CI tests Python 3.9 and 3.12; the image-redaction dependency is pinned to the newest Pillow line that retains Python 3.9 support | Pass |
| Codex package installation | An isolated remote `skills` CLI rehearsal copies all four skills and supporting files for the `codex` agent | Pass |
| Multi-agent package installation | The same rehearsal targets Claude Code, Cursor, GitHub Copilot, Goose, and OpenHands | Pass |
| Claude plugin package | `claude plugin validate --strict .` accepts the local repository; Claude Code `2.1.218` loaded `/codex-to-claude-coordinator:coordination-core` and returned the exact fixture result even with all tools disabled | Pass |
| Official Claude-to-Codex runtime | Claude Code `2.1.218` installed `codex@openai-codex` `1.0.6`; `/codex:setup` reported ready with the optional review gate disabled | Pass on this machine |
| Claude-to-Codex delegation | A fresh, read-only `/codex:rescue --wait --fresh` task returned the expected active-repository heading through Codex app server without changing files | Pass on this machine |
| Codex runtime invocation | Fresh Codex CLI `0.146.0-alpha.3` with GPT-5.6 Sol loaded the isolated `$coordination-core` install both explicitly and from an implicit description match, ran its classifier at low or no reasoning effort, and returned schema-conforming output under a read-only sandbox | Pass |
| goose runtime invocation | goose `1.37.0` listed all three skills from the isolated install; interactive `/skills coordination-core` loaded the skill, reference, script, and schema and returned the expected fixture classification | Pass with invocation caveat |
| Public repository contents | Public `main`, annotated tag `v0.2.0`, and the GitHub release contain the four-skill `0.2.0` payload; remote `skills --list` discovers all four | Pass |
| skills.sh package pages and direct install | The package and original three skill pages resolve with descriptions. Remote multi-skill, inverse-only, tag-pinned, and one-run installs succeed. The inverse skill has been accepted by the audit backend, with Agent Trust Hub safe and Snyk low-risk results, while its detail document is still pending | Pass with inverse detail-index lag |
| skills.sh CLI search | Owner-scoped, exact-name, and broad searches still return no matching `wildcard` package. The canonical package pages and successful direct installs are not treated as search inclusion | Pending registry search index |
| GitHub skill search | `gh skill search` finds the three previously published `wildcard` skills. The exact new `claude-to-codex-coordinator` file is present on public `main` but is not yet in GitHub's code-search-backed result set | Pending inverse-file index |
| Public Claude marketplace install | An isolated Claude configuration registered the public GitHub marketplace and installed version `0.2.0` with all four skills and no unexpected agents, hooks, MCP servers, or LSP servers | Pass |

## Deterministic local gate

Run:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/verify_launch.py
npx skills add . --list
claude plugin validate --strict .
```

The verifier checks the exact skill set, frontmatter names, Codex UI metadata,
starter-prompt shape, discovery keywords, relative references, executable
Python helpers, synchronized plugin versions, the Python 3.9-compatible Pillow
pin, manifest source paths, install documentation, tracked experiment evidence,
and private machine literals.

## Isolated install rehearsal

From a temporary Git repository, run:

```sh
npx skills add /path/to/codex-to-claude-coordinator \
  --skill '*' \
  --agent codex claude-code cursor github-copilot goose openhands \
  --copy \
  -y
npx skills list --json > inventory.json
python /path/to/codex-to-claude-coordinator/scripts/verify_install_inventory.py \
  inventory.json \
  --install-root "$PWD"
```

Pass only when the JSON inventory contains all four skill names and every
selected harness root contains each copied skill. Codex, Cursor, and GitHub
Copilot share `.agents/skills`; Claude Code, Goose, and OpenHands use their own
roots. The CLI's `agents` labels describe harnesses detected on the current
host, so a headless Linux runner may omit universal-root labels even after an
explicit successful install. The verifier still requires the distinct-root
labels for Claude Code, Goose, and OpenHands. Inspect the copied roots and
supporting files, not universal-root display labels or only the CLI summary.

## Reverse adapter notes

The `claude-to-codex-coordinator` skill composes the portable ledger with
OpenAI's official `codex-plugin-cc`; it does not copy the upstream Node runtime.
The local privacy-safe probe confirms Claude, Node, Codex authentication, and
the installed plugin without emitting account labels or absolute install paths.

The official plugin supports fresh and resumed Codex turns, background status,
stored results, cancellation, code review, and explicit transcript transfer.
It does not expose arbitrary mid-turn steering or a normal result field proving
the actual resolved model. Those capabilities remain `partial` and `unknown`
respectively.

## Runtime invocation notes

The portable fixture lives under
`experiments/fixtures/classification-read-only/`. Codex passed both explicit and
implicit skill selection in fresh, ephemeral, read-only runs.

An initial Claude tool-less run exposed that a reference-only classification
contract could be replaced with invented field names. The version `0.1` rules
and exact vocabulary now live in the main skill as well as its reference,
script, and schema. A repeated Claude Code `2.1.218` plugin run with all tools
disabled then returned the exact expected object when invoked through the
documented `/codex-to-claude-coordinator:coordination-core` namespace. In the
same headless setup, a plain-English request to "use coordination-core" did not
reliably activate the plugin skill and produced invented fields. Direct
namespaced invocation is therefore the reproducible Claude conformance path;
automatic model invocation remains a separate behavior to test.

The public `0.2.0` marketplace install also exposed
`/codex-to-claude-coordinator:claude-to-codex-coordinator` in a fresh process.
With tools disabled, the adapter mapped a hypothetical read-only review to
`/codex:review`, kept `permission_mode` read-only, and reported the unresolved
actual model as `unknown`.

goose `1.37.0` discovered the same `.agents/skills` packages. In the observed
configuration, a headless natural-language request attempted the separate
`summon.load` tool and could not resolve the skill. Interactive
`/skills coordination-core` used `load_skill` correctly and passed the fixture.
The default smart-approval mode also cannot answer a headless tool prompt.
Do not change goose to autonomous mode merely to bypass that guard outside a
disposable, no-remote, no-credential fixture. Treat unattended natural-language
activation as unknown until reproduced with a version-pinned adapter.

## Public discovery gate

The skills.sh FAQ says skills are indexed automatically from anonymous install
telemetry. The public update and ordinary telemetry-enabled remote installs are
complete. The canonical repository and skill pages resolve, but the search API
and `skills find` can lag or disagree with those pages. Run:

```sh
npx skills find "codex claude coordinator"
npx skills find coordinator --owner wildcard
npx skills find claude-to-codex-coordinator
npx skills add wildcard/codex-to-claude-coordinator --list
gh skill search claude-to-codex-coordinator --owner wildcard
```

Pass only when the skills.sh searches return the expected repository, GitHub
skill search returns the inverse adapter, the inverse skills.sh detail page
contains its real description, and the remote list contains all four published
skills. Until then, describe `0.2.0` as published and directly installable but
not yet fully search-indexed. Do not manufacture installs to influence
telemetry-backed ranking.

The repeatable, fail-closed check for the three asynchronous search surfaces is:

```sh
python3 scripts/check_public_discovery.py
```

It exits `0` only when every published description appears on skills.sh and
both skills.sh search and GitHub skill search return all four skills. Network,
authentication, or rate-limit failures are reported as `unknown`, not as
evidence of absence.

## External-action boundary

Committing, pushing, tagging, publishing, adding a marketplace, and performing
an indexing install are separate actions. The `0.2.0` push, tag, GitHub release,
repository metadata updates, public install rehearsals, and indexing installs
recorded above were explicitly authorized; future external actions still
require explicit human authorization.
