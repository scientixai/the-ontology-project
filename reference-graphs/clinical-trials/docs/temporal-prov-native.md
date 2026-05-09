# Native temporal + provenance — audit, posture, and v0.4.1 cleanup (working draft)

> Working document. Audits TOP v0.4 against NGSI-LD temporal conventions and W3C PROV. Establishes that **temporal and provenance are NATIVE TOP capabilities**, not cross-walk projections — a differentiation move with structural consequences. Folds into a v0.4.1 source-intermediate cleanup PR alongside this audit.
> Last touched 2026-05-09.

## Why this is foundational, not bookkeeping

TOP's differentiation argument has three legs:

1. **Operator-grounded substrate** (per FIRST-PRINCIPLES) — entity vocabulary matches how operators talk; standards are projection edges.
2. **Native temporal capabilities** — every property and relationship can be queried over time without a separate audit-log mechanism.
3. **Native provenance backbone** — every change, every derivation, every attribution is queryable as a W3C PROV graph without translation.

Standards-up vendors don't have (1). Workflow-up vendors don't have (2) or (3) natively — they bolt them on as audit-log tables, change-tracking shims, or after-the-fact lineage tools.

**TOP's claim**: the substrate carries temporal and provenance natively, so every regulator question, every monitor query, every twin-synthesis lineage trace, every M&A transfer audit is a *graph traversal*, not a join across audit tables.

This is what makes TOP defensible against:
- Compliance vendors who say "we have audit trails" (their audit trails are bolt-on logs, not the graph itself)
- Workflow vendors who say "we have versioning" (their versioning is row-level row_history, not temporal-property semantics)
- Standards bodies who say "use FHIR Provenance + NGSI-LD" (correct in principle; nobody operationalizes it natively at the ontology layer)

The substrate decisions in this note are the architectural moat.

## Audit 1 — NGSI-LD temporal compliance

### Standard temporal keys (ETSI GS CIM 009)

| Key | Meaning | Where it lives |
|---|---|---|
| `observedAt` | When a value was observed/measured (reflects reality) | Property metadata sub-attribute |
| `validFrom` / `validUntil` | Temporal validity interval of a Property/Relationship value | Property/Relationship metadata; supports versioning ("what was the value on 2026-08-15?") |
| `createdAt` / `modifiedAt` | Broker-managed system metadata | Not for domain modeling |

Plus standard `xsd:dateTime` / `xsd:date` / `xsd:time` literal types for properties whose VALUE is a datetime (e.g., `plannedStartDate` is a datetime literal — not metadata).

### Findings per entity

**Sponsor (v0.1.4)**:
- ✓ `validFrom` / `validUntil` on entity (M&A successor handoffs)
- **gap**: `validFrom` / `validUntil` should also be available on relationships — `parentSponsor` (M&A successor lineage), `actsOnBehalfOf` (CRO delegation handoffs). Currently flat relationships.
- **fix v0.4.1**: annotate parentSponsor and actsOnBehalfOf with `_temporalRelationship: true` in source intermediate; build_context.py emits relationship-level temporal sub-attributes.

**Site / StudySite (v0.2.0)**:
- ✓ StudySite has `validFrom` / `validUntil` for the participation record
- **gap**: `delegatesAuthorityTo` (per-Study DOA Log) needs per-relationship temporal — when a sub-investigator's delegation starts/ends mid-study. Currently flat.
- **gap**: `hasPrincipalInvestigator` needs per-relationship temporal for PI changes mid-study (ICH E6(R3) Section 2.3).
- **fix v0.4.1**: annotate both relationships with `_temporalRelationship: true`.

**Study (v0.3.0)**:
- **gap**: `studyStatus` is a flat enum; should be a NGSI-LD temporal property (validFrom/validUntil per value). Same pattern as Participant.participantStatus (Decision 10).
- **fix v0.4.1**: declare studyStatus as `_temporalProperty: true` in source intermediate.
- **legitimate flat**: `plannedStartDate`, `actualStartDate`, `primaryCompletionDate`, `plannedCompletionDate`, `actualCompletionDate`, `approvalDate`, `effectiveDate` (on Protocol) — these are domain-event datetime VALUES, not temporal validity intervals. Stay flat.

