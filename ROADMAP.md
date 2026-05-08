# TOP roadmap v1

> Working document. Edited frequently. Not a public artifact yet.
> Last touched 2026-05-08.

This roadmap captures the work that is queued behind the core ontology effort, the decisions that have been made about how that work is staged, and the items that need to land before TOP moves out of `CLAUDE OUTPUTS/` into `github.com/scientixai/the-ontology-project` under Apache 2.0. It supplements the per-spec open-issues tables and becomes the single place where future work is tracked once we have more than one finished top-level.

## Where we are (2026-05-08)

The clinical-trials reference graph is the first reference graph being built on TOP. The OOUX hierarchy is locked at eight top-levels: Sponsor, Study, Site, Participant, Visit, Investigational Product, Oversight Body, Event. All seven OOUX boundary decisions are resolved (see `ooux-hierarchy.html`).

**Sponsor** is fully sealed at v0.1.4-strawman with eight verification questions answered, four SHACL-SPARQL domain invariants encoded (one soft warning, three hard violations), one worked example validating clean against pyshacl, and a complete spec document (`sponsor-spec.html`).

**Site** has lifted to v0.2.0-strawman as a combined Site + StudySite spec (`site-spec.html`, 977 lines) — 14 verification questions pending Bo's review. The Site lift forced an architectural correction (Bo's "Site is the most important object — that's where trials operate" framing and the corrected operational hierarchy `Site → StudySite → Study → Protocol → SOA → Visit → Activity`). Outcomes:

- **Site** (top-level) lifted from 3 attrs / 5 rels to 49 attrs / 10 rels with full SFQ feasibility coverage (therapeutic area experience, past trial experience, infrastructure, regulatory defaults, insurance, staff capacity).
- **StudySite** (new commons horizontal) lifted with 17 attrs / 18 rels as the per-Study operational pivot. Crosswalks to `usdm:StudySite` (verified against cdisc-org/usdm via WebFetch).
- **Person**, **System**, **Log**, **Equipment**, **StorageLocation**, **Credential** all lifted as commons horizontals to support the Site spec without flagged-missing placeholders. **Document** horizontal expanded with R3 Appendix C `essentialRecordPurpose` + `responsibleParty` enums.
- **System three-axis** decision: `operatedBy` / `usedBy` / `oversightHeldBy` schema-level role pattern. Original "visibility-as-projection" framing superseded by R3 Section 3.9 / 2.12 oversight-as-relationship grounding.
- **Equipment + System + Log triad** resolves the freezer-with-IoT-monitor case cleanly: physical Equipment under R3 qualification/calibration discipline; computerised System under R3 Section 4.3 validation/audit-trail discipline; Log captures the temporal trail.
- **IIT pattern** captured without special schema relationship: same Organization plays both `managesSite` and `playsSponsorRole`. SHACL invariant 9 carries the IIT exception.
- **6 new SHACL invariants** added (10 total: Sponsor 4 + Site/StudySite 4 + System 1 + Credential 1).
- **3 worked examples** authored, all conforming under pyshacl advanced mode: traditional AMC (MSKCC + Pfizer), SMO network (Elevate Research three sites), IIT (MSKCC self-sponsored).

The Site spec extends the Sponsor template with five site-specific sections: architectural anchor (operational hierarchy), R3 alignment (Sections 2/3/4/Appendix C/Annex 2), ISF alignment (legacy operational view, 23 sections mapped), lifecycle state machines (Site + StudySite separately), persona-to-Site-view matrix (10 roles), SFQ projection (named query template), and delegation matrix.

The Sponsor spec template + Site spec extensions form the pattern for the remaining six top-levels. The translator scaffold's pre-emission guards still hold: polysemous-verb detection, target-missing minCount relaxation, target-missing class-constraint suppression.

## What ships next, in order

**Study as the third top-level spec.** Study is the natural follow-on because of the cross-cutting impact: every other top-level relates to Study somehow. Study lifting brings the Protocol and Arm sub-objects (already partially scaffolded) to full spec discipline, anchors the Schedule of Assessments structure, and exercises the operational hierarchy from the Study side. Site and StudySite now resolved cleanly, so Study lifts without architectural ambiguity around the Site-Study boundary.

