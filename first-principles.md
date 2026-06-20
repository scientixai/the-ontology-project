
# First Principles

The Ontology Project

---
**A human-centered foundation for universal interoperability.** *Operationalizing the TOP Manifesto · Cited by every spec doc · 2026-05-13*

> **The Tie-Breaker:** When "industry-standard X" conflicts with operator reality, this document wins.

Most systems are built to satisfy databases; **TOP is built to satisfy the human experience.** We ground our entities in how humans actually work, then project that reality outward into the standards the world requires.

> Want each principle shown against a real operator problem — the challenge in plain English, why the status quo hurts, and how TOP differs? See the companion: [**First Principles, Illustrated**](first-principles-illustrated.md).

---

## 1. The Inversion: Human-Down, not Standards-Up

Most ontologies are built **Standards-Up**: they let regulatory schemas dictate how data is shaped, forcing operators to act as translators between their work and the database. TOP inverts this gravity.

| Most Ontologies | The TOP Way |
| --- | --- |
| Built standards-up | **Built human-down** |
| Standards shape entities | **Operator workflow shapes entities** |
| Data-shaped UX (requires translation) | **Work-shaped UX (matches reality)** |
| Standards are the Foundation | **Standards are the *Projection Layer*** |

**The Move:** We stop trying to make humans think like databases, and we start making databases reflect how humans actually work.

---

## 2. What this means concretely

1. **Entity names come from operator vocabulary.** We name things based on what the person doing the work calls them.
* **Yes:** `Participant`, `Visit`, `Site`, `Part`, `Trade`.
* **No:** `ResearchSubject`, `Encounter`, `LegalEntity_ISO20022`.


2. **Attribute names match what operators say or type.**
* **Yes:** `firstName`, `batchNumber`, `randomizationNumber`.
* **No:** `USUBJID`, `LOT_QTY_HEX`, `ARMCD`.


3. **Sub-objects represent workflow milestones.** We model moments in a human's day, not database join tables.
* **Yes:** `InformedConsent`, `SafetyInspection`, `TradeConfirmation`.
* **No:** `ResearchSubjectProgressEntry`, `RelationalAuditMapping`.


4. **Standards are Ephemeral.** Systems shouldn't transform data; they should project it. The foundation remains anchored to the human even as standards evolve from v4 to v5.

---

## 3. Decision Rule: When in Doubt

Use this sequence to settle architectural debates. We prioritize operator reality over database convenience:

1. **The Verbal Test:** Does an operator say this term out loud during their workday?
2. **The Boundary Test:** Does this entity match a real-world workflow boundary?
3. **The Origin Test:** Am I shaping the Foundation to match a standard, or shaping a Projection?

---

## 4. Temporal & Provenance: Native, not Sidecars

In TOP, time and origin are baked into the property itself. We don't "audit" the data; the data **is** the audit.

* **Bitemporal by construction.** TOP carries two independent clocks, not one: *valid time* (when a fact was true in the world) and *transaction time* (when the system recorded it). Both are first-class and independently queryable — TOP answers "as we knew it at T₁" and "as it was true at T₂" as separate questions. This is the line between an audit system of record and a value-over-time catalog: single-clock temporal streams and JSON-Schema model catalogs record how values changed, but cannot separate the two clocks or guarantee non-repudiation. The model is specified in ADR-0021.
* **NGSI-LD temporal properties:** attributes operators watch change (Status, Phase) are temporal streams — `validFrom` / `validUntil` carry the valid-time interval, `observedAt` carries the transaction-time snapshot.
* **W3C PROV native typing:** every entity is a native PROV-O object (`prov:Agent`, `prov:Activity`, `prov:Entity`); corrections are PROV revisions (`prov:wasRevisionOf` / `prov:specializationOf`), append-only, never edited in place.
* **Audit is entailed, not optional:** a value carrying a cryptographic anchor (`integrityHash`, `signedBy`) must be an immutable version, and SHACL enforces it — you cannot sign or hash a value and then mutate it.

**Structural Integrity:** Compliance vendors *reconstruct* history from fragmented logs. TOP *renders* history by traversing the graph.

---

## 5. Universal Pattern: Specialization is Content

TOP carries **one universal pattern**: `Activity + Task + polymorphic value`. Specialization is content, never entity shape.

* **Never:** Create specific entity types like `OncologyImagingStudy` or `ForexTradeRecord`.
* **Always:** Model these as a universal `Activity` identified by a concept code.

---

## 6. Promote Facts to Entities: No Bespoke Flags

Every "is X" flag is a claim in disguise. A boolean strips away the authority, the time, and the reason. **Model the evidence, not the flag.**

* **Authority claims** (e.g., `isSponsor`) → `Attestation`.
* **State transitions** (e.g., `isClosed`) → `StatusChange`.
* **Rule enforcement** (e.g., `isRestricted`) → `Constraint`.

---

## 7. Build the Pipeline in Order

Every concept in TOP — Core, workflow, customer — eventually carries all six layers of the [ontology pipeline](https://www.ontologypipeline.com/). Each layer is the precondition for the next. Skip one, the next inherits the weakness.

1. **Controlled Vocabulary** — synonyms, anti-synonyms, definitions, per-property enums. With provenance.
2. **Taxonomy** — hierarchical organization of the vocabulary.
3. **Metadata Schema** — SHACL property shapes, NGSI-LD contexts, SSSOM crosswalks.
4. **Thesaurus** — SKOS-XL labels with provenance, cross-concept relations.
5. **Ontology** — OWL classes with PROV-O and BFO alignment.
6. **Knowledge Graph** — instances at scale.

**Three CV-layer obligations.** Context routing for homonyms (*Subject* in human research vs animal research). Anti-synonyms for false friends (*agent* in pharmacology ≠ TOP `Agent`). SSSOM crosswalks as first-class artifacts, not buried in `@context` files.

---

## 8. Open Core, Constrained Extension

The Core is open to extension but closed to redefinition. The discipline that prevents FHIR-style drift: per-property flavors, machine-checked at PR time.

* **Invariant** — semantics fixed; consumers cannot loosen or redefine. (5 properties: `identifier`, `observedAt`, `integrityHash`, `startTime`, `endTime`)
* **Tightenable** — shape stays; consumers may require what Core makes optional, narrow enums, tighten cardinality. (23 properties, including `status`)
* **Additive** — surfaces designed for downstream addition (enum values, subclasses).

Consumer extensions live in the consumer's namespace and chain to Core via `subClassOf` / `subPropertyOf` / `skos:*Match`. Full per-layer rules: [`governance/extension-contract.md`](governance/extension-contract.md).

**Why it matters:** Extensibility without a discipline produces drift over time — the same logical concept gets modeled multiple ways across consumers, extensions proliferate without discoverability, profiles diverge. The flavor discipline keeps Core extensions safe by construction. TOP integrates with peer ontologies — FHIR, USDM, SDTM, MedDRA — at the projection edge via the Broker and equivalent adapters; the Core stays small and stable while standards alignment lives where it belongs.

---

## 9. The Competitive Advantage: Why Human-Centered Wins

Sponsors burn millions on standards-compliance headcount because standards are built for regulators, not for work. **TOP eats the complexity so operators don't have to.**

* **The Moat of Reality:** No one who anchored Standards-Up can rebuild around the human without throwing away their entire data model. TOP starts at the finish line.
* **Force Multiplier:** By letting humans work in their own vocabulary while the foundation handles the logic, TOP accelerates regulated industries.

---

*Apache License 2.0 · [TOP GitHub Repository*](https://github.com/scientixai/the-ontology-project)