# TOP Taxonomy v1

> Classification before construction. The taxonomy comes first; the ontology builds on it. This document is the corrected classification scheme that should have been written before the first lift; written now after eight reference-graph entities surfaced the architectural ambiguities.

## What this fixes

The original namespace structure had two compounding errors:

1. **`top:` was bound to clinical-trials.** "TOP" stands for *The Ontology Project* — the framework. A prefix called `top:` should belong to the project, not to one of its reference graphs. The prefix label said "top is clinical"; the meaning said "top is the whole project." Mismatch.
2. **The reference graphs were imagined as sibling industry-domains.** Like FIWARE Smart Data Models — Healthcare, Manufacturing, Supply Chain, Smart City as walled-off siblings. But healthcare CONTAINS manufacturing (pharma), supply chain (drug distribution), and regulatory (FDA, EMA) — and those exist outside healthcare too. Sibling-by-industry collapses under the simplest test: a smart hospital sponsoring a clinical trial uses both clinical-research and care-delivery workflows simultaneously over the same TOP.

The corrected taxonomy is layered, not siblinged: a single TOP Primitives (universal cross-cutting concepts) plus composable workflow extensions (workflow-specific concepts that compose on top of TOP). Workflows are NOT mutually exclusive — a real-world deployment uses as many extensions as it needs, all over the same commons.

## The architecture (Option B — commons holds universal primitive shapes; workflows extend with specialization)

After working through whether `clinical-research/visit` and `healthcare/visit` both feel right (they do — same word, different shapes per workflow), then whether Document's primitive attrs are durable across every domain (yes — id, title, version, status, dates, retention are universal), the architecture commits to **Option B properly scoped**:

- **Commons holds universal primitive shapes** for entities with attributes durable across every workflow. Most entities qualify at the primitive level — Document, Equipment, System, Log, StorageLocation, Credential, Visit, Event, Site, OversightBody, Activity, Task, VisitObservation, Person, Organization. Each has a universal primitive shape that any workflow can use directly.
- **Workflow extensions specialize via subClassOf** when they need workflow-specific attributes. The clinical-research workflow adds essentialRecordPurpose to Document, visitDay+visitWindow to Visit, CTCAE grade to Event, etc.
- **Workflow-native entities** (no commons supertype) live in workflow extensions when the concept itself only exists in that workflow — Sponsor, Study, Participant, Recruit, InvestigationalProduct in clinical research.
- Cross-workflow queries against the commons supertype find every workflow's specialized shape via subClassOf inheritance.

