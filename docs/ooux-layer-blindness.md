# Design note: OOUX layer-blindness — an object catalog is not a class model

> A lesson learned the hard way, one step before it shipped. Every working group that builds
> on an OOUX object catalog inherits this note. Related: [RFC 0001](../governance/rfcs/accepted/0001-ooux-catalog-and-entity-view-schema.md)
> (the OOUX catalog as operator lens), [ADR-0026](../governance/decision-log.md) (the entity-view corpus),
> [ADR-0019](../governance/decision-log.md#adr-0019-open-core-constrained-extension-three-flavors-per-core-property)
> (open Core, constrained extension), [ADR-0023](../governance/decision-log.md#adr-0023-hub-and-spoke-domains-core-owns-the-contract-and-the-registry-each-domain-owns-its-repo)
> (hub-and-spoke domains), and [`governance/extension-contract.md`](../governance/extension-contract.md).

## What happened

We generated a reference entity-view per object in the clinical-research OOUX object catalog
(80 views, `cr-domain/views/entity/`, per RFC 0001). The generator was faithful. It produced,
among others:

- `cr:Person` — with `cr:personId`, `cr:firstName`, `cr:orcid`, `cr:npi` — while **`hcls:Person`
  already existed** in the mid-layer. Not extended. *Shadowed.*
- `cr:Date`, `cr:Tag`, `cr:AuditTrailEntry`, `cr:Region`, `cr:System` — each minted fresh in the
  `cr:` namespace, when each is a Core primitive (Temporal, a classification, provenance,
  Location, an autonomous agent).

Roughly a dozen of the ~80 objects were upper- or mid-layer concepts wearing a domain costume.
We caught it one step before carving clinical-research into its own repository (ADR-0023) — where
a conformance CI would have rejected a domain module that redefines the very primitives it claims
to inherit.

## Root cause: OOUX has no import statement

Upper ontologies carry `owl:imports` and `rdfs:subClassOf` — explicit machinery for *"this concept
is defined in a parent world; I am borrowing it."* OOUX has no such construct, and cannot, because
it elicits the **operator's** mental model — and the operator experiences every object as native.
They see "a Person," "a Date," "a Tag," never "a Person inherited from a healthcare base layer."
So every object in the catalog arrives **un-cited**, as if first-authored in this domain.

This is not a defect in OOUX. It is the method doing exactly its job: capturing one operator's
world completely, from the inside. The defect is in the naïve mapping **object catalog → ontology
classes**, which reads catalog completeness as self-containment.

## Why it is dangerous, not merely untidy

1. **Broken subsumption.** No `subClassOf` to the parent, so a reasoner cannot see that
   `cr:Investigator` *is a* `hcls:Person` *is a* `top:Agent`.
2. **Namespace capture.** Genuinely shared primitives become *owned* by one domain's namespace.
3. **Contract violation.** Under open-core / constrained-extension (ADR-0019), and under any
   BFO/OBO alignment, redefinition of a parent concept is forbidden. A flat catalog violates it
   wholesale.
4. **Federation break.** A domain repo that pins Core and the mid-layer (ADR-0023) but re-mints
   their primitives fails the executable extension contract. This is the failure that almost
   shipped.

## The principle

**Operator-completeness is not self-containment.** The operator's world is complete, but it is
furnished partly with borrowed furniture. OOUX captures the whole room faithfully — it just cannot
tell you which pieces you brought and which were already there. The ontology has to know what is
borrowed.

> OOUX captures the room; it can't tell you which furniture you brought and which was already there.

## The mitigation: a tier-attribution stage the pipeline already implies

Between the OOUX object catalog and class-minting, insert a **tier-attribution / reconciliation**
pass. For each object, ask *"does a parent world already own this?"*:

| Verdict | Action |
| --- | --- |
| Yes, and the parent class exists | **Dedupe** — bind to the existing upper/mid class; do not re-mint. |
| Yes in principle, but no parent has it yet | **Promote** — it reveals a real gap in Core or a mid-layer. (For us, `budget`, `shipment`, `capa`, `task` turned out to be cross-industry primitives, not clinical-research at all.) |
| No, genuinely domain-specific | **Mint native** — but still `rdfs:subClassOf` a parent category. |

This is nothing more than the **reuse-first alignment discipline of the ontology pipeline** the
project already credits (Jessica Talisman's pipeline). The trap is that an OOUX catalog *feels
finished* — complete and self-consistent — which is exactly what tempts a team to skip alignment
and jump to minting. An OOUX catalog is a valid **elicitation** artifact and an invalid **class
model**: it must re-enter the pipeline at alignment, never bypass it.

### For the view corpus specifically

Views should not re-invent inheritance. Let them **ride the class chain via SHACL `sh:targetClass`**:
a view targeting `hcls:Person` applies automatically to every `cr:Investigator` (targetClass
propagates through `subClassOf`). Author each object's view at its **home tier**; a subclass view
adds only its domain-specific facets. The generator preserves the "exhaustive flat menu" promise by
**authoring tiered, generating flat** — composing the flat file from parent + child at build time.
Correct ownership in source; viewer convenience in output.

## Checklist for any WG converting an OOUX catalog to classes

- [ ] Every catalog object has a **tier verdict**: dedupe / promote / mint-native.
- [ ] No object is minted in the domain namespace if a Core or mid-layer class already covers it.
- [ ] Every minted class carries `rdfs:subClassOf` to a parent category (extension-contract rule).
- [ ] "Promote" candidates are logged — they are the signal for what Core or a mid-layer is missing.
- [ ] Views target the class at its **home tier**; subclass views carry only deltas.
- [ ] The domain module passes the executable extension contract **before** federation carve-out.
