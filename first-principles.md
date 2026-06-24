
# First Principles

The Ontology Project

---

*Operationalizing the TOP Manifesto · 2026-06-24*

The [manifesto](manifesto.html) names what we value and why. These principles name how we apply those values — the architectural decisions we make again and again, the ones that settle debates and keep the work grounded.

They are enumerable by design. A contributor who has read this document should be able to recite them.

**The principles:**

1. **Practicality over dogma** — not BFO fundamentalists; we lean toward models that work
2. **Human-down, not standards-up** — operator vocabulary shapes the entity; standards are projections
3. **Temporal and provenance native, not sidecars** — two clocks and PROV-O baked in, not audited after
4. **Reference graphs are commons, not moats** — a reset function, not a lock-in
5. **Governance lives in the artifacts** — if it is not machine-readable, we do not have the rule yet
6. **Open core, constrained extension** — closed to redefinition, open to tightening and addition
7. **Pipeline layers are a precondition chain** — skip one, the next inherits the weakness

> **The tie-breaker.** When "industry-standard X" conflicts with these principles, these principles win.

---

## 1. Practicality over dogma

*We do not require BFO fundamentalism. We lean toward models that work.*

The most common failure mode of ontology projects is not technical — it is philosophical. A team picks a foundational ontology (BFO, DOLCE, UFO, or one of the others), then spends a year or more ensuring perfect alignment while the project stalls. The ontology becomes the end, not the means. The knowledge graph never ships.

TOP Core is aligned to BFO and to the broader consensus in foundational ontology. It draws on them. It does not import them as mandatory dependencies or declare strict compliance as a gate. Alignment is an aspiration that compounds value over time; mandatory import is a constraint that stops projects before they start.

A reference graph that ships and serves operators is worth more than a perfectly-aligned ontology that never leaves a whiteboard. We name this failure mode because we will face the same argument at every subsequent layer. Settling it here prevents it from recurring.

**Concretely:**
- TOP Core uses BFO-aligned distinctions (objects, processes, qualities) without requiring strict BFO import
- Where formal alignment and operator reality conflict, we model operator reality and document the alignment gap
- Consumers who want strict foundational compliance can align to it from our foundation; we do not impose that cost upstream

---

## 2. Human-down, not standards-up

Most ontologies are built Standards-Up: regulatory schemas dictate how data is shaped, forcing operators to act as translators between their work and the database. TOP inverts this.

| | The legacy way | The TOP way |
|---|---|---|
| Source of truth | Industry standard | Operator workflow |
| Operator UX | Data-shaped (requires translation) | Work-shaped (matches reality) |
| Standards | The foundation | The projection layer |
| When standards change | The model breaks | Only adapters change |

**Entity names come from operator vocabulary** — across every domain:

| Domain | Operator-grounded (foundation) | Standard-grounded (projection) |
|---|---|---|
| Fintech | `Client`, `Account`, `Trade` | `LegalEntity_LEI`, `ISO_20022_Acct` |
| Logistics | `Shipment`, `Driver`, `Route` | `Carrier_Alpha_Code`, `Transit_Leg_001` |
| Manufacturing | `Part`, `Batch`, `Machine` | `MRO_Item_Index`, `Lot_Unit_Hex` |
| Clinical | `Participant`, `Visit`, `Site` | `SUBJID`, `Encounter`, `ResearchOrg` |

**Workflow boundaries, not data structures.** We model moments in a human's day — `InformedConsent`, `SafetyInspection`, `TradeConfirmation` — not database join tables.

**Standards-alignment is a projection, not a constraint.** A "Participant" maps to FHIR `Patient`, CDISC `SUBJID`, and SNOMED CT via adapters. The foundation stays anchored to the human. Adapters evolve as standards do; the foundation does not.

**Three tests to settle any naming debate:**
1. *The Verbal Test:* Does an operator say this term out loud during their workday?
2. *The Boundary Test:* Does this entity match a real-world workflow boundary?
3. *The Origin Test:* Am I shaping the foundation to match a standard, or shaping a projection?

---

## 3. Temporal and provenance native, not sidecars

Most systems treat history as a log and ownership as a flag. In TOP, time and origin are baked into the property itself. We don't audit the data; the data *is* the audit.

**Bitemporal by construction.** TOP carries two independent clocks:
- *Valid time* — when a fact was true in the world
- *Transaction time* — when the system recorded it