```
TOP (the project framework — top.scientix.ai)
  │
  └── Commons (universal layer — topc:) — 15 entities WITH SHAPE
        │
        ├── Identity primitives (truly identical across workflows):
        │   topc:Person, topc:Organization
        │
        └── Operational primitives (universal core attrs; workflows specialize):
            topc:Site, topc:Visit, topc:Event, topc:OversightBody,
            topc:Document, topc:Equipment, topc:System, topc:Log,
            topc:StorageLocation, topc:Credential,
            topc:Activity, topc:Task, topc:VisitObservation

  └── Workflow extensions (composable; not mutually exclusive)
        │
        ├── Clinical Research (topcr:) — current, in flight
        │     │
        │     ├── SPECIALIZATIONS that subClassOf commons (add workflow-specific attrs):
        │     │   topcr:Document   (adds ICH E6(R3) Appendix C essentialRecordPurpose
        │     │                     + responsibleParty + isfSection + etmfLocation
        │     │                     + clinical-research documentType enum values)
        │     │   topcr:Equipment  (adds equipmentBinding enum)
        │     │   topcr:System     (adds three-axis pattern operatedBy/usedBy/oversightHeldBy)
        │     │   topcr:Log        (adds clinical-research log-type specifics)
        │     │   topcr:StorageLocation (adds temperature / sample-storage specifics)
        │     │   topcr:Credential (adds GCP/CLIA/IATA-specific credential types)
        │     │   topcr:Visit      (adds visitNumber, visitDay, visitWindow, definedBy,
        │     │                     forParticipant, forStudySite, protocolDeviationCode)
        │     │   topcr:Event      (adds CTCAE grade, expedited reporting, ICH E2A
        │     │                     reportability, eventCategory enum AE/SAE/Deviation/etc.)
        │     │   topcr:Site       (adds SFQ feasibility profile)
        │     │   topcr:OversightBody (adds IRB-registration / DSMB-charter specifics)
        │     │   topcr:Activity   (adds biomedicalConceptCode → COSMoS BC catalog)
        │     │   topcr:Task       (adds biomedicalConceptCode)
        │     │   topcr:VisitObservation (adds Path C Event-escalation specifics)
        │     │
        │     └── CLINICAL-RESEARCH-NATIVE entities (no commons supertype —
        │         these concepts only exist in clinical-research workflow):
        │         topcr:Sponsor, topcr:Study, topcr:Participant, topcr:Recruit,
        │         topcr:InvestigationalProduct, topcr:StudySite
        │         + Study sub-objects (Protocol, Arm, SOA, Endpoint, InclusionCriterion,
        │           ExclusionCriterion, VisitDefinition)
        │         + Participant sub-objects (InformedConsent, ScreeningRecord,
        │           EnrollmentRecord, WithdrawalRecord)
        │         + InvestigationalProduct sub-objects (Lot, Kit)
        │
        ├── Care Delivery (topcd:) — future
        │     SPECIALIZATIONS (topcd:Visit subClassOf topc:Visit; topcd:Event;
        │     topcd:OversightBody for P&T committees)
        │     + CARE-DELIVERY-NATIVE (topcd:Patient, topcd:Order, topcd:Diagnosis,
        │       topcd:Discharge)
        │
        ├── Manufacturing (topmfg:) — future
        │     SPECIALIZATIONS (topmfg:InspectionVisit subClassOf topc:Visit;
        │     topmfg:Event for OOS / Batch Failure / Contamination;
        │     topmfg:Site for manufacturing plants)
        │     + MANUFACTURING-NATIVE (ManufacturingBatch, BatchRecord,
        │       ProcessParameters)
        │
        └── Supply Chain (topsc:) — future
              SPECIALIZATIONS (topsc:DeliveryVisit subClassOf topc:Visit;
              topsc:Event for cold-chain excursions; topsc:Warehouse subClassOf
              topc:Site)
              + SUPPLY-CHAIN-NATIVE (Shipment, CustodyHandoff, Carrier)
```

**The pattern in plain language**: Commons gives you usable entities at the primitive-attributes level — a `topc:Document` instance is a real, queryable, validatable thing. Workflow extensions ADD attributes by subclassing. A clinical-research deployment uses `topc:Document` directly when the universal attrs are sufficient, or `topcr:Document subClassOf topc:Document` when it needs `essentialRecordPurpose`. Cross-workflow queries against `topc:Document` find every workflow's specialized Document via subClassOf inheritance.

**This is the FHIR-base-resource + profile pattern.** FHIR Encounter is a usable resource with universal attrs; US Core / AU Core / IPS profiles extend it with regional/jurisdictional specifics. TOP commons + workflow extensions follows the same pattern.

**Two kinds of entities exist in workflow extensions**:
1. **Specialization shapes that subClassOf a commons primitive** — when the primitive shape is universal but workflow needs additional attributes (Document, Equipment, Visit, Event, etc.).
2. **Workflow-native entities** (no commons supertype) — when the concept itself only exists in that workflow (Sponsor, Study, Participant, etc.).