**Visit, with the Visit Observation sub-object.** Visit Observation is the OOUX sub-object that landed under Visit during the Other Clinical Event boundary decision (Path C). Its specification needs the `derivedFrom` relationship that links it forward to a categorized Other Clinical Event when a CRA escalates. **Tracked corrections to apply when Visit lifts**: the OOUX has Visit pointing directly at `1 Site`; should be `1 StudySite` (or split into Visit-template vs Visit-occurrence with the occurrence pointing at StudySite). The definition-side chain (Protocol → SOA → Visit-template → Activity) and operational-side chain (StudySite → Visit-occurrence → Activity-occurrence) meet at the Visit; the OOUX conflates them.

**Event, with Other Clinical Event and the eventCategory enum.** The single-container Event holds AE, SAE, Deviation, Discrepancy, Safety Signal, Safety Report, and Other Clinical Event. The eventCategory enum carries the discrimination. The reportability handoff workflow (Visit Observation → Other Clinical Event via `derivedFrom`) is the operational tie between Visit and Event.

**Participant, Investigational Product, Oversight Body, in any reasonable order.** Participant is anchored by StudySite (StudySite.hasParticipant) and Visit-occurrence so it benefits from Visit being lifted first. **Tracked correction**: the OOUX has Participant pointing directly at `1 Site`; should be `1 StudySite` (per the operational hierarchy). IP is referenced by Sponsor's `supplies` relationship and by Visit Activity (the IP-administration step). Oversight Body is the IRB / EC / DSMB / IDMC top-level that Sponsor's `interfacesWith` and StudySite's `hasIRB` relationships target.

**Horizontal completions in parallel.** Lifted as of v0.2.0: Organization, Document (R3 Appendix C-aligned), StudySite, Person, System (R3 Section 4.3-aligned), Log (with logType discriminator covering CommunicationLog), Equipment, StorageLocation, Credential. Still flagged-missing as of v0.2.0 (lifting in v0.3 or as their referencing top-level lifts): RegulatoryAuthority, Contract, MonitoringVisit, Audit, TrainingRecord, Enrollment, StudyStartupPackage, OversightBody, Visit, Participant, CRF, Sample, Shipment, Meeting, Publication, SOP, TrainingProgram, CRO, Country, DataTransferAgreement.

## Projections and the open substrate / commercial validated deployment split

A central architectural pattern of TOP: operator-grounded reference graphs are the source of truth; *projections* into adjacent standards (FHIR R5, USDM v3, CDISC SDTM/CDASH, **OMOP CDM v5.4**, ICH/GCP ISF, and others) are first-class artifacts emitted alongside the source intermediate. Each projection is declarative (SPARQL CONSTRUCT or equivalent), versioned with the source it derives from, and tested against worked examples. The pattern earns its keep on the OMOP target specifically: TOP-conformant operational data projects into OMOP CDM without the multi-month custom-ETL pipelines that today's "raw data → OMOP" architectures (e.g., the AWS reference architecture published December 2025) require. Schema mapping is declarative; value-level transformations (de-identification, date shifting, tokenization) remain the domain of established privacy-engineering vendors (Datavant, John Snow Labs) and integrate at the deployment layer.

**The open substrate / commercial validated deployment split.** TOP draws a clean line:

- **Open (Apache 2.0, in this repo):** the reference graphs, the cross-walk metadata at every entity, the architectural pattern of declarative projection, the source intermediate, the translator scaffold, reference / proof-of-concept projection examples. This is what federal grants fund and what the manifesto commits to.
- **Commercial (Scientix.ai product, separate from this repo):** GxP-validated, GAMP5 Cat 5-qualified, SOC 2 Type II-audited, HIPAA-BAA-covered, 21 CFR Part 11-compliant production-grade runtime that executes the open mappings against PHI in a regulated clinical-operations environment. Plus complete production-grade SPARQL CONSTRUCT mappings (performance-optimized, error-handled), the OMOP CDM loader and version-migration tooling (v5.4 → v6), Datavant / John Snow Labs integration connectors, monitoring, multi-tenant operation, customer support.

