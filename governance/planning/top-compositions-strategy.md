# TOP Compositions Strategy

*Status: pre-RFC strategic planning. Author: Bo Lora (BDFL, sole signatory to The Ontology Project as of 2026-05-14). Audience: future composition working-group leads (smart-hospital, smart-clinic, DCT, VBC, others), and adopters deploying TOP reference graphs in composed real-world environments.*

*Companion to TOP Core, to `top-strategy-brief.md` (the architectural umbrella), to `top-workflows-strategy.md` (cross-bucket workflow discipline), to `top-foundations-strategy.md` (the bucket compositions most heavily reference), and to per-bucket strategies (`top-hcls-strategy.md`, future). Pre-RFC; the formal RFC process starts when the first composition working group does.*

---

## Why this document exists

Compositions are the fourth organizational layer above TOP Core. They are packaged bundles that reference workflow extensions (across one or more buckets) and add only the classes that emerge from the composition itself. A composition is a named deployment pattern, identified by what gets composed rather than by a single work category.

Examples of compositions:

- **smart-hospital** (foundations/physical-AI + foundations/operational + hcls/clinical-care + at AMCs hcls/clinical-research)
- **decentralized clinical trial (DCT)** (hcls/clinical-research + hcls/clinical-care + telehealth pattern + patient-portal pattern)
- **value-based-care program (VBC)** (hcls/clinical-care + foundations/operational + financial-services/clearing + analytics pattern)
- **registry-based study** (hcls/registries + hcls/clinical-research + sometimes hcls/clinical-care)
- **pharma manufacturing plant** (foundations/physical-AI + foundations/operational + manufacturing/CMC + sometimes hcls/clinical-supply)
- **specialty-pharmacy network** (hcls/clinical-care + supply-chain/distribution + financial-services/clearing + foundations/operational)

This document captures the discipline that makes the compositions layer work without recreating the FHIR mistake at a higher level.

## What a composition is

A composition is **not** a workflow extension. A composition is **not** a deployment instance. A composition sits between them, as a class-level pattern that:

- **References (not redeclares) the workflow extensions and foundations it composes.** Smart-hospital references `foundations:physical-ai/Bed` (or whatever the class becomes); smart-hospital does not redeclare `Bed`. Compositions are reference graphs that point to other reference graphs.
- **Adds only the classes that genuinely emerge from the composition.** The classes that have operator-vocabulary meaning only when multiple underlying workflows are deployed together. The emergent-from-composition test (below) gates which classes belong.
- **Carries cross-layer SHACL invariants.** Constraints that validate the composition holds together. A smart-hospital `BedManagement` instance must reference a physical-AI `Sensor`, an operational `Asset`, and a clinical-care `Bed`; the SHACL invariants enforce that.
- **Lives in `compositions/<composition-name>/v1/`** with its own SKOS taxonomy (for emergent classes), SHACL shapes (mostly cross-layer invariants), spec page, and walkthrough.

A composition has its own working group. The composition WG coordinates across the underlying workflow-extension WGs whose work the composition composes. The composition WG owns the emergent classes and the cross-layer invariants; it does not own the underlying workflow classes.

## The emergent-from-composition discipline

For the compositions layer to add value without recreating the FHIR mistake, the discipline is tight. A class belongs in a composition only when it passes the **emergent-from-composition test**:

> A class belongs in a workflow extension if it can be authored without reference to any other workflow extension.
>
> A class belongs in a composition only if it requires reference to two or more workflow extensions (or to one workflow plus one or more foundations) to have operator-vocabulary meaning.

### Examples

**BedManagement at a smart hospital.** Qualifies as emergent. Requires reference to physical-AI (the bed sensor reporting occupancy and environmental state), operational (the bed as inventory item tracked across the facility), and clinical-care (the patient assigned to the bed). None of those layers alone captures what an operator means by "BedManagement" at a smart hospital. The composition is the only home.

