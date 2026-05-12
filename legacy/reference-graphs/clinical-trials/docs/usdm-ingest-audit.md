# USDM v4 / ICH M11 ingest audit (working draft)

> Working document. Audits TOP Study v0.3.0 (Sponsor v0.1.4 / Site v0.2.0 alongside) against the USDM v4 model in `cdisc-org/usdm/main/src/usdm_model/` to determine whether a USDM v4 / ICH M11 compliant protocol document can be deterministically ingested into TOP NGSI-LD entities. Output: a punch list of structural gaps in both directions and recommended TOP-side adjustments before the ingester is built.
> Last touched 2026-05-09.

## Goal

TOP must support **automated ingestion** of a USDM v4 / ICH M11 compliant protocol JSON into NGSI-LD entities. Pipeline: USDM JSON in → TOP NGSI-LD entities out (Study, Protocol, Arm, ScheduleOfAssessments, Endpoint, InclusionCriterion, ExclusionCriterion, future Visit/Activity). No human in the loop for design-side entity creation.

This audit asks: **can the current Study v0.3.0 source intermediate accept a USDM document without lossy reshape, and is anything missing on the TOP side that the ingester would need?**

Verified against the live USDM v4 source: 72 files in `src/usdm_model/`. Field inventories captured for `study.py`, `study_version.py`, `study_design.py`, `study_arm.py`, `schedule_timeline.py`, `endpoint.py`, `objective.py`, `eligibility_criterion.py`, `encounter.py`, `activity.py`, `study_definition_document.py`, `study_definition_document_version.py`, `subject_enrollment.py`.

## Top finding

**TOP Study v0.3.0 is mostly compatible with USDM v4 ingestion**, but there are **eight structural mismatches** that need explicit decisions before the ingester is built. Two are big enough to potentially affect TOP's design layer; the other six are routine mapping concerns that need a documented convention.

The big two:
1. **StudyVersion is not modeled in TOP** — USDM treats every Study as having multiple versions; each StudyVersion carries its own studyDesigns, identifiers, dates, eligibility. TOP collapses to a single current effective set + Amendments. The ingester has to pick a StudyVersion to project; multi-version protocols lose fidelity unless TOP adds StudyVersion as a first-class entity.
2. **StudyIntervention / StudyEpoch / StudyElement / StudyCell / Estimand are not in TOP** — USDM models the design substructure richly. TOP has Arm but not Intervention as separate entity; SOA but not Epoch/Element/Cell; Endpoint but not Estimand (ICH E9(R1) Addendum). These are not blockers for first-pass ingest, but they ARE information loss.

The other six are routine:
3. Code-vs-enum mismatch (USDM uses CDISC controlled terms; TOP uses string enums)
4. Date-flattening (USDM GovernanceDate{type, value} vs TOP flat date fields)
5. Title-type-flattening (USDM titles[type] vs TOP studyTitle/studyShortTitle/studyAcronym)
6. Identifier-scope-flattening (USDM studyIdentifiers[scope] vs TOP per-registry fields)
7. Eligibility text living in a separate Item entity (USDM EligibilityCriterion → criterionItemId → EligibilityCriterionItem.text)
8. studyDesignRationale lives on Study/StudyDesign in USDM but TOP has it on Protocol

## USDM v4 architecture (verified)

```
Study (id, name, description, label, versions[], documentedBy[])
  ├── versions[] : StudyVersion (versionIdentifier, rationale, dateValues[],
  │                              amendments[], studyIdentifiers[], titles[],
  │                              eligibilityCriterionItems[], studyDesigns[],
  │                              roles[], organizations[], studyInterventions[],
  │                              administrableProducts[], biomedicalConcepts[],
  │                              ...)
  │     └── studyDesigns[] : InterventionalStudyDesign / ObservationalStudyDesign
  │           (studyType, studyPhase, therapeuticAreas[], encounters[],
  │            activities[], arms[], studyCells[], rationale, epochs[],
  │            elements[], estimands[], indications[], objectives[],
  │            population, scheduleTimelines[], eligibilityCriteria[],
  │            biospecimenRetentions[], analysisPopulations[],
  │            interventional: model, blindingSchema, intentTypes[];
  │            observational: timePerspective, samplingMethod)
  │
  └── documentedBy[] : StudyDefinitionDocument (language, type, templateName,
                       versions[])
        └── versions[] : StudyDefinitionDocumentVersion (version, status,
                         dateValues[], contents[NarrativeContent])
```