Schemas don't get validated; deployable systems do. The compliance burden is the moat. This is the same Red Hat / Elastic / MongoDB / HashiCorp open-core + commercial-services pattern that has historically sustained open-source-led infrastructure companies. It allows TOP to be maximally open at the substrate (manifesto-aligned, federation-friendly, grant-fundable) while preserving Scientix.ai's commercial value capture in the validated production layer.

## OBO Foundry alignment

OBO Foundry (Open Biological and Biomedical Ontology Foundry) is the convening precedent TOP emulates: 175+ community-governed biomedical ontologies, federated authoring, decades of NIH / academic / commercial investment, formal-logic-based semantic interoperability. The critical distinction: OBO Foundry is **research-shaped** (genes, phenotypes, anatomy, chemistry, organisms, diseases). TOP is **operator-shaped** (workflow, sponsorship, sites, visits, delegation, audit trail). The two stacks are complementary, not competing. Together they form a complete chain:

```
Operator-grounded ontology (TOP)            ← OPERATOR layer
    ↓ projects to
Observational data warehouse (OMOP CDM)     ← OBSERVATIONAL layer
    ↓ bridges via OMOP2OBO (Callahan et al. 2023, Apache 2.0)
Biomedical knowledge ontology (OBO Foundry) ← RESEARCH layer
```

**The OMOP2OBO bridge is built and public.** Callahan et al. published OMOP2OBO in npj Digital Medicine (May 2023; <https://github.com/callahantiff/OMOP2OBO>; PyPI `omop2obo`; Zenodo-archived mappings). It maps 92K SNOMED-CT conditions to HPO + Mondo, 8.6K RxNorm drug ingredients to ChEBI / NCBITaxon / PRO / VO, 10K LOINC measurements to HPO / Uberon / NCBITaxon / PRO / ChEBI / CL — covering 68–99% of concepts used across 24 hospital systems. **TOP does not need to do this work itself.** Once TOP→OMOP projection lands, TOP→OBO is a free transitive bridge through the OMOP2OBO mappings. This means TOP-grounded data immediately becomes available to HPO-based rare disease phenotyping, Mondo-based disease classification, ChEBI-based pharmacogenomic analysis, and the broader OBO Foundry-driven deep phenotyping ecosystem.

For TOP's own entity-level OBO cross-walks: deferred until top-levels with biological domain semantics lift. Site, Sponsor, StudySite, Person, Equipment, Document, Log, StorageLocation, Credential have no direct OBO equivalents (operator-side, not biological-side). Future Adverse Event, Sample (when it lifts to top-level in specialty graphs), Lab Result / Measurement, Diagnosis, IP active ingredient WILL get direct OBO cross-walks (HPO, Mondo, Uberon, CL, ChEBI, PRO) — discoverable through OMOP2OBO once those entities lift in v0.3+.

## Tooling alignments

Three community-standard infrastructure pieces TOP should adopt rather than reinvent:

- **SSSOM (Simple Standard for Sharing Ontological Mappings)** — the canonical format for ontology-to-ontology mappings. When TOP publishes its OMOP / FHIR / USDM / OBO cross-walks as machine-readable mapping artifacts, they should be SSSOM-formatted. Aligns TOP with the OBO Foundry / Mondo / Bioregistry tooling ecosystem; lets community contributors review and contribute mappings using already-known tooling. Tracked as a v0.3 deliverable.

- **Bioregistry** (<https://bioregistry.io>) — community-governed registry of prefixes and identifiers used across the biomedical-ontology ecosystem. TOP's prefixes (`top:`, `topc:`, future `topcmc:`, `topdh:`, etc.) should be registered there as TOP graduates from strawman to public release. Aligns identifier governance with OBO Foundry conventions. Tracked as a v0.2 publish-time deliverable.

- **OWL2 + SKOS for hierarchical concepts** — TOP's enums (siteType, equipmentClass, documentType, organizationType, essentialRecordPurpose) currently flat. Promoting selected enums to SKOS concept schemes with broader/narrower relationships allows transitive ancestry queries (the OMOP CONCEPT_ANCESTOR pattern) without OMOP's pre-computed-table approach. Tracked as a v0.3 enhancement.

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
