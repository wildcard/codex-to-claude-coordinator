# Launch readiness

Status: local release candidate; publication not authorized
Last checked: 2026-07-23
Published baseline: `bb0cfec535712abe2f0b4b747a1941f04540df12`

This page separates a valid package from a published and discoverable release.
Local success does not imply that the public repository, a marketplace, or
skills.sh contains the release candidate.

## Release evidence

| Requirement | Evidence | State |
| --- | --- | --- |
| Three Agent Skills packages | `npx skills add . --list` discovers `coordination-core`, `coordination-conformance`, and `codex-to-claude-coordinator` | Pass |
| Codex-compatible metadata | Every skill has matching frontmatter and `agents/openai.yaml`; `scripts/verify_launch.py` checks explicit `$skill-name` prompts | Pass |
| Portable behavior | Unit tests cover classification, lifecycle envelopes, privacy, usage-signal eligibility, and stop semantics | Pass |
| Python runtime range | CI tests Python 3.9 and 3.12; the image-redaction dependency is pinned to the newest Pillow line that retains Python 3.9 support | Pass |
| Codex package installation | Isolated `skills` CLI rehearsal copies all three skills and supporting files for the `codex` agent | Pass |
| Multi-agent package installation | The same rehearsal targets Claude Code, Cursor, GitHub Copilot, Goose, and OpenHands | Pass |
| Claude plugin package | `claude plugin validate --strict .` accepts the local repository; Claude Code `2.1.218` loaded `/codex-to-claude-coordinator:coordination-core` and returned the exact fixture result even with all tools disabled | Pass |
| Codex runtime invocation | Fresh Codex CLI `0.146.0-alpha.3` with GPT-5.6 Sol loaded the isolated `$coordination-core` install both explicitly and from an implicit description match, ran its classifier at low or no reasoning effort, and returned schema-conforming output under a read-only sandbox | Pass |
| goose runtime invocation | goose `1.37.0` listed all three skills from the isolated install; interactive `/skills coordination-core` loaded the skill, reference, script, and schema and returned the expected fixture classification | Pass with invocation caveat |
| Public repository contents | `wildcard/codex-to-claude-coordinator` still resolves to the published baseline, not this local release candidate | Blocked on approved publication |
| skills.sh discovery | Owner-scoped and broad searches return no matching `wildcard` skill | Blocked on approved publication and indexing |
| Claude marketplace install | Install the released plugin from its public marketplace source | Blocked on approved publication |

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

Pass only when the JSON inventory contains all three skill names and every
selected harness root contains each copied skill. Codex, Cursor, and GitHub
Copilot share `.agents/skills`; Claude Code, Goose, and OpenHands use their own
roots. The CLI's `agents` labels describe harnesses detected on the current
host, so a headless Linux runner may omit universal-root labels even after an
explicit successful install. The verifier still requires the distinct-root
labels for Claude Code, Goose, and OpenHands. Inspect the copied roots and
supporting files, not universal-root display labels or only the CLI summary.

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
telemetry. Therefore launch requires an approved public update followed by at
least one ordinary remote install with telemetry enabled. Then run:

```sh
npx skills find "codex claude coordinator"
npx skills find coordinator --owner wildcard
npx skills add wildcard/codex-to-claude-coordinator --list
```

Pass only when the searches return the expected repository and the remote list
contains all three current skills. Until then, describe the project as locally
validated but not externally discoverable.

## External-action boundary

Committing, pushing, tagging, publishing, adding a marketplace, and performing
the indexing install are separate actions. None is implied by a green local
gate. They require explicit human authorization.