USDM Study itself is **thin** (just identity + version pointers). All the meat lives in StudyVersion and StudyDesign.

## Field-by-field cross-walk — TOP Study top-level

For each TOP attribute: where it comes from in a USDM document, and any concern.

| TOP attribute | USDM source | Ingester action | Concern |
|---|---|---|---|
| `studyId` (URI) | Mint from `Study.id` (UUID) per URI policy | `urn:top:study:{usdm_study_id}` | None |
| `sponsorProtocolId` | `StudyVersion.studyIdentifiers[scope=sponsor].text` | Lookup by scope Code | Need scope-Code convention |
| `studyTitle` | `StudyVersion.titles[type=OfficialStudyTitle].text` | Lookup by type Code | Need type-Code convention |
| `studyShortTitle` | `StudyVersion.titles[type=BriefStudyTitle].text` | Lookup by type Code | None |
| `studyAcronym` | `StudyVersion.titles[type=Acronym].text` | Lookup by type Code | None |
| `studyDescription` | `Study.description` (inherited) | Direct | None |
| `studyType` | `StudyDesign.studyType.code` | Code → enum mapping | CDISC C99077 controlled term |
| `studyPhase` | `StudyDesign.studyPhase.standardCode` | Code → enum mapping | CDISC C66737 controlled term |
| `interventionModel` | `InterventionalStudyDesign.model.code` | Code → enum mapping | Only on InterventionalStudyDesign; observational has timePerspective |
| `allocation` | TOP-only attribute, not direct in USDM | Inferred from StudyDesign characteristics or arms | **Gap**: USDM doesn't have a single `allocation` field; ClinicalTrials.gov-style attribute |
| `masking` | `InterventionalStudyDesign.blindingSchema.standardCode` | Code → enum mapping | None |
| `primaryPurpose` | `InterventionalStudyDesign.intentTypes[].code` | Code → enum mapping (first or join) | None |
| `studyStatus` | Derived from `StudyVersion.dateValues[type=...]` + `StudyDefinitionDocumentVersion.status` | Compose | **Gap**: USDM doesn't have a single Study.status; status is per-document-version + governance dates |
| `conditionStudied` | `StudyDesign.indications[].name` | Concat or first | None |
| `therapeuticArea` | `StudyDesign.therapeuticAreas[0].decode` | First or concat | None |
| `targetEnrollment` | `StudyDesign.population.plannedSubjects.minimumValue/maximumValue` (via StudyDesignPopulation) OR sum of `StudyVersion.subjectEnrollments[].quantity` | Compute | **Gap**: USDM target enrollment is per-Population or per-SubjectEnrollment record, not a single Study field |
| `actualEnrollment` | NOT IN USDM | TOP-only runtime field | Operational; not from USDM ingest |
| `enrollmentType` (ANTICIPATED/ACTUAL) | Inferred from whether `actualEnrollment` is populated | Computed | TOP-only convention |
| `minAge` / `maxAge` / `sexEligibility` / `acceptsHealthyVolunteers` | `StudyDesign.population.minimumAge` / `.maximumAge` / `.plannedSex` / `.plannedHealthySubjectIndicator` | Direct (after StudyDesignPopulation traversal) | StudyDesignPopulation entity I haven't fetched; same shape, fetch on ingester build |
| `plannedStartDate` | `StudyVersion.dateValues[type=ProtocolEffectiveDate]` or `[type=PlannedStudyStartDate]` | Lookup by type Code | None |
| `actualStartDate` | `StudyVersion.dateValues[type=ActualStudyStartDate]` (if present) | Lookup by type Code | Often absent in protocol docs (runtime fact) |
| `primaryCompletionDate` | `StudyVersion.dateValues[type=PrimaryCompletionDate]` | Lookup by type Code | None |
| `plannedCompletionDate` | `StudyVersion.dateValues[type=PlannedCompletionDate]` | Lookup by type Code | None |
| `actualCompletionDate` | `StudyVersion.dateValues[type=ActualCompletionDate]` | Lookup by type Code | Often absent (runtime fact) |
| `responsibleParty` | Derived from `StudyVersion.roles[type=ResponsibleParty]` | Compose | TOP enum maps to USDM role-code |
| `studyVersion` | `StudyVersion.versionIdentifier` | Direct | When ingester picks a version, this is set; multi-version case open |
| `clinicalTrialsGovId` | `StudyVersion.studyIdentifiers[scope=ClinicalTrials.gov].text` | Lookup by scope Code | None |
| `eudraCT` / `euCtisId` / `isrctn` / `nciId` | Same pattern, different scope Codes | Lookup by scope Code | None |
| `otherRegistryIds` | Catch-all for unrecognized scope Codes, comma-joined | Concat | Lossy if registry info is structured |
| `tags` | Not in USDM | TOP-only operator concept | None |

