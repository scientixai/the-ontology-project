# Workflow Decomposition Strategy: HCLS and Adjacent Buckets

*Status: pre-RFC strategic planning. Author: Bo Lora (BDFL, sole signatory to The Ontology Project as of 2026-05-14). Audience: Bo for near-term build planning; the future Clinical Research Working Group and other HCLS working groups; future leads of non-HCLS buckets (smart foundations, manufacturing, supply chain, energy, financial services).*

*Companion to TOP Core (one root, eight categories, twenty-nine leaves), to ADRs 0001 through 0020, and to the clinical-research seed (`governance/planning/hcls-clinical-research-seed.md`). Pre-RFC; the formal RFC process starts when the relevant working groups do.*

---

## Why this document exists

The clinical-research seed sits one layer down from the question that needs to settle before any HCLS workflow extension stakes ground. The seed answers "when clinical-research overlaps with care-delivery, how does the shared concept attach?" That is the right question to ask **once the broader architecture is settled.** Before that, a larger question waits: **what shape does HCLS take above the individual workflows, and how do workflows that span HCLS and non-HCLS adjacencies (a smart hospital, a clinical research informatics platform, a pharma manufacturing facility) fit into the tree without recreating the FHIR / SMART Models structural mistake?**

This document captures that broader architecture. The seed is the first workflow extension's seed; this is the architecture the seed assumes. Once ratified through the working-group RFC process, this strategy becomes ADR-0023 (decomposition strategy) alongside the seed's ADR-0021 (workflow-overlap pattern) and ADR-0022 (NCIt-anchored alignment). The seed defers to this document on questions of bucket structure, axis choice, and composition patterns; this document defers to the seed on the specific clinical-research-to-care-delivery boundary.

## The failure mode this prevents

The FHIR / SMART Models architecture has a Healthcare domain. Under Healthcare, a sub-domain named **HL7**. That choice conflates two completely different axes:

- **Work category.** What kind of operational work is being done. Clinical research, care delivery, public health, manufacturing, pharmacovigilance.
- **Vocabulary publisher.** Who maintains the controlled vocabulary or schema. HL7, CDISC, FDA, ICH, SNOMED, MedDRA, FHIR-the-spec, ISO.

`Healthcare → HL7` is the publisher axis. The right axis for sub-domains is the work axis. HL7 is not a kind of healthcare work; HL7 is a standards body that publishes specs for healthcare work. Putting HL7 as a node in the work hierarchy creates a structural defect that propagates downstream: every time HL7 publishes something that's also FHIR-shaped (or vice versa), or that overlaps with CDISC, the placement gets weird and concepts end up in the wrong place.

TOP precludes this mistake by axis discipline. Children of domain buckets are work categories, never publishers. Vocabulary publishers and their specs (CDISC, HL7, FHIR, FDA, ICH, SNOMED, MedDRA, ICD, RxNorm, LOINC, NCIt) live at the **alignment edge**, accessed through the four-tier hub-and-spoke alignment named in Part 2 of the clinical-research seed. They are never nodes in the workflow hierarchy.

This needs naming because it's an attractor. Standards bodies are easy to reach for as organizing categories because their names are familiar and their boundaries feel like natural decompositions. They are not.

## Four decomposition axes, and which becomes a workflow extension

Real-world deployments cut across at least four axes. Naming each one and committing to which becomes a workflow extension is the single most consequential architectural choice in TOP after the eight Core categories themselves.

