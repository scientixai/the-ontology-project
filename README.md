<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="images/top-logo-inverse.svg">
    <img src="images/top-logo-readme.png" alt="The Ontology Project" width="420">
  </picture>
</p>

# The Ontology Project

> An open commons of reference knowledge graphs, governed by domain working groups, hosted under Apache 2.0.

The Ontology Project (TOP) is industry-agnostic infrastructure for building reference ontologies that downstream consumers actually use. TOP is NGSI-LD with JSON-LD as connective tissue. The first reference graph being built on TOP is for clinical research; CMC, drug discovery, energy and process industries, manufacturing, cell therapy, and rare disease are queued as separate working groups form.

If you are reading this in 2026 you are early. The clinical-research reference graph is shipping its first complete top-level (Sponsor) at v0.1.4-strawman and the second (Site) is queued. The translator scaffold is stdlib-only Python, no pip installs needed for the basic pipeline, unzip and run.

## What you will find here

- [`commons/`](commons/) — the `topc:` namespace, cross-cutting horizontals shared across every industry graph (Organization, Document, Person, Audit Trail Entry, Contract). One graph for all of HCLS, energy, manufacturing, and beyond.
- [`reference-graphs/clinical-trials/`](reference-graphs/clinical-trials/) — the `top:` namespace, the founding reference graph. Eight top-levels: Sponsor, Study, Site, Participant, Visit, Investigational Product, Oversight Body, Event.
- [`tools/`](tools/) — the translator scaffold. `build_context.py` emits the JSON-LD `@context`. `build_shacl.py` emits the SHACL Turtle shapes. Stdlib only.
- [`reference-patterns/`](reference-patterns/) — placeholder for role-specific projections and views (Sponsor PM Daily View, Investigator Today View, Regulator Audit View). Community-contributable. See [ROADMAP.md](ROADMAP.md) for the framework.
- [`governance/`](governance/) — working group structure, RFC process, release process, and the [architectural decision log](governance/decision-log.md). Where new contributors learn the rules.
- [`MANIFESTO.html`](MANIFESTO.html) — v0.2 manifesto with founding signatories.
- [`ROADMAP.md`](ROADMAP.md) — what ships next, what is queued behind it, how community contributions enter the project.

## Quickstart

Run the translator on the clinical-trials source intermediate. No pip installs needed for the basic pipeline.

```bash
python3 tools/build_context.py reference-graphs/clinical-trials/source/top-strawman.json reference-graphs/clinical-trials/contexts/clinical-trials-context.jsonld
python3 tools/build_shacl.py reference-graphs/clinical-trials/source/top-strawman.json reference-graphs/clinical-trials/shapes/clinical-trials-shapes.ttl
```

Validate the worked example against the SHACL shapes (requires pyshacl, which requires `pip install pyshacl rdflib`).

```bash
python3 -m pyshacl --advanced \
  -s reference-graphs/clinical-trials/shapes/clinical-trials-shapes.ttl \
  -d reference-graphs/clinical-trials/examples/sponsor-pfizer-iqvia.ttl
```

The `--advanced` flag enables SHACL-SPARQL constraint processing, which the v0.1.4 emitter relies on for the four domain invariants (one soft warning, three hard violations). Without `--advanced`, property-shape constraints still validate but the SHACL-SPARQL constraints are silently skipped.

Read the [Sponsor spec](reference-graphs/clinical-trials/docs/sponsor-spec.html) to see what a complete top-level looks like. The Sponsor object is the first finished spec and the template for the remaining seven.

## What problem this solves

Frontier AI is being deployed against healthcare and life sciences data faster than the data itself can be made trustworthy. Models hallucinate ("AI slop"). Provenance gets lost. Outputs get hand-waved as "good enough" by people who do not have to live with the consequences. The clinical lifecycle is one of the highest-stakes domains in this collision: a hallucinated dose, a misattributed adverse event, a missing audit trail can kill someone.

TOP is TOP for verifiable, source-grounded AI in regulated environments. The ontology defines what entities exist and how they relate. The SHACL shapes encode the structural invariants. The reference patterns define how each role consumes the graph for their specific job. Downstream tools (LLMs grounded in the graph, decision-support systems, regulatory analytics) project from the same source of truth and stay traceable.

The same TOP layer works outside HCLS. Energy and process industries (analogues to ISO 15926 and CFIHOS), manufacturing, defense supply chains, anywhere AI is being deployed against high-consequence data and provenance cannot be optional.

## How to contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for the working-group model, the RFC process, and per-domain ownership.

In short: every domain has a working group. The working group owns its reference graph's source intermediate. Amendments arrive as RFCs (markdown documents in `governance/rfcs/`), get reviewed by the working group, and merge through PR with at least one approving review from a working-group member. The commons (`topc:`) is governed jointly across working groups because changes affect every domain.

For now, while working groups are forming, Bo Lora as convener is the review pool of one. As working groups spin up, governance rotates to those groups, and founding signatories on the manifesto (named there as they accept the invitation) step into advisory roles.

## Releases

Each artifact in this repo carries its own semver: the commons (`topc:`), each reference graph (`top:`, future `topcmc:`, etc.), and the tools. Tagged GitHub releases include both the source intermediates and the emitted artifacts so consumers can pin a specific commons-plus-graph-plus-tools combination.

Current state:

- Commons (`topc:`) — embedded in the clinical-trials source intermediate at v0.1.4. Will split into its own source file once a second reference graph needs it.
- Clinical-trials reference graph (`top:`) — v0.1.4-strawman. Sponsor object complete; Site partial; Study minimal; Participant, Visit, IP, Oversight Body, Event not yet scaffolded.
- Tools — stdlib-only, no version tag yet. Versioning starts when the second domain begins consuming them.

## License

Apache License 2.0. See [LICENSE](LICENSE).

## Contact

The Ontology Project is convened by Bo Lora at Scientix.ai Inc.

- Project: [top.scientix.ai](https://top.scientix.ai)
- Manifesto: [MANIFESTO.html](MANIFESTO.html)
- Roadmap: [ROADMAP.md](ROADMAP.md)
- Convener: [bolora.me](https://bolora.me)

---

<p align="center">
  <a href="https://scientix.ai">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="images/sponsored-by-scientixai-inverse.svg">
      <img src="images/sponsored-readme.png" alt="Sponsored by Scientix.ai" width="240">
    </picture>
  </a>
</p>
