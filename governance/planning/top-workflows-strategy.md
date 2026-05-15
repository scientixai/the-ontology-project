# TOP Workflow Extensions Strategy

*Status: pre-RFC strategic planning. Author: Bo Lora (BDFL, sole signatory to The Ontology Project as of 2026-05-14). Audience: every working group authoring or planning a workflow extension across every bucket (HCLS, foundations, manufacturing, supply chain, energy, financial services, future).*

*Companion to TOP Core (`core/v1/`), to `top-strategy-brief.md` (the architectural umbrella), and to per-bucket strategy documents (`top-hcls-strategy.md`, `top-foundations-strategy.md`, future). Pre-RFC; the formal RFC process starts when the relevant working groups do.*

---

## Why this document exists

Workflow extensions are the third organizational layer above TOP Core. They are the reference graphs for specific operational work categories: clinical research, care delivery, physical-AI infrastructure, operational management, pharma CMC manufacturing, retail banking, grid operations. Each workflow extension is its own reference graph with its own working group, its own class catalog, its own SHACL shapes, its own NCIt or peer-vocabulary alignment.

This document captures the cross-bucket discipline for workflow extensions: how they decompose, how they compose against Core, how they relate to sibling workflow extensions, what calibration their internal structure follows. Per-bucket strategies (HCLS, foundations, manufacturing, etc.) inherit this discipline; bucket-specific decisions live in the per-bucket documents.

## The four-axis decomposition discipline

Real-world deployments cut across at least four axes. Naming each one and committing to which becomes a workflow extension is the single most consequential architectural choice in TOP after the eight Core categories themselves.

| Axis | What it is | How TOP handles it |
| --- | --- | --- |
| **Work category** | What kind of operational work. Clinical research, care delivery, manufacturing, building operations, financial clearing. | **Workflow extensions.** This is the only axis that becomes a workflow extension. |
| **Setting / place type** | Hospital, clinic, lab, home, mobile unit, pharmacy, infusion center, manufacturing facility, distribution center, retail outlet, vessel, field site. | **Instance-level property** on `top:Physical` (and its specializations). Operator-facing enum at the CV layer, optionally promoted to a SKOS hierarchy referencing NCIt's facility-type subset or its peers where applicable. |
| **Layer within a setting** | Physical infrastructure, operational management, the operational work itself. A hospital has all three; a manufacturing plant has all three; a smart office has the first two. | **Workflow-extension composition.** Each layer is its own workflow extension. A real deployment composes the relevant ones at the composition layer. Not a new axis. |
| **Therapeutic area / sector specialty** | Oncology, cardiology, rare disease, mental health, pediatrics in HCLS. Subsea vs onshore in energy. Discrete vs process in manufacturing. Retail vs commercial vs institutional in financial services. | **Instance-level property** on the relevant workflow class. Operator-facing enum at the CV layer, mapped to NCIt or other domain hub at the SKOS layer. Not a workflow-extension axis. |

The discipline is: **only the work axis branches the tree.** Everything else attaches as a property of instances, with SKOS hierarchies at the CV layer for the categorical structure operators recognize.