**The same example reads consistently**: a smart hospital sponsoring a clinical trial uses TOP Primitives (`topc:Person`, `topc:Organization`, `topc:Site`, `topc:Visit`, `topc:Event`, `topc:Document`, `topc:Equipment`, etc. — directly usable) + clinical-research workflow extensions (`topcr:Sponsor`, `topcr:Study`, `topcr:Visit subClassOf topc:Visit` for the protocol-specific attrs, etc.) + (future) care-delivery workflow extensions (`topcd:Patient`, `topcd:Visit subClassOf topc:Visit` for billing/encounter specifics). Same Visit *primitive*; multiple specialized shapes; cross-workflow queries find them all.

## URI / prefix conventions

```
top.scientix.ai/v1#                       ← project-level concepts (top:)
top.scientix.ai/commons/v1#               ← TOP Primitives (topc:)
top.scientix.ai/clinical-research/v1#     ← clinical research workflow extension (topcr:)
top.scientix.ai/care-delivery/v1#         ← future workflow extension (topcd:)
top.scientix.ai/manufacturing/v1#         ← future workflow extension (topmfg:)
top.scientix.ai/supply-chain/v1#          ← future workflow extension (topsc:)
```

Three rules:

1. **`top:` is reserved for project-level concepts only** (the taxonomy itself, top concepts, layer markers). It is NOT a domain prefix.
2. **Commons gets the `topc:` prefix** with IRI `top.scientix.ai/commons/v1#`. One commons. TOP Primitives.
3. **Each workflow extension gets its own prefix** with IRI `top.scientix.ai/{workflow-name}/v1#`. Workflow names are kebab-case (`clinical-research`, `care-delivery`, `supply-chain`). Each extension is self-contained but composes on top of commons.

The path `/onto/` is removed — operator-grounded over jargon-y.

## The classification rule (TOP Primitive test)

For every entity in TOP, the inclusion test for commons:

> **Do operators in workflows beyond a single domain recognize this concept as a first-class thing?**

If yes, commons. If no, workflow extension.

| Entity | Test outcome | Placement |
|---|---|---|
| Person | Yes — every workflow has people | Commons |
| Organization | Yes — every workflow has organizations | Commons |
| Site | Yes — hospitals, factories, warehouses, research facilities all have "sites" | Commons |
| Document | Yes — every regulated workflow has documents | Commons |
| Equipment | Yes — every operational workflow has equipment | Commons |
| Visit | Yes — patient visits, audit visits, delivery visits, manufacturing site visits | Commons |
| Event | Yes — AE, OOS, code blue, temperature excursion, regulatory finding | Commons |
| OversightBody | Yes — IRBs, P&T committees, audit boards, ethics committees | Commons |
| **Sponsor** | No — sponsor-as-per-Org-per-Study is clinical-research-specific | Clinical Research |
| **Study** | No — research study with protocol/arms is clinical-research-specific | Clinical Research |
| **Participant** | No — trial-subject role is clinical-research-specific | Clinical Research |
| **InvestigationalProduct** | No — IND-track regulatory specifics are clinical-research-specific | Clinical Research |
| **StudySite** | No — per-Study site role is clinical-research-specific | Clinical Research |

The discipline is reactive: only lift entities when a real operator workflow forces them, and only put them in commons if they actually pass the TOP Primitive test. This avoids over-pre-modeling and avoids the FIWARE mistake.

## Workflows compose — the smart-hospital-sponsors-a-trial test

The classification was forced by a simple test: what happens when a smart hospital sponsors a clinical trial? In sibling-domain models (FIWARE, my prior proposal), the hospital straddles two walled-off domains and every cross-domain query becomes integration work.

In composable workflows on a single commons:

```
Organization:mskcc                        ← topc:Organization (commons)
  ├── plays role: Sponsor:mskcc-iit-001   ← topcr:Sponsor (clinical-research)
  ├── plays role: Site:mskcc-main         ← topc:Site (commons)
  └── plays role: care-delivery facility  ← topcd:* (future, when care-delivery extension lifts)

Person:dr-kim                             ← topc:Person (commons)
  ├── plays role: Investigator on Sponsor ← clinical-research role context
  ├── plays role: Treating Physician      ← care-delivery role context (future)
  └── plays role: Hospital Staff          ← care-delivery role context (future)
```

