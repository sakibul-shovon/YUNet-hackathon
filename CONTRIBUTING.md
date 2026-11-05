# Contributing to Ebarki

Start with [local setup](docs/engineering/LOCAL_DEVELOPMENT.md), [architecture](docs/engineering/ARCHITECTURE.md) and [current limitations](docs/qa/CURRENT_STATUS.md). Internal package names retain ClaimCraft BD; the public product is Ebarki.

## Propose a focused change

Describe the user problem, expected behavior and a minimal fictional example. Use the [issue tracker](https://github.com/sakibul-shovon/YUNet-hackathon/issues) for ordinary bugs. Follow [SECURITY.md](SECURITY.md) for vulnerabilities; never attach real consumer records or credentials.

Before editing, read the applicable `AGENTS.md`, `.agent/state.json` and `.agent/handoff.md`. Query the knowledge graph before broad code searches:

```sh
python scripts/tasks.py graphify query "Which services own the behavior I am changing?"
```

Keep changes modular. Preserve ownership boundaries, source provenance, uncertainty and consent. Do not invent provider results, statutory citations, official submissions, approvals or recovery metrics. Synthetic fixtures must be identifiable as such.

## Validate what changed

```sh
python scripts/tasks.py check --scope foundation
python scripts/tasks.py check --scope core
```

Use focused tests when appropriate; report actual commands, results and remaining gaps. If the API/schema changes, update contracts and any migration/ADR required by the repository workflow. For structural changes, refresh the graph through the task runner.

Update the relevant feature/setup/provider documentation and [current status](docs/qa/CURRENT_STATUS.md). Keep intended roadmap behavior distinct from observed results. Documentation changes should have working relative links, meaningful image alt text and screenshots containing only fictional data.

## Review handoff

Explain the trigger, resulting behavior, evidence and risks in the PR. Do not present an unverified release as ready. AI-assisted changes remain the contributor's responsibility; disclose material external code, assets and tools.

There is no repository-wide license selected in this tree. Do not add or assume a blanket license without an explicit owner decision. Contributor coordination and acceptance are subject to the maintainer's review.

Follow the maintainer's latest commit/push authorization. The submission documentation and video-production cleanup were explicitly authorized for a GitHub push; later tasks must respect any newer approval constraints.
