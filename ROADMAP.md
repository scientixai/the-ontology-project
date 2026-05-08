# TOP roadmap v1

> Working document. Edited frequently. Not a public artifact yet.
> Last touched 2026-05-07.

This roadmap captures the work that is queued behind the core ontology effort, the decisions that have been made about how that work is staged, and the items that need to land before TOP moves out of `CLAUDE OUTPUTS/` into `github.com/scientixai/the-ontology-project` under Apache 2.0. It supplements the per-spec open-issues tables (currently only on the Sponsor spec) and becomes the single place where future work is tracked once we have more than one finished top-level.

## Where we are (2026-05-07)

The clinical-trials reference graph is the first reference graph being built on TOP. The OOUX hierarchy is locked at eight top-levels: Sponsor, Study, Site, Participant, Visit, Investigational Product, Oversight Body, Event. All seven OOUX boundary decisions are resolved (see `top_ooux-hierarchy_v1.html`). The Sponsor object is fully sealed at v0.1.4-strawman with eight verification questions answered, four SHACL-SPARQL domain invariants encoded (one soft warning, three hard violations), one worked example validating clean against pyshacl, and a complete spec document (`top_sponsor-spec_v1.html`) carrying the architectural decisions, stress tests, query patterns, NLP-to-NGSI-LD translation, SHACL invariants, cross-walks, and tracked open issues. The translator scaffold (`top_translator-scaffold_v1/`) emits clean JSON-LD `@context` and SHACL Turtle from a single source intermediate, with stdlib-only Python and no pip installs required for the basic pipeline.

The Sponsor spec is the template for the remaining seven top-levels. The pattern that earned its keep: TL;DR + model summary + architectural decisions + stress-test scenarios + query patterns by persona + NLP-to-NGSI-LD translation + SHACL invariants + cross-walks + tracked open issues. The translator scaffold's pre-emission guards (polysemous-verb detection, target-missing minCount relaxation, target-missing class-constraint suppression) catch entire classes of model errors before they ship.

## What ships next, in order

**Site as the second complete top-level spec.** Site is partially scaffolded in the source intermediate already (three attributes, five relationships). Lifting Site to full spec discipline forces a confrontation with the parked System work (the three-layer ownership-versus-use pattern from the eTMF insight) and gives us a second data point on whether the Sponsor spec template scales. Site lifting also pulls the partOfSiteNetwork SMO pattern into focus and exercises the `Organization → managesSite` inverse.

**Study as the third top-level spec.** Study is the natural follow-on because of the cross-cutting impact: every other top-level relates to Study somehow. Study lifting brings in the System horizontal (the `usesEtmfSystem`, `usesEdcSystem`, etc. split predicates from the eTMF discussion), the Protocol and Arm sub-objects (already partially scaffolded), and the Schedule of Assessments structure that anchors Visit timing.

**Visit, with the Visit Observation sub-object.** Visit Observation is the OOUX sub-object that landed under Visit during the Other Clinical Event boundary decision (Path C). Its specification needs the `derivedFrom` relationship that links it forward to a categorized Other Clinical Event when a CRA escalates.

**Event, with Other Clinical Event and the eventCategory enum.** The single-container Event holds AE, SAE, Deviation, Discrepancy, Safety Signal, Safety Report, and Other Clinical Event. The eventCategory enum carries the discrimination. The reportability handoff workflow (Visit Observation → Other Clinical Event via `derivedFrom`) is the operational tie between Visit and Event.

**Participant, Investigational Product, Oversight Body, in any reasonable order.** Participant is anchored by Visit (Visit hasParticipant) so it benefits from Visit being lifted first. IP is referenced by Sponsor's `supplies` relationship and by Visit Activity (the IP-administration step). Oversight Body is the IRB / EC / DSMB / IDMC top-level that Sponsor's `interfacesWith` relationship targets.

