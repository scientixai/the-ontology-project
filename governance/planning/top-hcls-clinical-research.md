# TOP HCLS Clinical-Research v1 Seed

*Status: pre-RFC seed for the clinical-research workflow extension. Author: Bo Lora (BDFL, sole signatory to The Ontology Project as of 2026-05-14). Audience: the future Clinical Research Working Group when it forms; reviewers evaluating TOP at JPM Healthcare Week 2027.*

*Companion to TOP Core, to `top-strategy-brief.md` (the architectural umbrella), to `top-workflows-strategy.md` (workflow-extension discipline), to `top-hcls-strategy.md` (HCLS bucket and the four-tier alignment), and to `top-compositions-strategy.md` (how smart-X compositions reference clinical-research). Pre-RFC; the formal RFC process starts when the Clinical Research Working Group does.*

This seed scopes down to clinical-research v1 specifically. The broader strategy (decomposition discipline, four-tier alignment, Pattern B, oncology Pattern-C escalation, composition relationships) lives in the layer and bucket documents this seed references. The seed inherits all of it.

---

## Why this document exists

Clinical-research is the first workflow extension TOP ships. It is the load-bearing demonstrator that proves Core composes into a real, regulated-industry reference graph without distorting Core itself. The clinical-research workflow extension launches alongside Core; it does not launch later.

This seed captures what clinical-research v1 ships, what it explicitly defers, and the worked examples that stress-test the architecture. The architectural choices it inherits (Pattern B, the four-tier alignment, the functional-areas calibration, the bucket structure) live in `top-workflows-strategy.md` and `top-hcls-strategy.md`; the seed implements them for clinical-research specifically.

## What clinical-research is

Clinical-research is the HCLS workflow extension covering the operational work of designing, conducting, and reporting clinical trials. The workflow operates on regulated industry concepts: sponsor, study, site, participant, visit, investigational product, oversight body, event, plus the operational machinery around them (finance, monitoring, quality management, data management, regulatory affairs, recruitment, intervention, pharmacovigilance, clinical supply).

The workflow lives at `hcls/clinical-research/v1/` with the per-workflow prefix `topcr:` (strawman; HCLS umbrella WG ratifies or overrides per `top-hcls-strategy.md`).

## Why clinical-research is the launch demonstrator

Three audiences read TOP at launch.

**Regulators and standards bodies** read TOP to ask whether it harmonizes with CDISC SDTM, ICH-GCP E6 R3, FDA 21 CFR Part 11, and the evolving USDM / DDF / Vulcan / SOA ecosystem. The clinical-research reference graph has to project cleanly into these standards without claiming to replace them. Standards-as-projection is the posture (per `first-principles.md` § 1, the human-down inversion). The clinical-research graph operationalizes that posture through the four-tier NCIt-anchored alignment (per `top-hcls-strategy.md`).

**HCLS practitioners** read TOP to ask whether the names match the workday. A study coordinator, a CRA, a regulatory affairs lead, a pharmacovigilance scientist, a PI, a research nurse, a research pharmacist. Each has a vocabulary. The reference graph either matches it or fails the practitioner-first commitment from ADR-0013. A 431-concept site-level SOP controlled vocabulary built 2026-05-13 (held externally pending migration into `hcls/clinical-research/v1/site-sop-vocabulary.ttl` when the WG forms) is one operator-vocabulary input. There will be others as the reference graph deepens.

**Frontier-AI consumers** read TOP to ask whether agents can reason against it. Audit-trail provenance through PROV-O (ADR-0001). Subset-grounded alignment through NCIt. Operator-vocabulary preservation through Core's smallness (ADR-0013). A model grounded in the clinical-research reference graph can answer "what is this entity, when was it captured, who attested to it, what does it mean in CDISC SDTM terms, what does it mean in MedDRA, what's the source document this CRF entry derives from" without hallucination, because every step is a graph traversal rather than a learned association.

