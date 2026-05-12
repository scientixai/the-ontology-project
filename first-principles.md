# TOP First Principles

> The design rules every spec doc, planning note, and PR can cite by name. Operationalizes the manifesto. When "but USDM does it this way" or "but SDTM has this column" enters an architectural argument, this is the document that wins it.

## The principle in one line

**A participant is a participant. Full stop.**

Operators are the customer. TOP is built from their workday down, not from the standards up. Standards become projection edges — ephemeral by design — and live below the operator-facing line.

## The inversion

| Most ontologies | TOP |
| --- | --- |
| Built standards-up | Built human-down |
| SDTM / FHIR / USDM shape entities | Operator workflow shapes entities |
| Operators see standards-shaped UX | Operators see what they actually do |
| Cross-walks are the deliverable | Cross-walks are projection rules below the line |
| Standards alignment is TOP | Standards alignment is the *projection layer* |

This is the move. Everything else follows from it.

## What this means concretely

1. **Entity names come from operator vocabulary.**
   - Yes: `Participant`, `Visit`, `Site`, `Sponsor`, `Activity`.
   - No: `ResearchSubject`, `Encounter`, `ResearchOrganization` (those are projection targets).

2. **Attribute names match what operators say or type.**
   - Yes: `firstName`, `screeningNumber`, `randomizationNumber`, `participantStatus`.
   - No: `USUBJID`, `SUBJID`, `ARMCD` (projection-time derivations).

3. **Enum values are operator-meaningful.**
   - Yes: `ON_TREATMENT`, `IN_FOLLOW_UP`, `WITHDRAWN`.
   - No: `ON_STUDY_INTERVENTION`, `WITHDRAWAL_OF_CONSENT` (projection layer).

4. **Sub-objects exist for operator-meaningful events, not for serialization fidelity.**
   - Yes: `InformedConsent`, `ScreeningRecord`, `EnrollmentRecord`, `WithdrawalRecord` — each is a moment in a coordinator's day.
   - No: `ResearchSubjectProgressEntry`, `DSRecord` — those are how the projection adapter renders the TOP sub-object as FHIR or SDTM at export time.

5. **Cross-walks live below the entity definition, never as the shape.** Every spec doc carries its FHIR / SDTM / CDASH / USDM / OMOP cross-walks as documentation of what the projection adapter will emit — not as constraints on the entity's shape.

6. **Standards adapters are ephemeral by design.** The USDM ingester, the FHIR exporter, the SDTM emitter, the OMOP projector — they evolve with their target standards. The entity layer doesn't. When CDISC ships a CT update or USDM bumps to v5, the adapter changes; TOP persists.

## Decision rule when in doubt

Ask in this order:

1. **Does an operator say this term out loud during their workday?** If yes, use it.
2. **Does this entity / attribute / enum match a workflow boundary?** (Consent is a real moment; `ResearchSubjectProgressEntry` is a serialization detail.)
3. **Am I shaping TOP to match a standard, or shaping a projection to match a standard?** If the former, stop. Shape the projection.

If a CDISC C-code, an HL7 resource name, or a USDM class name shows up in a TOP entity definition unprefixed by "this is how we project," something has gone wrong.

## TOP is shaped for practitioners, not for agents or ontologists

