# CDISC ecosystem alignment — COSMoS, USDM, SDTMIG, CDISC Library (working draft)

> Working document. Surveys the CDISC ontology / structured-metadata stack to determine which CDISC artifacts TOP should ingest, reference, or align with — and surfaces one architectural question (LinkML adoption) that warrants deliberate decision-making.
> Last touched 2026-05-09.

## Purpose

Triggered by digging into [`cdisc-org/COSMoS`](https://github.com/cdisc-org/COSMoS). Bo's exploring CDISC's ontology-adjacent work; this note captures what's there, what touches TOP, and what doesn't. Output: a small set of actionable touch-points and one architectural question.

Adjacent to the [USDM ingest audit](usdm-ingest-audit.md) — that note covers USDM specifically; this note covers the broader CDISC structured-metadata stack so TOP's ingest story is grounded across the full ecosystem.

## The CDISC structured-metadata stack (as observed)

```
┌──────────────────────────────────────────────────────────────────┐
│ CDISC Library (API + portal)                                     │
│ ├── Controlled Terminology (NCIt-backed C-codes for everything)  │
│ ├── SDTM Implementation Guide (SDTMIG) — DM, DS, AE, VS, EX,     │
│ │     IE, EC, MH, CM, etc. domain definitions                    │
│ ├── CDASH Implementation Guide — acquisition-side equivalents    │
│ ├── ADaM Implementation Guide — analysis-ready datasets          │
│ ├── SEND Implementation Guide — non-clinical                     │
│ └── Therapeutic Area User Guides (TAUGs)                         │
└──────────────────────────────────────────────────────────────────┘
                          ↑                ↑
                          │                │
            ┌─────────────┴────┐  ┌────────┴──────────────┐
            │ USDM (study     │  │ COSMoS (BC catalog +   │
            │ definition,     │  │ per-instrument Dataset │
            │ M11-aligned)    │  │ Specializations)       │
            │                 │  │                         │
            │ Pydantic models │  │ LinkML schemas (BC,    │
            │ (auto-gen)      │  │ CRF, SDTM)             │
            │                 │  │ YAML BC definitions    │
            │ JSON exports    │  │ JSON / SVG / Markdown  │
            └─────────────────┘  └─────────────────────────┘
```

## What COSMoS is

CDISC **Conceptual and Operational Standards Metadata Services**. Verified contents:

- **`model/cosmos_bc_model.yaml`** — LinkML schema for BiomedicalConcept (root class with conceptId, ncitCode, shortName, definition, categories, resultScales, coding, dataElementConcepts).
- **`model/cosmos_sdtm_model.yaml`** — LinkML schema for SDTM Dataset Specialization (root class SDTMGroup, with datasetSpecializationId, domain, biomedicalConceptId FK, variables[] of SDTMVariable).
- **`model/cosmos_crf_model.yaml`** — LinkML schema for CRF specializations.
- **`yaml/`** — versioned releases (latest visible: `20260630_r17/sdtm`) of YAML files. The SDTM folder contents are per-instrument specializations (EQ-5D-5L `sdtm_eq5d020[1-6].yaml`, Six-Minute Walk Test `sdtm_sixmw10[1-6].yaml`), NOT the canonical SDTM domain definitions.
- **`export/`** — Excel and CSV exports of the latest BCs and SDTM Dataset Specializations.
- **`bc_starter_package/`** — utilities for creating new BCs.
- **`openapi/`** — API definition.

## What COSMoS is NOT

- **Not the controlled-terminology source.** The C-codes (C99077, C66737, C174268, etc.) used throughout USDM and COSMoS come from the **CDISC Library's Controlled Terminology** publication (NCIt-backed). COSMoS *references* C-codes but doesn't *publish* them.
- **Not the SDTM domain definitions.** DM (Demographics), DS (Disposition), AE (Adverse Events), VS (Vital Signs), EX (Exposure), IE (Inclusion/Exclusion), MH (Medical History), CM (Concomitant Medications), etc. — these standard SDTM domains are defined in the **SDTMIG** (Implementation Guide). COSMoS's SDTM specializations are *per-assessment-instrument projections* (e.g., "when an EQ-5D-5L instrument is used, exactly how do those values populate SDTM QS variables").
- **Not LOINC/SNOMED-direct.** COSMoS BCs reference NCIt as primary terminology; cross-references to LOINC/SNOMED appear via the `coding` slot.

This split matters because the audit's claim that "TOP Participant projects to SDTM DM" depends on **SDTMIG**, not COSMoS, for the canonical DM column list. COSMoS's SDTM specializations are downstream of SDTMIG.

## Three places COSMoS touches TOP

### Touch-point 1 — BiomedicalConcept catalog

USDM `BiomedicalConcept` (in `StudyVersion.biomedicalConcepts[]`) is the model; COSMoS publishes the *catalog* of BCs in machine-readable form (LinkML YAML). Activities in USDM reference biomedicalConceptIds — and the canonical resolution is to a COSMoS-published BC.

**Implication for TOP**: when TOP lifts **Activity** (post-Participant, post-Visit), each Activity points at a BiomedicalConcept. The BC catalog is COSMoS. TOP doesn't need to model BCs internally — TOP Activity carries `bcRef → COSMoS BC URI` (e.g., NCIt C-code or COSMoS conceptId), and the consuming system dereferences against the COSMoS catalog.

**Action when Activity lifts**: TOP Activity model includes a `biomedicalConceptCode` field (NCIt C-code) and a `biomedicalConceptUri` field (resolves into COSMoS / NCIt). Document the COSMoS-as-canonical-BC-source convention then.

### Touch-point 2 — Per-instrument SDTM Dataset Specializations

When a study uses a standard instrument (EQ-5D, 6MWT, ADAS-Cog, etc.), the operational data captured at runtime needs to project to SDTM in a specific way. COSMoS publishes the projection rules per-instrument as Dataset Specializations.

**Implication for TOP**: TOP doesn't need to model these specializations directly. When TOP exports operational data to SDTM, the projection logic for instruments-with-COSMoS-specializations should defer to the COSMoS spec. For instruments without a COSMoS specialization, TOP's deployment falls back to a sponsor-defined mapping.

**Action**: defer until TOP has a runtime data export pipeline (post-Visit, post-Activity, post-Observation lift). Document the convention now in the audit.

### Touch-point 3 — LinkML as the schema language (architectural question)

COSMoS publishes its schemas in **LinkML** (the YAML-based schema language). LinkML natively generates:
- JSON-LD context files
- JSON Schema
- OWL / Turtle
- SHACL
- Pydantic / Python classes
- GraphQL
- SQL DDL

LinkML is becoming the convergence point for life-sciences structured-metadata (NIH, HL7 FHIR's adjacent work, CDISC, OBO Foundry tooling). USDM doesn't publish LinkML directly but its Pydantic models could be LinkML-generated; COSMoS does.

**Implication for TOP**: TOP currently uses a hand-rolled `top-strawman.json` source intermediate, with `tools/build_shacl.py` generating SHACL. **If TOP migrated its source intermediate to LinkML**, we'd get JSON-LD context, JSON Schema, OWL, SHACL, and Pydantic-for-the-broker for free, plus interoperability with the CDISC tooling.

This is an architectural decision, not a quick win. It's worth a deliberate evaluation; not appropriate to slip into a sub-task of the ingester build.

## Broader CDISC stack touch-points (beyond COSMoS)

For completeness, since the question is about CDISC ecosystem alignment:

### CDISC Library — controlled terminology

The C-codes everywhere in USDM (`StudyArm.type.code = "C174268"` for "Placebo Control Arm") come from CDISC CT, NCIt-backed. The Library publishes CT in multiple formats: ODM XML, Excel, RDF/Turtle, NCIt OWL.

**Implication for TOP**: TOP's Code→enum mapping table (audit Gap 3) is a subset of the CDISC CT export. Two paths:
- **A**: TOP maintains the mapping table by hand (current intent). Updates lag CDISC releases.
- **B**: TOP imports a slice of CDISC CT relevant to the locked-8-top-levels at build time. Updates auto-track CDISC releases.

Path B is much more powerful but requires either CDISC Library API access (free for registered) or pulling from the public RDF distribution.

### SDTMIG — SDTM domain definitions

DM, DS, AE, VS, EX, IE, EC, MH, CM, etc. are defined in SDTMIG. The Implementation Guide is published as PDF + structured artifacts (XML, Excel). The structured CDISC Library export covers SDTMIG variables with their controlled terminology.

**Implication for TOP**: TOP's per-Participant SDTM cross-walks (in the Participant planning note) are claims that need SDTMIG validation. The Participant→DM column mapping I wrote (USUBJID, SUBJID, SEX, RACE, etc.) is correct against SDTMIG, but the *exact* expected values, formats, and controlled terminology come from CDISC Library SDTM CT.

**Action**: when TOP starts emitting SDTM-shaped exports (deployment-side, not in TOP), the export logic dereferences SDTMIG specs from CDISC Library.

### CDASH — acquisition-side equivalents

Same pattern — CDASH IG defines the CRF-level acquisition variables. CDASH is upstream of SDTM (data captured in CDASH form gets transformed to SDTM submission form).

**Implication for TOP**: TOP doesn't need to model CDASH internally; CDASH is a projection target, like SDTM. The TOP Activity / Visit / Observation entities (when they lift) project to CDASH at acquisition and SDTM at submission.

### ADaM — analysis-ready datasets

ADaM IG defines analysis-ready dataset structures (ADSL, ADAE, ADTTE, etc.). Downstream of SDTM. Not directly relevant to TOP's operator-grounded foundation; ADaM lives in the analysis layer.

**Implication for TOP**: out of scope for the foundation; relevant only when TOP-deployed analysis pipelines emerge.

### SEND — non-clinical (preclinical)

Standard for non-clinical study tabulation. Out of scope for TOP clinical-trials reference graph; would matter for a TOP non-clinical reference graph if that ever lifts.

## Open architectural question — LinkML for TOP

The big question this survey surfaces:

**Should TOP migrate its source intermediate from `top-strawman.json` to LinkML?**

### What we'd gain

1. **Free generators**: JSON-LD context (the NGSI-LD foundation), JSON Schema (broker validation), OWL/Turtle (exports), SHACL (replaces `tools/build_shacl.py`), Pydantic (broker code generation), GraphQL.
2. **CDISC interop**: speak the same schema language as COSMoS / future-USDM. When TOP ingests a USDM document, the ingester can leverage shared LinkML tooling. When TOP imports a COSMoS BC, it's natively compatible.
3. **OBO Foundry / NIH alignment**: LinkML is the schema language for the NIH Common Data Elements project, the OBO Foundry's Data Standards work, and several HL7 FHIR adjacent efforts. TOP becomes part of an established ecosystem rather than an island.
4. **Cleaner versioning**: LinkML has explicit schema-evolution patterns (slot deprecation, class renames, migration paths).

### What we'd give up / pay

1. **Migration cost**: rewrite `top-strawman.json` (Sponsor + Site + StudySite + Study + 9 horizontals + future Participant) as LinkML. Non-trivial. ~1-2 weeks if done right.
2. **Coupling**: TOP becomes dependent on LinkML toolchain (`linkml`, `linkml-runtime`). Stable but adds a dependency.
3. **Loss of authorial control**: current source intermediate has TOP-specific patterns (NGSI-LD validFrom/validUntil, ngsi-ld:URI types, three-axis system pattern annotations) that need LinkML expressivity audit. If LinkML can't carry our patterns cleanly, we'd be carrying schemas in two places.
4. **Toolchain maturity in the NGSI-LD ecosystem**: LinkML can emit JSON-LD context, but NGSI-LD-specific patterns (Property/Relationship/GeoProperty native types, broker-level attribute structures) may need custom emitters.

### My read

Don't migrate now. The current `top-strawman.json` works, `build_shacl.py` works, and the spec discipline is paying off. **But** schedule a deliberate LinkML evaluation as a v0.5 or v0.6 architectural review. Specifically: prototype emitting the current Sponsor source-intermediate as LinkML and see whether the generated JSON-LD context, OWL, and SHACL are equivalent to (or better than) what we have. If yes, plan a migration; if no, document why we stay custom.

This is exactly the kind of decision Bo would want to make deliberately, not slip into.

## Recommended actions

1. **Note touch-points in source intermediate** — when TOP lifts Activity (post-Participant, post-Visit), include `biomedicalConceptCode` (NCIt C-code) and document COSMoS as the canonical BC catalog. (Future PR.)
2. **Document CDISC Library CT path for the Code→enum mapping (audit Gap 3)** — currently the audit recommends a side `ingester-mappings.md`. Add a note that the mapping should derive from CDISC Library CT exports, not be hand-curated. (Update to PR #4 audit.)
3. **Schedule LinkML evaluation as v0.5 milestone** — Bo's call. If yes, the evaluation lifts as a planning note then; if no, document the decision to stay custom.
4. **Don't model BiomedicalConcept inside TOP** — defer to COSMoS. TOP carries the *reference* (NCIt code or COSMoS conceptId), not the definition.
5. **Don't try to ingest COSMoS specializations directly now** — those are runtime / submission concerns, not foundation concerns.

## Open questions for Bo

1. **LinkML evaluation**: schedule for v0.5 milestone? Or punt indefinitely until USDM ingester is operational and we've actually seen the toolchain pain?
2. **CDISC Library access**: do we want TOP to depend on CDISC Library API (free with registration) for fresh CT exports? Or maintain a static mapping table?
3. **COSMoS BC reference convention**: when Activity lifts, do we use NCIt C-codes (e.g., `C25208` for Heart Rate) or COSMoS conceptIds, or both?
4. **Per-instrument SDTM specializations**: relevant only to deployment-side export pipelines; TOP stays clean. Confirm the boundary?

## Pointers

- [`usdm-ingest-audit.md`](usdm-ingest-audit.md) — Study-level USDM ingest audit; this note's parent context.
- [`participant-planning.md`](participant-planning.md) — Participant cross-walks (FHIR / SDTM / CDASH / USDM).
- [COSMoS](https://github.com/cdisc-org/COSMoS) — surveyed for this note.
- [LinkML](https://linkml.io/) — schema language COSMoS uses; raises TOP architectural question.
- [CDISC Library](https://www.cdisc.org/cdisc-library) — Controlled Terminology, SDTMIG, CDASH IG, ADaM IG.
- [NCIt EVS](https://evs.nci.nih.gov/) — terminology backbone for CDISC C-codes.
- [USDM v4 source](https://github.com/cdisc-org/usdm/tree/main/src/usdm_model) — verified against this in the parent audit.
