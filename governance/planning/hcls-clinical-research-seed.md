# Seed: HCLS Clinical-Research Reference Graph for TOP Launch

*Status: seed for a future RFC. Author: Bo Lora (Clinical Research BDLS, sole signatory to The Ontology Project as of 2026-05-14). Audience: Bo for near-term build planning; the Clinical Research Working Group when it forms; future HCLS domain leads (care-delivery, public-health, registries) who will follow the clinical-research pattern.*

*Companion to TOP Core (one root, eight categories, twenty-eight leaves) and to ADRs 0001–0017. Pre-RFC; the formal RFC process starts when the working group does.*

---

## Why this document exists

TOP Core is intentionally small. One root, eight categories, twenty-eight leaves, with class-level PROV-O alignment and light-edge BFO where it lands cleanly. The smallness is deliberate. Practitioner-first (ADR-0013) means Core stays in vocabulary a clinical coordinator, a manufacturing operator, or a supply-chain logistician all recognize without needing translation.

The smallness has a consequence. The first workflow extension TOP ships is a load-bearing artifact. It has to demonstrate that Core composes into a real, regulated-industry reference graph without distorting Core itself. The clinical-research workflow is that demonstrator. TOP does not launch with Core alone. TOP launches with Core plus a fully-built clinical-research reference graph, anchored in the operator workflow of a sponsor, a site, an investigator, and a participant, with the regulator-facing standards (CDISC, FDA, ICH, MedDRA) projecting cleanly from the same underlying source.

This document is the seed of that build. It captures the two architectural decisions that have to settle before the class-level work begins:

1. **How clinical-research relates to its sibling HCLS workflows** (care-delivery especially, with oncology as the densest overlap case).
2. **How external regulated-industry vocabularies attach** without forcing TOP to author and maintain N×N crosswalks.

Both decisions are surfaced here with recommendations. The recommendations are designed so a working group inheriting this seed can either ratify them through an RFC, or push back with a specific competing architecture, but in either case does not have to rediscover the question.

## What this seed proves to whom

Three audiences read TOP at launch.

**Regulators and standards bodies** read TOP to ask whether it harmonizes with CDISC SDTM, ICH-GCP E6 R3, FDA 21 CFR Part 11, and the evolving USDM / DDF / Vulcan / SOA ecosystem. The clinical-research reference graph has to project cleanly into these standards without claiming to replace them. Standards-as-projection is the posture (per first-principles.md § 1, the human-down inversion). The clinical-research graph operationalizes that posture.

**HCLS practitioners** read TOP to ask whether the names match the workday. A study coordinator, a CRA, a regulatory affairs lead, a pharmacovigilance scientist, a PI, a research nurse, a research pharmacist. Each has a vocabulary. The reference graph either matches it or fails the practitioner-first commitment from ADR-0013. The 431-concept site-level SOP controlled vocabulary built 2026-05-13 (`research/SOPs/raw-sop-research/CLAUDE OUTPUTS/site-sop-controlled-vocabulary_yaml_v1.yaml`) is one operator-vocabulary input. There will be others as the reference graph deepens.

**Frontier-AI consumers** read TOP to ask whether agents can reason against it. Audit-trail provenance through PROV-O (ADR-0001). Subset-grounded alignment through NCIt (this document, Part 3). Operator-vocabulary preservation through Core's smallness (ADR-0013). A model grounded in the clinical-research reference graph can answer "what is this entity, when was it captured, who attested to it, what does it mean in CDISC SDTM terms, what does it mean in MedDRA, what's the source document this CRF entry derives from" without hallucination, because every step is a graph traversal rather than a learned association.

The launch case is the JPM Healthcare Week 2027 audience: biopharma executives, sponsors, CROs, regulators in the room. The clinical-research reference graph is what they evaluate. If it reads as serious and practitioner-grounded, TOP earns the right to grow.

## The mission anchor

TOP exists to be **provenance infrastructure for HCLS decision architecture.** In an era when frontier AI is being deployed against high-consequence regulated data faster than the data can be made trustworthy, the failure mode is not theoretical. A hallucinated dose, a misattributed adverse event, a missing audit trail kills people. The clinical lifecycle is one of the highest-stakes domains where this collision plays out.

Every architecture choice in this seed traces back to that anchor. Where two patterns are equally clean in the abstract, the one that preserves provenance and operator agency wins. Where a tempting shortcut would let the data drift from its source, the seed names the temptation explicitly and refuses it.

## Two tests the architecture must pass

**The smart-hospital-sponsoring-a-trial test** (already named in ADR-0004). Every sponsored hospital trial uses both clinical-research and care-delivery workflows over the same Person / Organization / Site / Visit foundation. A single instance is simultaneously a Subject (research) and a Patient (care). The architecture must handle that without minting Subject-with-care-attached and Patient-with-research-attached as separate types.