The launch case is the JPM Healthcare Week 2027 audience: biopharma executives, sponsors, CROs, regulators in the room. The clinical-research reference graph is what they evaluate. If it reads as serious and practitioner-grounded, TOP earns the right to grow.

## The mission anchor

TOP exists to be provenance infrastructure for HCLS decision architecture. In an era when frontier AI is being deployed against high-consequence regulated data faster than the data can be made trustworthy, the failure mode is not theoretical. A hallucinated dose, a misattributed adverse event, a missing audit trail kills people. The clinical lifecycle is one of the highest-stakes domains where this collision plays out.

Every architecture choice in this seed traces back to that anchor. Where two patterns are equally clean in the abstract, the one that preserves provenance and operator agency wins. The HCLS stress tests in `top-hcls-strategy.md` (the smart-hospital-sponsoring-a-trial test and the AE-boundary-test) are the operational failure conditions this seed has to clear.

## The 12 functional areas

Per the functional-areas calibration in `top-workflows-strategy.md` (8-15 areas per workflow extension, 5-30 classes per area), clinical-research decomposes into twelve functional areas.

| # | Functional area | v1 scope envelope |
| --- | --- | --- |
| 1 | **Study Design** | Protocol, Synopsis, Eligibility Criteria, Endpoints, Schedule of Activities, Study Arms, Investigators' Brochure. USDM-aligned. |
| 2 | **Regulatory Affairs** | IRB / IEC submissions, FDA 1572, IND / IDE numbers, Regulatory Authority interactions, approval letters, continuing review, AE / SAE / SUSAR regulatory reporting. ICH and FDA subsets via Tier 2. |
| 3 | **Finance** | Clinical Trial Agreements, Budgets, Per-Subject payment schedule, Indemnification, Insurance, Reimbursement and Compensation tracking. |
| 4 | **Setup** | Site Identification, Site Qualification Visit, Site Initiation Visit, Site Activation, Pre-Admission Trial Team Meetings. |
| 5 | **Site Management** | DOA Log, Signature Log, Training Log, GCP Training records, Source Document maintenance, ISF / Regulatory Binder. |
| 6 | **Clinical Supply** | IMP receipt, storage, dispensing, accountability, return, destruction. Lot / batch / kit / UNII identifiers. Tier 4 FDA attachments. |
| 7 | **Recruitment** | Pre-screening, screening, eligibility checklist, enrollment, randomization, screen-failure tracking. |
| 8 | **Intervention** | Study medication administration, treatment cycles, dose modifications, premature discontinuation. **Densest cross-workflow zone. Worked example below.** |
| 9 | **Pharmacovigilance** | AE, SAE, SUSAR, UADE, UP, concomitant medications, causality, expectedness, outcome, IND Safety Reports, ICSR. **Densest external-vocabulary zone. Worked example below.** |
| 10 | **Data Management** | CRF / eCRF, source data verification, queries, data clarification forms, audit trail, database lock. DDF-aligned. |
| 11 | **Monitoring** | SIV, IMV, COV, FCV, monitoring plan (comprehensive and concise), monitoring report, follow-up letter, confirmation letter. |
| 12 | **Quality Management** | QM Studywide Review, QM Subject Data Review, CAPA, Note to File, Audit, Inspection. |

The twelve areas are the calibration template per `top-workflows-strategy.md`. Other HCLS workflow extensions (clinical-care, pharmacovigilance when graduated, etc.) decompose similarly.

## Pattern B stubs to clinical-care: the launch sequence commitment

Per `top-strategy-brief.md` and `top-hcls-strategy.md`, clinical-research v1 ships with **Pattern B stubs to clinical-care**. This is the operational commitment that makes the launch sequence work.

What this means concretely:

- Clinical-research v1's class declarations that cross into clinical-care (AdverseEvent, MedicationAdministration, Encounter, Procedure) declare `rdfs:subClassOf` against placeholder clinical-care classes (`topcd:AdverseEvent`, `topcd:MedicationAdministration`, `topcd:Encounter`, `topcd:Procedure`).
- A minimal `hcls/clinical-care/v1/` directory exists at clinical-research v1 ship time, with placeholder spec page language and stub class declarations for the few classes clinical-research crosses into. The stubs carry enough structure for SHACL validation to pass; they do not pretend to be a complete clinical-care reference graph.
- Full clinical-care v1 lifts after clinical-research v1 ships. When the clinical-care WG forms, the stubs graduate to real classes; clinical-research's Pattern B declarations point to the same URIs and continue to resolve.
- Each cross-workflow `subClassOf` declaration carries the one-line operator-grounded justification per `top-workflows-strategy.md` Pattern B discipline.

The stubs are honest about the dependency. They are not hidden; they are a documented part of clinical-research v1's seed.

## Worked example: Pharmacovigilance (functional area 9)

Pharmacovigilance is where the four-tier external-vocabulary alignment (per `top-hcls-strategy.md`) matters most. A single adverse event participates in at least five vocabularies simultaneously.

```turtle
@prefix topcr: <https://top.scientix.ai/hcls/clinical-research/v1#> .
@prefix topcd: <https://top.scientix.ai/hcls/clinical-care/v1#> .
@prefix top: <https://top.scientix.ai/v1#> .
@prefix ncit: <http://purl.obolibrary.org/obo/NCIT_> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

topcr:AdverseEvent
    a owl:Class ;
    rdfs:subClassOf top:Observation, topcd:AdverseEvent ;     # Pattern B: crosses to clinical-care
    rdfs:subClassOf prov:Entity ;                              # PROV-O class alignment (ADR-0001)
    skos:exactMatch ncit:C41331 ;                              # NCIt anchor (Tier 1)
    skos:prefLabel "Adverse Event"@en ;
    skos:definition "Any untoward medical occurrence in a clinical investigation subject..." ;
    rdfs:comment "Inherits CDISC SDTM AE domain alignment via NCIt:C41331 within the CDISC subset (C61410). Inherits ICH E2A definition via the ICH subset (C217022). MedDRA coding available via hcls/clinical-research/v1/crosswalks/ncit-to-meddra.sssom.tsv. ICD-10-CM coding available via ncit-to-icd10cm.sssom.tsv." .

topcr:SeriousAdverseEvent
    a owl:Class ;
    rdfs:subClassOf topcr:AdverseEvent ;
    skos:exactMatch ncit:C41332 ;
    skos:prefLabel "Serious Adverse Event"@en ;
    skos:definition "An adverse event that meets one or more seriousness criteria..." .

topcr:SUSAR
    a owl:Class ;
    rdfs:subClassOf topcr:SeriousAdverseEvent ;
    skos:exactMatch ncit:C99613 ;
    skos:prefLabel "Suspected Unexpected Serious Adverse Reaction"@en .
```

One graph traversal answers regulator questions ("show me every CDISC SDTM AE in this trial coded to MedDRA Preferred Term"), clinician questions ("show me this patient's adverse events with ICD-10 codes for billing"), and AI-agent questions ("show me every observation that is also a clinical-care AE, with attestation chain"). Operator vocabulary is preserved throughout (`AdverseEvent`, not `topcr:ResearchSubjectObservationOfUnfavorableOutcome`).

## Worked example: Intervention (functional area 8)

Intervention is where Pattern B's cross-workflow `subClassOf` matters most. Oncology trials are the densest case (per the oncology overlap zone in `top-hcls-strategy.md`): an infusion of investigational PARP inhibitor administered alongside carboplatin standard-of-care is both research and care.