**Verdict on Study top-level**: ~95% deterministic mapping. Three soft-gaps (allocation, studyStatus, targetEnrollment) are inferable from compound USDM lookups with documented conventions. One architectural gap: **TOP's flat shape forces the ingester to project a chosen StudyVersion**; multi-version projects lose fidelity.

## Field-by-field cross-walk — Protocol sub-object

| TOP attribute | USDM source | Ingester action | Concern |
|---|---|---|---|
| `protocolId` (URI) | Mint from `StudyDefinitionDocumentVersion.id` | `urn:top:study:{usdm_study_id}/protocol/version:{usdm_doc_version_id}` | None |
| `protocolNumber` | Often duplicates Study.sponsorProtocolId | Direct | Operator convention |
| `protocolTitle` | Same as Study.studyTitle (often) | Direct | Document title can differ |
| `protocolVersion` | `StudyDefinitionDocumentVersion.version` | Direct | None |
| `protocolStatus` | `StudyDefinitionDocumentVersion.status.code` | Code → enum mapping | None |
| `approvalDate` | `StudyDefinitionDocumentVersion.dateValues[type=ApprovalDate]` | Lookup | None |
| `effectiveDate` | `StudyDefinitionDocumentVersion.dateValues[type=EffectiveDate]` | Lookup | None |
| `protocolDocumentRef` | NOT IN USDM | TOP-only (where the bytes live; eTMF URI) | Populated by deployment |
| `ddfDocumentRef` | The USDM JSON itself's URI | Direct | Self-referential |
| `studyDesignRationale` | `StudyDesign.rationale` | **Misplaced in TOP** — USDM has rationale on StudyDesign; TOP has it on Protocol | **Gap 8**: should move to Study top-level |

**Verdict on Protocol**: clean ingest except for `studyDesignRationale` which TOP misplaced — should live on Study.studyDesignRationale (or on a future StudyDesign sub-object), not on Protocol.

## Field-by-field cross-walk — Arm sub-object

| TOP attribute | USDM source | Ingester action | Concern |
|---|---|---|---|
| `armId` (URI) | Mint from `StudyArm.id` | `urn:top:study:{usdm_id}/arm:{usdm_arm_id}` | None |
| `armName` | `StudyArm.name` (inherited) | Direct | None |
| `armShortName` | `StudyArm.label` (inherited, if present) | Direct | None |
| `armType` | `StudyArm.type.code` | Code → enum mapping (CDISC C174266 ARMT) | None |
| `armDescription` | `StudyArm.description` (inherited) | Direct | None |
| `armSize` | `StudyDesign.population.cohorts[].plannedSubjects` per cohort linked to this Arm | **Compute via Population traversal** | **Gap**: USDM keeps cohort sizes structurally separate from the Arm |
| `interventionDescription` | `StudyVersion.studyInterventions[id IN StudyDesign.studyInterventionIds].description` | **Compute via StudyIntervention traversal** | **Gap**: USDM separates StudyIntervention from Arm; TOP collapses |
| `isPlaceboArm` | Computed: `armType.code == "PLACEBO_COMPARATOR"` | Derived | OK if armType is canonical |
| `isControlArm` | Computed: `armType.code IN {"PLACEBO_COMPARATOR", "ACTIVE_COMPARATOR", "NO_INTERVENTION", "SHAM_COMPARATOR"}` | Derived | OK |

**Verdict on Arm**: needs ingester traversal logic for armSize (USDM Population) and interventionDescription (USDM StudyIntervention). Both are tractable. Information loss if a single TOP Arm aggregates multiple USDM cohorts, or if multiple USDM Arms share a single StudyIntervention (TOP duplicates the description).

## Field-by-field cross-walk — Endpoint sub-object

