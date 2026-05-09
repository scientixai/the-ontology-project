# Visit spec planning note (working draft)

> Working document. Surfaces the architectural decisions Visit has to make before the source-intermediate lift and the spec-doc draft. Folds into `visit-spec.html` once the decisions below are sealed.
> Last touched 2026-05-09.

## Purpose

Visit is the sixth top-level to lift to full spec discipline (after Sponsor v0.1.4, Site/StudySite v0.2.0, Study v0.3.0, Participant + Recruit v0.4.0). Visit is the natural follow-on because it expands the queryability surface for digital-twin synthesis and unblocks several flagged-missing edges (Participant.hasVisit, StudySite.hostsVisit). The lift will also move the OOUX-locked-9 from "5 of 9 scaffolded" to "6 of 9 scaffolded."

This note captures the architectural decisions Visit has to make so Bo can weigh in before implementation.

## Current state

Visit is not yet in the source intermediate. Multiple flagged-missing references already point at it:

- `StudySite.hostsVisit → Visit` (0..N, _targetMissing) — the per-StudySite list of Visit-occurrences
- `Participant.hasVisit → Visit` (0..N, _targetMissing) — the per-Participant list of Visit-occurrences
- `Study.hasSchedule → ScheduleOfAssessments` already lifted in Study v0.3.0; the Visit-template chain runs through SOA

The OOUX Visit object is well-specified but carries the same OOUX-level error as Participant: it points directly at `1 Site` rather than at `1 StudySite`. The Site spec tracked this correction; Visit lift applies it.

## Where Visit sits in the operational hierarchy

```
Site ─→ StudySite ─→ Study ─→ Protocol ─→ SOA ─→ VisitDefinition ─→ Activity (template)
  │                                                       ▲
  │                                                       │ definedBy
  │                                                       │
  └─→ StudySite ─→ Visit (occurrence) ── for ──▶ Participant
                          │                       │
                          │ hasActivity           │ assignedToArm ──▶ Arm
                          ▼                       │
                       Activity (occurrence)      │
                          │                       │
                          ▼                       │
                       Observation / Result       │
                          │                       │
                          ▼                       │
                       (when Event lifts)         │
                       hasAdverseEvent            │
```

**Two chains meet at Visit**: the design-side chain (Protocol → SOA → VisitDefinition → Activity-template) carries WHAT IS SUPPOSED TO HAPPEN, the operational-side chain (StudySite → Visit-occurrence → Activity-occurrence → Observation) carries WHAT ACTUALLY HAPPENED. The OOUX conflates them — TOP separates them per FIRST-PRINCIPLES (different operators ask different questions of the two layers).

## Standards alignment posture

Standards that touch Visit, with their realm:

- **USDM v4 `Encounter`** (verified against `cdisc-org/usdm/main/src/usdm_model/encounter.py`) — the *design-side* visit template. Fields: `type` (Code; encodes visit-or-not + location + mode as a triple), `previousId`/`nextId` (linked-list ordering), `scheduledAtId`, `environmentalSettings[]` (Codes), `contactModes[]` (Codes), `transitionStartRule`/`transitionEndRule`, `notes`. Inherited: `id`/`name`/`label`/`description`. **No per-occurrence runtime data** — USDM's Encounter is template-only. This parallels USDM's pattern for Subject (no per-subject runtime entity); Visit-occurrence is operational, not in USDM.
- **USDM v4 `Activity`** — *design-side* activity template (the procedure). Fields: `previousId`/`nextId`, `childIds[]`, `definedProcedures[]`, `biomedicalConceptIds[]`, `bcCategoryIds[]`, `bcSurrogateIds[]`, `timelineId`. **No per-occurrence runtime data**.
- **USDM v4 `ScheduleTimeline`** — the timing structure (which encounters in which order, with planned durations and timings). Lives on StudyDesign.scheduleTimelines[].
- **FHIR R5 `Encounter`** — the *operational-side* clinical encounter. Status (`planned` / `in-progress` / `on-hold` / `completed` / `cancelled` / `discharged` / etc.), class (inpatient / outpatient / home-health / virtual), type, subject (Patient), period, location, participant, partOf. **TOP Visit-occurrence maps directly.**
- **FHIR R5 `Appointment`** — pre-occurrence scheduling artifact (status: `proposed` / `pending` / `booked` / `arrived` / `fulfilled` / `cancelled` / `noshow` / `waitlist` / `checked-in`). Operationally distinct from Encounter; some sponsors model scheduled-not-yet-occurred as Appointment, completed as Encounter.
- **SDTM `SV` (Subject Visits)** — analysis/submission projection. Columns: STUDYID, DOMAIN, USUBJID, VISITNUM, VISIT, VISITDY, SVSTDTC, SVENDTC, SVUPDES (visit description for unscheduled). Per-Subject visit-occurrence record.
- **CDASH `VISIT`** — acquisition-side visit fields (CRF-level).
- **OMOP `VISIT_OCCURRENCE`** — research-warehouse visit projection. Fields: visit_concept_id, visit_start_datetime, visit_end_datetime, visit_type_concept_id, provider_id, care_site_id, preceding_visit_occurrence_id.
- **ICH E6(R3) Annex 2** — decentralized-clinical-trial framing. Establishes IN_PERSON / REMOTE / HYBRID modes as canonical operator vocabulary; supports virtual visits, home health, telehealth, async.

