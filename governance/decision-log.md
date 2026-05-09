# Architectural Decision Log

> The chain of architectural decisions that shape The Ontology Project, in the order they were made. Each entry captures the question, the pivotal moment that forced an answer, the decision, and what it commits us to. Decisions are append-only: a later decision can supersede an earlier one, but the earlier one is never edited away — the reasoning is the artifact.

This log is the answer to "why is it shaped this way?" When a contributor proposes a change that conflicts with one of these decisions, the path forward is a new ADR that supersedes the old, not a quiet edit to the docs.

## Index

| # | Date | Title | Status |
| --- | --- | --- | --- |
| [ADR-0001](#adr-0001-temporal-and-prov-native-at-the-substrate) | 2026-05-08 | Temporal and PROV native at the substrate | Accepted |
| [ADR-0002](#adr-0002-universal-substrate-posture-no-specialized-entity-types-for-cross-cutting-shapes) | 2026-05-08 | Universal substrate posture — no specialized entity types for cross-cutting shapes | Accepted |
| [ADR-0003](#adr-0003-correct-the-namespace-mislabeling-top-is-the-project) | 2026-05-09 | Correct the namespace mislabeling — `top:` is the project | Accepted |
| [ADR-0004](#adr-0004-composable-workflow-extensions-not-sibling-reference-graphs) | 2026-05-09 | Composable workflow extensions, not sibling reference graphs | Accepted |
| [ADR-0005](#adr-0005-drop-onto-from-uri-paths) | 2026-05-09 | Drop `/onto/` from URI paths | Accepted |
| [ADR-0006](#adr-0006-skos-as-the-canonical-taxonomy-format) | 2026-05-09 | SKOS as the canonical taxonomy format | Accepted |
| [ADR-0007](#adr-0007-option-b-commons-as-vocabulary-workflows-as-shape) | 2026-05-09 | Option B — commons as vocabulary, workflows as shape | Accepted |
| [ADR-0008](#adr-0008-option-b-properly-scoped-commons-carries-universal-primitive-shapes) | 2026-05-09 | Option B properly scoped — commons carries universal primitive shapes | Accepted |
| [ADR-0009](#adr-0009-specialization-pattern-workflow-concepts-extend-commons-primitives-via-subclassof) | 2026-05-09 | Specialization pattern — workflow concepts extend commons primitives via `subClassOf` | Accepted |
| [ADR-0010](#adr-0010-four-layer-enforcement-against-drift) | 2026-05-09 | Four-layer enforcement against drift | Accepted |
| [ADR-0011](#adr-0011-prov-as-taxonomy-governance-dogfood) | 2026-05-09 | PROV as taxonomy governance — dogfood | Proposed |

---

## ADR-0001: Temporal and PROV native at the substrate

**Date:** 2026-05-08 · **Status:** Accepted · **PR:** [#8](https://github.com/scientixai/the-ontology-project/pull/8) · **Refs:** [FIRST-PRINCIPLES.md § Temporal and provenance, native](../FIRST-PRINCIPLES.md)

### Context

Operators in regulated industries do not get to bolt provenance on later. GxP, 21 CFR Part 11, ICH E6(R3), and every audit-trail discipline downstream of them require that *who* did *what*, *when*, and *based on what* be answerable from the data without reconstruction. Ontologies that punt provenance to a higher layer end up reinventing it badly.

### Decision

The substrate adopts NGSI-LD temporal semantics and W3C PROV native typing as first-class concerns. Every entity declares its `provType` (Agent / Activity / Entity); every property declares its `provSemantics` where one applies (`prov:wasGeneratedBy`, `prov:wasAttributedTo`, `prov:wasAssociatedWith`, `prov:wasDerivedFrom`, `prov:actedOnBehalfOf`, `prov:wasInformedBy`, `prov:wasInvalidatedBy`, `prov:hadRole`). The translator emits `rdfs:subClassOf prov:*` and `rdfs:subPropertyOf prov:*` from these annotations. Audit-trail entries are container-typed; not specialized.

### Consequences

- Audit-trail tooling that consumes PROV gets a free seat at the table. No special-case adapters.
- The substrate cannot drift away from PROV without breaking every downstream provenance query.
- Future ADRs (notably [ADR-0011](#adr-0011-prov-as-taxonomy-governance-dogfood)) can extend the same discipline to the taxonomy itself, not just instance data.

---

## ADR-0002: Universal substrate posture — no specialized entity types for cross-cutting shapes

**Date:** 2026-05-08 · **Status:** Accepted · **PR:** [#9](https://github.com/scientixai/the-ontology-project/pull/9) · **Refs:** [FIRST-PRINCIPLES.md § Universal substrate](../FIRST-PRINCIPLES.md)

### Context

A draft of the Visit lift introduced `VisitObservation` as a specialized entity type. That triggered a question: do we keep adding specialized types every time a workflow expresses a shape, or do we treat the substrate as universal containers that get specialized through *content* rather than *shape*?

### Decision

Cross-cutting shapes (Activity, Task, observation) are expressed as universal containers in the substrate. Specialization happens through reference data, role bindings, and projection — not by minting new entity types every time a workflow expresses the same shape with different content.

### Consequences

- The substrate stays small and stable. Shapes that recur across workflows are recognizable.
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

Workflows are **composable extensions** layered on a single commons substrate, not siblings. A smart hospital is not in `topcd:`-or-`topcr:`; it is in both, simultaneously, by binding the same `topc:Person` (the patient) to both a `topcd:Encounter` and a `topcr:Visit`. The commons provides the primitives; workflows specialize them.

### Consequences

- New workflow extensions ship as additive packages, not as new top-of-tree concept schemes.
- Cross-workflow composition (the smart-hospital-as-sponsor case) becomes a first-class scenario rather than an edge case.
- The taxonomy explicitly models **WorkflowExtensions** as a top concept distinct from the substrate, so contributors can see at a glance which layer they are touching.

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
- Every concept in the substrate is now traceable to a single canonical record.

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

- The commons stops being a vocabulary stub and becomes the actual reusable substrate.
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

**Date:** 2026-05-09 · **Status:** Proposed · **Refs:** [ADR-0001](#adr-0001-temporal-and-prov-native-at-the-substrate)

### Context

ADR-0001 commits the substrate to PROV native typing for instance data. The taxonomy itself is data — concepts get proposed, reviewed, approved, deprecated, replaced, attributed to people. If we believe what ADR-0001 says, the taxonomy should carry the same provenance discipline it imposes on the data below it.

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
- The substrate now dogfoods its own provenance discipline at every layer.
- Status remains **Proposed** until the meta-shapes ship and the taxonomy is backfilled with concept-level provenance for the existing 52 concepts.

---

## How to add an ADR

1. Pick the next number in sequence.
2. Open a PR adding a new section to this file. Title format: `ADR-NNNN: Short imperative phrase`.
3. Required fields: Date, Status (Proposed / Accepted / Superseded by ADR-N), Context, Decision, Consequences. Refs to artifacts and PRs are encouraged.
4. If the ADR supersedes a prior one, mark the prior ADR's status as `Superseded by ADR-N` in the same PR. Don't delete it.
5. Quoting the conversation that forced the decision is welcome — the operator's actual words usually capture the question better than any rewrite.