**The adverse-event-crossing-the-boundary test** (surfaced 2026-05-14). A patient on a PARP-inhibitor oncology trial getting carboplatin as the standard-of-care backbone experiences nausea after the infusion. That nausea is simultaneously a research event (IRB-reportable, sponsor-reportable, CDISC SDTM AE domain, MedDRA-coded for FDA submission) and a care event (chart-documented, clinician-noted, ICD-10 R11.0, SNOMED 422587007). One nausea. One nurse documenting it. Two regulatory pathways downstream. The architecture must absorb that without forcing the nurse to enter the same observation twice in different vocabularies.

Both tests are stated up front because they are the failure conditions that drive Part 2's choice. A pattern that passes the smart-hospital test but fails the AE-boundary test is incomplete. A pattern that passes both at the cost of an unwieldy intermediate layer trades one failure for another.

---

## Part 1: The HCLS workflow shape

### The problem, operator-down

Clinical-research and care-delivery overlap. The overlap is densest in oncology, but it is not unique to oncology. Cardiology trials use standard-of-care imaging. Pulmonology trials use standard-of-care spirometry. Pediatric trials run in the same hospitals that admit the same children to the same wards for the same conditions. The boundary between "this is research" and "this is care" lives in the operator's head, not in the data shape.

The architecture cannot pretend the boundary is sharper than it is. It also cannot dissolve the boundary entirely (regulators require sponsor-side accountability for what happens to a research subject in ways they do not require for a routine clinical encounter). The architecture has to model both.

ADR-0004 commits TOP to composable workflow extensions over a shared Core, not sibling reference graphs by industry. That commitment is correct and stays. The question this seed answers is the next-level-down: **when two workflows share a concept, how does the shared concept attach to each workflow?**

### Four patterns

| Pattern | What it does | What it preserves | Where it fails |
| --- | --- | --- | --- |
| **A. Flat sibling, instance composition only.** | Both workflows under Core. A Person can hold both classifications at the instance level; no class-level relationship. | Maximum simplicity. ADR-0004 unchanged. | Concepts that genuinely cross (Treatment, Visit, Procedure, AdverseEvent) get awkwardly homed in one workflow with the other importing. The AE-boundary test bends but does not break — the import works mechanically — but the operator has to know which workflow owns the term. |
| **B. Cross-workflow `subClassOf` allowed.** | A clinical-research class can declare `rdfs:subClassOf` against a care-delivery class (or vice versa) when the concept genuinely crosses. `topcr:OncologyTreatment rdfs:subClassOf topcd:Treatment, top:Activity`. | Flat-sibling workflow directories. Operator vocabulary preserved on both sides. ADR-0004 still holds (workflows compose, not sibling). | Care-delivery becomes a class-level dependency of clinical-research. Version skew between workflows becomes a real concern. Governance has to control which cross-workflow declarations are valid. |
| **C. Intermediate shared HCLS tier.** | A `shared-clinical/` layer (namespace `topcs:`) between Core and the individual HCLS workflows holds concepts both clinical-research and care-delivery need: Patient, Visit, Treatment, Procedure, MedicalCondition. Each workflow specializes from both Core and the shared tier. | Concepts that genuinely cross have a clear home. | Requires defending the line between "Core-universal" and "shared-clinical-only" on every new concept. Risks recreating the "Healthcare-TOP sub-federation" failure mode ADR-0004 rejected, at a smaller scale. Increases the namespace surface area; future contributors have one more namespace decision to make on every class. |
| **D. Promote shared concepts back to Core.** | Treatment, Procedure, Encounter, MedicalCondition become Core leaves alongside Person, Organization, Site, Visit. | One structural anchor. | Breaks the manufacturing test. Manufacturing has Batches and Materials, not Treatments. Promoting workflow-specific concepts to Core dilutes ADR-0013 (practitioner-first) by absorbing things that aren't truly universal across every TOP workflow. Core stops being small. |

### Recommendation

**Pattern B, narrowly scoped, with an explicit oncology caveat.**

Cross-workflow `rdfs:subClassOf` is allowed when (and only when) the concept genuinely crosses both workflows' operator semantics. The test is operator-grounded, not engineering-grounded:

- A nausea AE in an oncology trial: passes. It is both a research event (sponsor-reportable, MedDRA-coded) and a care event (chart-noted, ICD-10 coded). `topcr:AdverseEvent rdfs:subClassOf topcd:AdverseEvent, top:Observation`.
- An infusion in an oncology trial backbone: passes. It is both research administration and care treatment. `topcr:StudyMedicationAdministration rdfs:subClassOf topcd:MedicationAdministration, top:Activity`.
- A clinical-research `Sponsor`: fails. It is not a care-delivery concept. Stays in clinical-research only.
- A clinical-research `IRBApproval`: fails. Not a care-delivery concept. Stays in clinical-research only.