**Per FIRST-PRINCIPLES**: TOP entities are operator-grounded. Visit / VisitDefinition / Activity / Observation come from operator vocabulary. Standards cross-walks (USDM Encounter, FHIR Encounter, SDTM SV, etc.) live below the line as projection-adapter rules.

## USDM/M11 ingest boundary (visit edition)

**VisitDefinition is USDM-ingest-derivable** (template-side). When the USDM ingester runs, it creates VisitDefinition entities from `StudyDesign.encounters[]`. Activity-templates from `StudyDesign.activities[]`.

**Visit (occurrence) is NOT USDM-ingest-derivable** (runtime). Visit-occurrence entities are created by operational systems (EDC, scheduling system, eVisit platform) when real participants attend real visits. Same operational/design boundary as Participant: USDM defines what's supposed to happen; runtime systems record what actually happened.

The `Visit.definedBy → VisitDefinition` link uses the URI policy established in the Participant planning note: `urn:top:study:{usdm_study_id}/visit-definition:{usdm_encounter_id}`. EDC writing a Visit-occurrence references the same VisitDefinition URI the ingester wrote — SHACL invariant resolves cleanly.

## Multi-realm projection — Visit in three rooms

| Realm | Operator | Visit appears as | Standards projection |
|---|---|---|---|
| **Trial conduct (TOP carries this)** | Site coordinator / PI / monitor | `Visit` (operational occurrence) | FHIR `Encounter`, SDTM `SV`, CDASH `VISIT` |
| Clinical care | Treating physician / PCP | `Encounter` in their EMR | FHIR `Encounter` (in their care realm), USCDI |
| Real-world evidence | RWE analyst | `VISIT_OCCURRENCE` row | OMOP CDM, Sentinel, PCORnet |

Per FIRST-PRINCIPLES, TOP carries the trial-conduct realm; the others are projection-adapter targets at deployment edge. Cross-realm linkage (this trial visit happened the day after a standard-care ER visit) is federation, not substrate.

## Architectural decisions to seal

### Decision 1 — Visit-template vs Visit-occurrence (the architectural call)

The protocol-defined Visit-template ("Visit 1 happens at Day 1; performs Screening procedures") is operationally distinct from the Visit-occurrence ("Mary attended Visit 1 on 2026-04-08 at MSKCC, completed all screening procedures except labs which were rescheduled"). Three options:

**Option A: Two separate entities — `VisitDefinition` as Study sub-object, `Visit` as top-level occurrence.**
- VisitDefinition lives under Study (parallel to or under SOA), is USDM-ingest-derivable from `StudyDesign.encounters[]`
- Visit (top-level) is the operational occurrence; references VisitDefinition via `definedBy`
- Pro: matches USDM separation (USDM Encounter is design-only); each entity has a clean operator-vocabulary; SHACL invariants per layer
- Pro per FIRST-PRINCIPLES: "Visit 1" (template) and "Mary's Visit 1" (occurrence) ARE different operational objects

**Option B: Single `Visit` entity with `visitKind` enum (TEMPLATE / OCCURRENCE).**
- One entity; the enum discriminates
- Pro: simpler entity count
- Con: violates per-FIRST-PRINCIPLES "different operator vocabulary gets first-class entity"; SHACL invariants get conditional ("when visitKind=OCCURRENCE, must have actualStartDate") — verbose
- Con: cross-walks become discriminator-driven (TEMPLATE projects to USDM Encounter; OCCURRENCE projects to FHIR Encounter / SDTM SV) — doable but messier