| TOP attribute | USDM source | Ingester action | Concern |
|---|---|---|---|
| `endpointId` (URI) | Mint from `Endpoint.id` | `urn:top:study:{usdm_id}/endpoint:{usdm_endpoint_id}` | None |
| `endpointName` | `Endpoint.name` (inherited from SyntaxTemplate) | Direct | None |
| `endpointDescription` | `Endpoint.description` (inherited) | Direct | None |
| `endpointType` | `Endpoint.level.code` (PRIMARY / SECONDARY / EXPLORATORY / SAFETY) | Code → enum mapping | OR derived from parent `Objective.level.code` if Endpoint level is not set |
| `endpointMeasurementType` | NOT IN USDM directly | TOP-only operator field | Could be inferred from associated BiomedicalConcept measurement type |
| `measurementUnit` | NOT IN USDM directly | TOP-only operator field | Could be inferred from BiomedicalConcept |
| `timeFrame` | NOT IN USDM directly | TOP-only operator field; ICH E9(R1) Estimand has time-related attributes | **Gap**: USDM Estimand carries time framing more rigorously |
| `statisticalApproach` | NOT IN USDM directly | TOP-only operator field | **Gap**: USDM Estimand attribute |

**Verdict on Endpoint**: TOP carries operator-grounded richer fields than USDM Endpoint exposes. Ingester can populate `endpointType` from USDM Endpoint.level OR Objective.level; cannot populate `endpointMeasurementType` / `measurementUnit` / `timeFrame` / `statisticalApproach` from USDM directly. **Recommendation**: add a TOP `Estimand` sub-object in v0.4 to carry these attributes properly per ICH E9(R1); current Endpoint fields are operator-grounded but doctrinally sit at the Estimand level.

## Field-by-field cross-walk — InclusionCriterion / ExclusionCriterion

| TOP attribute | USDM source | Ingester action | Concern |
|---|---|---|---|
| `criterionId` (URI) | Mint from `EligibilityCriterion.id` | `urn:top:study:{usdm_id}/eligibility:{usdm_criterion_id}` | None |
| `criterionNumber` | `EligibilityCriterion.identifier` | Direct | None |
| `criterionText` | Dereference `EligibilityCriterion.criterionItemId` → `StudyVersion.eligibilityCriterionItems[id == criterionItemId].text` | Lookup | **Gap**: text lives in a separate Item entity, ingester must dereference |
| `criterionCategory` | NOT IN USDM directly | TOP-only operator filter | Could be inferred via NLP from criterionText (out of scope for ingester v1) |
| `waiverAllowed` | NOT IN USDM | TOP-only operator concept | Default false |
| `waiverConditions` | NOT IN USDM | TOP-only operator concept | Default empty |

**Inclusion vs Exclusion routing**: `EligibilityCriterion.category.code` is the discriminator (`Inclusion` / `Exclusion`). Ingester routes to TOP InclusionCriterion or ExclusionCriterion sub-object based on category Code.

**Verdict on Eligibility**: clean once the Item-dereferencing pattern is documented.

## Field-by-field cross-walk — ScheduleOfAssessments sub-object

| TOP attribute | USDM source | Ingester action | Concern |
|---|---|---|---|
| `soaId` (URI) | Mint from `ScheduleTimeline.id` | `urn:top:study:{usdm_id}/soa:{usdm_timeline_id}` | None |
| `soaName` | `ScheduleTimeline.name` (inherited) | Direct | None |
| `soaVersion` | NOT directly on ScheduleTimeline | Inherited from `StudyVersion.versionIdentifier` | Convention |
| `soaStatus` | Inherited from StudyVersion / DocumentVersion status | Compose | Convention |
| `approvalDate` / `effectiveDate` | Inherited from StudyVersion / DocumentVersion dates | Compose | None |
| `soaDocumentRef` | NOT IN USDM | TOP-only deployment concern | None |
| `description` | `ScheduleTimeline.description` (inherited) | Direct | None |

**Verdict on SOA top-level**: TOP's SOA top-level is thin (deliberately, since Visit/Activity haven't lifted). The richness of ScheduleTimeline (mainTimeline boolean, entryCondition, entryId, exits[], timings[], instances[], plannedDuration) maps to entities TOP has not yet introduced. **Note for Visit/Activity lift**: when those lift, the USDM ScheduleTimeline structure (timings + instances + encounter linkages) becomes the canonical ingest source.

## Eight structural gaps requiring decisions

### Gap 1 — StudyVersion not modeled in TOP (architectural)

USDM v4 treats every Study as having `versions[]` of StudyVersion, each carrying its own studyDesigns, identifiers, dates, eligibility, organizations. TOP collapses to a single current effective set + Amendments[] (Amendment not yet in source).

**Implication**: ingester picks one StudyVersion to project (typically the most recent EFFECTIVE version). Multi-version protocols where amendments are substantively different (different study designs, different eligibility) lose fidelity.

