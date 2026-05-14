# TOP Taxonomy

> The classification scheme for The Ontology Project. One root, eight categories, twenty-nine leaves. Authored as SKOS for taxonomy tooling, mirrored as OWL/SHACL for reasoners and validators, aligned to PROV-O at the class level and to BFO on the four edges where it is clean. Practitioner-first: AI agents and ontologist tooling are honored at the edge, never as primary customers of TOP.

## Three layers

| Layer | What it is | What it carries |
| --- | --- | --- |
| **L0 — Root** (`top:CommonEntity`) | The lattice every TOP entity inherits | Universal DNA: identifier, observed-at, status |
| **L1 — Categories** (the 8) | Operational-context buckets | Class-level PROV-O alignment + 3 relational extensions each + light-edge BFO on the four clean categories |
| **L2 — Leaves** (the 28) | First-class operator concepts | Their own class-level PROV-O alignment; workflow extensions specialize from here |

## What this fixes

The earlier draft of the SKOS taxonomy had two compounding faults that surfaced when [TermBoard](https://termboard.com) loaded the file for the first round-trip:

1. **Mechanical.** Forty-six concepts carried a malformed PROV typing line of the form `prov:Agent "prov:Agent" .` — using a class as a predicate, with a string literal as object. No SKOS-aware tool could interpret it. ADR-0001's encoding (`rdfs:subClassOf prov:*`) had been replaced with a placeholder during the SKOS lift.
2. **Architectural.** The fifteen "TOP Primitives" had no shared structural parentage. Person, Organization, and OversightBody were each a primitive but nothing tied them together as Agents. Site and StorageLocation didn't share Location. Document, Log, and Credential didn't share Evidence. The taxonomy was a flat bag with PROV typing as the only (broken) cross-cutting structure.

The fix is the three-layer architecture below, with Universal DNA at the root and a categorical layer between the root and the leaves. A reviewer in TermBoard now drills from TOP Core → Agent → Person rather than scanning a flat list. A reasoner walks `?x rdfs:subClassOf top:Agent` to find every kind of agent across every workflow without enumerating each leaf. (See [governance/decision-log.md](governance/decision-log.md), ADR-0012 and ADR-0013.)

## L0 — Root: `top:CommonEntity` and Universal DNA

Three properties every TOP entity carries, no exceptions:

- **`top:identifier`** — globally unique URI / URN. Functional.
- **`top:observedAt`** — when the entity-state was observed or recorded.
- **`top:status`** — current lifecycle / health state.

These are the three an operator universally encounters: *what is this thing, when was it captured, is it current.* The earlier draft listed seven Universal DNA properties (identifier, wasAttributedTo, wasGeneratedBy, observedAt, status, value, unit). ADR-0013 trimmed to three because the other four overreached — they were universal in the engineering sense, not in the practitioner sense, and forced the taxonomy into record-level vs. domain-level provenance gymnastics.

Provenance lives where PROV-O puts it, at the class level, not as a universal-level shortcut property. Record-level metadata uses Dublin Core (`dcterms:creator`, `dcterms:created`, `dcterms:modified`) — clearly metadata, never confused with domain claims. Value and unit live where measurement happens (Outcome leaves), not at the universal level.

A SHACL `top:UniversalDNAShape` enforces the three properties on every `top:CommonEntity` instance. It targets the root class so every leaf inherits the obligation through `rdfs:subClassOf`.

## L1 — The eight categories

Each category is `rdfs:subClassOf top:CommonEntity` and `rdfs:subClassOf prov:Agent | prov:Activity | prov:Entity | prov:Plan | prov:Location` per its PROV-O peer. Each carries three category-level relational extensions — the verbs that category brings to TOP. Four also declare `rdfs:subClassOf bfo:*` for OBO Foundry interop on the cases where BFO membership is clean.

| # | Category | Focus | PROV-O peer | BFO peer | Relational extensions |
| --- | --- | --- | --- | --- | --- |
| 1 | `top:Agent` | Authority | `prov:Agent` | `bfo:IndependentContinuant` | `hasCredential`, `memberOf`, `authorizedBy` |
| 2 | `top:Location` | Space | `prov:Location` | `bfo:Site` | `withinLocation`, `geoSpatialData`, `accessRequirement` |
| 3 | `top:Resource` | Tools | `prov:Entity` | (mixed; leaf-level) | `ownedBy`, `hasMaintenanceLog`, `operationalState` |
| 4 | `top:Scope` | Intent | `prov:Plan` | (mixed; leaf-level) | `governedBy`, `containsActivity`, `objectiveStatement` |
| 5 | `top:Temporal` | Rhythm | `prov:Activity` | `bfo:Process` | `startTime`, `endTime`, `precededBy`, `occursAt` |
| 6 | `top:Evidence` | Proof | `prov:Entity` | `bfo:GenericallyDependentContinuant` | `verifiesOutcome`, `integrityHash`, `signedBy` |
| 7 | `top:Outcome` | Results | `prov:Entity` | (mixed; leaf-level) | `measuredBy`, `satisfiesConstraint`, `variance` |
| 8 | `top:Constraint` | Validity | `prov:Entity` | (mixed; leaf-level) | `enforcedBy`, `severityLevel`, `appliesTo` |

The four mixed-membership categories (Resource, Scope, Outcome, Constraint) carry BFO scope notes documenting their alignment rationale, but no forced subClassOf at the category level. Leaves under those categories declare their BFO type if and when OBO interop demands it. This buys the clean OBO interop where it lands cleanly without paying the BFO maintenance tax across all of TOP.

## L2 — The twenty-nine leaves

Each leaf is `rdfs:subClassOf` its category (and transitively `top:CommonEntity`) and carries its own class-level PROV-O alignment.

**Agent (5)** — `Person`, `Organization`, `Group`, `AutonomousAgent`, `Organism`. Person → `prov:Person`; Organization → `prov:Organization`; Group → `prov:Agent`; AutonomousAgent → `prov:SoftwareAgent`; Organism → `prov:Agent` (close match; non-human living agents — laboratory animals, plants, microbial cultures, model organisms).

**Location (3)** — `Physical`, `Virtual`, `Storage`. All → `prov:Location`.

**Resource (3)** — `System`, `Equipment`, `Material`. All → `prov:Entity`.

**Scope (3)** — `Portfolio`, `Program`, `Project`. All → `prov:Plan`.

**Temporal (4)** — `Schedule`, `Window`, `Activity`, `Milestone`. All → `prov:Activity`.

**Evidence (4)** — `Document`, `Log`, `Attestation`, `Credential`. Document/Attestation/Credential → `prov:Entity`; Log → `prov:Collection` (a time-ordered set).

**Outcome (4)** — `Observation`, `StatusChange`, `Artifact`, `Conclusion`. All → `prov:Entity`.

**Constraint (3)** — `PhysicalLimit`, `RegulatoryLaw`, `SafetyGuardrail`. All → `prov:Entity`. (Constraints have no clean PROV-O peer; the alignment to ODRL/SHACL conceptually is a separate alignment pass.)

## How the layers compose

```
top:CommonEntity                          ← root, Universal DNA
   ├── top:Agent                          ← L1 category, PROV+BFO alignment
   │     ├── top:Person                   ← L2 leaf, prov:Person
   │     ├── top:Organization             ← L2 leaf, prov:Organization
   │     ├── top:Group                    ← L2 leaf, prov:Agent
   │     └── top:AutonomousAgent          ← L2 leaf, prov:SoftwareAgent
   ├── top:Location ...
   ├── top:Resource ...
   ├── top:Scope ...
   ├── top:Temporal ...
   ├── top:Evidence ...
   ├── top:Outcome ...
   └── top:Constraint ...
```

Workflow extensions — clinical research, care delivery, manufacturing, supply chain — layer on top by declaring their workflow-specific classes `rdfs:subClassOf` a TOP leaf. A clinical-research `Investigator` is `rdfs:subClassOf top:Person`. A manufacturing `BatchRecord` is `rdfs:subClassOf top:Document`. The same instance can carry both classifications; Universal DNA, the category's relational extensions, and the PROV-O / BFO alignment all flow through automatically.

The same instance answers a coordinator's "is this protocol current?" query and an OBO reasoner's "give me every IndependentContinuant in this graph" query. The first query gets the practitioner shape; the second gets the formal alignment; both work; neither distorts the other.

## Authoring layers

| File | View | Audience |
| --- | --- | --- |
| [`taxonomy/taxonomy.ttl`](taxonomy/taxonomy.ttl) | Pure SKOS | TermBoard, PoolParty, Synaptica, Protégé. Vocabulary, definitions, scope notes only. |
| [`taxonomy/taxonomy.csv`](taxonomy/taxonomy.csv) | Flat companion | Spreadsheet review of the SKOS. |
| [`core/v1/shapes.ttl`](core/v1/shapes.ttl) | OWL classes + SHACL contract | Reasoners, SHACL validators, downstream NGSI-LD tooling. Same URIs as the SKOS. |
| [`core/v1/walkthroughs/person.ttl`](core/v1/walkthroughs/person.ttl) | Concrete instance | Anyone wanting to verify the pattern end-to-end on a single entity. |
| [`core/v1/index.html`](core/v1/index.html) | Spec page | Web view; what gets shared with reviewers and conveners. |

The SKOS file carries operator vocabulary only. Property names, types, ranges, and the SHACL contract live in the OWL/SHACL layer. Earlier drafts modeled the contract as a SKOS top concept ("Universal DNA") — removed because the contract is metadata, not a thing operators recognize as first-class.

## How to read the SKOS file

The TTL is annotated with authoring rules sourced from TermBoard's quality conformance:

- A concept's `skos:definition` never repeats the concept's own `prefLabel` (avoids circular-definition flag).
- Definitions never use "include" / "includes" / "including" / "included" (anti-pattern flag).
- Each L2 leaf names its L1 parent in the first sentence of its definition (parent-in-description rule).
- The acronym "TOP" is expanded to "The Ontology Project" the few times it must appear.

These rules are enforced by inspection on every change. They are not load-bearing for the meaning, but they are load-bearing for clean SKOS round-trip.

## What this rules out

- **Sibling-by-industry.** TOP is not federations of separate ontologies (Healthcare-TOP, Manufacturing-TOP, Supply-Chain-TOP). Workflows are composable extensions on top of one Core, not siblings. (See ADR-0004.)
- **Specialized entity types for cross-cutting shapes.** A Visit is a Visit. TOP doesn't mint `topcr:Visit` and `topcd:Visit` as separate class types — it specializes through subClassOf where workflow specifics demand it. (See ADR-0002, ADR-0007, ADR-0008, refined by ADR-0012.)
- **Universal-level provenance shortcuts.** PROV-O lives where PROV-O puts it. Record-level metadata uses Dublin Core. No record-level vs. domain-level fork. (See ADR-0013.)
- **AI-agent-shaped Core.** AI agents and ontologist tooling reason against TOP via the PROV-O + BFO alignment at the class edge. They do not shape the Core. The practitioner shapes the Core. (See ADR-0013.)

## Pointers

- [`governance/decision-log.md`](governance/decision-log.md) — architectural decision log; ADR-0012, ADR-0013, ADR-0014 record this layer's commitments
- [`first-principles.md`](first-principles.md) — design rules; the practitioner-first posture grounded here
- [`manifesto.html`](manifesto.html) — philosophical foundation; "we owe it to humans"
- [`roadmap.md`](roadmap.md) — what ships next, what is queued
