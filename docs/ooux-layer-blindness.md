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

## The second axis: object vs property (Jessica Talisman)

Reviewing this, Jessica Talisman pushed the finding one level deeper:

> "First name, last name, employee are not classes or objects — they are properties. **Context is a property, not an object.** Classes are the TBox, which is small; properties represent the data — the ABox."
> — [*Context Is a Property, Not an Object*](https://substack.com/@jessicatalisman/note/p-206101455)

Layer-blindness is the *tier* axis. This is the *kind* axis — and OOUX flattens it too. It renders the operator's world as **objects**, but many catalog "objects" are really **attributes, relations, or context** — the ABox, where the data actually lives. Reifying them into classes is a category error that *compounds* the tier problem. "Promote `Date` or `Tag` to a Core class" can itself be wrong: a date is a value, a tag is an annotation, a role is a relationship, context is a property. They should be **demoted to properties**, not minted as classes at all.

So the reconciliation is **two-axis**, and both are answered before anything is minted:

1. **KIND** — is this a class (an object; the TBox, which is small), or a property / relation / context (the ABox, where the data lives)? A property reified as a class is *demoted*, not tiered.
2. **TIER** — *only if it is a class*, which layer owns it (the original layer-blindness question).

Class-first modeling — the shape an object catalog hands you — is backwards from where the data is. The TBox is a thin scaffold; the properties carry the weight. The gate enforces both axes (`tier-map.json` carries a `kind` per object; a non-class term modeled as a class is a REIFY violation).

## The mitigation: a two-axis reconciliation stage the pipeline already implies

Between the OOUX object catalog and class-minting, insert a **reconciliation** pass. For each catalog item, first fix its KIND, then — if it is a class — its TIER:

| Verdict | Axis | Action |
| --- | --- | --- |
| **Demote** | kind | Not a class at all — a property, relation, or context reified as an object. Re-model as a property (Jessica Talisman: *context is a property, not an object*). |
| **Dedupe** | tier | The parent class exists — bind to the existing upper/mid class; do not re-mint. |
| **Promote** | tier | A class, but no parent has it yet — it reveals a real gap in Core or a mid-layer. (For us, `budget`, `shipment`, `capa` turned out to be cross-industry primitives, not clinical-research at all.) |
| **Mint native** | tier | Genuinely domain-specific — mint it, but still `rdfs:subClassOf` a parent category. |

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

## Enforcement

This is a machine-checked rule, not a convention. [`tools/lint_layering.py`](../tools/lint_layering.py)
flags every **shadow** (a domain name equal to a `top:`/`hcls:` class) and every **orphan** (a
domain class with no `subClassOf` chain to a parent). Resolution is recorded per object in
[`cr-domain/views/tier-map.json`](../cr-domain/views/tier-map.json) — `dedupe` / `subclass`
(resolved) vs. `promote` / `review` (tracked backlog). An object **absent** from the map fails the
gate, so a new shadow cannot regress in. The check is wired into `cr-domain/tests/run_tests.py` and
[`.github/workflows/layering.yml`](../.github/workflows/layering.yml); `--strict` is the
federation-readiness gate (zero `promote`/`review` before a domain is carved out). Codified in
[`governance/extension-contract.md`](../governance/extension-contract.md) § "Layer discipline."