**RoundingEncounter at a smart hospital.** Qualifies as emergent. Requires reference to physical-AI (the building knows which room the rounding team is in), operational (the schedule knows which team is rounding when), clinical-care (the encounter is the clinical work). Cross-layer named workflow.

**DischargeWorkflow at a smart hospital.** Qualifies as emergent. Clinical-care discharge order + operational transport scheduling + physical-AI bed release + sometimes clinical-research notification (if the patient is a study participant).

**Bed itself.** Does NOT qualify as emergent. Belongs in physical-AI (a physical asset with sensor connections) or operational (an inventory item) or both via Pattern B. The smart-hospital composition references `Bed`; it does not redeclare `Bed`.

**Patient, Visit, Encounter.** Do NOT qualify as emergent. All belong in clinical-care. The composition references them.

**HVACSystem.** Does NOT qualify as emergent. Belongs in physical-AI.

The discipline keeps compositions small. A typical composition probably carries ten to thirty emergent classes plus its cross-layer SHACL invariants. Most of what a composition's spec page describes is references to underlying workflow extensions, not new class declarations.

## Anticipated composition inventory

The list is open. A composition lifts when adopters need a packaged bundle, the emergent-from-composition test surfaces real classes, and a steward steps forward to run the composition WG. Compositions without adopter demand do not lift speculatively.

### Smart-X compositions

| Composition | Composes | Notes |
| --- | --- | --- |
| `compositions/smart-hospital/` | foundations/physical-AI + foundations/operational + hcls/clinical-care + (at AMCs) hcls/clinical-research | The reference smart-X composition. Informs smart-clinic, smart-cancer-center variants if they justify separate compositions; most variants are configuration of smart-hospital, not new compositions. |
| `compositions/smart-clinic/` | foundations/physical-AI + foundations/operational + hcls/clinical-care | Lifts when the operator-vocabulary differs meaningfully from smart-hospital (smaller scope, no inpatient beds, different visit cadence). |
| `compositions/smart-lab/` | foundations/physical-AI + foundations/operational + lab-ops (workflow extension TBD; possibly in HCLS or its own bucket) | Lifts when lab-ops as a workflow extension is scoped. Bo's 2026-05-14 note: smart-lab interfaces with smart-clinic within clinical research, so the composition relationship is real. |
| `compositions/smart-pharmacy/` | foundations/physical-AI + foundations/operational + hcls/clinical-care + supply-chain/distribution | Lifts when an adopter needs it. |
| `compositions/smart-factory/` | foundations/physical-AI + foundations/operational + manufacturing/<discrete-or-process-CMC> | Outside HCLS. Pattern is the same. |

### Non-smart compositions

| Composition | Composes | Notes |
| --- | --- | --- |
| `compositions/dct/` (decentralized clinical trial) | hcls/clinical-research + hcls/clinical-care + telehealth pattern + patient-portal pattern | Composes HCLS workflow extensions in a pattern that crosses traditional site boundaries. Telehealth and patient-portal may themselves be functional areas of clinical-care or their own workflows; TBD at composition WG activation. |
| `compositions/vbc/` (value-based care program) | hcls/clinical-care + foundations/operational + financial-services/clearing + analytics pattern | Composes care delivery with operational, financial, and analytics layers. |
| `compositions/registry-based-study/` | hcls/registries + hcls/clinical-research + (sometimes) hcls/clinical-care | Real-world evidence studies. |
| `compositions/specialty-pharmacy-network/` | hcls/clinical-care + supply-chain/distribution + financial-services/clearing + foundations/operational | Cross-bucket composition. |

### Pattern, not exhaustive

Future compositions emerge from adopter need. Each candidate composition gets evaluated against the emergent-from-composition test before it lifts. If the proposed composition has fewer than ~5 genuinely emergent classes, it's probably configuration of an existing composition, not a new composition.

## Composition WG structure

