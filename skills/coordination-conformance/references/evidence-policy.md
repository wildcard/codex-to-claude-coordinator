# Evidence policy

## Accepted provenance

Every record declares one class:

- `official-doc`: a first-party source;
- `observed`: reproduced product behavior with local evidence;
- `advisor`: an agent recommendation awaiting verification;
- `inference`: reasoning derived from evidence;
- `unknown`: explicitly unverified.

Product summaries and advisor prose do not substitute for transcripts,
artifacts, state transitions, or exact usage labels.

## Privacy boundary

Use only generic fixtures. Exclude credentials, personal content, account
identifiers, repository remotes, unrelated project paths, and cross-project
transcripts.

Screenshots, transcripts, and logs must be redacted derivatives. The redactor
removes common email, home-path, and secret patterns from text. For images,
provide opaque rectangles that cover every private region. Inspect the
derivative manually because no local OCR guarantee exists.

Evidence paths must be relative to the run root. The validator rejects absolute
paths, `..` traversal, hash mismatches, missing files, and common private-value
patterns.

## Capability disposition

Use these statuses independently per adapter operation:

- `pass`: the exact behavior was observed and met its criterion;
- `fail`: it was attempted and violated the criterion;
- `unavailable`: the tested surface explicitly lacked the capability;
- `not_tested`: the run deliberately omitted it;
- `unknown`: there is no adequate observation.

An absent UI control is `unknown` until the protocol established that the
surface was complete enough to call it unavailable.

## Threshold signals

Threshold automation requires all of:

- explicit named-model scope;
- explicit consumed direction;
- an exact displayed percentage;
- visible reset or window semantics;
- known freshness;
- redacted evidence.

A plan, weekly, context, token, or cost signal cannot be relabeled as
model-specific. Cross-surface agreement and response to bounded use remain
experiment-level requirements.

## Stop semantics

Archive, hide, detach, idle, or close are not stop evidence. A passing stop
observation requires an explicit stop or cancel action followed by a terminal
worker state.
