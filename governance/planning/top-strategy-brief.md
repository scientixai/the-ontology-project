# TOP Architectural Strategy Brief

*Status: pre-RFC strategic planning. Author: Bo Lora (BDFL, sole signatory to The Ontology Project as of 2026-05-14). Audience: Bo, future working-group leads across every bucket, founding signatories, and anyone reading TOP to understand how the project organizes its work above Core.*

*Companion to TOP Core (one root, eight categories, twenty-nine leaves) and to ADRs 0001 through 0020. Pre-RFC; the formal RFC process starts when the relevant working groups do.*

This document is the umbrella for TOP's architectural strategy above Core. Detailed strategy lives in five layer-specific and bucket-specific documents this brief references:

- `top-workflows-strategy.md`: how workflow extensions are structured across every bucket
- `top-foundations-strategy.md`: the foundations bucket (physical-AI, operational management)
- `top-compositions-strategy.md`: the compositions namespace (smart-hospital, DCT, VBC, etc.)
- `top-hcls-strategy.md`: HCLS bucket specifics (clinical-research, clinical-care, pharmacovigilance, public-health, registries)
- `top-hcls-clinical-research.md`: the clinical-research workflow extension v1 seed (the launch demonstrator)

The brief carries cross-cutting commitments only. Each layer-specific document is the source of truth for its layer; cross-references point here when concepts span layers.

---

## Why this document exists

The Ontology Project commits to keeping Core small (one root, eight categories, twenty-nine leaves) and to scaling everything else through composition. That commitment is operationally specific: it determines how working groups organize, how reference graphs compose, how cross-cutting concepts get a home, and how TOP avoids the structural failure modes that other ontology projects have lived through.

The brief captures the cross-cutting commitments. The layer-specific documents capture the per-layer details. Both are pre-RFC; they become the basis for ADR-0021 (workflow decomposition strategy, ratifying `top-workflows-strategy.md`), ADR-0022 (HCLS bucket strategy and NCIt-anchored alignment, ratifying `top-hcls-strategy.md`), ADR-0023 (foundations bucket strategy, ratifying `top-foundations-strategy.md` when foundations activates), ADR-0024 (compositions namespace strategy, ratifying `top-compositions-strategy.md` when the first composition activates), and ADR-0025 (clinical-research workflow-overlap pattern and v1 scope, ratifying `top-hcls-clinical-research.md`).

ADR numbering is a strawman. The actual numbers will be assigned at ratification time based on which documents reach RFC first.

## The mission anchor

TOP exists to be provenance infrastructure for decision architecture in high-consequence regulated industries. The clinical lifecycle is the first focus because the stakes are highest there and the failure modes are best-named, but the architecture generalizes. The manifesto's "we owe it to humans" stance and the first-principles document's practitioner-first, standards-as-projection posture are the mission anchor every layer of this strategy traces back to.

Every architectural choice this brief and the layer-specific documents commit to passes the practitioner-first test (operators recognize the names) and the provenance-grade test (every claim has a chain back to its source). Where two patterns are equally clean in the abstract, the one that preserves operator agency and provenance wins.

## The FHIR / HL7 anti-pattern

This is the foundational discipline. Every architectural choice in the layer-specific documents derives from it.

FHIR / SMART Models has a Healthcare domain. Under Healthcare, a sub-domain named HL7. That choice conflates two completely different axes:

- **Work category.** What kind of operational work is being done. Clinical research, care delivery, public health, manufacturing, pharmacovigilance.
- **Vocabulary publisher.** Who maintains the controlled vocabulary or schema. HL7, CDISC, FDA, ICH, SNOMED, MedDRA, FHIR-the-spec, ISO.

`Healthcare -> HL7` is the publisher axis. The right axis for sub-domains is the work axis. HL7 is not a kind of healthcare work; HL7 is a standards body that publishes specs for healthcare work. Putting HL7 as a node in the work hierarchy creates a structural defect that propagates downstream: every time HL7 publishes something that's also FHIR-shaped (or vice versa), or that overlaps with CDISC, the placement gets weird and concepts end up in the wrong place.

