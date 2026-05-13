
# First Principles

The Ontology Project

---
**A human-centered foundation for universal interoperability.** *Operationalizing the TOP Manifesto · Cited by every spec doc · 2026-05-13*

> **The Tie-Breaker:** When "industry-standard X" conflicts with operator reality, this document wins.

Most systems are built to satisfy databases; **TOP is built to satisfy the human experience.** We ground our entities in how humans actually work, then project that reality outward into the standards the world requires.

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

* **NGSI-LD Temporal Properties:** Attributes that operators see change (Status, Phase) are temporal streams. They use `validFrom` / `validUntil` for real-world intervals and `observedAt` for system snapshots.
* **W3C PROV Native Typing:** Every entity is a native PROV-O object (`prov:Agent`, `prov:Activity`, or `prov:Entity`).

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

## 7. The Competitive Advantage: Why Human-Centered Wins

Sponsors burn millions on standards-compliance headcount because standards are built for regulators, not for work. **TOP eats the complexity so operators don't have to.**

* **The Moat of Reality:** No one who anchored Standards-Up can rebuild around the human without throwing away their entire data model. TOP starts at the finish line.
* **Force Multiplier:** By letting humans work in their own vocabulary while the foundation handles the logic, TOP accelerates regulated industries.

---

*Apache License 2.0 · [TOP GitHub Repository*](https://github.com/scientixai/the-ontology-project)