```turtle
topcr:StudyMedicationAdministration
    a owl:Class ;
    rdfs:subClassOf topcd:MedicationAdministration, top:Activity ;   # Pattern B: crosses to clinical-care
    rdfs:subClassOf prov:Activity ;
    skos:exactMatch ncit:C70770 ;
    skos:prefLabel "Study Medication Administration"@en ;
    rdfs:comment "Cross-workflow subClassOf justified: the same administration is documented in the EHR (clinical-care) and on the CRF (clinical-research). Operator (research nurse, oncology infusion RN) documents once; downstream consumers project into their respective regulatory paths." .

topcr:ConcomitantMedicationAdministration
    a owl:Class ;
    rdfs:subClassOf topcd:MedicationAdministration, top:Activity ;   # Pattern B again
    rdfs:subClassOf prov:Activity ;
    skos:prefLabel "Concomitant Medication Administration"@en ;
    rdfs:comment "Same cross-workflow rationale: the carboplatin administration is clinical-care primary, clinical-research observational. Operator documents the dose; both workflows project from it." .
```

The cross-workflow declarations are explicit, justified, and reviewable. A future PR that proposes `topcr:Sponsor rdfs:subClassOf topcd:Organization` would fail the operator-grounded test (Sponsor is not a clinical-care operator vocabulary concept) and would be rejected in review.

## Worked example: Study Design (functional area 1)

Study Design is where USDM alignment matters most (per `top-hcls-strategy.md`). USDM defines the protocol-level entities CDISC expects downstream.

```turtle
topcr:Protocol
    a owl:Class ;
    rdfs:subClassOf top:Document ;
    rdfs:subClassOf prov:Plan ;                                # PROV-O alignment: a Protocol is a Plan
    skos:exactMatch ncit:C42775 ;                              # NCIt: Clinical Trial Protocol
    skos:prefLabel "Protocol"@en ;
    rdfs:comment "USDM aligned via NCIt:C42775 within the CDISC subset (C61410). DDF-aligned attributes (schedule of activities, eligibility criteria, endpoints) attach as separate workflow classes specializing top:Activity, top:Constraint, top:Outcome." .

topcr:ScheduleOfActivities
    a owl:Class ;
    rdfs:subClassOf top:Schedule ;
    rdfs:subClassOf prov:Plan ;
    skos:exactMatch ncit:C156088 ;
    skos:prefLabel "Schedule of Activities"@en ;
    skos:altLabel "SoA"@en, "Schedule of Assessments"@en .

topcr:EligibilityCriterion
    a owl:Class ;
    rdfs:subClassOf top:Constraint ;
    skos:exactMatch ncit:C25303 ;
    skos:prefLabel "Eligibility Criterion"@en ;
    skos:altLabel "Inclusion Criterion"@en, "Exclusion Criterion"@en .
```

Inclusion and Exclusion as `altLabel`s rather than separate classes is a deliberate ADR-0015 application: an Eligibility Criterion is the entity; whether it's inclusion or exclusion is a property of the criterion, not a different class.

## Site SOP vocabulary import path

A 431-concept site-level SOP controlled vocabulary built 2026-05-13 is operator-vocabulary input for clinical-research. Two paths for how it lands:

**Path (a): Co-author into clinical-research SKOS.** Each SOP concept becomes either a workflow class (if its semantics warrant a class) or a `skos:altLabel` on an existing class. The 431 concepts inform the workflow's vocabulary directly.

**Path (b): Ship as a separate aligned file.** `hcls/clinical-research/v1/site-sop-vocabulary.ttl` lives alongside the workflow taxonomy with `skos:closeMatch` triples bridging the two. SOP vocabulary keeps its own provenance to the source SOPs.

Recommendation: **Path (b) for v1.** It preserves the SOP vocabulary's source-grounded provenance (which is the whole point of the work). Path (a) can replace it later if the working group judges the indirection adds friction without adding value. Starting with (b) preserves the option to consolidate; starting with (a) means the SOP vocabulary's provenance gets diluted into the workflow file and is hard to reconstruct.

The vocabulary is held externally pending migration into the repo when the WG forms.