Per [ADR-0013](governance/decision-log.md#adr-0013-practitioner-first-tops-primary-customer), TOP's primary customer is the human practitioner. AI agents reason against TOP to help humans become superhuman; they do not shape it. Ontologist tooling (Termboard, OBO reasoners, BFO/PROV-O alignment checkers) is honored at the edge; it does not shape TOP either.

This is the manifesto position made structural. *"Decades have gone by where humans are asked to conform to non-sensical user experiences because they are shaped by a database developer priority. In the end, we want to augment the humans, machines have plenty of help."* TOP's vocabulary, Core concepts, and universal interface are all answerable to the operator's workday — not to the ontologist's elegance, not to the agent's reasoning convenience, not to the database administrator's normalization preferences.

What this looks like in practice:

- **Universal DNA is three properties, not seven.** *What is this thing? When was it captured? Is it current?* Those are the three questions every operator asks about every entity. PROV-O semantics live at the class level, not the universal level. Record-level metadata uses Dublin Core, not Universal DNA.
- **PROV-O alignment is strict at the class level.** Every TOP class declares `rdfs:subClassOf prov:Agent | prov:Activity | prov:Entity` correctly. AI agents and ontologists get a clean PROV graph by construction.
- **BFO alignment is light, edge-only.** The four L2 categories with clean BFO membership (Agent, Location, Temporal, Evidence) declare a single `rdfs:subClassOf bfo:*` so OBO Foundry tooling can reason against TOP without bridge adapters. The four mixed-membership categories (Resource, Scope, Outcome, Constraint) carry a BFO scope-note rather than a forced alignment, deferred to leaf-level decisions.
- **The next test for any change.** *Did an operator's workday cause this, or did an AI agent's / ontologist's / DBA's preference cause this?* If the latter, the change goes to a projection adapter, an annotation layer, or a workflow extension — not TOP.

## What this rules OUT

- CDISC C-codes in operator UX.
- Standards-driven entity names (`fhir:ResearchSubject`, `usdm:Encounter`) as TOP entity types — these are projection targets.
- Nesting under regulatory taxonomies for browsing (e.g., ICH E6(R3) Section 2.x as primary navigation).
- Carrying every standards-mandated field that operators don't actually use ("we have to carry it because USDM has it" — no).
- Treating standards alignment as the deliverable.
- **Therapeutic-area-specific or modality-specific entity types** (`OncologyImagingStudy`, `CardiologyECGRecording`, `PHQ9Response`, `DICOMSeriesAnnotation`, `EProSession`, `LabResult`). Specialization is content (`taskValue` polymorphism + `biomedicalConceptCode` + URI references), never entity shape. See the "Universal pattern" section below.

## What this rules IN

- Operator vocabulary as the authoritative naming.
- Workflow-bound entity boundaries.
- Sub-objects that match operator events.
- Cross-walks documented thoroughly, but always as projection rules below the line.
- Standards alignment as a quality of the projection layer, not of TOP.
- Aggressive simplification of TOP. **Less is the win.**

## Already-applied examples

The principle has been at work, sometimes implicitly:

- TOP `Participant.participantStatus` uses operator-meaningful enums (`ON_TREATMENT`, `IN_FOLLOW_UP`, `WITHDRAWN`) with the FHIR / SDTM mappings as projection-layer documentation, not entity shape.
- TOP doesn't carry `USUBJID` — that's the SDTM projection's `STUDYID-SITEID-SUBJID` derivation; operators type the parts, not the concatenation.
- TOP `Site` is the place where things happen (operator-grounded). USDM has no operational `Site` (it has `Organization` with `type=Site` as a projection-time shape). TOP didn't morph to USDM's flatter shape; the cross-walk runs the other direction.
- TOP carries `InformedConsent` / `ScreeningRecord` / `EnrollmentRecord` / `WithdrawalRecord` as workflow-bound sub-objects. The SDTM DS-record projection happens at the edge — operators never see DSDECOD.
- TOP `Sponsor` is per-Organization-per-Study (operator's view) backed by `Organization` for corporate truth — distinct from USDM's "Sponsor as a Code on Organization" pattern, which would have collapsed the operator-facing entity.

## Implications for in-flight work

- **USDM ingest audit (PR #4) reframes**: not "is TOP USDM-aligned?" but "can the USDM ingester project USDM IN to TOP without losing operator-grounded fidelity?" TOP at the center; USDM at the edge. The audit's eight gaps stand, but their *justification* gets re-rooted: Gap 8 (rationale on Study) — yes, because operators see rationale at Study level (the why-this-trial answer), not because USDM has rationale on StudyDesign. Gap 9 (Protocol cardinality 0..1) — yes, because a planning-state Study with no finalized protocol document is a real operator state, not because USDM allows `documentedBy: []`.
- **CDISC dependency pipeline (PR #5) is the load-bearing mechanism**: TOP, the human-grounded layer, persists across upstream churn; the projection adapters absorb the changes. The pipeline is what makes ephemeral-projections actually work in practice.
- **CDISC ecosystem alignment (PR #5)**: names which CDISC artifacts get to influence TOP entity shape (**none**, by principle) versus which get to influence projection-adapter rules (**most of them**, by design).
- **Participant planning (PR #3)**: the cross-walks I wrote (FHIR / SDTM / CDASH / USDM) are correctly placed *below* the entity decisions. They document what the projection adapters will emit; they don't constrain Participant's shape.

## Implications for every future decision

Each new entity, attribute, enum, sub-object, or relationship asks itself: **did an operator's workday cause this, or did a standards body cause this?** If the answer is "standards body," it doesn't go in TOP. It goes in a projection adapter.

Each spec doc, planning note, and PR description can cite this document by reference: *"per `first-principles.md`, the operator-facing layer is the prize."*

## Why this matters beyond the architecture

CDISC alone publishes 11+ standards across SDTM / CDASH / ADaM / SEND / ODM / USDM / M11 / COSMoS / CT / TAUGs / Implementation Guides. FHIR adds research-side resources. ICH layers governance vocabulary. NCIt feeds terminology. **No human can hold all of this in working memory.** Sponsors burn millions on standards-compliance headcount; CROs charge premiums for CDISC expertise; coordinators and PIs either ignore standards (creating downstream submission pain) or drown in them (and don't actually conduct trials).

TOP's bet is that **TOP eats the standards complexity so operators don't have to**. A coordinator sees "Participant" — that's it. The Participant→SDTM, Participant→FHIR, Participant→USDM cross-walks happen at the edges, automatically, maintained by ephemeral adapters that ride upstream releases.

This is the force-multiplier story made structural. The notes that look like overhead — audits, cross-walks, dependency pipelines — are the absorber. The point is the absorber itself is the product.

Standards-up ontologies make humans pay the integration cost forever. TOP makes TOP pay it once, and then again whenever the standards change.

That's the bet.

## Temporal and provenance, native

Two structural commitments differentiate TOP from compliance vendors, workflow vendors, and most knowledge-graph projects:

1. **NGSI-LD temporal-property semantics native.** Status / outcome / state attributes that operators see change over time are NGSI-LD temporal properties (`validFrom` / `validUntil` per value), not flat enums with separate audit-log mechanisms. Measurement timestamps use the canonical `observedAt` Property metadata. Trajectory queries work directly against TOP.

2. **W3C PROV native typing.** Every TOP entity declares its PROV type (`prov:Agent` / `prov:Activity` / `prov:Entity`) via `rdfs:subClassOf`. Relationships that carry PROV semantics (`wasAssociatedWith`, `wasAttributedTo`, `wasGeneratedBy`, `wasDerivedFrom`, `actedOnBehalfOf`, `wasInformedBy`, `wasInvalidatedBy`) declare those via `rdfs:subPropertyOf`. TOP IS a PROV graph by construction, not via cross-walk translation.

These two commitments answer compliance-grade questions as graph traversals:

- "Show me the chain of custody for this data point." → PROV traversal.
- "Who attributed Mary's enrollment, and what was her status on 2026-08-15?" → PROV + temporal-property traversal.
- "What sources did this synthetic-control twin derive from?" → PROV `wasDerivedFrom` chain.
- "When did this consent become invalid and what activity invalidated it?" → PROV `wasInvalidatedBy` traversal.

No audit-log table. No bespoke versioning shim. No translation layer.

This is what compliance vendors, workflow vendors, and most ontologies *don't* have natively. TOP's claim — that TOP carries temporal and provenance natively — is the architectural moat that complements the operator-grounded vocabulary moat.

Per FIRST-PRINCIPLES, the operator vocabulary remains primary (`InformedConsent`, `Participant`, `screeningNumber`). The PROV typing layers structurally — the same instance answers `?ic a top:InformedConsent` (operator query) and `?ic a prov:Activity` (compliance query). Both views, one TOP.

The consuming-view exemplar: a per-Activity provenance card showing the complete chain of custody (consent → collection → processing → packaging → transit) for a single blood-draw, with every evidentiary checkmark traceable to a TOP facts. Compliance vendors render that card from hand-curated audit logs. TOP renders it from TOP facts, in real time, against any Activity. See [`legacy/reference-graphs/clinical-trials/docs/temporal-prov-native.md`](legacy/reference-graphs/clinical-trials/docs/temporal-prov-native.md) for the original audit, conventions, and consuming-view example (pre-Core; treat as historical reference).

## Universal pattern — specialization is content, not shape

A third structural commitment, alongside operator-grounded vocabulary and native temporal+provenance: **TOP accommodates any assessment without modeling its specifics. Specialization is content; specialization is never entity-shape.**

Therapeutic-area diversity (oncology, cardiology, neurology, vaccines, rare disease, mental health, endocrinology) and modality diversity (DICOM imaging, ePRO questionnaires, ECG, biopsy, IP administration, lab values, sequencing) generate enormous variation in *what* gets captured during a trial. Standards-up vendors model that variation as N entity types per therapeutic area: `OncologyImagingStudy`, `CardiologyECGRecording`, `PHQ9Response`, `DICOMSeriesAnnotation`. TOP then grows linearly with the union of clinical specialties — and breaks every time a new modality or assessment type lifts.

TOP carries **one universal pattern**: `Activity + Task + polymorphic taskValue + biomedicalConceptCode + URI references`. A DICOM imaging Activity and a blood-draw Activity are the same TOP entity shape. They differ in:

- `biomedicalConceptCode` (what the Activity / Task is — via NCIt / LOINC / SNOMED, anchored in the COSMoS BC catalog)
- `taskValueType` and `taskValue` content (`NUMERIC` / `TEXT` / `CODED` / `URI_REFERENCE` / `STRUCTURED` / `DATE` / `IMAGE_REFERENCE`)
- The Equipment they `prov:used`, the Person they `prov:wasAssociatedWith`, the Document they `governedBy`

External systems (DICOM PACS, lab LIS, ePRO platform, EHR, sequencing pipelines) hold the implementation specifics. TOP holds the universal trial-conduct-realm reference; URI references point to wherever the specialized artifact actually lives.

### What this rules out — never

- Therapeutic-area-specific entity types in TOP. **No `OncologyImagingStudy`, no `CardiologyECGRecording`, no `PHQ9Response`, no instrument-specific or modality-specific entities. Ever.** If a future requirement appears to need one, the answer is to reformulate it as content variation: project it through `taskValue` polymorphism + concept-code identification + URI references to the implementation.
- Modality-specific shape (`DICOMImagingStudy`, `EProSession`, `LabResult`, `GenomicVariant`). Same answer — content, not shape.
- Instrument-specific entities (`PHQ9Item`, `ADASCogResult`, `EQ5D5LCapture`). Same answer.
- "Just-in-case" specialization driven by anticipated future requirements. The discipline is reactive: only lift entities when a real operator workflow forces them, and only as TOP Core, not specialization.

### What this *doesn't* rule out — TOP Core

Universal entities that operators across all therapeutic areas talk about as first-class things lift legitimately. These aren't specialization; they're TOP Core:

- `Sample` — every trial that takes specimens has Samples; not oncology-specific
- `AuditEvent` — every regulated workflow generates audit events; not therapeutic-area-specific
- `InvestigationalProduct` — every interventional trial has IP
- `Event` (the OOUX-locked Event container with discriminator) — every trial has events
- The other entries in the OOUX-locked-9: `Visit`, `OversightBody`

Lifting these expands TOP horizontally without specializing it. The test: does this entity exist as a first-class concept in operator vocabulary across therapeutic areas, or only within a specific clinical specialty?

### The discipline

Every proposed new TOP entity must defend itself as a **TOP Core concept** (universal across therapeutic areas, operator-vocabulary-grounded) — not as **therapeutic-area or modality specialization**. If it can't pass that test, it belongs in implementation (sponsor workflow tools, vendor platforms, EHR integrations), not in TOP.

This is the architectural moat made structural: standards-up vendors model N entity types per therapeutic area. TOP carries one universal pattern that handles all of them — and stays small enough for an operator to comprehend in their head.

## Promote facts to entities — no bespoke flags

A fourth structural commitment, alongside operator-grounded vocabulary, native temporal+provenance, and universal pattern: **when you reach for a boolean or a bespoke enum, you're hiding a fact that wants to be a first-class entity. Model the fact.**

Every "is X" flag squashes information. The thing the flag is hiding usually has:

- a **time** (when did this become true)
- an **authority** (who declared it)
- a **scope** (over what jurisdiction, study, participant)
- a **revocability** (can it be undone, and what supersedes it)
- **evidence** (a letter, a ruling, a signed record)

A boolean strips all of that to `true / false`. The result is a bespoke vocabulary on each entity that only the engineer who wrote it understands — the same digital archaeology that makes relational databases full of opaque enums unreadable to anyone but the original author. The graph loses the ability to answer *who* designated this, *when*, under *what authority*, and *whether it has been revoked*.

The Core categories were designed to absorb these patterns:

- *"Is designated"* claims → `top:Attestation` (an Evidence leaf). The Agent who designated, the date, the scope, and the revocation chain all live on the Attestation.
- *"Is bounded by"* rules → `top:Constraint`. The bound, the severity, who enforces, what it applies to.
- *"Has transitioned"* state changes → `top:StatusChange` (an Outcome leaf). The transition, the time, the cause.
- *"Is documented in"* artifacts → `top:Document` or `top:Attestation`. The artifact carries its own provenance.
- *"Was measured"* facts → `top:Observation` (an Outcome leaf). Value, unit, instrument, observer.

When an entity inherits from a Core primitive, the system *understands the meaning* — Universal DNA carries identity, time, and status; PROV-O semantics carry attribution and chain of custody. The boolean approach forces every consumer to learn a private vocabulary; the primitive approach is predictable across every workflow.

### Two rules to internalize

1. **A boolean is evidence in disguise — model the evidence.** Before adding a boolean property, ask: *who declares this true, when, under what authority?* If any of those has an answer, the boolean is hiding an Attestation, a Constraint, or a StatusChange.
2. **If you can't say which primitive it inherits from, you haven't named the thing yet.** Every entity in TOP traces to one of the 8 Core categories. A flag that can't be reified to a primitive is a flag that hasn't earned its place — refactor before shipping.

### What this rules out

- Boolean flags that hide a designation, an authority, or a time-bounded claim (`isSponsorOfRecord`, `hasRegulatoryResponsibility`, `isBlinded` on a Study, `isPrimaryInvestigator`, …). These reify to Attestations.
- Bespoke enums that aren't a finite, stable, operator-vocabulary set. The boundary: `staffRole` (a stable, finite, universally-recognized operator vocabulary) earns its keep; `portfolioType` (varies by sponsor org, drifts with reorg, every domain extends it) does not.
- Per-entity status booleans (`isActive`, `isClosed`, `isFinalized`) where the underlying truth is a lifecycle state. Use `top:status` and the temporal trajectory.
- Properties that look universal but only one workflow uses. Promote to a Core primitive only when a real second workflow forces the lift; otherwise the property lives in the workflow extension.

### When a primitive is genuinely missing

The discipline is purist but not dogmatic. If a real operator workflow surfaces a fact that none of the 8 Core categories absorbs cleanly, the path is an ADR proposing a new Core leaf — not a workaround through bespoke flags. Bespoke flags accumulate; new primitives stay rare. The current 8 categories were designed to be the smallest set that covers the operator space; adding a ninth is a structural event, governed by the same rigor as any Core change.

The bar for a new primitive: at least two unrelated workflows need the same shape and none of the existing 8 absorb it. The cost of a wrong addition is propagation across every domain forever; the cost of an honest absence is one workflow modeling a slightly awkward variant for a while.

### Already-applied — what this prevents going forward

The earlier clinical-research draft modeled Sponsor with four booleans (`isSponsorOfRecord`, `hasRegulatoryResponsibility`, `hasFinancialResponsibility`, `hasOperationalResponsibility`) and one bespoke enum (`regulatoryAuthorityScope`). Under this principle, the honest model is:

- "Pfizer-US is sponsor-of-record with FDA on KEYNOTE-189" → an instance of `top:Attestation` granting that responsibility, with the FDA as the granting Agent, the timestamp of designation, the regulatory jurisdiction, and the Study scope. Revocation creates a new Attestation that supersedes the first.
- The dual-sponsor case (Pfizer-US for FDA, Pfizer-Ireland for EMA) is two Attestations on the same Study with different scopes. No flags. No bespoke enum.
- A query "who is the current sponsor of record for KEYNOTE-189 under FDA jurisdiction?" walks the Attestation graph, finds the most recent unsuperseded Attestation in that scope, returns the granting Agent. Auditable end-to-end. PROV-traversable. Time-bounded.

This is the architectural reset for the clinical-research rebuild and every workflow that follows.

## Naming and citation

Cite as: **`first-principles.md`** or, in prose, as **"TOP first principles"**. The principle in one line — *a participant is a participant, full stop* — is the quotable form.

## Pointers

- [`manifesto.html`](manifesto.html) — the philosophical foundation; this document operationalizes it.
- [`roadmap.md`](roadmap.md) — what we're building, in what order.
- [`legacy/reference-graphs/clinical-trials/docs/`](legacy/reference-graphs/clinical-trials/docs/) — pre-Core spec docs that surfaced this principle through specific operational scenarios; archived but instructive.
