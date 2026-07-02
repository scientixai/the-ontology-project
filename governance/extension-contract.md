# TOP Extension Contract

> Per [ADR-0019](decision-log.md#adr-0019-open-core-constrained-extension-three-flavors-per-core-property), TOP commits to **open Core, constrained extension** — every Core property and concept is a stable point of attachment, not a ceiling. Extension is permitted; redefinition is not. This document is the per-layer rulebook that makes the principle machine-checkable.

The contract applies to every consumer of TOP — workflow extensions (clinical research, care delivery, manufacturing, supply chain) and customer-built knowledge graphs alike. The linter (`tools/lint_extension.py`, follow-on PR) enforces the rules at PR time; this document is the source of truth the linter implements.

## The three flavors

Every Core property declares one of three extensibility flavors via the `top:flavor` annotation property:

| Flavor | What it means | Extension permitted? |
| --- | --- | --- |
| **Invariant** | Stable across every workflow and every customer. Type, range, cardinality, semantics cannot drift. | No. Tightening allowed (a workflow may require what Core makes optional); redefinition forbidden. |
| **Tightenable** | Stable shape; downstream consumers may add SHACL constraints (require what Core makes optional, narrow an enum, bind a value set, tighten cardinality). Cannot loosen what Core requires. | Tightening only. |
| **Additive** | A surface specifically designed for downstream addition (custom synonyms in CV, custom subclasses via `subClassOf`, additive enum values that extend rather than replace Core values). | Yes. Additions live in the consumer's namespace; Core terms remain valid. |

The flavor is the load-bearing annotation. Every other rule in this document derives from it.

## Layer 1 — Controlled Vocabulary

The CV layer is where a Core concept's synonyms, anti-synonyms, definitions, and per-property enums live. For each Core leaf, the CV artifact lives in `core/v1/vocabulary/<category>/<leaf>.yaml` (per ADR-0018).

### A consumer MAY

- **Add inbound synonyms** for any Core leaf, in the consumer's own namespace, with the consumer's own provenance. Example: `acme:hasSynonym "EmployeeRecord" :- top:Person, scope=acme-internal-only`.
- **Add per-property enum values** to any Core enum marked **Additive**. Custom values live in the consumer's namespace (`acme:status_LEAVE_OF_ABSENCE` extends `top:Person.status`).
- **Add disambiguation notes** scoped to the consumer's context — including their own `contextRouting` and `antiSynonym` blocks for terms the consumer's source vocabularies use that Core did not anticipate.

### A consumer MUST NOT

- **Redefine a Core canonical label.** `top:Person.prefLabel` is "Person" everywhere; no consumer rewrites it.
- **Remove or deprecate Core synonyms.**
- **Reassign a Core synonym to a different concept.** No consumer declares "in our system, *Subject* maps to `top:Material` instead of `top:Person`."
- **Add a custom enum value that *conflicts* with a Core enum value.** No "we use ACTIVE to mean what Core means by INACTIVE."
- **Modify a Core CV file directly.** Consumer additions live in the consumer's own files in the consumer's own namespace.

### Enforcement

- Every CV YAML in `core/v1/vocabulary/` carries an `extensionPolicy` block declaring the per-property flavor.
- Consumer CV files reference Core leaves via a `cextends` (or equivalent) declaration; they do not redeclare Core synonyms.
- The linter refuses CV PRs that violate the contract (custom synonym in Core namespace; Core canonical label modified; Additive value declared in Core namespace by a non-Core-steward author).

## Layer 2 — Taxonomy

Taxonomy is the SKOS hierarchy of Core concepts (`taxonomy/taxonomy.ttl`).

### A consumer MAY

- **Declare their own SKOS concept scheme** that references Core concepts via mapping properties.
- **Map consumer concepts to Core concepts** via `skos:exactMatch` / `closeMatch` / `broadMatch` / `narrowMatch` / `relatedMatch`.

### A consumer MUST NOT

- **Modify the Core SKOS concept scheme directly.** The Core scheme (`top:TaxonomyV1`) is governed at the Core layer.
- **Add `skos:broader` or `skos:narrower` edges between Core concepts.** The Core hierarchy is governed at the Core layer; consumer connective tissue is the mapping properties, not hierarchy edits.
- **Reuse the `top:TaxonomyV1` scheme IRI for consumer concepts.** Each consumer declares their own scheme.

### Enforcement

- Namespace governance — `top:` URIs require a Core-steward author.
- The linter inspects taxonomy PRs and refuses `skos:broader` / `skos:narrower` triples whose subject and object are both in the Core scheme but the author is not a Core steward.

## Layer 3 — Metadata Schema

The metadata schema layer is per-concept SHACL property shapes (`core/v1/shapes.ttl` and forthcoming `core/v1/shapes/<leaf>.ttl`), NGSI-LD JSON-LD contexts, and SSSOM crosswalk manifests.

### A consumer MAY

- **Add properties** to a Core concept via `subClassOf` in the consumer's namespace. Example: `acme:Document subClassOf top:Document; acme:Document acme:retentionPolicy "..."`.
- **Tighten Core SHACL property shapes** by adding consumer-side constraints. Examples: require a property Core makes optional (`sh:minCount 1`); bind a value set on a property Core leaves open (`sh:in (...)`); narrow cardinality from `0..*` to `1..1`.
- **Add new SHACL constraints** (cross-property invariants, conditional requirements) on top of Core.
- **Add their own crosswalks** in their own SSSOM file (`acme/v1/crosswalks/document.sssom.tsv`) without touching the Core file.
- **Set `sh:closed`** on the consumer's own subclass shape if the consumer's internal regime requires it.

### A consumer MUST NOT

- **Redefine the type, range, or domain** of a Core property.
- **Loosen a Core SHACL constraint.** Core says `sh:minCount 1`; a consumer cannot make it `sh:minCount 0`. Core says `sh:datatype xsd:dateTime`; a consumer cannot relax to `xsd:string`.
- **Remove a Core property** from a `subClassOf` extension. Every `acme:Document` is a `top:Document` and carries every `top:Document` property; the Liskov substitution principle holds at the schema layer.
- **Use the Core namespace for custom properties.** The `top:` namespace is governed; consumer additions go in the consumer's namespace (`acme:`, `topcr:`, etc.).
- **Change a Core property's `top:flavor` annotation.** Flavor declarations are Core-steward authority.

### Enforcement

- SHACL composition. The Core shapes target `top:CommonEntity` and Core leaf classes. Consumer shapes target consumer classes. Validation runs both shape sets; an extended instance must pass both.
- SHACL's `sh:closed` is **not** set at the Core layer (open by design — the additive flavor) but consumers may set `sh:closed` on their own subclass shapes if their internal regime requires it.
- The linter inspects SHACL PRs and refuses constraints that loosen Core (e.g., adding a `sh:minCount 0` to a property that Core declared `sh:minCount 1`), refuses property declarations in the `top:` namespace by non-Core-steward authors, refuses flavor annotation changes by non-Core-steward authors.

## Layer 4 — Thesaurus

The thesaurus layer is SKOS-XL labels with provenance and cross-vocabulary mappings. The current `taxonomy/taxonomy.ttl` will upgrade to SKOS-XL per ADR-0018; consumer-side thesaurus extensions live in consumer-namespace TTL files.

### A consumer MAY

- **Declare their own SKOS-XL labels** on their own concepts (with their own provenance).
- **Declare cross-vocabulary mappings** between their concepts and other external vocabularies (FHIR, internal HR systems, vendor catalogs).
- **Declare `skos:related` relations** between consumer concepts.

### A consumer MUST NOT

- **Modify Core SKOS-XL labels.** Core labels are Core-steward authority.
- **Redefine the meaning of a Core SKOS-XL label.**
- **Declare consumer labels in the Core namespace.**

### Enforcement

- Namespace governance.
- SKOS-XL labels have their own IRIs; consumer-IRI labels are inspectable.

## Layer 5 — Ontology

The OWL artifact in `core/v1/shapes.ttl` is the formal-logic view of Core. Consumers extend the ontology in their own files.

### A consumer MAY

- **Subclass any Core OWL class** (`acme:Document subClassOf top:Document`).
- **Add object and datatype properties** whose domain is the consumer's class.
- **Declare `rdfs:subPropertyOf`** from a consumer property to a Core property (a consumer's `acme:authoredBy` may be a sub-property of `top:signedBy`).
- **Add disjointness or equivalence axioms** between the consumer's own classes.

### A consumer MUST NOT

- **Redeclare the domain or range of a Core property.**
- **Add `owl:disjointWith` axioms** involving Core classes. The Core class structure is governed at the Core layer; consumer additions are subClasses, not disjointness assertions.
- **Use the Core namespace** for custom OWL declarations.

### Enforcement

- Namespace governance plus an OWL profile check.
- The linter validates that consumer OWL files only declare in the consumer's namespace and only refer to the Core namespace via `subClassOf` / `subPropertyOf` / `equivalentClass` / `disjointWith` chains where the Core element is the *upper bound*, not the redefinition target.

## Layer 6 — Knowledge Graph

The KG layer is instances at scale. The contract here is structural — instances must conform to the SHACL shapes at all the layers above.

### A consumer MAY

- **Create instances** of Core classes or consumer subclasses, in any namespace.
- **Add consumer properties** to instances of their own subclasses.
- **Federate Core-class instances** across consumers — a `top:Person` instance created by one consumer is recognizable by another consumer reading the same data.

### A consumer MUST NOT

- **Create an instance of a Core class with consumer-namespace properties** that have no `subClassOf` or `subPropertyOf` chain to Core. The chain is what makes the extension intelligible to a Core-only consumer.

### Enforcement

- SHACL validation against both Core and consumer shape sets.
- Federation reads — a Core-only consumer reads only the Core view of the data; the extensions are visible only to consumers that explicitly request them.

## The structural pattern this contract prevents

Any ontology project that adopts the one-Core-many-extensions bet inherits a structural risk: extensibility without a per-property discipline produces drift. Over a decade of independent specialization across vendors, jurisdictions, and customers, the same logical concept ends up modeled multiple ways; extensions proliferate without discoverability; profiles diverge.

The pattern isn't anyone's fault — it's what an unspecified extension surface produces. Several large ontology projects have lived this trajectory; the resulting friction usually surfaces as "interoperable on paper, uninteroperable in practice." TOP takes the same architectural bet (one Core, many extensions) and prevents the same outcome through the per-property flavors and per-layer rules this document records.

**TOP's posture toward peer ontologies** is integration at the projection edge, not Core-shape competition. The Broker (and equivalent projection adapters) ingest FHIR, USDM, SDTM, MedDRA, and other peer-ontology data and normalize it into NGSI-LD entities against Core. The Core stays small and stable; the peer-ontology alignment lives in projection-layer artifacts (SSSOM crosswalks per leaf, per ADR-0018). The discipline in this document is what keeps Core itself from drifting under extension pressure.

## What a consumer reads to understand their obligations

A workflow extension or customer building on TOP reads, in order:

1. **`first-principles.md`** — the design rules (especially § 7 "Build the Pipeline in Order" and § 8 "Open Core, Constrained Extension").
2. **`taxonomy.md`** — the three-layer architecture (1 root, 8 categories, 28 leaves).
3. **`core/v1/shapes.ttl`** — the SHACL property shapes with `top:flavor` annotations.
4. **This document** — the per-layer extension rules.
5. **`governance/decision-log.md` ADR-0018, ADR-0019** — the decisions this document operationalizes.

A consumer who follows this contract gets safe extension by construction. A consumer who violates it gets a linter rejection at PR time. Either way, the Core stays stable and the ecosystem stays interoperable.