Each cross-workflow `subClassOf` declaration is documented in the dependent workflow's spec page with a one-line operator-grounded justification. A future PR adding a new cross-workflow declaration trips a review checkbox: "this concept genuinely crosses both workflows' operator semantics, as evidenced by..."

The discipline keeps the cross-workflow surface small. Most clinical-research classes do not cross into care-delivery; only the dense overlap (clinical interventions, AEs, visits, procedures, samples in some contexts) does.

### Why not the others

**Why not Pattern A.** It is technically sufficient (the AE-boundary test bends rather than breaks), but it pushes the burden of knowing which workflow owns each shared concept into operator memory and into custom adapters. The seed's bar is launch-grade. Asking practitioners to translate between workflows for every cross-cutting concept fails the human-down posture from first-principles.md § 1.

**Why not Pattern C.** The governance overhead is the killer. Every new class proposed by a future WG triggers a debate: does this belong in Core, in shared-clinical, or in our workflow? The debate is not always resolvable on principle (the boundary between "needed by care-delivery and clinical-research" and "needed only by clinical-research" is empirical, not architectural). Defending the boundary becomes the project's permanent work, and it is governance work, not architecture work. Pattern B handles the same crosses surgically without the governance load. Pattern C is an option in reserve for if oncology specifically (or another dense overlap zone) accumulates enough cross-workflow declarations that a scoped intermediate tier is warranted. That promotion path is described below.

**Why not Pattern D.** Core absorption breaks the manufacturing test. Treatment is not a universal TOP concept (a pharmaceutical batch is not a treatment, a logistics shipment is not a treatment). Promoting Treatment to Core would either force manufacturing and supply-chain to inherit a concept they don't use, or it would force Core to carry conditional semantics (a Core leaf that applies in some workflows but not others), which is exactly the entity-with-flags antipattern ADR-0015 rejects.

### The oncology caveat

Oncology is the densest cross-workflow zone in HCLS. If, after the clinical-research v1 reference graph ships and care-delivery joins it, the cross-workflow `subClassOf` declarations under oncology accumulate to the point where the pattern becomes hard to maintain (a rough threshold: more than a dozen cross-workflow declarations specific to oncology, with operator-grounded justifications that share a common shape), the future WG has a clean RFC path:

**Promote an oncology-shared tier.** Introduce `oncology-shared/` (namespace `topcsx:` or similar) as a sub-pattern of Pattern C, scoped specifically to oncology rather than to all of HCLS. The shared tier holds the oncology-specific concepts both clinical-research and care-delivery need (TumorMeasurement, ChemotherapyRegimen, RECIST assessment, etc.). The general clinical-research / care-delivery boundary stays at Pattern B; only oncology lifts.

This is the failure-mode-aware fallback. It keeps Core small while admitting that one HCLS sub-domain may need its own shared layer. Other sub-domains (cardiology, pulmonology, etc.) follow the same promotion path if and when they accumulate similar pressure.

### What this commits the project to

- ADR-0004 stands. Workflows compose, not sibling, at the directory level.
- A new ADR (ADR-0018 when this seed ratifies) authorizes cross-workflow `rdfs:subClassOf` declarations subject to the operator-grounded crossing test.
- Each cross-workflow declaration appears in the dependent workflow's spec page with a one-line justification, and PR review enforces that.
- Pattern C in scoped form remains available as a future RFC for dense sub-domain overlaps (oncology first; others as warranted).
- Care-delivery is queued behind clinical-research on the roadmap precisely because the dependency graph then is real rather than theoretical. Care-delivery ships next; oncology-shared decisions happen after that.

---

## Part 2: External vocabulary alignment

### The problem

A clinical trial sits at the meeting point of at least a dozen controlled vocabularies. CDISC SDTM and Protocol shape what regulators expect. MedDRA codes every adverse event the FDA reads. SNOMED CT and ICD-10 carry the conditions clinicians put in the chart. RxNorm names US drug products. LOINC names labs and observations. HGNC names genes when biomarkers enter the trial. FDA UNII names active ingredients. SPL is the structured product label. ICSR is the schema safety reports serialize into. mCode is the FHIR-aligned oncology dataset. ICH-GCP is the conduct framework. USDM and DDF are CDISC's emerging unified study definition and digital data flow standards. And the site SOPs speak operator dialect on top of all of it.

Authoring bilateral crosswalks between every pair of vocabularies is the N×N maintenance failure mode. TOP cannot afford it.

### The architectural insight

Three NCI infrastructures resolve this when taken together.