The hospital doesn't *belong* to one reference graph. The same Organization, Person, Site, Visit, Event entities serve multiple workflows simultaneously. Roles are role-relationships pointing at the same TOP entities.

This is exactly the pattern already established with Sponsor (per-Organization-per-Study role) and the IIT case (same Organization plays managesSite + playsSponsorRole). We just hadn't generalized it to the project taxonomy.

## Migration from current state (Option B)

The current source intermediate (v0.6.0-strawman) carries:

- `top:` prefix → `https://top.scientix.ai/onto/clinical/v1#` (mislabeled clinical)
- `topc:` prefix → `https://top.scientix.ai/onto/commons/v1#` (correct intent, wrong path)

Migration under Option B is more nuanced than the prior single-prefix shuffle. Workflow-specific SHAPES move to `topcr:`; the corresponding commons CONCEPTS get added to `topc:` (vocabulary-only; SKOS).

| Current | Corrected | Type of move |
|---|---|---|
| `top:Sponsor` | `topcr:Sponsor` | Clinical-research-native (no commons supertype) |
| `top:Study` | `topcr:Study` | Clinical-research-native |
| `top:Participant` | `topcr:Participant` | Clinical-research-native |
| `top:Recruit` | `topcr:Recruit` | Clinical-research-native |
| `top:InvestigationalProduct` | `topcr:InvestigationalProduct` | Clinical-research-native |
| `top:Site` | `topcr:Site subClassOf topc:Site` | Shape stays in clinical-research; commons gets concept |
| `top:Visit` | `topcr:Visit subClassOf topc:Visit` | Shape stays in clinical-research; commons gets concept |
| `top:OversightBody` | `topcr:OversightBody subClassOf topc:OversightBody` | Shape stays in clinical-research; commons gets concept |
| Future `top:Event` (about to lift) | `topcr:Event subClassOf topc:Event` | Shape lifts in clinical-research; commons concept anchors it |
| `topc:StudySite` | `topcr:StudySite` | Move from commons to clinical-research-native |
| `topc:Document` | `topcr:Document subClassOf topc:Document` | Shape moves to clinical-research; commons keeps concept |
| `topc:Equipment` | `topcr:Equipment subClassOf topc:Equipment` | Shape moves; commons keeps concept |
| `topc:System` | `topcr:System subClassOf topc:System` | Shape moves; commons keeps concept |
| `topc:Log` | `topcr:Log subClassOf topc:Log` | Shape moves; commons keeps concept |
| `topc:StorageLocation` | `topcr:StorageLocation subClassOf topc:StorageLocation` | Shape moves; commons keeps concept |
| `topc:Credential` | `topcr:Credential subClassOf topc:Credential` | Shape moves; commons keeps concept |
| **`topc:Person`** | **`topc:Person`** (stays as commons class with shape) | Truly identical attrs across workflows; commons-with-shape |
| **`topc:Organization`** | **`topc:Organization`** (stays as commons class with shape) | Truly identical attrs across workflows; commons-with-shape |

**Sub-object shapes** (Activity, Task, VisitObservation, Protocol, Arm, etc.) follow the same pattern: workflow-specific shapes in `topcr:` with subClassOf to commons concepts where applicable.

**IRI path correction**: `/onto/clinical/v1#` → `/clinical-research/v1#`; `/onto/commons/v1#` → `/commons/v1#` (drops `/onto/`).

**What TOP looks like in practice**:

- **Commons-with-shape**: 2 entities (Person, Organization) — usable directly from `topc:`
- **Commons concepts only** (vocabulary anchors): 13 — Visit, Event, Site, OversightBody, Activity, Task, VisitObservation, Document, Equipment, System, Log, StorageLocation, Credential
- **Clinical-research workflow-native entities**: 6 top-level + 13 sub-objects = 19 entities, all in `topcr:` with no commons supertype
- **Clinical-research workflow-shaped extensions** (subClassOf commons concepts): 13 entities in `topcr:` matching the 13 commons concepts

