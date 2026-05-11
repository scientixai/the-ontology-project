# Contributing to The Ontology Project

Welcome. TOP is open community-governed infrastructure for high-consequence regulated industries, hosted under Apache 2.0. Contributions land through GitHub pull requests against `main`.

## Before you start

Read these in order. They take an hour combined and save you a week of misaligned work:

1. [`MANIFESTO.html`](MANIFESTO.html) — what TOP is for and why it exists.
2. [`FIRST-PRINCIPLES.md`](FIRST-PRINCIPLES.md) — the design rules every spec and PR can cite by name.
3. [`TAXONOMY.md`](TAXONOMY.md) — the three-layer architecture and how to read it.
4. [`governance/decision-log.md`](governance/decision-log.md) — the architectural decisions and the reasoning behind them. New contributors who try to undo an ADR get pointed at the relevant entry, not into a long discussion.
5. [`governance/working-groups.md`](governance/working-groups.md) — how working groups operate.
6. [`governance/rfcs/README.md`](governance/rfcs/README.md) — the RFC process for structural changes.

## What contribution looks like

### Routine changes — direct PR

You can open a PR directly for:

- Adding worked examples, tests, or validation cases under a workflow extension's directory.
- Fixing typos, broken links, formatting.
- Refining existing entity definitions, scope notes, alt-labels in your WG's taxonomy.
- Adding a new attribute to an existing entity *inside your WG's workflow* that doesn't ripple to Core.
- Spec doc additions, planning notes, cross-walk updates within a workflow.

These PRs need approval from at least one CODEOWNER for the affected directory.

### Structural changes — RFC first

File an [RFC](governance/rfcs/README.md) before opening a PR for:

- Anything that modifies `/core/` or `/taxonomy/`.
- Anything that crosses two or more workflow extensions.
- Defining a concept that belongs in Core (e.g., a Sample type used by both clinical-research and manufacturing).
- Forming or dissolving a working group.
- Changing URI / namespace conventions.
- Adopting or retiring a tooling / standards alignment.

The cost of an RFC is small (a markdown file, a PR, a review). The cost of an unraveled structural decision is large.

## Working group ownership

Per [`.github/CODEOWNERS`](.github/CODEOWNERS), every directory has owners. PRs touching a directory require approval from at least one of its owners. Cross-cutting PRs (touching Core plus a workflow, or two workflows) need approval from every affected owner.

If you don't see a working group for the domain you want to contribute to, the path forward is to propose one. File an RFC under [`governance/rfcs/`](governance/rfcs/) using the template. See [`governance/working-groups.md`](governance/working-groups.md) for the lifecycle.

While working groups are forming, the convener (Bo Lora, [@bo-lora](https://github.com/bo-lora)) is the review pool of one. As WGs activate, governance rotates to those groups.

## Pull request hygiene

- One topic per PR. If you find yourself touching two unrelated areas, split into two PRs.
- The PR description states the *why*, not the *what* — the diff already shows the *what*. The *why* is what reviewers need to evaluate.
- Cite the relevant ADR or RFC if your PR follows one.
- Run validators where they exist:
  - `python3 -m pyshacl --advanced -s core/v1/shapes.ttl -d <your-instance>.ttl` for any TTL you author against Core.
  - `python3 -c "from rdflib import Graph; Graph().parse('<your-file>.ttl')"` to catch Turtle syntax errors before review.
- Link to any external documents, standards, or prior art your change relies on.

## Quality discipline

TOP is built for high-consequence regulated environments. The discipline you'd expect in those environments applies here:

- **Operator vocabulary first.** Names come from the workday, not from the standards. See [FIRST-PRINCIPLES.md](FIRST-PRINCIPLES.md).
- **PROV-O alignment is class-level, not universal-level.** Per [ADR-0013](governance/decision-log.md#adr-0013-practitioner-first-tops-primary-customer).
- **Universal DNA is three properties, not seven.** `top:identifier`, `top:observedAt`, `top:status`. Don't add more.
- **Specializations declare `rdfs:subClassOf` against a Core leaf.** Don't mint parallel classes that duplicate Core shapes.
- **Decisions are append-only.** ADRs document what was decided and why. Superseding an ADR requires a new ADR; you don't quietly edit the old one.

## Conduct

Contributors and reviewers are expected to act with the seriousness this domain warrants. Disagreement happens; it gets worked through via the artifacts (RFCs, decision log, PR comments) rather than in side channels.

## Contact

- Project: [top.scientix.ai](https://top.scientix.ai)
- Repository: [scientixai/the-ontology-project](https://github.com/scientixai/the-ontology-project)
- Convener: [bolora.me](https://bolora.me)