**Participant (v0.4.0)**:
- ✓ `validFrom` / `validUntil` on entity
- ✓ `participantStatus` declared as NGSI-LD temporal property in spec doc (Decision 10)
- **gap**: source intermediate doesn't carry the explicit `_temporalProperty: true` annotation — declared in prose but not machine-readable for build_shacl.py / build_context.py
- **fix v0.4.1**: add `_temporalProperty: true` to the participantStatus attribute definition; build_context.py emits the appropriate JSON-LD context entry.
- **legitimate flat**: `randomizationDate`, `enrollmentDate`, `completionDate`, `withdrawalDate`, `consentDate`, `screeningStartDate` / `screeningEndDate` — domain-event facts. Stay flat for operator-query convenience.

**Recruit (v0.4.0)**:
- ✓ `validFrom` / `validUntil` on entity
- **gap**: `recruitStatus` should be a NGSI-LD temporal property like participantStatus (parallel pattern; funnel state trajectory analytics). Declared in spec; needs explicit annotation.
- **fix v0.4.1**: add `_temporalProperty: true` annotation.

**Future Visit / Activity / Task (v0.5)**:
- `visitStatus` → NGSI-LD temporal property
- Task `taskValue` → standard `observedAt` Property metadata, not custom `performedDateTime`
- Activity → `validFrom` / `validUntil` for operational time window
- Apply at lift time; do not retrofit.

### NGSI-LD cleanup punch list (v0.4.1)

```
SOURCE INTERMEDIATE ANNOTATIONS:

 _temporalProperty: true on:
   Study.studyStatus
   Participant.participantStatus
   Recruit.recruitStatus
   StudySite.studySiteStatus
   Site.siteStatus  (when site goes inactive — currently has 'status' attr)
   Sponsor.status
   Document.documentStatus
   Protocol.protocolStatus
   InformedConsent.consentStatus
   ScreeningRecord.screeningOutcome
   (Generally: any *Status / *Outcome attribute that operators see change over time)

 _temporalRelationship: true on:
   Sponsor.parentSponsor       (M&A successor lineage)
   Sponsor.actsOnBehalfOf      (CRO delegation handoff)
   StudySite.hasPrincipalInvestigator  (PI changes mid-study)
   StudySite.delegatesAuthorityTo      (per-staff delegation start/end)
   Recruit.recruitedBy         (recruiter changes — rare but possible)

EMITTER UPDATES:
   build_context.py  → emit @context entries for temporal-property attributes:
                       "participantStatus": { "@type": "ngsi-ld:TemporalProperty" }
   build_shacl.py    → optionally emit sh:datatype permissive for temporal-property values;
                       SHACL invariant pattern for temporal-property completeness can defer
```

## Audit 2 — W3C PROV native adoption

### Why PROV native, not cross-walk

A cross-walk says "TOP InformedConsent maps to prov:Activity via owl:sameAs." That works for export but:
- TOP queries don't natively traverse PROV chains (have to go through the cross-walk)
- Downstream PROV-aware tools (provenance dashboards, lineage tracers, regulatory audit tools) need translation
- The substrate isn't itself a PROV graph

**Native** says "TOP InformedConsent IS a prov:Activity by definition (rdfs:subClassOf prov:Activity)." That changes:
- Every TOP entity instance is automatically a typed PROV-graph node
- PROV traversals (`?activity prov:wasAssociatedWith ?agent`) work directly against TOP data without translation
- Regulatory tools using PROV (and there are many, including the BridgeEH and Healthcare Provenance Framework efforts) consume TOP graphs natively
- Operator vocabulary (top:InformedConsent in UX) and PROV vocabulary (prov:Activity in compliance queries) coexist; same instance, both views.

This is what "native" buys.

### PROV core mapping

PROV defines three core types and a small set of canonical relationships. TOP entities map as follows:

#### Type mapping

| PROV type | TOP entities | Reasoning |
|---|---|---|
| `prov:Agent` | `top:Sponsor`, `top:Site`, `topc:Organization`, `topc:Person`, `topc:StudySite` | Things bearing responsibility — sponsors, organizations, people, sites in their operational role |
| `prov:Activity` | `top:InformedConsent`, `top:ScreeningRecord`, `top:EnrollmentRecord`, `top:WithdrawalRecord`, future `top:Visit`, future `top:Task`, future `top:Activity` (sub-object), future `topc:MonitoringVisit`, future `topc:Audit` | Things that occur over time and act on entities — events, encounters, checks |
| `prov:Entity` | `top:Study`, `top:Participant`, `top:Recruit`, `top:Protocol`, `top:Arm`, `top:Endpoint`, `top:InclusionCriterion`, `top:ExclusionCriterion`, `top:ScheduleOfAssessments`, `topc:Document`, `topc:Equipment`, `topc:System`, `topc:StorageLocation`, `topc:Credential`, future `topc:Sample`, future `topc:CRF` | Records, defined artifacts, physical/digital things being acted upon |

