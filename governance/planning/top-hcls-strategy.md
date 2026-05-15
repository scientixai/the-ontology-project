# TOP HCLS Bucket Strategy

*Status: pre-RFC strategic planning. Author: Bo Lora (BDFL, sole signatory to The Ontology Project as of 2026-05-14; HCLS BDFL when the HCLS umbrella WG forms). Audience: future HCLS working groups (clinical-research, clinical-care, pharmacovigilance, public-health, registries), the HCLS umbrella WG, and adopters whose workflows depend on HCLS reference graphs.*

*Companion to TOP Core, to `top-strategy-brief.md` (the architectural umbrella), to `top-workflows-strategy.md` (cross-bucket workflow discipline), to `top-compositions-strategy.md` (how compositions reference HCLS), to `top-foundations-strategy.md` (how smart-X compositions reference both foundations and HCLS), and to `top-hcls-clinical-research.md` (the first HCLS workflow seed). Pre-RFC; the formal RFC process starts when the HCLS umbrella WG forms.*

---

## Why this document exists

HCLS (Healthcare and Life Sciences) is the first domain bucket TOP activates. The clinical-research workflow extension is the launch demonstrator; the other HCLS workflows (clinical-care, pharmacovigilance, public-health, registries) follow on their own cadence. This document captures HCLS-specific commitments that the workflow seeds inherit: the bucket structure, the WG umbrella shape, the stress tests, the external-vocabulary alignment story (the four-tier NCIt-anchored hub-and-spoke), the standards landscape, the oncology overlap zone, and the composition relationships with foundations and with HCLS-only compositions.

The HCLS bucket follows the brief's commitment to keep buckets as governance and directory groupings, not class-level shared tiers. There is no `tophcls:` namespace; HCLS workflow classes compose against TOP Core directly. Cross-workflow concepts (an adverse event that crosses clinical-research and clinical-care) use Pattern B from `top-workflows-strategy.md`.

## What HCLS is

HCLS is a domain bucket. It coordinates the working groups that ship reference graphs for the operational work of medicine, clinical research, public health, and adjacent regulated life-sciences activities. The bucket is:

- A directory grouping in the repository: `hcls/clinical-research/`, `hcls/clinical-care/`, `hcls/pharmacovigilance/`, etc.
- A URI grouping: `https://top.scientix.ai/hcls/clinical-research/v1`, etc.
- A WG umbrella for cross-workflow coordination (the HCLS stewards or HCLS umbrella WG).
- A governance scope for HCLS-specific RFCs (the four-tier alignment, the oncology Pattern-C escalation, etc.).

The bucket is **not** a class-level namespace. There is no `tophcls:` prefix. HCLS workflow classes use their per-workflow prefixes (`topcr:` for clinical-research, `topcd:` for clinical-care, `toppv:` for pharmacovigilance, etc.).

## Workflows in HCLS

| Workflow extension | What it covers | Activation status |
| --- | --- | --- |
| **clinical-research** | The operational work of designing, conducting, and reporting clinical trials. Sponsor, study, site, participant, visit, investigational product, oversight body, event, finance, monitoring, quality. | Active. Launch demonstrator. v1 seed in `top-hcls-clinical-research.md`. |
| **clinical-care** | The operational work of treating patients. Patient registration, encounter, orders, clinical documentation, billing, discharge planning, care coordination, lab integration, imaging integration, medication reconciliation. | Anticipated. Ships v1 after clinical-research v1, picking up Pattern B stubs from clinical-research and graduating them to real classes. WG forms after clinical-research launches. |
| **pharmacovigilance** | The operational work of monitoring drug safety post-approval and across the lifecycle. Signal detection, risk management plans, post-market surveillance, REMS programs. | Anticipated. v1 of clinical-research includes a Pharmacovigilance functional area covering AE / SAE / SUSAR / ICSR within the trial context; pharmacovigilance graduates to its own workflow extension when scope outgrows the functional area. |
| **public-health** | The operational work of population-level intervention. Disease surveillance, outbreak investigation, vaccination programs, health-equity initiatives, social determinants. | Anticipated. Activates when a WG forms; not on the launch timeline. |
| **registries** | The operational work of running disease, device, exposure, and outcome registries. Patient enrollment, longitudinal follow-up, data quality, regulatory reporting (FDA MAUDE, state registries). | Anticipated. Activates when a WG forms. Composes against clinical-care and clinical-research for registry-based studies. |