**Horizontal completions in parallel.** The horizontals that Sponsor and Site already reference are Organization (locked) and Document (minimal). The flagged-missing horizontals that Sponsor relationships point at need full specs: System (with vendor, productName, instanceId, baseUrl, systemType), RegulatoryAuthority, CRO, Country, Publication, SOP, TrainingProgram, DataTransferAgreement. These can lift in parallel with the top-levels rather than serially.

## Roadmap item: reference architecture for role-specific projections and views

This is the item Bo asked to be tracked separately, captured here as a placeholder until the core objects are done. The substance:

The core ontology defines what entities exist, how they relate, and what invariants must hold. It does not define how a given role consumes those entities for a given job. A Sponsor PM looking at Study X cares about a different projection than a Regulator looking at Study X. Both project from the same underlying graph, but the operationally useful view is different. Today these projections are sketched ad hoc in the spec's query-patterns section (`§5` of the Sponsor spec). That works for documentation. It does not work as a contract for downstream tooling.

What this roadmap item builds, when we get to it:

A reference-architecture artifact that identifies personas, roles, and jobs-to-be-done for each top-level entity. The Sponsor spec's six-perspective query patterns (site, patient, regulator, SMO, sponsor portfolio analyst, compliance officer) are a starting point but need to be made systematic across all eight top-levels. The output is a matrix: top-level entity × persona × job-to-be-done × the projection that serves it.

Common projections per role, defined as named query templates rather than ad hoc query examples. A "Sponsor PM Daily View" projects the active Studies, the open Action Items, and the upcoming Milestones for a given Sponsor entity. An "Investigator Today View" projects the visits scheduled at a Site for the current day plus the open queries on those visits. These projections get formal names and live as separate artifacts (markdown files, wiki pages) so they can evolve independently of the core ontology. The core ontology references them; it does not own them.

Reference patterns documented as separate, community-contributable artifacts. The core ontology stays compact and load-bearing. Reference patterns live next to it in the same repository (under `reference-patterns/` or similar), but evolve through community contribution without requiring the core to change. This honors the federation pattern at the documentation layer the same way the prefix architecture honors it at the schema layer: the core stays narrow, the periphery stays open.

The benefits Bo wants this to deliver: reduced maintenance burden on the core ontology because role-specific work does not bleed into the schema; increased flexibility for adopters because they can layer their own projections on top of the core without forking the schema; community-driven evolution of patterns and best practices without needing a central catalog to register with.

The next steps Bo wants sequenced: solidify all eight top-level entities first (currently in progress); then create a `reference-patterns/` placeholder; then schedule a separate effort to define personas, roles, and jobs-to-be-done; then invite community contributions through whatever governance shape TOP has by then (working group, GitHub PR review, RFC process).

This is a v0.3 or later effort. It does not block v0.1 of the clinical-research reference graph. It does shape how v0.2 packages the v0.1 work for community consumption, so it lands before the public Apache 2.0 publish.

## Tracked roadmap items, by category

### Translator scaffold improvements

The current `tools/build_shacl.py` and `tools/build_context.py` are stdlib-only and emit clean artifacts from the source intermediate. Three improvements queued behind the spec work.

A structured `invariants` field on each class in the source intermediate, replacing the hardcoded domain invariants in `build_shacl.py`. Today `emit_domain_invariants` carries four hand-maintained SHACL-SPARQL constraints for the Sponsor and Study classes. v0.2 of the strawman will define an `invariants` field on each class with a vocabulary of constraint types (implication, forall, exists, count, temporal-coverage), and the emitter will materialize them mechanically. This pulls domain knowledge out of the build script and back into the source where domain experts can edit it.

A docx-to-JSON extractor that parses the OOUX map directly. Today the source intermediate is hand-written from the v0.2 OOUX map; the docx is the source of truth and humans transcribe. The extractor reads `Section 3` of the OOUX map and emits the JSON intermediate directly, eliminating the transcription error class. This is Phase 1 work owned by the OOUX-map-to-source-intermediate pipeline, called out in the scaffold README.

A round-trip validator using pyld that reads an entity instance, projects it through the @context, and confirms every property is bound. Catches the "we emitted a context term but the instance uses a different name" class of error. Will require the first pip install in the repo (pyld), so we hold it until the unzip-and-run promise is no longer foundational.