**Option C: Visit-occurrence only as TOP top-level; VisitDefinition deferred to v0.6.**
- Lift only the operational entity now; defer the design-side template to a later pass when richer SOA modeling is needed
- Pro: smaller v0.5 lift
- Con: USDM ingester immediately needs VisitDefinition; deferring forces awkward "ingester writes VisitDefinition stub entities while the design model isn't there" — bad architecture

**Recommendation: Option A.** Two separate entities. `VisitDefinition` lifts as a Study sub-object (parallel to ScheduleOfAssessments — the SOA references VisitDefinitions in its grid). `Visit` lifts as a top-level entity carrying the operational occurrence. Clear operator vocabulary; clean USDM ingest mapping; SHACL invariants stay simple.

This makes Visit the sixth top-level, and VisitDefinition the seventh Study sub-object (Study has 6 currently; Activity may also lift as a Study sub-object — see Decision 4).

### Decision 2 — Anchor pattern

A Visit-occurrence anchors at:

- `forParticipant → Participant` (1..1) — whose visit it is
- `forStudySite → StudySite` (1..1) — where it operationally happens (in-person or remote — the StudySite is the operational owner regardless of physical location)
- `definedBy → VisitDefinition` (0..1) — what the protocol says happens at this visit. 0..1 because UNSCHEDULED visits (urgent care, AE workup, sponsor-requested follow-up) don't have a corresponding VisitDefinition

Note: Visit anchors at *both* Participant AND StudySite, not via traversal through Participant.forStudySite. The redundancy is deliberate — query convenience for "all visits at MSKCC across all participants" doesn't require a join.

OOUX correction to apply: OOUX has Visit pointing at `1 Site`; should be `1 StudySite`. (Same correction tracked in Site spec and applied in Participant lift.)

### Decision 3 — Visit Observation as sub-object

The OOUX-locked sub-object that lands under Visit during the boundary decisions (Path C). Captures something the operator notices during the visit that doesn't fit a structured Activity slot. Has the `derivedFrom` relationship that links forward to a categorized Other Clinical Event when a CRA escalates.

