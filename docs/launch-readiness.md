# Launch readiness

Status: local 0.2 four-skill candidate; public 0.1 search indexing pending
Last checked: 2026-07-23
Release payload commit: `7e5e2e3f4e35ac2cb51b77614cec09ee47a3997f`

This page separates a valid package from a published and discoverable release.
Public source and direct installation do not imply that a marketplace or the
skills.sh search index has ingested the same revision.

## Release evidence

| Requirement | Evidence | State |
| --- | --- | --- |
| Four Agent Skills packages | `npx skills add . --list` also discovers the new `claude-to-codex-coordinator` adapter | Pass locally |
| Codex-compatible metadata | Every skill has matching frontmatter and `agents/openai.yaml`; `scripts/verify_launch.py` checks explicit `$skill-name` prompts | Pass |
| Portable behavior | Unit tests cover classification, lifecycle envelopes, privacy, usage-signal eligibility, and stop semantics | Pass |
| Python runtime range | CI tests Python 3.9 and 3.12; the image-redaction dependency is pinned to the newest Pillow line that retains Python 3.9 support | Pass |
| Codex package installation | Isolated `skills` CLI rehearsal copies all four skills and supporting files for the `codex` agent | Pass locally |
| Multi-agent package installation | The same rehearsal targets Claude Code, Cursor, GitHub Copilot, Goose, and OpenHands | Pass |
| Claude plugin package | `claude plugin validate --strict .` accepts the local repository; Claude Code `2.1.218` loaded `/codex-to-claude-coordinator:coordination-core` and returned the exact fixture result even with all tools disabled | Pass |
| Official Claude-to-Codex runtime | Claude Code `2.1.218` installed `codex@openai-codex` `1.0.6`; `/codex:setup` reported ready with the optional review gate disabled | Pass on this machine |
| Claude-to-Codex delegation | A fresh, read-only `/codex:rescue --wait --fresh` task returned the expected active-repository heading through Codex app server without changing files | Pass on this machine |
| Codex runtime invocation | Fresh Codex CLI `0.146.0-alpha.3` with GPT-5.6 Sol loaded the isolated `$coordination-core` install both explicitly and from an implicit description match, ran its classifier at low or no reasoning effort, and returned schema-conforming output under a read-only sandbox | Pass |
| goose runtime invocation | goose `1.37.0` listed all three skills from the isolated install; interactive `/skills coordination-core` loaded the skill, reference, script, and schema and returned the expected fixture classification | Pass with invocation caveat |
| Public repository contents | Public `main` contains the 0.1 payload introduced at `7e5e2e3`; remote `skills --list` discovers the original three skills, not the local 0.2 adapter | Publication pending for 0.2 |
| skills.sh package pages and direct install | The repository and all three skill pages resolve; telemetry-enabled multi-skill and one-skill remote installs succeed; all three registry audit providers return safe or low-risk results | Pass |
| skills.sh CLI search | Owner-scoped, exact-name, and broad searches still return no matching `wildcard` skill even though the canonical pages resolve | Pending registry search index |
| Project Claude marketplace install | Claude Code `2.1.218` registered the local checkout as a user marketplace, installed the `0.2.0` plugin with all four skills, and a fresh tool-disabled process invoked the namespaced reverse adapter successfully | Pass locally; public 0.2 publication pending |

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

The local `0.2.0` marketplace install also exposed
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
npx skills add wildcard/codex-to-claude-coordinator --list
```

Pass only when the searches return the expected repository and the remote list
contains the expected published skills. Until the 0.2 candidate is separately
approved and pushed, describe the public package as the three-skill 0.1 release
and the reverse adapter as locally validated only.

## External-action boundary

Committing, pushing, tagging, publishing, adding a marketplace, and performing
an indexing install are separate actions. The public push and indexing installs
recorded above were explicitly authorized; future external actions still require
explicit human authorization.
