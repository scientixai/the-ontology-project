# Participant spec planning note (working draft)

> Working document. Surfaces the architectural decisions Participant has to make before the source-intermediate lift and the spec-doc draft. Folds into `participant-spec.html` once the decisions below are sealed.
> Last touched 2026-05-08.

## Purpose

Participant is the fourth top-level to lift to full spec discipline (after Sponsor v0.1.4, Site/StudySite v0.2.0, Study v0.3.0). Bo's question — Participant before Visit, given that Participant has fewer architectural ambiguities and stands alone better — is the right call. This note captures the architectural decisions Participant has to make so Bo can weigh in before implementation.

## Current state

The Participant entity is not yet in the source intermediate. The OOUX Participant object is well-specified (~30 attributes, ~30 relationships listed) but carries the same OOUX-level error as Visit: it points directly at `1 Site` rather than at StudySite. The Site spec tracked this correction; Participant lift applies it.

## Where Participant sits in the operational hierarchy

```
Site ─→ StudySite ─→ Study ─→ Protocol ─→ SOA ─→ Visit ─→ Activity
              │
              ↓
         Participant ←── enrolled via StudySite, attends Visits-occurrences,
                         consents to Study Protocol, may be assigned to an Arm
```

Participant is anchored by StudySite (1..1) — every Participant is enrolled at exactly one StudySite for exactly one Study. Multi-Study participation is modeled as separate Participant entities (one per Study). Cross-Study identity resolution is a federation concern, downstream.

## Standards alignment posture (critical context)

A meaningful finding from cross-walking against USDM v3: **USDM does not model per-subject runtime data.** Verified against `cdisc-org/usdm/src/usdm_model/`: there is no `study_subject.py`. The closest entity is `SubjectEnrollment` — an aggregate quantity (planned enrollment count for a cohort/site/geographic scope), not a per-subject entity. USDM is a **study-definition** model (design, arms, endpoints, criteria, schedule); per-subject data lives at a different standards layer.

This means TOP Participant's primary cross-walk targets are not USDM but the operational/analysis standards that DO model subjects:

- **FHIR R5 `ResearchSubject`** (canonical operational standard) — has `status`, `progress` (a list of state-change events with type, subjectState, milestone, reason, startDate, endDate), `period`, `study` (Ref → ResearchStudy), `subject` (Ref → Patient), `assignedComparisonGroup`, `actualComparisonGroup`, `consent` (Ref → Consent, 0..N supporting re-consent). **TOP Participant maps directly.** My sub-object approach (Consent / Screening / Enrollment / Withdrawal) corresponds to FHIR `progress` entries.
- **CDISC SDTM `DM` (Demographics)** (canonical analysis/submission standard) — USUBJID, SUBJID, SEX, RACE, ETHNIC, BRTHDTC, AGE, AGEU, COUNTRY, RFSTDTC, RFENDTC, RFICDTC, ARMCD, ACTARMCD, SITEID, INVID. **TOP Participant attributes project here.**
- **CDISC SDTM `DS` (Disposition)** (canonical event-stream standard) — DSDECOD controlled terminology covers SCREEN FAILURE / INFORMED CONSENT OBTAINED / ENROLLED / RANDOMIZED / COMPLETED / DISCONTINUED / WITHDRAWAL OF CONSENT / LOST TO FOLLOW-UP / DEATH / PROTOCOL DEVIATION / etc. **TOP sub-objects (InformedConsent / ScreeningRecord / EnrollmentRecord / WithdrawalRecord) ARE the SDTM DS records.** The sub-object decision turns out to be exactly the SDTM DS domain pattern.
- **CDISC CDASH `DM`** — acquisition-side equivalent of SDTM DM (CRF-level).
- **USDM** — referenced indirectly: TOP Participant points at TOP Study, and TOP Study cross-walks to USDM. The Participant-level link to USDM is via the Study.

**This validates the architectural decisions stronger than I originally noted.** The sub-object pattern for lifecycle events is the SDTM DS domain pattern. The lifecycle enum should align with SDTM DSDECOD controlled terminology and FHIR ResearchSubjectStatus value set. Demographics fields should map directly to SDTM DM columns. Below, every decision now carries explicit cross-walk verification.

## USDM/M11 ingest boundary (full-automation posture)

A foundational TOP requirement: the design layer of every Study must be **derivable from a USDM v3 / ICH M11 compliant protocol document via automated ingestion**. No human in the loop for design-side entity creation. The pipeline shape is:

```
USDM v3 / M11 protocol (JSON)  ──[ingester]──▶  TOP NGSI-LD entities (Study, Protocol, Arm,
                                                  ScheduleOfAssessments, Endpoint,
                                                  Inclusion/Exclusion criteria, Visit, Activity)
```

**Participant sits on the operational side of that boundary.** USDM v3 has no per-subject entity (verified — see "Standards alignment posture" above), so:

- TOP `Participant` entities are NOT created by USDM ingest. They are created at runtime by operational systems (eConsent, EDC, IRT, CTMS) when real humans enroll.
- TOP `Participant.forStudy → Study`, `Participant.assignedToArm → Arm`, `Participant.hasEnrollmentRecord.protocolVersionAtEnrollment → StudyVersion` MUST resolve to entities that the USDM ingester previously created. The ingester's URI minting policy and the operational system's Participant-creation policy MUST share an identifier scheme.
- Provisional URI policy (to be sealed alongside the ingester):
  - Study: `urn:top:study:{usdm_study_id}`
  - StudyVersion: `urn:top:study:{usdm_study_id}/version:{usdm_version_id}`
  - Arm: `urn:top:study:{usdm_study_id}/arm:{usdm_arm_id}`
  - EligibilityCriterion: `urn:top:study:{usdm_study_id}/eligibility:{usdm_criterion_id}`
  - SOA / Visit / Activity: `urn:top:study:{usdm_study_id}/soa:{usdm_timeline_id}/visit:{usdm_encounter_id}/activity:{usdm_activity_id}`

  USDM `id` fields are stable within a document version; TOP URIs derive deterministically. Re-ingesting an amended protocol produces stable URIs for unchanged entities and new URIs for added entities.

- The Participant spec carries the canonical identifier-resolution example: a Participant created by an EDC at enrollment time references `urn:top:study:{usdm_study_id}/arm:{usdm_arm_id}` — the same URI the ingester wrote — and the SHACL invariant `Participant.assignedToArm.forStudy == Participant.forStudy` resolves cleanly because both ingester and EDC follow the URI policy.

