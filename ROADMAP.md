# TOP roadmap v1

> Working document. Edited frequently. The single place where future TOP work is tracked.
> Last touched 2026-05-10.

This roadmap captures what is in flight now, what is queued behind it, and the items that need to land before TOP graduates from strawman to a stable v1 release.

## Where we are (2026-05-10)

**TOP Core landed.** The foundation has consolidated into a clean three-layer architecture:

- **L0 — Root (`top:CommonEntity`).** Carries Universal DNA: `top:identifier`, `top:observedAt`, `top:status`. Three properties practitioners universally encounter (*what is this thing, when was it captured, is it current*). Per ADR-0013 (practitioner-first).
- **L1 — Eight categories.** `top:Agent`, `top:Location`, `top:Resource`, `top:Scope`, `top:Temporal`, `top:Evidence`, `top:Outcome`, `top:Constraint`. Each `rdfs:subClassOf top:CommonEntity` plus class-level PROV-O alignment (`prov:Agent` / `prov:Activity` / `prov:Entity` / `prov:Plan` / `prov:Location`). Four carry light-edge BFO alignment (Agent → IndependentContinuant, Location → Site, Temporal → Process, Evidence → GenericallyDependentContinuant) for OBO interop.
- **L2 — Twenty-eight leaves.** Person, Organization, Group, AutonomousAgent (Agent); Physical, Virtual, Storage (Location); System, Equipment, Material (Resource); Portfolio, Program, Project (Scope); Schedule, Window, Activity, Milestone (Temporal); Document, Log, Attestation, Credential (Evidence); Observation, StatusChange, Artifact, Conclusion (Outcome); PhysicalLimit, RegulatoryLaw, SafetyGuardrail (Constraint).

Authoritative sources:
- [`taxonomy/taxonomy.ttl`](taxonomy/taxonomy.ttl) — pure SKOS view, TermBoard-clean (PoolParty / Synaptica / Protégé all load it).
- [`core/v1/shapes.ttl`](core/v1/shapes.ttl) — OWL/SHACL view: same URIs as the SKOS, expressed as `owl:Class` with `rdfs:subClassOf` chains, plus the 24 category-level relational extensions and the SHACL `top:UniversalDNAShape`.
- [`core/v1/walkthroughs/person.ttl`](core/v1/walkthroughs/person.ttl) — concrete walkthrough, validates clean against `pyshacl --advanced`.
- [`core/v1/index.html`](core/v1/index.html) — public spec page.
- [`taxonomy/taxonomy.csv`](taxonomy/taxonomy.csv) — flat companion for spreadsheet review.

The architectural decisions are documented in [`governance/decision-log.md`](governance/decision-log.md) — ADR-0012 (three-level architecture), ADR-0013 (practitioner-first; Universal DNA trim from 7 → 3), ADR-0014 (rename Primitives → Core, single namespace, drop `/onto/`).

## What ships next, in order

