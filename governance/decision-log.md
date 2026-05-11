# Architectural Decision Log

> The chain of architectural decisions that shape The Ontology Project, in the order they were made. Each entry captures the question, the pivotal moment that forced an answer, the decision, and what it commits us to. Decisions are append-only: a later decision can supersede an earlier one, but the earlier one is never edited away — the reasoning is the artifact.

This log is the answer to "why is it shaped this way?" When a contributor proposes a change that conflicts with one of these decisions, the path forward is a new ADR that supersedes the old, not a quiet edit to the docs.

## Index

| # | Date | Title | Status |
| --- | --- | --- | --- |
| [ADR-0001](#adr-0001-temporal-and-prov-native-at-the-foundation) | 2026-05-08 | Temporal and PROV native at the foundation | Accepted |
| [ADR-0002](#adr-0002-universal-foundation-posture-no-specialized-entity-types-for-cross-cutting-shapes) | 2026-05-08 | Universal foundation posture — no specialized entity types for cross-cutting shapes | Accepted |
| [ADR-0003](#adr-0003-correct-the-namespace-mislabeling-top-is-the-project) | 2026-05-09 | Correct the namespace mislabeling — `top:` is the project | Accepted |
| [ADR-0004](#adr-0004-composable-workflow-extensions-not-sibling-reference-graphs) | 2026-05-09 | Composable workflow extensions, not sibling reference graphs | Accepted |
| [ADR-0005](#adr-0005-drop-onto-from-uri-paths) | 2026-05-09 | Drop `/onto/` from URI paths | Accepted |
| [ADR-0006](#adr-0006-skos-as-the-canonical-taxonomy-format) | 2026-05-09 | SKOS as the canonical taxonomy format | Accepted |
| [ADR-0007](#adr-0007-option-b-commons-as-vocabulary-workflows-as-shape) | 2026-05-09 | Option B — commons as vocabulary, workflows as shape | Accepted |
| [ADR-0008](#adr-0008-option-b-properly-scoped-commons-carries-universal-primitive-shapes) | 2026-05-09 | Option B properly scoped — commons carries universal primitive shapes | Accepted |
| [ADR-0009](#adr-0009-specialization-pattern-workflow-concepts-extend-commons-primitives-via-subclassof) | 2026-05-09 | Specialization pattern — workflow concepts extend commons primitives via `subClassOf` | Accepted |
| [ADR-0010](#adr-0010-four-layer-enforcement-against-drift) | 2026-05-09 | Four-layer enforcement against drift | Accepted |
| [ADR-0011](#adr-0011-prov-as-taxonomy-governance-dogfood) | 2026-05-09 | PROV as taxonomy governance — dogfood | Proposed |
| [ADR-0012](#adr-0012-three-level-architecture-universal-dna-eight-categories-leaves) | 2026-05-09 | Three-level architecture — Universal DNA, eight categories, leaves | Accepted (refined by ADR-0013; supersedes part of ADR-0008) |
| [ADR-0013](#adr-0013-practitioner-first-tops-primary-customer) | 2026-05-09 | Practitioner-first — TOP's primary customer | Accepted |
| [ADR-0014](#adr-0014-rename-primitives-to-core-and-cleanups) | 2026-05-10 | Rename Primitives → Core, and cleanups | Accepted (supersedes naming in ADR-0008, ADR-0012, ADR-0013) |
| [ADR-0015](#adr-0015-promote-facts-to-entities-no-bespoke-flags) | 2026-05-11 | Promote facts to entities — no bespoke flags | Accepted |

---

## ADR-0001: Temporal and PROV native at the foundation

**Date:** 2026-05-08 · **Status:** Accepted · **PR:** [#8](https://github.com/scientixai/the-ontology-project/pull/8) · **Refs:** [FIRST-PRINCIPLES.md § Temporal and provenance, native](../FIRST-PRINCIPLES.md)

### Context

Operators in regulated industries do not get to bolt provenance on later. GxP, 21 CFR Part 11, ICH E6(R3), and every audit-trail discipline downstream of them require that *who* did *what*, *when*, and *based on what* be answerable from the data without reconstruction. Ontologies that punt provenance to a higher layer end up reinventing it badly.

### Decision

The foundation adopts NGSI-LD temporal semantics and W3C PROV native typing as first-class concerns. Every entity declares its `provType` (Agent / Activity / Entity); every property declares its `provSemantics` where one applies (`prov:wasGeneratedBy`, `prov:wasAttributedTo`, `prov:wasAssociatedWith`, `prov:wasDerivedFrom`, `prov:actedOnBehalfOf`, `prov:wasInformedBy`, `prov:wasInvalidatedBy`, `prov:hadRole`). The translator emits `rdfs:subClassOf prov:*` and `rdfs:subPropertyOf prov:*` from these annotations. Audit-trail entries are container-typed; not specialized.

### Consequences

- Audit-trail tooling that consumes PROV gets a free seat at the table. No special-case adapters.
- The foundation cannot drift away from PROV without breaking every downstream provenance query.
- Future ADRs (notably [ADR-0011](#adr-0011-prov-as-taxonomy-governance-dogfood)) can extend the same discipline to the taxonomy itself, not just instance data.

---

## ADR-0002: Universal foundation posture — no specialized entity types for cross-cutting shapes

**Date:** 2026-05-08 · **Status:** Accepted · **PR:** [#9](https://github.com/scientixai/the-ontology-project/pull/9) · **Refs:** [FIRST-PRINCIPLES.md § Universal foundation](../FIRST-PRINCIPLES.md)

### Context

A draft of the Visit lift introduced `VisitObservation` as a specialized entity type. That triggered a question: do we keep adding specialized types every time a workflow expresses a shape, or do we treat the foundation as universal containers that get specialized through *content* rather than *shape*?

### Decision

Cross-cutting shapes (Activity, Task, observation) are expressed as universal containers in the foundation. Specialization happens through reference data, role bindings, and projection — not by minting new entity types every time a workflow expresses the same shape with different content.

### Consequences

- The foundation stays small and stable. Shapes that recur across workflows are recognizable.
- This decision sets up the question that ADR-0007 and ADR-0008 answer in the affirmative: if cross-cutting shapes belong to the universal layer, *which layer is that*, and how does workflow-specific specialization actually attach?

---

## ADR-0003: Correct the namespace mislabeling — `top:` is the project

**Date:** 2026-05-09 · **Status:** Accepted · **Refs:** [TAXONOMY.md § Three layers](../TAXONOMY.md)

### Context

Through the first eight top-level lifts, `top:` was bound to the clinical-trials reference graph and `topc:` to the commons. That was inverted. `top` is the **project** — The Ontology Project — and clinical-trials is one workflow extension among many to come. Labeling clinical-trials as `top:` made every cross-cutting concern look like a clinical-trials concern, which is exactly the FIWARE failure mode.

> "Event moves from `top:Event` to `topc:Event`. We got this all wrong and we need to stop and fix this. 'Top' is the overall project. I think the mistake is that I hadn't done taxonomy work before we started — this is exactly the failure mode the taxonomy literature warns about."

The discipline being violated: **classification before construction.** We had skipped the classification layer and were paying for it.

### Decision

Re-bind the namespaces:

- `top:` — project-level concept scheme, governance, top-of-tree concepts.
- `topc:` — commons (primitives shared across every workflow).
- `topcr:` — clinical-research workflow extension. Future siblings: `topcd:` (clinical-data), `topmfg:` (manufacturing), `topsc:` (supply-chain), and so on.

The mechanical refactor is mechanically large but conceptually clean: rename `top:` → `topcr:` everywhere it pointed at clinical-research-native concepts; promote cross-cutting concepts (Event, Visit, Document, Person, Organization, Site, …) from `top:` to `topc:`.

### Consequences

- The taxonomy can grow new workflow extensions without renaming anything.
- The website and docs need a one-time mechanical refactor.
- This decision is the wedge that opens [ADR-0004](#adr-0004-composable-workflow-extensions-not-sibling-reference-graphs), [ADR-0007](#adr-0007-option-b-commons-as-vocabulary-workflows-as-shape), and [ADR-0008](#adr-0008-option-b-properly-scoped-commons-carries-universal-primitive-shapes).

---

## ADR-0004: Composable workflow extensions, not sibling reference graphs

**Date:** 2026-05-09 · **Status:** Accepted · **Refs:** [TAXONOMY.md § Workflow extensions](../TAXONOMY.md)

### Context

A first-pass taxonomy proposal modeled clinical-research, healthcare-delivery, manufacturing, and regulatory as **sibling** reference graphs. Bo pushed back with a single test:

> "What happens when a smart hospital sponsors a clinical trial? It feels off."

It does feel off. A smart hospital sponsoring a trial is a healthcare-delivery operator running a clinical-research workflow. If those are siblings, the operator has to choose one and lose the other. That is the FIWARE Smart Data Models failure mode: workflows treated as siblings end up with duplicated primitives, conflicting names for the same concept, and no path to compose.

### Decision

Workflows are **composable extensions** layered on a single commons foundation, not siblings. A smart hospital is not in `topcd:`-or-`topcr:`; it is in both, simultaneously, by binding the same `topc:Person` (the patient) to both a `topcd:Encounter` and a `topcr:Visit`. The commons provides the primitives; workflows specialize them.

### Consequences

- New workflow extensions ship as additive packages, not as new top-of-tree concept schemes.
- Cross-workflow composition (the smart-hospital-as-sponsor case) becomes a first-class scenario rather than an edge case.
- The taxonomy explicitly models **WorkflowExtensions** as a top concept distinct from the foundation, so contributors can see at a glance which layer they are touching.

---

## ADR-0005: Drop `/onto/` from URI paths

**Date:** 2026-05-09 · **Status:** Accepted · **Refs:** [TAXONOMY.md § URI conventions](../TAXONOMY.md)

### Context

URIs were `https://top.scientix.ai/onto/commons/v1#Person` and similar. The `/onto/` segment was load-bearing for nothing — it didn't disambiguate (the host already says ontology), and it added a noise word to every reference.

> "Making the taxonomy SKOS will earn the respect of ontologists. Then we can import into TermBoard and manipulate there."

Human-friendly URIs were the same conversation: ontologist-grade structure, operator-grade legibility.

### Decision

URI structure: `https://top.scientix.ai/{layer}/v{N}#{Concept}`.

- `https://top.scientix.ai/commons/v1#Person`
- `https://top.scientix.ai/clinical-research/v1#Sponsor`
- `https://top.scientix.ai/clinical-research/v1#Visit`

Prefixes: `topc:` → `https://top.scientix.ai/commons/v1#`, `topcr:` → `https://top.scientix.ai/clinical-research/v1#`.

### Consequences

- Documentation reads cleanly. Curl commands fit on one line.
- The `onto/` directory in the repo (a convenience mirror) keeps its name; that's a filesystem detail, not a URI commitment.

---

## ADR-0006: SKOS as the canonical taxonomy format

**Date:** 2026-05-09 · **Status:** Accepted · **PR:** [#13](https://github.com/scientixai/the-ontology-project/pull/13) · **Refs:** [`taxonomy/taxonomy.ttl`](../taxonomy/taxonomy.ttl), [`taxonomy/taxonomy.csv`](../taxonomy/taxonomy.csv), [TAXONOMY.md](../TAXONOMY.md)

### Context

The taxonomy needs to be importable into the tools ontologists actually use (TermBoard, PoolParty, Synaptica, Protégé) without bespoke adapters, and it needs to be legible to non-ontologists who are reviewing names and definitions.

### Decision

Author the taxonomy in SKOS Turtle as the source of truth (`taxonomy/taxonomy.ttl`). Ship a CSV companion (`taxonomy/taxonomy.csv`) for spreadsheet review and a Markdown narrative (`TAXONOMY.md`) for human readers. Each concept declares `skos:Concept` + `skos:inScheme top:TaxonomyV1` + `skos:broader` + `skos:prefLabel` + `skos:definition` + `skos:notation`, plus `rdfs:subClassOf` and PROV typing where applicable.

### Consequences

- The taxonomy round-trips through TermBoard and equivalent tools.
- The CSV is the curator's working surface; the Turtle is the system of record; the Markdown is the readers' entry point.
- Every concept in the foundation is now traceable to a single canonical record.

---

## ADR-0007: Option B — commons as vocabulary, workflows as shape

**Date:** 2026-05-09 · **Status:** Accepted (refined by ADR-0008) · **Refs:** [TAXONOMY.md](../TAXONOMY.md)

### Context

Once `topc:` was correctly identified as the commons (ADR-0003) and workflows were composable extensions (ADR-0004), the question collapsed to: **where does the shape of a Visit live?** Two readings both felt right, and that was the diagnostic:

> "Something still doesn't feel right. `clinical-research/visit` feels like the right shape. But so does `healthcare/visit`."

> "In manufacturing you might have an inspection visit."

Three options were on the table:

- **Option A** — commons holds only abstract concepts (no shape); every workflow defines its own Visit from scratch. Maximum independence, maximum drift.
- **Option B** — commons defines the *vocabulary* (the concept of Visit); workflows define the *shape* (which properties, which constraints, which sub-objects). One name, many shapes.
- **Option C** — commons defines a single fully-shaped Visit; workflows extend it monolithically. Minimum independence, all drift compressed into one fight.

Bo's call:

> "Yes Option B."

### Decision

Commons is the **vocabulary layer**. It declares that a Visit exists as a concept (with a definition, a PROV type, and the broader/narrower relations a SKOS scheme demands). Workflow extensions declare the **shape** of a Visit *as it operates in their domain* — which properties, which constraints, which sub-objects, which projections.

### Consequences

- `topcr:Visit` and `topmfg:Visit` (eventual) are both Visits in the SKOS sense — same vocabulary entry — and both `rdfs:subClassOf topc:Visit`.
- Cross-workflow composition (smart hospital sponsoring a trial) works: a single physical encounter can be both a `topcd:Encounter` and a `topcr:Visit` because both specialize the same commons concept.
- The smart-hospital-as-sponsor problem from ADR-0004 has a concrete answer.
- This decision was refined within hours by [ADR-0008](#adr-0008-option-b-properly-scoped-commons-carries-universal-primitive-shapes).

---

## ADR-0008: Option B properly scoped — commons carries universal primitive shapes

**Date:** 2026-05-09 · **Status:** Accepted · **Supersedes part of ADR-0007** · **Refs:** [TAXONOMY.md § Three layers](../TAXONOMY.md), [`taxonomy/taxonomy.ttl`](../taxonomy/taxonomy.ttl)

### Context

Initial implementation of ADR-0007 over-corrected: it pushed *every* shape — even Document, even Person, even Site — out of the commons and into workflow extensions. Bo flagged the problem in one sentence:

> "Can't a document truly exist EVERYWHERE? The definition of a document and its attributes as a primitive are durable across every domain."

Yes. Some primitives are universal not just at the *concept* level but at the *primitive shape* level. A Document has a title, an author, a creation timestamp, a content reference, a content type, and a hash, in every workflow. Specializing those into per-workflow shapes is making up work that doesn't need doing.

### Decision

The commons holds **universal primitive shapes** for concepts where the durable attributes are stable across every domain. Workflow extensions specialize via `rdfs:subClassOf` to add domain-specific properties, constraints, projections, and sub-objects.

Universal primitive shapes (current set, 15): Person, Organization, Site, Visit, Event, OversightBody, Document, Equipment, System, Log, StorageLocation, Credential, Activity, Task, VisitObservation.

Workflow-extension shapes are *narrower* than the commons primitive — they add, they don't replace. A `topcr:Visit` is a `topc:Visit` with clinical-research-specific properties (protocol-window, required-procedures, IP-administration sub-object). Drop the clinical-research-specific properties and you're back to a `topc:Visit`.

### Consequences

- The commons stops being a vocabulary stub and becomes the actual reusable foundation.
- Workflow extensions stay small — they only own the delta.
- The line between "belongs in commons" and "belongs in a workflow extension" is now testable: *if every workflow needs this property with this meaning, it's commons; if even one workflow disagrees, it's an extension.*
- This refines ADR-0007 in the direction Bo wanted but the original ADR didn't quite reach.

---

## ADR-0009: Specialization pattern — workflow concepts extend commons primitives via `subClassOf`

**Date:** 2026-05-09 · **Status:** Accepted · **Refs:** [`taxonomy/taxonomy.ttl`](../taxonomy/taxonomy.ttl)

### Context

ADR-0008 commits to specialization, but doesn't say *how* a workflow concept declares it specializes a commons primitive. A concrete example forced the question:

> "I can see a need to declare primitives that may be extended through domains. For example: clinical-research>1572 extends commons>document?"

Form 1572 (the FDA Statement of Investigator) is unmistakably a Document — it has a title, an author, a date, a content reference, a hash. It also has clinical-research-specific properties — the principal investigator it is signed by, the study it commits to, the regulatory submission it attaches to. We need a pattern that says *both*.

### Decision

A workflow-extension concept that specializes a commons primitive declares two relations:

```turtle
topcr:Form1572 a skos:Concept, owl:Class ;
    skos:inScheme top:TaxonomyV1 ;
    skos:broader topc:Document ;
    rdfs:subClassOf topc:Document ;
    skos:prefLabel "FDA Form 1572"@en ;
    skos:altLabel "Statement of Investigator"@en ;
    skos:definition "The clinical-research-specific signed statement…"@en ;
    skos:notation "topcr:Form1572" ;
    prov:Entity "prov:Entity" .
```

`skos:broader` is the SKOS relation (taxonomy navigation, TermBoard surfaces it). `rdfs:subClassOf` is the OWL relation (reasoners specialize on it). Both. Always paired. The commons primitive is named in both.

### Consequences

- Specialization is *visibly* specialization. A reviewer can read a workflow concept and see exactly which commons primitive it claims to inherit from.
- Reasoners get a real `subClassOf` edge for inference, not just a SKOS narrower edge.
- The pattern generalizes: `topcr:InformedConsentForm subClassOf topc:Document`, `topcr:Protocol subClassOf topc:Document`, `topcr:InvestigatorBrochure subClassOf topc:Document`, `topmfg:BatchRecord subClassOf topc:Document` (future), and so on.

---

## ADR-0010: Four-layer enforcement against drift

**Date:** 2026-05-09 · **Status:** Accepted · **Refs:** [TAXONOMY.md § Drift prevention](../TAXONOMY.md)

### Context

ADR-0008 and ADR-0009 only work if domains *actually use* the commons primitives instead of redefining their own. The FIWARE failure mode is exactly drift: every domain reinvents Document because nobody enforces against it.

> "The curation in my mind is how we keep this structure pure without drift — how do you enforce against domains creating replications of commons primitives?"

### Decision

Drift prevention runs on four layers, each catching what the layer above it might miss:

1. **Lint rules (mechanical).** SHACL meta-shapes in `taxonomy/meta-shapes.ttl` validate the taxonomy itself. Rules: every workflow-extension concept that names a commons-primitive label must declare `rdfs:subClassOf` on that primitive; no workflow extension may declare a concept with the same `skos:prefLabel` as a commons primitive without a `subClassOf` edge; deprecated concepts must declare `dct:isReplacedBy`.

2. **RFC process (procedural).** New concepts arrive as RFCs in `governance/rfcs/`. The RFC template (forthcoming) requires the proposer to answer: *Is there a commons primitive this should specialize? If no, why not?* The default answer is "yes, specialize"; "no" must be argued.

3. **Working group curation (human).** The TaxonomyWG reviews every RFC for layer assignment before approving. The WG owns the call on whether a proposed concept belongs in commons or in a workflow extension.

4. **Documentation discipline (cultural).** TAXONOMY.md, this decision log, and FIRST-PRINCIPLES.md are the references contributors are expected to read before opening an RFC. New contributors who try to add a duplicate primitive get pointed at the relevant ADR rather than into a long discussion.

### Consequences

- Drift becomes detectable mechanically (Layer 1) and reviewable procedurally (Layers 2–3) before it becomes cultural (Layer 4).
- The TaxonomyWG has authority over the commons / workflow boundary. That authority is documented.
- A new contributor cannot quietly add `topmfg:Document` without tripping at least one of the four layers.

---

## ADR-0011: PROV as taxonomy governance — dogfood

**Date:** 2026-05-09 · **Status:** Proposed · **Refs:** [ADR-0001](#adr-0001-temporal-and-prov-native-at-the-foundation)

### Context

ADR-0001 commits the foundation to PROV native typing for instance data. The taxonomy itself is data — concepts get proposed, reviewed, approved, deprecated, replaced, attributed to people. If we believe what ADR-0001 says, the taxonomy should carry the same provenance discipline it imposes on the data below it.

> "Should the taxonomy itself use PROV as a way to document governance and accountability?"

### Decision (Proposed)

Yes. Each concept in `taxonomy/taxonomy.ttl` carries a PROV provenance chain at the concept level:

```turtle
topc:Document a skos:Concept, owl:Class ;
    rdfs:subClassOf prov:Entity ;
    skos:prefLabel "Document"@en ;
    prov:wasGeneratedBy top:ConceptDecision_topc-Document ;
    prov:wasAttributedTo <https://github.com/bo-lora> ;
    dct:created "2026-05-08T00:00:00Z"^^xsd:dateTime .

top:ConceptDecision_topc-Document a prov:Activity ;
    prov:wasAssociatedWith <https://github.com/bo-lora> ;
    prov:hadRole top:ProposerRole ;
    prov:atTime "2026-05-08T00:00:00Z"^^xsd:dateTime ;
    rdfs:seeAlso <https://github.com/scientixai/the-ontology-project/pull/13> .
```

Concept-level provenance enables governance auditing as SPARQL queries: *who proposed each commons primitive*, *when was a concept deprecated and what replaced it*, *which curator approved each WorkflowExtension*.

The meta-shapes in [ADR-0010](#adr-0010-four-layer-enforcement-against-drift) Layer 1 are extended to require the PROV chain on every concept.

Three named PROV roles are introduced for taxonomy governance: `top:ProposerRole`, `top:ReviewerRole`, `top:CuratorRole`.

### Consequences

- The taxonomy is auditable by the same tools as the data it governs.
- New concept proposals must carry a provenance chain to merge — the meta-shape will block PRs that don't.
- The foundation now dogfoods its own provenance discipline at every layer.
- Status remains **Proposed** until the meta-shapes ship and the taxonomy is backfilled with concept-level provenance for the existing 52 concepts.

---

## ADR-0012: Three-level architecture — Universal DNA, eight categories, leaves

**Date:** 2026-05-09 · **Status:** Proposed · **Supersedes part of [ADR-0008](#adr-0008-option-b-properly-scoped-commons-carries-universal-primitive-shapes)** · **Refs:** [`taxonomy/taxonomy.ttl`](../taxonomy/taxonomy.ttl), [`commons/source/core.ttl`](../commons/source/core.ttl)

### Context

ADR-0008 committed commons to a flat set of 15 universal primitive shapes (Person, Organization, Site, Visit, Event, OversightBody, Document, Equipment, System, Log, StorageLocation, Credential, Activity, Task, VisitObservation). The classification told Termboard which concepts were universal versus workflow-specific, but it did not tell Termboard — or any reasoner — *what those concepts have in common*. When Bo loaded `taxonomy/taxonomy.ttl` into Termboard for the first SKOS round-trip, the result was a mess. Two compounding causes:

1. **Mechanical:** every commons and workflow concept ended with a malformed PROV typing line of the form `prov:Agent "prov:Agent" .` — using a class as a predicate, with a string literal as object. ADR-0001 specified `rdfs:subClassOf prov:*` as the encoding; the SKOS lift in PR #13 emitted a placeholder that no SKOS-aware tool could interpret. Forty-six concepts carried this defect.
2. **Architectural:** the 15 TOP Primitives had no shared structural parentage. Each one declared `skos:broader top:CommonsFoundation` and `prov:Agent` / `prov:Activity` / `prov:Entity`, but nothing tied a Person, an Organization, and an OversightBody together as *Agents*; nothing tied a Site and a StorageLocation together as *Locations*; nothing tied a Document, a Log, and a Credential together as *Evidence*. TOP was a flat bag of 15 primitives with PROV typing as the only (broken) cross-cutting structure.

The architectural fix forced itself: between TOP Primitives and the leaves, a **categorical layer** was missing. The categorical layer is what gives a reasoner — and a reviewer — a way to ask "what kind of thing is this?" before drilling into specifics.

### Decision

Commons adopts a **three-level architecture**:

**Level 1 — Universal DNA.** Every TOP entity, regardless of category, inherits a fixed set of seven properties:

- `top:identifier` — globally unique URI/URN (the technical anchor)
- `top:wasAttributedTo` — the Agent responsible for the existence of this record (record-level provenance, distinct from domain-level `prov:wasAttributedTo` semantics; documented in `commons/source/core.ttl`)
- `top:wasGeneratedBy` — the Activity that produced this record (record-level provenance)
- `top:observedAt` — NGSI-LD-style timestamp anchor
- `top:status` — lifecycle / health state
- `top:value` — core data payload (optional; meaningful for data-bearing entities, blank for structural ones)
- `top:unit` — standardized unit of measure (optional; paired with `top:value` where data is dimensional)

The `top:` prefix is correct here per ADR-0003: these are project-level structural properties, not workflow-specific. Universal DNA lives in `commons/source/core.ttl`; the SKOS taxonomy carries a marker concept (`top:UniversalDNA`) so reviewers in Termboard see that the layer exists.

**Level 2 — Category-Level Objects.** TOP Primitives organize around eight categories. Every primitive is a subclass of exactly one (with multi-classification permitted only when explicitly justified — see *Consequences*):

| Category | Primary focus | Category-level relational extensions |
| --- | --- | --- |
| `topc:Agent` | Authority | `hasCredential`, `memberOf`, `authorizedBy` |
| `topc:Location` | Space | `withinLocation`, `geoSpatialData`, `accessRequirement` |
| `topc:Resource` | Tools | `ownedBy`, `hasMaintenanceLog`, `operationalState` |
| `topc:Scope` | Intent | `governedBy`, `containsActivity`, `objectiveStatement` |
| `topc:Temporal` | Rhythm | `startTime`, `endTime`, `precededBy`, `occursAt` |
| `topc:Evidence` | Proof | `verifiesOutcome`, `integrityHash`, `signedBy` |
| `topc:Outcome` | Results | `measuredBy`, `satisfiesConstraint`, `variance` |
| `topc:Constraint` | Validity | `enforcedBy`, `severityLevel`, `appliesTo` |

**Level 3 — Leaves.** The 15 commons primitives from ADR-0008 are preserved, re-homed under their L2 category:

- **Agent** — Person, Organization, OversightBody
- **Location** — Site, StorageLocation
- **Resource** — Equipment, System
- **Evidence** — Document, Log, Credential
- **Temporal** — Visit, Activity
- **Outcome** — Event, VisitObservation, Task

`Scope` and `Constraint` ship without leaves in this ADR. They are reserved as L2 anchors; concrete leaves (Portfolio / Program / Project under Scope; PhysicalLimit / RegulatoryLaw / SafetyGuardrail under Constraint) defend themselves under [ADR-0010](#adr-0010-four-layer-enforcement-against-drift) Layer 2 (RFC) when a real workflow forces them.

### What this changes vs. ADR-0008

ADR-0008's 15 primitive shapes survive intact at L3. What changes is their parentage: instead of all sharing `skos:broader top:Primitives` flatly, they now declare `skos:broader topc:<Category>` and `rdfs:subClassOf topc:<Category>, prov:<provType>`. TOP becomes navigable — a reviewer in Termboard can drill from TOP Primitives → Agent → Person, or query `?x rdfs:subClassOf topc:Agent` to find every kind of agent across every workflow.

### Consequences

- **Termboard renders cleanly.** With the 46 malformed PROV lines repaired and a real categorical hierarchy, Termboard's tree view shows Universal DNA → 8 categories → 15 leaves → workflow specializations.
- **Cross-workflow queries get more powerful.** "Find every Agent across every workflow" now resolves to a `subClassOf topc:Agent` traversal that picks up `topc:Person`, `topc:Organization`, `topc:OversightBody`, plus their workflow specializations (`topcr:Investigator subClassOf topc:Person`, etc.) — without enumerating each leaf.
- **The 8 categories are not perfectly orthogonal, by design.** An autonomous AI agent is both an Agent (it acts) and a Resource (it can be deployed and maintained). A clinical site is both a Location (it has geospatial coordinates) and a Resource (it can be allocated). Multi-classification is permitted but must be explicit and justified in the leaf concept's `skos:scopeNote`. Drift-prevention Layer 1 (per ADR-0010) gets a new SHACL meta-shape: a leaf may declare `rdfs:subClassOf` against multiple L2 categories only if its `skos:scopeNote` cites the operator workflow that requires the multi-classification.
- **Universal DNA at the root has PROV-O semantics implications.** `prov:wasAttributedTo` in PROV-O is a property of `prov:Entity`, not of `prov:Agent` or `prov:Activity`. Putting `top:wasAttributedTo` on every entity (including Agents and Activities) inverts the domain semantics. The resolution: `top:wasAttributedTo` is **record-level provenance** — the Agent responsible for the existence of this record, distinct from domain-level `prov:wasAttributedTo` (the Agent the entity is attributed to in domain semantics). Workflow extensions that need PROV-O-aligned semantics declare a separate domain-typed `prov:wasAttributedTo` relation; commons stays at the record level. This distinction is documented in `commons/source/core.ttl`.
- **"Less is the win" is preserved.** The TOP Primitives count rises from 15 leaves to 8 categories + 15 leaves = 23 commons concepts. The increase is the categorical layer that was already implicit in PROV typing; it's now explicit and navigable. New leaves (Portfolio, RegulatoryLaw, etc.) do not auto-lift; each defends itself per ADR-0010.
- **ADR-0011 (PROV-as-taxonomy-governance) becomes easier to land.** With `rdfs:subClassOf prov:*` correctly declared on every concept, the per-concept PROV provenance chain in ADR-0011 has a stable anchor.

### Migration

Three artifacts ship together with this ADR:

1. **`taxonomy/taxonomy.ttl`** — rewritten with `owl:` prefix, 8 L2 category concepts, re-homed leaves, repaired PROV typing (`rdfs:subClassOf prov:*`).
2. **`commons/source/core.ttl`** (new) — L1 Universal DNA properties + L2 category classes + category-level relational extensions, with the record-level vs. domain-level PROV distinction documented inline.
3. **`commons/source/walkthroughs/person.ttl`** (new) — one concrete `topc:Person` instance with Universal DNA filled in, Agent category classification declared, and PROV typing exercised end-to-end. Reviewers verify the pattern by loading this into Termboard or any SKOS/OWL tool.

`onto/commons/v1/shapes.ttl` (the legacy SHACL definitions carrying mixed clinical+commons content) is not touched in this PR. Its rebuild against the L2 category shapes is a follow-on once the L1+L2+L3 structure verifies in Termboard.

### Status

Accepted. Status moved from Proposed to Accepted on 2026-05-09 after Bo locked the path. Refined by ADR-0013, which trims Universal DNA from seven properties to three and locks practitioner-first as TOP's primary commitment.

---

## ADR-0013: Practitioner-first — TOP's primary customer

**Date:** 2026-05-09 · **Status:** Accepted · **Refines:** [ADR-0012](#adr-0012-three-level-architecture-universal-dna-eight-categories-leaves) · **Refs:** [`commons/source/core.ttl`](../commons/source/core.ttl), [FIRST-PRINCIPLES.md](../FIRST-PRINCIPLES.md), [MANIFESTO.html](../MANIFESTO.html)

### Context

ADR-0012 introduced a three-level architecture with seven Universal DNA properties (identifier, wasAttributedTo, wasGeneratedBy, observedAt, status, value, unit). The seven were a first-pass list — practical, not principled. Reviewing the proposal surfaced a deeper question: who is TOP's primary customer? Two coherent answers were on the table:

- **Pure Semantic Path** — strict W3C BFO + PROV-O alignment at every level. Universal DNA stripped to BFO/PROV-O essentials. Every relationship a typed triple between distinct types. Bulletproof against ontologist critique. Earns OBO Foundry interop. Optimizes for the ontologist customer.

- **Practitioner-first** — TOP is shaped by what operators do at work. AI agents reason against TOP via PROV-O + BFO alignment at the categorical edge, but TOP itself is not shaped to make agents' jobs easier at the cost of operator legibility. Optimizes for the operator customer.

Bo's call:

> "TOP has to be practitioner friendly — hence the focus on OOUX as the way to model from a practitioner perspective and goal to provide a foundation that AI agents can reason to help humans be super human. The manifesto says that we owe it to humans. Decades have gone by where humans are asked to conform to non-sensical user experiences because they are shaped by a database developer priority. In the end, we want to augment the humans, machines have plenty of help."

This is principle-level, not tactical. It belongs in the decision log and in FIRST-PRINCIPLES, named explicitly so future contributors can cite it.

### Decision

**TOP's primary customer is the human practitioner.** AI agents and ontologist tooling are honored at the edge — via PROV-O class-level alignment, BFO subClassOf annotations on the four L2 categories where alignment is clean, and SKOS round-trip into Termboard / PoolParty / Synaptica — but they do not shape TOP Primitives, TOP's vocabulary, or TOP's universal interface. The same instance answers a coordinator's "is this protocol current?" query and an OBO reasoner's "give me every IndependentContinuant in this graph" query. The first query gets the practitioner shape; the second gets the formal alignment; both work; neither distorts the other.

Three concrete commitments follow:

1. **Universal DNA trims from seven properties to three.** Only `top:identifier`, `top:observedAt`, `top:status` remain at the universal level. These are the three properties practitioners universally encounter for every entity: *what is this thing*, *when was it captured*, *is it current*. The four dropped properties (`wasAttributedTo`, `wasGeneratedBy`, `value`, `unit`) overreached — they were universal in the engineering sense, not in the practitioner sense, and forcing them at the root invited the record-level vs. domain-level provenance gymnastics ADR-0012 had to invent.

2. **PROV-O alignment is strict at the class level, not at the universal level.** Every TOP class declares its proper `rdfs:subClassOf prov:Agent | prov:Activity | prov:Entity`. Provenance lives where PROV-O says it belongs (with proper domain semantics), not as universal-level shortcut properties. Workflows that need provenance attach it via PROV-O directly. Record-level metadata (who created the row, when, what tool) uses Dublin Core (`dcterms:creator`, `dcterms:created`, `dcterms:modified`) — clearly metadata, never confused with domain claims.

3. **BFO alignment is light, edge-only.** The four L2 categories with clean BFO membership declare a single `rdfs:subClassOf bfo:*`:
   - `topc:Agent rdfs:subClassOf bfo:IndependentContinuant`
   - `topc:Location rdfs:subClassOf bfo:Site`
   - `topc:Temporal rdfs:subClassOf bfo:Process`
   - `topc:Evidence rdfs:subClassOf bfo:GenericallyDependentContinuant`

   The four mixed-membership categories (Resource, Scope, Outcome, Constraint) carry a BFO scope-note documenting the alignment rationale, but no forced subClassOf at the category level. Leaves under those categories declare their BFO type if and when OBO interop demands it. This buys the OBO Foundry alignment for the clean cases without paying the BFO maintenance tax across all of TOP.

### Consequences

- **The "AI agents reason against TOP, they don't shape it" rule becomes constitutional.** Every future architectural decision asks itself: *did an operator's workday cause this, or did an AI agent's / ontologist's preference cause this?* If the answer is the latter, the change goes to the edge (a projection adapter, an annotation layer, a workflow extension), not into TOP itself.
- **Universal DNA stays small enough that an operator can hold it in their head.** Three properties. *What is this thing? When was it captured? Is it current?* Every TOP entity answers those three.
- **The record-level vs. domain-level PROV gymnastics from ADR-0012 § Consequences disappear.** PROV-O class-level subClassOf is the only PROV alignment commons makes. Workflows that need PROV-O domain provenance use it with proper domain. Record-level metadata uses Dublin Core. Two clean lanes; no fork.
- **OBO Foundry interop is available where it is clean and not forced where it is not.** TOP can cross-reference UBERON, CHEBI, GO, DOID for the four BFO-clean categories without bridging adapters. The four mixed categories carry the BFO discussion in their scope notes, deferred to leaf-level decisions.
- **FIRST-PRINCIPLES gets a new explicit commitment.** A short addition under the "What this rules OUT" / "What this rules IN" structure: *TOP is shaped by operator workdays. AI agents and ontologist tooling are honored at the edge, never as primary customers of TOP.* Citing this ADR.
- **The manifesto's "we owe it to humans" stance becomes structural, not aspirational.** TOP's smallness, the operator-vocabulary primacy, the principled rejection of standards-up shaping — all of it now traces to a single named decision in the log.

### What this does NOT change

- The eight L2 Category-Level Objects from ADR-0012 stand. Categories are how operators organize what they do; that's practitioner-grounded.
- The fifteen L3 commons leaves from ADR-0008 stand, re-homed under their L2 category per ADR-0012.
- The PROV class-level alignment from ADR-0001 stands and is now the *only* PROV alignment commons commits to.
- The Universal DNA marker concept (`top:UniversalDNA`) in `taxonomy/taxonomy.ttl` stays — its scope note is updated to reflect the three-property trim and the new posture.

### Status

Accepted. The artifacts on this branch (`commons/source/core.ttl`, `taxonomy/taxonomy.ttl`, `commons/source/walkthroughs/person.ttl`, FIRST-PRINCIPLES addition) implement this ADR. Termboard verification of the SKOS taxonomy is the next gate.

---

## ADR-0014: Rename Primitives → Core, and cleanups

**Date:** 2026-05-10 · **Status:** Accepted · **Refs:** [taxonomy/taxonomy.ttl](../taxonomy/taxonomy.ttl), [core/v1/index.html](../core/v1/index.html)

### Context

Three architectural rough edges accumulated across PR #16 and the homepage build that followed. Each was small individually; together they were large enough to deserve a single decision rather than three quiet edits.

First, the SKOS top concept was named "Primitives" (computer-science precise: atomic, irreducible building blocks). The rename followed an earlier rename from "Commons Foundation" → "TOP Primitives," because "foundation" was jargon nobody recognized in a room. Reviewing the result with the same audience-fit lens, "Primitives" requires technical literacy to land, while "Core" is immediately accessible to executives, operators, and working group conveners without losing architectural meaning. Cost of the switch: a collision with the existing SHACL file `commons/source/core.ttl` (a "which core" ambiguity), which had to be resolved by moving and renaming that file.

Second, the URI namespace had been split into `top:` (project-level concepts) and `topp:` (the primitive concepts), with primitives at `https://top.scientix.ai/v1/primitives/`. The split was a leftover from an earlier draft. Single-prefix form reads cleaner in extensions and matches the standard W3C ontology pattern (PROV-O at one namespace document, SKOS at one, etc.).

Third, the URL path `top.scientix.ai/onto/primitives/v1/` had `/onto/` as a holdover from the time when the project was federating reference graphs as siblings under one umbrella. With Core as the universal layer and domain reference graphs as compositions on top, `/onto/` adds nothing the path doesn't already carry.

Bo's call:

> "I wonder if 'core' is a better term than 'primitives'."
>
> "Yes let's go with the core change — I think it is a more accurate representation. Make all the changes necessary and do a pull request and merge."
>
> Earlier in the same session: "I also don't care for /onto/ in the path: top.scientix.ai/primitives/v1." (Resolved as `/core/v1/` after the Primitives → Core rename.)

### Decision

Three coupled changes, shipped in one branch:

**1. Rename SKOS top concept Primitives → Core.**
- `top:Primitives` → `top:Core` (URI change at `https://top.scientix.ai/v1#Core`).
- prefLabel "TOP Primitives" → "TOP Core".
- altLabels "Primitives", "Universal Primitives" → "Core", "Universal Core".
- All eight L1 category definitions update from "The Primitives category for ..." to "The Core category for ...".
- All cross-references in homepage, namespaces page, spec page, ADR index, and prose docs follow.

**2. Collapse `topp:` into `top:`.** The previously split namespaces become one. Concept URIs are now `https://top.scientix.ai/v1#Agent`, `https://top.scientix.ai/v1#Person`, etc. The taxonomy.ttl prefix declarations and the 23 PROV-O alignment triples all carry the new prefix.

**3. Drop `/onto/` from the spec page URL.** The Core spec page moves from `/onto/primitives/v1/` to `/core/v1/`. The namespaces landing page stays at `/onto/index.html` for now (it serves as the namespace federation index), with a forward-looking note that the legacy clinical reference graph will follow the same path collapse when its `top:` → `topcr:` rebase lands.

**4. Resolve the file collision.** The previously named `commons/source/core.ttl` (the SHACL invariants file) moves to `core/v1/shapes.ttl`. The empty `commons/` scaffolding directory is removed. The walkthroughs directory follows to `core/v1/walkthroughs/`. The relabeled file becomes the canonical SHACL companion to the SKOS taxonomy.

### What this supersedes

- The naming "Primitives" in [ADR-0008](#adr-0008-option-b-properly-scoped-commons-carries-universal-primitive-shapes) (commons-as-vocabulary), [ADR-0012](#adr-0012-three-level-architecture-universal-dna-eight-categories-leaves) (three-level architecture), and [ADR-0013](#adr-0013-practitioner-first-tops-primary-customer) (practitioner-first) is superseded by "Core". The architectural commitments those ADRs made about layering, vocabulary scope, and practitioner-first orientation stand unchanged; only the label changes. Each ADR keeps its original prose for the historical record per the append-only rule.
- The path `/onto/primitives/v1/` introduced informally during the homepage build is superseded by `/core/v1/`. ADR-0005 (drop `/onto/` from URI paths) anticipated this direction; ADR-0014 implements it for the universal layer ahead of the legacy clinical reference graph following.

### Consequences

- **The "which core" ambiguity is resolved.** The SKOS top concept and the SHACL file have different names: top:Core (vocabulary) vs. core/v1/shapes.ttl (SHACL invariants). Both can be referenced in conversation without disambiguation overhead.
- **Single-prefix URIs.** Anyone reading the taxonomy or extending Core in a workflow sees one prefix (`top:`) instead of two (`top:`, `topp:`). The mental model of "domain X extends Core via topdomain:X subClassOf top:Y" stays clean.
- **Termboard re-import required.** The 37 concept URIs all change (subdomain of namespace shifts from `/v1/primitives/` to `/v1#`). The 23 PROV-O alignments preserve their semantics across the move. All five Termboard quality rules (circular definition, includes anti-pattern, TOP acronym, parent-in-description, em-dashes) remain at zero violations after the rename.
- **Legacy clinical-research namespace still uses `top:`.** The legacy `top:Sponsor`, `top:Study`, `top:Site` URIs in `reference-graphs/clinical-trials/` are now technically colliding with the new Core URIs. The clinical files are unchanged in this PR; the rebase to `topcr:` is the next priority precisely because it removes this last inconsistency. The homepage and namespaces page already flag this with a "Namespace rebase queued" badge so readers see the planned end state.
- **Several stale documents (TAXONOMY.md, core/v1/shapes.ttl) carry pending-rewrite banners.** They predate the current architecture and will be rewritten in a follow-up pass. Banners point readers to the authoritative sources (taxonomy/taxonomy.ttl and core/v1/index.html) so confusion is bounded.

### What this does NOT change

- The eight L1 categories, the twenty-eight L2 leaves, and the membership test that decides what lives at the universal layer. Pure rename.
- The 23 PROV-O `skos:exactMatch` / `skos:closeMatch` alignments. Same triples, same semantics, the subjects just carry new URIs.
- The provenance contract (identifier, observedAt, status) as the SHACL invariants enforced underneath every entity.
- The practitioner-first commitment from ADR-0013. "Core" is more practitioner-friendly than "Primitives," so this rename strengthens the constitutional commitment rather than weakening it.

### Status

Accepted. The artifacts on this branch implement the rename, the namespace collapse, the path move, and the file rename. Deferred: clinical-research namespace rebase to `topcr:`, rebuild of `core/v1/shapes.ttl` content (currently carries stale legacy content under a deprecation banner), JSON-LD context.jsonld for NGSI-LD wire compatibility, and rewrite of TAXONOMY.md to match current architecture.

---

## ADR-0015: Promote facts to entities — no bespoke flags

**Date:** 2026-05-11 · **Status:** Accepted · **Refs:** [FIRST-PRINCIPLES.md § Promote facts to entities](../FIRST-PRINCIPLES.md)

### Context

The clinical-research rebuild surfaced a recurring modeling temptation: when a Sponsor "is the sponsor of record" or "has regulatory responsibility," the natural reflex is to add boolean flags (`isSponsorOfRecord`, `hasRegulatoryResponsibility`, …). The earlier draft of Sponsor in `reference-graphs/clinical-trials/` carried four such flags plus a `regulatoryAuthorityScope` bespoke enum.

> "I don't like a bunch of Boolean flags — we need to do better."
>
> "Whenever you introduce a bespoke boolean, you take a strike at predictability. Now, for an object that inherits an evidence or an attestation primitive, then the system doesn't have to predict it. It understands what that meaning is."
>
> "In a lot of systems that I've seen in the past, relational databases are full of enums that only the database engineer who built them really truly understands, and it requires a lot of digging, again, digital archaeology."

Boolean flags and bespoke enums hide structure. The thing they hide — *who declared this, when, under what authority, against what scope, with what evidence, can it be revoked* — is exactly the kind of structure the Core categories were designed to absorb. Attestation, Constraint, StatusChange, Observation, Document each carry the time, authority, scope, and provenance that booleans throw away.

The current 8 Core categories (Agent, Location, Resource, Scope, Temporal, Evidence, Outcome, Constraint) were the result of a deliberate design pass to be the smallest set that covers the operator space. Every time a workflow extension reaches for a flag instead of a primitive, the architecture's predictability erodes. Without a principle that names this discipline, every clinical-research, manufacturing, supply-chain, and care-delivery workflow will independently rediscover the boolean trap.

### Decision

**A boolean is evidence in disguise — model the evidence.** Promoted from a modeling preference to a structural commitment.

The rule:

1. When reaching for a boolean property or a bespoke enum on a workflow-extension entity, ask: *who declares this true, when, under what authority?* If any of those has an answer, the boolean is hiding an Attestation, a Constraint, or a StatusChange — model the underlying entity.
2. Every entity in TOP traces to one of the 8 Core categories. A flag that can't be reified to a primitive is a flag that hasn't earned its place.
3. The discipline is purist but not dogmatic. If a real operator workflow surfaces a fact that none of the 8 absorbs cleanly, the path is an ADR proposing a new Core leaf — not a workaround through bespoke flags. The bar for a new primitive: at least two unrelated workflows need the same shape, and none of the existing 8 absorb it.

### Consequences

- **Predictability across workflows.** Every "is designated" claim is an Attestation in clinical-research, manufacturing, supply-chain, care-delivery. The same query patterns work everywhere.
- **PROV-O auditability flows through.** Attestation inherits PROV-O semantics via the Core hierarchy. Boolean flags inherit nothing.
- **Time and revocability become first-class.** A booleanized "is sponsor of record" can't answer "as of when, under what authority, and has that authority since revoked it?" An Attestation can.
- **No bespoke vocabulary tax.** Future contributors don't need to learn each workflow's private boolean dictionary. They read the Core categories, which are operator-vocabulary and stable.
- **The clinical-research rebuild applies this from the first commit.** Sponsor, sponsorships, regulatory designations, financial responsibilities, oversight authorities — all reify to Core primitives. No boolean flag escapes.
- **Some bespoke flags survive — when they meet the bar.** `staffRole` (finite, stable, operator-vocabulary, universally recognized across clinical-research) is fine. `portfolioType` (varies by sponsor org, drifts with reorg, every domain extends it differently) is not. The principle distinguishes between *operator vocabulary* and *engineer shorthand*; only the former earns its place.
- **The Core stays small.** The pressure released by this principle is the pressure to add bespoke flags. New Core primitives stay rare because most candidates resolve to existing primitives once the discipline applies.

### What this does NOT change

- Universal DNA stays at three properties (`top:identifier`, `top:observedAt`, `top:status`). Status is the one universal-level enum that survives; it represents lifecycle, not designation.
- The 8 Core categories stand. This principle protects them from drift; it doesn't add or remove any.
- Workflow extensions can still declare their own classes (e.g., `topcr:ClinicalSupplyChain rdfs:subClassOf top:Program`) — class-level specialization is fine when shape differs. The principle bites property-level flags, not class-level subclassing.

### Status

Accepted. FIRST-PRINCIPLES.md (and its .html mirror) carry the canonical rule as a fourth structural commitment alongside operator-grounded vocabulary, native temporal+provenance, and universal pattern. The clinical-research rebuild applies this discipline from its first commit.

---

## How to add an ADR

1. Pick the next number in sequence.
2. Open a PR adding a new section to this file. Title format: `ADR-NNNN: Short imperative phrase`.
3. Required fields: Date, Status (Proposed / Accepted / Superseded by ADR-N), Context, Decision, Consequences. Refs to artifacts and PRs are encouraged.
4. If the ADR supersedes a prior one, mark the prior ADR's status as `Superseded by ADR-N` in the same PR. Don't delete it.
5. Quoting the conversation that forced the decision is welcome — the operator's actual words usually capture the question better than any rewrite.