**System pattern this codifies.** USDM ingest is the source of design truth; operational systems are the source of runtime truth; both meet at TOP through a shared identifier scheme. Participant is the canonical "operational-side, design-referencing" entity.

(Open question added below: is the `urn:top:...` URI policy correct, or should TOP defer to USDM's own URN scheme?)

## Multi-realm projection — Mary in five rooms

Per [`FIRST-PRINCIPLES.md`](../../../../FIRST-PRINCIPLES.md): a participant is a participant, full stop. Operators say "Mary." That's the anchor. *Realms* and *states* are the lenses different operators look at Mary through:

| Realm | Operator role | Mary appears as | Standards projection |
| --- | --- | --- | --- |
| **Recruitment** | Recruiter / outreach coordinator | A `Recruit` (responder, in funnel, pre-consent) | (no canonical standard; sponsor-internal) |
| **Trial conduct** | Study coordinator / PI / monitor | A `Participant` (consented through completion / withdrawal) | FHIR `ResearchSubject`, SDTM `DM` + `DS`, USDM (no per-subject) |
| **Standard care** | Primary care nurse / treating physician | A `Patient` (clinical relationship outside the study) | FHIR `Patient`, USCDI, OMOP `PERSON` |
| **Claims / payer** | Claims processor / payer ops | A `Claimant` / `Member` | FHIR `Claim` / `Coverage`, X12 837, NCPDP |
| **Real-world evidence** | Epidemiologist / RWE analyst | A `Patient` (post-trial, observed in EMR/claims) | OMOP CDM, Sentinel, PCORnet CDM |

**TOP carries one realm: trial conduct.** TOP `Participant` is the Mary-as-trial-subject role-entity. Other realms are out of TOP's scope as entities — they are *projection targets* handled by separate adapters (FHIR adapter for Patient, OMOP projector for RWE, claims adapter for Claimant).

**This is the same projection-edge pattern as standards.** Just as TOP doesn't carry FHIR `Patient` shape but emits Patient via the FHIR adapter, TOP doesn't carry Mary-as-Claimant but emits a Claimant view via a claims adapter. The substrate persists; the projections are ephemeral.

**Identity resolution across realms is federation, not substrate.** Mary's Participant URI in TOP, Mary's Patient URI in her PCP's FHIR server, Mary's Claimant ID in her insurer's system — these resolve to the same human via Datavant tokens, master patient indexes, or cross-realm trust agreements. TOP doesn't model this resolution; it provides the substrate that *can be resolved against* at the deployment edge.

**Pre-consent is a real workflow boundary** (new architectural decision below — see Decision 9). Recruiters work with people who haven't yet entered the trial-conduct realm. Whether `Recruit` becomes a separate TOP entity or is folded as a pre-consent state on `Participant` is the architectural call.

## Digital-twin posture — Mary as a model

A participant — at any stage (recruit, screening, randomized, on-treatment, post-trial) — needs to be **spec-able as a digital twin**. Twin synthesis is a major axis of research workflow now (synthetic control arms, in-silico trials, individual outcome prediction, shadow-enrollment dashboards) and TOP's posture matters because the twin is a high-value derivative.

**TOP's posture: digital twin is a projection lens, not an entity.** Same pattern as everything else in this note. The TOP Participant carries the substrate; a *twin synthesizer* (model-driven, not part of TOP) reads from TOP and emits a twin representation.

**What TOP must guarantee for the substrate to be twin-spec-able**: every Participant — at every stage — must be queryable along the dimensions a twin needs. Not "TOP carries the twin"; *"TOP carries enough that a twin can be derived."*

The dimensions the twin synthesizer needs:

| Twin dimension | TOP source |
| --- | --- |
| **Demographic substrate** | Participant attributes (sex, dateOfBirth, race, ethnicity, country) |
| **Disease state at entry** | ScreeningRecord + Activity occurrences during screening (when Visit/Activity lift) |
| **Treatment assignment** | EnrollmentRecord + assignedToArm + protocolVersionAtEnrollment (Arm carries intervention reach via the USDM-ingester chain) |
| **Time-varying observations** | Visit / Activity / Observation occurrences (when those lift) |
| **Lifecycle state trajectory** | participantStatus over time (the 11-state enum carries this; sub-objects carry the state-change events) |
| **Outcome trajectory** | Endpoint values + AE occurrences (when those lift) + final state (COMPLETED / WITHDRAWN / DISCONTINUED / etc.) |
| **Cross-realm context** (when federation provides it) | Linked Patient (FHIR), Claimant (claims), historical Patient (OMOP) — at the deployment edge, not in TOP substrate |

**Implication for Participant entity design**: every attribute, every relationship, every sub-object is queryable across the participant's lifetime. The lifecycle states (SCREENING → CONSENTED → ENROLLED → RANDOMIZED → ON_TREATMENT → ...) are not just labels; they are *queryable temporal axes* the twin synthesizer reads. The `validFrom` / `validUntil` temporal pattern (already used on Sponsor and StudySite for relationship handoffs) extends to Participant attributes that change over time.

**Implication for the lifecycle enum (Decision 6)**: every state transition must produce a queryable record. The sub-object pattern already does this for the canonical events (Consent, Screening, Enrollment, Withdrawal). State transitions inside on-trial states (ON_TREATMENT → IN_FOLLOW_UP) need either a new sub-object (`StateTransition`?) or temporal-property semantics on `participantStatus` itself.

**Twin spec is a separate document, not a TOP substrate decision** — but it shapes the substrate. The actionable implication for v0.4 Participant: ensure every lifecycle transition leaves an audit-queryable record (sub-object OR temporal-property change) so a twin synthesizer downstream can reconstruct the trajectory.

**What's NOT in TOP**: the twin model itself (computational artifact), the twin synthesis logic, the twin's predicted outputs, the model-version-vs-Participant linkage. Those live in twin-synthesizer infrastructure, not TOP substrate. TOP provides the contract; the synthesizer fulfills it.

### Prior art — PMDT (Patient Medical Digital Twin, El Gammal et al., under review at SoSyM)

The ontology-driven digital-twin direction is validated in real-world deployment: the **Patient Medical Digital Twin (PMDT)** framework (El Gammal et al., authored at ServTech / Cairo University / FernUniversität / Macquarie / UNSW, currently under review at *Software and Systems Modeling*) is an OWL 2.0 ontology for chronic-care patient digital twins, validated in the EU H2020 **QUALITOP** project pilot with real-world immunotherapy patients. Reference for TOP's twin posture; not a dependency.

**PMDT's modular Blueprints map roughly to TOP's expected lift trajectory:**

| PMDT Blueprint | TOP entity (current or expected) | Realm |
| --- | --- | --- |
| Patient | `Participant` (trial realm) / `Patient` projection (care realm) | Trial / care |
| Disease and diagnosis | `Condition` (when it lifts; currently `conditionStudied` is a string on Study) | Trial |
| Treatment and follow-up | `Activity` + `IPDispensation` (when they lift) | Trial |
| Trajectories | The twin-queryability discipline above (Decision 10) | Trial |
| Safety | `AdverseEvent` (when it lifts; flagged-missing currently) | Trial |
| Pathways | `ScheduleOfAssessments` + Activity-flow (in progress, post-Visit) | Trial |
| Adverse events | `AdverseEvent` (separate from Safety in PMDT's framing) | Trial |

PMDT's structural carving is good prior-art for what TOP will need to address as the clinical-trials reference graph matures past Participant. Useful as a sanity check rather than a blueprint to copy directly — PMDT serves *chronic care* (continuous, longitudinal, post-diagnosis) while TOP clinical-trials serves *trial conduct* (bounded, protocol-driven). Adjacent realms; different operational tempos; same underlying human anchor.

**Substrate divergence**: PMDT is **OWL 2.0** (DL-classical, optimized for SPARQL reasoning). TOP is **NGSI-LD / JSON-LD-native** (broker-based, optimized for operational data exchange + temporal-property semantics + streaming). These are different ontology paradigms, both legitimate. **TOP can export to OWL/RDF as another projection edge** — same pattern as FHIR/SDTM/USDM exports — for downstream tools that prefer classical-reasoning toolchains. This is one more projection adapter, not a substrate change. Per FIRST-PRINCIPLES, the substrate stays in the operator-grounded paradigm; OWL is downstream.

**Reference-ontology alignments PMDT uses, that TOP will need when it lifts the relevant entities:**
- **Disease Ontology (DO)** — for `Condition` semantics (when Condition lifts; currently absent in TOP)
- **OWL-Time** — for temporal-trajectory reasoning (TOP uses NGSI-LD's native temporal-property semantics; OWL-Time is the projection target when TOP exports to OWL)
- **CTCAE** (Common Terminology Criteria for Adverse Events) — for AdverseEvent grading (when AE lifts)
- **GDPR-compliant federated analytics** — prior art for cross-realm identity resolution (which TOP defers as a federation concern in v0.6+)

These reference ontologies belong in the [CDISC dependency pipeline manifest](cdisc-dependency-pipeline.md) when TOP picks them up — same pattern as USDM / FHIR / SDTMIG.

**Federation lessons from QUALITOP**: PMDT's multi-institutional, privacy-preserving federation in real-world immunotherapy deployment is direct prior art for what TOP will need when cross-realm identity resolution becomes operational (per the multi-realm posture above). When TOP reaches v0.6+ federation work, the QUALITOP architecture and pilot lessons are reference material.

**Net read**: PMDT validates the ontology-driven twin approach, sanity-checks TOP's expected entity lift trajectory, and provides useful federation prior-art. TOP's clinical-trials reference graph and PMDT's chronic-care framework cover different realms with the same underlying conviction (semantic substrate + ephemeral analytics on top). Citing PMDT alongside FHIR / SDTM / USDM in the spec doc strengthens the standards-and-prior-art posture for community/regulator review.

## Architectural decisions to seal

### Decision 1 — Sub-objects for lifecycle events

Participant has several lifecycle events that have their own structure (date, signatures, witnesses, document references, lifecycle state). Two ways to model:

**Option A (recommended): each lifecycle event is a sub-object under Participant.** Sub-objects: InformedConsent, ScreeningRecord, EnrollmentRecord, WithdrawalRecord. Each carries its own dates, signatures, witness, document reference, lifecycle status. Aligns with GCP audit-trail discipline (full event history); supports re-consent after protocol amendment, re-screening, multiple withdrawals if re-enrolled.

**Option B: each is a flat attribute set on Participant.** consentSignedDate, consentSignedBy, consentWitnessedBy, consentVersion, screeningStartDate, screeningEndDate, screenFailReason, enrollmentDate, etc. Simpler model; loses event-history audit fidelity. Re-consent and re-screening become rewrites rather than appended events.

**Recommendation: Option A.** GCP audit demands the full event history; sub-objects encode that. The Sponsor spec's "Sponsor is per-Org-per-Study" pattern and the Site spec's StudySite sub-pivot pattern both established sub-object containment for events that have their own lifecycle. Participant's lifecycle events follow the same pattern.

**Cross-walk validation.** This decision lines up with both authoritative standards that DO model per-subject events:
- **FHIR R5 `ResearchSubject.progress`** — a 0..N list of state-change events, each with `type`, `subjectState`, `milestone`, `reason`, `startDate`, `endDate`. TOP sub-objects map 1:1 to `progress` entries.
- **CDISC SDTM `DS` (Disposition) domain** — every disposition event is its own DS record with USUBJID, DSDECOD (controlled term), DSSTDTC, DSTERM, EPOCH. TOP InformedConsent / ScreeningRecord / EnrollmentRecord / WithdrawalRecord each project to one or more DS records with the appropriate DSDECOD code.

Sub-objects-as-events is the SDTM DS pattern. Reviewers familiar with SDTM should recognize it immediately.

Trade-off accepted: 4 new sub-objects under Participant (InformedConsent, ScreeningRecord, EnrollmentRecord, WithdrawalRecord). Sub-object count is similar to Study (which has 6).

### Decision 2 — Demographics PHI posture

Participant carries demographics that, in production, are PHI. Three options for how the schema relates to identification:

**Option A: schema carries identifying demographics directly** (firstName, lastName, dateOfBirth, fullAddress). Operator portals see real values. PHI handling is the deployment's problem.

**Option B: schema carries de-identified fields only** (yearOfBirth, age-at-screening, sex, race, ethnicity). HIPAA Safe Harbor compliant by construction. Loses operator-grounding (Site Coordinator can't call participant by name from this schema).

**Option C (recommended): schema is identification-status-agnostic.** Same fields exist; deployment populates with real values for operator-facing systems and Datavant tokens / de-identified values for research-facing systems. The schema doesn't encode identification status; the deployment handles tokenization, date-shifting, and redaction at the boundary between operator-grounded data and research-warehouse projections.

**Recommendation: Option C.** Same posture established in Site spec for de-identification (TOP is upstream of de-id; Datavant + John Snow Labs handle privacy engineering at the deployment layer). Participant follows the same posture. Document it in the spec; don't try to encode it in the schema.

Practical implication: demographics fields the schema carries are operator-grounded — fields the operator actually uses. Recommended set, with explicit SDTM DM / FHIR / CDASH cross-walks:

| TOP attribute | SDTM DM column | FHIR (R5) target | CDASH DM | Notes |
| --- | --- | --- | --- | --- |
| `participantId` (URI) | USUBJID (Unique Subject ID) | `ResearchSubject.identifier` | SUBJID | TOP carries URI; SDTM USUBJID is `STUDYID-SITEID-SUBJID` concatenation, derivable |
| `screeningNumber` | SUBJID (Subject ID for the Study) | `ResearchSubject.identifier` (use=secondary) | SUBJID | Site-assigned; matches CDASH/SDTM SUBJID |
| `randomizationNumber` | (often a SUPPDM qualifier or kit-level ID) | (not standardized; kept on TOP as operator-facing) | RANDNO (custom) | Sponsor-assigned at randomization |
| `firstName` / `middleName` / `lastName` | not in SDTM (PHI excluded) | `Patient.name.given` / `.family` (linked via `ResearchSubject.subject`) | not in CDASH | Operator-grounded only; never enters SDTM submission |
| `dateOfBirth` | BRTHDTC (ISO 8601) | `Patient.birthDate` | BRTHDAT / BRTHDD/BRTHMO/BRTHYY | May be year-only or shifted in research projections |
| `sex` (MALE / FEMALE / INTERSEX / UNKNOWN / NOT_REPORTED) | SEX (M / F / U / UNDIFFERENTIATED) | `Patient.gender` (male / female / other / unknown) | SEX | Biological sex per ICH E5 / FDA; controlled term mappings documented in spec |
| `race` | RACE (CDISC controlled term) | `Patient.extension[us-core-race]` | RACE | May be comma-separated for multiracial; SDTM uses MULTIPLE + SUPPDM RACEMUL |
| `ethnicity` | ETHNIC (HISPANIC OR LATINO / NOT HISPANIC OR LATINO / NOT REPORTED / UNKNOWN) | `Patient.extension[us-core-ethnicity]` | ETHNIC | CDISC controlled term |
| `primaryLanguage` (ISO 639-1) | (not in SDTM DM) | `Patient.communication.language` | (CDASH custom) | Operator-grounded |
| `country` (ISO 3166-1 alpha-3) | COUNTRY (ISO 3166-1 alpha-3) | `Patient.address.country` | COUNTRY | Direct match |

The sex enum deliberately uses the longer form (MALE/FEMALE/INTERSEX/UNKNOWN/NOT_REPORTED) for operator clarity; the `mapsTo` annotation in the source intermediate carries the SDTM SEX single-letter code projection. INTERSEX maps to SDTM `UNDIFFERENTIATED` per CDISC controlled terminology; FHIR `Patient.gender` carries `other` with the underlying `Observation` for biological detail.

### Decision 3 — StudySite anchoring (apply OOUX correction)

Per the operational hierarchy: Participant.forStudySite → StudySite (1..1). NOT Participant → Site directly.

This is the OOUX correction tracked in both the Site spec and the Study spec. Participant lift applies it. The OOUX has Participant pointing at `1 Site`; should be `1 StudySite`.

Settled. Apply.

### Decision 4 — Subject vs Person

Person (TOP commons horizontal, lifted in v0.2.0) is for staff: investigators, coordinators, monitors, pharmacists, regulatory affairs. Participant is for trial subjects. Different role, different entity. Subject identity is bound to the Study; Person identity is independent of any Study.

Settled by the Site spec. Document explicitly in the Participant spec to avoid confusion.

Edge case: a study staff member who is also enrolled as a participant in the same study (rare; some Phase 1 dose-escalation studies have staff as healthy volunteers). In TOP, that's two entities — one Person record (staff role) and one Participant record (subject role) — backed by the same real human. The schema doesn't link them; that's deliberate (privacy-preserving).

### Decision 5 — Arm assignment

How does the Participant link to an Arm?

**Option A: simple relationship.** `Participant.assignedToArm → Arm` (0..1; 0 in pre-randomization, 1..1 once randomized). Capture randomization date as a Participant attribute.

**Option B: RandomizationRecord sub-object.** Sub-object with arm assignment, randomization date, randomization method (block, stratified, etc.), randomization seed/sequence reference, possibly stratification factor values.

**Recommendation: Option A for v0.4.0.** Simple relationship plus `randomizationNumber` and `randomizationDate` attributes on Participant. RandomizationRecord lifts as a sub-object in v0.5+ if studies with complex stratification or multiple-arm-reassignments warrant it.

### Decision 6 — Lifecycle status enum

Participant has a complex lifecycle. Comprehensive enum proposal — and explicit cross-walk to FHIR `ResearchSubjectStatus` value set and SDTM DS `DSDECOD` controlled terminology:

| TOP `participantStatus` | FHIR R5 `ResearchSubject.status` | SDTM DS `DSDECOD` (event-record term) | Notes |
| --- | --- | --- | --- |
| `SCREENING` | `screening` | (no DS event; pre-screening start may appear as INFORMED CONSENT OBTAINED followed by screening procedures) | Operational state during screening window |
| `SCREEN_FAILED` | `ineligible` | `SCREEN FAILURE` | DS record carries DSCAT=DISPOSITION EVENT, DSSCAT=STUDY PARTICIPATION |
| `CONSENTED` | `pending-on-study` | `INFORMED CONSENT OBTAINED` | When consent precedes enrollment as a separate state |
| `ENROLLED` | `on-study` | `ENROLLED` | Single-arm or pre-randomization "enrolled" state |
| `RANDOMIZED` | `on-study` | `RANDOMIZED` | DS record marks arm assignment |
| `ON_TREATMENT` | `on-study-intervention` | (treatment start as separate EX/DS depending on Sponsor convention) | Active treatment phase |
| `IN_FOLLOW_UP` | `follow-up` | (follow-up start) | Post-treatment follow-up phase |
| `COMPLETED` | `off-study` | `COMPLETED` | Per-protocol completion |
| `WITHDRAWN` | `withdrawn` | `WITHDRAWAL OF CONSENT` (or `WITHDRAWAL BY SUBJECT`) | Subject-initiated; consent withdrawal is the canonical case |
| `DISCONTINUED` | `off-study` | `DISCONTINUED` (with reason in DSTERM/DSREAS) | Investigator-initiated discontinuation |
| `LOST_TO_FOLLOW_UP` | `off-study` | `LOST TO FOLLOW-UP` | Common DS code |

11 states. Operationally meaningful — operators distinguish these in their daily workflow (a coordinator preparing for tomorrow's visits queries `ON_TREATMENT` participants; a Sponsor PM tracking enrollment queries `RANDOMIZED` count; a regulator looking at safety queries `DISCONTINUED` participants and reasons).

The TOP enum is a superset of FHIR `ResearchSubjectStatus` (FHIR collapses several operational states under `on-study` and `off-study`). The TOP-to-FHIR mapping is many-to-one and well-defined; the inverse is one-to-many and requires sub-object/DS context to disambiguate. Spec doc carries the full mapping table and a `valueSet` reference to FHIR `ValueSet/research-subject-state`.

Trade-off: more enum values = more SHACL invariants to think about. The lifecycle transitions form a state machine; SHACL invariants encode legal transitions.

### Decision 7 — Multi-Study participation

Can a Participant entity span multiple Studies?

OOUX has Participant with `1 Study`. TOP follows: each Study participation is its own Participant entity. A real human enrolling in two studies has two Participant entities (one per Study).

Cross-Study linking (the same human across multiple Participant records) is an identity-resolution concern, downstream:
- Within an institution: linking via Datavant tokens or a local master patient index
- Across institutions: federation concern, not part of v0.4.0

Document the per-Study-Participant scoping. Don't attempt cross-Study linking in the schema.

### Decision 8 — Adverse event / lab result / sample / IP-dispensation reach

Participant has a LOT of OOUX outbound relationships (~30). Most are to entities that haven't lifted yet (Visit, AE, SAE, LabResult, Sample, IPDispensation, CRF, Discrepancy, etc.). Same direct-vs-traversed discipline as Site:

- **Direct on Participant** (per-Participant attributes that are subject-bound, not visit-bound): demographics, identifiers, lifecycle status, sub-objects (Consent, Screening, Enrollment, Withdrawal).
- **Reached via traversal**: Visit-occurrences (via Visit → atParticipant inverse, when Visit lifts), AEs (via AE → atParticipant, when Event lifts), CRFs (via CRF → forParticipant, when CRF lifts), etc.

For relationships that are deferred (target entity not yet lifted), use the existing flagged-missing pattern.

Recommend modest direct-edge set for v0.4.0:
- `forStudySite → StudySite` (1..1, anchoring)
- `forStudy → Study` (1..1, traversable from forStudySite but kept direct for query convenience)
- `assignedToArm → Arm` (0..1)
- Sub-objects: `hasInformedConsent`, `hasScreeningRecord`, `hasEnrollmentRecord`, `hasWithdrawalRecord` (each 0..N or 0..1; multi-event lifecycles like re-consent need multi-cardinality)
- Flagged-missing forward references: `hasVisit → Visit` (0..N), `hasAdverseEvent → Event` (0..N) — with explicit `_targetMissing` markers

Defer everything else to traversal or to later passes.

### Decision 9 — Recruit (pre-consent) as separate entity vs pre-Participant state

The recruitment realm has its own operator (recruiter / outreach coordinator), its own workflow (response to ads, pre-screening calls, eligibility pre-check, contact attempts), and its own data shape (lighter than full Participant — no consent, no enrollment, often no full demographics, sometimes only a phone number and a name).

When a Recruit consents, they become a Participant. **Question: does Recruit get its own TOP entity, or fold as a pre-consent state on Participant?**

**Option A (recommended for v0.4.0): separate `Recruit` top-level entity.** Lift Recruit alongside Participant. Recruit carries: contactInfo, recruitmentSource, contactAttempts[], preScreeningOutcome, eligibilityPreCheck, prospectStatus (RESPONDED / CONTACTED / PRE-SCREENED / SCHEDULED / NO_SHOW / DECLINED / CONVERTED_TO_PARTICIPANT / DROPPED). Recruit→Participant transition is a separate workflow event (consent triggers the conversion). Recruit data is typically not PHI in the same way (no full DOB, no medical history).
- Pro: matches recruitment-coordinator workflow; respects PHI boundary (recruiter doesn't need full demographics); Recruit data can be retained separately for unconverted-recruit analytics
- Pro per FIRST-PRINCIPLES: recruiter is a real operator role with a distinct workflow; their entity should not be a hidden state on someone else's

**Option B: pre-consent state on Participant.** Add `RECRUIT` and `PRE_SCREENING` to the lifecycle enum. Participant entity exists pre-consent.
- Pro: simpler entity count
- Con: forces full Participant shape on incomplete data; PHI boundary leaks; recruiter and coordinator share an entity even though their workflows differ

**Recommendation: Option A.** Recruit lifts as a separate top-level (or commons horizontal — TBD). v0.4 Participant lift should NOT include pre-consent states; the lifecycle enum starts at SCREENING (after consent has been obtained but during eligibility verification). Recruit→Participant transition is captured by Participant.hasInformedConsent linkage (the InformedConsent sub-object's existence IS the conversion event).

Implication: TOP top-level count moves from 8 to 9 (or Recruit lifts as a horizontal — open architectural question). Tracked.

### Decision 10 — Twin-queryability discipline

Per the digital-twin posture above: every Participant lifecycle transition must produce a queryable record so a downstream twin synthesizer can reconstruct the trajectory.

**Rule**: every `participantStatus` transition either (a) creates a sub-object instance (Consent, Screening, Enrollment, Withdrawal — already covered), or (b) creates a `StateTransition` sub-object record, or (c) produces a NGSI-LD temporal-property change with `validFrom` / `validUntil` semantics on `participantStatus` itself.

**Recommendation: combination of (a) and (c).**
- The four canonical transitions (consent, screening, enrollment, withdrawal) produce sub-objects (already in the design).
- Mid-trial transitions (RANDOMIZED → ON_TREATMENT → IN_FOLLOW_UP → COMPLETED) produce temporal-property changes on `participantStatus` with `validFrom` / `validUntil` brackets. NGSI-LD's native temporal-property semantics handle this; the broker layer answers "what was Mary's status on 2026-08-15?" cleanly.
- A separate `StateTransition` sub-object is overkill for v0.4; revisit if temporal-property querying proves insufficient.

**Implication for source intermediate**: `participantStatus` declared as a NGSI-LD temporal property (not a flat enum), with status-change emission patterns documented. The Sponsor entity already established the temporal-property pattern (validFrom/validUntil on the relationship); Participant extends it to the lifecycle attribute.

**Implication for SHACL invariants**: add an invariant that any participantStatus value matching a state requiring an event sub-object (e.g., RANDOMIZED requires assignedToArm + randomizationDate; WITHDRAWN requires WithdrawalRecord) — already in the SHACL candidates list.

## Cross-walk verification (FHIR R5 / SDTM / CDASH / USDM)

Consolidated cross-walk for the spec doc. Every Participant attribute, relationship, and sub-object resolves to recognizable FHIR / CDISC structures, so a CDISC or USDM reviewer reading the spec sees standards alignment by construction rather than by assertion.

**Top-level Participant — relationships**

| TOP relationship | FHIR R5 | SDTM | Notes |
| --- | --- | --- | --- |
| `forStudySite → StudySite` | `ResearchSubject.site` (Ref → Location/Organization) | SITEID + INVID | StudySite is TOP's per-study site pivot (operational) |
| `forStudy → Study` | `ResearchSubject.study` (Ref → ResearchStudy) | STUDYID | TOP Study cross-walks to USDM `StudyDesign` / `StudyVersion` (study-definition layer) |
| `assignedToArm → Arm` | `ResearchSubject.assignedComparisonGroup` (string referencing `ResearchStudy.comparisonGroup.name`) | ARMCD / ARM, ACTARMCD / ACTARM | Arm structure on the Study side cross-walks to USDM `StudyArm` |
| `hasInformedConsent → InformedConsent` | one `Consent` per record (Ref'd from `ResearchSubject.consent` 0..N) + one `ResearchSubject.progress` entry of type=milestone, milestone=InformedConsentObtained | DS records with DSDECOD=INFORMED CONSENT OBTAINED, DSDECOD=WITHDRAWAL OF CONSENT (re-consent → multiple Consent resources + multiple progress entries) | Re-consent supported via 0..N |
| `hasScreeningRecord → ScreeningRecord` | `ResearchSubject.progress` entries with subjectState=screening / off-study (with reason) | DS records with DSDECOD=SCREEN FAILURE (when screening fails) | One per screening attempt (re-screening = multiple) |
| `hasEnrollmentRecord → EnrollmentRecord` | `ResearchSubject.progress` entry with subjectState=on-study, milestone=Enrolled; `ResearchSubject.period.start` | DS record with DSDECOD=ENROLLED | Single typically; multi-enrollment if re-enrolled |
| `hasWithdrawalRecord → WithdrawalRecord` | `ResearchSubject.progress` entry with subjectState=withdrawn / off-study; `ResearchSubject.period.end` | DS record with DSDECOD=WITHDRAWAL OF CONSENT / DISCONTINUED / LOST TO FOLLOW-UP | One per withdrawal event |

**Sub-object — InformedConsent**

| TOP attribute | FHIR `Consent` field | SDTM | Notes |
| --- | --- | --- | --- |
| `consentId` | `Consent.identifier` | DSSEQ within DS records | URI |
| `consentVersion` | `Consent.policyText` reference / version | (SUPPDM consent version qualifier in many sponsors) | Document version of ICF |
| `consentDate` / `consentTime` | `Consent.dateTime` | DSSTDTC for DSDECOD=INFORMED CONSENT OBTAINED | ISO 8601 |
| `consentMethod` (PAPER / ELECTRONIC / ELECTRONIC_REMOTE) | `Consent.sourceAttachment` vs sourceReference; eConsent indicated via extension | (SUPPDM) | Method of capture |
| `consentingPerson` | `Consent.subject` (Ref → Patient) or `Consent.grantor` if LAR | n/a | Participant or LAR |
| `personObtainingConsent` | `Consent.grantee` / `Consent.actor` with role=consenter | (SUPPDM) | Site staff (TOP `Person`) |
| `consentWitness` | `Consent.actor` with role=witness (0..1) | (SUPPDM) | Optional |
| `language` | `Consent.language` (or via Patient.communication) | (SUPPDM) | ISO 639-1 |
| `translatorUsed` | `Consent.actor` role=interpreter (0..1) | (SUPPDM) | Boolean in TOP, structural in FHIR |
| Lifecycle status: OBTAINED / WITHDRAWN / EXPIRED / RECONSENTED | `Consent.status` (active / inactive / not-done / entered-in-error) | DSDECOD chain: INFORMED CONSENT OBTAINED → WITHDRAWAL OF CONSENT | Multi-step lifecycle |

**Sub-object — ScreeningRecord**

| TOP attribute | FHIR | SDTM | Notes |
| --- | --- | --- | --- |
| `screeningStartDate` / `screeningEndDate` | `ResearchSubject.progress[type=milestone, milestone=ScreeningStarted/Completed].startDate/endDate` | DS records bracketing the screening window | ISO 8601 |
| `screeningOutcome` (ENROLLED / SCREEN_FAILED / RE_SCREENING_PENDING / WITHDREW_BEFORE_DECISION) | `ResearchSubject.progress[].subjectState` | DSDECOD code | Maps to controlled terms |
| `screenFailReason` | `ResearchSubject.progress[].reason` (CodeableConcept) | DS record DSTERM (verbatim) + DSDECOD | Free text or coded |
| `failedInclusionCriteria` / `failedExclusionCriteria` | (typically captured in trial-domain IE — Inclusion/Exclusion Exceptions) | IE domain (Inclusion/Exclusion Not Met) | TOP keeps the criterion-number list directly on ScreeningRecord; SDTM IE domain is the canonical projection |

**Sub-object — EnrollmentRecord**

| TOP attribute | FHIR | SDTM | Notes |
| --- | --- | --- | --- |
| `enrollmentDate` | `ResearchSubject.period.start`, `progress[milestone=Enrolled].startDate` | DS DSDECOD=ENROLLED with DSSTDTC | RFSTDTC on DM is often the enrollment date or first study treatment date |
| `enrollmentMethod` (ON_SITE / REMOTE / HYBRID) | (extension on `ResearchSubject` or operational metadata) | (SUPPDM) | TOP-direct; not in standard SDTM core |
| `enrollmentNumber` | `ResearchSubject.identifier` (use=secondary) | (SUPPDM) | Sponsor-assigned |
| `eligibilityConfirmedBy` | `ResearchSubject.progress[].actor` (extension; reference to Practitioner) | (SUPPDM) | PI signing eligibility |
| `protocolVersionAtEnrollment` | (extension referring to `ResearchStudy.protocol`) | (SUPPDM) | Protocol version at enrollment time |

**Sub-object — WithdrawalRecord**

| TOP attribute | FHIR | SDTM | Notes |
| --- | --- | --- | --- |
| `withdrawalDate` | `ResearchSubject.period.end`, `progress[milestone=Withdrawn].startDate` | DS DSSTDTC for the withdrawal record | ISO 8601 |
| `withdrawalCategory` (CONSENT_WITHDRAWN / INVESTIGATOR_DECISION / ADVERSE_EVENT / LOST_TO_FOLLOW_UP / NON_COMPLIANCE / OTHER) | `ResearchSubject.progress[].subjectState` + `.reason` | DSDECOD: WITHDRAWAL OF CONSENT / DISCONTINUED / ADVERSE EVENT / LOST TO FOLLOW-UP / NON-COMPLIANCE / OTHER | Maps to CDISC DS controlled terminology |
| `withdrawalReason` | `progress[].reason` (CodeableConcept) | DSTERM (verbatim) | Free text |
| `continueDataCollection` | (extension; or absence of `period.end` despite withdrawn `status`) | (SUPPDM) | Boolean — withdrawn from treatment, follow-up continues |
| `withdrawnFromAllProcedures` | (extension) | (SUPPDM) | Boolean |

**USDM positioning.** USDM v3 doesn't model per-subject runtime data. The Participant-side TOP model has no direct USDM cross-walk for runtime fields, by design — USDM is the wrong layer. What TOP Participant DOES connect to USDM via:
- `Participant.forStudy → Study` — TOP Study cross-walks to USDM `StudyVersion` / `StudyDesign`
- `Participant.assignedToArm → Arm` — TOP Arm cross-walks to USDM `StudyArm` (Arm is on the Study side of TOP, lifted in Study v0.3.0)
- Inclusion/Exclusion criteria the Participant was screened against — TOP `InclusionCriterion`/`ExclusionCriterion` cross-walk to USDM `EligibilityCriterion`
- `Participant.hasEnrollmentRecord.protocolVersionAtEnrollment` — references the USDM `StudyVersion` in force at enrollment

So USDM/CDISC reviewers see: TOP carries USDM at the design layer (Study), CDISC SDTM at the analysis layer (DM/DS/IE/EX domains projected from Participant + sub-objects), FHIR R5 at the operational/exchange layer (`ResearchSubject` + `Consent` + `Patient`), CDASH at the acquisition layer. No standards conflict; TOP is the operator-grounded substrate that all four standards project through.

## Source intermediate scope (the implementation lift)

After decisions above, the Participant lift would land. **Every attribute and relationship below carries a `mapsTo` annotation in the source intermediate citing the FHIR R5 path and the SDTM column** (and CDASH where it differs from SDTM), per the Cross-walk verification table above. Same convention as Sponsor / Site / Study, applied tighter here because Participant is where the standards stack is most concentrated.

- **Participant top-level** (~22 attrs / ~10 rels):
  - Identity: participantId, screeningNumber, randomizationNumber, randomizationDate
  - Demographics (operator-grounded, identification-status-agnostic): firstName, middleName, lastName, dateOfBirth, sex, race, ethnicity, primaryLanguage, country
  - Lifecycle: participantStatus (11-value enum), enrollmentDate, completionDate, withdrawalDate
  - Tags
  - Relationships: forStudySite, forStudy, assignedToArm, hasInformedConsent, hasScreeningRecord, hasEnrollmentRecord, hasWithdrawalRecord, plus flagged-missing hasVisit and hasAdverseEvent
  - CTAs: Screen Participant, Consent Participant, Enroll Participant, Randomize Participant, Withdraw Participant, Complete Participation, Discontinue Participant, Re-screen Participant, Re-consent Participant

- **InformedConsent** sub-object (~10 attrs):
  - consentId, consentVersion, consentDate, consentTime, consentMethod (PAPER, ELECTRONIC, ELECTRONIC_REMOTE), consentingPerson (the participant or LAR), personObtainingConsent (Person, the staff member), consentWitness (Person, optional), language, translatorUsed (boolean), withdrawalDate (optional), reconsentRequired (boolean), reconsentReason (optional). Lifecycle status: OBTAINED, WITHDRAWN, EXPIRED, RECONSENTED.

- **ScreeningRecord** sub-object (~8 attrs):
  - screeningRecordId, screeningStartDate, screeningEndDate, screeningOutcome (ENROLLED, SCREEN_FAILED, RE_SCREENING_PENDING, WITHDREW_BEFORE_DECISION), screenFailReason (free text or comma-separated codes), failedInclusionCriteria (comma-separated criterion numbers), failedExclusionCriteria (comma-separated criterion numbers), reScreeningEligibility (boolean).

- **EnrollmentRecord** sub-object (~6 attrs):
  - enrollmentRecordId, enrollmentDate, enrollmentMethod (ON_SITE, REMOTE, HYBRID), enrollmentNumber (Sponsor-assigned), enrollmentVerificationStatus, enrollmentVerifiedBy (Person), eligibilityConfirmedBy (Person, the PI), protocolVersionAtEnrollment.

- **WithdrawalRecord** sub-object (~7 attrs):
  - withdrawalRecordId, withdrawalDate, withdrawalReason (free text or coded), withdrawalCategory (CONSENT_WITHDRAWN, INVESTIGATOR_DECISION, ADVERSE_EVENT, LOST_TO_FOLLOW_UP, NON_COMPLIANCE, OTHER), continueDataCollection (boolean — withdrawn from treatment but follow-up continues), withdrawnFromAllProcedures (boolean), notes.

## SHACL invariants candidates

- (a) **Hard violation**: Participant with `participantStatus` in {RANDOMIZED, ON_TREATMENT, IN_FOLLOW_UP, COMPLETED, WITHDRAWN, DISCONTINUED} must have at least one InformedConsent sub-object with status=OBTAINED. (Cannot be on study without consent.)
- (b) **Hard violation**: Participant with `participantStatus`=SCREEN_FAILED must have at least one ScreeningRecord with screeningOutcome=SCREEN_FAILED.
- (c) **Hard violation**: Participant with `participantStatus`=RANDOMIZED must have `assignedToArm` populated and `randomizationDate` populated.
- (d) **Hard violation**: Participant with `participantStatus`=WITHDRAWN must have at least one WithdrawalRecord; the WithdrawalRecord's withdrawalCategory must be CONSENT_WITHDRAWN.
- (e) **Soft warning**: Participant with `participantStatus`=COMPLETED should have `completionDate` populated.
- (f) **Hard violation**: Participant `assignedToArm` Arm must belong to the same Study that the Participant's StudySite forStudy points at. (Cross-entity consistency: arm comes from this Study's design, not from another Study.)
- (g) **Soft warning**: Participant `dateOfBirth` (if populated) must yield a calculated age within the Study's eligibility range (Study.minAge / Study.maxAge). Soft because the schema doesn't store age-at-screening directly and DOB might be shifted for de-id.

Six to seven invariants. Manageable.

## Worked example plan

Extend the four existing examples (sponsor-pfizer-iqvia, site-mskcc-onco423, site-elevate-network, site-iit-mskcc) to add at least one Participant per StudySite. Each Participant gets:
- Identity + demographics (operator-grounded values; not de-identified)
- One InformedConsent sub-object with status=OBTAINED
- One EnrollmentRecord
- assignedToArm (after randomization)
- participantStatus appropriate to the example state

The MSKCC IIT example specifically can demonstrate the IIT-context Participant case (consenting to a single-PI academic study).

A new dedicated Participant-focused worked example may not be necessary if the existing four cover the patterns. Decide during the lift.

## Open questions for Bo

1. **Confirm Decision 1**: sub-objects (Consent / Screening / Enrollment / Withdrawal) over flat attributes? Recommendation: sub-objects.
2. **Confirm Decision 2**: identification-status-agnostic demographics (Option C)? Same posture as Site spec set for de-identification.
3. **Confirm Decision 5**: simple Arm relationship for v0.4.0 (RandomizationRecord defers to v0.5+)?
4. **Confirm Decision 6**: 11-value lifecycle enum, or trim to a smaller set? Operators legitimately distinguish all 11 in practice; trade-off is more SHACL state-machine invariants.
5. **Demographics field set**: is the recommended set (firstName, middleName, lastName, dateOfBirth, sex, race, ethnicity, primaryLanguage, country) the right scope? Anything to add (height/weight as per-Participant attrs vs visit-time observations)? Anything to drop?
6. **Screen Fail as separate top-level vs sub-object**: OOUX has "Screen Fail" as a top-level object (one of the listed objects). TOP has been folding lifecycle events into sub-objects of the entity they describe. Recommend Screen Fail stays as a sub-object (ScreeningRecord with outcome=SCREEN_FAILED) rather than a separate top-level. The locked-8-top-levels boundary supports this.
7. **URI policy for USDM-ingest-derived entities**: provisional `urn:top:study:{usdm_study_id}/arm:{usdm_arm_id}` etc. — does that work, or should the ingester emit URIs in USDM's own URN format (e.g., what USDM uses internally) and TOP just adopt them? The Participant spec needs to commit to the policy because runtime systems referencing Arms/Studies need to mint matching URIs. This is the upstream of a much bigger ingester-tool conversation; we can seal a default and revisit during the ingester build.
8. **Confirm Decision 9 (Recruit boundary)**: Recruit lifts as a separate top-level entity (or commons horizontal — TBD), with Participant lifecycle starting at SCREENING after consent? Recommendation: yes. Top-level count moves from 8 to 9, which warrants explicit acknowledgment.
9. **Confirm Decision 10 (twin-queryability)**: `participantStatus` as NGSI-LD temporal property (validFrom/validUntil bracketing each value), so trajectory is queryable for downstream twin synthesis? Recommendation: yes.
10. **Multi-realm scope for v0.4**: confirm TOP carries only the trial-conduct realm (Participant entity); Patient / Claimant / RWE-Patient are projection-adapter targets, not TOP entities? Recommendation: yes — same projection-edge pattern as standards. Cross-realm identity resolution (Datavant, MPI, federation) deferred to deployment-edge concerns.
11. **Digital-twin spec as v0.5+ deliverable**: capture the twin-synthesizer contract as a separate planning note (not in scope for v0.4 Participant lift, but the queryability discipline it requires shapes Decision 10)? Recommendation: yes — twin-spec note lifts when Visit / Activity / Observation lift, since the twin contract reaches into time-varying observations beyond what v0.4 Participant carries.

## Estimated lift scope

Once decisions are sealed:

- Source intermediate: ~22 attrs / 10 rels on Participant; ~8 attrs each on 4 sub-objects (~32 sub-object attrs total). About the same scale as Study (36 attrs / 16 rels / 6 sub-objects).
- SHACL invariants: 6-7 new (22-23 total in the graph), plus 1-2 additional for twin-queryability discipline (Decision 10).
- Spec doc: ~600 lines (smaller than Site's 977; comparable to Study's 659).
- Worked examples: extend existing 4 to add Participants.
- Verification history: ~10 questions.

If Decision 9 confirms a separate Recruit entity, that lifts as **its own PR** (parallel to Participant), with its own ~10-15 attrs and ~3-4 relationships. Recruit is smaller than Participant since it carries less data per FIRST-PRINCIPLES (recruiter doesn't need full demographics).

Single PR for Participant; potentially second PR for Recruit (if Decision 9 confirms separate-entity). Twin-spec planning note deferred to v0.5+ when Visit / Activity / Observation lift expands the queryability surface.

Pattern follows Sponsor / Site / Study lift discipline.

## Pointers

- [`participant-spec.html`](participant-spec.html) — to be written; this note seeds it.
- [`ooux-hierarchy.html`](ooux-hierarchy.html) — Participant OOUX entry (with the Site→StudySite correction tracked).
- [`top-strawman.json`](../source/top-strawman.json) — source intermediate.
- [`site-spec.html`](site-spec.html) — Site/StudySite spec; establishes the operational hierarchy that Participant anchors into.
- [`study-spec.html`](study-spec.html) — Study spec; establishes the design-side chain that Participant's Arm assignment reaches into.