This is what keeps a clinical-research `Study` and a clinical-care `Encounter` and a pharmacovigilance `SignalDetection` from each minting "oncology" classes. Oncology is a property both reference. The Study has `therapeuticArea=oncology`. The Encounter has `therapeuticArea=oncology`. The shared meaning lives at the CV layer (a SKOS concept scheme of therapeutic areas anchored to NCIt's Disease subset), not in a workflow-extension axis.

Same for setting. A clinical-research `Site` is a `top:Physical` with `settingType=academic-medical-center`. A clinical-care `Site` is a `top:Physical` with `settingType=community-hospital` or `outpatient-clinic`. The hospital-ness, the clinic-ness, the academic-ness all live at the CV layer as a SKOS hierarchy of facility types. No "hospital" workflow extension exists, because hospital is a kind of place, not a kind of work.

## Pattern B: cross-workflow `subClassOf`

Sibling workflow extensions sometimes share concepts. The discipline for handling cross-workflow concepts is **Pattern B**: a workflow class can declare `rdfs:subClassOf` against a class in a sibling workflow extension when the concept genuinely crosses both workflows' operator semantics.

The test is operator-grounded, not engineering-grounded. A nausea adverse event in an oncology trial is both a research event (sponsor-reportable, MedDRA-coded) and a care event (chart-noted, ICD-10 coded). Same nausea, one nurse documenting it, two regulatory pathways downstream. That concept genuinely crosses: `topcr:AdverseEvent rdfs:subClassOf topcd:AdverseEvent, top:Observation`. The cross-workflow declaration carries an operator-grounded justification.

A clinical-research `Sponsor` does not pass the test: Sponsor is not a care-delivery concept. Stays in clinical-research only.

The discipline keeps the cross-workflow surface small. Most workflow classes do not cross into sibling workflows; only the dense overlap (clinical interventions, AEs, visits, procedures, samples in HCLS; pharma supply Lots crossing into manufacturing Batches; etc.) does.

Each cross-workflow `subClassOf` declaration is documented in the dependent workflow's spec page with a one-line operator-grounded justification. A PR adding a new cross-workflow declaration trips a review checkbox: "this concept genuinely crosses both workflows' operator semantics, as evidenced by..."

### Alternatives considered

| Pattern | What it does | Why not |
| --- | --- | --- |
| **A. Flat sibling, instance composition only.** | Both workflows under their buckets. A Person can hold both classifications at the instance level; no class-level relationship. | Technically sufficient, but pushes the burden of knowing which workflow owns each shared concept into operator memory and into custom adapters. Fails the human-down posture from first-principles.md § 1. |
| **C. Intermediate shared tier between Core and workflows.** | A namespace (`tophcls:` for HCLS, `topfound:` for foundations, etc.) between Core and individual workflows holds concepts both workflows in the bucket need. Each workflow specializes from Core and from the shared tier. | Governance overhead is the killer. Every new class triggers a debate: does this belong in Core, in the shared tier, or in the workflow? The debate is not always resolvable on principle; defending the boundary becomes permanent project work. Recreates the FHIR / HL7 mistake at a smaller scale. |
| **D. Promote shared concepts back to Core.** | Cross-workflow concepts (Treatment, MedicationAdministration, Procedure) become Core leaves. | Breaks ADR-0013 (practitioner-first). Promoting workflow-specific concepts to Core dilutes Core by absorbing things that aren't truly universal across every TOP workflow. Core stops being small. |

Pattern B is the choice. The alternatives stay documented as the reasoning others can audit.

### Pattern C as the escalation path for dense overlap zones

Pattern C is not adopted across the board, but it remains available as a scoped escalation path for dense overlap zones within a single bucket. The canonical case is oncology in HCLS: cross-workflow `subClassOf` declarations between clinical-research and clinical-care may accumulate enough oncology-specific weight (rough threshold: more than a dozen declarations specific to oncology, with operator-grounded justifications that share a common shape) that an `oncology-shared/` tier scoped specifically to oncology (not to all of HCLS) becomes warranted.

The escalation path is RFC-gated. Other dense overlap zones (cardiology, pulmonology, etc.) follow the same pattern if and when they accumulate similar pressure. Cross-bucket overlap (e.g., pharma manufacturing CMC overlapping with HCLS clinical-supply) likewise has Pattern-C-scoped escalation available if it accumulates.

## Cross-bucket Pattern B

The pattern extends across buckets, not just within them. A pharma manufacturing CMC class declaring `rdfs:subClassOf` against an HCLS clinical-supply class is the same shape as the within-HCLS Pattern B. Cross-bucket declarations require the same operator-grounded test and the same justification documentation.

A composition that references workflow extensions from multiple buckets (a smart-hospital references both HCLS workflows and foundations workflows) is not Pattern B; it's a composition. See `top-compositions-strategy.md`.

## The functional-areas calibration

Every workflow extension decomposes into functional areas at a consistent granularity. The clinical-research seed names twelve (Study Design, Regulatory Affairs, Finance, Setup, Site Management, Clinical Supply, Recruitment, Intervention, Pharmacovigilance, Data Management, Monitoring, Quality Management). That number and that shape are deliberate, and they are the right pattern for every workflow extension TOP adopts.

The discipline:

| Property | Calibration |
| --- | --- |
| Number of functional areas per workflow extension | 8 to 15 |
| Classes per functional area | 5 to 30 |
| Operator-vocabulary recognizability | Each functional area maps to a department, function, or operational responsibility a practitioner in the domain would name without prompting |
| Stewardship | One or two WG maintainers per functional area, ideally; one SHACL shapes file per functional area |
| Spec doc structure | Each functional area gets a section in the workflow extension's spec page with its classes, properties, NCIt anchors (or peer-vocabulary anchors), cross-workflow declarations, and SHACL shapes |

This calibration is what lets a working group joining a new workflow extension immediately know what to build. Clinical-research has twelve functional areas (Study Design through Quality Management). Clinical-care will probably have ten to fifteen (patient registration, encounter, orders, clinical documentation, billing, discharge planning, care coordination, lab integration, imaging integration, medication reconciliation, and so on). Physical-AI will have eight to twelve (sensors, HVAC, security, access control, environmental monitoring, lighting, power, network). Operational management will have ten to fifteen (HR, finance, procurement, quality, forecasting, supply, facilities, contracts, scheduling). Manufacturing CMC will have its own list. The pattern is the same.

The calibration also disciplines scope. If a proposed workflow extension has only three functional areas, it's probably a functional area of an existing workflow, not its own workflow. If it has thirty, it's probably two workflows. Per-bucket strategies refine the calibration where domain-specific evidence warrants; the brief-level numbers above are the strawman.

## What a workflow extension contains

Each workflow extension is a directory under its bucket (e.g., `hcls/clinical-research/v1/`) with these artifacts at v1:

- **SKOS taxonomy** (`taxonomy.ttl`). Workflow classes with operator-vocabulary `prefLabel`, `altLabel` for synonyms, `skos:exactMatch` / `closeMatch` to NCIt or peer-vocabulary anchors.
- **OWL classes + SHACL shapes** (`shapes.ttl`). Workflow classes with `rdfs:subClassOf` chains to TOP Core and (where Pattern B applies) to sibling workflow extensions. SHACL property shapes per functional area.
- **CV YAMLs** (`vocabulary/<functional-area>/<concept>.yaml`, per ADR-0018). Operator-vocabulary synonyms, anti-synonyms, context-routing for homonyms, per-property enums.
- **SSSOM crosswalks** (`crosswalks/<functional-area>/<concept>.sssom.tsv`, per ADR-0018). Per-class mappings to peer vocabularies, mirrored from EVS REST mapsets or other source-of-truth at pinned versions.
- **Walkthroughs** (`walkthroughs/<scenario>.ttl`). Concrete instances demonstrating L0 -> L1 -> L2 -> workflow-class composition end-to-end. SHACL-validated against the workflow's shapes.
- **Spec page** (`index.html`). One-page narrative covering the workflow's mission, functional areas, alignment summary, cross-workflow declarations, deferred items.

The artifacts compose against TOP Core directly (or, for cross-workflow concepts, against a sibling workflow extension via Pattern B). No class-level shared tier is interposed.

## What this strategy commits the project to

- **Workflow extensions decompose along the work-category axis only.** Setting, layer within setting, and therapeutic area are instance-level properties.
- **Pattern B is the cross-workflow discipline.** Sibling workflow extensions may cross-reference via `rdfs:subClassOf` when concepts genuinely cross both workflows' operator semantics.
- **Pattern C is the scoped escalation path for dense overlap zones.** Not adopted across the board; available via RFC for specific zones (oncology first).
- **The functional-areas calibration applies across every workflow extension.** 8 to 15 functional areas, 5 to 30 classes per area.
- **Workflow extensions live under their bucket's directory.** `hcls/clinical-research/`, `foundations/physical-ai/`, `manufacturing/cmc/`, etc.
- **Strategy ratifies as ADR-0021 (workflow decomposition strategy)** when the cross-WG umbrella forms and the RFC process formally starts. ADR number is a strawman pending activation order.

## What this strategy does NOT do

- It does not author any class catalog. Each workflow extension's classes ship in its own seed and its own RFCs.
- It does not commit any specific workflow extension to a ship date. Per-workflow seeds and RFCs handle that.
- It does not specify bucket structure. Bucket inventory and per-bucket details live in per-bucket strategy documents.
- It does not specify composition behavior. Compositions are a fourth layer above workflows; see `top-compositions-strategy.md`.
- It does not preclude future axes. If a future workflow surfaces a fifth genuine decomposition axis, a brief-level RFC adds it.

## Pointers

- Strategy brief: `top-strategy-brief.md`
- HCLS bucket strategy: `top-hcls-strategy.md` (HCLS-specific NCIt alignment, oncology Pattern-C escalation)
- Foundations bucket strategy: `top-foundations-strategy.md`
- Compositions strategy: `top-compositions-strategy.md`
- Clinical-research seed (first workflow extension seed): `top-hcls-clinical-research.md`
- TOP Core: `core/v1/`, `taxonomy/taxonomy.ttl`
- Extension contract: `governance/extension-contract.md`

---

*Workflows strategy v1. The substance of this strategy becomes the basis for ADR-0021 (workflow decomposition strategy) when the cross-WG umbrella forms and the RFC process formally starts.*
