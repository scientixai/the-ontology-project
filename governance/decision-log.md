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
| [ADR-0016](#adr-0016-schemaorg-alignment-where-the-peer-is-honest) | 2026-05-11 | schema.org alignment — where the peer is honest | Accepted |
| [ADR-0017](#adr-0017-monorepo-with-directory-scoped-ownership) | 2026-05-12 | Monorepo with directory-scoped ownership | Accepted |
| [ADR-0018](#adr-0018-adopt-the-six-stage-ontology-pipeline-as-tops-build-discipline) | 2026-05-13 | Adopt the six-stage ontology pipeline as TOP's build discipline | Accepted |
| [ADR-0019](#adr-0019-open-core-constrained-extension-three-flavors-per-core-property) | 2026-05-13 | Open Core, constrained extension — three flavors per Core property | Accepted |
| [ADR-0020](#adr-0020-add-toporganism-as-the-fifth-agent-leaf) | 2026-05-13 | Add `top:Organism` as the fifth Agent leaf | Accepted (resolves ADR-0018 forward-looking note) |
| [ADR-0021](#adr-0021-bitemporal-model-valid-time-and-transaction-time-on-core) | 2026-06-19 | Bitemporal model — valid time and transaction time on Core | Accepted |

---

## ADR-0001: Temporal and PROV native at the foundation

**Date:** 2026-05-08 · **Status:** Accepted · **PR:** [#8](https://github.com/scientixai/the-ontology-project/pull/8) · **Refs:** [first-principles.md § Temporal and provenance, native](../first-principles.md)

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

**Date:** 2026-05-08 · **Status:** Accepted · **PR:** [#9](https://github.com/scientixai/the-ontology-project/pull/9) · **Refs:** [first-principles.md § Universal foundation](../first-principles.md)

### Context

A draft of the Visit lift introduced `VisitObservation` as a specialized entity type. That triggered a question: do we keep adding specialized types every time a workflow expresses a shape, or do we treat the foundation as universal containers that get specialized through *content* rather than *shape*?

### Decision

Cross-cutting shapes (Activity, Task, observation) are expressed as universal containers in the foundation. Specialization happens through reference data, role bindings, and projection — not by minting new entity types every time a workflow expresses the same shape with different content.

### Consequences

- The foundation stays small and stable. Shapes that recur across workflows are recognizable.
- This decision sets up the question that ADR-0007 and ADR-0008 answer in the affirmative: if cross-cutting shapes belong to the universal layer, *which layer is that*, and how does workflow-specific specialization actually attach?

---

## ADR-0003: Correct the namespace mislabeling — `top:` is the project

**Date:** 2026-05-09 · **Status:** Accepted · **Refs:** [taxonomy.md § Three layers](../taxonomy.md)

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

**Date:** 2026-05-09 · **Status:** Accepted · **Refs:** [taxonomy.md § Workflow extensions](../taxonomy.md)

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

**Date:** 2026-05-09 · **Status:** Accepted · **Refs:** [taxonomy.md § URI conventions](../taxonomy.md)

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

**Date:** 2026-05-09 · **Status:** Accepted · **PR:** [#13](https://github.com/scientixai/the-ontology-project/pull/13) · **Refs:** [`taxonomy/taxonomy.ttl`](../taxonomy/taxonomy.ttl), [`taxonomy/taxonomy.csv`](../taxonomy/taxonomy.csv), [taxonomy.md](../taxonomy.md)

### Context

The taxonomy needs to be importable into the tools ontologists actually use (TermBoard, PoolParty, Synaptica, Protégé) without bespoke adapters, and it needs to be legible to non-ontologists who are reviewing names and definitions.

### Decision

Author the taxonomy in SKOS Turtle as the source of truth (`taxonomy/taxonomy.ttl`). Ship a CSV companion (`taxonomy/taxonomy.csv`) for spreadsheet review and a Markdown narrative (`taxonomy.md`) for human readers. Each concept declares `skos:Concept` + `skos:inScheme top:TaxonomyV1` + `skos:broader` + `skos:prefLabel` + `skos:definition` + `skos:notation`, plus `rdfs:subClassOf` and PROV typing where applicable.

### Consequences

- The taxonomy round-trips through TermBoard and equivalent tools.
- The CSV is the curator's working surface; the Turtle is the system of record; the Markdown is the readers' entry point.
- Every concept in the foundation is now traceable to a single canonical record.

---

## ADR-0007: Option B — commons as vocabulary, workflows as shape

**Date:** 2026-05-09 · **Status:** Accepted (refined by ADR-0008) · **Refs:** [taxonomy.md](../taxonomy.md)

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

**Date:** 2026-05-09 · **Status:** Accepted · **Supersedes part of ADR-0007** · **Refs:** [taxonomy.md § Three layers](../taxonomy.md), [`taxonomy/taxonomy.ttl`](../taxonomy/taxonomy.ttl)

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

**Date:** 2026-05-09 · **Status:** Accepted · **Refs:** [taxonomy.md § Drift prevention](../taxonomy.md)

### Context

ADR-0008 and ADR-0009 only work if domains *actually use* the commons primitives instead of redefining their own. The FIWARE failure mode is exactly drift: every domain reinvents Document because nobody enforces against it.

> "The curation in my mind is how we keep this structure pure without drift — how do you enforce against domains creating replications of commons primitives?"

### Decision

Drift prevention runs on four layers, each catching what the layer above it might miss:

1. **Lint rules (mechanical).** SHACL meta-shapes in `taxonomy/meta-shapes.ttl` validate the taxonomy itself. Rules: every workflow-extension concept that names a commons-primitive label must declare `rdfs:subClassOf` on that primitive; no workflow extension may declare a concept with the same `skos:prefLabel` as a commons primitive without a `subClassOf` edge; deprecated concepts must declare `dct:isReplacedBy`.

2. **RFC process (procedural).** New concepts arrive as RFCs in `governance/rfcs/`. The RFC template (forthcoming) requires the proposer to answer: *Is there a commons primitive this should specialize? If no, why not?* The default answer is "yes, specialize"; "no" must be argued.

3. **Working group curation (human).** The TaxonomyWG reviews every RFC for layer assignment before approving. The WG owns the call on whether a proposed concept belongs in commons or in a workflow extension.

4. **Documentation discipline (cultural).** taxonomy.md, this decision log, and first-principles.md are the references contributors are expected to read before opening an RFC. New contributors who try to add a duplicate primitive get pointed at the relevant ADR rather than into a long discussion.

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

**Date:** 2026-05-09 · **Status:** Accepted · **Refines:** [ADR-0012](#adr-0012-three-level-architecture-universal-dna-eight-categories-leaves) · **Refs:** [`commons/source/core.ttl`](../commons/source/core.ttl), [first-principles.md](../first-principles.md), [manifesto.html](../manifesto.html)

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
- **Several stale documents (taxonomy.md, core/v1/shapes.ttl) carry pending-rewrite banners.** They predate the current architecture and will be rewritten in a follow-up pass. Banners point readers to the authoritative sources (taxonomy/taxonomy.ttl and core/v1/index.html) so confusion is bounded.

### What this does NOT change

- The eight L1 categories, the twenty-eight L2 leaves, and the membership test that decides what lives at the universal layer. Pure rename.
- The 23 PROV-O `skos:exactMatch` / `skos:closeMatch` alignments. Same triples, same semantics, the subjects just carry new URIs.
- The provenance contract (identifier, observedAt, status) as the SHACL invariants enforced underneath every entity.
- The practitioner-first commitment from ADR-0013. "Core" is more practitioner-friendly than "Primitives," so this rename strengthens the constitutional commitment rather than weakening it.

### Status

Accepted. The artifacts on this branch implement the rename, the namespace collapse, the path move, and the file rename. Deferred: clinical-research namespace rebase to `topcr:`, rebuild of `core/v1/shapes.ttl` content (currently carries stale legacy content under a deprecation banner), JSON-LD context.jsonld for NGSI-LD wire compatibility, and rewrite of taxonomy.md to match current architecture.

---

## ADR-0015: Promote facts to entities — no bespoke flags

**Date:** 2026-05-11 · **Status:** Accepted · **Refs:** [first-principles.md § Promote facts to entities](../first-principles.md)

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

Accepted. first-principles.md (and its .html mirror) carry the canonical rule as a fourth structural commitment alongside operator-grounded vocabulary, native temporal+provenance, and universal pattern. The clinical-research rebuild applies this discipline from its first commit.

---

## ADR-0016: schema.org alignment — where the peer is honest

**Date:** 2026-05-11 · **Status:** Accepted · **Refs:** [`taxonomy/taxonomy.ttl`](../taxonomy/taxonomy.ttl), [ADR-0001](#adr-0001-temporal-and-prov-native-at-the-foundation), [ADR-0013](#adr-0013-practitioner-first-tops-primary-customer)

### Context

TOP Core ships with two existing standards alignments:

- **PROV-O** — `skos:exactMatch` / `closeMatch` in `taxonomy/taxonomy.ttl` and `rdfs:subClassOf prov:*` in `core/v1/shapes.ttl`. Per ADR-0001.
- **BFO** — `rdfs:subClassOf bfo:*` on the four BFO-clean L1 categories (Agent / Location / Temporal / Evidence) in `core/v1/shapes.ttl`. Per ADR-0013.

Reviewing the 8 categories and 28 leaves against schema.org surfaced the question of whether TOP is reinventing concepts schema.org already covers cleanly. The convener flagged the NIH-syndrome risk directly:

> "If we create our own spec without leveraging what's already out there, then I think we're off with our skis crossing over. […] We don't want to suffer from that awful disease that I call NIH syndrome, or not invented here syndrome."

The audit found:

- **Exact matches (7 of 28 leaves)** — `Person`, `Organization`, `Physical`, `Virtual`, `Project`, `Schedule`, `Observation` map cleanly to `schema:Person`, `schema:Organization`, `schema:Place`, `schema:VirtualLocation`, `schema:Project`, `schema:Schedule`, `schema:Observation`.
- **Close matches (10 of 28 leaves)** — `Group`, `System`, `Equipment`, `Material`, `Activity`, `Milestone`, `Document`, `Log`, `Credential`, `RegulatoryLaw` have schema.org peers with partial overlap (different shape but recognizably the same concept).
- **No peer (11 of 28 leaves)** — `AutonomousAgent`, `Storage`, `Portfolio`, `Program`, `Window`, `Attestation`, `StatusChange`, `Artifact`, `Conclusion`, `PhysicalLimit`, `SafetyGuardrail` have no schema.org equivalent. schema.org's web-markup origins do not model regulated-industry concepts (constraints, attestations, state transitions, conclusions, safety guardrails). Inventing them here is justified.
- **The 8 categories themselves** — Agent / Location / Resource / Scope / Temporal / Evidence / Outcome / Constraint — are a TOP-original abstraction layer. schema.org is a flat-ish type system rooted at `schema:Thing` with no comparable categorical layer. The 8 categories are a TOP contribution, not a reinvention.

### Decision

Declare schema.org alignment in `taxonomy/taxonomy.ttl` using the same `skos:exactMatch` / `skos:closeMatch` pattern already in place for PROV-O. Document the absences (the 11 leaves without a schema.org peer) inline so the gap is intentional and not an oversight.

The alignment is taxonomy-level only — `taxonomy/taxonomy.ttl` carries the `skos:*Match` triples. No `rdfs:subClassOf schema:*` triples are added to `core/v1/shapes.ttl`. schema.org's class semantics differ from PROV-O's in ways that don't always map cleanly to OWL inheritance; SKOS mappings give schema.org-aware tools the alignment they need without forcing structural commitments TOP shouldn't take on.

### Consequences

- **schema.org-aware tools interpret TOP without bridge adapters.** Web crawlers, search engines, LLMs trained on schema.org, JSON-LD adopters all get a recognizable entity surface where the peer exists.
- **The NIH-syndrome risk is closed off transparently.** Future contributors auditing TOP against schema.org find the alignment declared explicitly. Where TOP invents (Attestation, Constraint leaves, Portfolio, Program), the absence is documented with the reason: schema.org doesn't model regulated-industry concerns.
- **The pattern generalizes.** Future alignments against FHIR, FOAF, Dublin Core (for record-level metadata), or domain-specific standards follow the same approach: SKOS mappings in `taxonomy/taxonomy.ttl`, absences documented inline, ADR recording the audit.
- **TOP stays the operator-vocabulary anchor.** Per ADR-0013, the practitioner is the primary customer. schema.org alignment is edge-only — it serves consumers (search engines, AI tools) without shaping TOP itself. The same posture as BFO and PROV-O alignment.

### What this does NOT do

- It does not add schema.org as an `rdfs:subClassOf` parent to any TOP class. Inheritance commitments stay with PROV-O (class-level) and BFO (light, edge-only on four categories). schema.org's semantics aren't suited to structural inheritance.
- It does not commit TOP to schema.org's evolution cadence. schema.org versions; the mapping is reviewed when the peer concept changes, not on every schema.org release.
- It does not reduce the 8-category or 28-leaf set. The categorical layer and the leaves stay; alignment is overlay, not replacement.

### Future alignments to consider (not part of this ADR)

- **FHIR R5** — clinical-research workflow extensions will need this. FHIR resources (`Patient`, `Encounter`, `MedicationKnowledge`, `Observation`, `AdverseEvent`) map to clinical-research-specific subclasses of Core leaves, not to Core leaves directly. Handled at the workflow-extension level.
- **FOAF** — overlaps with schema.org's Person/Organization but adds social-network semantics TOP doesn't need.
- **Dublin Core** — already used in `core/v1/shapes.ttl` (`dct:title`, `dct:created`, `dct:license`) for record-level metadata. Per ADR-0013, Dublin Core handles record metadata; PROV-O handles domain provenance.

### Status

Accepted. `taxonomy/taxonomy.ttl` carries 7 exactMatch + 10 closeMatch triples plus inline comments documenting the 11 absences.

---

## ADR-0017: Monorepo with directory-scoped ownership

**Date:** 2026-05-12 · **Status:** Accepted · **Refs:** [`.github/CODEOWNERS`](../.github/CODEOWNERS), [`governance/working-groups.md`](working-groups.md), [`governance/rfcs/README.md`](rfcs/README.md), [`governance/branch-protection.md`](branch-protection.md), [`CONTRIBUTING.md`](../CONTRIBUTING.md)

### Context

TOP today is a single repository at [scientixai/the-ontology-project](https://github.com/scientixai/the-ontology-project), with the convener as the review pool of one. Core has stabilized (ADRs 0012–0014); the pre-Core artifacts are archived under `legacy/` (PR #23); doc filenames are lowercased for URL hygiene (PR #24). The clinical-research workflow rebuild is queued next. Before the rebuild begins and additional workflow extensions follow, the project needs a structural answer to *how TOP manages multiple domains over time across multiple working groups.*

Three structural options were considered:

1. **Monorepo** — single repository, all working groups contribute, directory-scoped ownership via `CODEOWNERS`.
2. **Polyrepo with git submodules** — Core in one repo, each workflow in its own repo, parent repo pulls them in as submodules.
3. **Polyrepo with cadence-based imports** — Core and each workflow in separate repos; a release pipeline assembles `top.scientix.ai` from pinned versions.

Submodules are conceptually clean but operationally cursed (detached HEADs, stale pointers, brittle CI). Cadence-based imports work for releases (the Linux-distribution pattern) but add real cost during active development and require a build pipeline that TOP does not yet need. Monorepo, paired with directory-scoped ownership and an RFC process for structural change, handles the multi-WG case at TOP's current and reachable-future scale.

The convener's framing: *"Let's go with the best option now before we go down a path of a lot of work and then it's tough to unravel."* An earlier draft of this ADR (PR #20) was closed unmerged when clinical-research timing wasn't right; the structural decision was acknowledged but the procedural scaffolding was parked. With cleanup PRs #23 and #24 landed, the rebuild's start is the right moment to land the scaffolding.

### Decision

TOP stays a single repository. Working group ownership is enforced by:

1. **`.github/CODEOWNERS`** — each top-level directory has a designated owner. Pull requests modifying files in a directory require approval from at least one of that directory's owners. Cross-cutting changes require each affected owner's approval. Today every line resolves to `@bo-lora`; as WGs form, individual lines reassign to GitHub teams.

2. **`governance/working-groups.md`** — five-state lifecycle (Proposed → Forming → Active → Mature → Archived) for how a working group comes into being, operates, and dissolves. Each WG owns one or more directories; the WG's authority and accountability are mapped to those directories.

3. **`governance/rfcs/`** — the formal coordination mechanism for structural changes. RFCs are required for: changes to Core, cross-WG changes, governance changes, WG formation/dissolution, URI/namespace changes, and tooling/standards adoption. The cost is small (a markdown file, a PR, a review); the benefit is a durable artifact recording the decision.

4. **Branch protection** — `main` requires PR + CODEOWNER approval + linear history. No force pushes, no direct commits, no bypassing the rules. Documented in [`governance/branch-protection.md`](branch-protection.md) because branch protection is a GitHub Settings concern, not an in-repo file.

5. **Per-directory versioning** — each working group releases its directory on its own schedule (`core/v1/`, future `clinical-research/v1/`, etc.). No working group blocks any other; nobody waits for anyone else.

6. **Source topology and deployment topology are decoupled.** Today both are monorepo. If a workflow ever needs to spin out into its own repository, the deployment pipeline for `top.scientix.ai` can keep the public site unified across multiple source repositories. The deployment can adapt without forcing the source to.

7. **Submodules are explicitly rejected.** If polyrepo ever lands, it lands via deployment-time assembly, not version-controlled repo nesting.

### Consequences

- **Scales to many working groups without repo proliferation.** Ten WGs in one repository is fine when their ownership boundaries are honored at the directory level.
- **Operator trust grows on a single review surface.** Anyone tracking TOP can read every change in one place, file PRs against one place, and trust one set of governance rules.
- **GitHub Pages stays simple.** `top.scientix.ai` is served straight from `main`. No assembly pipeline, no submodule materialization, no release manifests.
- **Cross-cutting changes are atomic.** When Core renames a class (the Primitives → Core rename was an example), every affected workflow can be updated in the same commit. Polyrepo would have made that a multi-step coordinated dance.
- **Governance enforcement depends on GitHub features.** CODEOWNERS, branch protection, and required reviews are configured in GitHub Settings — not in the repository. The configuration is documented in [`governance/branch-protection.md`](branch-protection.md) so it can be reconstructed if it drifts.
- **The convener as review pool of one is the only practical operating mode today.** The structure documented here graduates cleanly as WGs form: rename a CODEOWNERS line to point at a team, raise the required-reviewer count if needed, no architectural rework.
- **Reassessment trigger documented.** If a specific WG's pace of change overwhelms the monorepo's PR queue, or if a working group requires repository-level autonomy that CODEOWNERS cannot deliver, a new ADR proposes spinning that WG out. The polyrepo + deployment-pipeline option stays available; it is not the default today.

### What this changes vs. earlier ADRs

This ADR is structural / process-level. It does not change any taxonomy, OWL/SHACL, or vocabulary decisions. It formalizes what TOP has been doing informally and adds the discipline that makes the informal mode scale.

It also supersedes the PR #20 draft (closed unmerged 2026-05-11) — the substance is the same; the timing was wrong then, right now.

### Status

Accepted. Artifacts shipping with this ADR: `.github/CODEOWNERS`, `governance/working-groups.md`, `governance/rfcs/README.md`, `governance/rfcs/0000-template.md`, `governance/branch-protection.md`, `CONTRIBUTING.md`.

After merge, the convener applies the branch-protection rules per `governance/branch-protection.md` in GitHub → Settings → Branches.

---

## ADR-0018: Adopt the six-stage ontology pipeline as TOP's build discipline

**Date:** 2026-05-13 · **Status:** Accepted · **Refs:** [first-principles.md § 7. Build the Pipeline in Order](../first-principles.md), [Ontology Pipeline (Talisman)](https://www.ontologypipeline.com/)

### Context

TOP's architectural history has surfaced a recurring pattern: each layer of the ontology build-out turns out to need a more foundational layer beneath it. The first lift was clinical-research entities (Sponsor, Site, Study, …); the namespace mislabeling forced the taxonomy work (ADR-0003); the Core architecture forced the universal-DNA + categorical structure (ADR-0012, ADR-0013); the schema.org audit forced the cross-vocabulary alignment discipline (ADR-0016). Each correction pushed the build one layer deeper into the stack.

A review of TOP Core against Talisman's [Ontology Pipeline](https://www.ontologypipeline.com/) (six stages: Controlled Vocabulary → Taxonomy → Metadata Schema → Thesaurus → Ontology → Knowledge Graph) made the gap explicit: **TOP did the taxonomy first and skipped the controlled vocabulary layer entirely.** The taxonomy held because the eight categories and twenty-eight leaves are operator-grounded, but the layer above (metadata schema, with per-leaf SHACL property shapes) and the layer two-above (thesaurus, with SKOS-XL labels and cross-vocabulary mappings) never had a CV foundation to build on. The result was a strong taxonomy supporting partial layers above it.

The same gap will surface in every workflow extension that lifts on TOP, and in every customer-built knowledge graph, unless the build discipline is named structurally.

### Decision

TOP adopts the six-stage ontology pipeline as its build discipline, structurally and permanently:

1. **Controlled Vocabulary** — per concept, deduplicated and disambiguated synonyms (with provenance), anti-synonyms (with rationale), per-property enum vocabularies, context-routing for homonyms.
2. **Taxonomy** — hierarchical organization (already in place at Core v1; ADR-0012).
3. **Metadata Schema** — per-concept SHACL property shapes, NGSI-LD JSON-LD contexts, SSSOM crosswalk manifests.
4. **Thesaurus** — SKOS-XL labels as first-class objects with provenance; cross-concept `skos:related` relations; mapping properties across vocabularies.
5. **Ontology** — OWL classes and properties with axioms; PROV-O class-level alignment; BFO alignment on clean categories.
6. **Knowledge Graph** — instances at scale (workflow extensions, customer deployments).

**Each layer is the precondition for the next.** A concept may be lifted with the CV and taxonomy authored first and the metadata schema, thesaurus, and ontology added in subsequent PRs. The reverse is forbidden — no concept ships only its ontology layer; no taxonomy entry exists without a corresponding CV record.

**The discipline applies to:**
- TOP Core itself (the eight categories + twenty-nine leaves currently at L1/L2 of the taxonomy)
- Every workflow extension (clinical-research first, then care-delivery / manufacturing / supply-chain / others)
- Every customer-built knowledge graph on TOP

**Three CV-layer obligations carry forward:**

1. **Context routing** for homonyms. *Subject* (Person in human research; LabAnimal in animal research), *agent* (an Agent in TOP; a Material in pharmacology) — every concept with homonym risk declares its `contextRouting` and `antiSynonym` blocks at CV authoring time.
2. **Per-property enums as CVs in their own right.** A status enum, a severity enum, a category enum each gets a CV record with operator-meaningful value definitions, inbound synonyms, anti-synonyms.
3. **Crosswalks as first-class SSSOM artifacts.** Per Core concept (and per workflow concept, mapping to its parent Core concept), an SSSOM TSV declaring mappings to PROV-O, BFO, schema.org, FHIR, USDM, SDTM, MedDRA, NCIt, LOINC, SNOMED, and any other peer vocabulary where the alignment is honest. Not buried in `@context` files; not buried in inline `owl:equivalentClass` declarations. SSSOM is the format the OBO Foundry community already consumes.

### Consequences

- **Every future concept-introduction PR is audited against the pipeline.** A reviewer can ask: *does this concept have a CV record? a taxonomy entry? a SHACL shape? a thesaurus entry? a crosswalk file?* The reviewer expects all six (or a declared roadmap for the missing ones).
- **The CV layer is now load-bearing.** A back-fill pass is required for the current twenty-nine Core leaves — one YAML per leaf under `core/v1/vocabulary/`, with synonyms, anti-synonyms, context routing where applicable, and per-property enum CVs.
- **SKOS-XL upgrade follows the CV pass.** The current `taxonomy/taxonomy.ttl` carries plain SKOS labels; SKOS-XL promotes labels to first-class objects with provenance. The upgrade is mostly mechanical once the CV YAMLs exist.
- **SSSOM crosswalk files per leaf land alongside the SHACL property shapes.** Both generated from the same structured intermediate.
- **Workflow extensions adopt the pipeline from their first PR.** The clinical-research rebuild does not lift an entity without authoring its CV first, then its taxonomy entry, then its SHACL shape, then its thesaurus entry, then its OWL class.
- **The OBO Foundry / Mondo / Bioregistry community gains an obvious read.** TOP's crosswalks in SSSOM are the format they already consume.

### What this ADR does NOT commit to

- A timeline. The discipline is permanent; the execution is per-leaf and per-workflow as work progresses.
- A specific authoring format. YAML for the CV layer (round-tripped to SKOS-XL via a small emitter) is a reasonable default; the format is a working-group decision.
- A specific crosswalk target list. The audit list per concept is curated, not mandated.

### Forward-looking notes (not part of this ADR)

- **The CV back-fill may surface a `top:Organism` (or `top:LivingSubject`) Core leaf** — the *Subject* homonym suggests that when the second life-sciences workflow extension lifts (animal research, comparative medicine, plant research, microbial research), the Agent category may need an Organism leaf with Person as a specialization. Documented as a trigger, not a decision. *Resolved 2026-05-13 by [ADR-0020](#adr-0020-add-toporganism-as-the-fifth-agent-leaf): added as a sibling leaf alongside Person rather than as a parent of Person, because Person carries practitioner-specific Universal DNA and PROV-O alignment (`prov:Person`) that should not be diluted through an intermediate Organism class.*
- **The CV back-fill may surface a need to clarify `top:Material` scope** to include biological substances (proteins, antibodies, cell-line aliquots) explicitly — the *agent (pharmacological)* anti-synonym routes here.

### Status

Accepted. The first-principles.md § 7 carries the canonical statement; this ADR records the decision.

---

## ADR-0019: Open Core, constrained extension — three flavors per Core property

**Date:** 2026-05-13 · **Status:** Accepted · **Refs:** [first-principles.md § 8. Open Core, Constrained Extension](../first-principles.md), [governance/extension-contract.md](extension-contract.md), [core/v1/shapes.ttl](../core/v1/shapes.ttl)

### Context

TOP's central architectural bet is that one universal Core can serve every regulated industry. Workflow extensions (clinical research, care delivery, manufacturing, supply chain, …) and customer-built knowledge graphs all compose on top of the same Core, declare their own classes via `subClassOf`, and inherit Core's PROV-O / BFO / schema.org alignments automatically.

The risk this creates is the classical extensibility tradeoff: a Core open enough for every consumer to specialize without forking can also be open enough for two consumers to model the same logical concept in mutually unintelligible ways. The pattern surfaces in any ontology project that takes the one-Core-many-extensions bet without naming the per-property limits: extensions proliferate without discoverability; the same concept gets modeled multiple ways across consumers; profiles diverge over time. The structural failure isn't anyone's fault — it's what an unspecified extension surface produces over a decade of independent specialization.

TOP integrates with peer ontologies (FHIR, USDM, SDTM, MedDRA, NCIt, LOINC, SNOMED, …) at the projection edge — the Broker and equivalent adapters ingest peer-ontology data and normalize it into NGSI-LD entities against Core. The Core itself, where TOP commits to a stable shape, needs a per-property discipline that names what consumers may and may not change. That discipline is this ADR.

### Decision

Every Core property declares one of three extensibility flavors, machine-annotated in the OWL/SHACL artifact and machine-enforced at PR time:

| Flavor | What it means | Extension permitted? |
| --- | --- | --- |
| **Invariant** | Stable across every workflow and every customer. Type, range, cardinality, semantics cannot drift. | No. Tightening allowed (a workflow may require what Core makes optional); redefinition forbidden. |
| **Tightenable** | Stable shape; downstream consumers may add SHACL constraints (require what Core makes optional, narrow an enum, bind a value set, tighten cardinality). | Tightening only. |
| **Additive** | A surface specifically designed for downstream addition (custom synonyms in CV, custom subclasses via `subClassOf`, additive enum values that extend rather than replace Core values). | Yes. Additions live in the consumer's namespace; Core terms remain valid. |

The flavor is declared via a `top:flavor` annotation property on each Core SHACL property shape (and each Core OWL class where the principle applies).

**Per-layer extension contract.** The flavor discipline extends through every pipeline layer (per ADR-0018). The full per-layer rules — what a consumer MAY do, what a consumer MUST NOT do, how the rules are enforced at each layer — are documented in [`governance/extension-contract.md`](extension-contract.md). Summary:

- **Controlled Vocabulary.** Consumers add synonyms in their namespace; add per-property enum values where Core marked the enum additive; add disambiguation notes scoped to their context. Cannot redefine canonical labels, remove or reassign Core synonyms, or conflict with Core enum values.
- **Metadata Schema.** Consumers add properties via `subClassOf`, tighten Core SHACL constraints, add their own SSSOM crosswalks. Cannot redefine Core property types, loosen Core constraints, or use the Core namespace for custom additions.
- **Thesaurus.** Consumers declare their own SKOS concept schemes that map to Core via the `skos:*Match` properties. Cannot modify the Core scheme or add `skos:broader` / `skos:narrower` edges between Core concepts.
- **Ontology.** Consumers subclass Core OWL classes, declare consumer properties as `subPropertyOf` Core properties. Cannot redeclare Core domains/ranges or add `owl:disjointWith` axioms involving Core classes.

**Enforcement.** A linter (`tools/lint_extension.py` — to be authored as a separate PR) reads any consumer's CV / SHACL / SKOS / OWL files and refuses changes that violate the contract. The linter runs in CI on every PR. Branch protection makes the linter required for merge.

### Initial flavor assignment

The current Core SHACL artifact (`core/v1/shapes.ttl`) carries 28 properties (3 Universal DNA + 25 category-level relational extensions). The initial flavor assignment, landed alongside this ADR:

- **Invariant (5 properties):** `top:identifier`, `top:observedAt`, `top:integrityHash`, `top:startTime`, `top:endTime`. These five carry semantics that cannot drift — globally unique identity, observation timestamp, cryptographic non-repudiation, temporal interval bounds. Any consumer redefining them breaks the audit-trail and federation guarantees Core exists to provide.
- **Tightenable (23 properties):** everything else, including `top:status` (Core leaves the enum open; workflows bind their own status sets), `top:hasCredential`, `top:memberOf`, `top:authorizedBy`, `top:withinLocation`, `top:geoSpatialData`, `top:accessRequirement`, `top:ownedBy`, `top:hasMaintenanceLog`, `top:operationalState`, `top:governedBy`, `top:containsActivity`, `top:objectiveStatement`, `top:precededBy`, `top:occursAt`, `top:verifiesOutcome`, `top:signedBy`, `top:measuredBy`, `top:satisfiesConstraint`, `top:variance`, `top:enforcedBy`, `top:severityLevel`, `top:appliesTo`.
- **Additive (0 properties currently):** no Core property today is designed for additive extension at the property level. Additive flavors land when Core properties bind value sets (e.g., a future `documentType` or `eventCategory`) where workflow extensions are expected to add domain-specific values.

The two Invariant Universal DNA properties (`top:identifier`, `top:observedAt`) are the strongest commitment in the artifact — no workflow extension and no customer can loosen, retype, or redefine them. `top:status` is the third Universal DNA property; it is Tightenable rather than Invariant because Core deliberately leaves its value set open for workflow specialization.

### Consequences

- **Downstream extensions become safe by construction.** A customer adding `acme:Document subClassOf top:Document` knows precisely what they may and may not change. The linter refuses violations at PR time.
- **The FHIR failure mode is structurally prevented.** Two extensions of the same Core concept cannot diverge into mutually unintelligible parallel implementations.
- **AI agents trained on Core read consumer extensions correctly.** An agent encountering `acme:LEAVE_OF_ABSENCE` walks the SKOS-XL chain to `top:Person.status` and knows it is a Person status value, even though the agent was trained on Core only.
- **The Core stays small.** Every property earns its place. The pressure to add new Core properties is balanced by the cost of pinning their flavor declaration.
- **Reviewers can audit any consumer extension in under five minutes.** The flavor metadata is visible; the linter output is precise; the per-layer contract is one document.

### What this ADR does NOT do

- It does not declare additional Core properties beyond the current 28. New properties land via their own PRs; each carries its flavor declaration at introduction.
- It does not author the linter. The linter is a separate PR; this ADR commits to its existence in CI before workflow extensions begin to lift consumer entities.
- It does not preclude future flavor introductions. If the per-layer contract surfaces a need for additional flavors (e.g., "Deprecating"), a new ADR adds them; this ADR does not foreclose.

### Status

Accepted. The flavor annotations land in `core/v1/shapes.ttl` alongside this ADR. The full per-layer extension contract is in `governance/extension-contract.md`. The linter is a follow-on PR.

---

## ADR-0020: Add `top:Organism` as the fifth Agent leaf

**Date:** 2026-05-13 · **Status:** Accepted · **Refs:** [taxonomy.md § L2 — The twenty-nine leaves](../taxonomy.md), [taxonomy/taxonomy.ttl](../taxonomy/taxonomy.ttl), [core/v1/shapes.ttl](../core/v1/shapes.ttl), [ADR-0018 forward-looking note](#adr-0018-adopt-the-six-stage-ontology-pipeline-as-tops-build-discipline)

### Context

ADR-0018's forward-looking notes flagged that the CV back-fill — particularly the *Subject* homonym (Person in human research; living non-human in animal / plant / microbial research) — would likely surface a `top:Organism` Core leaf. The trigger arrived earlier than expected: while building out the practitioner walkthrough and reviewing the Agent category's coverage, it became clear that TOP today has no honest home for laboratory animals, livestock under veterinary care, plants in agricultural trials, microbial cultures in fermentation, or model organisms in biology studies. These are operational subjects across multiple regulated industries (clinical-research adjuncts, veterinary medicine, agriculture, food production, biopharma manufacturing), they are not `top:Person` (the human actor), and they are not `top:Material` (a substance consumed or transformed).

Two structural options surfaced:

- **Option A:** Add `top:Organism` as a fifth sibling leaf under `top:Agent` alongside Person, Organization, Group, and AutonomousAgent.
- **Option B:** Add `top:Organism` as an intermediate Agent and make `top:Person rdfs:subClassOf top:Organism`. Honors the biological hierarchy (humans are living organisms) and aligns Person under a more general Agent class.

> "i think option a is the best"

### Decision

Adopt **Option A**: `top:Organism` is the fifth sibling leaf under `top:Agent`, alongside `top:Person`, `top:Organization`, `top:Group`, and `top:AutonomousAgent`. `top:Person` retains its direct subclass relationship to `top:Agent` and its `prov:Person` alignment without an intermediate Organism layer.

The definition: an Agent that is a living biological entity acting or being acted upon in an operational context — laboratory animals in research, livestock under veterinary care, plants in agricultural trials, microbial cultures in fermentation, model organisms in biology studies. Distinct from Person (the human actor) and from Material (a substance consumed or transformed).

PROV-O alignment: `top:Organism skos:closeMatch prov:Agent` (close match, not exact — PROV-O's Agent admits any actor that can be attributed an action; Organism is the non-human-living subset, which is operationally meaningful in TOP but has no exact peer in PROV-O).

Schema.org alignment: none (schema.org has no honest peer for non-human living agents; Organism joins the absence list).

BFO alignment: deferred. `bfo:Organism` is a candidate alignment at the leaf level if and when OBO Foundry interop demands it; not forced at this ADR.

CV-layer context routing for the *Subject* homonym: in human research, *Subject* routes to `top:Person`; in animal / plant / microbial research, *Subject* routes to `top:Organism`. The CV YAML for each leaf (forthcoming per ADR-0018) declares the `contextRouting` and `antiSynonym` blocks that disambiguate by source vocabulary.

### Rationale — why Option A over Option B

- **Practitioner clarity (per ADR-0013).** Operators in animal research, agriculture, and fermentation do not say "the Person we are dosing"; operators in human research do not say "the Organism we are enrolling." Making Person a subclass of Organism conflates two operationally distinct concepts behind a shared parent that nobody asks for at the practitioner layer.
- **PROV-O alignment is cleaner.** `top:Person rdfs:subClassOf prov:Person` is the direct, defensible alignment. Routing Person through an intermediate Organism class that itself maps only to `prov:Agent` (close match) would dilute the alignment for the most-used Agent leaf.
- **Workflow extensions stay clean.** A clinical-research `Investigator subClassOf top:Person` carries the right semantics; a veterinary-research `AnimalSubject subClassOf top:Organism` carries the right semantics. Neither workflow needs to traverse an Organism intermediate to reach Person.
- **The biological hierarchy is honored where it matters — in the BFO / OBO alignment at the leaf level, not in the practitioner-facing Core taxonomy.** When (or if) the OBO Foundry alignment lands, `top:Organism rdfs:subClassOf bfo:Organism` and `top:Person rdfs:subClassOf bfo:Organism` (transitively, via Person's leaf-level BFO alignment) both hold without forcing the Core taxonomy itself to express the biological subclass relationship.

### Consequences

- **Core grows from 28 to 29 leaves.** The eight-category structure is unchanged; only the Agent category's leaf count moves from 4 to 5.
- **The "Subject" homonym now has two honest landing points in Core.** Workflow extensions disambiguate via the CV-layer context routing per ADR-0018.
- **Animal-research / veterinary / agricultural workflow extensions are now expressible against Core without abuse of `top:Person` or `top:Material`.** A future workflow extension declares `vetcare:AnimalSubject subClassOf top:Organism`; an agriculture workflow declares `agtrial:PlantSubject subClassOf top:Organism`; a biopharma manufacturing workflow declares `biomfg:MicrobialCulture subClassOf top:Organism`.
- **ADR-0018's forward-looking note is resolved.** The "may surface a `top:Organism` Core leaf" trigger is now a landed decision.
- **CV back-fill scope grows by one leaf.** The forthcoming `core/v1/vocabulary/agent/organism.yaml` carries the synonyms (Living Subject, Specimen, Subject (life-sciences), animal subject, lab animal, study organism, model organism, plant subject, culture), the anti-synonyms (Person, Material, Specimen-when-substance), and the context routing rules for the *Subject* homonym.
- **No counts-only churn in workflow extensions.** Workflow extensions that referenced Agent's leaf count by number rather than by name update once; those that referenced Agent by named leaves (Person / Organization / Group / AutonomousAgent) need no edit.

### What this ADR does NOT do

- It does not commit to a BFO alignment for `top:Organism` at this time. The OBO interop is the natural place for one; the alignment lands when OBO Foundry consumption demands it.
- It does not author the CV YAML for `top:Organism`. The CV back-fill is per-leaf work tracked under ADR-0018.
- It does not introduce a `top:LivingSubject` synonym leaf. The CV layer carries the synonym; the Core taxonomy carries one canonical concept.
- It does not change `top:Person`'s alignment, parentage, or Universal DNA obligations. Person remains a direct subclass of `top:Agent` with `prov:Person` exact-match alignment.

### Status

Accepted. The Organism leaf lands in `taxonomy/taxonomy.ttl` and `core/v1/shapes.ttl` alongside this ADR; the count references in README.md, taxonomy.md, governance/extension-contract.md, and core/v1/index.html update from 28 to 29.

## ADR-0021: Bitemporal model — valid time and transaction time on Core

**Date:** 2026-06-19 · **Status:** Accepted (2026-06-20) · **Extends:** [ADR-0001](#adr-0001-temporal-and-prov-native-at-the-foundation), [ADR-0013](#adr-0013-practitioner-first-tops-primary-customer) · **Refs:** [ADR-0009](#adr-0009-specialization-pattern-workflow-concepts-extend-commons-primitives-via-subclassof), [ADR-0015](#adr-0015-promote-facts-to-entities-no-bespoke-flags), [ADR-0019](#adr-0019-open-core-constrained-extension-three-flavors-per-core-property), [core/v1/shapes.ttl](../core/v1/shapes.ttl), [first-principles.md § 4](../first-principles.md), [FIWARE lessons](planning/fiware-smart-models-lessons.md)

> **Accepted 2026-06-20.** The maintainer ratified all four sign-off questions as recommended (see *Ratified decision*, below). The bitemporal vocabulary and Tier-1 enforcement land in `core/v1/shapes.ttl` alongside this acceptance. The proposal text below is retained as the reasoning of record.

### Context

ADR-0001 made temporal and PROV-O semantics native. What Core carries today is one timestamp axis, not two:

- **`top:observedAt`** (Universal DNA, required exactly once, `xsd:dateTime`, Invariant). Its comment reads "observed *or recorded*" — and that conflation is the bug: "observed" leans to *valid time* (when a fact became true in the world), "recorded" leans to *transaction time* (when the system learned it). One property cannot honestly be both.
- **`top:startTime` / `top:endTime`** on `top:Temporal` only — valid-time intervals, but only for activities, and only for the activity's own occurrence.

So Core is **mono-temporal in practice**: it answers "what does the record say now," but not, independently, "what did we *know* at T" versus "what was *true* at T." Regulated audit needs both — the canonical "as we knew it at T₁, as it was valid at T₂" query. This is the differentiator over single-clock value-over-time catalogs (NGSI-LD streams, JSON-Schema model libraries such as FIWARE Smart Data Models); see the [FIWARE lessons note](planning/fiware-smart-models-lessons.md).

Terms, fixed for this ADR: **valid time** — when a fact is true in the world; **transaction time** — when the system recorded it (append-only by nature); **bitemporal** — both axes, independently queryable.

Prior art: SQL:2011 system-versioned + application-time tables; the NGSI-LD temporal interface (TOP already echoes it — `observedAt` is NGSI-LD-shaped); W3C PROV revision/invalidation (`prov:generatedAtTime`, `prov:invalidatedAtTime`, `prov:wasRevisionOf`, `prov:specializationOf`).

### The pivot: entities are composed, so versioning is per-attribute

The decisive design fact is a granularity mismatch:

- **PROV-O entities are immutable, whole-thing snapshots.** A `prov:Entity` is a fixed aspect of a thing; any change mints a *new* entity linked by `prov:wasRevisionOf`. PROV's natural grain is the whole entity.
- **NGSI-LD entities are the opposite** — dynamically composed bags of attributes, each updating independently, each carrying its own `observedAt` / `createdAt` / `modifiedAt`, queried per-attribute.

If TOP versioned the *whole entity* on every field change (naive Option A, below), a patient whose weight, status, and address move on independent schedules would clone the entire entity each time — snapshot explosion — and discard the per-attribute history NGSI-LD gives for free.

Resolution: **PROV-O is granularity-agnostic.** Apply the immutable-snapshot + revision semantics at the **attribute-instance** grain (which is *naturally* immutable — "weight = 80 kg, recorded March 5" never changes), and treat the NGSI-LD entity as a `prov:Collection` **composed at query time** from the currently-selected attribute instances. This *deepens* the PROV-O commitment (PROV now works at both the attribute-revision grain and the entity-composition grain) rather than walking it back.

### Options

**Option A — immutable versioned records (event-sourcing), whole-entity grain.** New immutable version per change; `prov:wasRevisionOf` chains; corrections append.
- For: append-only audit fit (Part 11, GxP), one-to-one with PROV revision, per-version `integrityHash`.
- Against: at *whole-entity* grain it snapshot-explodes against composed/streaming entities and discards per-attribute history.

**Option B — dual intervals on the entity (SQL:2011).** `validFrom`/`validUntil` + `recordedFrom`/`recordedTo` on the entity.
- For: textbook-clean, compact, both axes explicit.
- Against: closing a transaction-time interval means *mutating* the prior row — the edit-in-place pattern append-only audit forbids; to stay honest you version anyway, collapsing toward A.

**Option C — NGSI-LD per-attribute temporal.** Each attribute instance carries its own valid + system time; temporal queries per-attribute.
- For: wire-compatible with the queued NGSI-LD profile; fine-grained; off-the-shelf brokers (Orion-LD, Scorpio, Stellio) implement the queries.
- Against: each attribute reifies into its own node — heavier shapes; and *if used alone* it lacks A's append-only revision discipline and B's explicit valid-time interval.

The real choice is **grain**, and no single option is complete on its own.

### Recommended decision (for sign-off, not yet binding)

**Adopt the attribute-grain synthesis: Option C's granularity + Option A's immutable append-only discipline + Option B's valid-time interval — with PROV revision as the semantics.**

1. **Transaction time stays the universal anchor; `top:observedAt` is disambiguated to mean it.** Sharpen its definition to "when this attribute-version was recorded by the system." It stays required, Invariant, unchanged in shape — the `UniversalDNAShape` minimum does not move and no existing data breaks.
2. **Valid time is Core-level but opt-in — not a fourth Universal DNA property.** Introduce `top:validFrom` / `top:validUntil` (`xsd:dateTime`, Invariant, mirroring `startTime`/`endTime`), governed by a *separate* opt-in `top:BitemporalShape` that targets only versioned attribute instances — **not** the always-on `UniversalDNAShape`.
3. **Each tracked attribute-value-at-a-time is an immutable `prov:Entity` instance**, carrying: `observedAt` (transaction time), `validFrom`/`validUntil` (valid time), `prov:wasRevisionOf` → the prior instance *of that same attribute*, and `prov:specializationOf` → a stable attribute-slot identity. A correction appends a new instance and closes the prior with `prov:invalidatedAtTime`; nothing is mutated.
4. **The entity is a `prov:Collection`**, reconstructed at query time by selecting, per attribute, the instance that satisfies the requested clock(s).

This gives genuine bitemporality, preserves append-only audit, reuses PROV at the grain NGSI-LD actually works in, and still projects to NGSI-LD on the wire.

### Triggering: which attributes get the treatment (semantic, not a manual switch)

Per-attribute reification is the cost; it must land only where it earns its place. The trigger is **entailed by what an attribute declares about itself**, in three tiers, off by default otherwise:

- **Tier 1 — structural entailment (automatic, Core-level, always-on).** An attribute carrying `top:integrityHash` or `top:signedBy`, or an entity that is a `top:Attestation` or `top:StatusChange`, **must** be an immutable version — you cannot hash or sign a value and then mutate it. No human tag required.
- **Tier 2 — propagation along regulated edges.** Audit-criticality flows across Core verbs: an `top:Outcome` that `top:satisfiesConstraint` a `top:RegulatoryLaw` / `top:SafetyGuardrail`, or a `top:Constraint` with `severityLevel` MAJOR/CRITICAL or `enforcedBy` a regulator, pulls its targets into the audited set.
- **Tier 3 — workflow-declared opt-in.** Domain attributes only the workflow knows are critical are marked by *tightening* Core per ADR-0019 (a Tightenable requirement of `BitemporalShape`). This is where "is patient weight a GxP field" is answered — in the clinical-research layer, not Core.
- **Default-off** for everything else (high-frequency telemetry, derived/recomputable metrics): the current single `observedAt`, no version chain.

Payoff of the attribute grain: one entity can carry a `signedBy` consent attribute on the full immutable chain *and* a lightweight streaming `heartRate` attribute at once — mixed sensitivity within one composed entity, each attribute getting exactly the treatment its semantics earn.

### Tier-1 SHACL enforcement (recommended: hard)

Tier 1 is the one part that is **always-on in Core** (the entailment "hash/signature ⇒ immutable" holds in every domain) and **enforced at `sh:Violation`** — a soft warning would let exactly the violation it guards against pass CI. Mechanism is SHACL Core, no SPARQL:

```turtle
# Presence of a cryptographic anchor SELECTS the node and REQUIRES the version contract.
top:SignedOrHashedMustVersion a sh:NodeShape ;
    sh:targetSubjectsOf top:integrityHash ;   # (a sibling shape targets top:signedBy)
    sh:node top:BitemporalShape ;
    sh:severity sh:Violation ;
    sh:message "A value carrying top:integrityHash must be an immutable version (top:validFrom + prov:specializationOf). You cannot hash a value and leave it mutable." .
```

**Lifecycle calibration:** hard (`sh:Violation`) on the *committed* markers — `integrityHash`, `signedBy`, `top:Attestation`, `top:StatusChange`; soft (`sh:Warning`) on *in-progress* evidentiary types — a `top:Document` / `top:Evidence` not yet hashed or signed (a draft protocol is legitimately mutable), which auto-hardens the instant an anchor is attached. Keying off cryptographic markers, not `status` enum strings, keeps this robust (the `status` value set is open/Tightenable).

**Named cost:** hard enforcement is **fail-closed at ingestion** — peer/legacy data (FHIR, USDM) carrying signatures/hashes but lacking the version apparatus is rejected at the boundary. That is correct (audit-bearing data should fail closed, not slip in half-modeled) but it relocates work to the Broker/projection layer, which must materialize `prov:specializationOf` + `validFrom` during the lift.

### Implied SHACL (illustrative — lands only on acceptance)

```turtle
# Opt-in, NOT folded into UniversalDNAShape. Targets versioned attribute instances.
top:BitemporalShape a sh:NodeShape ;
    sh:property [ sh:path top:validFrom ; sh:datatype xsd:dateTime ;
                  sh:minCount 1 ; sh:maxCount 1 ;
                  sh:message "A versioned value must state when its state became valid (top:validFrom)." ] ;
    sh:property [ sh:path top:validUntil ; sh:datatype xsd:dateTime ; sh:maxCount 1 ;
                  sh:message "top:validUntil is open (absent) for the currently-valid version." ] ;
    sh:property [ sh:path prov:specializationOf ; sh:minCount 1 ; sh:maxCount 1 ;
                  sh:message "Every version must point at its stable attribute-slot identity (prov:specializationOf)." ] .
```

`top:observedAt` (transaction time) continues to come from the always-on `UniversalDNAShape`; `validFrom`/`validUntil` and the revision links come from this opt-in shape. New properties carry ADR-0019 flavors (interval bounds Invariant, like `startTime`/`endTime`).

### Example as-of queries (the contract to ratify — Sign-off Question 3)

Each query selects, per attribute, the right instance, then composes the entity view.

```sparql
# (i) Transaction-time slice — "as we knew it on 2026-03-01" (latest instance recorded by then)
SELECT ?slot ?value WHERE {
  ?v prov:specializationOf ?slot ; top:observedAt ?tx ; top:value ?value .
  FILTER (?tx <= "2026-03-01T00:00:00Z"^^xsd:dateTime)
  FILTER NOT EXISTS { ?v2 prov:specializationOf ?slot ; top:observedAt ?tx2 .
                      FILTER (?tx2 > ?tx && ?tx2 <= "2026-03-01T00:00:00Z"^^xsd:dateTime) }
}

# (ii) Valid-time slice — "as it was true on 2026-02-15" (regardless of when recorded)
SELECT ?slot ?value WHERE {
  ?v prov:specializationOf ?slot ; top:validFrom ?vf ; top:value ?value .
  OPTIONAL { ?v top:validUntil ?vu }
  FILTER (?vf <= "2026-02-15T00:00:00Z"^^xsd:dateTime && (!BOUND(?vu) || ?vu > "2026-02-15T00:00:00Z"^^xsd:dateTime))
}

# (iii) Bitemporal point — "as we knew it on 2026-03-01, about what was valid on 2026-02-15"
#       = (i) and (ii) combined: filter the per-attribute instances on both clocks, then compose.
```

### PROV mapping (attribute grain — Sign-off Question 4 context)

| Bitemporal concept | PROV-O term |
| --- | --- |
| instance minted (transaction-time start) | `prov:generatedAtTime` (≈ `top:observedAt`) |
| instance superseded (transaction-time end) | `prov:invalidatedAtTime` |
| this instance revises the prior | `prov:wasRevisionOf` |
| stable cross-version attribute-slot | `prov:specializationOf` |
| entity as a composition of current instances | `prov:Collection` / `prov:hadMember` |
| valid-time interval | no native PROV peer — TOP-local (`top:validFrom`/`validUntil`) |

The one honest gap: PROV has no valid-time-of-a-fact term, so `validFrom`/`validUntil` are TOP-local with no `subPropertyOf prov:*` — a declared absence, consistent with how Constraint leaves have no PROV peer.

### Consequences (if Accepted as recommended)

- **Bitemporality without disturbing Universal DNA.** The always-on minimum is unchanged; mono-temporal data stays valid; only opted-in attributes carry the second axis.
- **Audit stays append-only**, and **`observedAt` gains one honest meaning** (transaction time).
- **PROV-O deepens** — it now governs both attribute revisions and entity composition.
- **NGSI-LD projection preserved**; mixed sensitivity within one entity becomes expressible.
- **Cost is real and bounded:** reification per tracked attribute, paid only where Tiers 1–3 fire; ingestion fail-closed pushes the lift to the Broker.

### What this ADR does NOT do

- It does **not** land any class, property, or shape. Nothing changes in `core/v1/shapes.ttl` until Accepted.
- It does **not** make valid time mandatory or add a fourth Universal DNA property.
- It does **not** author the temporal query layer, the Broker lift, or the linter rule for the triggering tiers — each is a follow-on PR.
- It does **not** fix the marker mechanism for "versioned" / "tracked" (a `top:Versioned` class vs. a flavor vs. workflow opt-in) — a design detail for the implementing PR.

### Sign-off questions (the actual decision)

1. **Representation & grain.** Accept the attribute-grain synthesis (Option C grain + A discipline + B valid-time interval, PROV revision, append-only)? Or pure A (whole-entity), B, or C?
2. **Valid-time scope.** Core-level but **opt-in** via `top:BitemporalShape` (recommended), promote valid time into Universal DNA on `top:CommonEntity` (universal, but changes the always-on contract), or keep it domain-only on `top:Temporal` (status quo, not truly bitemporal)?
3. **As-of contract.** Are query patterns (i)/(ii)/(iii) the complete set to support?
4. **Tier-1 enforcement.** Enforce structural entailment at **`sh:Violation`** (recommended — fail-closed) or **`sh:Warning`** (advisory)? And confirm the lifecycle calibration (hard on cryptographic/event markers, soft on in-progress evidentiary types).

### Ratified decision (2026-06-20)

All four questions accepted as recommended:

1. **Representation & grain.** The attribute-grain synthesis — Option C's per-attribute granularity + Option A's immutable append-only PROV-revision discipline + Option B's `validFrom` / `validUntil` interval.
2. **Valid-time scope.** Core-level but **opt-in** via `top:BitemporalShape`; Universal DNA is unchanged (`observedAt` stays the always-on transaction-time anchor).
3. **As-of contract.** Patterns (i) transaction-time slice, (ii) valid-time slice, (iii) bitemporal point are the complete set for now.
4. **Tier-1 enforcement.** `sh:Violation` (fail-closed), with the lifecycle calibration: hard on the committed markers (`integrityHash`, `signedBy`, `top:Attestation`, `top:StatusChange`); soft (`sh:Warning`) on in-progress evidentiary types (`top:Document`, `top:Log`, `top:Credential`) until they acquire an anchor.

### Status

Accepted 2026-06-20. The bitemporal vocabulary (`top:validFrom`, `top:validUntil`, `top:Versioned`), `top:BitemporalShape`, and the Tier-1 enforcement shapes land in `core/v1/shapes.ttl` alongside this acceptance, with a versioned walkthrough under `core/v1/walkthroughs/`. The first-principles § 4 "(Proposed)" marker is removed. Out of scope here (follow-on work): Tier-2 propagation and the Tier-3 linter rule, the temporal query layer, and the Broker ingestion lift.

---

## How to add an ADR

1. Pick the next number in sequence.
2. Open a PR adding a new section to this file. Title format: `ADR-NNNN: Short imperative phrase`.
3. Required fields: Date, Status (Proposed / Accepted / Superseded by ADR-N), Context, Decision, Consequences. Refs to artifacts and PRs are encouraged.
4. If the ADR supersedes a prior one, mark the prior ADR's status as `Superseded by ADR-N` in the same PR. Don't delete it.
5. Quoting the conversation that forced the decision is welcome — the operator's actual words usually capture the question better than any rewrite.