First, **NCI EVS publishes CDISC, FDA, ICH, mCode, HL7 UCUM, the FDA-NIH Modernizing Research and Evidence Glossary, and other regulated-industry vocabularies as curated subsets of the NCI Thesaurus.** A clinical-research class that anchors to an NCIt concept inherits subset membership in every subset that concept belongs to. CDISC alignment, ICH alignment, FDA alignment, mCode alignment all come at no incremental cost. The subset query is one REST call against the EVS API.

Second, **NCI EVS publishes the FDA-side terminology** (UNII for ingredients, SPL for labels, GUDID for devices, ICSR for safety reports, PQCMC for quality, NDF-RT for drug classes, the Problem List subset) in a separate FTP directory. These are not part of the NCIt graph proper; they attach to clinical-research classes as typed identifier properties or reference schemas.

Third, **NCI EVS publishes eighteen mapsets through its REST API** that bridge NCIt to vocabularies outside the NCIt graph: NCIt → MedDRA, NCIt → ICD10CM, NCIt → ICD10, NCIt → ChEBI, NCIt → HGNC, NCIt → SwissProt, NCIt → GDC, NCIt → ICDO3 (three variants), plus SNOMEDCT_US → ICD10CM and a handful of other internal bridges. Every mapset has NCIt at one end. The pattern is hub-and-spoke with NCIt as the hub.

The architectural commitment: **anchor clinical-research classes to NCIt concepts via `skos:exactMatch` / `skos:closeMatch`, and the rest of the vocabulary stack composes through that one anchor.**

### Four tiers of alignment

**Tier 1: NCIt as the SKOS alignment hub.** Every clinical-research class that has an NCIt peer declares it in the workflow's SKOS taxonomy file. Same pattern as the schema.org alignment in ADR-0016.

```turtle
@prefix topcr: <https://top.scientix.ai/clinical-research/v1#> .
@prefix ncit: <http://purl.obolibrary.org/obo/NCIT_> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

topcr:AdverseEvent
    rdfs:subClassOf top:Observation, topcd:AdverseEvent ;   # Pattern B applied
    skos:exactMatch ncit:C41331 ;                            # NCIt anchor
    skos:prefLabel "Adverse Event"@en .
```

One anchor. Everything downstream composes through it.

**Tier 2: Inherited subset membership.** Clinical-research formally adopts a NCIt subset whitelist as its alignment target set:

| Subset | NCIt code | Why |
|---|---|---|
| CDISC | C61410 | SDTM, SEND, ADaM, CDASH, Glossary, Protocol — all in one subtree |
| FDA Terminology | C131123 | FDA-specific controlled terms |
| ICH | C217022 | ICH-GCP, ICH E2A, ICH E6, ICH E9 |
| FDA-NIH Modernizing Research and Evidence Glossary | C220787 | Cross-agency harmonization |
| mCode | C193006 | FHIR-aligned oncology |
| HL7 Unit of Measure | C68669 | Units for vitals and labs |
| UCUM | C67567 | Complementary measurement units |
| Pediatric Terminologies | C165276 | Pediatric trial overlay |
| HemOnc | C201599 | Hematology / oncology regimens |
| Childhood Cancer Predisposition Study | C177281 | Rare-disease pediatric oncology |

When clinical-research's `AdverseEvent` anchors to NCIt:C41331 (Adverse Event), it inherits CDISC SDTM AE domain alignment, ICH E2A definition, FDA-NIH Glossary alignment, and (in oncology trials) mCode alignment. No additional triples in the workflow.

Whitelist additions or removals route through RFC, because they affect what downstream consumers can rely on.