| Property | Calibration |
| --- | --- |
| Number of WGs per composition | One. Each composition has its own working group. |
| WG composition | Maintainers familiar with all the underlying workflow extensions the composition references. A smart-hospital WG includes members familiar with physical-AI, operational, clinical-care, and clinical-research. |
| Cross-composition coordination | Optional umbrella "compositions stewards" group, if cross-composition RFC volume warrants. Strawman: not yet. |
| Per-composition spec page | One. Mirrors the workflow-extension spec page structure (mission, what it composes, emergent classes, cross-layer invariants, deployment reference patterns, deferred items). |
| ADR ratification | Each composition's seed ratifies as its own ADR when activated. The compositions strategy itself ratifies as ADR-0024 (compositions namespace strategy). |

The composition WG's job is **coordination across underlying WGs** plus stewardship of the emergent classes. The underlying WGs (foundations/physical-AI, hcls/clinical-care, etc.) own their workflows; the composition WG owns the composition.

## Cross-layer SHACL invariants

A significant fraction of a composition's value is the cross-layer SHACL invariants it carries. These are constraints that span multiple workflow extensions and cannot live in any single workflow.

Example (smart-hospital, illustrative):

```
A smart-hospital:BedManagement SHACL shape requires:
  - exactly one reference to physical-AI:Bed (the physical bed object)
  - exactly one reference to operational:InventoryAsset (the bed-as-asset record)
  - 0 or 1 reference to clinical-care:PatientAssignment (current occupant)
  - the physical-AI:Bed.location must match the operational:InventoryAsset.location
  - the clinical-care:PatientAssignment.bedID must equal the physical-AI:Bed.bedID
```

This invariant cannot live in physical-AI alone (clinical-care doesn't exist there). Cannot live in clinical-care alone (physical-AI doesn't exist there). Cannot live in operational alone. It is a cross-layer constraint that belongs to the composition.

Adopters validate their deployed knowledge graphs against the composition's SHACL invariants. A smart-hospital instance graph that doesn't satisfy the BedManagement invariant is malformed at the composition level even if it satisfies every underlying workflow's invariants.

## Risks and how to mitigate them

| Risk | Failure mode | Mitigation |
| --- | --- | --- |
| **Composition bloat.** | smart-hospital, smart-AMC, smart-community-hospital, smart-children's-hospital, smart-cancer-center proliferate as separate compositions. | Discipline: a new composition lifts only when it produces emergent classes that don't fit in an existing composition. Most variants are configuration of smart-hospital, not new compositions. PR review enforces. |
| **The FHIR mistake at the composition layer.** | A composition starts redeclaring concepts that belong in an underlying workflow. The composition becomes an alternate-universe duplicate of physical-AI or clinical-care. | The emergent-from-composition test gates every composition class addition. PR review enforces. A future linter rule operationalizes the test when contribution volume warrants. |
| **WG coordination overhead.** | A smart-hospital WG coordinating four underlying WGs becomes the bottleneck for everything related to smart-hospital deployments. | Composition WG owns coordination across underlying WGs. Per-underlying-WG decisions stay with the underlying WG. The composition WG handles cross-cutting RFCs only. |
| **Specifications drift between composition and underlying workflows.** | A smart-hospital composition pins to specific versions of physical-AI, clinical-care, etc. When the underlying workflows release new versions, the composition's references break or silently misalign. | Composition reference graphs pin to specific versions of underlying workflows. Version upgrades land via PR that updates both the references and any affected emergent classes. SHACL invariants validate cross-version compatibility. |
| **Composition-specific features creep into underlying workflows.** | A specific smart-hospital deployment need leaks into physical-AI as a domain-specific class, dragging hospital-specific semantics into a workflow that serves multiple buckets. | Underlying workflow WGs reject domain-specific additions; the additions go to the composition or to a workflow-level Pattern B declaration where the cross is operator-grounded. |

## Composition lifecycle

Each composition progresses through five states (mirroring `governance/working-groups.md` for workflow extensions):

