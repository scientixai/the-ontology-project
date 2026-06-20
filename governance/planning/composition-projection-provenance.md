# Composition, projection, and copy-free provenance: the substrate posture

*Status: pre-RFC strategic planning. Author: Bo Lora (BDFL), with AI-agent assistance. Audience: Bo, future working-group leads, founding signatories, anyone trying to understand why TOP is a substrate and not a set of schemas.*

*Companion to [first-principles.md § 4](../../first-principles.md), [ADR-0021](../decision-log.md#adr-0021-bitemporal-model-valid-time-and-transaction-time-on-core), [ADR-0004](../decision-log.md#adr-0004-composable-workflow-extensions-not-sibling-reference-graphs), [ADR-0009](../decision-log.md#adr-0009-specialization-pattern-workflow-concepts-extend-commons-primitives-via-subclassof), the [FIWARE lessons note](fiware-smart-models-lessons.md), and the [FPF comparison](fpf-comparison.md).*

---

## Why this document exists

TOP's value is not "another set of data models." It is that downstream consumers **project from one provenanced source of truth** instead of copying and transforming data across boundaries. This note captures the posture that makes that real, worked out against a concrete operator example (a blood draw), so the principle is on the record before it hardens into doctrine or implementation.

The posture has three moves — composition, projection, and copy-free provenance — and one naming discipline.

## Two kinds of composition (do not conflate them)

"Composed entity" means two different things; both are first-class, and keeping them distinct keeps the model honest.

| Sense | What it is | Example | Mechanism in TOP |
| --- | --- | --- | --- |
| **Attribute composition** | one entity is a bag of attributes that version independently | a patient's `weight`, `status`, `address` each evolving on their own schedule | per-attribute bitemporal instances (ADR-0021) |
| **Entity composition** (aggregation / mereology) | one entity is composed of *other whole entities*, each provenanced in its own right | a specimen **collection** = these tubes; a **shipment** = these specimens + a temperature log + a tracking number | `prov:Collection` / `prov:hadMember`, PROV generation, `withinLocation`; open part-whole question — see [FPF comparison § mereology](fpf-comparison.md) |

The decisive graph property: **a part can belong to many wholes at once.** One tube participates in the *collection*, *chain-of-custody*, *billing*, and *consent* compositions simultaneously, by reference, with no duplication. Plain tree mereology forbids this; a graph permits it — and it is exactly what makes fit-for-purpose projection possible.

### The blood draw, mapped to Core

| Operator thing | TOP Core |
| --- | --- |
| the draw, the "stops" (collect → label → package → ship → receive → store) | `top:Activity` chained by `precededBy` (`prov:wasInformedBy`); "received" etc. as `top:Milestone` |
| the collection of tubes | a `prov:Collection`; the collect-Activity `prov:generated` each tube |
| each tube | `top:Material` |
| transport cooler | `top:Storage` (a mobile Location subtype); tubes `withinLocation` it |
| FedEx number | the cooler's `identifier`; journey as an `observedAt` stream |
| temperature log | `top:Log` (Evidence) with `integrityHash` → Tier-1 immutable |
| patient consent | `top:Attestation` (Evidence), `signedBy` the Person → Tier-1 immutable |

## Projection: fit-for-purpose views, not forks

A lab or courier needs only `{ shipment, cooler, tracking number, temperature log }` and could not care less about patient consent. In this system that view is a **projection** — a query over the shared graph — not a copy. The consent is one or two edges away (tube → `prov:wasGeneratedBy` → collection → patient → consent), *present but not projected*. Traceability is preserved; visibility is scoped.

This is the precise opposite of the FIWARE failure mode (every consumer mints its own divergent schema; the catalog rots): **one graph, many lenses, every lens still fully provenanced** because it is a window onto the source, not a lossy export of it. (FPF formalizes the same idea as "Epistemic Viewing" / "views are projections, not alternative facts" — see the comparison note.)

## Copy-free provenance: reference and decorate, never duplicate (the thesis)

This is the load-bearing claim. In the status quo every boundary crossing is a copy-and-transform (HL7 → LIMS, CSV → warehouse, SDTM transform for submission). **The transform-on-copy is the precise moment context dies** — consent, operator, instrument, custody chain all get left on the other side; provenance is then reconstructed afterward from fragmented logs, badly.

In this system there are only two moves, and neither copies:

- **A sub-entity crossing a boundary is the *same* entity** (same durable identity), now *referenced* in a new composition. It carries its provenance because it *is* itself, not a transformed echo.
- **New processed data decorates rather than replaces** — a derived value attaches to the source by a derivation edge (`prov:wasDerivedFrom` / `wasGeneratedBy`), append-only. A "new composition" is a new *view assembled by reference*, not a new *copy assembled by transform*.

So provenance is not *added* to the data; it is **the absence of a copy event at which to lose it.** That is what makes it first-class structurally rather than aspirationally — you cannot lose what you never severed. (This is the structural version of first-principles § 4: "we don't audit the data; the data *is* the audit.")

### Why this is coherent with the existing machinery

- **`top:identifier` (Invariant Universal DNA, opaque durable URI) is the enabling mechanism** — global stable identity is what lets you reference instead of copy.
- **Append-only / immutable versions (ADR-0021)** is the same discipline from the write side: decorate by adding, never mutate.
- **Tier-1 integrity survives boundaries *because* of no-copy** — a `signedBy` consent or hashed temperature log keeps its hash valid across the lab boundary; in ETL the hash breaks at the first transform. No-copy is what makes the cryptographic anchor meaningful end to end.
- **Projection (read) and decoration (write) are the two halves** of operating on one substrate.

## The federation caveat (so the vision survives reality)

Separate organizations, separate stores, data sovereignty, and confidentiality mean you sometimes *must* physically move data. The robust form of "no copy" for those cases: move a **self-describing, provenance-carrying, signed projection** — identity, PROV edges, and integrity hash travel *with* it — so even an unavoidable copy stays context-preserving and verifiable, not a naked transformed row. It degrades gracefully instead of collapsing back to ETL. Cost side, stated plainly: reference-don't-copy demands globally resolvable identity and something (the Broker) that can dereference or verify across boundaries.

## Naming discipline (adopt the structure, not the dogma)

- **"Entity composition"** (instance/graph level) is *not* the same as **"compositions"** the above-Core namespace (smart-hospital, DCT, VBC) used in the strategy docs. Different altitudes; say which one is meant.
- **"Projection"** is a read view, never a copy.
- **`prov:Bundle` / named graph** is the concrete, off-the-shelf container for an addressable context unit.
- **"Holon" is lineage only.** Koestler's whole/part and the knowledge-graph application of it (Cagle) are credited prior art, not TOP keywords — the term is esoteric and drifts into dogma. We adopt the structure and describe it in operator-plain words.

## Open questions

1. **Does Core need a general part-whole primitive, or do `prov:hadMember` + `withinLocation` + PROV generation suffice?** Worked through in the [FPF comparison](fpf-comparison.md#the-mereology-fork-the-immediately-actionable-one); recommendation there is to let the clinical-research lighthouse force the need before adding anything to Core.
2. **Projection (a view) vs. access-control (a policy) are different axes.** "Doesn't need consent" is projection; "isn't allowed to see consent" is confidentiality (a `Constraint` / `accessRequirement`). Same graph, two concerns; do not bake authorization into the ontology.

## Status

Proposed planning note. Nothing binding. The thesis (copy-free provenance) is a candidate for elevation into first-principles once the bitemporal model (ADR-0021) is accepted and the clinical-research lighthouse has exercised the composition/projection posture against real data.