TOP precludes this mistake by axis discipline. Children of domain buckets are work categories, never publishers. Vocabulary publishers and their specs (CDISC, HL7, FHIR, FDA, ICH, SNOMED, MedDRA, ICD, RxNorm, LOINC, NCIt) live at the alignment edge, accessed through the four-tier hub-and-spoke alignment named in `top-hcls-strategy.md`. They are never nodes in the workflow hierarchy.

This needs naming because it's an attractor. Standards bodies are easy to reach for as organizing categories because their names are familiar and their boundaries feel like natural decompositions. They are not. The discipline applies at every layer: not just at the workflow-extension axis (where it's most visible) but also at the compositions layer (a smart-X composition is a deployment pattern, not a publisher) and at the bucket level (HCLS is a work-category bucket, not an HL7 bucket).

## Four organizational layers above TOP Core

| Layer | What it is | Document | What lives here |
| --- | --- | --- | --- |
| **1. TOP Core** | One root, eight categories, twenty-nine leaves. Universal across every TOP workflow. | `core/v1/` artifacts; `taxonomy.md`; ADRs 0001 through 0020. | The eight Category-Level Objects, the twenty-nine leaves, class-level PROV-O alignment, light-edge BFO, the SHACL Universal DNA contract. |
| **2. Domain buckets** | Governance umbrellas and directory groupings that coordinate stewardship across related workflow extensions. **Not class layers.** | Per-bucket: `top-hcls-strategy.md`, `top-foundations-strategy.md`, future `top-manufacturing-strategy.md`, etc. | Working-group cohorts, CODEOWNERS structure, repository directory roots, URI path prefixes. No classes. |
| **3. Workflow extensions** | Reference graphs for specific operational work categories. Each composes against TOP Core directly; some declare cross-workflow `subClassOf` to sibling workflow extensions per Pattern B. | Cross-cutting: `top-workflows-strategy.md`. Per-workflow seeds: `top-hcls-clinical-research.md`, future seeds. | Class definitions, SHACL shapes, CV YAMLs, SSSOM crosswalks, walkthroughs, spec pages. |
| **4. Compositions** | Packaged bundles that reference multiple workflow extensions (and the foundations underneath them) to express a named deployment pattern. Each composition adds only the concepts that **genuinely emerge** from the composition, never redeclares anything from the underlying layers. | `top-compositions-strategy.md`. Per-composition seeds when activated. | Composition-specific classes, cross-layer SHACL invariants, deployment reference patterns, spec pages. |

Domain buckets are governance, not architecture. Compositions are architecture but sit above workflow extensions, not as a replacement for them. The full elaboration of each layer is in its own document.

## The four-axis decomposition discipline

Workflow extensions decompose along the **work-category axis only**. Other axes that real-world deployments cut across (setting / place type, layer within a setting, therapeutic area / sector specialty) attach as instance-level properties, not as new workflow-extension branches.

The full treatment is in `top-workflows-strategy.md`. The commitment captured here is that no future workflow-extension RFC will propose a non-work-category axis without first going through a brief-level RFC that names the new axis.

## Launch sequence

The first concrete artifact TOP ships is **clinical-research v1**, with Pattern B stubs to clinical-care. The launch sequence at a glance:

1. **Clinical-research v1.** Twelve functional areas, NCIt-anchored alignment, three worked examples, Pattern B stubs to clinical-care. Launch demonstrator. JPM Healthcare Week 2027 is the audience-readiness milestone. Full scope in `top-hcls-clinical-research.md`.
2. **Clinical-care v1.** Stubs from clinical-research v1 graduate to real classes. The clinical-care WG forms; the rest of HCLS workflows follow on their own cadence.
3. **Foundations workflow extensions** (physical-AI, operational management). Driven by composition demand from adopters. Ali is the candidate WG lead for physical-AI (per Bo's 2026-05-14 signal); operational management WG lead TBD.
4. **First composition** (smart-hospital is the likely first, given HCLS launch). Lifts when an adopter needs a packaged composition and a steward steps forward.
5. **Other buckets and workflows** (manufacturing, supply chain, energy, financial services) on their own RFC paths.

The sequence reflects what adopters need first and where stewardship capacity exists. Foundations and compositions do not gate clinical-research v1; they lift in parallel as demand and capacity allow.

## What this brief commits the project to

- **Four organizational layers above Core.** Core, buckets, workflow extensions, compositions. Layer-specific strategies in the five companion documents.
- **The FHIR / HL7 anti-pattern is precluded at every layer.** Standards bodies and their specs live at the alignment edge, never as nodes in the work hierarchy. The discipline applies to buckets, to workflows, to compositions, and to instance properties.
- **The work-category axis is the only workflow-extension branching axis.** Other axes are instance-level properties.
- **Clinical-research v1 is the first concrete artifact.** Other workflows and the foundations and compositions namespaces lift on their own cadence.
- **Pre-RFC strategy ratifies through working-group RFCs.** Each layer-specific document becomes the basis for one or more ADRs when its WG activates.
- **Manifesto and first-principles remain load-bearing.** Practitioner-first (ADR-0013), standards-as-projection (first-principles.md § 1), no bespoke flags (ADR-0015), open Core with constrained extension (ADR-0019).

## What this brief does NOT do

- It does not author classes. Each workflow extension's class catalog ships in its own seed and its own RFCs.
- It does not finalize bucket or composition names. Working names are used throughout (foundations, compositions, HCLS); WGs ratify or override at activation time.
- It does not change TOP Core. Core's eight categories and twenty-nine leaves are unchanged.
- It does not preclude future layers or axes. If a future workflow surfaces a fifth genuine decomposition axis or a fifth organizational layer, a new brief-level RFC addresses it.
- It does not assign ADR numbers definitively. The strawman numbers (0021 through 0025) assume sequential ratification; actual numbers depend on which documents reach RFC first.

## Relationship to existing ADRs

This strategy operationalizes and extends prior commitments without superseding any.

- **ADR-0004 (composable workflow extensions, not sibling reference graphs).** Operationalized by the four-layer model. Buckets and compositions are not siblings of Core; they are layers that compose against Core.
- **ADR-0013 (practitioner-first).** Drives the work-category axis choice. Operators name their work; setting and therapeutic area are properties of the work.
- **ADR-0015 (promote facts to entities, no bespoke flags).** Disciplines the instance-level treatment of setting and therapeutic area.
- **ADR-0016 (schema.org alignment).** Generalizes to the four-tier alignment in `top-hcls-strategy.md`.
- **ADR-0017 (monorepo with directory-scoped ownership).** Maps directly to the bucket-then-workflow-then-composition directory structure.
- **ADR-0018 (six-stage ontology pipeline).** Every workflow extension carries the pipeline; compositions add a layer on top.
- **ADR-0019 (open Core, constrained extension).** Sets the property-flavor discipline. The strategy preserves it.
- **ADR-0020 (top:Organism as fifth Agent leaf).** Most recent Core addition. Unchanged.

## Pointers

- TOP Core: `core/v1/`, `taxonomy/taxonomy.ttl`, `taxonomy.md`
- Mission and design rules: `manifesto.html`, `first-principles.html`, `first-principles.md`
- Working groups: `governance/working-groups.md`
- Extension contract: `governance/extension-contract.md`
- Decision log: `governance/decision-log.md`
- Roadmap: `roadmap.md`, `roadmap.html`

---

*Brief v1. Iterative document. The substance of this brief becomes the foundational ADR (strawman ADR-0021 or 0023 depending on activation order) when the cross-WG umbrella forms and the RFC process formally starts.*