### Source intermediate hygiene

Versioning every emitted `@context` and SHACL artifact with the source version and a git commit hash. Hooked in once the repo moves out of `CLAUDE OUTPUTS/` into the public GitHub repo.

A SHACL temporal coverage continuity invariant: no gaps in Sponsor coverage across handoffs. The Sponsor at `validUntil = T1` should be succeeded by a Sponsor with `validFrom = T1` on the same Study. Optional, low priority. Translator scaffold v3.

### Outreach and validation

USDM `parentOrganization` equivalent verification with the CDISC USDM working group. Confirms that the Organization horizontal's hierarchy field aligns with what USDM v3 actually exposes. Outreach pending.

Founding signatories on the manifesto: invitations queued. Practitioners across OOUX, FIWARE / NGSI-LD, knowledge graphs, ontology pedagogy, and semantic technology will be approached individually once the v0.1 release of the clinical-trials reference graph is in stable shape and the manifesto has settled. Each invitation is its own conversation; signatories are named in the manifesto as they accept.

### Federation expansion

The clinical-trials reference graph at `top:` is the first. The TOP commons at `topc:` carries cross-cutting horizontals shared across every industry graph. Future graphs each get their own prefix and their own context, and import the same commons.

Candidate next reference graphs, in no particular order: clinical CMC (`topcmc:`); drug discovery (`topdd:`); energy and process industries (`topenergy:`, analogous to ISO 15926 and CFIHOS); manufacturing (`topmfg:`); cell therapy (`topct:`, with Sample and Supply/Logistics elevated); rare disease (`toprd:`, with Participant elevated). Each domain working group converges first; the schema follows. The pattern is the same: hand-write a strawman intermediate, run the same `build_context.py` and `build_shacl.py`, ship the artifacts.

### Governance and community

Working group formation for the clinical-trials reference graph. Founding signatories on the v0.2 manifesto, once their invitations are accepted and they are named there, shape the working-group charter when it spins up.

Apache 2.0 publish on `github.com/scientixai/the-ontology-project`. Today the work lives in `CLAUDE OUTPUTS/` for incubation. The move to public GitHub happens once v0.1 of the clinical-trials reference graph is locked across all eight top-levels.

Contributor onboarding documents and an RFC process for amendments, both written before the GitHub publish so first-day contributors have a path in.

A docs site (likely Docusaurus or similar) generated from the spec HTMLs, the README, and the roadmap, hosted at `top.scientix.ai/docs` once Scientix.ai Inc has the domain configured.

## Pointers

- [`MANIFESTO.html`](MANIFESTO.html) — v0.2 manifesto, signatories pending.
- [`reference-graphs/clinical-trials/docs/ooux-hierarchy.html`](reference-graphs/clinical-trials/docs/ooux-hierarchy.html) — eight top-levels, all seven boundary decisions resolved.
- [`reference-graphs/clinical-trials/docs/sponsor-spec.html`](reference-graphs/clinical-trials/docs/sponsor-spec.html) — first complete top-level spec, template for the remaining seven.
- [`tools/`](tools/) — translator scaffold (build_context.py, build_shacl.py).
- [`reference-graphs/clinical-trials/source/top-strawman.json`](reference-graphs/clinical-trials/source/top-strawman.json) — source intermediate.
- [`reference-graphs/clinical-trials/examples/sponsor-pfizer-iqvia.ttl`](reference-graphs/clinical-trials/examples/sponsor-pfizer-iqvia.ttl) — worked example.

## How this document evolves

The roadmap is edited in place. New items get appended to the relevant category. Closed items get crossed out (`~~strikethrough~~`) rather than deleted, so the historical record stays visible. Major shifts (a new reference graph entering the queue, a working group spinning up, a phase boundary crossing) get a header bump.

Once TOP moves into the public GitHub repo, this file becomes `ROADMAP.md` at the repo root and starts taking community contributions through PR review.
