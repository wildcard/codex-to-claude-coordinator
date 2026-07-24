# Claude advisor protocol

Claude is an advisor and experimental harness for this project. Its output is input to review, not canonical truth.

## Before an advisory session

1. Inspect current model usage.
2. Apply the user model policy and record the choice.
3. Create or reuse a session scoped only to this repository.
4. State whether Claude may read, edit, run commands, browse, commit, or publish.
5. Provide the research question and required evidence format.

## Advisory prompt contract

Ask Claude to:

- distinguish official documentation, local observation, inference, and unknowns;
- link first-party sources;
- avoid unrelated history and private context;
- identify falsifiable experiments;
- challenge hardcoded product assumptions;
- avoid editing or external actions unless explicitly requested.

## After the response

1. Independently open the most important sources.
2. Reject claims whose product names or APIs cannot be verified.
3. Convert accepted claims into dated research notes.
4. Turn important uncertainties into reproducible experiments.
5. Record the model, visible usage basis, and session scope.

## Model-policy warning

Model names and usage meters change. The advisor should review whether Fable, Opus, and Sonnet remain available, whether usage means consumed or remaining quota, and whether each meter is model-specific or plan-wide. If any field is ambiguous, the coordinator must not infer eligibility.