Total clinical-research workflow entity count: 19 native + 13 shape extensions = 32. Plus 2 commons-with-shape (Person, Organization) the workflow uses directly. Plus the 13 commons concepts the workflow's shapes reference.

## Migration plan

Three sequential PRs:

1. **PR — Taxonomy artifacts (this PR)** — TAXONOMY.md prose, taxonomy.ttl SKOS canonical, taxonomy.csv companion. No code changes; foundational documentation that captures the corrected classification scheme.
2. **PR — Namespace refactor (mechanical)** — rename prefixes (`top:` → `topcr:` for clinical research), reassign Site/Visit/OversightBody to commons, move StudySite to clinical-research extension, drop `/onto/` from IRI paths, bump version to v0.7.0. Source intermediate, emitters, examples, spec docs, ROADMAP, FIRST-PRINCIPLES all updated lockstep. TOP decisions don't change; only namespace labels.
3. **PR — Event lift as `topc:Event`** — proceed with the original Event plan but in correct namespace as a TOP Primitives primitive with cross-realm posture.

## Working with the SKOS file

The canonical taxonomy lives in `taxonomy/taxonomy.ttl` (SKOS Turtle, importable into TermBoard, PoolParty, Synaptica, Protégé, any SKOS-aware tool).

A flat CSV companion (`taxonomy/taxonomy.csv`) is provided for spreadsheet-based review and lighter-weight import.

The Markdown narrative (this file) is the human-readable accompaniment; it should track changes to the SKOS canonically.

**Contributor workflow** when proposing taxonomy changes:
1. Edit the SKOS Turtle in TermBoard (or your preferred tool); export back to `taxonomy/taxonomy.ttl`
2. Regenerate the CSV companion (a small script could automate this; for now, manual sync)
3. Update TAXONOMY.md prose to reflect the change
4. Open a PR with all three lockstep changes
5. The TOP Primitive test (does this concept belong in commons or in a workflow extension?) is the discipline; cite it in the PR description

## Forward-looking — adding a new workflow extension

When TOP-Manufacturing or TOP-CareDelivery or TOP-SupplyChain comes alive:

1. **Define the prefix and IRI** (`topmfg:` at `top.scientix.ai/manufacturing/v1#`)
2. **Extend the SKOS taxonomy** with the workflow's top concepts under `top:WorkflowExtensions`
3. **Add concepts** for each workflow-specific top-level entity, with broader = the workflow concept
4. **Reference commons concepts** for cross-cutting reuse (the Manufacturing workflow uses `topc:Site`, `topc:Equipment`, `topc:Event`, etc.)
5. **Document the TOP Primitive test outcomes** for the new entities — what's workflow-specific (extension), what's cross-cutting and might bubble up to commons

The architecture handles cross-workflow integration naturally: a hospital with a manufacturing pharmacy that also runs trials uses commons + clinical-research + manufacturing + (future) care-delivery extensions all over the same Organization, Person, Site, Equipment, Event TOP. No walls.

## Pointers

- [`taxonomy/taxonomy.ttl`](taxonomy/taxonomy.ttl) — SKOS Turtle canonical (importable into TermBoard, PoolParty, Synaptica, Protégé)
- [`taxonomy/taxonomy.csv`](taxonomy/taxonomy.csv) — CSV companion (spreadsheet-friendly review)
- [`FIRST-PRINCIPLES.md`](FIRST-PRINCIPLES.md) — design rules; the universal-pattern posture is the discipline that grounds this taxonomy
- [`MANIFESTO.html`](MANIFESTO.html) — the philosophical foundation
- [`ROADMAP.md`](ROADMAP.md) — build sequence; lift order respects the taxonomy
- The discipline applied here: classification BEFORE construction. The mistake we're correcting is having skipped this step at the start. Better late than later.