| Axis | What it is | How TOP handles it |
| --- | --- | --- |
| **Work category** | What kind of operational work. Clinical research, care delivery, manufacturing, building operations, financial clearing. | **Workflow extensions.** This is the only axis that becomes a workflow extension. |
| **Setting / place type** | Hospital, clinic, lab, home, mobile unit, pharmacy, infusion center, manufacturing facility, distribution center, retail outlet, vessel, field site. | **Instance-level property** on `top:Physical` (and its specializations). Operator-facing enum at the CV layer, optionally promoted to a SKOS hierarchy referencing NCIt's facility-type subset where applicable. |
| **Layer within a setting** | Physical infrastructure, operational management, the operational work itself. A hospital has all three; a manufacturing plant has all three; a smart office has the first two. | **Workflow-extension composition.** Each layer is its own workflow extension. A real deployment composes the relevant ones. Not a new axis. |
| **Therapeutic area / sector specialty** (HCLS-specific; analogous concepts in other buckets) | Oncology, cardiology, rare disease, mental health, pediatrics in HCLS. Subsea vs onshore in energy. Discrete vs process in manufacturing. | **Instance-level property** on the relevant workflow class. Operator-facing enum at the CV layer, mapped to NCIt or other domain hub at the SKOS layer. Not a workflow-extension axis. |

The discipline is: **only the work axis branches the tree.** Everything else attaches as a property of instances, with SKOS hierarchies at the CV layer for the categorical structure operators recognize.