**Tier 3: External crosswalks via EVS REST mapsets, carried as SSSOM artifacts.** For vocabularies outside the NCIt graph (MedDRA, SNOMED CT, ICD-10, HGNC, ChEBI, etc.), the workflow consumes the EVS REST mapsets as the bridge. The mapsets become SSSOM-formatted TSV files (the Simple Standard for Sharing Ontological Mappings, already named in TOP's roadmap as the carrier format).

```
clinical-research/v1/mappings/
├── ncit-to-meddra.sssom.tsv          (NCIt 26.04d → MedDRA, refreshed quarterly)
├── ncit-to-icd10cm.sssom.tsv          (NCIt 26.04d → ICD-10-CM)
├── ncit-to-chebi.sssom.tsv            (NCIt → ChEBI, Aug 2024)
├── ncit-to-hgnc.sssom.tsv             (NCIt → HGNC, Apr 2026)
├── ncit-to-swissprot.sssom.tsv        (NCIt → UniProt, Apr 2026)
├── ncit-to-gdc.sssom.tsv              (NCIt → Genomic Data Commons)
├── snomedct-to-icd10cm.sssom.tsv      (SNOMED CT → ICD-10-CM, Sep 2025)
└── icd10-to-meddra.sssom.tsv          (ICD-10 → MedDRA, Jul 2023)
```

Each mapping file is mirrored from the EVS REST API at a pinned version, with version and refresh date in the SSSOM metadata block. Mapset upgrades land as PRs; downstream consumers can audit what's in play and when it changed.

**Tier 4: FDA EVS regulated-product directory.** Vocabularies in the FDA FTP directory that are not part of the NCIt graph attach as typed identifier properties or reference schemas, not as class-level alignment.

| FDA artifact | Attaches to | Mechanism |
|---|---|---|
| UNII | `topcr:InvestigationalProduct`, `topcr:DrugSubstance`, `topcr:Comparator` | Active-ingredient identifier property |
| SPL | `topcr:InvestigatorsBrochure`, `topcr:PackageInsert` | Source-document reference for marketed-product IBs |
| GUDID | `topcr:InvestigationalDevice` | Device identifier property |
| ICSR | `topcr:SAEReportForm`, `topcr:INDSafetyReport` | Schema for regulator-facing serialization |
| NDF-RT | `topcr:ConcomitantMedication` | Drug-class taxonomy reference (older but still cleanest) |

These are properties on clinical-research entities, not SKOS class alignments.

### How the site SOP vocabulary lands

The 431-concept site-level SOP controlled vocabulary built 2026-05-13 is operator-vocabulary input for clinical-research. Two paths for how it lands:

**Path (a): Co-author into clinical-research SKOS.** Each SOP concept becomes either a workflow class (if its semantics warrant a class) or a `skos:altLabel` on an existing class. The 431 concepts inform the workflow's vocabulary directly.

**Path (b): Ship as a separate aligned file.** `clinical-research/v1/site-sop-vocabulary.ttl` lives alongside the workflow taxonomy with `skos:closeMatch` triples bridging the two. SOP vocabulary keeps its own provenance to the 98 source SOPs.

Recommendation: **Path (b) for v1.** It preserves the SOP vocabulary's source-grounded provenance (which is the whole point of the work). Path (a) can replace it later if the working group judges the indirection adds friction without adding value. Starting with (b) preserves the option to consolidate; starting with (a) means the SOP vocabulary's provenance gets diluted into the workflow file and is hard to reconstruct.

### USDM and DDF specifically

CDISC's **Unified Study Definitions Model (USDM)** and **Digital Data Flow (DDF)** initiatives are the protocol-design-side and data-design-side of an emerging open standards stack. USDM defines a study at the protocol level (schedule of activities, eligibility criteria, endpoints, study arms). DDF defines how protocol metadata flows into downstream operational systems.

Both are NCIt-published as part of the CDISC subset (NCIt code C61410). Clinical-research classes in the Study Design functional area (Part 4 below) anchor to USDM concepts directly via Tier 1. Classes in the Data Management functional area anchor to DDF concepts via the same mechanism. The architectural pattern is the same. USDM and DDF are not special cases; they are first-class citizens of the CDISC subset, alignable through the same Tier-1 anchor.

Worth calling out because USDM and DDF are where regulatory expectations are moving over the next three to five years. A clinical-research reference graph that anchors cleanly to them at launch is positioned for the regulatory direction, not against it.

### What this tier-stack does NOT do

- It does not bring NCIt vocabulary into Core. NCIt is an external dependency, accessed through SKOS alignment triples and SSSOM mapping files. Core's eight categories and twenty-eight leaves are unchanged.
- It does not commit TOP to publishing crosswalks from TOP back to NCIt. The direction is TOP → NCIt → everything else, not bidirectional.
- It does not change ADR-0013 (practitioner-first). External vocabularies live at the edge. Clinical-research class names, property names, and operator-vocabulary stay practitioner-shaped. The alignment is annotation, not naming.

---

## Part 3: Clinical-research v1 launch scope

The clinical-research workflow extension organizes around twelve operational functional areas, named on the roadmap on 2026-05-11 from the operator-vocabulary reframe. For each area below, the seed names the scope envelope (what ships in v1) without yet authoring the classes. Three areas are explored in worked-example detail because they stress-test the architecture hardest.

### The twelve functional areas

| # | Functional area | v1 scope envelope |
|---|---|---|
| 1 | **Study Design** | Protocol, Synopsis, Eligibility Criteria, Endpoints, Schedule of Activities, Study Arms, IB. USDM-aligned. |
| 2 | **Regulatory Affairs** | IRB / IEC submissions, FDA 1572, IND / IDE numbers, Regulatory Authority interactions, approval letters, continuing review, AE / SAE / SUSAR regulatory reporting. ICH and FDA subsets via Tier 2. |
| 3 | **Finance** | Clinical Trial Agreements, Budgets, Per-Subject payment schedule, Indemnification, Insurance, Reimbursement and Compensation tracking. |
| 4 | **Setup** | Site Identification, Site Qualification Visit, Site Initiation Visit, Site Activation, Pre-Admission Trial Team Meetings. |
| 5 | **Site Management** | DOA Log, Signature Log, Training Log, GCP Training records, Source Document maintenance, ISF / Regulatory Binder. |
| 6 | **Clinical Supply** | IMP receipt, storage, dispensing, accountability, return, destruction. Lot / batch / kit / UNII identifiers. Tier 4 FDA attachments. |
| 7 | **Recruitment** | Pre-screening, screening, eligibility checklist, enrollment, randomization, screen-failure tracking. |
| 8 | **Intervention** | Study medication administration, treatment cycles, dose modifications, premature discontinuation. **Densest cross-workflow zone — worked example below.** |
| 9 | **Pharmacovigilance** | AE, SAE, SUSAR, UADE, UP, concomitant medications, causality, expectedness, outcome, IND Safety Reports, ICSR. **Densest external-vocabulary zone — worked example below.** |
| 10 | **Data Management** | CRF / eCRF, source data verification, queries, data clarification forms, audit trail, database lock. DDF-aligned. |
| 11 | **Monitoring** | SIV, IMV, COV, FCV, monitoring plan (comprehensive and concise), monitoring report, follow-up letter, confirmation letter. |
| 12 | **Quality Management** | QM Studywide Review, QM Subject Data Review, CAPA, Note to File, Audit, Inspection. |

### Worked example: Pharmacovigilance (Part 9)

Pharmacovigilance is where the architecture's external-vocabulary alignment matters most. A single adverse event participates in at least five vocabularies simultaneously.

```turtle
@prefix topcr: <https://top.scientix.ai/clinical-research/v1#> .
@prefix topcd: <https://top.scientix.ai/care-delivery/v1#> .
@prefix top: <https://top.scientix.ai/v1#> .
@prefix ncit: <http://purl.obolibrary.org/obo/NCIT_> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

topcr:AdverseEvent
    a owl:Class ;
    rdfs:subClassOf top:Observation, topcd:AdverseEvent ;     # Pattern B: crosses to care-delivery
    rdfs:subClassOf prov:Entity ;                              # PROV-O class alignment (ADR-0001)
    skos:exactMatch ncit:C41331 ;                              # NCIt anchor (Tier 1)
    skos:prefLabel "Adverse Event"@en ;
    skos:definition "Any untoward medical occurrence in a clinical investigation subject..." ;
    rdfs:comment "Inherits CDISC SDTM AE domain alignment via NCIt:C41331 ∈ CDISC subset (C61410). Inherits ICH E2A definition via ICH subset (C217022). MedDRA coding available via clinical-research/v1/mappings/ncit-to-meddra.sssom.tsv. ICD-10-CM coding available via ncit-to-icd10cm.sssom.tsv." .

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

One graph traversal answers regulator questions ("show me every CDISC SDTM AE in this trial coded to MedDRA Preferred Term"), clinician questions ("show me this patient's adverse events with ICD-10 codes for billing"), and AI-agent questions ("show me every observation that is also a care-delivery AE, with attestation chain"). Operator vocabulary is preserved throughout (`AdverseEvent`, not `topcr:ResearchSubjectObservationOfUnfavorableOutcome`).

### Worked example: Intervention (Part 8)

Intervention is where Pattern B's cross-workflow `subClassOf` matters most. Oncology trials are the densest case: an infusion of investigational PARP inhibitor administered alongside carboplatin standard-of-care is both research and care.

```turtle
topcr:StudyMedicationAdministration
    a owl:Class ;
    rdfs:subClassOf topcd:MedicationAdministration, top:Activity ;   # Pattern B: crosses to care-delivery
    rdfs:subClassOf prov:Activity ;
    skos:exactMatch ncit:C70770 ;
    skos:prefLabel "Study Medication Administration"@en ;
    rdfs:comment "Cross-workflow subClassOf justified: the same administration is documented in the EHR (care-delivery) and on the CRF (clinical-research). Operator (research nurse, oncology infusion RN) documents once; downstream consumers project into their respective regulatory paths." .

topcr:ConcomitantMedicationAdministration
    a owl:Class ;
    rdfs:subClassOf topcd:MedicationAdministration, top:Activity ;   # Pattern B again
    rdfs:subClassOf prov:Activity ;
    skos:prefLabel "Concomitant Medication Administration"@en ;
    rdfs:comment "Same cross-workflow rationale: the carboplatin administration is care-delivery primary, clinical-research observational. Operator documents the dose; both workflows project from it." .
```

The cross-workflow declarations are explicit, justified, and reviewable. A future PR that proposes `topcr:Sponsor rdfs:subClassOf topcd:Organization` would fail the operator-grounded test (Sponsor is not a care-delivery operator vocabulary concept) and would be rejected in review.

### Worked example: Study Design (Part 1)

Study Design is where USDM alignment matters most. USDM defines the protocol-level entities CDISC expects downstream.

```turtle
topcr:Protocol
    a owl:Class ;
    rdfs:subClassOf top:Document ;
    rdfs:subClassOf prov:Plan ;                                # PROV-O alignment: a Protocol is a Plan
    skos:exactMatch ncit:C42775 ;                              # NCIt: Clinical Trial Protocol
    skos:prefLabel "Protocol"@en ;
    rdfs:comment "USDM aligned via NCIt:C42775 ∈ CDISC subset (C61410). DDF-aligned attributes (schedule of activities, eligibility criteria, endpoints) attach as separate workflow classes specializing top:Activity, top:Constraint, top:Outcome." .

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

### What ships in v1 vs deferred

**Ships in v1.**

- All 12 functional areas with at least one anchor class each.
- The three worked examples above (Pharmacovigilance AE family, Intervention oncology overlap, Study Design USDM alignment).
- Site SOP vocabulary as a separate aligned file (Tier 3 carrier).
- NCIt subset alignments via Tier 1 SKOS.
- The 10-subset whitelist named in Part 2.
- The 8 EVS REST mapsets named in Part 2, imported as SSSOM at pinned versions.
- Tier 4 FDA attachments for UNII, SPL, GUDID, ICSR.
- Cross-workflow `subClassOf` declarations against `topcd:*` even though care-delivery ships second (placeholder workflow with stub classes for the few cross-workflow targets needed).

**Deferred to v1.x or v2.**

- FHIR R5 alignment. FHIR carries class shapes, not just terminology, so it needs its own RFC (Open Question 6).
- RxNorm and LOINC alignment. Neither is in EVS REST mapsets; access requires UMLS dependency (Open Question 5).
- Bioregistry registration. Pre-RFC; timing question (Open Question 7).
- Oncology-shared sub-tier (Pattern C escalation). Only happens if cross-workflow declarations accumulate.
- Full care-delivery workflow extension. Ships second on the roadmap.

---

## Part 4: Open questions for working-group resolution

The seed surfaces these so the working group inherits a clean question list. Each has a strawman position in this document; the WG can ratify, modify, or override.

1. **Workflow-overlap pattern choice.** Seed recommends Pattern B narrowly scoped with oncology Pattern-C-promotion path. WG may ratify, soften (Pattern A), or escalate (immediate Pattern C).

2. **Site SOP vocabulary import path.** Seed recommends Path (b) — separate aligned file preserving SOP provenance. WG may consolidate to Path (a) if friction outweighs the preserved provenance.

3. **NCIt subset whitelist governance.** Seed names a 10-subset initial whitelist. WG decides whether additions / removals are RFC-governed centrally or WG-governed per workflow.

4. **Mapset refresh cadence.** Seed pins to specific mapset versions in v1 (versions named in Part 2). WG decides on refresh discipline: PR-per-upgrade, scheduled cadence, or automatic-with-validation.

5. **RxNorm and LOINC handling.** Neither is in EVS REST mapsets. Seed defers to a follow-on RFC. WG decides whether to take a UMLS dependency or seek an alternative access path.

6. **FHIR R5 alignment timing.** FHIR is class-shape, not just terminology. Seed defers to a follow-on RFC. WG decides on the model: same Tier-1 hub pattern, or a class-shape-aware alignment with its own ADR.

7. **Bioregistry registration timing.** Seed defers. WG decides whether to register the `topcr:` prefix and NCIt alignment with Bioregistry at clinical-research launch, before, or after.

8. **Oncology Pattern-C threshold.** Seed names a rough threshold (more than a dozen cross-workflow declarations specific to oncology) for when Pattern C scoped to oncology becomes warranted. WG sharpens the threshold or replaces it.

9. **Care-delivery dependency timing.** Clinical-research v1 ships with cross-workflow `subClassOf` declarations against placeholder care-delivery stubs. The full care-delivery workflow follows. WG decides care-delivery's ship sequence and how the v1 placeholders graduate to real classes.

10. **The 12 functional areas vs CDISC's view.** CDISC organizes around SDTM domains and the USDM data model. The 12 functional areas organize around operator workflow. The two views are complementary, not identical. WG decides whether to surface the SDTM-domain view as a projection (per the roadmap's "Reference architecture for role-specific projections and views") or leave it implicit.

