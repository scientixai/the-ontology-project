# TOP Taxonomy v1

> Classification before construction. The taxonomy comes first; the ontology builds on it. This document is the corrected classification scheme that should have been written before the first lift; written now after eight reference-graph entities surfaced the architectural ambiguities.

## What this fixes

The original namespace structure had two compounding errors:

1. **`top:` was bound to clinical-trials.** "TOP" stands for *The Ontology Project* — the framework. A prefix called `top:` should belong to the project, not to one of its reference graphs. The prefix label said "top is clinical"; the meaning said "top is the whole project." Mismatch.
2. **The reference graphs were imagined as sibling industry-domains.** Like FIWARE Smart Data Models — Healthcare, Manufacturing, Supply Chain, Smart City as walled-off siblings. But healthcare CONTAINS manufacturing (pharma), supply chain (drug distribution), and regulatory (FDA, EMA) — and those exist outside healthcare too. Sibling-by-industry collapses under the simplest test: a smart hospital sponsoring a clinical trial uses both clinical-research and care-delivery workflows simultaneously over the same substrate.

The corrected taxonomy is layered, not siblinged: a single commons substrate (universal cross-cutting concepts) plus composable workflow extensions (workflow-specific concepts that compose on top of the substrate). Workflows are NOT mutually exclusive — a real-world deployment uses as many extensions as it needs, all over the same commons.

## The architecture

```
TOP (the project framework — top.scientix.ai)
  │
  └── Commons substrate (universal layer — topc:)
        │
        ├── Person, Organization, Site, Document, Equipment, System, Log,
        │   StorageLocation, Credential, Visit, Event, OversightBody
        │   (12 substrate primitives)
        │
        └── Visit sub-concepts (universal across workflows)
            ├── Activity (the universal work unit)
            ├── Task (the universal data-capture leaf)
            └── VisitObservation (operator narrative)

  └── Workflow extensions (composable; not mutually exclusive)
        │
        ├── Clinical Research (topcr:) — current, in flight
        │     ├── Sponsor, Study, Participant, Recruit, InvestigationalProduct,
        │     │   StudySite (6 top-level concepts)
        │     ├── Study sub-objects: Protocol, Arm, ScheduleOfAssessments,
        │     │   Endpoint, InclusionCriterion, ExclusionCriterion, VisitDefinition (7)
        │     ├── Participant sub-objects: InformedConsent, ScreeningRecord,
        │     │   EnrollmentRecord, WithdrawalRecord (4)
        │     └── InvestigationalProduct sub-objects: Lot, Kit (2)
        │
        ├── Care Delivery (topcd:) — future
        │     Patient, Encounter, Order, Diagnosis, Discharge, ...
        │
        ├── Manufacturing (topmfg:) — future
        │     ManufacturingBatch, BatchRecord, ProcessParameters, ...
        │
        └── Supply Chain (topsc:) — future
              Shipment, CustodyHandoff, Carrier, ...
```

## URI / prefix conventions

```
top.scientix.ai/v1#                       ← project-level concepts (top:)
top.scientix.ai/commons/v1#               ← universal substrate (topc:)
top.scientix.ai/clinical-research/v1#     ← clinical research workflow extension (topcr:)
top.scientix.ai/care-delivery/v1#         ← future workflow extension (topcd:)
top.scientix.ai/manufacturing/v1#         ← future workflow extension (topmfg:)
top.scientix.ai/supply-chain/v1#          ← future workflow extension (topsc:)
```

Three rules:

1. **`top:` is reserved for project-level concepts only** (the taxonomy itself, top concepts, layer markers). It is NOT a domain prefix.
2. **Commons gets the `topc:` prefix** with IRI `top.scientix.ai/commons/v1#`. One commons. Universal substrate primitives.
3. **Each workflow extension gets its own prefix** with IRI `top.scientix.ai/{workflow-name}/v1#`. Workflow names are kebab-case (`clinical-research`, `care-delivery`, `supply-chain`). Each extension is self-contained but composes on top of commons.

The path `/onto/` is removed — operator-grounded over jargon-y.

## The classification rule (substrate-primitive test)

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

The discipline is reactive: only lift entities when a real operator workflow forces them, and only put them in commons if they actually pass the substrate-primitive test. This avoids over-pre-modeling and avoids the FIWARE mistake.

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

The hospital doesn't *belong* to one reference graph. The same Organization, Person, Site, Visit, Event entities serve multiple workflows simultaneously. Roles are role-relationships pointing at the same substrate entities.

This is exactly the pattern already established with Sponsor (per-Organization-per-Study role) and the IIT case (same Organization plays managesSite + playsSponsorRole). We just hadn't generalized it to the project taxonomy.

## Migration from current state

The current source intermediate (v0.6.0-strawman) carries:

- `top:` prefix → `https://top.scientix.ai/onto/clinical/v1#` (mislabeled clinical)
- `topc:` prefix → `https://top.scientix.ai/onto/commons/v1#` (correct intent, wrong path)

Migration to corrected taxonomy:

| Current | Corrected |
|---|---|
| `top:Sponsor` | `topcr:Sponsor` (clinical-research extension) |
| `top:Study` | `topcr:Study` (clinical-research extension) |
| `top:Participant` | `topcr:Participant` (clinical-research extension) |
| `top:Recruit` | `topcr:Recruit` (clinical-research extension) |
| `top:InvestigationalProduct` | `topcr:InvestigationalProduct` (clinical-research extension) |
| **`top:Site`** | **`topc:Site`** (moves to commons — universal) |
| **`top:Visit`** | **`topc:Visit`** (moves to commons — universal) |
| **`top:OversightBody`** | **`topc:OversightBody`** (moves to commons — universal) |
| Future `top:Event` (was about to lift) | **`topc:Event`** (commons — universal) |
| `topc:StudySite` | **`topcr:StudySite`** (moves to clinical-research extension — clinical-research-specific despite being structurally a horizontal) |
| `topc:Organization` | `topc:Organization` (already correct) |
| `topc:Document` | `topc:Document` (already correct) |
| `topc:Person` | `topc:Person` (already correct) |
| `topc:System` / `topc:Log` / `topc:Equipment` / `topc:StorageLocation` / `topc:Credential` | unchanged (already correct) |

**IRI path correction**: `/onto/clinical/v1#` → `/clinical-research/v1#`; `/onto/commons/v1#` → `/commons/v1#` (drops `/onto/`).

## Migration plan

Three sequential PRs:

1. **PR — Taxonomy artifacts (this PR)** — TAXONOMY.md prose, taxonomy.ttl SKOS canonical, taxonomy.csv companion. No code changes; foundational documentation that captures the corrected classification scheme.
2. **PR — Namespace refactor (mechanical)** — rename prefixes (`top:` → `topcr:` for clinical research), reassign Site/Visit/OversightBody to commons, move StudySite to clinical-research extension, drop `/onto/` from IRI paths, bump version to v0.7.0. Source intermediate, emitters, examples, spec docs, ROADMAP, FIRST-PRINCIPLES all updated lockstep. The substrate decisions don't change; only namespace labels.
3. **PR — Event lift as `topc:Event`** — proceed with the original Event plan but in correct namespace as a commons substrate primitive with cross-realm posture.

## Working with the SKOS file

The canonical taxonomy lives in `taxonomy/taxonomy.ttl` (SKOS Turtle, importable into TermBoard, PoolParty, Synaptica, Protégé, any SKOS-aware tool).

A flat CSV companion (`taxonomy/taxonomy.csv`) is provided for spreadsheet-based review and lighter-weight import.

The Markdown narrative (this file) is the human-readable accompaniment; it should track changes to the SKOS canonically.

**Contributor workflow** when proposing taxonomy changes:
1. Edit the SKOS Turtle in TermBoard (or your preferred tool); export back to `taxonomy/taxonomy.ttl`
2. Regenerate the CSV companion (a small script could automate this; for now, manual sync)
3. Update TAXONOMY.md prose to reflect the change
4. Open a PR with all three lockstep changes
5. The substrate-primitive test (does this concept belong in commons or in a workflow extension?) is the discipline; cite it in the PR description

## Forward-looking — adding a new workflow extension

When TOP-Manufacturing or TOP-CareDelivery or TOP-SupplyChain comes alive:

1. **Define the prefix and IRI** (`topmfg:` at `top.scientix.ai/manufacturing/v1#`)
2. **Extend the SKOS taxonomy** with the workflow's top concepts under `top:WorkflowExtensions`
3. **Add concepts** for each workflow-specific top-level entity, with broader = the workflow concept
4. **Reference commons concepts** for cross-cutting reuse (the Manufacturing workflow uses `topc:Site`, `topc:Equipment`, `topc:Event`, etc.)
5. **Document the substrate-primitive test outcomes** for the new entities — what's workflow-specific (extension), what's cross-cutting and might bubble up to commons

The architecture handles cross-workflow integration naturally: a hospital with a manufacturing pharmacy that also runs trials uses commons + clinical-research + manufacturing + (future) care-delivery extensions all over the same Organization, Person, Site, Equipment, Event substrate. No walls.

## Pointers

- [`taxonomy/taxonomy.ttl`](taxonomy/taxonomy.ttl) — SKOS Turtle canonical (importable into TermBoard, PoolParty, Synaptica, Protégé)
- [`taxonomy/taxonomy.csv`](taxonomy/taxonomy.csv) — CSV companion (spreadsheet-friendly review)
- [`FIRST-PRINCIPLES.md`](FIRST-PRINCIPLES.md) — design rules; the universal-substrate posture is the discipline that grounds this taxonomy
- [`MANIFESTO.html`](MANIFESTO.html) — the philosophical foundation
- [`ROADMAP.md`](ROADMAP.md) — build sequence; lift order respects the taxonomy
- The discipline applied here: classification BEFORE construction. The mistake we're correcting is having skipped this step at the start. Better late than later.