This is what keeps a clinical-research `Study` and a clinical-care `Encounter` and a pharmacovigilance `SignalDetection` from each minting "oncology" classes. Oncology is a property both reference. The Study has `therapeuticArea=oncology`. The Encounter has `therapeuticArea=oncology`. The shared meaning lives at the CV layer (a SKOS concept scheme of therapeutic areas anchored to NCIt's Disease subset), not in a workflow-extension axis.

Same for setting. A clinical-research `Site` is a `top:Physical` with `settingType=academic-medical-center`. A clinical-care `Site` is a `top:Physical` with `settingType=community-hospital` or `outpatient-clinic`. The hospital-ness, the clinic-ness, the academic-ness all live at the CV layer as a SKOS hierarchy of facility types. No "hospital" workflow extension exists, because hospital is a kind of place, not a kind of work.

## Smart-X is composition, not workflow

The clearest illustration of the layer-within-setting axis is the "smart hospital" question. A smart hospital is not a sub-domain of HCLS and not a workflow extension. A smart hospital is what you get when you compose three layers at one deployed site:

| Layer | Workflow extension | Cross-industry reach |
| --- | --- | --- |
| Physical | physical-AI (working name) | Smart office, smart factory, smart warehouse, smart campus, smart lab, smart retail. Cross-industry, not HCLS-specific. |
| Operational | operational management (working name) | Any sufficiently large operation. Hospital, university, manufacturer, retailer, financial institution. Cross-industry, not HCLS-specific. |
| Work | clinical-care, and at AMCs also clinical-research | HCLS-specific. |

A smart hospital = physical-AI + operational + clinical-care + (at AMCs) clinical-research. A smart clinic = physical-AI + operational + clinical-care, smaller scope, no clinical-research. A smart lab = physical-AI + operational + lab-ops (which may be its own workflow extension, or a functional area within clinical-research, depending on what the WG decides). A pharma manufacturing plant = physical-AI + operational + CMC-manufacturing. A bank branch = physical-AI + operational + retail-banking.

The replication that the work-category axis avoids in the workflow-extension space is the same replication this composition avoids at the deployment-context space. Building a "smart hospital" reference graph that re-declares HVAC, sensors, security, access control, HR, finance, procurement, and clinical care all in one place is the same defect as putting HL7 under Healthcare. Pick the right primitive layer, ship each layer as its own reference graph, compose at deployment time.

The composition is real and operationally important. A coordinator running a clinical trial at an AMC interacts with all four layers daily: she badges into the building (physical-AI), books a room and orders supplies (operational), documents a participant's vitals (clinical-care), and updates the eCRF (clinical-research). The graph she queries spans all four. But the architecture stores each layer once, in its own workflow extension, and the composition is in the instance data, not in the class hierarchy.

## Three layers of organization above TOP Core

With the axis question settled, the architectural layers become legible:

| Layer | What it is | What lives here |
| --- | --- | --- |
| **1. TOP Core** | One root, eight categories, twenty-nine leaves. Universal across every TOP workflow. | The eight Category-Level Objects (Agent, Location, Resource, Scope, Temporal, Evidence, Outcome, Constraint) and their twenty-nine leaves. Class-level PROV-O alignment; light-edge BFO where it lands cleanly. The SHACL Universal DNA contract. |
| **2. Domain buckets** | Governance umbrellas and directory groupings that coordinate stewardship across related workflow extensions. **Not class layers.** | Working-group cohorts, CODEOWNERS structure, repository directory roots, URI path prefixes. No classes. |
| **3. Workflow extensions** | Reference graphs for specific operational work categories. Each composes against TOP Core directly; some declare cross-workflow `subClassOf` to sibling workflow extensions per the seed's Pattern B. | The actual class definitions, SHACL shapes, CV YAMLs, SSSOM crosswalks, walkthroughs, spec pages. |

Domain buckets are governance, not architecture. They exist because working-group cohesion benefits from coordinated stewardship across related workflows (the HCLS WGs share regulatory context, standards-body alignment, and operator-vocabulary overlap; an HCLS WG umbrella coordinates their PR review cadence and their RFC discussions). But buckets contain no classes of their own. A clinical-research class composes against TOP Core directly, not against a non-existent `hcls:` namespace.

This is the third treatment of "HCLS as a layer" question, and it's worth stating each treatment explicitly:

1. **HCLS as a class-level shared tier (Pattern C in the seed).** Rejected. Governance overhead is the killer; defending the line between "Core-universal" and "shared-HCLS-only" becomes permanent project work; recreates the FHIR mistake at a smaller scale.
2. **HCLS as a working-group umbrella.** Adopted. Coordinated WG cohort for clinical-research, clinical-care, pharmacovigilance, public-health, registries.
3. **HCLS as a directory and URI grouping.** Adopted. The bucket is visible in the repository tree (`hcls/clinical-research/`, `hcls/clinical-care/`) and in URIs (`https://top.scientix.ai/hcls/clinical-research/v1`). The namespace prefix remains short and operator-readable (`topcr:`, `topcd:`); the path reflects the architecture.

## Domain bucket inventory

Buckets known or anticipated at TOP launch and shortly after. This list is open; new buckets land via RFC.

| Bucket | Workflow extensions (anticipated) | Status |
| --- | --- | --- |
| **HCLS** | clinical-research, clinical-care, pharmacovigilance, public-health, registries | Active. Clinical-research is the launch demonstrator. |
| **Smart foundations** (working name) | physical-AI, operational management | Anticipated. Cross-industry; HCLS depends on it for smart-hospital deployments. Bucket-vs-sibling question open. |
| **Manufacturing** | CMC-manufacturing (pharma), discrete manufacturing, process manufacturing | Anticipated. Bucket because manufacturing is a coherent operator audience with shared standards (ISA-88, ISA-95, ISO 9001) even when products differ. |
| **Supply chain** | logistics, distribution, cold-chain, customs | Anticipated. |
| **Energy** | grid operations, generation, distribution, retail | Anticipated. ISO 15926 / CFIHOS adjacencies. |
| **Financial services** | clearing, custody, trading, retail banking | Future. |

Cross-bucket relationships matter. A pharma manufacturing plant uses smart-foundations (physical-AI + operational) plus manufacturing (CMC) plus possibly HCLS (when GMP-relevant clinical interactions occur). A clinical trial uses HCLS (clinical-research, clinical-care) plus possibly smart-foundations (if running at an AMC with smart-hospital deployment). The Pattern B cross-workflow `subClassOf` discipline from the seed applies across buckets as well as within them.

## The functional-areas calibration

Every workflow extension decomposes into functional areas at a consistent granularity. The clinical-research seed names twelve (Study Design, Regulatory Affairs, Finance, Setup, Site Management, Clinical Supply, Recruitment, Intervention, Pharmacovigilance, Data Management, Monitoring, Quality Management). That number and that shape are deliberate, and they are the right pattern for every workflow extension TOP adopts.

The discipline:

| Property | Calibration |
| --- | --- |
| Number of functional areas per workflow extension | 8 to 15 |
| Classes per functional area | 5 to 30 |
| Operator-vocabulary recognizability | Each functional area maps to a department, function, or operational responsibility a practitioner in the domain would name without prompting |
| Stewardship | One or two WG maintainers per functional area, ideally; one SHACL shapes file per functional area |
| Spec doc structure | Each functional area gets a section in the workflow extension's spec page with its classes, properties, NCIt anchors, cross-workflow declarations, and SHACL shapes |

This calibration is what lets a working group joining a new workflow extension immediately know what to build. Clinical-research has twelve functional areas (Study Design through Quality Management). Clinical-care will probably have ten to fifteen (patient registration, encounter, orders, clinical documentation, billing, discharge planning, care coordination, lab integration, imaging integration, medication reconciliation, and so on). Physical-AI will have eight to twelve (sensors, HVAC, security, access control, environmental monitoring, lighting, power, network). Operational will have ten to fifteen (HR, finance, procurement, quality, forecasting, supply, facilities, contracts, scheduling). Manufacturing CMC will have its own list. The pattern is the same.

The calibration also disciplines scope. If a proposed workflow extension has only three functional areas, it's probably a functional area of an existing workflow, not its own workflow. If it has thirty, it's probably two workflows.

## Launch sequence

Commitment: **clinical-research ships first, with Pattern B stubs to clinical-care.**

The reasoning:

- Clinical-research is the launch demonstrator. JPM Healthcare Week 2027 is the audience-readiness milestone. Biopharma executives, sponsors, CROs, regulators evaluate clinical-research v1 in the room.
- Clinical-research crosses into clinical-care at well-defined boundaries (AE, MedicationAdministration, Visit, Procedure). Per the seed's Pattern B, these crosses are explicit `rdfs:subClassOf` declarations against clinical-care classes.
- For v1, clinical-care exists as **stub workflow extension**: the directory exists, the spec page exists with placeholder language, and the few classes clinical-research crosses into (`topcd:AdverseEvent`, `topcd:MedicationAdministration`, `topcd:Encounter`) exist as stub declarations. The stubs carry enough structure for clinical-research's Pattern B declarations to resolve and for SHACL validation to pass, but they do not pretend to be a complete clinical-care reference graph.
- Clinical-care v1 (full reference graph) lifts after clinical-research v1 ships. When clinical-care's WG forms, the stubs graduate to real classes; clinical-research's Pattern B declarations point to the same URIs and continue to resolve cleanly.
- Physical-AI, operational, the full smart-foundations bucket follow at their own pace, driven by need rather than launch sequencing.

What this commits to:

- The clinical-research seed's v1 launch scope (Part 3) stays as written. Twelve functional areas, NCIt-anchored alignment, the three worked examples.
- The clinical-care workflow extension's stub state is documented explicitly. The placeholder spec page and the stub class declarations land alongside clinical-research v1, not before and not after.
- Pattern B cross-workflow declarations from clinical-research to clinical-care are reviewed against the operator-grounded crossing test (per the seed) even when the target is a stub. The discipline applies from day one.

What this defers:

- Full clinical-care v1. Lifts when the clinical-care WG forms.
- Pharmacovigilance v1 as a standalone workflow extension. The pharmacovigilance functional area of clinical-research v1 ships first; pharmacovigilance as its own workflow extension (potentially with its own functional areas for signal management, risk management plans, post-market surveillance) lifts when there's WG capacity and clear scope separation from clinical-research.
- Smart-foundations bucket (physical-AI and operational management). Lifts on its own timeline, driven by smart-hospital deployment demand from adopters, not by HCLS launch sequencing.
- Any non-HCLS bucket. Manufacturing, supply chain, energy, financial services all lift on their own RFC paths.

## What this strategy commits the project to

- **Workflow extensions decompose along the work-category axis only.** Setting, layer within setting, and therapeutic area are instance-level properties, not workflow-extension axes.
- **Smart-X compositions are deployment-time.** No "smart hospital" workflow extension exists. Smart hospitals are deployed instances composing physical-AI, operational, clinical-care, and clinical-research.
- **Domain buckets are governance and directory groupings, not class layers.** HCLS is a bucket; it has no namespace, no classes, no SHACL shapes of its own.
- **The four-axis discipline precludes the FHIR / HL7 mistake.** Standards bodies and their specs live at the alignment edge, never as nodes in the work hierarchy.
- **The functional-areas calibration (8 to 15 areas per workflow extension, 5 to 30 classes per area) is the project-wide pattern.** Working groups inherit the calibration; new workflow extensions decompose into it from day one.
- **Clinical-research ships first with Pattern B stubs to clinical-care.** Launch sequence committed.
- **Strategy ratification appends ADR-0023 (decomposition strategy)** alongside the seed's ADR-0021 (workflow-overlap pattern) and ADR-0022 (NCIt-anchored alignment), once the relevant working groups form and the RFC process opens.

## What this strategy does NOT do

- It does not finalize the smart-foundations bucket name. "Smart foundations" is the current working name and the strawman the WG ratifies or overrides at bucket activation time. The double meaning (the physical foundations of a building, the operational foundations of an enterprise) is deliberate and pairs cleanly with smart-X deployments built on top.
- It does not commit physical-AI and operational management to one bucket vs two. They might be siblings inside one smart-foundations bucket, or two separate top-level buckets. The decision waits until at least one of them activates and the WG candidates surface.
- It does not author any class catalog. Each workflow extension's class catalog ships in its own seed and its own RFCs, following this strategy as the architectural anchor.
- It does not change TOP Core. Core's eight categories and twenty-nine leaves are unchanged. This strategy operates entirely in the layers above Core.
- It does not preclude future axes. If a future workflow surfaces a fifth genuine decomposition axis that resists treatment as an instance-level property, a new RFC addresses it. The current four are what real-world HCLS, manufacturing, and smart-foundations deployments expose; that may not be exhaustive.

## Open questions for working-group resolution

The strategy surfaces these as questions the relevant working groups settle, with strawman positions taken in this document for each.

1. **Smart-foundations bucket name.** Working name: `smart-foundations/`. The name captures both the physical foundations of a building and the operational foundations of an enterprise; it pairs cleanly with smart-X deployments built on top (smart hospital, smart clinic, smart lab, smart factory built on smart foundations). WG ratifies or overrides at bucket activation time.
2. **Physical-AI and operational management: one bucket or two?** Strawman: one (`smart-foundations/physical-ai/`, `smart-foundations/operational/`). WG may split into two top-level buckets if stewardship cohorts genuinely diverge.
3. **Therapeutic-area treatment.** Strawman: instance-level property with a SKOS hierarchy anchored to NCIt's Disease subset. HCLS WGs may sharpen this if oncology-specific (or rare-disease-specific) operational needs require classes rather than just properties; in that case Pattern C scoped to oncology (per the seed's escalation path) is the route, not a therapeutic-area workflow-extension axis.
4. **Setting / place-type treatment.** Strawman: instance-level property on `top:Physical` (and on its workflow specializations like `topcr:Site` and `topcd:Site`) with a SKOS hierarchy of facility types. HCLS WGs may push back if a `top:Healthcare-Facility` leaf is justified; that's a Core-promotion RFC, not a workflow-extension RFC.
5. **Stub-class governance for clinical-care during clinical-research v1.** The clinical-care stub classes that clinical-research v1's Pattern B declarations point to live in `hcls/clinical-care/v1/` as a minimal-stub spec page. WG decides who reviews stub additions (clinical-research WG, future clinical-care WG, both, or the HCLS umbrella) until clinical-care's WG activates.
6. **Pharmacovigilance graduation timing.** Pharmacovigilance is a functional area of clinical-research v1. It may graduate to its own workflow extension when its scope (signal detection, RMP, post-market surveillance, REMS) outgrows the functional-area calibration. WG decides the threshold.
7. **Cross-bucket Pattern B.** The seed names Pattern B for cross-workflow declarations within HCLS. The strategy implies the same pattern across buckets (e.g., a pharma manufacturing class declaring `rdfs:subClassOf` against a clinical-supply class). WG ratifies that explicitly when the first cross-bucket case arises.

