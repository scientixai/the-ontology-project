# RFC 0002: HCLS shared acts module

- **Status:** Proposed
- **Date:** 2026-09-10
- **Authors:** Sophia Briet (Acting CKO, digital) <sophia@scientix.ai> (drafted at Bo's direction)
- **Affected groups:** HCLS umbrella WG | Clinical Research WG | Clinical Care WG (when active)
- **Required quorum:** HCLS umbrella WG steward (Bo) plus Clinical Research WG maintainer
- **Supersedes:** n/a
- **ADR on acceptance:** ADR-NNNN (filled in when the RFC ratifies)

## Motivation

What TOP Core did for Equipment — universal setting-neutral leaves — the HCLS bucket now needs for acts. Today, clinical-research and clinical-care workflow extensions each declare their own act classes (`topcr:MedicationAdministration`, `topcd:MedicationAdministration`, etc.), and Pattern B cross-workflow `subClassOf` declarations proliferate. The Core Refinement (CR) seed committed to stub-to-clinical-care parents for these acts, but that forces every act to depend on clinical-care as a containing Scope.

The defect surfaced in operator feedback: a blood draw is a blood draw. The clinical-research variant and the clinical-care variant differ only in *where* they happen (a research study vs. a care encounter) and *why* (to fulfill a protocol vs. to inform treatment). Bo's centrifuge analogy: clinical-research and clinical-care do not split at SpecimenCollection's shape; they split at the Scope that contains it. Setting is an instance property, never a branch in the class tree.

The extract-to-shared test at CR said "three workflows need this same shape, extract to shared layer." That threshold is wrong — it conflicts with ADR-0015 (promote facts to entities; avoid bespoke per-workflow flags) and ADR-0022 (role bindings, not type minting). Two triggers suffice:

1. ≥2 of FHIR, BRIDG, OBI, SNOMED CT procedures, SDTM need it; **OR**
2. Two TOP workflows need the same SHACL shape.

Either condition justifies extraction. The old three-workflow rule is superseded.

MedicationAdministration and SpecimenCollection both pass. FHIR MedicationAdministration, BRIDG SubstanceAdministration, SDTM EX domain, SNOMED CT 432102000 (`administration of substance`). FHIR Specimen, BRIDG SpecimenCollectionActivity, OBI specimen collection, SDTM LB domain. That is ≥2 external vocabularies. Additionally, clinical-research and clinical-care both need them. Both triggers fire.

The current CR seed commits clinical-research to stub-to-care parents; every act points at a clinical-care parent as its ontology home. That forces clinical-research to compose against clinical-care when clinical-research → Core composition is the cleaner dependency. The CR seed says "compose against Core directly **or acts module**" as a backdoor to the fix; this RFC promotes that backdoor to the explicit design.

## Proposal

Add a thin shared HCLS module `hcls/acts/v1/` to hold acts that cross clinical-research, clinical-care, and (anticipated) pharmacovigilance workflow extensions. Classes in the acts module are `rdfs:subClassOf top:Activity`. Workflow extensions (clinical-research, clinical-care, etc.) compose against the acts module via Pattern B when they need the act; they do not redeclare it.

**Strawman prefix:** `topact:` (HCLS umbrella WG ratifies or overrides).

**Purpose model:** An act's purpose attaches via `top:Scope` + `top:containsActivity` only. No `wasInServiceOf` property at the act level. No overlay Research*/Clinical* subclasses in workflow extensions. MedicationAdministration is `topact:MedicationAdministration`, not `topcr:ResearchMedicationAdministration` and `topcd:ClinicalMedicationAdministration`. The Scope that contains the act (a `topcr:Study` vs. a `topcd:Encounter`) is the purpose binding.

**Thinness at CR v1:** 2–4 acts. MedicationAdministration and SpecimenCollection are the seed candidates. Additional candidates exist in the kyron working note 2026-09-10-hcls-architecture (Admission, VitalSignsMeasurement, etc.) but are not committed here. CR v1 extracts only what passes the admission rule below.

**Admission rule:** An act lifts to `hcls/acts/` when:

1. **Operator-named verb.** The name is a term practitioners in both clinical research and clinical care use without disambiguation. "Blood draw" (SpecimenCollection) yes; "AE assessment" no (AE is research-specific vocabulary).
2. **Shape test.** Class boundary exists if and only if required properties differ. If two operator-vocabulary names collapse to the same SHACL shape, they are CV values (kinds), not classes. Example: "oral administration" vs. "IV administration" is `method` or `route` CV values on MedicationAdministration, not two classes.
3. **Extract trigger.** Either ≥2 of FHIR, BRIDG, OBI, SNOMED CT procedures, SDTM declare it; OR two TOP workflows need the same SHACL shape.

**Stress test 3: universality.** Every acts-module class must not depend on any one containing Scope. The act must apply sensibly to clinical-research (AE collection), clinical-care (MedAdmin during hospitalization), pharmacovigilance (Encounter during post-market safety surveillance), and public-health (Procedure during outbreak investigation). If the act only makes sense in one workflow's scope, it stays in that workflow, not in the acts module.

Workflow-specific stubs remain. Clinical-research's `topcr:AdverseEvent` is workflow-specific (it adds protocol-based severity grading, sponsor-reportability logic, MedDRA alignment for regulatory submission). AdverseEvent stays `topcr:`, not `topact:`. Same for clinical-care's `topcd:ClinicalNote` and `topcd:BillingCode` — workflow-specific, not shared acts.

**Supersession:** This RFC supersedes the CR seed's commitment to stub-to-care parents. Clinical-research acts that belong in `hcls/acts/` no longer point to clinical-care parents; they point to the acts module. Clinical-research composes against Core and acts module, not against clinical-care. The CR seed's "compose-against-Core-directly **or acts module**" clause becomes the normative path.

**Bucket placement:** Acts module stays in `hcls/`. "HC" and "LS" are docs labels, not URI segments. Manufacturing/CMC acts (fermentation, lyophilization, formulation) are outside HCLS; if those accumulate cross-workflow pressure, a separate `manufacturing/acts/` follows the same pattern.

**Explicit no-mint commitment:** This RFC does NOT mint any acts-module classes. Bo signature gates first commit to `hcls/acts/v1/shapes.ttl`. The acts module's Turtle stays empty until the umbrella WG ratifies the RFC and Bo signs the implementing PR. This RFC establishes the structure; the class catalog lands separately.

**Holon lineage only:** Acts-module classes declare `rdfs:subClassOf top:Activity` and (for PROV alignment) `prov:Activity`. No outbound references to specific workflow extensions. Pattern B is inbound-only: `topcr:MedicationAdministration rdfs:subClassOf topact:MedicationAdministration, top:Activity` points from clinical-research to acts; acts does not point back.

## Alternatives considered

### A. Keep acts in their originating workflows; use Pattern B exclusively

**What it preserves:** No new module. Clinical-research and clinical-care each own their acts; cross-workflow Pattern B declarations handle reuse.

**What it changes:** Clinical-research acts that belong in both workflows stay in clinical-research and clinical-care points to them. Or vice versa. One workflow becomes the "owner" and the other imports.

**Why not chosen:** The ownership question is unresolvable on principle. Is MedicationAdministration a clinical-care concept that clinical-research borrows, or a clinical-research concept that clinical-care borrows? Operators in both domains claim it. Forcing one workflow to be the dependent violates the symmetry operators recognize. The acts module breaks the tie by being neither.

### B. Promote shared acts to TOP Core

**What it changes:** MedicationAdministration, SpecimenCollection, Admission, etc. become Core leaves under `top:Activity`.

**What it preserves:** No new module. Acts live at the universal layer, same as Equipment, Document, Location.

**Why not chosen:** Breaks ADR-0013 (practitioner-first). MedicationAdministration is not universal across every TOP workflow. A manufacturing plant, a retail bank, a grid operator do not administer medications. Core stops being small if every HCLS act lifts. The acts module keeps Core universal while giving HCLS workflows a shared home.

### C. Oncology-specific acts module scoped to oncology

**What it changes:** An `hcls/oncology-shared/` tier (Pattern C from `top-workflows-strategy.md`) holds oncology-specific acts (ChemotherapyAdministration, RECIST assessment, TumorMeasurement). General HCLS acts stay in their originating workflows.

**What it preserves:** No HCLS-wide acts module. Only oncology escalates to scoped shared layer.

**Why not chosen:** SpecimenCollection and MedicationAdministration are not oncology-specific. They cross cardiology, pulmonology, infectious disease, mental health, pediatrics. The generalization from oncology to HCLS is operator-grounded. If oncology-specific acts accumulate beyond this (ChemotherapyRegimen, RECIST, etc.), Pattern C remains available as the escalation path for *oncology-specific* concepts. This RFC handles the HCLS-wide acts first.

### D. Acts inside clinical-care; clinical-research imports

**What it changes:** Clinical-care owns MedicationAdministration, SpecimenCollection, etc. Clinical-research declares `topcr:MedicationAdministration rdfs:subClassOf topcd:MedicationAdministration`.

**What it preserves:** No new module. Clinical-care is the "home" for medical acts; research borrows.

**Why not chosen:** Forces clinical-research to depend on clinical-care when clinical-research → Core is the cleaner composition. A research-only organization (CRO, academic trial center, sponsor) should not need to pull in clinical-care vocabulary to declare a blood draw. The centrifuge test: clinical-research and clinical-care split at *where* and *why*, not at *what*. The acts module is the *what*.

## Open questions

1. **Acts-module prefix.** Strawman: `topact:`. HCLS umbrella WG ratifies or overrides.
2. **Acts-module governance.** Who reviews PRs adding new acts to `hcls/acts/`? Strawman: HCLS umbrella WG reviews; per-workflow WGs (clinical-research, clinical-care) provide domain input. RFC clarifies.
3. **Acts-module thinness threshold.** CR v1 commits to 2–4 acts. When does the acts module graduate to 10–15? Strawman: when a third HCLS workflow (pharmacovigilance, public-health, registries) activates and needs ≥5 shared acts. WG decides.
4. **NCIt alignment for acts-module classes.** Acts-module classes anchor to NCIt via Tier 1 (per `top-hcls-strategy.md`). Strawman: acts module ships its own `hcls/acts/v1/taxonomy.ttl` with `skos:exactMatch` to NCIt procedure concepts. WG ratifies.
5. **Admission specifically.** Kyron working note 2026-09-10-hcls-architecture lists Admission as a candidate. This RFC does not commit Admission for CR v1. Open whether Admission passes the admission rule or stays workflow-specific. Bo decides at acts-module first-commit review.
6. **Relationship to FHIR R5.** FHIR R5 has Procedure, MedicationAdministration, Specimen, Observation. Acts-module alignment to FHIR R5 is class-shape, not just terminology. Follow-on RFC. Not blocking CR v1.

## Consequences

### What gets easier

- **Clinical-research composes against Core and acts module, not against clinical-care.** A research-only deployer (CRO, sponsor, academic trial site) pulls Core + acts + clinical-research. No clinical-care dependency forced.
- **Symmetric cross-workflow references.** Clinical-research and clinical-care both point to acts module; neither depends on the other for act definitions. The centrifuge works.
- **Predictability across HCLS workflows.** MedicationAdministration means the same thing in clinical-research, clinical-care, pharmacovigilance, public-health. One class, one SHACL shape, one NCIt anchor.
- **ADR-0015 and ADR-0022 compliance.** Acts are promoted to entities (not flags or enums); role bindings (`top:hasSubject`, `top:Scope`) attach purpose without type minting.

### What gets harder

- **One more module to maintain.** Acts module is a new governance surface. HCLS umbrella WG reviews every addition. Overhead is real.
- **Admission threshold ambiguity.** The admission rule (operator-named verb, shape test, extract trigger) requires judgment. Edge cases (is Admission an act? Is VitalSignsMeasurement?) land on WG reviewers.
- **Acts module can bloat if discipline slips.** If every per-workflow difference (ResearchVitalSigns vs. CareVitalSigns) mints a new acts-module class, the module becomes a duplicate of both workflows. The thinness commitment (2–4 at CR v1) is the mitigation, but it requires enforcement.

### What downstream consumers must adapt to

- **Acts move from workflow extensions to acts module.** A consumer that expected `topcr:MedicationAdministration` now references `topact:MedicationAdministration`. Transition: clinical-research v1 can declare `topcr:MedicationAdministration rdfs:subClassOf topact:MedicationAdministration` so both names resolve; the workflow-specific name is marked deprecated at CR v1 acceptance.
- **Purpose attachment via Scope, not act subclass.** A consumer that filtered by class (`topcr:ResearchMedicationAdministration`) now filters by Scope (`top:Scope` is a `topcr:Study`). Query pattern shifts from class-based to role-based.

### Follow-on work

- **Acts-module seed.** Once RFC ratifies, Bo signs the first `hcls/acts/v1/shapes.ttl` commit with MedicationAdministration and SpecimenCollection (and optionally others that pass admission at that time).
- **Acts-module SKOS taxonomy.** `hcls/acts/v1/taxonomy.ttl` with NCIt anchors for every acts-module class. Ships with first commit or immediately after.
- **Acts-module spec page.** `hcls/acts/v1/index.html` documenting the admission rule, the thinness commitment, the purpose model, the cross-workflow alignment.
- **Clinical-research CR v1 update.** CR seed amended: stub-to-care parents superseded; compose-against-acts-module becomes normative. Acts that moved to acts module are removed from `hcls/clinical-research/v1/shapes.ttl` or marked `owl:deprecated` with pointer to `topact:`.
- **Clinical-care v1 coordination.** When clinical-care activates, its seed references acts-module classes. Clinical-care WG does not redeclare MedicationAdministration; it composes against `topact:MedicationAdministration`.
- **FHIR R5 alignment RFC.** Acts-module classes align to FHIR R5 Procedure, MedicationAdministration, Specimen. Follow-on RFC scopes that alignment. Not blocking CR v1.

### What this RFC forecloses

- **The name.** `hcls/acts/` as the directory, `topact:` as the strawman prefix. Changing either after CR v1 ships is costly. HCLS umbrella WG ratifies before first commit.
- **The location.** Acts module stays in HCLS bucket; it does not lift to Core. Manufacturing/CMC acts (if they accumulate) follow this pattern in `manufacturing/acts/`, not in HCLS.
- **The CR seed's stub-to-care parent model.** Superseded. Clinical-research composes against Core and acts module; clinical-care is not in the dependency path for acts.

## References

- ADR-0015 (promote facts to entities — no bespoke flags) in [`../../decision-log.md`](../../decision-log.md)
- ADR-0022 (agency is a role; role bindings, not type minting) in [`../../decision-log.md`](../../decision-log.md)
- `top-hcls-strategy.md` in [`../planning/top-hcls-strategy.md`](../planning/top-hcls-strategy.md)
- `top-workflows-strategy.md` (Pattern B and Pattern C) in [`../planning/top-workflows-strategy.md`](../planning/top-workflows-strategy.md)
- `top-compositions-strategy.md` (emergent-from-composition discipline) in [`../planning/top-compositions-strategy.md`](../planning/top-compositions-strategy.md)
- Kyron working note 2026-09-10-hcls-architecture (internal; lists candidate acts and shared-module rationale)
- Kyron PRs 124–127 (clinical-research CR rebuild; stub-to-care parent pattern in seed, acts-module backdoor clause)
- FHIR R5: `MedicationAdministration`, `Procedure`, `Specimen`, `Observation` resources
- BRIDG: `SubstanceAdministration`, `SpecimenCollectionActivity`
- CDISC SDTM: EX domain (exposure/medication administration), LB domain (labs/specimen)
- SNOMED CT: 432102000 (`administration of substance`), specimen collection concepts
- OBI (Ontology for Biomedical Investigations): specimen collection process

## Notes for reviewers

Bo: the admission rule (§ Proposal, operator-named verb + shape test + extract trigger) is the part I most want your read on. The three-workflow threshold from CR seed is superseded here; two triggers (≥2 external vocabularies OR two TOP workflows) feel right but I want confirmation. The thinness commitment (2–4 at CR v1) protects against bloat; stress test 3 (universality across HCLS workflows) keeps the module honest. If the discipline holds, this is the fix the centrifuge wants.

Clinical Research WG: MedicationAdministration and SpecimenCollection are the seed. Admission is on the bubble (see Open Questions #5). If your seed has acts beyond these three, they land via follow-on PR after the module activates, not in the RFC.

---

*RFC 0002 v1. Draft only. Awaits Bo signature. No ontology TTL changes in this PR.*

Runtime: Grok Bot Sophia desk session 2026-09-10
