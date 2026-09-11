# RFC 0002: HCLS shared acts (`tophcls:`)

- **Status:** Proposed (scope frozen 2026-09-10 by Bo Lora)
- **Date:** 2026-09-10
- **Authors:** Sophia Briet (Acting CKO, digital) <sophia@scientix.ai> (drafted at Bo's direction)
- **Affected groups:** HCLS umbrella WG | Clinical Research WG | Clinical Care WG (when active)
- **Required quorum:** HCLS umbrella WG steward (Bo) plus Clinical Research WG maintainer
- **Supersedes:** n/a (amends `top-hcls-strategy.md` and strategy-brief layer-2 as stated below)
- **ADR on acceptance:** ADR-NNNN (filled when the RFC ratifies)
- **No mint** until Bo signs this RFC.

## Motivation

Core already treats `top:Equipment` as one setting-neutral leaf; setting is an instance-level property, never a branch. A centrifuge in a clinic, a phlebotomy office, and a wet lab is one kind of Equipment. Shared HCLS acts need the same discipline: a blood draw is a blood draw; purpose attaches via Scope, not via mission-branched act classes.

## Proposal (five items only)

### 1. `tophcls:` as the bucket's one thin class namespace

- **Prefix:** `tophcls:`
- **IRI strawman (umbrella WG may adjust path):** `https://top.scientix.ai/hcls/v1#` with directory `hcls/v1/`, mirroring how `top:` maps to `core/v1/`. The **prefix is settled**; the path is a strawman for the umbrella WG.
- **Strategy amendments (honest, not a workaround):**
  - Amends `governance/planning/top-hcls-strategy.md` lines 13 and 24 that forbid a `tophcls:` prefix / treat the bucket as never a class-level namespace.
  - Amends the strategy brief's layer-2 "No classes": the HCLS bucket may host **one** thin class namespace, admitted by the rule in §3.

### 2. Two classes at launch

| Class | Kind properties (CV value sets, never classes) |
| --- | --- |
| `tophcls:SpecimenCollection` | `method` (e.g. venipuncture, fingerstick) |
| `tophcls:MedicationAdministration` | `route`, dose form (e.g. IV push, infusion) |

Both are `rdfs:subClassOf top:Activity`. No other act classes ship under this RFC. Purpose attaches only via `top:Scope` + `top:containsActivity`. No `wasInServiceOf`. No overlay `Research*` / `Clinical*` subclasses.

### 3. Admission rule

An act may enter `tophcls:` when all of the following hold:

1. It is an act on a **living subject**, bound by `top:hasSubject`, and **never** as an `Agent`.
2. It is **shape-distinct** from its sibling acts (required properties differ; otherwise the distinction is a CV kind, not a class).
3. It is modeled **context-neutrally** by **at least two** of: FHIR, BRIDG, OBI, SNOMED CT procedures, SDTM.
4. The **same operator verb** is used in two settings.

Entities that fail this rule stay out of `tophcls:` until a later RFC amends the rule.

### 4. Stress test 3 and CR seed withdrawal

**Stress test 3 (universality):** Is this thing whole on its own (identity, provenance, subject) and part of more than one larger thing? If yes, its class may not depend on any one of them.

Apply that test to the four planned CR-seed stub-to-care parents (AdverseEvent, MedicationAdministration, Encounter, Procedure). This RFC **withdraws** those stub-to-care declarations from the CR seed. Shared acts compose against Core (and, once ratified, against `tophcls:`); they do not take a universal `rdfs:subClassOf` into clinical-care.

### 5. Extraction triggers and pre-v2 review

**Triggers (either sufficient):**

1. External shape evidence from at least two of FHIR, BRIDG, OBI, SNOMED CT procedures, SDTM; **or**
2. Two TOP workflows needing the same shape or SHACL.

The prior three-workflow extraction rule is dropped (conflicts with ADR-0015 and ADR-0022).

**Ritual:** CR-first; candidate register; **pre-v2 review** before further `tophcls:` admissions beyond the two launch classes.

## Three sentences carried from the discussion (no more)

1. **Scope rule.** Acts on a living subject, wherever they occur. Other buckets contain `tophcls:` acts at the instance level when the subject is a living thing.
2. **Dependency rule.** Instance links cross buckets freely through `top:containsActivity`; class dependency never runs from foundations into HCLS; cross-bucket invariants live in compositions, per `top-compositions-strategy.md`.
3. **Prior art.** GS1 EPCIS (ISO/IEC 19987) carries purpose separately from the act. One line; no alignment work under this RFC.

## Worked examples (only these two)

### Blood draw (`tophcls:SpecimenCollection`)

```turtle
:draw-0910 a tophcls:SpecimenCollection ;
    top:hasSubject :maria ;
    prov:wasAssociatedWith :nurse-jane ;
    top:occursAt :mskcc-infusion-suite ;
    prov:generated :tube-12345 .

:onco423 a topcr:Study ;
    top:containsActivity :draw-0910 ;
    top:governedBy :irb-approval-onco423, :ich-gcp-e6 .

:cbc-order-0910 a topcd:Order ;
    top:containsActivity :draw-0910 ;
    top:governedBy :clia-cert-mskcc-lab .
```

One act instance; two Scopes attach purpose. No mission-branched subclass.

### DOT workplace drug test (`tophcls:SpecimenCollection`)

A collector, an HHS-certified lab, and a physician MRO perform an HCLS act inside an **employer's program** Scope. The class carries no mission: not care, not research — employment/transportation safety as Scope via `top:containsActivity`.

```turtle
:dot-urine-0910 a tophcls:SpecimenCollection ;
    top:hasSubject :driver-42 ;
    prov:wasAssociatedWith :collector-7 ;
    prov:generated :specimen-dot-0910 .

:employer-dot-program a top:Scope ;
    top:containsActivity :dot-urine-0910 .
```

## Out of scope (not deliverables of this RFC)

HR module (HR already lives in foundations operational management); a DOT composition; a manufacturing acts module; energy; EPCIS alignment work; veterinary or agricultural extensions. None of it ships before clinical-research v1. Argument and appendix material lives in the kyron topic note, not here.

## Sibling RFC

`top:partOf` remains **RFC 0003**, unchanged in scope from the addendum on kyron#124. Not part of this document.

## Consequences

- **On acceptance:** mint only `tophcls:SpecimenCollection` and `tophcls:MedicationAdministration` under the settled prefix; amend the named strategy lines; withdraw the four CR-seed stub-to-care parents; record ADR number.
- **Until signature:** markdown draft only. **No TTL mint. No Holon CG / Kurt / standards outbound.**

## References

- `governance/planning/top-hcls-strategy.md` (lines 13, 24 — amended by §1)
- Strategy brief layer-2 "No classes" (amended by §1)
- `top-compositions-strategy.md` (dependency rule)
- ADR-0015, ADR-0022
- kyron working note `2026-09-10-hcls-architecture.md` (register, appendices, SOP verb test)
- GS1 EPCIS / ISO/IEC 19987 (prior-art sentence only)

---

*Authored: Sophia Briet (Acting CKO, digital). Runtime: Grok Bot / Sophia desk session 2026-09-10. Scope freeze: Bo mail 2026-09-10.*