## Relationship to existing ADRs

This strategy operationalizes and extends prior commitments without superseding any.

- **ADR-0004 (composable workflow extensions, not sibling reference graphs)** is the foundation. The strategy adds the layer above (domain buckets as governance) and the layer below (workflow-extension composition via Pattern B). The "no sibling reference graphs by industry" commitment is preserved at the workflow-extension level. Buckets are not siblings of Core; they are governance umbrellas over workflow extensions, with no class content of their own.
- **ADR-0013 (practitioner-first, TOP's primary customer)** drives the axis choice. Operators name their work category as the primary identifier; setting and therapeutic area are properties of the work, not new categories. The work-category axis is the practitioner-first axis.
- **ADR-0015 (promote facts to entities, no bespoke flags)** disciplines the instance-property treatment of setting and therapeutic area. A `therapeuticArea=oncology` instance value is the operator-vocabulary surface; the underlying SKOS / NCIt graph carries the structural ancestry.
- **ADR-0016 (schema.org alignment where the peer is honest)** generalizes to the four-tier alignment model in the clinical-research seed. Strategy doesn't change this.
- **ADR-0017 (monorepo with directory-scoped ownership)** maps directly to the directory-bucket-then-workflow structure. CODEOWNERS resolves `/hcls/` to the HCLS WG umbrella, `/hcls/clinical-research/` to the clinical-research WG, and so on.
- **ADR-0019 (open Core, constrained extension)** sets the property-flavor discipline. Workflow extensions extend Core through the flavor mechanism. The strategy preserves this; buckets and compositions don't affect property flavors.
- **ADR-0020 (top:Organism as fifth Agent leaf)** is the most recent ADR. Unchanged by this strategy.

## Pointers

- Clinical-research seed (this strategy's primary downstream consumer): `governance/planning/hcls-clinical-research-seed.md`
- TOP Core taxonomy: `/taxonomy/taxonomy.ttl`, `/taxonomy.md`, `/core/v1/shapes.ttl`, `/core/v1/index.html`
- First-principles: `/first-principles.md`, `/first-principles.html`. Practitioner-first, standards-as-projection, the BDFL governance term, the six-stage pipeline.
- Manifesto: `/manifesto.html`. Convener and founding signatories. The mission anchor for HCLS provenance infrastructure.
- Extension contract: `/governance/extension-contract.md`. Open Core, constrained extension. The property-flavor discipline.
- Working groups: `/governance/working-groups.md`. WG lifecycle, CODEOWNERS structure.
- Decision log: `/governance/decision-log.md`. ADRs 0001 through 0020. Future ADR-0021 (workflow-overlap), ADR-0022 (NCIt-anchored alignment), ADR-0023 (decomposition strategy) ratify when the relevant working groups form.

---

*Strategy v1. Iterative document. The substance of this strategy becomes the basis for ADR-0023 (decomposition strategy) when the HCLS working groups form and the RFC process formally starts. Until then, this document is the architectural anchor that the clinical-research seed and future workflow seeds (clinical-care, physical-AI, operational, others) reference for the layers above Core.*