## What ships in v1 vs deferred

**Ships in v1.**

- All 12 functional areas with at least one anchor class each.
- The three worked examples above (Pharmacovigilance AE family, Intervention oncology overlap, Study Design USDM alignment).
- Site SOP vocabulary as a separate aligned file (Path b per above).
- NCIt subset alignments via Tier 1 SKOS (per `top-hcls-strategy.md`).
- The 10-subset whitelist named in `top-hcls-strategy.md` Tier 2.
- The 8 EVS REST mapsets named in `top-hcls-strategy.md` Tier 3, imported as SSSOM at pinned versions.
- Tier 4 FDA attachments for UNII, SPL, GUDID, ICSR.
- Cross-workflow `subClassOf` declarations against `topcd:*` placeholder stubs (per the launch sequence commitment above).

**Deferred to v1.x or v2.**

- FHIR R5 alignment. FHIR carries class shapes, not just terminology, so it needs its own RFC (per `top-hcls-strategy.md` open question).
- RxNorm and LOINC alignment. Neither is in EVS REST mapsets; access requires UMLS dependency (per `top-hcls-strategy.md` open question).
- Bioregistry registration. Pre-RFC; timing question (per `top-hcls-strategy.md` open question).
- Oncology Pattern-C escalation. Only happens if cross-workflow declarations accumulate (per `top-hcls-strategy.md` and `top-workflows-strategy.md`).
- Full clinical-care workflow extension. Ships next on the HCLS roadmap.
- Pharmacovigilance graduation to its own workflow extension. Stays as functional area 9 of clinical-research v1.

## Open questions specific to clinical-research v1

The seed surfaces these so the WG inherits a clean question list. Strategy-level questions (NCIt whitelist governance, mapset refresh cadence, FHIR, RxNorm, LOINC, Bioregistry, etc.) live in `top-hcls-strategy.md`; this list is clinical-research-v1-specific.