**Clinical-research workflow extension rebuilt against Core.** The legacy `reference-graphs/clinical-trials/` work (Sponsor, Study, Site, Participant, Recruit, Visit, OversightBody, InvestigationalProduct, Event lifted across PRs #1–#14) was authored before Core landed. The rebuild migrates those concepts into `clinical-research/` as workflow specializations: each clinical-research class declares `rdfs:subClassOf` against the appropriate Core leaf (e.g., a clinical-research Investigator is `rdfs:subClassOf top:Person`; a clinical-research Protocol is `rdfs:subClassOf top:Document`; a clinical-research Visit is `rdfs:subClassOf top:Activity`). Universal DNA, the category's relational extensions, and the PROV-O / BFO alignment all flow through automatically. The translator scaffold under `tools/` either follows the migration or is retired in favor of direct OWL/SHACL authoring; that decision rides with the rebuild.

**TermBoard curation pass.** The SKOS file imports clean now; the curation pass refines definitions, alt-labels, scope notes, and concept relationships against the live tooling. No code changes; the curation produces a v1.x SKOS file that the workflow rebuilds consume.

**Care-delivery workflow extension** (`care-delivery/`). Every sponsored hospital trial uses both clinical-research and care-delivery workflows over the same Person / Organization / Site / Visit foundation — the smart-hospital-sponsoring-a-trial test from ADR-0004 forced this design. Care-delivery is the natural second workflow because the composition cost lands immediately; the rebuild verifies the L0 → L1 → L2 inheritance chain holds across two workflows.

**Manufacturing workflow extension** (`manufacturing/`). Pharmaceutical CMC, batch records, and IP-supply chains. Anchored on `top:Material` and `top:Artifact` leaves; pulls the Constraint category for batch-release rules.

**Supply-chain workflow extension** (`supply-chain/`). Cold-chain monitoring, custody handoffs, deliveries. Anchored on `top:Material`, `top:Storage`, and `top:Activity`.

**PROV-O domain provenance properties** (per workflow). `prov:wasAttributedTo`, `prov:wasGeneratedBy`, `prov:wasAssociatedWith` attached at the workflow level with proper PROV-O domain semantics. TOP Core does not invent record-level vs. domain-level provenance shortcuts (per ADR-0013); workflows that need PROV-O domain provenance use it directly.

**Sub-object refinements** as workflow-specific operator vocabulary deepens. ReviewDecision under OversightBody (within clinical-research), ActivityTemplate under Schedule (within clinical-research and manufacturing), AuditTrailEntry as a Log specialization. Each refinement is a small additive PR within its workflow.

## OBO Foundry alignment

OBO Foundry covers the biomedical-knowledge layer (genes, phenotypes, anatomy, chemistry). TOP covers the operator layer (workflow, sponsorship, sites, visits, audit trail). The two are complementary.

The four BFO-clean L1 categories (Agent, Location, Temporal, Evidence) carry `rdfs:subClassOf bfo:*` directly in `core/v1/shapes.ttl`, so OBO-aligned reasoners pick up TOP entities as BFO-classified continuants and processes without bridging adapters. The other four categories (Resource, Scope, Outcome, Constraint) are mixed-membership at the category level; their leaves declare BFO type if and when OBO interop demands it.

Direct entity-level cross-walks to UBERON, CHEBI, GO, DOID land at the workflow-extension layer where the biomedical leaves live, not in TOP Core.

## Tooling alignments

Three community-standard infrastructure pieces TOP should adopt rather than reinvent:

- **SSSOM (Simple Standard for Sharing Ontological Mappings).** When TOP publishes its workflow-extension cross-walks (FHIR, USDM, OMOP, OBO) as machine-readable mapping artifacts, they should be SSSOM-formatted. Aligns TOP with the OBO Foundry / Mondo / Bioregistry tooling ecosystem.
- **Bioregistry** ([bioregistry.io](https://bioregistry.io)). TOP's namespaces (`top:`, future workflow prefixes) should be registered there as TOP graduates to public release.
- **Schema-level SKOS for enums.** Selected enums (severity scales, status enums, document types) can be promoted to SKOS concept schemes with `broader` / `narrower` relationships, allowing transitive ancestry queries without pre-computed-table approaches.

## Reference architecture for role-specific projections and views

The core taxonomy and the workflow extensions define what entities exist, how they relate, and what invariants must hold. They do not define how a given role consumes those entities for a given job. A Sponsor PM looking at Study X cares about a different projection than a Regulator looking at Study X. Both project from the same underlying graph, but the operationally useful view is different.

What this item builds, when the project gets to it:

A reference-architecture artifact identifying personas, roles, and jobs-to-be-done for the workflow extensions. Common projections per role defined as named query templates rather than ad hoc examples. A "Sponsor PM Daily View" projects the active Projects, the open Constraints, and the upcoming Milestones for a given Organization. An "Investigator Today View" projects the Activities scheduled at a Location for the current day plus the open Outcomes pending review. These projections get formal names and live as separate artifacts so they can evolve independently of the core taxonomy.

Reference patterns live next to TOP in the same repository (a future `reference-patterns/` directory), evolving through community contribution without requiring Core to change.

## Pointers

- [`README.md`](README.md) — project landing page.
- [`TAXONOMY.md`](TAXONOMY.md) — prose narrative of the three-layer taxonomy.
- [`taxonomy/taxonomy.ttl`](taxonomy/taxonomy.ttl) — SKOS view (system of record for vocabulary).
- [`core/v1/shapes.ttl`](core/v1/shapes.ttl) — OWL classes + SHACL contract.
- [`core/v1/index.html`](core/v1/index.html) — public spec page.
- [`core/v1/walkthroughs/person.ttl`](core/v1/walkthroughs/person.ttl) — concrete walkthrough.
- [`FIRST-PRINCIPLES.md`](FIRST-PRINCIPLES.md) — design rules.
- [`MANIFESTO.html`](MANIFESTO.html) — manifesto, signatories pending.
- [`governance/decision-log.md`](governance/decision-log.md) — architectural decision log (ADRs 1–14).
- [`reference-graphs/clinical-trials/`](reference-graphs/clinical-trials/) — pre-Core groundwork; being migrated into `clinical-research/`.
- [`clinical-research/`](clinical-research/) — clinical-research workflow extension; rebuild in flight.
