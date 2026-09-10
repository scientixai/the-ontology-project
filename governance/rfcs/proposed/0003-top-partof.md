# RFC 0003: Declare `top:partOf` in Core (close the mereology fork)

- **Status:** Proposed
- **Date:** 2026-09-10
- **Authors:** @sophia-briet (Acting CKO, digital)
- **Affected groups:** Core Stewards
- **Required quorum:** Core steward (the convener)
- **Supersedes:** n/a
- **ADR on acceptance:** ADR-NNNN (to be assigned on ratification)

## Motivation

Core has no constitutive part-whole edge for Temporal, Material, or Equipment entities. Three forcing cases surfaced this gap concretely (Bo addendum on kyron#124, 2026-09-10):

1. **Temporal hierarchy:** a blood draw (`top:Temporal`) occurs *within* a clinic visit, which occurs *within* a longitudinal study. The containing relationship is neither precedence (`precededBy`) nor scope-membership (`containsActivity`, which binds a Scope to its Temporals). It is structural composition: the draw is part of the visit.

2. **Material lineage:** an aliquot is a portion *of* a tube, which is part *of* a kit, which belongs to a lot, which belongs to a batch. The chain of material derivation requires a clean transitive part-whole that distinguishes constitutive composition from provenance (`prov:wasDerivedFrom`) or spatial containment (`withinLocation`).

3. **Equipment assembly:** a rotor is a component *of* a centrifuge. The relationship is functional composition, not spatial containment or ownership.

The gap was identified in [`governance/planning/fpf-comparison.md`](../planning/fpf-comparison.md) § "The mereology fork (the immediately actionable one)": the FPF framework distinguishes four part-of relations (`MemberOf`, `PhaseOf`, `ComponentOf`, `PortionOf`), of which TOP covers aggregation via `top:memberOf` and `prov:hadMember`, but lacks clean Core support for constitutive temporal, material, or equipment composition. The comparison note recommended a single well-flavored Core relation, anchored to BFO for OBO interoperability, once the clinical-research lighthouse forced the need.

That need is now concrete. The three cases above are load-bearing in the Scientix.AI operational vocabulary and in the clinical-research workflow designs underway. Without a Core relation, each workflow invents its own property — the FIWARE failure mode, at the edge TOP exists to prevent.

This RFC resolves the fork left open by the FPF comparison: one transitive `top:partOf`, promoted to Core, tightenable by workflows, BFO-aligned, and neutral across Temporal / Material / Equipment / other domains.

## Proposal

Declare `top:partOf` in `core/v1/shapes.ttl` as a transitive, tightenable, domain-neutral part-whole property, aligned to BFO's `bfo:part-of` at the edge for OBO-Foundry interoperability.

```turtle
top:partOf a owl:ObjectProperty, owl:TransitiveProperty ;
    rdfs:label "part of"@en ;
    top:flavor "Tightenable" ;
    rdfs:domain top:CommonEntity ;
    rdfs:range top:CommonEntity ;
    rdfs:subPropertyOf bfo:part-of ;
    rdfs:comment "Constitutive part-whole: this entity is a structural, material, temporal, or functional part of the whole. Transitive: if A partOf B and B partOf C, then A partOf C. Domain-neutral: applies to Temporal (a draw within a visit), Material (an aliquot of a tube), Equipment (a rotor of a centrifuge), and other entities. Tightenable: workflows refine via rdfs:subPropertyOf (e.g., cr:aliquotOf, eq:componentOf) to add domain-specific cardinality and range constraints (ADR-0019). Aligned to BFO part-of (bfo:part-of) for OBO-Foundry interoperability. Complements top:memberOf (aggregation, Agent→Agent only) and prov:hadMember (collection membership). Distinct from spatial containment (withinLocation), provenance (prov:wasDerivedFrom), and precedence (precededBy). Cardinality at Core: optional. Workflows require it by tightening in their shapes (ADR-0019, ADR-0022 precedent)."@en .
```

Properties of the declaration:

- **Domain:** `top:CommonEntity`. Any entity may be part of another entity.
- **Range:** `top:CommonEntity`. The whole is also a CommonEntity.
- **Flavor:** Tightenable (ADR-0019). Core makes no cardinality requirement; workflows tighten in their own shapes. Precedent: `top:hasSubject` (ADR-0022).
- **Transitivity:** Declared via `owl:TransitiveProperty`. If an aliquot is part of a tube, and the tube is part of a kit, the aliquot is part of the kit by entailment.
- **BFO alignment:** `rdfs:subPropertyOf bfo:part-of` for OBO-Foundry interoperability. BFO 2020 defines `bfo:part-of` as the foundational mereological relation; TOP's `top:partOf` is a specialization that respects BFO semantics while remaining workflow-neutral.
- **Cardinality at Core:** optional. No Universal DNA change; no requirement in `top:UniversalDNAShape`. Workflows that need part-whole on specific entities require it by tightening in their shapes (e.g., `cr:SpecimenShape` might require `top:partOf` with range `cr:Specimen`).
- **Distinguishing:** Not aggregation (`top:memberOf`, `prov:hadMember`), not spatial containment (`withinLocation`), not provenance (`prov:wasDerivedFrom`), not precedence (`precededBy`). It is constitutive composition: the part is a structural or functional constituent of the whole.

Workflow refinement path (ADR-0019, ADR-0022 precedent):

Workflows refine `top:partOf` via `rdfs:subPropertyOf` to add domain-specific semantics and constraints:

```turtle
# Example (not in this RFC; illustrative of the extension path):
cr:aliquotOf a owl:ObjectProperty ;
    rdfs:subPropertyOf top:partOf ;
    rdfs:domain cr:Aliquot ;
    rdfs:range cr:Specimen ;
    rdfs:comment "Material portion: this aliquot is a portion of the parent specimen."@en .

eq:componentOf a owl:ObjectProperty ;
    rdfs:subPropertyOf top:partOf ;
    rdfs:domain eq:Component ;
    rdfs:range eq:Equipment ;
    rdfs:comment "Functional component: this part is a component of the equipment assembly."@en .
```

The Core pull request implementing this will be prepared on branch `core/partof` and opened on acceptance (not as part of this RFC PR).

## Alternatives considered

- **Do nothing; let workflows invent their own part-whole properties.** Preserves Core's minimal footprint. Rejected: the three forcing cases (Temporal, Material, Equipment) span workflows, and each workflow inventing its own property fractures the composition graph. A downstream consumer querying "what is part of what" cannot federate across workflows without a shared root. This is the FIWARE lesson (ADR-0013): the thing that is structurally universal belongs in Core.

- **Import FPF's four-way mereology (`MemberOf`, `PhaseOf`, `ComponentOf`, `PortionOf`).** Rigorous and typed. Rejected: that is FPF's altitude (methodological framework), not TOP's (practitioner-first reference ontology). TOP's bet (ADR-0012, ADR-0013) is one domain-neutral primitive that workflows specialize. One `top:partOf`, refined by `rdfs:subPropertyOf`, preserves the open-core model (ADR-0019) and keeps the operator interface simple. FPF's typology remains credited prior art (see References); the distinction is design vocabulary, not runtime taxonomy.

- **Use `prov:hadMember` or `top:memberOf` for all composition.** Already in Core; no new primitive. Rejected: `top:memberOf` is narrowly Agent→Agent (membership in an Organization or Group, ADR-0006); `prov:hadMember` is set-membership (ADR-0021), not structural composition. An aliquot is not a "member" of a tube; it is a *portion* of it. A draw is not a "member" of a visit; it is a *part* of it. The semantics do not align.

- **Use spatial containment (`withinLocation`).** Already in Core. Rejected: an aliquot within a freezer and an aliquot *of* a specimen are different relationships. Spatial containment is "where," not "part of what." A rotor bolted into a centrifuge and stored in a lab are both spatially contained; only the former is a functional component.

- **Make `top:partOf` non-transitive.** Preserves local control; workflows assert only direct part-whole. Rejected: the material-lineage case (aliquot → tube → kit → lot → batch) is inherently transitive, and the transitivity is load-bearing for federated queries ("all aliquots from batch B"). Declaring transitivity at Core lets reasoners infer the full chain. Workflows that need only direct part-whole can ignore entailed triples.

## Open questions

1. **Inverse property.** Should Core declare `top:hasPart` as the inverse (`owl:inverseOf top:partOf`)? BFO 2020 has `bfo:has-part` as the inverse of `bfo:part-of`. Pro: symmetric querying (both directions). Con: one more Core property for the same edge. The draft omits it; the accepting ADR decides.

2. **Cardinality tightening precedent.** Should `top:BitemporalShape` or a future `top:TemporalCompositionShape` require `top:partOf` on composed Temporals as an existence proof that the tightening path works? Parallel to the open question in RFC 0001 (whether `top:BitemporalShape` should require `top:recordedAt` on versioned nodes). Not proposed here so the RFC stays a clean declaration; raised for the accepting ADR.

3. **PROV-O alignment.** PROV-O has no direct part-whole property; `prov:hadMember` is collection-membership, not mereology. Should `top:partOf` carry a declared absence note ("`top:partOf` has no PROV-O peer; `prov:hadMember` is set-membership, not composition") parallel to ADR-0021's declared absence for `top:validFrom`? The draft comment distinguishes them inline; the accepting ADR decides whether a formal absence declaration belongs in the decision log.

## Consequences

- **What gets easier.** Temporal, Material, and Equipment composition graphs are expressible with one shared root property. Workflows specialize it via `rdfs:subPropertyOf` (the ADR-0019 path) without fracturing the composition vocabulary. Federated queries can traverse part-whole across workflows. BFO alignment lets OBO-Foundry consumers align TOP data to other biomedical ontologies (OBI, UBERON, etc.) at the mereology edge. The FPF mereology fork is resolved with a concrete decision.

- **What gets harder.** One more Core property (the 30th, if accepted). Workflows must distinguish part-whole (`top:partOf`) from set-membership (`prov:hadMember`), spatial containment (`withinLocation`), and provenance (`prov:wasDerivedFrom`) — but that is a distinction operators already make ("this is *part of* that" vs "this is *in* that" vs "this came *from* that"). The property naming and comment must carry that distinction clearly.

- **What downstream consumers must adapt to.** Nothing required at ingestion; `top:partOf` is optional at Core. A consumer that declared its own part-whole property (e.g., `scientix:componentOf`) may map it by `rdfs:subPropertyOf top:partOf` or `owl:equivalentProperty` when TOP alignment is desired.

- **Follow-on work.** The accepting ADR; the Core implementation PR (`core/partof` branch → `core/v1/shapes.ttl`); the spec page (`core/v1/index.html`) property list; demonstration in a walkthrough (e.g., the blood-draw material-lineage case); the controlled-vocabulary record when the CV layer lands (ADR-0018); decisions on open questions 1–3; likely refinements in the clinical-research and equipment-management workflows as the first `rdfs:subPropertyOf` specializations.

- **What this forecloses.** The root property name (`top:partOf`). Workflows are free to refine it (`cr:aliquotOf`, `eq:componentOf`), but the shared primitive is now named. The decision to use one domain-neutral property rather than FPF's four typed relations (the altitude choice in `fpf-comparison.md`) is committed; revisiting it would require a superseding RFC.

## References

- [`governance/planning/fpf-comparison.md`](../planning/fpf-comparison.md) § "The mereology fork (the immediately actionable one)" — the strategic planning note that identified the gap and recommended one BFO-aligned Core relation.
- ADR-0019 (flavors, Tightenable) in [`../decision-log.md`](../decision-log.md) and [`../extension-contract.md`](../extension-contract.md) — the open-core model that lets workflows refine Core properties via `rdfs:subPropertyOf`.
- ADR-0022 (Agency is a role, add `top:hasSubject`) in [`../decision-log.md`](../decision-log.md) — the precedent for a Tightenable Core property with `top:CommonEntity` domain and range, refined by workflows in their shapes.
- BFO 2020 `bfo:part-of` ([Basic Formal Ontology](https://github.com/BFO-ontology/BFO)) — the OBO-Foundry mereological primitive that `top:partOf` aligns to.
- FPF (First Principles Framework) Advanced Mereology (A.14) at [github.com/ailev/FPF](https://github.com/ailev/FPF) — prior art for the four-way mereology typology (credited as design vocabulary; not imported as runtime taxonomy).
- ADR-0013 (practitioner-first) and ADR-0012 (three-level architecture) in [`../decision-log.md`](../decision-log.md) — the design posture that keeps Core minimal and domain-neutral.
- RFC 0001 (declare `top:recordedAt`) in [`accepted/0001-declare-recordedat.md`](../accepted/0001-declare-recordedat.md) — parallel structure (reconciliation of a known-needed property, Tightenable flavor, optional at Core).

## Notes for reviewers

Bo: the transitivity declaration (line 2 of the Turtle: `owl:TransitiveProperty`) and the BFO alignment (`rdfs:subPropertyOf bfo:part-of`) are the two substantive design calls. The rest is bookkeeping. Open question 1 (inverse property) and open question 2 (cardinality tightening in a Core shape as an existence proof) are worth your read if either would change the recommendation.

---

**Trailer:** Runtime: Grok Bot Sophia desk session 2026-09-10