Notes on edge cases:
- **Person as both Agent and (potential) subject of measurements**: PROV allows multi-role typing. TOP `Person` is primarily Agent (staff who do things); Person is never a Participant in TOP's model (Decision 4 in Participant spec — they're separate entities).
- **Participant as Entity, not Agent**: The TOP Participant *record* is the Entity. The trial subject's *actions* (giving consent, attending visits, taking IP) are Activities done BY the Participant-as-Agent. TOP's InformedConsent sub-object IS that Activity, with `prov:wasAttributedTo` linking back to the Participant's Agent role. This avoids dual-typing on the Participant entity.
- **Visit as Activity, not Entity**: A Visit IS an event happening over time (with start/end). prov:Activity is exactly right. Distinct from a Visit's *appointment* (an Entity in some FHIR profiles).
- **Document as Entity**: Documents are subjects of activities (drafted, approved, retired). prov:Entity. The drafting/approving/retiring are Activities (often modeled implicitly through Document.documentStatus transitions plus PROV attribution).

#### Relationship mapping

| PROV relationship | TOP relationships that ARE this | New annotations needed |
|---|---|---|
| `prov:wasAssociatedWith` (Activity ↔ Agent — Activity carried out by/under Agent) | `InformedConsent.personObtainingConsent`, `ScreeningRecord.screenedBy`, `EnrollmentRecord.eligibilityConfirmedBy`, `WithdrawalRecord.documentedBy`, `Recruit.recruitedBy` | All five become `rdfs:subPropertyOf prov:wasAssociatedWith` |
| `prov:wasAttributedTo` (Entity ← Agent — entity is attributed to agent) | `InformedConsent.consentingPerson` (the Participant in their Agent role) | becomes `rdfs:subPropertyOf prov:wasAttributedTo` |
| `prov:wasGeneratedBy` (Entity ← Activity — entity was created by activity) | Future `Task.value ← Task (Activity)`; future `Document.draftedBy ← drafting Activity` | Lift-time |
| `prov:wasDerivedFrom` (Entity ← Entity) | `Participant.convertedFromRecruit` (Participant entity was derived from Recruit funnel record); future `Protocol.amendsPriorVersion`; `Sponsor.parentSponsor` (M&A successor lineage); future `InformedConsent.reconsents` (re-consent derives from prior consent) | All become `rdfs:subPropertyOf prov:wasDerivedFrom` |
| `prov:actedOnBehalfOf` (Agent ← Agent — delegation) | `Sponsor.actsOnBehalfOf` (CRO acting for sponsor of record) | becomes `rdfs:subPropertyOf prov:actedOnBehalfOf` |
| `prov:wasInformedBy` (Activity ← Activity — communication chain) | Future: `OtherClinicalEvent.derivedFromObservation` (Path C reportability handoff); `EnrollmentRecord.followsScreening` (when made explicit) | Lift-time annotations |
| `prov:wasInvalidatedBy` (Entity ← Activity — entity destroyed/withdrawn) | `InformedConsent.withdrawnBy` (when consentStatus=WITHDRAWN); `Document.supersededBy` (when documentStatus=SUPERSEDED) | Lift-time annotations |
| `prov:hadPrimarySource` (Entity ← Entity) | (USDM ingest case) Study `wasDerivedFrom` USDM document | When ingester lifts |

#### What this looks like in source intermediate

Each entity gets a `provType` attribute in its definition:

```yaml
- id: InformedConsent
  role: an informed-consent event under GCP
  provType: prov:Activity      # NEW
  description: ...
  attributes: [...]
  relationships:
    - name: personObtainingConsent
      target: Person
      cardinality: 1..1
      provSemantics: wasAssociatedWith    # NEW — this relationship IS prov:wasAssociatedWith
      doc: ...
    - name: consentingPerson
      target: Person
      cardinality: 0..1
      provSemantics: wasAttributedTo      # NEW
      doc: ...
```

The `build_context.py` and `build_shacl.py` emitters read these annotations and emit:
- JSON-LD context entries declaring the PROV types
- SHACL shapes with `rdfs:subClassOf` to the appropriate prov:* superclass
- Property shapes with `rdfs:subPropertyOf` for relationships carrying PROV semantics