**Options**:
- **A**: Keep TOP flat. Ingester picks current effective StudyVersion; previous versions tracked via Amendment (when lifted). Lossy for substantive amendments.
- **B**: Add `StudyVersion` as a TOP sub-object under Study. Each StudyVersion carries its own per-version fields; current Study attributes split between Study (identity-only) and StudyVersion (per-version). Higher fidelity, more complexity.
- **C** (recommended): Keep TOP flat for v0.3.0. Document the convention "TOP Study reflects current effective StudyVersion; previous versions reachable via Amendment when Amendment lifts." Adds a `currentStudyVersionRef` attribute on Study pointing at the USDM StudyVersion id used for the projection. Re-evaluate when Amendment lifts (probably v0.5).

### Gap 2 — StudyIntervention / StudyEpoch / StudyElement / StudyCell / Estimand not in TOP (architectural)

USDM models the design substructure deeply:
- **StudyIntervention** (per-StudyVersion): the actual intervention (drug, device, procedure) with its administrableProducts[]. Multiple Arms can share one StudyIntervention.
- **StudyEpoch** (per-StudyDesign): time-block of the study (Screening, Treatment, Follow-Up).
- **StudyElement** (per-StudyDesign): a procedural unit (e.g., "Drug X 200mg PO QD").
- **StudyCell** (per-StudyDesign): the (Arm × Epoch × Elements[]) intersection — the structural matrix that defines what each Arm receives in each Epoch.
- **Estimand** (per-StudyDesign): ICH E9(R1) Addendum — the formal definition of the treatment effect (population, treatment, endpoint, intercurrent-event handling, summary measure).

TOP has none of these.

**Implication**: ingester drops these structures. Information loss is real but most operators won't notice (StudyCells are typically rendered as the SOA grid; Estimands live in the SAP). Estimand is the most painful loss because ICH E9(R1) is becoming the canonical way to specify endpoints.

**Options**:
- **A** (recommended for v0.3.0): Drop on ingest; document the loss. Add `Estimand` sub-object in v0.4 (lifts before Visit/Activity since SAP-level design lifts before runtime). Defer StudyEpoch / StudyElement / StudyCell to ingester-only — they're internal USDM design glue, not reflected in operator UX.
- **B**: Add Estimand AND StudyIntervention now. Both lift to v0.3.1. Higher fidelity, more sub-objects.
- **C**: Add all five. Match USDM. Opposite-of-OOUX-grounded — these aren't operator-facing.

### Gap 3 — Code-vs-enum mismatch (routine)

USDM uses `Code{code, codeSystem, codeSystemVersion, decode}` (CDISC controlled terminology) wherever there's a category. TOP uses string enums with the decode value as the enum.

**Implication**: ingester needs a Code-to-enum mapping per attribute. If USDM emits a Code TOP doesn't recognize, fall back to "OTHER" or fail loudly.

**Action**: document the Code→enum mapping policy in the ingester spec; emit a `mapsToCode` annotation in source-intermediate alongside `mapsTo`.

### Gap 4 — Date-flattening (routine)

USDM models dates as `GovernanceDate{type Code, dateValue, geographicScopes[]}` in a single `dateValues[]` list. TOP has flat `plannedStartDate` / `actualStartDate` / `primaryCompletionDate` / `plannedCompletionDate` / `actualCompletionDate`.

**Implication**: ingester dispatches by GovernanceDate.type Code into the right TOP attribute. Geographic scope (per-jurisdiction dates) collapses unless TOP grows multi-valued date fields.

**Action**: document the type-Code convention; for multi-jurisdiction dates, take the global one or pick by configured priority (US-first or EU-first).

### Gap 5 — Title-type-flattening (routine)

USDM has `titles[type Code]` with multiple title types. TOP has `studyTitle` / `studyShortTitle` / `studyAcronym`.

**Action**: document the type-Code → TOP-attribute mapping. Trivial.

### Gap 6 — Identifier-scope-flattening (routine)

USDM has `studyIdentifiers[scope]` where scope is a Code (e.g., the registry org). TOP has flat per-registry fields.

**Action**: document the scope-Code → TOP-attribute mapping. Catch-all goes to `otherRegistryIds`.

### Gap 7 — Eligibility-text-via-Item dereferencing (routine)

USDM EligibilityCriterion holds `criterionItemId` pointing at `StudyVersion.eligibilityCriterionItems[]` for the text. TOP holds text inline.

