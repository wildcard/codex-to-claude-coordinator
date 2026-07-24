# Classification read-only fixture

This fixture checks whether a harness can discover and apply the unchanged
`coordination-core` skill. It contains no credentials, remotes, personal data,
or writes.

Ask the harness to load or invoke `coordination-core`, classify `input.json`
with the bundled `scripts/classify.py`, and return only the six fields in
`expected.json`.

Pass only when:

1. the harness identifies the installed skill rather than reconstructing its
   policy from the prompt;
2. the harness follows the self-contained version `0.1` rules and, when tools
   are available, can access the supporting reference and classifier;
3. the output exactly matches `expected.json`;
4. the harness makes no fixture or external-system writes.

Record skill discovery, explicit invocation, implicit invocation, tool
approval, and output validation separately. A copied folder or list entry is
not runtime invocation evidence.
