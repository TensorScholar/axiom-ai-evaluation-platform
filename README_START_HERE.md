# AXIOM Codex App Autopilot Pack v0.5

This pack is designed for the Codex macOS app workflow:

1. Open this folder as the project folder in Codex.
2. Give Codex the prompt from `START_PROMPT_FOR_CODEX.md`.
3. Codex should run the autonomous loop inside this folder.
4. Codex should implement one unlocked task at a time.
5. Codex must generate verification ledgers and task reports.
6. Codex must stop only when a stop condition is triggered or all unlocked work is complete.

## Important

This pack does not require you to run an external supervisor manually.

Instead, it uses:

- strict `AGENTS.md`,
- one-shot start prompt,
- task graph,
- task status file,
- internal verifier,
- protected file manifest,
- self-audit checklist,
- anti-fake-validation policy.

## Trust Model

This is the strongest setup possible if you only want to use the Codex app interactively with one initial prompt.

However, because Codex has write access to the folder, this cannot be as strong as an external verifier. To reduce risk, this pack marks protected files and requires Codex to compare them against checksums.