1. **Proposed.** A new composition is on the radar. RFC names the composition, identifies which workflow extensions it composes, names the initial maintainers, gives at least three candidate emergent classes that pass the test.
2. **Forming.** The composition WG has acceptance but has not yet shipped artifacts. Composition directory created when first artifact is ready. WG README documents intended scope.
3. **Active.** The composition has shipped its v1 spec page, its initial emergent class catalog, and at least one walkthrough. Adopters reference it.
4. **Mature.** Stable composition with steady release cadence. Adopters in production.
5. **Archived.** Composition dissolves. Underlying workflows continue; the composition's reference graph stays in the repo for historical reference.

## What this strategy commits the compositions layer to

- **Compositions are a fourth organizational layer above TOP Core.** Not workflow extensions; not deployment instances. Class-level patterns that reference workflow extensions and add only emergent classes.
- **The emergent-from-composition test is the discipline.** A class belongs in a composition only when it requires reference to two or more underlying workflow extensions to have operator-vocabulary meaning. Everything else stays in the underlying workflow.
- **Reference, never redeclare.** Compositions never duplicate classes from their underlying workflows. Linter rule (future) operationalizes the discipline.
- **One WG per composition.** Composition WG coordinates across underlying workflow-extension WGs.
- **Cross-layer SHACL invariants are the composition's other primary artifact.** Constraints that span multiple workflow extensions live in the composition, not in any single workflow.
- **Compositions lift on adopter demand.** A composition without adopter pull does not activate speculatively.
- **Strategy ratifies as ADR-0024 (compositions namespace strategy)** when the first composition WG activates. ADR number is a strawman.

## What this strategy does NOT do

- It does not author any composition. Each composition's emergent classes and SHACL invariants land in the composition's own seed and RFC.
- It does not finalize the namespace name. `compositions/` is the strawman; WG ratifies or overrides at first activation.
- It does not commit any specific composition to a ship date. Each composition lifts on its own timeline.
- It does not preclude future compositions. The list is open; new compositions land via RFC.
- It does not specify the relationship to TOP Core directly. Compositions reference workflow extensions; workflow extensions reference Core. The composition's relationship to Core is transitive.

## Open questions for working-group resolution

1. **Compositions namespace name.** Strawman: `compositions/`. WG ratifies or overrides at first activation.
2. **Compositions namespace scope.** Strawman: flat (`compositions/smart-hospital/`, `compositions/dct/`). Sub-namespaces (`compositions/smart-X/`, `compositions/programs/`) emerge only if the flat list grows unwieldy.
3. **Emergent-from-composition test enforcement.** Strawman: human review enforces; future linter operationalizes when contribution volume warrants.
4. **Composition WG structure.** Strawman: one WG per composition. Optional umbrella "compositions stewards" group if cross-composition RFC volume warrants.
5. **Cross-layer SHACL invariant authoring.** Strawman: composition WG authors them, in consultation with underlying-workflow WGs. RFC review for invariants that constrain underlying workflows tightly.
6. **Composition version pinning.** Strawman: composition v1 pins to specific versions of underlying workflows. Upgrade PRs land both at the composition and at any affected emergent classes.
7. **Composition-specific extension contracts.** ADR-0019's three flavors (Invariant, Tightenable, Additive) apply to Core properties. Do they apply to composition-emergent classes? Strawman: yes, same discipline. WG ratifies.
8. **Smart-lab specifically.** Bo's 2026-05-14 note flagged smart-lab as interfacing with smart-clinic within clinical research. Open whether lab-ops is a workflow extension under HCLS, a workflow extension in its own bucket, or a functional area within clinical-research. The composition activates after that question is settled.

## Pointers

- Strategy brief: `top-strategy-brief.md`
- Workflows strategy: `top-workflows-strategy.md`
- Foundations bucket strategy: `top-foundations-strategy.md`
- HCLS bucket strategy: `top-hcls-strategy.md`
- TOP Core: `core/v1/`, `taxonomy/taxonomy.ttl`
- Working groups: `governance/working-groups.md`

---

*Compositions strategy v1. The substance of this strategy becomes the basis for ADR-0024 (compositions namespace strategy) when the first composition WG activates. ADR number is a strawman.*
