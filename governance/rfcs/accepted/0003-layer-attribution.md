# RFC 0003: Layer attribution — the two-axis reconciliation (KIND × TIER) and disposition of the clinical-research object catalog

- **Status:** Accepted (ratified 2026-07-10, ADR-0028)
- **Date:** 2026-07-10
- **Authors:** @bo-lora (convener)
- **Affected groups:** Core Stewards, HCLS umbrella WG (forming), Clinical Research WG
- **Required quorum:** Core stewards + one Clinical Research WG maintainer
- **Supersedes:** n/a — depends on [ADR-0026](../../decision-log.md) (entity-view corpus); unblocks [RFC 0002](0002-repository-federation.md)
- **ADR on acceptance:** ADR-0028

## Motivation

The generated entity-view corpus (ADR-0026, 80 objects) is a faithful OOUX snapshot of the operator's world — and, exactly because it is faithful, it is **layer-blind and kind-blind**. It minted concepts a parent layer already owns (`cr:Person` shadowing `hcls:Person`; `cr:Date`, `cr:Tag`, `cr:System` re-minting Core primitives) and reified attributes, relations, and context into classes. The full analysis is in [`docs/ooux-layer-blindness.md`](../../docs/ooux-layer-blindness.md).

Two forces make this a **blocking** pre-federation item, not a cleanup:

1. **The extension contract forbids it.** Redefining a parent concept violates open-core / constrained-extension (ADR-0019). [RFC 0002](0002-repository-federation.md) carves `clinical-research` into a repo that *pins* Core and the HCLS base; a module that re-mints the primitives it inherits cannot pass conformance CI. The layer-discipline gate (`tools/lint_layering.py --strict`) must reach **zero** unresolved items before the carve.
2. **The premise was too narrow.** Reviewing the finding, Jessica Talisman added the decisive correction:

   > "First name, last name, employee are not classes or objects — they are properties. **Context is a property, not an object.** Classes are the TBox, which is small; properties represent the data — the ABox." — [*Context Is a Property, Not an Object*](https://jessicatalisman.substack.com/p/context-is-a-property-not-an-object)

   The reconciliation is not "which layer owns this class." It is first "is this a class at all?"

This RFC ratifies the two-axis reconciliation already built (`tools/lint_layering.py`, `cr-domain/views/tier-map.json`, the extension-contract § "Layer discipline") and **decides the 66 flagged objects**.

## Proposal

### 1. Ratify the two-axis reconciliation as a required pipeline stage

Between an object catalog and class-minting, every catalog item passes two axes, in order:

- **KIND** — a class (an object; the TBox, small), or a property / relation / context (the ABox, where the data lives)? A property reified as a class is **demoted**, not tiered.
- **TIER** — *only if a class* — which layer owns it: `dedupe` (bind to an existing parent), `subclass` (mint native, `subClassOf` a named parent), or `promote` (a genuine gap in a parent layer).

Enforcement is machine-checked and already merged: the linter flags **reify**, **shadow**, and **orphan**; the disposition is recorded per object in `tier-map.json`; the gate blocks any untriaged term. This RFC makes the doctrine normative for every domain, not just clinical-research.

### 2. Disposition of the 66 flagged clinical-research objects

The machine-readable record is [`cr-domain/views/tier-map.json`](../../cr-domain/views/tier-map.json). Summary:

**KIND — demote (5): properties/relations reified as objects.**

| Object | Kind | Re-model as |
| --- | --- | --- |
| `Date` | property | a datetime value on the milestone/subject it dates |
| `Tag` | property | an annotation value / `skos:Concept` |
| `TherapeuticArea` | property | a classification value (`skos:Concept`) |
| `PersonRole`, `UserRole` | relation | a role is a relationship/context, not an object (ADR-0020/0022) |

**TIER — dedupe (9): exact shadows bound to the existing parent.**

`Person`→`hcls:Person`, `System`→`top:System`, `Log`→`top:Log`, `Document`→`top:Document`, `Equipment`→`top:Equipment`, `Credential`→`top:Credential`, `Milestone`→`top:Milestone`, `Attestation`→`top:Attestation`, `Window`→`top:Window`.

**TIER — subclass: domain-native, `subClassOf` a named existing parent.** The nearest-category rule resolves the bulk without any new Core class:

| Parent | Objects (subclass of) |
| --- | --- |
| `top:Location` | Region, Country, StorageLocation |
| `top:Log` | Audit, AuditTrailEntry, CommunicationLog |
| `top:Schedule` | ScheduleOfAssessments, StudyTimeline |
| `top:Document` | Amendment, CRF, Contract, Report, RegulatorySubmission, TrainingRecord, CSR, Protocol |
| `top:Constraint` | InclusionCriteria, ExclusionCriteria |
| `top:Outcome` | Deviation, Discrepancy, Finding, ScreenFail, OtherClinicalEvent, SafetySignal |
| `top:Evidence` | InterimAnalysis, DataQualityMetric, StudyPerformanceMetric, EnrollmentForecast |
| `top:Activity` | MonitoringVisit, DataTransfer, AnalysisRequest |
| `top:Artifact` | ServiceConfiguration, SystemConfiguration |
| `top:Scope` | Plan |
| `top:Equipment` | InvestigationalDevice |
| `hcls:Organization` | OversightBody, RegulatoryAuthority, SiteNetwork |
| `hcls:Observation` | LabResults |
| `hcls:Specimen` | Sample |
| `hcls:Consent` | InformedConsent |
| `hcls:HealthcareFacility` | Site |
| `hcls:MedicinalProduct` | ConcomitantMedication |
| `hcls:Action` | Task, ActionItem |

**TIER — promote (1 genuine): a real mid-layer gap.**

| Object | Home | Justification |
| --- | --- | --- |
| `Questionnaire` | **`hcls:Questionnaire`** (new HCLS-base class) | Recurs across clinical-research, clinical-care, and registries (rule of three); aligns FHIR `Questionnaire`. |

**Deferred — out of clinical-research scope (3):**

| Object | Disposition |
| --- | --- |
| `Budget`, `BudgetForecast`, `Payment` | A future **`financial-services` bucket** owns these (per `top-foundations`/`top-compositions` strategy). Not Core, not CR. Removed from the CR object catalog; re-enter when the finance bucket forms. |

**Held for a dedicated decision (2):**

| Object | Why held |
| --- | --- |
| `Participant` | The pseudonymous-subject **boundary** — routes to `hcls:Person` only through the attested `cr:Enrollment` bridge; must not be naively merged. Resolved in the participant/PII sub-decision, not here. |
| `Service`, `AnalysisService` | Software-service tier is unsettled; decide with the smart-X composition work, not CR-core. |

### 3. The headline result: the TBox does not grow — it shrinks

Applying KIND first changes the answer. The original tier-only reading produced a "promote to a new Core class" pile (Date, Tag, Budget, metrics…). After KIND:

- Date, Tag, TherapeuticArea, the roles → **properties** (leave the TBox entirely).
- Metrics, analyses, events → **subclass existing Core categories** (no new class).
- Finance → **out of scope** (a different bucket).
- **Exactly one** genuine mid-layer addition: `hcls:Questionnaire`.

Core gains nothing; the HCLS base gains one class; ~5 objects leave the class model for the property layer. This is precisely the "TBox is small; the ABox is the data" outcome the KIND axis predicts.

### 4. Author tiered, generate flat

`cr-domain/tools/gen_entity_views.py` gains a `tier-map.json` dependency and changes its emit rule:

- `dedupe`/`subclass` → the view's `sh:targetClass` is the **resolved parent**; the view carries only the object's **delta** properties (inherited attributes come from the parent-tier view via SHACL `sh:targetClass` propagation through `subClassOf`).
- `demote` → **no EntityView**; the item becomes a property shape on the object it belongs to.
- `promote`/deferred/held → excluded from the CR corpus until resolved.

The corpus is regenerated from the catalog + tier-map; it stays byte-reproducible. Hand-editing the generated views is forbidden (they carry the "generated — do not edit" header).

### 5. Federation gate

`python3 tools/lint_layering.py --strict` must return zero before `clinical-research` carves out (RFC 0002 §sequencing). On acceptance, the disposition above moves the tier-map from *tracked backlog* to *resolved*, and the generator re-emit makes the ontology match.

## Alternatives considered

- **Do nothing.** *Preserves* the corpus as-is. *Rejected:* blocks federation — the carve produces a non-conformant repo — and ships a graph that re-mints Core primitives.
- **Tier-only (the pre-Jessica framing).** *Changes:* attribute each object to a layer, but keep everything a class. *Rejected:* misses that Date/Tag/roles/context are not objects; it would *grow* the TBox with reified properties (new Core classes for a date, a tag). The KIND axis is load-bearing.
- **Hand-edit the 80 views.** *Rejected:* they are generator output; edits would be overwritten and drift from the catalog. Fix the source (catalog + tier-map + generator).
- **Put the cross-industry primitives in Core.** *Changes:* add `top:Budget`, `top:Tag`, etc. *Rejected:* bloats the deliberately-small 8-category / 29-leaf Core with domain and property concerns; finance is a bucket, a tag is a property.

## Open questions

1. **`hcls:Questionnaire` shape.** Adopt the FHIR `Questionnaire` structure via the standards crosswalk (RFC 0002 `standards` node), or a minimal HCLS-base shape? Recommend minimal + crosswalk.
2. **Finance bucket timing.** Budget/Payment leave CR now; does a `financial-services` bucket form on demand, or do they sit unmodeled? Recommend: out of scope, re-enter on bucket formation.
3. **`Participant` boundary.** Resolved here by reference only. Does it warrant its own short RFC given the PII/pseudonymization stakes? Recommend yes.
4. **Nearest-category calls.** A handful of `subclass` parents above (e.g. `MonitoringVisit`→`top:Activity`, `EnrollmentForecast`→`top:Evidence`) are defensible but not unique. CR WG confirms or re-homes; none creates a new class, so none is Core-affecting.

## Consequences

- **What gets easier.** Federation unblocks (the `--strict` gate can go green). The graph stops shadowing Core. Downstream reasoners see real subsumption (`cr:Investigator ⊑ hcls:Person`). The TBox shrinks and the property layer carries the data, as it should.
- **What gets harder.** The generator gains a tier-map dependency and a two-pass (tiered author → flat emit) shape. ~80 views regenerate; consumers pinned to the old flat `cr:` targets repoint to the resolved parents.
- **What downstream consumers adapt to.** View `sh:targetClass` values move from `cr:X` to `top:`/`hcls:` parents; demoted objects (Date, Tag) are no longer entities but properties.
- **Follow-on work.** Add `hcls:Questionnaire`; regenerate the corpus; the `Participant` sub-RFC; wire the finance objects out. All tracked by the tier-map + `--strict`.
- **What this forecloses.** Minting domain classes for concepts a parent owns, or for things that are properties — both now fail CI.

## References

- [`docs/ooux-layer-blindness.md`](../../docs/ooux-layer-blindness.md); Jessica Talisman, [*Context Is a Property, Not an Object*](https://jessicatalisman.substack.com/p/context-is-a-property-not-an-object).
- [`cr-domain/views/tier-map.json`](../../cr-domain/views/tier-map.json), [`tools/lint_layering.py`](../../tools/lint_layering.py), [`governance/extension-contract.md`](../../extension-contract.md) § "Layer discipline."
- [RFC 0001](accepted/0001-ooux-catalog-and-entity-view-schema.md) (OOUX catalog + entity-view schema), [RFC 0002](0002-repository-federation.md) (federation — the gate consumer), [ADR-0019](../../decision-log.md#adr-0019-open-core-constrained-extension-three-flavors-per-core-property), [ADR-0020](../../decision-log.md)/[ADR-0022](../../decision-log.md) (agency is a role), [ADR-0026](../../decision-log.md) (entity-view corpus).

## Notes for reviewers

Bo: the two calls I most want your read on are **§2 `Questionnaire` → `hcls:Questionnaire`** (the only new class this RFC creates — is the rule-of-three met, or hold it too?) and **§3's claim that Core gains nothing** — if you accept that, this RFC is non-Core-affecting except for the one HCLS-base addition, which lowers the quorum bar.
