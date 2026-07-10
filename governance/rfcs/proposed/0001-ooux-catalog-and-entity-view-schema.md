# RFC 0001: the OOUX object catalog as the operator-facing lens, and the entity-view schema a generic viewer builds from

- **Status:** Proposed
- **Date:** 2026-07-10
- **Authors:** @scientixai (Clinical Research WG)
- **Affected groups:** Clinical Research WG, Core Stewards
- **Required quorum:** Core stewards + one Clinical Research WG maintainer
- **Supersedes:** n/a
- **ADR on acceptance:** ADR-0022

## Motivation

A recurring downstream need: a consumer wants to render **any** entity's page on the fly from the graph, with no hardcoded "Study Page" or "Document Page." A single generic entity viewer reads a node, identifies its type, pulls a schema, and generates the view; clicking a related entity shifts the central node rather than loading a different template. In the same pattern, lightweight applications are themselves entities whose sole purpose is an ephemeral projection that queries the graph at runtime (no ETL, no copy, context inherited by edge traversal).

The pivotal realization: a generic viewer and these projective apps both need **one schema to read**, and that schema is not a UI artifact — it is the ontology, expressed for the operator. The clinical-research OOUX (Object-Oriented UX) object catalog (v0.2) already carries that structure: its relationship lines are literal triples (`Study —conductedAt→ Site`, `Participant —enrolledIn→ Study`), and its four columns (Attributes, Metadata, Relationships, Calls to Action) are exactly the NGSI-LD shape its own reading guide names.

The risk this RFC addresses: the OOUX map (v0.2, 78 objects) and the model that already exists in `cr-domain` — `ontology/cr-core-*.ttl` classes, `views/operator-views.ttl`, `projections/*.rq` — will drift apart unless they are explicitly reconciled. Much of "how a generic viewer builds a page" is already implemented here; the OOUX map must map onto it, not land on top of it.

## Proposal

### 1. Adopt the OOUX v0.2 catalog as the operator-facing projection of `cr-domain`

The OOUX map is not a rival ontology. It is the operator-facing view of the same domain the `cr-core` modules already model, and it reconciles to TOP by the existing rule: **every object is `rdfs:subClassOf` a TOP leaf** (e.g. `cr:Study rdfs:subClassOf top:Scope` already ships). Its four columns map to the model as its reading guide states:

| OOUX column | Model home | Notes |
| --- | --- | --- |
| Attributes | NGSI-LD Properties on the `cr` class (literals, enums, structured records) | e.g. `studyStatus`, `enrollmentType`, `enrollmentCount` |
| Metadata | The PROV + bitemporal envelope (`conventions.md`): `createdAt`, `modifiedAt`, `providedBy`, `wasAttributedTo`, transaction/valid time | the provenance seam a consumer notarizes |
| Relationships | `cr` object properties — the triples — with cardinality | `conductedAt`, `enrols`, `records`, `sponsoredBy` |
| Calls to Action | Persona actions gated by role and entity state | not yet modeled in `cr-domain`; see §Proposal.3 |

### 2. Define the entity-view schema: four ontology-sourced layers

A generic viewer builds an entity page from four layers, each sourced from the ontology, not from UI code:

1. **Context / Identity** — the node's `@id` (stable), label/slug, and `status` (from the class's status enum, e.g. `studyStatus: PLANNED..ENROLLING..COMPLETED`). Universal DNA (identifier, observedAt, status) already guarantees the minimum.
2. **Core Record** — the class's Properties, rendered by type (string → text, enum → pill, date → timeline, `array<object>` → structured list). The class definition already carries these.
3. **Graph** — the entity's forward-linked neighbors, sourced from the SHACL retrieval views in `views/operator-views.ttl` and walked by `tools/ngsild_view.py`. Each `sh:NodeShape` already declares exactly which relationships a single `?join=inline` pull inlines and which leaf shape renders each neighbor. This *is* the graph-layer schema, already built and tooled. A viewer groups edges as upstream (parents: `sponsoredBy`, `governedBy`), downstream (children: `conductedAt`, `enrols`, `contains`), and peer/process (`executes`, `receives`).
4. **Action** — persona actions gated by role × entity state. This layer has no ontology home yet. This RFC proposes a lightweight, additive annotation (see §3) so the Action layer is also schema-driven.

Nothing in layers 1–3 is new construction; the RFC's contribution is naming this arrangement as a **contract** consumers depend on, and reconciling the OOUX catalog onto it.

### 3. Reconciliation table (worked set) and the CTA gap

A worked reconciliation for the first objects, to be extended to all 78 in follow-on WG work:

| OOUX object | TOP leaf | `cr` class | Operator view | Projections that read it |
| --- | --- | --- | --- | --- |
| Study | `top:Scope` | `cr:Study` (exists) | *propose `cr:StudyView`* | `usdm_study.rq`, `planned_vs_actual.rq`, `enrollment_as_of_cut.rq` |
| Participant (Subject) | `top:Agent` | `cr:StudySubject` (exists; `Participant` is the preferred label per ADR-0024, `subject` an altLabel) | `cr:SubjectLeaf` (exists) | `sdtm_dm.rq`, `analysis_population_membership.rq` |
| Enrollment | (PII bridge) | `cr:Enrollment` (exists) | `cr:EnrollmentView` (exists) | `enrollment_as_of_cut.rq` |
| Adverse Event | `top:Outcome` | `cr:AdverseEvent` (exists) | `cr:AdverseEventView` (exists) | `safety_ae_by_soc.rq`, `sdtm_ae.rq` |
| Site | `top:Location` | *gap — additive* | `cr:SiteLeaf` (exists) | `site_activation_tracker.rq` |
| Deviation, Screen Fail, Document, Protocol, Tag, Task, CRF, Milestone, Budget, Contract, Person, Person Role | (per leaf) | *gaps — additive* | *some leaves exist* | *various* |

The **Calls to Action** column is the one genuinely missing piece. Proposal: add a small, additive vocabulary that attaches CTAs to a class as `(action, persona, gatingState)` triples — for example, `cr:Study cr:hasAction [ cr:action "Activate Study" ; cr:persona "Sponsor PM" ; cr:whenState "IN_STARTUP" ]`. This lives in the operator layer, is Additive per the extension contract, and gives the Action layer a schema without touching Core.

### 4. Governance

- **Additive only.** Per the extension contract (ADR-0019), gap objects are added as new `cr` classes subclassing a TOP leaf in the `cr` namespace; no Core term is redefined and no canonical label is rewritten. The OOUX "Participant (Subject)" reconciles to the settled ADR-0024 decision (Participant preferred, subject altLabel), not a new label.
- **Tests stay green.** New classes ship with worked examples and pass `tests/run_tests.py`; the deterministic build (`build_dist.py`) round-trips.
- **The OOUX catalog itself** is imported into `cr-domain/docs/` (or a `catalog/` sibling) as the durable source the reconciliation is measured against, so the mapping never drifts silently.

## Alternatives considered

- **Do nothing.** The OOUX map stays an external document; each consumer re-derives structure ad hoc. *Preserves* the current model untouched; *changes* nothing; *not chosen* because the map and the model drift and the "build any page from the ontology" goal never gets a single schema.
- **House the entity-view schema in a consuming product or a design system.** *Changes* where the schema lives; *preserves* speed for one consumer; *not chosen* because it inverts the dependency direction — consumers depend on the commons; the commons must depend on none of them. The schema is ontology, so it lives here.
- **Treat the OOUX map as a replacement ontology.** *Changes* Core wholesale; *not chosen* because it would redefine Core terms and violate open-core / constrained-extension (ADR-0019). The map is a lens, not a new spine.

## Open questions

- **CTA home and format.** Should Calls to Action be modeled in the ontology (the `cr:hasAction` proposal above) or remain consumer policy? If modeled, is `(action, persona, whenState)` sufficient, or do actions need pre/post-conditions and effects? Reviewer guidance wanted.
- **StudyView scope.** `operator-views.ttl` has `EnrollmentView`, `AdverseEventView`, `EDCObservationView`, etc., but no `StudyView`. A Study inlines a very large forward fan-out; should its operator view inline a curated subset (the monitoring-relevant edges) rather than all ~45 relationships?
- **Catalog import.** Import the full 78-object OOUX catalog as a doc artifact in `cr-domain`, or keep it external and track only the reconciliation table here?

## Consequences

- **What gets easier:** a consumer's generic viewer reads one ontology-sourced schema; a new relationship added to the ontology tomorrow renders as a new connection block with no UI change; projective apps inherit context by edge traversal for free.
- **What gets harder:** every operator-facing object now carries an obligation to define its operator view (Graph layer) and, if adopted, its CTAs (Action layer), not just its class and shapes.
- **What downstream consumers must adapt to:** consumers that render entities from the graph treat `operator-views.ttl` + class properties + CTA annotations as the contract.
- **Follow-on work:** the full 78-object reconciliation pass (additive), the CTA vocabulary, and `StudyView` and the other missing views.
- **What this forecloses:** hardcoded per-type pages in any consumer; the ontology becomes the source of the operator UI, so UI structure changes route through the model.

## References

- Clinical Research OOUX Map v0.2 (operator-facing object catalog, 78 objects × four columns)
- `cr-domain/views/operator-views.ttl` and `cr-domain/tools/ngsild_view.py` (the retrieval-view schema and its walker)
- `cr-domain/projections/*.rq` (projective-view queries: `enrollment_as_of_cut`, `planned_vs_actual`, `site_activation_tracker`, and the SDTM/FHIR/safety set)
- `governance/decision-log.md`: ADR-0018 (CV layout), ADR-0019 (open-core constrained extension), ADR-0024 (Participant preferred label)
- `governance/extension-contract.md` (the three flavors)

## Notes for reviewers

- Bo: the §Proposal.2 framing (the four layers, with the Graph layer sourced from the existing `operator-views.ttl`) is the part I most want your read on. It asserts that most of "how a generic viewer builds a page" already exists here, and the new work is reconciliation plus the Action layer. If that reading of `operator-views.ttl` is right, the remaining build is smaller than it looks.