The list is the current planning view. New HCLS workflows lift via RFC; existing workflows graduate from functional areas of other workflows when scope warrants.

## HCLS-specific stress tests

Every HCLS architecture choice has to pass two operator-grounded tests. Both are stated as the failure conditions that drive design decisions.

### Test 1: The smart-hospital-sponsoring-a-trial test

Every sponsored hospital trial uses both clinical-research and clinical-care workflows over the same Person / Organization / Site / Visit foundation. A single instance is simultaneously a Subject (research) and a Patient (care). The architecture must handle that without minting Subject-with-care-attached and Patient-with-research-attached as separate types.

Pattern B (cross-workflow `subClassOf`) is the answer. A clinical-care `Patient` and a clinical-research `Participant` are both `top:Person`. When the same Person is both, the instance carries both classifications. No specialization is forced.

The smart-hospital composition (per `top-compositions-strategy.md`) is what makes this concrete at deployment time. A smart hospital references both clinical-care and clinical-research workflows; the composition's cross-layer SHACL invariants validate that a Person who is both a Patient and a Participant has consistent context across both views.

### Test 2: The adverse-event-crossing-the-boundary test

A patient on a PARP-inhibitor oncology trial getting carboplatin as the standard-of-care backbone experiences nausea after the infusion. That nausea is simultaneously a research event (IRB-reportable, sponsor-reportable, CDISC SDTM AE domain, MedDRA-coded for FDA submission) and a care event (chart-documented, clinician-noted, ICD-10 R11.0, SNOMED 422587007).

One nausea. One nurse documenting it. Two regulatory pathways downstream. The architecture must absorb that without forcing the nurse to enter the same observation twice in different vocabularies.

Pattern B handles this directly: `topcr:AdverseEvent rdfs:subClassOf topcd:AdverseEvent, top:Observation`. The same instance carries both classifications; downstream regulatory adapters (MedDRA coding for FDA, ICD-10 coding for billing) project from the same source through SSSOM crosswalks (per the four-tier alignment below).

These tests are HCLS-specific. They become RFC checkboxes for any HCLS architecture proposal: does this proposal pass both tests, or only one, or neither?

## External vocabulary alignment: the four-tier NCIt-anchored hub-and-spoke

A clinical trial (or a clinical-care encounter, or a pharmacovigilance signal) sits at the meeting point of at least a dozen controlled vocabularies. CDISC SDTM and Protocol shape what regulators expect. MedDRA codes every adverse event the FDA reads. SNOMED CT and ICD-10 carry the conditions clinicians put in the chart. RxNorm names US drug products. LOINC names labs and observations. HGNC names genes when biomarkers enter the trial. FDA UNII names active ingredients. SPL is the structured product label. ICSR is the schema safety reports serialize into. mCode is the FHIR-aligned oncology dataset. ICH-GCP is the conduct framework. USDM and DDF are CDISC's emerging unified study definition and digital data flow standards.

Authoring bilateral crosswalks between every pair of vocabularies is the N×N maintenance failure mode. HCLS workflows do not author them. Instead, the architecture uses **NCIt as the SKOS alignment hub** and composes the rest through it.

### The architectural insight

Three NCI infrastructures resolve this when taken together:

1. **NCI EVS publishes CDISC, FDA, ICH, mCode, HL7 UCUM, the FDA-NIH Modernizing Research and Evidence Glossary, and other regulated-industry vocabularies as curated subsets of the NCI Thesaurus.** A clinical-research class that anchors to an NCIt concept inherits subset membership in every subset that concept belongs to. CDISC alignment, ICH alignment, FDA alignment, mCode alignment all come at no incremental cost. The subset query is one REST call against the EVS API.

2. **NCI EVS publishes the FDA-side terminology** (UNII for ingredients, SPL for labels, GUDID for devices, ICSR for safety reports, PQCMC for quality, NDF-RT for drug classes, the Problem List subset) in a separate FTP directory. These are not part of the NCIt graph proper; they attach to HCLS workflow classes as typed identifier properties or reference schemas.

3. **NCI EVS publishes eighteen mapsets through its REST API** that bridge NCIt to vocabularies outside the NCIt graph: NCIt to MedDRA, NCIt to ICD10CM, NCIt to ICD10, NCIt to ChEBI, NCIt to HGNC, NCIt to SwissProt, NCIt to GDC, NCIt to ICDO3 (three variants), plus SNOMEDCT_US to ICD10CM and a handful of other internal bridges. Every mapset has NCIt at one end. The pattern is hub-and-spoke with NCIt as the hub.

The architectural commitment for HCLS: **anchor HCLS workflow classes to NCIt concepts via `skos:exactMatch` / `skos:closeMatch`, and the rest of the vocabulary stack composes through that one anchor.**

### Tier 1: NCIt as the SKOS alignment hub

Every HCLS workflow class that has an NCIt peer declares it in the workflow's SKOS taxonomy file. Same pattern as the schema.org alignment in ADR-0016.

```turtle
@prefix topcr: <https://top.scientix.ai/hcls/clinical-research/v1#> .
@prefix ncit: <http://purl.obolibrary.org/obo/NCIT_> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

topcr:AdverseEvent
    rdfs:subClassOf top:Observation, topcd:AdverseEvent ;   # Pattern B applied
    skos:exactMatch ncit:C41331 ;                            # NCIt anchor
    skos:prefLabel "Adverse Event"@en .
```

One anchor. Everything downstream composes through it.

### Tier 2: Inherited subset membership

HCLS workflows formally adopt a NCIt subset whitelist as their alignment target set. The clinical-research whitelist is the starting point; other HCLS workflows inherit and refine.

| Subset | NCIt code | Why |
| --- | --- | --- |
| CDISC | C61410 | SDTM, SEND, ADaM, CDASH, Glossary, Protocol, all in one subtree |
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

Whitelist additions or removals route through HCLS-bucket RFC, because they affect what downstream consumers can rely on.

### Tier 3: External crosswalks via EVS REST mapsets, carried as SSSOM artifacts