### Provenance gaps and fills (v0.4.1 vs v0.5+)

**v0.4.1 (annotation-only, no structural changes)**:

```
ENTITY TYPING:
   Sponsor          → rdfs:subClassOf prov:Agent
   Site             → rdfs:subClassOf prov:Agent
   Organization     → rdfs:subClassOf prov:Agent
   Person           → rdfs:subClassOf prov:Agent
   StudySite        → rdfs:subClassOf prov:Agent
   Study            → rdfs:subClassOf prov:Entity
   Protocol         → rdfs:subClassOf prov:Entity
   Arm              → rdfs:subClassOf prov:Entity
   Endpoint         → rdfs:subClassOf prov:Entity
   InclusionCriterion / ExclusionCriterion → rdfs:subClassOf prov:Entity
   ScheduleOfAssessments → rdfs:subClassOf prov:Entity
   Participant      → rdfs:subClassOf prov:Entity
   Recruit          → rdfs:subClassOf prov:Entity
   Document         → rdfs:subClassOf prov:Entity
   Equipment / System / StorageLocation / Credential → rdfs:subClassOf prov:Entity
   Log              → rdfs:subClassOf prov:Activity (a Log entry IS an event record)
   InformedConsent  → rdfs:subClassOf prov:Activity
   ScreeningRecord  → rdfs:subClassOf prov:Activity
   EnrollmentRecord → rdfs:subClassOf prov:Activity
   WithdrawalRecord → rdfs:subClassOf prov:Activity

RELATIONSHIP SEMANTICS (rdfs:subPropertyOf):
   InformedConsent.personObtainingConsent → prov:wasAssociatedWith
   InformedConsent.consentingPerson       → prov:wasAttributedTo
   InformedConsent.consentWitness         → prov:wasAssociatedWith (witness role)
   ScreeningRecord.screenedBy             → prov:wasAssociatedWith
   EnrollmentRecord.eligibilityConfirmedBy → prov:wasAssociatedWith
   WithdrawalRecord.documentedBy          → prov:wasAssociatedWith
   Recruit.recruitedBy                    → prov:wasAssociatedWith
   Sponsor.actsOnBehalfOf                 → prov:actedOnBehalfOf
   Sponsor.parentSponsor                  → prov:wasDerivedFrom
   Participant.convertedFromRecruit       → prov:wasDerivedFrom
   Recruit.convertedToParticipant         → (inverse; convention: emit but no prov annotation)

NAMESPACE / @context:
   prov: http://www.w3.org/ns/prov#  added to namespaces
   build_context.py emits prov:* qualified names in the JSON-LD context
   build_shacl.py emits @prefix prov: in the Turtle prelude
```

**v0.5+ (structural; not in this PR)**:

```
NEW STRUCTURAL ELEMENTS:

  AuditEvent (sub-object on entities OR top-level):
     A generic prov:Activity record for state changes / annotations / corrections
     not already captured by domain-specific event sub-objects.
     Attributes: auditEventId, eventType, performedAt, performedBy, before, after, reason
     Used for: data corrections, query resolutions, e-signature events.

  Re-consent derivation:
     New InformedConsent.reconsents → InformedConsent (0..1)
     prov:wasDerivedFrom semantics
     Replaces the current 'reconsentRequired' boolean + 'reconsentReason' freetext;
     full lineage chain from current consent back to original.

  Protocol amendment derivation:
     New Protocol.amendsPriorVersion → Protocol (0..1)
     prov:wasDerivedFrom semantics
     Replaces the current Study.hasAmendment list approach with explicit
     versioning chain on Protocol itself.

  Document supersession:
     New Document.supersededBy → Document (0..1; inverse: supersedes)
     prov:wasInvalidatedBy semantics
     Captures TMF version evolution natively.

  IP/Sample chain (when Sample / IP lift):
     Generated/used PROV chains for sample collection and IP administration
```

### Worked-example projection

Take Maria from the MSKCC ONCO-423 example. The current substrate carries the entities; with PROV annotations, the same data answers PROV-canonical questions natively:

```sparql
# Question: Who did what to Maria's consent?
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX top:  <https://top.scientix.ai/onto/clinical/v1#>

SELECT ?activity ?actorAgent ?attributedAgent ?date WHERE {
    ?p a top:Participant ;
       top:hasInformedConsent ?activity .
    ?activity top:consentDate ?date ;
              prov:wasAssociatedWith ?actorAgent ;     # Jones obtained consent
              prov:wasAttributedTo ?attributedAgent .  # Maria gave consent
}

# Question: Trace Maria's lineage from recruit to participant
SELECT ?p ?recruit ?source WHERE {
    ?p a top:Participant ;
       prov:wasDerivedFrom ?recruit .
    ?recruit top:recruitmentSource ?source .
}

# Question: Show the full audit trail across all on-trial activities for Maria
SELECT ?activity ?actor ?date WHERE {
    ?p a top:Participant ; top:participantId "...maria..." .
    ?activity prov:wasAttributedTo|^(top:hasInformedConsent|top:hasScreeningRecord|top:hasEnrollmentRecord|top:hasWithdrawalRecord) ?p ;
              prov:wasAssociatedWith ?actor .
    OPTIONAL { ?activity top:consentDate ?date }
    OPTIONAL { ?activity top:screeningStartDate ?date }
    OPTIONAL { ?activity top:enrollmentDate ?date }
    OPTIONAL { ?activity top:withdrawalDate ?date }
}
ORDER BY ?date
```

These queries work natively. No translation layer. No audit-log-table join. Pure PROV traversal against the operator-grounded substrate.

This is what differentiation looks like.

## How operator vocabulary and PROV typing coexist

Per FIRST-PRINCIPLES, operator-grounded names are primary. PROV typing is structural and additive. The schema declares both:

```ttl
top:InformedConsent
   a owl:Class ;
   rdfs:label "Informed Consent" ;
   rdfs:subClassOf prov:Activity ;            # PROV native typing
   rdfs:comment "An informed-consent event under GCP..." .

top:personObtainingConsent
   a owl:ObjectProperty ;
   rdfs:domain top:InformedConsent ;
   rdfs:range topc:Person ;
   rdfs:subPropertyOf prov:wasAssociatedWith ;  # PROV native semantics
   rdfs:label "Person Obtaining Consent" .
```

Operators see "Informed Consent" / "Person Obtaining Consent" in UX. The same instance answers both:
- `?ic a top:InformedConsent` (operator-vocabulary query)
- `?ic a prov:Activity` (PROV-canonical query)

Both views, one substrate. Per FIRST-PRINCIPLES — operator vocabulary primary; standards/PROV layered as native structural commitments below the line.

## Differentiation framing (for ROADMAP / public-facing)

The market reality:

- **Standards-up vendors** (CDISC consultancies, eClinical SaaS) — bolt-on audit logs; not native PROV; not native temporal versioning at the data layer.
- **Workflow-up vendors** (EDC, CTMS, eTMF) — row-level versioning at best (created_at / modified_at columns); no graph traversal of provenance; no native PROV.
- **Compliance vendors** (audit-log products, GxP validation tools) — focus on log capture, not native data-layer provenance.
- **Knowledge-graph projects** (most healthcare ontologies) — domain modeling; rarely PROV-native; rarely NGSI-LD-temporal-aware.

**TOP carries both natively, by definition.** A regulator's "show me the chain of custody for this data point" or a sponsor's "what derivations did this synthetic-control twin use" or a CRA's "what was Mary's status on date X and who attributed it" are all single graph traversals.

This is the architectural moat that complements the operator-grounded-substrate moat.

## The consuming view — what this enables for operators and auditors

The substrate decisions in this audit are not abstract. They enable **per-Activity provenance views** that render the complete chain of custody for any data point as a graph traversal — not as a pre-computed audit log. Bo shared the following mock-up of the end-state UX:

```
Activity: Blood draw · Subject 423-MU07-018 · Visit 04
Trial ONCO-423 · Site Munich-07 · Protocol v3.2

1. Subject consented · Day -7 · 14:22 CET
   ✓ eConsent v3.2 signed                          eC-2026-0411
   ✓ Witnessed by site coordinator                 SC delegated
   ✓ Subject ID 423-MU07-018 verified              CTMS

2. Sample collected · Day 0 · 09:14 CET
   ✓ Phlebotomist credentialed                     cert# 2024-088
   ✓ PI delegation log entry                       DG-2026-0047
   ✓ Trained on protocol v3.2                      TR-2026-0188
   ✓ Subject consent on v3.2 (matches)             version-link
   ✓ 3× EDTA + 1× SST per protocol §7.4            vial-spec

3. Sample processed · Day 0 · 09:42 CET
   ✓ Centrifuge model CF-200                       S/N 2023-441
   ✓ Calibration current (next 2026-09-15)         CAL-2026-03-15
   ✓ Spin: 3000 rpm × 15 min (per §7.6)            in spec

4. Sample packaged · Day 0 · 10:30 CET
   ✓ Packager IATA certified                       IATA-2025-0911
   ✓ PI delegation + protocol training             DG / TR linked
   ✓ Validated dry-shipper VS-2024                 cert in file
   ✓ Per shipping SOP-2026-CL-019                  SOP linked

5. Cold-chain transit · Day 0 11:00 → Day 1 14:00
   ✓ Data logger DL-2026-2287                      attached
   ✓ Continuous temp log · no excursion            -78°C ± 2
   ✓ Carrier custody trace complete                FedEx CC
```

Every numbered step is a `prov:Activity`. The chain itself is a `prov:wasInformedBy` sequence (consent → collection → processing → packaging → transit). Every checkmark is a SHACL/SPARQL-queryable assertion against substrate state at a specific point in time. Operators see a clean compliance-grade view; underneath, every fact is a graph traversal answered natively by the substrate's PROV typing and NGSI-LD temporal properties.

This view is what differentiates TOP. Compliance vendors render the same view from a hand-curated audit log. Workflow vendors can't render it at all (no provenance graph). TOP renders it from substrate facts, in real time, against any Activity, with full traceability — because the substrate IS the audit graph by construction.

### Activity diversity — therapeutic areas, modalities, and spatial data

The blood-draw mock-up is **one Activity type**. Real trials carry many: imaging (CT / MRI / PET / DICOM), ePRO questionnaires, ECG / Holter, biopsy, infusion, cognitive battery, IP administration, sample shipment, ePRO diary, vaccine reactogenicity capture. Therapeutic-area diversity multiplies further:

- **Oncology**: imaging studies (RECIST evaluation, tumor segmentation), biopsies with histopathology, ECOG performance status assessment
- **Cardiology**: ECGs, echocardiograms with measurements, cardiac MRI with chamber volumes, Holter/event monitoring
- **Neurology**: structural/functional MRI, EEG, cognitive batteries (ADAS-Cog, MMSE, neuropsych panels)
- **Vaccines**: titers, cell-mediated immunity panels, reactogenicity diaries
- **Mental health**: PHQ-9, GAD-7, structured clinical interviews
- **Rare disease / genomics**: WGS / WES / panel sequencing with variant calling, biomarker panels
- **Endocrinology / metabolic**: continuous glucose monitoring streams, OGTT, hormone panels

Each Activity type has different equipment, credentials, data shapes, and standards-projection targets (different SDTM domains, different FHIR resources, different OMOP tables, different USDM `BiomedicalConcept` references).

