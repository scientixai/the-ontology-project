# TOP roadmap v1

> Working document. Edited frequently. The single place where future TOP work is tracked once more than one finished top-level exists.
> Last touched 2026-05-08.

This roadmap captures the work queued behind the core ontology effort, the decisions about how that work is staged, and the items that need to land before TOP moves out of `CLAUDE OUTPUTS/` into [github.com/scientixai/the-ontology-project](https://github.com/scientixai/the-ontology-project) under Apache 2.0. It supplements the per-spec open-issues tables and becomes the single place where future work is tracked once we have more than one finished top-level.

## Where we are (2026-05-09)

The clinical-trials reference graph is the first reference graph being built on TOP. The OOUX hierarchy is locked at nine top-levels: Sponsor, Study, Site, Participant, Recruit, Visit, Investigational Product, Oversight Body, Event. **All nine top-levels are now lifted as of v0.7.0-strawman** — the OOUX-locked-9 set is structurally complete. All seven OOUX boundary decisions are resolved (see [`ooux-hierarchy.html`](reference-graphs/clinical-trials/docs/ooux-hierarchy.html)).

**Sponsor** is fully sealed at v0.1.4-strawman with eight verification questions answered, four SHACL-SPARQL domain invariants encoded (one soft warning, three hard violations), one worked example validating clean against pyshacl, and a complete spec document ([`sponsor-spec.html`](reference-graphs/clinical-trials/docs/sponsor-spec.html)).

**Study** is fully sealed at v0.3.0-strawman with twelve verification questions pending Bo's review, six SHACL-SPARQL domain invariants encoded covering Study lifecycle and design constraints, four worked examples extended with Endpoint / InclusionCriterion / ScheduleOfAssessments entities and validating clean against pyshacl, and a complete spec document ([`study-spec.html`](reference-graphs/clinical-trials/docs/study-spec.html)).

**Participant** is fully sealed at v0.4.0-strawman as the human in the trial-conduct realm. The lift forced two architectural extensions surfaced during planning: (1) **Recruit** lifts as a separate ninth top-level (top-level count moves 8 → 9) for the pre-consent recruitment realm, recognizing the recruiter as a distinct operator role with its own workflow and lighter PHI surface; (2) **multi-realm projection posture** — the same human is a Participant in trial conduct, a Patient in care, a Claimant in claims, an RWE-Patient in research warehouses; TOP carries one realm (trial conduct), the others are projection-adapter targets. Outcomes:

- **Participant** (top-level) lifted with 22 attrs / 11 rels and 4 sub-objects (InformedConsent / ScreeningRecord / EnrollmentRecord / WithdrawalRecord). 11-state lifecycle enum (`SCREENING` through `LOST_TO_FOLLOW_UP`) with NGSI-LD temporal-property semantics for trajectory queryability.
- **Recruit** (new top-level) lifted with 18 attrs / 4 rels covering the recruitment funnel (RESPONDED → CONTACTED → PRE_SCREENED → QUALIFIED_PENDING_CONSENT → CONVERTED_TO_PARTICIPANT, with attrition states DECLINED / NO_SHOW / NOT_QUALIFIED / DROPPED). Recruit→Participant transition via `convertedFromRecruit` with InformedConsent existence as the canonical conversion event.
- **9 new SHACL invariants** added (25 total: 4 soft warnings + 21 hard violations). Includes cross-entity consistency (Participant.assignedToArm.forStudy must match Participant.forStudy; Participant.forStudySite.forStudy must match Participant.forStudy).
- **1 worked example extended** (site-mskcc-onco423.ttl) with one Participant (ON_TREATMENT) and three Recruits demonstrating different funnel states. Conforms under pyshacl --advanced.
- **Operator-grounded vocabulary** per [`FIRST-PRINCIPLES.md`](FIRST-PRINCIPLES.md): `screeningNumber`, `randomizationNumber`, `participantStatus` enum values like `ON_TREATMENT` / `WITHDRAWN`. Standards cross-walks (FHIR R5 `ResearchSubject`, SDTM `DM` + `DS` + `IE`, CDASH `DM`) live below the line as projection-adapter rules. USDM v4 has no per-subject runtime entity; TOP→USDM linkage is via the design layer (forStudy, assignedToArm, eligibility criteria, protocolVersionAtEnrollment).
- **Twin-queryability discipline**: every lifecycle transition produces a queryable record (sub-objects for canonical events; NGSI-LD temporal property for mid-trial states). Substrate carries the contract; downstream twin synthesizers fulfill it. PMDT (El Gammal et al., under review at SoSyM) is direct prior art for ontology-driven twin substrate. Substrate decisions made now are the load-bearing pre-conditions for twin-for-enrollment in v0.5+ — the highest-value digital-twin use case (synthetic control arms, predicted-response cohort selection, drop-out risk prediction, trial feasibility simulation).
- **Spec docs**: [`participant-spec.html`](reference-graphs/clinical-trials/docs/participant-spec.html) and [`recruit-spec.html`](reference-graphs/clinical-trials/docs/recruit-spec.html).

**Visit** is fully sealed at v0.5.0-strawman as the sixth top-level — the operational visit-occurrence (a Participant attended a real visit at a StudySite on a real date). Per the universal-substrate posture in [`FIRST-PRINCIPLES.md`](FIRST-PRINCIPLES.md), the Visit lift introduces three universal sub-objects that accommodate any assessment without modeling its specifics: a DICOM imaging Activity and a blood-draw Activity are the same TOP entity shape, distinguished only by content (`biomedicalConceptCode`, `taskValueType`, `taskValue`, linked Equipment, governing Document). Outcomes:

- **Visit** (top-level) lifted with 17 attrs / 8 rels covering occurrence-side facts (visitMode 6-state DCT enum per ICH E6(R3) Annex 2; visitStatus 9-state lifecycle as NGSI-LD temporal property; planned-vs-actual datetime separation; OUT_OF_WINDOW + UNSCHEDULED deviation handling).
- **VisitDefinition** (new Study sub-object — seventh) lifted as the protocol template (USDM-ingest-derivable from `StudyDesign.encounters[]`). Visit.definedBy → VisitDefinition (0..1 because UNSCHEDULED visits don't have a corresponding template).
- **Activity** (Visit sub-object) — the universal work unit. Same TOP shape regardless of activity type (vitals, MRI, ePRO, biopsy, IP-admin, ECG, sequencing); coarse `activityType` enum for sort/filter only, NOT for specialization. PROV: `prov:Activity`; `performedBy` carries `prov:wasAssociatedWith`; `usedEquipment` carries `prov:used`; `governedBy` references the SOP / protocol section that defines the Activity.
- **Task** (Visit sub-object) — the universal leaf data-capture unit (one Task per measurement / response / dose / observation). Polymorphic `taskValue` discriminated by `taskValueType` (NUMERIC / TEXT / CODED / URI_REFERENCE / STRUCTURED / DATE / IMAGE_REFERENCE) handles ANY data shape including external-system references (DICOM Study Instance UIDs, lab LIS records, S3 URIs). `observedAt` as canonical NGSI-LD Property metadata (NOT a flat `performedDateTime` attribute). `belongsToActivity` links to the parent Activity within the same Visit.
- **VisitObservation** (Visit sub-object) — operator-narrative observation per OOUX Path C reportability handoff. `escalated` + `escalatedTo → Event` capture the AE / deviation / discrepancy escalation chain (Event flagged-missing until v0.7+).
- **9 new SHACL invariants** added (34 total: 5 soft + 29 hard). Includes cross-entity consistency (Visit.forParticipant.forStudySite must match Visit.forStudySite); status-driven completeness guards on Visit / Activity / Task; required-field invariants for OUT_OF_WINDOW + UNSCHEDULED + NOT_PERFORMED states.
- **1 worked example extended** (site-mskcc-onco423.ttl) — Maria's Cycle 1 Day 1 visit at MSKCC: 1 Visit (IN_PERSON_CLINIC, COMPLETED) + 3 Activities (Vital Signs, Blood Draw — CBC, Drug X Administration) + 8 Tasks (4 vitals NUMERIC, 3 lab NUMERIC, 1 IP-admin STRUCTURED with dose/unit/route/lot). Conforms under pyshacl --advanced.
- **FHIR Questionnaire projection** — TOP's universal Visit → Activity → Task hierarchy projects cleanly to FHIR R5 `Questionnaire` (form template) and `QuestionnaireResponse` (captured data); consumable by Epic / Cerner / SMART on FHIR apps / ePRO vendors. Single source of truth → many ephemeral renderings. Adapter implementation deferred to v0.6+.
- **Chain-of-custody view** enabled — every Activity becomes queryable as a complete provenance chain (consent → performance → equipment-with-calibration → governing-SOP → captured-Tasks). Compliance vendors render this from hand-curated audit logs; TOP renders it from substrate facts in real time.
- **Spec doc**: [`visit-spec.html`](reference-graphs/clinical-trials/docs/visit-spec.html).

**OversightBody** is fully sealed at v0.5.1-strawman as the seventh top-level — IRB / EC / DSMB / IDMC / Steering Committee / CEC. Per FIRST-PRINCIPLES universal-substrate posture, OversightBody is a substrate primitive (every regulated trial has oversight bodies regardless of therapeutic area; not specialization). Single TOP entity with `oversightBodyType` enum carries the operator-grounded discrimination — same architectural moat as Activity + Task. Outcomes:

- **OversightBody** (top-level) lifted with 14 attrs / 5 rels covering identity (registrationNumber + registrationAuthority + registrationCountry), type discriminator, scope, member roster + chair, and review-authority relationships to Study and StudySite. NGSI-LD temporal property on `status` (ACTIVE / SUSPENDED / DISBANDED).
- **PROV typing**: OversightBody is `prov:Agent` (committees bear responsibility); `hasMember` carries `prov:actedOnBehalfOf` semantics (members act on behalf of the body). When ReviewDecision lifts (deferred to v0.6+), it becomes `prov:Activity` with `prov:wasAssociatedWith` linking to the OversightBody.
- **Three flagged-missing relationships un-flagged**: `Sponsor.interfacesWith`, `StudySite.hasIRB`, `Study.hasOversightBody` now have a real target with sh:class enforcement active.
- **2 new SHACL invariants** added (36 total: 5 soft + 31 hard). Type/scope alignment: IRB / EC require LOCAL or CENTRAL scope (review boards have geographic / institutional scope); DSMB / IDMC require SPONSOR scope (sponsor-convened safety boards).
- **3 worked examples extended**: MSKCC IRB serving ONCO-423 + ONCO-423 IDMC at MSKCC; same IRB committee playing different roles on IIT-ONCO-001 (per-Role-per-Study pattern); Advarra Central IRB serving Elevate Network's three sites.
- **Spec doc**: [`oversightbody-spec.html`](reference-graphs/clinical-trials/docs/oversightbody-spec.html).

**InvestigationalProduct (IP)** is fully sealed at v0.6.0-strawman as the eighth top-level — the substance, biologic, device, or combination product under investigation. Per FIRST-PRINCIPLES universal-substrate posture, IP is one TOP entity covering all product types (DRUG / BIOLOGIC / DEVICE / DIAGNOSTIC / COMBINATION_PRODUCT / OTHER) with `investigationalProductType` as the operator-grounded discriminator — not a shape discriminator. The substrate doesn't carry type-specific specifics; external systems (Drug Master Files, device databases, IRT systems) hold implementation details. Outcomes:

- **InvestigationalProduct** (top-level) lifted with 16 attrs / 5 rels covering identity (name, type, generic/brand), product properties (mechanismOfAction, dosageForm, routeOfAdministration, strength), regulatory (status, source IND/EudraCT), blinding flag, and supply-chain relationships to Sponsor, Study, Lot, Kit, Document.
- **Lot** (sub-object, ~10 attrs) — manufacturing batch with lotNumber, manufactured/release/expiration/retest dates, manufacturer / facility, quantity, lot status as NGSI-LD temporal property (MANUFACTURING / RELEASED / IN_DISTRIBUTION / DISTRIBUTED / EXPIRED / RECALLED / DESTROYED).
- **Kit** (sub-object, ~7 attrs / 2 rels) — blinded packaging unit with kitNumber, treatmentAssignment (IRT-issued code; unblinding key held separately by IRT vendor), assignment date, kitStatus as NGSI-LD temporal property. `belongsToLot → Lot` + `assignedToParticipant → Participant`.
- **PROV typing**: IP / Lot / Kit are `prov:Entity` (defined artifacts; manufacturing batch; packaging unit). Dispensation Activities (in Visit, from v0.5) are `prov:Activity` that `prov:used` the Lot/Kit. Chain of custody assembles via substrate traversal — no audit-log join.
- **Two flagged-missing relationships un-flagged**: `Sponsor.supplies` and `Study.suppliesInvestigationalProduct` now have a real target.
- **No separate Dispensation entity** — per universal-substrate posture, dispensation events live in the Visit > Activity > Task substrate (activityType=IP_ADMINISTRATION + STRUCTURED taskValue carrying dose/route/lot/kit references). The substrate handles IP administration without specialization.
- **4 new SHACL invariants** added (40 total: 6 soft + 34 hard). Blinded IP requires kits; assigned/dispensed kit needs participant; past-expiry lot soft warning + EXPIRED status hard requirement.
- **1 worked example extended** (site-mskcc-onco423.ttl) — Drug X (BIOLOGIC, anti-PD-L1 mAb, blinded) supplied by Pfizer for ONCO-423; one Lot (DRX-2026-0117, DISTRIBUTED, expires 2027-07-15); one Kit (KIT-00042, treatmentAssignment="TREATMENT_A", DISPENSED to Maria at C1D1).
- **Spec doc**: [`investigationalproduct-spec.html`](reference-graphs/clinical-trials/docs/investigationalproduct-spec.html).

**Event** is fully sealed at v0.7.0-strawman as the ninth and final OOUX-locked top-level — the single container for clinical-trial occurrences requiring tracking, reporting, or escalation (Adverse Event, Serious Adverse Event, Protocol Deviation, Data Discrepancy, Safety Signal, Safety Report, Other Clinical Event). Per FIRST-PRINCIPLES universal-substrate posture, one TOP entity covers all categories with `eventCategory` as the operator-grounded discriminator — same architectural moat as Activity + Task / OversightBody / InvestigationalProduct. With Event sealed, the OOUX-locked-9 top-level set is structurally complete. Outcomes:

- **Event** (top-level) lifted with 22 attrs / 14 rels covering identity (eventId, eventCategory, eventType, identifier), timeline (eventDate, detectedDate, reportedDate as NGSI-LD temporal properties), severity / status / detectionSource, AE/SAE-specific attributes (causality, expectedness, MedDRA PT + SOC, CTCAE grade, actionTakenWithIp, outcome), regulatory reporting (regulatoryReportable / regulatoryReportDeadline / regulatoryReportSubmitted / regulatoryReportSubmittedDate as a temporal-property pair), DEVIATION-specific attributes (protocolDeviationCategory + protocolDeviationImpact per ICH E6(R3) §6), and full relationship coverage to Study / Participant / StudySite / Visit / IP / Lot / Kit / Person / VisitObservation / OversightBody / Document, plus self-references (partOf for aggregation, causedBy for causal lineage).
- **PROV typing**: Event is `prov:Activity` (the event IS what happened); `eventDate` carries `prov:atTime`; `reportedBy → Person` carries `prov:wasAssociatedWith`; `derivedFrom → VisitObservation` carries `prov:wasInformedBy` (the operator-meaningful escalation chain — a routine vital-sign observation escalates to a tracked Event with first-class queryable provenance).
- **Three flagged-missing relationships un-flagged**: `Participant.hasAdverseEvent`, `Visit.hasAdverseEvent`, `VisitObservation.escalatedTo` now resolve to a real target with sh:class enforcement active.
- **5 new SHACL invariants** added (45 total: 7 soft + 38 hard). SAE must have regulatoryReportable=true (#41); ctcaeGrade only valid for AE/SAE (#42); protocolDeviationCategory only valid for DEVIATION (#43); regulatoryReportSubmitted=true requires submittedDate (#44); soft warning when reportable+overdue+unsubmitted (#45).
- **1 worked example extended** (site-mskcc-onco423.ttl) — Maria's Grade 3 immune-related hepatitis SAE (Day 13 post-C1D1, regulatoryReportable + submitted under E2B 15-day window, MedDRA "Immune-mediated hepatitis", causality PROBABLY, action DOSE_INTERRUPTED, reviewed by ONCO-423 DSMB); plus a DEVIATION (Day 8 labs drawn at Day 9 due to weather closure, OUT_OF_WINDOW_VISIT MINOR, CLOSED).
- **Per the [TAXONOMY.md](TAXONOMY.md) migration table**, Event is destined to split into `topc:Event` (universal primitive shape — every regulated workflow has Events) + `topcr:Event subClassOf topc:Event` (clinical-research specialization). For v0.7 the universal-grade and clinical-specific attributes co-locate under `top:`; the upcoming namespace-refactor PR performs the split with no shape changes.
- **Spec doc**: [`event-spec.html`](reference-graphs/clinical-trials/docs/event-spec.html).

**Site** has lifted to v0.2.0-strawman as a combined Site + StudySite spec ([`site-spec.html`](reference-graphs/clinical-trials/docs/site-spec.html), 977 lines), with 14 verification questions pending Bo's review. The Site lift forced an architectural correction (Bo's "Site is the most important object, that's where trials operate" framing and the corrected operational hierarchy `Site → StudySite → Study → Protocol → SOA → Visit → Activity`). Outcomes:

- **Site** (top-level) lifted from 3 attrs / 5 rels to 49 attrs / 10 rels with full SFQ feasibility coverage (therapeutic area experience, past trial experience, infrastructure, regulatory defaults, insurance, staff capacity).
- **StudySite** (new commons horizontal) lifted with 17 attrs / 18 rels as the per-Study operational pivot. Crosswalks to `usdm:StudySite` (verified against cdisc-org/usdm via WebFetch).
- **Person**, **System**, **Log**, **Equipment**, **StorageLocation**, **Credential** all lifted as commons horizontals to support the Site spec without flagged-missing placeholders. **Document** horizontal expanded with R3 Appendix C `essentialRecordPurpose` + `responsibleParty` enums.
- **System three-axis** decision: `operatedBy` / `usedBy` / `oversightHeldBy` schema-level role pattern. Original "visibility-as-projection" framing superseded by R3 Section 3.9 / 2.12 oversight-as-relationship grounding.
- **Equipment + System + Log triad** resolves the freezer-with-IoT-monitor case cleanly: physical Equipment under R3 qualification/calibration discipline; computerised System under R3 Section 4.3 validation/audit-trail discipline; Log captures the temporal trail.
- **IIT pattern** captured without special schema relationship: same Organization plays both `managesSite` and `playsSponsorRole`. SHACL invariant 9 carries the IIT exception.
- **6 new SHACL invariants** added (10 total: Sponsor 4 + Site/StudySite 4 + System 1 + Credential 1).
- **3 worked examples** authored, all conforming under pyshacl advanced mode: traditional AMC (MSKCC + Pfizer), SMO network (Elevate Research three sites), IIT (MSKCC self-sponsored).

The Site spec extends the Sponsor template with five site-specific sections: architectural anchor (operational hierarchy), R3 alignment (Sections 2 / 3 / 4 / Appendix C / Annex 2), ISF alignment (legacy operational view, 23 sections mapped), lifecycle state machines (Site + StudySite separately), persona-to-Site-view matrix (10 roles), SFQ projection (named query template), and delegation matrix.

The Sponsor spec template plus Site spec extensions form the pattern for the remaining six top-levels. The translator scaffold's pre-emission guards still hold: polysemous-verb detection, target-missing minCount relaxation, target-missing class-constraint suppression.

## What ships next, in order

**TermBoard import + curation pass.** With the SKOS taxonomy landed (PR #13) and all nine OOUX top-levels lifted, the next operator-facing milestone is importing `taxonomy/taxonomy.ttl` into TermBoard and curating concept-level definitions, alt-labels, scope notes, and relationships against the live tooling. This is the prerequisite the convener flagged before the namespace-refactor PR runs — taxonomy curation discipline first, mechanical refactor second. No code changes; the curation produces a v1.1 SKOS file that the refactor PR consumes.

**Mechanical namespace refactor PR.** Per the [TAXONOMY.md](TAXONOMY.md) migration table: rename `top:` (project) vs `topcr:` (clinical-research workflow) prefixes, move universal primitive shapes (Site, Visit, Event, OversightBody, Document, Person, Organization, Equipment, etc.) into `topc:` commons, drop `/onto/` from URI paths, apply `rdfs:subClassOf topc:*` for workflow specializations. Substrate decisions don't change — only namespace labels and the addition of subClassOf edges. Bounded ~3-4 hours of careful refactoring + revalidation.

**Sub-object refinements** as the operator-vocabulary deepens. ReviewDecision under OversightBody (per OversightBody spec); ActivityTemplate under Study (per Visit spec — currently an inline 0..N template ref); Amendment / Milestone / StudyStartupPackage under Study; AuditTrailEntry as a horizontal extension of Log. Each refinement is a small additive PR that doesn't break consumers.

**Workflow extensions begin** (`topcd:`, `topmfg:`, `topsc:`). Care Delivery is the natural next workflow — every sponsored hospital trial uses both clinical-research and care-delivery workflows over the same Person / Organization / Site / Visit / Event substrate. Manufacturing follows for IP-supply CMC. Supply Chain ties cold-chain monitoring to Lot / Kit. Each workflow lifts as an additive package per the composable-extensions decision (see [governance/decision-log.md](governance/decision-log.md) ADR-0004).

**PROV-as-governance backfill** (parked behind a stable v1). Per ADR-0011, concept-level provenance enrichment of `taxonomy.ttl` waits for v1 stabilization to avoid churn during refactor.

**Horizontal completions in parallel.** Lifted as of v0.6.0: Organization, Document (R3 Appendix C-aligned), StudySite, Person, System (R3 Section 4.3-aligned), Log (with logType discriminator covering CommunicationLog), Equipment, StorageLocation, Credential. Still flagged-missing (lifting in v0.8+): RegulatoryAuthority, Contract, MonitoringVisit, Audit, TrainingRecord, Enrollment, StudyStartupPackage, CRF, Sample, Shipment, Meeting, Publication, SOP, TrainingProgram, CRO, Country, DataTransferAgreement, Tag.

## OBO Foundry alignment

OBO Foundry covers the biomedical-knowledge layer (genes, phenotypes, anatomy, chemistry). TOP covers the operator layer (workflow, sponsorship, sites, visits, audit trail). The two are complementary. Direct entity-level OBO cross-walks are deferred until biological-domain top-levels (Adverse Event, Sample, Lab Result, Diagnosis) lift in v0.3 or later, and even then much of the work is reachable transitively through existing public mappings.

## Tooling alignments

Three community-standard infrastructure pieces TOP should adopt rather than reinvent:

- **SSSOM (Simple Standard for Sharing Ontological Mappings),** the canonical format for ontology-to-ontology mappings. When TOP publishes its OMOP / FHIR / USDM / OBO cross-walks as machine-readable mapping artifacts, they should be SSSOM-formatted. Aligns TOP with the OBO Foundry / Mondo / Bioregistry tooling ecosystem; lets community contributors review and contribute mappings using already-known tooling. Tracked as a v0.3 deliverable.
- **Bioregistry** ([bioregistry.io](https://bioregistry.io)), community-governed registry of prefixes and identifiers used across the biomedical-ontology ecosystem. TOP's prefixes (`top:`, `topc:`, future `topcmc:`, `topdh:`, etc.) should be registered there as TOP graduates from strawman to public release. Aligns identifier governance with OBO Foundry conventions. Tracked as a v0.2 publish-time deliverable.
- **OWL2 + SKOS for hierarchical concepts.** TOP's enums (siteType, equipmentClass, documentType, organizationType, essentialRecordPurpose) currently flat. Promoting selected enums to SKOS concept schemes with broader/narrower relationships allows transitive ancestry queries (the OMOP CONCEPT_ANCESTOR pattern) without OMOP's pre-computed-table approach. Tracked as a v0.3 enhancement.

## Reference architecture for role-specific projections and views

Tracked here as a placeholder until the core objects are done.

The core ontology defines what entities exist, how they relate, and what invariants must hold. It does not define how a given role consumes those entities for a given job. A Sponsor PM looking at Study X cares about a different projection than a Regulator looking at Study X. Both project from the same underlying graph, but the operationally useful view is different. Today these projections are sketched ad hoc in the spec's query-patterns section (`§5` of the Sponsor spec). That works for documentation. It does not work as a contract for downstream tooling.

What this item builds, when the project gets to it:

A reference-architecture artifact that identifies personas, roles, and jobs-to-be-done for each top-level entity. The Sponsor spec's six-perspective query patterns (site, patient, regulator, SMO, sponsor portfolio analyst, compliance officer) are a starting point but need to be made systematic across all eight top-levels. The output is a matrix: top-level entity × persona × job-to-be-done × the projection that serves it.

Common projections per role, defined as named query templates rather than ad hoc query examples. A "Sponsor PM Daily View" projects the active Studies, the open Action Items, and the upcoming Milestones for a given Sponsor entity. An "Investigator Today View" projects the visits scheduled at a Site for the current day plus the open queries on those visits. These projections get formal names and live as separate artifacts (markdown files, wiki pages) so they can evolve independently of the core ontology. The core ontology references them; it does not own them.

Reference patterns documented as separate, community-contributable artifacts. The core ontology stays compact and load-bearing. Reference patterns live next to it in the same repository (under `reference-patterns/` or similar), but evolve through community contribution without requiring the core to change. This honors the federation pattern at the documentation layer the same way the prefix architecture honors it at the schema layer: the core stays narrow, the periphery stays open.

The benefits this delivers: reduced maintenance burden on the core ontology because role-specific work does not bleed into the schema; increased flexibility for adopters because they can layer their own projections on top of the core without forking the schema; community-driven evolution of patterns and best practices without needing a central catalog to register with.

Sequencing: solidify all eight top-level entities first (currently in progress); then create a `reference-patterns/` placeholder; then open a separate workstream to define personas, roles, and jobs-to-be-done; then invite community contributions through whatever governance shape TOP has by then (working group, GitHub PR review, RFC process).

This is a v0.3 or later effort. It does not block v0.1 of the clinical-research reference graph. It does shape how v0.2 packages the v0.1 work for community consumption, so it lands before the public Apache 2.0 publish.

## Pointers

- [`MANIFESTO.html`](MANIFESTO.html) — v0.2 manifesto, signatories pending.
- [`reference-graphs/clinical-trials/docs/ooux-hierarchy.html`](reference-graphs/clinical-trials/docs/ooux-hierarchy.html) — eight top-levels, all seven boundary decisions resolved.
- [`reference-graphs/clinical-trials/docs/sponsor-spec.html`](reference-graphs/clinical-trials/docs/sponsor-spec.html) — first complete top-level spec, template for the remaining seven.
- [`reference-graphs/clinical-trials/docs/site-spec.html`](reference-graphs/clinical-trials/docs/site-spec.html) — second top-level spec at v0.2.0-strawman, combined Site + StudySite.
- [`reference-graphs/clinical-trials/docs/study-spec.html`](reference-graphs/clinical-trials/docs/study-spec.html) — third top-level spec at v0.3.0-strawman, Study with Protocol / Arm / SOA / Endpoint / InclusionCriterion / ExclusionCriterion sub-objects.
- [`reference-graphs/clinical-trials/docs/event-spec.html`](reference-graphs/clinical-trials/docs/event-spec.html) — ninth top-level spec at v0.7.0-strawman, Event closing the OOUX-locked-9 set.
- [`TAXONOMY.md`](TAXONOMY.md) — SKOS taxonomy + migration table; queues the namespace-refactor PR.
- [`governance/decision-log.md`](governance/decision-log.md) — architectural decision log (ADRs).
- [`tools/`](tools/) — translator scaffold (build_context.py, build_shacl.py).
- [`reference-graphs/clinical-trials/source/top-strawman.json`](reference-graphs/clinical-trials/source/top-strawman.json) — source intermediate.
- [`reference-graphs/clinical-trials/examples/sponsor-pfizer-iqvia.ttl`](reference-graphs/clinical-trials/examples/sponsor-pfizer-iqvia.ttl) — worked example.

## How this document evolves

The roadmap is edited in place. Major shifts (a new reference graph entering the queue, a working group spinning up, a phase boundary crossing) get a header bump.

Once TOP moves fully into the public GitHub repo, granular tracking moves to GitHub Issues. The roadmap document settles into the high-altitude view, where we are, what ships next, why; the issue queue carries the day-to-day work and takes community contributions through the normal PR-and-review path.

---

*Working document · Last touched 2026-05-08 · sponsorship of TOP infrastructure during the founding phase provided by Scientix.ai Inc · stewardship will rotate to domain working groups on a published cadence*