---

## Part 5: Reference patterns

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
    rdfs:comment "Cross-workflow declaration justified: an AE in a research subject is simultaneously a care-delivery observation when the subject is a hospital patient. Practitioner documents once; both workflows project from the source." .
```

One-line operator-grounded justification accompanies every cross-workflow declaration.

### SSSOM mapping file structure

```tsv
# curie_map:
#   NCIT: http://purl.obolibrary.org/obo/NCIT_
#   MEDDRA: https://meddra.org/
# license: https://www.nlm.nih.gov/databases/umls.html (MedDRA license required for use)
# mapping_set_id: https://top.scientix.ai/clinical-research/v1/mappings/ncit-to-meddra
# mapping_set_version: NCIt-26.04d
# mapping_set_source: https://api-evsrest.nci.nih.gov/api/v1/mapset/NCIt_Maps_To_MedDRA
# mapping_date: 2026-05-14

subject_id  subject_label                  predicate_id        object_id           object_label                       mapping_justification
NCIT:C41331  Adverse Event                  skos:exactMatch     MEDDRA:10000001     <preferred-term>                   semapv:LexicalMatching
NCIT:C41332  Serious Adverse Event          skos:exactMatch     MEDDRA:10000002     <preferred-term>                   semapv:LexicalMatching
```

Version, source, date in the metadata block; the body is auditable and downstream-tool-compatible.

### Workflow-extension spec page template

The spec page for `clinical-research/v1/` follows the shape of `core/v1/index.html`: one-paragraph summary, the layered architecture (where it sits relative to Core), the functional areas covered, the alignment summary (NCIt subsets, EVS mapsets, FDA tier-4 attachments), the cross-workflow declarations, the SHACL validations, and the deferred items. Future workflow extensions inherit this shape; care-delivery's spec page follows the same template.

---

## What this seed does NOT do

- It does not author the class catalog. Each functional area's classes ship in a subsequent PR by the WG (or by Bo as solo signatory until the WG forms).
- It does not commit the project to CDISC USDM as a structural parent. USDM alignment is via NCIt subset inheritance at the SKOS level, not via `rdfs:subClassOf usdm:*`. Same posture as BFO and PROV-O alignment.
- It does not change Core. Core's eight categories and twenty-eight leaves are unchanged. Cross-workflow `subClassOf` is a new pattern, not a new layer; the ADR that ratifies it is additive.
- It does not bundle care-delivery's vocabulary. Care-delivery ships second; v1 of clinical-research uses placeholder stubs for the small set of care-delivery classes it crosses into.
- It does not specify the JSON-LD context for NGSI-LD wire compatibility. That is a follow-on (named in ADR-0014 as deferred).

---

## Pointers

- TOP Core taxonomy: `/taxonomy/taxonomy.ttl`, `/taxonomy.md`, `/core/v1/shapes.ttl`, `/core/v1/index.html`.
- First-principles: `/first-principles.md`. Practitioner-first, standards-as-projection, no bespoke flags.
- Roadmap: `/roadmap.md`. 12 functional areas, SSSOM commitment, Bioregistry commitment.
- Decision log: `/governance/decision-log.md`. ADRs 0001–0017. The ratification of this seed appends ADR-0018 (workflow-overlap Pattern B with oncology caveat) and ADR-0019 (NCIt-anchored alignment).
- Unwound RFC draft: `CLAUDE OUTPUTS/_drafts/draft-ncit-anchored-vocabulary-alignment.md`. Substance is incorporated into Part 2 of this seed; the RFC was retracted because the formal RFC process had not started.
- Site SOP controlled vocabulary v1: `research/SOPs/raw-sop-research/CLAUDE OUTPUTS/site-sop-controlled-vocabulary_yaml_v1.yaml`. 431 reconciled concepts with anti-synonyms; carried into clinical-research v1 via Tier 3 (Path b) per Part 2.
- NCI EVS:
  - Subsets: `https://evsexplore.semantics.cancer.gov/evsexplore/subsets/ncit`
  - Mappings: `https://evsexplore.semantics.cancer.gov/evsexplore/mappings`
  - CDISC FTP: `https://evs.nci.nih.gov/ftp1/CDISC/`
  - FDA FTP: `https://evs.nci.nih.gov/ftp1/FDA/`
  - REST API: `https://api-evsrest.nci.nih.gov/api/v1/`
- SSSOM: `https://mapping-commons.github.io/sssom/`
- Bioregistry: `https://bioregistry.io/`

---

*Seed v1. Iterative document. Edit any part; the substance is what we'll work from. When the working group forms and the RFC process formally starts, the substance of this seed becomes the basis for ADR-0018 (workflow-overlap pattern) and ADR-0019 (NCIt-anchored alignment), with the seed itself retained as the source artifact in `governance/rfcs/accepted/` once ratified.*
