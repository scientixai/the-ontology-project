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

## Architectural decisions to seal

### Decision 1 — Sub-objects for lifecycle events

Participant has several lifecycle events that have their own structure (date, signatures, witnesses, document references, lifecycle state). Two ways to model:

**Option A (recommended): each lifecycle event is a sub-object under Participant.** Sub-objects: InformedConsent, ScreeningRecord, EnrollmentRecord, WithdrawalRecord. Each carries its own dates, signatures, witness, document reference, lifecycle status. Aligns with GCP audit-trail discipline (full event history); supports re-consent after protocol amendment, re-screening, multiple withdrawals if re-enrolled.

**Option B: each is a flat attribute set on Participant.** consentSignedDate, consentSignedBy, consentWitnessedBy, consentVersion, screeningStartDate, screeningEndDate, screenFailReason, enrollmentDate, etc. Simpler model; loses event-history audit fidelity. Re-consent and re-screening become rewrites rather than appended events.

**Recommendation: Option A.** GCP audit demands the full event history; sub-objects encode that. The Sponsor spec's "Sponsor is per-Org-per-Study" pattern and the Site spec's StudySite sub-pivot pattern both established sub-object containment for events that have their own lifecycle. Participant's lifecycle events follow the same pattern.

Trade-off accepted: 4 new sub-objects under Participant (InformedConsent, ScreeningRecord, EnrollmentRecord, WithdrawalRecord). Sub-object count is similar to Study (which has 6).

### Decision 2 — Demographics PHI posture

Participant carries demographics that, in production, are PHI. Three options for how the schema relates to identification:

**Option A: schema carries identifying demographics directly** (firstName, lastName, dateOfBirth, fullAddress). Operator portals see real values. PHI handling is the deployment's problem.

**Option B: schema carries de-identified fields only** (yearOfBirth, age-at-screening, sex, race, ethnicity). HIPAA Safe Harbor compliant by construction. Loses operator-grounding (Site Coordinator can't call participant by name from this schema).

**Option C (recommended): schema is identification-status-agnostic.** Same fields exist; deployment populates with real values for operator-facing systems and Datavant tokens / de-identified values for research-facing systems. The schema doesn't encode identification status; the deployment handles tokenization, date-shifting, and redaction at the boundary between operator-grounded data and research-warehouse projections.

**Recommendation: Option C.** Same posture established in Site spec for de-identification (TOP is upstream of de-id; Datavant + John Snow Labs handle privacy engineering at the deployment layer). Participant follows the same posture. Document it in the spec; don't try to encode it in the schema.

Practical implication: demographics fields the schema carries are operator-grounded — fields the operator actually uses. Recommended set:
- `participantId` (URI, unique) — local Participant identifier
- `screeningNumber` (string) — Site-assigned screening identifier (operator-facing)
- `randomizationNumber` (string, optional) — assigned at randomization
- `firstName`, `lastName`, `middleName` (optional) — operator-grounded; populated with real values OR empty after de-id
- `dateOfBirth` (date, optional) — populated with real DOB, or yearOfBirth approximation, or shifted date depending on deployment
- `sex` (enum: MALE / FEMALE / INTERSEX / UNKNOWN / NOT_REPORTED) — biological sex per ICH E5 / FDA guidance; gender identity is a separate field if needed
- `race` (string, optional, may be comma-separated for multiracial)
- `ethnicity` (string, optional)
- `primaryLanguage` (ISO 639-1 code, optional)
- `country` (ISO 3166-1 alpha-3, optional) — for multi-region trials

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

Participant has a complex lifecycle. Comprehensive enum proposal:

- `SCREENING` — actively in screening
- `SCREEN_FAILED` — failed eligibility (often gets a separate ScreeningRecord with reason)
- `CONSENTED` — consented but not yet enrolled (some studies separate consent from enrollment)
- `ENROLLED` — passed screening, not yet randomized (or immediately enrolled in single-arm)
- `RANDOMIZED` — assigned to arm, may not have started treatment
- `ON_TREATMENT` — active in treatment phase
- `IN_FOLLOW_UP` — treatment complete, in follow-up phase
- `COMPLETED` — full participation completed per protocol
- `WITHDRAWN` — voluntarily withdrew consent (subject-initiated)
- `DISCONTINUED` — discontinued by investigator (e.g., for safety)
- `LOST_TO_FOLLOW_UP` — unable to contact, dropped from active follow-up

11 states. Operationally meaningful — operators distinguish these in their daily workflow (a coordinator preparing for tomorrow's visits queries `ON_TREATMENT` participants; a Sponsor PM tracking enrollment queries `RANDOMIZED` count; a regulator looking at safety queries `DISCONTINUED` participants and reasons).

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

## Source intermediate scope (the implementation lift)

After decisions above, the Participant lift would land:

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

## Estimated lift scope

Once decisions are sealed:

- Source intermediate: ~22 attrs / 10 rels on Participant; ~8 attrs each on 4 sub-objects (~32 sub-object attrs total). About the same scale as Study (36 attrs / 16 rels / 6 sub-objects).
- SHACL invariants: 6-7 new (22-23 total in the graph).
- Spec doc: ~600 lines (smaller than Site's 977; comparable to Study's 659).
- Worked examples: extend existing 4 to add Participants.
- Verification history: ~10 questions.

Single PR. Follows the patterns established by Sponsor / Site / Study.

## Pointers

- [`participant-spec.html`](participant-spec.html) — to be written; this note seeds it.
- [`ooux-hierarchy.html`](ooux-hierarchy.html) — Participant OOUX entry (with the Site→StudySite correction tracked).
- [`top-strawman.json`](../source/top-strawman.json) — source intermediate.
- [`site-spec.html`](site-spec.html) — Site/StudySite spec; establishes the operational hierarchy that Participant anchors into.
- [`study-spec.html`](study-spec.html) — Study spec; establishes the design-side chain that Participant's Arm assignment reaches into.