Both clocks are first-class and independently queryable. TOP answers "as we knew it at T₁" and "as it was true at T₂" as separate questions. That is the line between a system of record and a value catalog: single-clock streams record how values changed but cannot separate the two clocks or guarantee non-repudiation.

**W3C PROV-O native.** Every entity is a native PROV-O object (`prov:Agent`, `prov:Activity`, `prov:Entity`). Corrections are PROV revisions (`prov:wasRevisionOf`), append-only, never edited in place. A value carrying a cryptographic anchor (`integrityHash`, `signedBy`) must be immutable — SHACL enforces it.

> Compliance vendors *reconstruct* history from fragmented logs. TOP *renders* history by traversing the graph.

---

## 4. Reference graphs are commons, not moats

This principle is the manifesto applied to engineering decisions.

The manifesto names the problem: industries wrecked by vendor lock-in and secret-sauce thinking, ontologies that stay behind when the contract ends. TOP's purpose is to be a **reset function** — to give companies a way out of the ontology technical debt trap and to give ontologists a way out of the "justify the discipline" conversation.

That only works if the reference graphs are genuinely portable and openly owned.

**Concretely:**
- Every reference graph is Apache-2.0 licensed, no exceptions
- Builds are byte-reproducible and verifiable (deterministic serialization, SHA256 checksums)
- The reference graph grounds any platform; no platform grounds the reference graph
- Any architectural decision that creates dependency on a specific runtime, broker, or commercial product violates this principle

**The reset function for ontologists.** The most common friction point for ontologists inside companies is not technical — it is organizational. Years spent arguing for the value of the discipline before anyone invests in a proper model is the norm, not the exception. A TOP reference graph changes that first conversation: the argument shifts from "why do we need an ontology" to "how do we extend what's already here." An ontologist who walks in with a TOP reference graph is already an architect of the future, not a defender of the past.

**Why no moats.** Creating lock-in in a commons defeats the commons. An architecture that makes a TOP reference graph harder to leave is an architecture that replicates the exact problem TOP was built to solve.

---

## 5. Governance lives in the artifacts, not in policy documents

A constraint that exists only in a Word document is not a constraint. If we cannot express a rule machine-readably, we do not have it yet.

- SHACL shapes enforce rules at build time, not at deployment time
- OWL declares the classes; the CI gate validates structural soundness on every push
- Crosswalks (SSSOM) are versioned alongside the model, not buried in `@context` files
- Every entity carries provenance by construction, not by policy

**The consequence.** Compliance is entailed, not optional. A value carrying a cryptographic anchor cannot be mutated because the SHACL shape prevents it — not because someone wrote a policy. Audit is not a post-hoc layer; it is a property of the graph. This is governance by construction.

---

## 6. Open core, constrained extension

The core is open to extension, closed to redefinition. This discipline prevents the drift pattern — the same logical concept modeled differently across consumers until semantics diverge silently.

Every TOP core property carries an explicit extension contract:

| Contract | What it means |
|---|---|
| **Invariant** | Semantics fixed; no consumer may loosen or redefine |
| **Tightenable** | Shape stays; consumers may narrow enums, require what core makes optional, tighten cardinality |
| **Additive** | Surfaces designed for downstream addition (enum values, subclasses) |

Consumer extensions live in the consumer's namespace and chain to core via `subClassOf`, `subPropertyOf`, or `skos:*Match`. The contract, enforced at contribution time, holds the line.

---

## 7. Pipeline layers are a precondition chain, not a menu

The six layers of the ontology pipeline are not a menu. Each is the precondition for the next. Skip one and the next inherits the weakness.

1. **Controlled vocabulary** — definitions, synonyms, anti-synonyms, per-property enums, with provenance
2. **Taxonomy** — hierarchical organization of the vocabulary
3. **Metadata schema** — SHACL property shapes, SSSOM crosswalks
4. **Thesaurus** — SKOS-XL labels with provenance, cross-concept relations
5. **Ontology** — OWL classes with PROV-O alignment
6. **Knowledge graph** — instances at scale

Controlled vocabulary without taxonomy gives synonyms with no hierarchical context. Ontology without SHACL shapes gives classes without enforceable constraints. Instances without a validated ontology are data, not knowledge. The reference graph demonstrates the chain. Contributions that skip layers return to the layer they skipped.

---

*Apache License 2.0 · [TOP GitHub Repository](https://github.com/scientixai/the-ontology-project)*