**Recommendation: lift VisitObservation as a sub-object.** Attributes:
- observationId (URI)
- observationText (the operator's free-text note)
- observationDate / observationTime
- observationCategory (initial enum: PROTOCOL_DEVIATION / SAFETY_SIGNAL / DATA_DISCREPANCY / OPERATIONAL_NOTE / OTHER)
- escalated (boolean) / escalationDate / escalatedTo (Event reference, when Event lifts)
- recordedBy (Person, drawn from forStudySite delegation)

Captures the reportability handoff workflow per OOUX boundary decision Path C: the CRA's "this looks like an AE — escalate" action.

### Decision 4 — Activity + Task as universal sub-objects (universal substrate posture)

Per Bo: TOP must accommodate any assessment without modeling its specifics. Specific visit structures, therapeutic-area assessments, instrument configurations are implementation details — they belong in sponsor-side workflow tools, vendor platforms, EHR integrations. The substrate stays universal.

The substrate carries **`Activity` and `Task` as universal containers** under Visit. Specialization happens via content (biomedicalConceptCode, polymorphic taskValue, Equipment used, Document governing), never via specialized entity shapes. A DICOM imaging Activity and a blood-draw Activity are the same TOP shape; they differ in content, not in entity type.

```
Visit (occurrence)
  ├── hasActivity → Activity[*] (universal: vitals OR MRI OR ePRO OR biopsy OR IP-admin OR ...)
  ├── hasTask → Task[*]    (universal leaf data-capture; task.belongsToActivity links to Activity)
  └── hasVisitObservation → VisitObservation[*]
```

**Activity sub-object** (~7 attrs / ~3 rels) — the universal work unit:
- `activityId` (URI)
- `activityName` (operator-friendly: "Vital Signs", "MRI Brain", "ECOG Status", "Drug X Administration", "EQ-5D-5L")
- `activityType` (coarse enum for operator categorization: PROCEDURE / ASSESSMENT / IP_ADMINISTRATION / SAMPLE_COLLECTION / QUESTIONNAIRE / IMAGING / OTHER) — used for filter/sort, not for specialization
- `activityStatus` (PERFORMED / NOT_PERFORMED / PARTIALLY_PERFORMED / RESCHEDULED) — NGSI-LD temporal property
- `validFrom` / `validUntil` — operational time window
- `governedBy → Document` (0..N) — protocol section / SOP that defines this Activity (references Document with section anchor)
- `usedEquipment → Equipment` (0..N) — `prov:used` semantics
- `performedBy → Person` (0..N) — `prov:wasAssociatedWith` semantics

PROV typing: `Activity rdfs:subClassOf prov:Activity` (per the v0.4.1 temporal+PROV native commitment). The PROV chain works identically regardless of activityType.

**Task sub-object** (~9 attrs / ~2 rels) — the universal leaf data-capture unit (this is the CRF entry / EDC item / Observation; one Task per measurement):
- `taskId` (URI)
- `taskName` (operator-friendly: "Systolic BP", "MRI Study Instance UID", "PHQ-9 Item 1", "Drug X dose")
- `taskValue` (Property whose value is polymorphic — see taskValueType)
- `taskValueType` (NUMERIC / TEXT / CODED / URI_REFERENCE / STRUCTURED / DATE / IMAGE_REFERENCE) — discriminates the value's shape
- `taskUnit` (UCUM where applicable: `[mmHg]`, `cm`, `mg`)
- `biomedicalConceptCode` (NCIt C-code; references COSMoS BC catalog) — what the Task IS
- `taskStatus` (COMPLETED / NOT_PERFORMED / PARTIALLY_COMPLETED) — NGSI-LD temporal property
- `notPerformedReason` (when NOT_PERFORMED)
- NGSI-LD `observedAt` Property metadata on `taskValue` — when the value was measured/captured (NOT a separate flat `performedDateTime` attribute; per the temporal+PROV native conventions)
- `belongsToActivity → Activity` (1..1; links to the parent Activity within the same Visit)
- `performedBy → Person` (1..1; `prov:wasAssociatedWith`)

**Why polymorphic taskValue is the key mechanism**:
- BP=128 → `taskValueType=NUMERIC`, `taskValue=128`, `taskUnit="[mmHg]"`, `biomedicalConceptCode=NCIt:C25298`
- MRI Study reference → `taskValueType=URI_REFERENCE`, `taskValue="urn:dicom:study/1.2.840.113654...."`, `biomedicalConceptCode=NCIt:C16809`
- PHQ-9 item response → `taskValueType=CODED`, `taskValue="2"`, `biomedicalConceptCode=LOINC:44261-6`
- IP dose recorded → `taskValueType=NUMERIC`, `taskValue=200`, `taskUnit="mg"`, `biomedicalConceptCode=NCIt:C172310`
- Lesion measurement (RECIST) → `taskValueType=STRUCTURED`, `taskValue={longestDiameter: 22, unit: "mm", lesionId: "L1"}`

External systems (DICOM PACS, lab LIS, ePRO platform, EHR) hold implementation specifics. TOP holds the universal trial-conduct-realm reference; the URI points to wherever the specialized artifact actually lives.

**This eliminates the need for specialized horizontals** like ImagingStudy, IPAdministration, QuestionnaireResponse. The substrate stays universal; specialization is content. The architectural moat: standards-up vendors model N entity types per therapeutic area; TOP carries one universal pattern that handles all of them.

**FHIR Questionnaire projection target**: TOP's universal Visit > Activity > Task hierarchy projects cleanly to FHIR R5 `Questionnaire` (form template) and `QuestionnaireResponse` (captured data). VisitDefinition + Activity-templates + Task-templates → Questionnaire JSON (consumable by Epic, Cerner, SMART on FHIR apps, ePRO vendors). Reverse projection (FHIR QuestionnaireResponse → TOP) ingests captured data from EHR/ePRO devices. One source of truth → many ephemeral renderings — exactly the projection-edge pattern.

### Decision 5 — Visit modes (DCT framing per ICH E6(R3) Annex 2)

Visit modes per ICH E6(R3) Annex 2 (decentralized clinical trials):

```
visitMode enum:
  IN_PERSON_CLINIC    — traditional clinic visit
  IN_PERSON_HOME      — home health visit (clinician travels to patient)
  REMOTE_VIDEO        — telehealth video visit
  REMOTE_PHONE        — telephone visit
  REMOTE_ASYNC        — eDiary / ePRO / async data capture
  HYBRID              — mix of in-person and remote elements in one visit
```

Maps to USDM Encounter.environmentalSettings + contactModes (which carry Codes; TOP collapses to enum per FIRST-PRINCIPLES). FHIR Encounter.virtualService is the equivalent indicator.

**Recommendation: include visitMode as Visit attribute with the 6-state enum above.** Critical for trial-feasibility analytics, post-COVID DCT design uptake, and twin synthesis (modality is a covariate).

### Decision 6 — Lifecycle states

Visit-occurrence lifecycle:

```
visitStatus enum:
  SCHEDULED        — appointment booked; visit not yet started
  IN_PROGRESS      — visit actively happening
  COMPLETED        — visit finished per protocol
  PARTIALLY_COMPLETED — visit happened but some activities not performed (rescheduled separately)
  MISSED           — visit was supposed to happen, didn't, no make-up scheduled yet
  RESCHEDULED      — visit moved to a new date (the Rescheduled visit is closed; a new SCHEDULED visit replaces it)
  CANCELLED        — visit cancelled (early termination, withdrawal, etc.)
  OUT_OF_WINDOW    — visit happened but outside the protocol-defined visit window (still recorded; protocol deviation flagged)
  UNSCHEDULED      — extra visit not in the SOA (urgent care, AE workup, sponsor-requested)
```

NGSI-LD temporal property on `visitStatus` (validFrom/validUntil per state value), parallel to Participant.participantStatus. Twin-queryability discipline extends to Visit.

**Recommendation: 9-state enum as above.** Fewer states forces operationally-meaningful states to fold together (e.g., MISSED collapsing into CANCELLED loses the "we tried to make this happen" vs "we cancelled it on purpose" distinction).

### Decision 7 — Protocol-deviation handling

Visits cause protocol deviations in three operationally-distinct ways:

1. **Out-of-window**: visit happened outside the protocol-defined visit window (visit window typically Day-3 to Day+3, configurable). Captured by `visitStatus=OUT_OF_WINDOW` and `protocolDeviationCode` attribute.
2. **Missed**: visit was supposed to happen, didn't, follow-up plan unclear or not yet documented. `visitStatus=MISSED`.
3. **Unscheduled**: extra visit not in the SOA. `visitStatus=UNSCHEDULED`. May be linked to an AE (when Event lifts) via the Visit→Event chain.

Recommendation: handle protocol deviations via the three lifecycle states above + a `protocolDeviationCode` attribute (free text or coded; aligns with sponsor-defined deviation taxonomies). A separate ProtocolDeviation sub-object can lift in v0.6+ if structured deviation modeling becomes operationally needed.

### Decision 8 — Scheduling semantics (planned-vs-actual datetimes)

Two timestamps per Visit-occurrence:

- `plannedStartDate` / `plannedEndDate` — what the SOA / scheduling system says
- `actualStartDate` / `actualStartTime` / `actualEndDate` / `actualEndTime` — what actually happened

Both kept distinct. The visit-window analytics ("was this visit on time?") use both. The SOA / VisitDefinition reaches into planned datetimes via the visit-template's offset from the protocol's anchor day (e.g., Day 1 for randomization).

### Decision 9 — Twin-queryability extension

Visit lifts the queryability surface for digital-twin synthesis significantly:

- Per-Participant time-series of Visits (with `visitDate` temporal axis)
- Per-Visit Activity-occurrences with their Observations (the actual measurements / assessments)
- Visit-window adherence (planned vs actual) as a covariate for drop-out prediction

**Recommendation: every Visit-occurrence and every Activity-occurrence is a queryable temporal record.** NGSI-LD temporal property on `visitStatus` (parallel to Participant); every Activity has `performedDate` + `performedTime` for time-series queries.

This is where the substrate decisions made in Participant pay off: Participant.hasVisit (when it un-flagged-misses) provides the trajectory the twin synthesizer needs.

## Cross-walk verification (FHIR R5 / SDTM / CDASH / USDM / OMOP)

Top-level **Visit** attributes:

| TOP attribute | FHIR R5 Encounter | SDTM SV | OMOP VISIT_OCCURRENCE | USDM | Notes |
|---|---|---|---|---|---|
| `visitId` (URI) | `Encounter.identifier` | (SUPPDM or implied) | visit_occurrence_id | n/a | Operator URI; SDTM derives from VISITNUM |
| `visitNumber` | `Encounter.identifier` (use=secondary) | VISITNUM | n/a | (via VisitDefinition.identifier) | Numeric ordering per protocol |
| `visitName` | `Encounter.type[].text` | VISIT | n/a | (via VisitDefinition.name) | "Screening Visit", "Day 1", "Week 12" |
| `visitMode` (6-state enum) | `Encounter.virtualService` (boolean indicator) + `Encounter.location` for in-person sub-mode | (SUPPDM) | visit_concept_id (with mode-specific concepts) | Encounter.environmentalSettings + contactModes Codes | DCT modality |
| `visitStatus` (9-state enum) | `Encounter.status` (planned / in-progress / completed / cancelled / etc.) | (computed from SVSTDTC presence + study disposition) | (computed) | n/a (template only) | NGSI-LD temporal property |
| `plannedStartDate` / `plannedEndDate` | `Encounter.plannedStartDate` / `plannedEndDate` | (computed via VISITDY + RFSTDTC) | (n/a) | (via VisitDefinition + ScheduleTimeline) | What the SOA says |
| `actualStartDate/Time` / `actualEndDate/Time` | `Encounter.actualPeriod` | SVSTDTC / SVENDTC | visit_start_datetime / visit_end_datetime | n/a | What happened |
| `visitDay` | (computed from study Day-anchor) | VISITDY | (n/a) | (via VisitDefinition relative-day) | Days from anchor (Day 1 typically randomization) |
| `protocolDeviationCode` | (extension) | (SUPPDM or DV domain) | (n/a) | n/a | Sponsor-defined |
| `unscheduledReason` | `Encounter.reason[].text` | SVUPDES | visit_source_value | n/a | When visitStatus=UNSCHEDULED |

Top-level **Visit** relationships:

| TOP relationship | FHIR R5 | SDTM | OMOP | USDM | Notes |
|---|---|---|---|---|---|
| `forParticipant → Participant` | `Encounter.subject` (Ref → Patient) | USUBJID | person_id | n/a | Whose visit |
| `forStudySite → StudySite` | `Encounter.serviceProvider` (Org) + `Encounter.location` | SITEID | care_site_id | (via StudySite) | Operational owner |
| `definedBy → VisitDefinition` | `Encounter.appointment.basedOn` (Ref → ServiceRequest derived from Protocol) | (computed from VISITNUM matching SOA grid) | (n/a) | Encounter (template) | Protocol-design link |
| `hasActivity → ActivityOccurrence (sub-object)` | `Encounter.diagnosis` + linked Procedure / Observation / Specimen / etc. | (procedure-level domains: VS, EC, EX, LB, etc.) | (linked tables: procedure_occurrence, measurement) | (Activity templates) | Per-Visit performed activities |
| `hasVisitObservation → VisitObservation (sub-object)` | (extension; or note Observation linked) | (NV / SUPPDM / DV) | (note table) | n/a | Operator-noticed things |
| `partOf → Visit (parent)` | `Encounter.partOf` | (n/a) | preceding_visit_occurrence_id (linked-list) | n/a | For multi-part visits or follow-up linkage |
| `hasAdverseEvent → Event` | (linked AdverseEvent) | (linked AE) | (linked condition_occurrence) | n/a | Flagged-missing until Event lifts |

Sub-object **VisitObservation**:

| TOP attribute | FHIR | SDTM | Notes |
|---|---|---|---|
| `observationText` | `Observation.note[].text` or `Encounter.note[]` | (NV / DV / SUPPDM) | Free text |
| `observationCategory` | `Observation.category[].coding` | (DV.DVDECOD or NV.NVDECOD) | Initial enum |
| `escalated` / `escalationDate` / `escalatedTo` | `Observation.basedOn` (linked AdverseEvent) | (linked AE record) | Reportability handoff |

Sub-object **ActivityOccurrence**:

| TOP attribute | FHIR | SDTM | OMOP | Notes |
|---|---|---|---|---|
| `activityName` | (Procedure.code / Observation.code / etc.) | (varies by domain: VSTEST, EXTRT, LBTEST) | (varies) | Operator-friendly |
| `activityType` (PROCEDURE / ASSESSMENT / IP_ADMIN / SAMPLE / QUESTIONNAIRE / IMAGING / OTHER) | (FHIR resource discriminator) | (SDTM domain discriminator) | (OMOP table discriminator) | Routes to projection target |
| `performedDate` / `performedTime` | (resource performed timestamp) | (per-domain DTC) | (per-table datetime) | When |
| `activityStatus` (PERFORMED / NOT_PERFORMED / etc.) | (resource.status) | (per-domain status field) | n/a | Whether |
| `biomedicalConceptCode` (NCIt C-code) | (resource.code.coding) | (per-domain code) | concept_id | NCIt / COSMoS BC catalog reference |

**USDM positioning**: TOP carries USDM at the design layer (VisitDefinition → USDM Encounter; ActivityTemplate when it lifts → USDM Activity), FHIR R5 at the operational/exchange layer (Visit → Encounter, ActivityOccurrence → Procedure/Observation/etc.), SDTM at the analysis layer (Visit → SV; ActivityOccurrence → per-domain projection), OMOP at the RWE layer (Visit → VISIT_OCCURRENCE).

## Source intermediate scope (the implementation lift)

After decisions above, the Visit lift would land:

- **Visit top-level** (~17 attrs / ~7 rels):
  - Identity: visitId, visitNumber, visitName
  - Lifecycle: visitStatus (NGSI-LD temporal property), visitMode
  - Datetimes: plannedStartDate, plannedEndDate, actualStartDate, actualStartTime, actualEndDate, actualEndTime, visitDay
  - Deviations: protocolDeviationCode, unscheduledReason
  - Tags
  - Temporal: validFrom, validUntil
  - Relationships: forParticipant, forStudySite, definedBy, hasActivity, hasVisitObservation, partOf, hasAdverseEvent (flagged-missing), hasTag (flagged-missing)
  - CTAs: Schedule Visit, Start Visit, Complete Visit, Reschedule Visit, Cancel Visit, Mark Missed, Record Observation, Escalate Observation, Add Activity, Mark Out-of-Window, Mark Unscheduled

- **VisitDefinition** (Study sub-object; ~10 attrs / ~3 rels):
  - Identity: visitDefinitionId, visitNumber, visitName
  - Schedule: visitDay, visitWindowMinDays, visitWindowMaxDays, expectedDuration
  - Description: description
  - Lifecycle: visitDefinitionStatus (DRAFT / EFFECTIVE / SUPERSEDED)
  - Relationships: appearsInSchedule (SOA), hasExpectedActivity (ActivityTemplate; lifts later)

- **ActivityOccurrence** (Visit sub-object; ~9 attrs / ~3 rels):
  - Identity: activityId, activityName
  - Type: activityType (7-state enum)
  - Datetimes: performedDate, performedTime
  - Lifecycle: activityStatus (4-state enum), notPerformedReason
  - Concept: biomedicalConceptCode (NCIt C-code; references COSMoS BC catalog when applicable)
  - Relationships: definedByActivityTemplate (0..1; flagged-missing until ActivityTemplate lifts), performedBy (Person), hasObservation (flagged-missing until Observation lifts as sub-object or Event-side entity)

- **VisitObservation** (Visit sub-object; ~6 attrs / ~2 rels):
  - Identity: observationId
  - Content: observationText, observationCategory (5-state enum)
  - Datetimes: observationDate, observationTime
  - Escalation: escalated (boolean), escalationDate, escalatedTo (Event ref; flagged-missing)
  - Relationships: recordedBy (Person), escalatedTo (Event; flagged-missing)

## SHACL invariants candidates

- (a) **Hard violation**: Visit with `visitStatus` in {COMPLETED, PARTIALLY_COMPLETED, OUT_OF_WINDOW} must have `actualStartDate` populated. Cannot have completed a visit without recording when it happened.
- (b) **Hard violation**: Visit with `visitStatus`=COMPLETED must have `actualEndDate` populated.
- (c) **Hard violation**: Visit with `visitStatus`=UNSCHEDULED must have `unscheduledReason` populated. UNSCHEDULED visits require operator justification per protocol-deviation discipline.
- (d) **Hard violation**: Visit's `forParticipant` and `forStudySite` must agree (i.e., Participant.forStudySite == Visit.forStudySite). Cross-entity consistency.
- (e) **Hard violation**: Visit's `forParticipant.forStudy` must match the Study referenced by `definedBy.appearsInSchedule`'s containing Study (when definedBy is populated). Cross-entity consistency at the Study level.
- (f) **Soft warning**: Visit with `visitStatus`=COMPLETED and `actualStartDate` / `actualEndDate` outside the `definedBy.visitWindowMinDays / visitWindowMaxDays` window should be flagged. Surfaces protocol-deviation candidates that operators may have forgotten to set OUT_OF_WINDOW.
- (g) **Hard violation**: Visit with `visitStatus`=OUT_OF_WINDOW must have `protocolDeviationCode` populated.
- (h) **Hard violation**: ActivityOccurrence with `activityStatus`=NOT_PERFORMED must have `notPerformedReason` populated.
- (i) **Soft warning**: VisitObservation with `escalated`=true should have `escalatedTo` populated (when Event lifts). Surfaces ungrounded escalation flags.

Eight to nine new invariants. Total invariants moves 25 → 33-34.

## Worked example plan

Extend the MSKCC ONCO-423 example (already has Maria as Participant in ON_TREATMENT state). Add:

- 2-3 VisitDefinitions on the Study (Screening Visit, Visit 1 / Day 1, Visit 4 / Day 28)
- 2-3 Visit-occurrences for Maria:
  - Visit 1 / Day 1: COMPLETED, in-window, with 4-5 ActivityOccurrences (vital signs, ECOG, blood draw, IP administration, ECG)
  - Visit 4 / Day 28: COMPLETED, OUT_OF_WINDOW (visit happened on Day 31 due to scheduling), with `protocolDeviationCode` populated
  - One UNSCHEDULED visit for an AE workup (with `unscheduledReason` and a VisitObservation that escalated to a flagged-missing Event reference)
- Demonstrate visitMode variation: one visit IN_PERSON_CLINIC, one REMOTE_PHONE for follow-up

## Open questions for Bo

1. **Confirm Decision 1**: separate VisitDefinition (Study sub-object) + Visit (top-level occurrence)? Recommendation: yes. Lifts Visit as sixth top-level; VisitDefinition becomes the seventh Study sub-object.
2. **Confirm Decision 4**: ActivityOccurrence as Visit sub-object (deferring ActivityTemplate to v0.6)? Recommendation: yes.
3. **Confirm Decision 5**: 6-state visitMode enum (IN_PERSON_CLINIC / IN_PERSON_HOME / REMOTE_VIDEO / REMOTE_PHONE / REMOTE_ASYNC / HYBRID)? Recommendation: yes.
4. **Confirm Decision 6**: 9-state visitStatus enum? Operators legitimately distinguish all 9 in their daily workflow; trade-off is more SHACL state-machine invariants.
5. **Activity types enum**: PROCEDURE / ASSESSMENT / IP_ADMINISTRATION / SAMPLE_COLLECTION / QUESTIONNAIRE / IMAGING / OTHER (7 states). Right scope? Anything to add or drop?
6. **VisitObservation category enum**: PROTOCOL_DEVIATION / SAFETY_SIGNAL / DATA_DISCREPANCY / OPERATIONAL_NOTE / OTHER (5 states). Right scope?
7. **Visit windowing**: visitWindowMinDays / visitWindowMaxDays as VisitDefinition attributes (per-template) — vs Visit-side actual-vs-window calculation? Recommendation: VisitDefinition holds the window; SHACL invariant (f) checks adherence.
8. **biomedicalConceptCode reach**: should ActivityOccurrence carry NCIt C-codes for the procedures/assessments performed? Recommendation: yes — sets up the COSMoS BC catalog touch-point (per CDISC ecosystem alignment note PR #5) without requiring TOP to model BCs internally.

## Estimated lift scope

Once decisions are sealed:

- Source intermediate: ~17 attrs / 7 rels on Visit; ~10 attrs on VisitDefinition (Study sub-object); ~9 attrs on ActivityOccurrence (Visit sub-object); ~6 attrs on VisitObservation (Visit sub-object). About 42 attrs total in the lift, distributed across 4 entities.
- SHACL invariants: 8-9 new (33-34 total in the graph).
- Spec doc: ~700 lines (between Site's 977 and Study's 659; Visit straddles design and operations and needs both stories).
- Worked example: extend MSKCC ONCO-423 with VisitDefinitions + Maria's Visit-occurrences + ActivityOccurrences.
- Verification history: ~10 questions.

Single PR. Follows the patterns established by Sponsor / Site / Study / Participant.

## Pointers

- [`visit-spec.html`](visit-spec.html) — to be written; this note seeds it.
- [`participant-planning.md`](participant-planning.md) — Participant lift (where the boundary pattern was established).
- [`participant-spec.html`](participant-spec.html) — Participant spec (where Decision 10 twin-queryability was set, extending to Visit here).
- [`top-strawman.json`](../source/top-strawman.json) — source intermediate.
- [`study-spec.html`](study-spec.html) — Study spec; SOA + future VisitDefinition reach into Study sub-objects.
- [`site-spec.html`](site-spec.html) — Site/StudySite spec; StudySite.hostsVisit is the un-flag-missed edge after this lift.
- [`FIRST-PRINCIPLES.md`](../../../FIRST-PRINCIPLES.md) — operator-grounded substrate; cross-walks below the line.
- [USDM v4 Encounter](https://github.com/cdisc-org/usdm/blob/main/src/usdm_model/encounter.py) — verified reference for VisitDefinition cross-walk.
- ICH E6(R3) Annex 2 — DCT framing for visitMode enum.