**Action**: ingester dereferences. Trivial.

### Gap 8 — studyDesignRationale on Protocol vs Study (TOP misplacement)

USDM puts `rationale` on StudyDesign. TOP puts `studyDesignRationale` on Protocol.

**Action (recommended)**: move TOP `studyDesignRationale` from Protocol to Study top-level (or to a future StudyDesign sub-object). Backwards-compatibility hazard is minimal since TOP isn't yet ingesting any USDM docs.

## Summary table — ingest readiness per TOP entity

| TOP entity | Ingest readiness | Action needed |
|---|---|---|
| Study top-level | 95% | Document conventions for allocation / studyStatus / targetEnrollment composition; commit URI policy |
| Protocol sub-object | 90% | Move studyDesignRationale to Study (Gap 8); commit URI policy |
| Arm sub-object | 85% | Document Population traversal for armSize, StudyIntervention traversal for interventionDescription |
| Endpoint sub-object | 70% | Lossy for measurementType/timeFrame/statisticalApproach. **Recommend adding Estimand sub-object in v0.4.** |
| InclusionCriterion / ExclusionCriterion | 95% | Document Item-dereferencing pattern; commit URI policy |
| ScheduleOfAssessments | 60% | Thin top-level; Visit/Activity lift unlocks the ScheduleTimeline ingest. Adequate placeholder. |

Overall: TOP Study v0.3.0 is **ready for first-pass USDM ingest** with the conventions documented above and the studyDesignRationale move (Gap 8). Adding Estimand and StudyVersion-as-sub-object are improvements that should be sequenced thoughtfully (likely v0.4 and v0.5 respectively).

## Recommended TOP-side adjustments before the ingester is built

1. **Move `studyDesignRationale` from Protocol to Study** (small change to source intermediate; one commit). Aligns with USDM's StudyDesign.rationale.
2. **Add `currentStudyVersionRef` attribute on Study** (small change). String holding the USDM StudyVersion.id used at ingest. Provides traceability.
3. **Add `Estimand` sub-object on Study in v0.4** (deferred; documented here as future work). Carries ICH E9(R1) attributes (population spec, treatment spec, endpoint linkage, intercurrent-event handling, summary measure). The current TOP Endpoint operator-fields (timeFrame, statisticalApproach) move to Estimand when it lifts; Endpoint becomes thinner and more aligned with USDM Endpoint.
4. **Document the URI policy formally** in a new `tools/ingest_usdm_uri_policy.md` (or as part of the ingester spec). Provisional pattern from Participant planning note: `urn:top:study:{usdm_study_id}/...`.
5. **Document the Code→enum mapping table** in the source intermediate as `_codeMap` annotations or in a separate `ingester-mappings.md`.

## Validation against USDM integration test files

The audit above was constructed from per-class field inventories. To validate against real USDM documents, I read several files from `cdisc-org/usdm/main/tests/integration_test_files/`:

- `minimum.json` — minimal valid USDM Study (Phase II Alzheimer's, single-arm, no scheduleTimelines, no eligibility criteria, no documentedBy)
- `full_1.json` — full USDM Study (Phase III diabetes, two arms, four epochs, six encounters, four amendments, multiple eligibility criteria, multiple objectives/endpoints)
- `eligibility_criteria_1.json` — full eligibility-criteria patterns
- `arms_epochs.json` — arm/epoch/cell structure
- `interventions.json` — StudyIntervention examples

Concrete findings that supplement or amend the audit above:

### Finding A — USDM is at v4.0.0 (corrected)

The integration test files carry `"usdmVersion": "4.0.0"` and `"systemVersion": "0.67.0"`. The python source on `main` is the v4 model. References throughout this audit corrected from v3 to v4. **Action**: ingester targets USDM v4. Earlier-version compatibility is a separate concern.

### Finding B — Protocol is OPTIONAL in USDM (new Gap 9)

`minimum.json` has `"documentedBy": []`. A valid USDM Study with no attached `StudyDefinitionDocument` exists. TOP's `Study.hasProtocol` is currently `1..1`.

**This is a structural mismatch that breaks ingest of valid USDM documents.**

**Action (Gap 9)**: change `Study.hasProtocol` cardinality from `1..1` to `0..1`. Update the SHACL invariant to say "Protocol is required once the Study reaches RECRUITING status" rather than "Protocol is required for all Studies." A planning-state Study from M11 may have no formal protocol document yet.

### Finding C — Identifier scope is via Organization reference, not Code directly (refines Gap 6)

Audit Gap 6 said "studyIdentifiers[scope] is a Code." Wrong. `StudyIdentifier` has `scopeId` referencing `StudyVersion.organizations[id == scopeId]`. The scope is an Organization (FDA, EMA, ClinicalTrials.gov, NCI, sponsor's own — all modeled as Organization entities, with the Organization's `type.code` indicating role).

**Action (refines Gap 6)**: ingester resolves `studyIdentifiers[].scopeId` → Organization → check `Organization.type.code` to dispatch into TOP's `clinicalTrialsGovId` / `eudraCT` / `nciId` / `sponsorProtocolId` / etc. The `Organization.type` Code values are the discriminator (e.g., `C42627` for Clinical Trial Registry; sponsor org has `type.code` like `C54149` for Drug Company).

### Finding D — EligibilityCriterionItem text uses placeholder substitution (refines Gap 7)

`eligibility_criteria_1.json`: `EligibilityCriterionItem.text = "Subjects shall be between [min_age] and [max_age]"` with `dictionaryId` referencing a `SyntaxTemplateDictionary` that holds the substitution values.

**Action (refines Gap 7)**: ingester does TWO steps:
1. Dereference `EligibilityCriterion.criterionItemId` → `EligibilityCriterionItem.text` (the templated form)
2. Resolve `[placeholder]` substitutions via `EligibilityCriterionItem.dictionaryId` → `SyntaxTemplateDictionary`

TOP `criterionText` should hold the **resolved** form (operator reading: "Subjects shall be between 18 and 70 years old"). The templated form can be preserved in a TOP-side annotation if needed for round-trip fidelity, but the resolved form is the operator-grounded value.

### Finding E — StudyVersion.amendments[] is the Amendment ingest source

Confirmed against `full_1.json`: 4 amendments live in `StudyVersion.amendments[]` with reasons (TYPO_FIX, DESIGN_CHANGE, UNBLINDING_SECTION, INCLUSION_CRITERIA_UPDATE) and per-amendment enrollment-scope changes by geography. When TOP lifts Amendment (currently flagged-missing in `Study.hasAmendment`), ingest source is `usdm:StudyAmendment` from this list.

### Finding F — Every USDM entity carries `extensionAttributes[]`

`extensionAttributes: []` appears on every entity (Study, StudyVersion, StudyDesign, StudyArm, StudyEpoch, StudyCell, GovernanceDate, etc.). This is for sponsor-specific extensions in the M11 spec.

**Action (new convention)**: ingester preserves `extensionAttributes[]` in a TOP-side `_usdmExtensions` map per entity. Lossy by convention if extensions are dropped; round-trip-safe if preserved. **Recommend preserving** by default (just JSON; cheap to keep).

### Finding G — StudyDesignPopulation is the canonical source for TOP eligibility-roll-up fields (verified)

Verified against `minimum.json`:
- `population.includesHealthySubjects` (bool) → TOP `acceptsHealthyVolunteers`
- `population.plannedEnrollmentNumber.value` (Quantity float) → TOP `targetEnrollment` (cast to int)
- `population.plannedSex[].decode` (Code list, often "Both" / "Male" / "Female") → TOP `sexEligibility`
- `population.plannedAge.minValue.value` + unit Code → TOP `minAge` (formatted as "{value} {unit}")
- `population.plannedAge.maxValue.value` + unit Code → TOP `maxAge`
- `population.cohorts[]` — multi-cohort detail (TOP currently rolls into Study; per-cohort fidelity lost unless TOP adds Cohort)
- `population.criterionIds[]` — per-population eligibility scoping (vs cross-cutting `StudyDesign.eligibilityCriteria`)

`plannedCompletionNumber` (planned-to-complete) is a separate Quantity; TOP doesn't have a corresponding field. Information loss; could add `targetCompletion` if operationally useful.

### Finding H — StudyInterventionIds is on StudyDesign and StudyElement, NOT on StudyArm (refines Gap 2)

Verified against `study_arm.py`, `study_design.py`, `minimum.json` StudyElement field. The chain is:
- `StudyDesign.studyInterventionIds[]` lists which interventions are used in this design
- `StudyDesign.studyInterventions[]` defines them (on StudyVersion, referenced by id)
- `StudyDesign.studyCells[]` joins (Arm × Epoch × Elements[])
- `StudyElement.studyInterventionIds[]` lists which interventions are administered in this element

So per-arm intervention assignment traverses: Arm → Cells (filtered by armId) → Elements (filtered by epoch) → Interventions. Three levels of indirection.

**Action (refines Gap 2)**: ingester's "Arm.interventionDescription" derivation walks this chain. For TOP v0.3.0 (no StudyIntervention sub-object), produce a comma-joined list of intervention names per arm. When TOP adds StudyIntervention as a sub-object/horizontal in v0.4+, the proper graph projection lifts.

### Finding I — Visit modes encoded in Encounter.type Code

`full_1.json` Encounter type decodes include "Visit, Clinic, In Person" and "Visit, Home, Telephone Call". The Encounter type Code carries (visit-or-not, location, mode) as a triple. **For Visit lift**: TOP Visit.visitMode and Visit.visitLocation should derive from this Code structure. Worth noting for the Visit-lift planning note.

### Finding J — IntentTypes vs primaryPurpose mapping

`InterventionalStudyDesign.intentTypes[]` is a list (e.g., `["Treatment Study"]` in minimum.json). TOP `primaryPurpose` is single-valued. If the list has multiple entries, TOP must pick one or join. **Action**: ingester takes the first entry; documents convention.

---

**Net effect on the audit**: One new gap added (Gap 9 — Protocol cardinality), two routine gaps refined (Gap 6 — scope-via-Organization; Gap 7 — placeholder resolution), one new convention added (extensionAttributes preservation), and minor refinements to Gaps 2 and the cross-walk tables.

The audit's overall verdict is unchanged: **Study v0.3.0 is ready for first-pass USDM v4 ingest with the gaps and conventions documented**. Gap 9 (Protocol cardinality) is the only new TOP-side change required before the ingester is built; trivial fix.

## Updated open questions for Bo

(Adds Gap 9 to the original six.)

1. **Gap 1 (StudyVersion)**: keep flat with Amendment-tracking (Option A/C), or lift StudyVersion to first-class (Option B)?
2. **Gap 2 (Estimand)**: add Estimand sub-object in v0.4 (recommended), or accept lossy ingest for now?
3. **Gap 8 (rationale move)**: move `studyDesignRationale` from Protocol to Study now (recommended) or defer?
4. **URI policy commitment**: `urn:top:study:{usdm_id}/...` (provisional), or different scheme?
5. **Code→enum mapping policy**: emit `mapsToCode` annotations in source intermediate (heavier), or maintain a side `ingester-mappings.md` (lighter)?
6. **Ingester sequencing**: build ingester now (v0.4) before Participant lift, OR after Participant lift, OR after Visit/Activity lift?
7. **Gap 9 (Protocol cardinality)**: change `Study.hasProtocol` from `1..1` to `0..1` to accept USDM documents with no `documentedBy[]`. Recommended; trivial.

## What this audit does NOT cover

- **Visit / Activity / Procedure**: not yet lifted in TOP. When those lift (post-Participant), the audit must be extended to USDM Encounter / Activity / Procedure.
- **Population / StudyDesignPopulation**: not fetched in this round; expected to map cleanly to TOP Study eligibility-roll-up fields.
- **Indication / Condition / BiomedicalConcept**: USDM models clinical concepts richly; TOP keeps `conditionStudied` as free text. Adequate for v0.3.0; deeper alignment needed when TOP starts ingesting Activity content (procedures reference BiomedicalConcepts).
- **NarrativeContent / SyntaxTemplate**: USDM models the protocol prose (M11 sections) as structured NarrativeContent. TOP doesn't aspire to ingest prose; the protocol PDF reference is enough for operators.

## Pointers

- [`top-strawman.json`](../source/top-strawman.json) — TOP source intermediate audited here.
- [`study-spec.html`](study-spec.html) — Study v0.3.0 spec (sealed).
- [`participant-planning.md`](participant-planning.md) — Participant planning note; introduced the USDM/M11 ingest boundary.
- [USDM v4 source](https://github.com/cdisc-org/usdm/tree/main/src/usdm_model) — verified against this revision.
- [USDM integration test files](https://github.com/cdisc-org/usdm/tree/main/tests/integration_test_files) — used to validate the audit (`minimum.json`, `full_1.json`, `eligibility_criteria_1.json`, `arms_epochs.json`, `interventions.json`).
- [ICH E9(R1) Addendum](https://www.ich.org/page/efficacy-guidelines) — Estimands framework (motivates Gap 2).
- [ICH M11](https://www.ich.org/page/efficacy-guidelines) — protocol template the USDM digital instantiation conforms to.