**Some activities carry spatial data**, not just temporal. DICOM imaging is the canonical example:
- The image itself is a binary artifact (TOP doesn't store pixels; it references via URI to a PACS / image archive)
- Annotations on images carry spatial coordinates (ROIs, tumor boundaries, lesion measurements)
- DICOM SR (Structured Reports) and W3C Web Annotation are the standard layers for spatial provenance
- Tumor segmentation across timepoints is BOTH temporal AND spatial — a 4D problem

**Substrate posture for diversity — universal containers, not specialized entities**:

Per Bo's clarification: **TOP must accommodate any assessment without modeling its specifics. Specific visit structures, therapeutic-area assessments, instrument configurations are implementation details — they belong in sponsor-side workflow tools, vendor platforms, and EHR integrations. The substrate stays universal.**

The substrate carries **`Activity` and `Task` as universal containers**:

```
Visit (occurrence)
  └── Activity (universal: vitals OR MRI OR ePRO OR biopsy OR IP-admin OR genomic panel OR ECG OR ...)
        ├── governedBy → Document (the SOP / protocol section that defines this Activity)
        ├── usedEquipment → Equipment (the device, with its own Credential chain)
        ├── performedBy → Person (with PROV wasAssociatedWith)
        └── hasTask → Task[*]
                       ├── biomedicalConceptCode (NCIt → COSMoS BC: identifies what this is)
                       ├── taskValue (polymorphic: number, string, URI, coded, structured)
                       ├── taskValueType (NUMERIC / TEXT / CODED / URI_REFERENCE / STRUCTURED / DATE / IMAGE_REFERENCE)
                       └── (PROV + observedAt temporal metadata)
```

**Specialization is in CONTENT, not in SHAPE.**

A DICOM imaging Activity and a blood-draw Activity are the **same entity shape**. They differ in:

| | Blood draw | DICOM MRI | ePRO PHQ-9 | IP administration |
|---|---|---|---|---|
| `Activity.biomedicalConceptCode` | NCIt: Phlebotomy | NCIt: MRI Brain | LOINC: PHQ-9 | NCIt: Drug Administration |
| `Equipment used` | Centrifuge, dry shipper | MRI scanner | Patient device | Infusion pump |
| `Person performedBy` | Phlebotomist | MR Technologist | Self | Nurse |
| `Document governedBy` | Lab manual §7.4 | Imaging protocol §4.2 | ePRO SOP | IP handling SOP |
| `Task.taskValue` | numeric (mL, count) | URI → DICOM Study Instance UID in PACS | enum (0–3 per item) | numeric (mg, mL, route code) |
| `Task.taskValueType` | NUMERIC | URI_REFERENCE | CODED | NUMERIC + STRUCTURED |

The substrate doesn't know it's DICOM. The PROV chain works identically (`?activity prov:used ?equipment ; prov:wasAssociatedWith ?agent ; prov:generated ?artifact`). The compliance view (the mock-up's per-Activity provenance card) renders identically — what changes is the content of the cells, not the shape of the substrate.

**This is the architectural moat**. A standards-up vendor would model DICOM as one specialized type, ePRO as another, lab as another — and end up with N entity types per therapeutic area. TOP carries one universal Activity + Task pattern that handles all of them.

**Polymorphic taskValue is the key mechanism**:
- `NUMERIC`: BP=128, weight=72.4
- `TEXT`: free-text observations
- `CODED`: enum from a code system (CTCAE grade, RECIST response, ECOG status)
- `URI_REFERENCE`: URI to external artifact (DICOM PACS, S3 bucket, lab LIS, video file)
- `STRUCTURED`: nested object (a complex measurement with multiple components — e.g., blood pressure with systolic/diastolic/MAP)
- `DATE`: a captured date value
- `IMAGE_REFERENCE`: special case of URI_REFERENCE for radiology/pathology images, often paired with PACS-side metadata

External systems (DICOM PACS, lab LIS, ePRO platform, EHR) hold the implementation specifics. TOP holds the universal trial-conduct-realm reference; the URI points to wherever the specialized artifact lives.

**Federation across substrates** (v0.6+): when an external system (PACS, EHR) publishes its own PROV graph, TOP's PROV chain extends across the boundary via `prov:wasGeneratedBy` references. No translation; PROV is the universal language for cross-system provenance.

**Per-therapeutic-area assessment instruments** (e.g., EQ-5D-5L, ADAS-Cog, RECIST, vital signs panel):
- COSMoS BC catalog handles these via NCIt + LOINC codes (per the CDISC ecosystem alignment note)
- TOP Task carries `biomedicalConceptCode` referencing the canonical concept
- The COSMoS Dataset Specialization carries the per-instrument SDTM projection rules
- **TOP doesn't model the instruments internally** — references them via biomedicalConceptCode; specialization is content, not entity-shape

**The bet**: universal Activity + Task + polymorphic taskValue + temporal+PROV native = handles 100% of assessment diversity. Specialized horizontals like ImagingStudy, IPAdministration, QuestionnaireResponse are NOT planned for v0.6+ — they would violate the universal-substrate posture. Instead: when DICOM imaging trials surface needs that exceed the universal pattern, the additions are **constrained** to taskValueType polymorphism + URI references, not new entity types.

The substrate doesn't try to enumerate any activity type. It provides the universal frame; the BC catalog + polymorphic value + URI references handle every therapeutic area's diversity without TOP changing.

### What the mock-up surfaces for substrate refinement

The mock-up forces several refinements that flow naturally from the temporal+PROV commitment but aren't yet in the substrate. These are architectural deferrals (v0.5+ work, not v0.4.1 cleanup):

1. **`Equipment.calibrationStatus` must be a NGSI-LD temporal property** (current vs lapsed; `validUntil >= activity time` is the SHACL check).
2. **`Person.hasCredential` (multi-realm)** — IATA shipping certs, phlebotomy certs, GCP training certs all surface here. Credential horizontal already exists; richer credentialType enum needed.
3. **`Person.hasTrainingRecord` per-protocol-version** — training records linked to specific Protocol versions. Currently flagged-missing; lifts when training-record requirements concretize.
4. **`Document` section anchors** (§7.4, §7.6 references) — protocols and SOPs are referenced by Activities at the section level. Document horizontal needs section-level addressing.
5. **`Activity.governedBy → Document` + `Activity.parameters` referencing Protocol sections** — Visit's Activity sub-object (v0.5) needs these relationships.
6. **`Log` temporal-property enrichment for continuous monitoring** — temperature observations across a window; no-excursion verification is a SHACL-queryable assertion.
7. **External-system integration** (carrier custody) — TOP federates with external PROV-bearing graphs (FedEx logistics, EHR audit trails). Cross-system PROV interop is v0.6+ federation work.

These refinements don't change the v0.4.1 annotation cleanup; they're items the v0.5 Visit lift and the Equipment/Document/Person enrichments absorb at lift time. **None of them require new entity types** — they extend the universal Activity / Task / Equipment / Document / Person primitives with annotations and temporal-property semantics. The substrate posture stands: universal containers, specialization in content.

## Convention summary (additions to FIRST-PRINCIPLES)

The two new conventions to make explicit:

1. **NGSI-LD temporal-property semantics for state attributes**: any attribute named `*Status` or `*Outcome` that operators see change over time SHOULD be a NGSI-LD temporal property. Source intermediate annotates with `_temporalProperty: true`; emitters generate appropriate JSON-LD context and SHACL shapes.

2. **W3C PROV native typing**: every TOP entity declares its PROV type via `provType: prov:Agent | prov:Activity | prov:Entity` in source intermediate; relationships that carry PROV semantics declare `provSemantics: wasAssociatedWith | wasAttributedTo | wasGeneratedBy | wasDerivedFrom | actedOnBehalfOf | wasInformedBy | wasInvalidatedBy`. Emitters generate `rdfs:subClassOf` / `rdfs:subPropertyOf` declarations to the prov: namespace.

These are baked into FIRST-PRINCIPLES as load-bearing conventions; future lifts apply them at lift-time, not retrofit.

## Cleanup PR scope (v0.4.1)

Single PR, this branch:

1. **Source intermediate** — annotate temporal properties + PROV types/semantics on all v0.4 entities and sub-objects (Sponsor / Site / StudySite / Study + sub-objects / Participant + sub-objects / Recruit + horizontals). Bump version to v0.4.1-strawman.
2. **build_context.py** — add `prov:` namespace prefix; emit PROV typing in JSON-LD context.
3. **build_shacl.py** — add `prov:` prefix prelude; emit `rdfs:subClassOf prov:*` and `rdfs:subPropertyOf prov:*` declarations from annotations.
4. **FIRST-PRINCIPLES.md/.html** — add "Native temporal and provenance" section; update the manifest of conventions.
5. **ROADMAP.md/.html** — add v0.4.1 line summarizing the cleanup; surface the temporal+provenance differentiation framing.
6. **Worked example** — extend the MSKCC example (or add commentary) showing PROV traversal queries answering compliance-grade questions natively.
7. **Validate**: all five conforming examples still conform; PROV typing emerges in shapes.ttl and context.jsonld.

This PR is purely annotative + emitter-aware — no entity-shape changes. Safe to merge before Visit lift.

## Pointers

- [`FIRST-PRINCIPLES.md`](../../../FIRST-PRINCIPLES.md) — to be updated with this audit's conventions.
- [`participant-planning.md`](participant-planning.md) — Decision 10 (twin-queryability) explicitly invokes NGSI-LD temporal properties; this audit makes that machine-readable.
- [`visit-planning.md`](visit-planning.md) — Visit lift will apply both conventions at lift time (Task uses `observedAt`; Visit/Activity declare prov:Activity).
- [`cdisc-dependency-pipeline.md`](cdisc-dependency-pipeline.md) — the dependency pipeline's assessment-PR record IS a PROV chain natively; this audit makes that explicit.
- [W3C PROV Overview](https://www.w3.org/TR/prov-overview/) — canonical reference.
- [W3C PROV-O OWL ontology](https://www.w3.org/TR/prov-o/) — the prov:* class/property hierarchy TOP subClasses into.
- [NGSI-LD ETSI GS CIM 009 v1.4.2](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/) — temporal-property semantics canonical reference.