1. **Per-workflow prefix.** Strawman: `topcr:`. WG ratifies or overrides.
2. **The 12 functional areas vs CDISC's view.** CDISC organizes around SDTM domains and the USDM data model. The 12 functional areas organize around operator workflow. The two views are complementary, not identical. WG decides whether to surface the SDTM-domain view as a projection (per the roadmap's "Reference architecture for role-specific projections and views") or leave it implicit.
3. **Site SOP vocabulary import path.** Strawman: Path (b). WG may consolidate to Path (a) if friction outweighs the preserved provenance.
4. **Stub-class governance for clinical-care.** The clinical-care stub classes that clinical-research v1's Pattern B declarations point to live in `hcls/clinical-care/v1/`. WG decides who reviews stub additions (clinical-research WG, future clinical-care WG, both, or HCLS umbrella) until clinical-care's WG activates.
5. **JPM Healthcare Week 2027 launch envelope.** What concrete demo readiness counts as "TOP ships clinical-research v1"? Spec page + at least one walkthrough + the three worked examples + the alignment summary? WG decides launch criteria.
6. **Walkthrough catalog.** The seed authors three worked examples in spec form; v1 ships at least one full walkthrough TTL (Maria's Cycle 1 Day 1 visit at MSKCC from the prior pre-Core work is a candidate). WG decides which walkthroughs ship.
7. **SHACL shape granularity.** Strawman per `top-workflows-strategy.md`: one SHACL shapes file per functional area. WG sharpens for clinical-research v1.

## Reference patterns

Worked examples a future contributor pattern-matches against.

### Anchoring a clinical-research class to NCIt

```turtle
topcr:InformedConsentForm
    a owl:Class ;
    rdfs:subClassOf top:Document ;
    rdfs:subClassOf prov:Entity ;
    skos:exactMatch ncit:C16735 ;                # NCIt: Informed Consent Form
    skos:prefLabel "Informed Consent Form"@en ;
    skos:altLabel "ICF"@en, "Consent Form"@en .
```

One Tier-1 anchor; subset inheritance free.

### Cross-workflow `subClassOf` (Pattern B)

```turtle
topcr:AdverseEvent
    rdfs:subClassOf top:Observation, topcd:AdverseEvent ;
    rdfs:comment "Cross-workflow declaration justified: an AE in a research subject is simultaneously a clinical-care observation when the subject is a hospital patient. Practitioner documents once; both workflows project from the source." .
```

One-line operator-grounded justification accompanies every cross-workflow declaration per `top-workflows-strategy.md` Pattern B.

### SSSOM mapping file structure

```tsv
# curie_map:
#   NCIT: http://purl.obolibrary.org/obo/NCIT_
#   MEDDRA: https://meddra.org/
# license: https://www.nlm.nih.gov/databases/umls.html (MedDRA license required for use)
# mapping_set_id: https://top.scientix.ai/hcls/clinical-research/v1/crosswalks/ncit-to-meddra
# mapping_set_version: NCIt-26.04d
# mapping_set_source: https://api-evsrest.nci.nih.gov/api/v1/mapset/NCIt_Maps_To_MedDRA
# mapping_date: 2026-05-14

subject_id  subject_label                  predicate_id        object_id           object_label                       mapping_justification
NCIT:C41331  Adverse Event                  skos:exactMatch     MEDDRA:10000001     <preferred-term>                   semapv:LexicalMatching
NCIT:C41332  Serious Adverse Event          skos:exactMatch     MEDDRA:10000002     <preferred-term>                   semapv:LexicalMatching
```

Version, source, date in the metadata block; the body is auditable and downstream-tool-compatible.

### Workflow-extension spec page template

The spec page for `hcls/clinical-research/v1/` follows the shape of `core/v1/index.html`: one-paragraph summary, the layered architecture (where it sits relative to Core), the functional areas covered, the alignment summary (NCIt subsets, EVS mapsets, FDA Tier-4 attachments), the cross-workflow declarations, the SHACL validations, and the deferred items. Future HCLS workflow extensions inherit this shape; clinical-care's spec page follows the same template.

## What this seed does NOT do

- It does not author the class catalog. Each functional area's classes ship in a subsequent PR by the WG (or by Bo as solo signatory until the WG forms).
- It does not commit clinical-research to CDISC USDM as a structural parent. USDM alignment is via NCIt subset inheritance at the SKOS level, not via `rdfs:subClassOf usdm:*`. Same posture as BFO and PROV-O alignment.
- It does not change Core. Core's eight categories and twenty-nine leaves are unchanged. The Pattern B cross-workflow `subClassOf` is a workflow-level discipline.
- It does not bundle clinical-care's vocabulary. Clinical-care ships next; v1 of clinical-research uses placeholder stubs for the small set of clinical-care classes it crosses into.
- It does not specify the JSON-LD context for NGSI-LD wire compatibility. That is a follow-on (named in ADR-0014 as deferred).

## Pointers

- Strategy brief: `top-strategy-brief.md`
- Workflows strategy: `top-workflows-strategy.md`
- HCLS bucket strategy: `top-hcls-strategy.md` (the four-tier alignment lives here)
- Foundations bucket strategy: `top-foundations-strategy.md`
- Compositions strategy: `top-compositions-strategy.md`
- TOP Core: `core/v1/`, `taxonomy/taxonomy.ttl`
- First-principles: `first-principles.md`, `first-principles.html`
- Manifesto: `manifesto.html`
- Roadmap: `roadmap.md`, `roadmap.html`
- Decision log: `governance/decision-log.md` (ADRs 0001 through 0020)
- NCI EVS resources: listed in `top-hcls-strategy.md`

---

*Clinical-research v1 seed v1. The substance of this seed becomes the basis for ADR-0025 (clinical-research workflow-overlap pattern and v1 scope) when the Clinical Research Working Group forms. ADR number is a strawman.*