For vocabularies outside the NCIt graph (MedDRA, SNOMED CT, ICD-10, HGNC, ChEBI, etc.), HCLS workflows consume the EVS REST mapsets as the bridge. The mapsets become SSSOM-formatted TSV files (the Simple Standard for Sharing Ontological Mappings, named in TOP's roadmap as the carrier format and operationalized per ADR-0018).

```
hcls/clinical-research/v1/crosswalks/
├── ncit-to-meddra.sssom.tsv          (NCIt 26.04d to MedDRA, refreshed quarterly)
├── ncit-to-icd10cm.sssom.tsv          (NCIt 26.04d to ICD-10-CM)
├── ncit-to-chebi.sssom.tsv            (NCIt to ChEBI, Aug 2024)
├── ncit-to-hgnc.sssom.tsv             (NCIt to HGNC, Apr 2026)
├── ncit-to-swissprot.sssom.tsv        (NCIt to UniProt, Apr 2026)
├── ncit-to-gdc.sssom.tsv              (NCIt to Genomic Data Commons)
├── snomedct-to-icd10cm.sssom.tsv      (SNOMED CT to ICD-10-CM, Sep 2025)
└── icd10-to-meddra.sssom.tsv          (ICD-10 to MedDRA, Jul 2023)
```

Each mapping file is mirrored from the EVS REST API at a pinned version, with version and refresh date in the SSSOM metadata block. Mapset upgrades land as PRs; downstream consumers can audit what's in play and when it changed.

Other HCLS workflows (clinical-care, pharmacovigilance, registries) consume the same Tier-3 crosswalks. The crosswalk files are shared across workflows in the HCLS bucket; per-workflow versions are not needed unless a workflow has specific extensions.

### Tier 4: FDA EVS regulated-product directory

Vocabularies in the FDA FTP directory that are not part of the NCIt graph attach as typed identifier properties or reference schemas, not as class-level alignment.

| FDA artifact | Attaches to (clinical-research example) | Mechanism |
| --- | --- | --- |
| UNII | `topcr:InvestigationalProduct`, `topcr:DrugSubstance`, `topcr:Comparator` | Active-ingredient identifier property |
| SPL | `topcr:InvestigatorsBrochure`, `topcr:PackageInsert` | Source-document reference for marketed-product IBs |
| GUDID | `topcr:InvestigationalDevice` | Device identifier property |
| ICSR | `topcr:SAEReportForm`, `topcr:INDSafetyReport` | Schema for regulator-facing serialization |
| NDF-RT | `topcr:ConcomitantMedication` | Drug-class taxonomy reference (older but still cleanest) |

These are properties on HCLS workflow entities, not SKOS class alignments. Other HCLS workflows attach the same FDA artifacts at their relevant classes (clinical-care attaches GUDID at its `Device` class; pharmacovigilance attaches ICSR at its `SafetyReport` class; etc.).

### USDM and DDF specifically

CDISC's Unified Study Definitions Model (USDM) and Digital Data Flow (DDF) are the protocol-design-side and data-design-side of an emerging open standards stack. USDM defines a study at the protocol level (schedule of activities, eligibility criteria, endpoints, study arms). DDF defines how protocol metadata flows into downstream operational systems.

Both are NCIt-published as part of the CDISC subset (NCIt code C61410). HCLS workflow classes in study-design and data-management functional areas anchor to USDM and DDF concepts directly via Tier 1. The architectural pattern is the same; USDM and DDF are first-class citizens of the CDISC subset, alignable through the same Tier-1 anchor.

Worth calling out because USDM and DDF are where regulatory expectations are moving over the next three to five years. HCLS workflow extensions that anchor cleanly to them at launch are positioned for the regulatory direction, not against it.

## The oncology overlap zone

Oncology is the densest cross-workflow zone in HCLS. Standard-of-care oncology infusions delivered as part of trial protocols, AEs that cross research and care, biomarker measurements that span clinical-research, clinical-care, and registries, RECIST assessments that span multiple modalities. The overlap density is real, not theoretical.

The general HCLS Pattern B (`top-workflows-strategy.md`) handles most of this. For dense overlap zones where the cross-workflow declarations accumulate (rough threshold: more than a dozen oncology-specific cross-workflow declarations with operator-grounded justifications that share a common shape), the **scoped Pattern-C escalation path** in `top-workflows-strategy.md` becomes available.

For oncology specifically: an `oncology-shared/` tier (within HCLS) holds the oncology-specific concepts both clinical-research and clinical-care need (TumorMeasurement, ChemotherapyRegimen, RECIST assessment, etc.). The general clinical-research / clinical-care boundary stays at Pattern B; only oncology lifts to scoped Pattern C.

This is the failure-mode-aware fallback. It keeps Core small while admitting that one HCLS sub-domain may need its own scoped shared layer. Other HCLS sub-domains (cardiology, pulmonology, rare disease, mental health) follow the same promotion path if and when they accumulate similar pressure. The decision is RFC-gated at the HCLS umbrella level.

## Composition relationships

HCLS workflow extensions feed multiple compositions in the compositions namespace (per `top-compositions-strategy.md`):

| Composition | HCLS workflows referenced | Foundations workflows referenced | Notes |
| --- | --- | --- | --- |
| `compositions/smart-hospital/` | clinical-care + (at AMCs) clinical-research | physical-AI + operational | Reference smart-X composition. |
| `compositions/smart-clinic/` | clinical-care | physical-AI + operational | Smaller-scope sibling. |
| `compositions/smart-lab/` | clinical-research (or lab-ops workflow TBD) | physical-AI + operational | Lifts when lab-ops scope is settled. |
| `compositions/dct/` (decentralized clinical trial) | clinical-research + clinical-care | None directly | Composes HCLS workflows in a pattern that crosses traditional site boundaries. |
| `compositions/vbc/` (value-based care program) | clinical-care | operational | Plus financial-services and analytics from other buckets. |
| `compositions/registry-based-study/` | registries + clinical-research + sometimes clinical-care | None directly | Real-world evidence studies. |
| `compositions/specialty-pharmacy-network/` | clinical-care | operational | Plus supply-chain and financial-services from other buckets. |

The compositions reference HCLS workflow classes; HCLS workflow extensions do not reference compositions. The dependency direction is fixed.

## HCLS WG umbrella structure

| Property | Calibration |
| --- | --- |
| Umbrella WG | HCLS umbrella WG (or "HCLS stewards") coordinates across the per-workflow WGs. Bo holds the umbrella BDFL role until co-stewards are named. |
| Per-workflow WGs | clinical-research, clinical-care, pharmacovigilance (when graduated), public-health, registries each have their own WG. |
| Cross-workflow RFC review | HCLS umbrella WG reviews cross-workflow `subClassOf` PRs (Pattern B declarations between sibling HCLS workflows) and the four-tier alignment governance (subset whitelist changes, mapset version pinning). |
| Per-workflow PR review | Per-workflow WGs review additions within their workflow (functional-area-level changes). |
| Composition coordination | Each composition WG (smart-hospital, DCT, VBC, etc.) coordinates with the relevant HCLS workflow WGs; the HCLS umbrella has visibility into composition-level RFCs that affect HCLS workflows. |
| Standards-body interactions | HCLS umbrella holds interactions with NCI EVS, CDISC, HL7, FDA, ICH at the project level. Per-workflow WGs interact with the specific standards bodies relevant to their workflow (clinical-research with CDISC, clinical-care with HL7, etc.). |

The umbrella is governance, not architecture. It does not own classes.

## What this strategy commits the HCLS bucket to

- **HCLS is a domain bucket, not a class-level shared tier.** No `tophcls:` namespace; per-workflow prefixes (`topcr:`, `topcd:`, `toppv:`, etc.) only.
- **The four-tier NCIt-anchored hub-and-spoke is the HCLS alignment story.** Tier 1 (SKOS anchoring), Tier 2 (inherited subset membership), Tier 3 (SSSOM crosswalks from EVS REST mapsets), Tier 4 (FDA EVS for UNII, SPL, GUDID, ICSR, NDF-RT).
- **The smart-hospital-sponsoring-a-trial test and the AE-boundary-test are HCLS-specific RFC gates.** Every HCLS architecture proposal passes both.
- **Pattern B (per `top-workflows-strategy.md`) handles cross-workflow concepts.** Pattern C scoped to oncology (or other dense sub-domain) is the escalation path; not adopted by default.
- **Clinical-research is the launch demonstrator.** Other HCLS workflows lift on their own cadence; clinical-care v1 follows directly, with stubs graduating from clinical-research v1 Pattern B declarations.
- **NCIt subset whitelist (10 subsets initially) is HCLS-bucket-governed.** Changes route through HCLS umbrella RFC.
- **EVS REST mapset versions pinned in v1; upgrades land via PR.** SSSOM metadata blocks carry version and refresh date.
- **USDM and DDF alignment via Tier 1.** Not special cases; first-class citizens of the CDISC subset.
- **Strategy ratifies as ADR-0022 (HCLS bucket strategy and NCIt-anchored alignment)** when the HCLS umbrella WG forms. ADR number is a strawman.

## What this strategy does NOT do

- It does not author any class catalog. Each HCLS workflow's class catalog ships in its own seed.
- It does not finalize the per-workflow prefixes. `topcr:`, `topcd:`, `toppv:`, etc. are strawmen; WGs ratify or override.
- It does not commit any non-clinical-research HCLS workflow to a ship date. Each WG forms on its own timeline.
- It does not specify FHIR R5 alignment. FHIR is class-shape, not just terminology; needs its own follow-on RFC.
- It does not specify RxNorm and LOINC handling. Neither is in EVS REST mapsets; access requires UMLS dependency. Follow-on RFC.
- It does not specify Bioregistry registration timing. WG decides.
- It does not promote any HCLS concept to TOP Core. Core changes route through Core-stewards RFC, not HCLS.

## Open questions for HCLS umbrella WG resolution

1. **HCLS umbrella WG composition.** When does the umbrella form? Who are the founding stewards? Bo holds the role until co-stewards are named.
2. **Per-workflow prefixes.** `topcr:`, `topcd:`, `toppv:`, etc. are strawmen. WG ratifies or overrides.
3. **NCIt subset whitelist governance.** Initial 10 subsets named. Additions and removals route through HCLS umbrella RFC. Threshold for what triggers a new subset addition.
4. **Mapset refresh cadence.** Strawman: PR-per-upgrade. Alternatives: scheduled cadence (quarterly), automatic-with-validation. WG decides.
5. **RxNorm and LOINC handling.** Neither is in EVS REST mapsets. Follow-on RFC. WG decides whether to take a UMLS dependency or seek an alternative access path.
6. **FHIR R5 alignment.** FHIR is class-shape, not just terminology. Follow-on RFC. WG decides on the model.
7. **Bioregistry registration timing.** WG decides whether to register the `topcr:`, `topcd:`, etc. prefixes and NCIt alignment with Bioregistry at HCLS launch, before, or after.
8. **Oncology Pattern-C threshold.** Strawman: more than a dozen oncology-specific cross-workflow declarations. WG sharpens or replaces.
9. **Pharmacovigilance graduation timing.** Pharmacovigilance starts as a functional area of clinical-research v1. Graduates to its own workflow extension when scope warrants. WG names the threshold.
10. **Public-health and registries activation.** When do these workflows form WGs? Driven by adopter demand.
11. **Stub-class governance for clinical-care during clinical-research v1.** Clinical-care stubs that clinical-research v1's Pattern B declarations point to live in `hcls/clinical-care/v1/`. WG decides who reviews stub additions until clinical-care's WG activates.

## Pointers

- Strategy brief: `top-strategy-brief.md`
- Workflows strategy: `top-workflows-strategy.md`
- Foundations bucket strategy: `top-foundations-strategy.md`
- Compositions strategy: `top-compositions-strategy.md`
- Clinical-research seed: `top-hcls-clinical-research.md`
- NCI EVS:
  - Subsets: `https://evsexplore.semantics.cancer.gov/evsexplore/subsets/ncit`
  - Mappings: `https://evsexplore.semantics.cancer.gov/evsexplore/mappings`
  - CDISC FTP: `https://evs.nci.nih.gov/ftp1/CDISC/`
  - FDA FTP: `https://evs.nci.nih.gov/ftp1/FDA/`
  - REST API: `https://api-evsrest.nci.nih.gov/api/v1/`
- SSSOM: `https://mapping-commons.github.io/sssom/`
- Bioregistry: `https://bioregistry.io/`
- TOP Core: `core/v1/`, `taxonomy/taxonomy.ttl`
- Working groups: `governance/working-groups.md`

---

*HCLS bucket strategy v1. The substance of this strategy becomes the basis for ADR-0022 (HCLS bucket strategy and NCIt-anchored alignment) when the HCLS umbrella WG forms. ADR number is a strawman.*
