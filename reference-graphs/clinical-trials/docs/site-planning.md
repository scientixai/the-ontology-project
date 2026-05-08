# Site spec planning note (working draft)

> Working document. Edited as Site lifts from partial scaffold to full spec discipline. Folds into `site-spec.html` once the scope decisions below are sealed.
> Last touched 2026-05-08.

## Purpose

Site is the second top-level to lift to full spec discipline (per ROADMAP.md). This note captures the scope, the open architectural questions, and the recommendations to resolve before drafting `site-spec.html` and expanding the source intermediate. Deliberately short — a working artifact, not a sealed spec.

## Current state

The Site entry in `top-strawman.json` carries three attributes (`siteId`, `siteName`, `siteType`) and five relationships (`belongsToOrganization`, `partOfSiteNetwork`, `parentSite`, `hasPrincipalInvestigator`, `participatesIn`), with a `_partialEntry` note flagging that the rest of OOUX Section 3 entry #1 has not been transcribed. There is no `site-spec.html`, no Site examples, and no Site SHACL invariants. The OOUX hierarchy entry (`docs/ooux-hierarchy.html`, lines 214–224) names five sub-objects/relationships that have not been modeled yet: Site Staff (delegated), Site Network membership, Equipment (site-bound), Storage Location (site-bound), Site Performance Metric. The hierarchy also notes "Sites can exist independently of any single Study; they enter Studies through CTAs."

## OOUX Site entry — full transcription

The original OOUX document (Bo's working file) lists Site attributes and CTAs but leaves the relationships block explicitly `TODO`. The inverse view — every other object that points at Site — is the canonical source for Site's relationship set. Captured here so the source-intermediate lift is grounded in OOUX rather than re-derived.

### Attributes (OOUX-listed; 21 total)

`siteId`, `siteNumber`, `siteName`, `siteType` (HOSPITAL / CLINIC / RESEARCH_CENTER), `siteStatus` (PLANNED / ACTIVE / CLOSED), `principalInvestigatorId`, `address`, `city`, `state`, `country`, `postalCode`, `phone`, `email`, `activationDate`, `deactivationDate`, `enrollmentTarget`, `actualEnrollment`, `lastMonitoringVisitDate`, `irbId`, `regulatoryAuthority`, `tags` (array).

The current source intermediate's `siteType` enum (HOSPITAL, CLINIC, ACADEMIC_MEDICAL_CENTER, RESEARCH_CENTER, COMMUNITY_PRACTICE, DECENTRALIZED_HUB, VIRTUAL) is broader than OOUX's (HOSPITAL, CLINIC, RESEARCH_CENTER); keep the broader v0.2 enum and document the expansion in the spec's architectural-decisions section. The OOUX `siteStatus` (PLANNED, ACTIVE, CLOSED) is narrower than what an operational lifecycle wants; the open-questions section below proposes IN_QUALIFICATION and ON_HOLD additions.

### CTAs (OOUX-listed; 6 total)

Create Site, Update Site Details, Activate/Deactivate Site, Initiate Site, Monitor Site, Close Site.

### Inverse relationships (derived from every object that references Site)

Every object that names Site in its relationships block. Cardinality is the OOUX source's (Site-side cardinality reads as inverse). 36 inverse relationships in total:

- **Sponsor** 1-Many Site → Site engaged by Sponsor (already covered by Sponsor.engages, inverse)
- **Study** 1-Many Site → already modeled as Site.participatesIn → Study
- **Visit** 1 Site → Site hosts 0-Many Visit (Study-traversal candidate; see scope decision)
- **Task** 0-1 Site → Site has 0-Many Task
- **Participant** 1 Site → Site has 0-Many Participant (Study-traversal candidate)
- **Discrepancy (Query)** 1 Site → Site has 0-Many Query (Study-traversal candidate)
- **Deviation** 1 Site → Site has 0-Many Deviation
- **Screen Fail** 1 Site → Site has 0-Many Screen Fail
- **Person** 0-Many Site → Site has 1-Many Person (the Site Staff cluster)
- **CRF** 1 Site → Site has 0-Many CRF (Study-traversal candidate)
- **Document** 0-1 Site → Site has 0-Many Document
- **Adverse Event** 1 Site → Site has 0-Many Adverse Event (Study-traversal candidate)
- **Informed Consent** 1 Site → Site has 0-Many Informed Consent (Study-traversal candidate)
- **Action Item** 0-1 Site → Site has 0-Many Action Item
- **Milestone** 0-1 Site → Site has 0-Many Milestone (site-specific milestones)
- **Enrollment** 1 Site → Site has 0-Many Enrollment (Study-traversal candidate)
- **Payment** 0-1 Site → Site has 0-Many Payment
- **Investigational Product** 1-Many Site → Site uses 0-Many IP
- **Investigational Device** 1-Many Site → Site uses 0-Many Device
- **Plan** 1-Many Site → Site has 0-Many Plan
- **System** 1-Many Site → Site uses 0-Many System (the central architectural concern below)
- **System Configuration** 0-1 Site → Site has 0-Many System Configuration
- **Service Configuration** 0-1 Site → Site has 0-Many Service Configuration
- **Study Startup Package** 1 Site → Site has 1-Many Study Startup Package
- **Budget** 0-Many Site → Site has 0-Many Budget (site-specific)
- **Contract** 0-1 Site → Site has 0-Many Contract (site-specific CTA)
- **Audit** 0-1 Site → Site has 0-Many Audit
- **Report** 0-1 Site → Site has 0-Many Report
- **Shipment** Sender/Receiver Site → Site has 0-Many Shipment (sent + received)
- **CAPA** 0-1 Site → Site has 0-Many CAPA
- **Date** 0-Many Site → covered by Site's own date attributes
- **Sample** 1 Site → Site has 0-Many Sample (Study-traversal candidate via Participant)
- **Equipment** 1-Many Site → Site has 0-Many Equipment (already in Equipment horizontal via equipmentBinding)
- **User Role** 1-Many Site → Site has 0-Many User Role
- **Monitoring Visit** 1 Site → Site has 0-Many Monitoring Visit
- **Serious Adverse Event** 1 Site → Site has 0-Many SAE (Study-traversal candidate)
- **Credential** 0-1 Site → Site has 0-Many Credential (site-level credentials)

Plus two relationships from the Site attributes themselves:
- `principalInvestigatorId` → Site has 1 Person (Principal Investigator) — already modeled as `hasPrincipalInvestigator`
- `irbId` → Site has 1 Oversight Body (IRB of record) — **not yet modeled**; needs `hasIRB → OversightBody` (or `interfacesWith` mirroring Sponsor's predicate to keep the enum behavior consistent)

### Direct-vs-traversed: which inverses survive on Site

Sponsor's spec sets the precedent. Sponsor does not have direct relationships to Visit, CRF, Lab Result, Sample, etc.; those are Study-scoped and traversed. Sponsor keeps direct relationships to things that are Sponsor-scoped (Contracts, Budgets, Submissions, Audits, Documents) where Sponsor is the unambiguous owner. The same discipline applies to Site:

- **Keep direct on Site**: things that are *Site-scoped*, *Site-owned*, or *Site-contracted*. Site Staff (Person via role), Equipment (already SITE_BOUND), StorageLocation, Audits at Site, Monitoring Visits at Site, Site-specific Budgets, Site-specific Contracts, StudyStartupPackage, Credentials at Site level (`gcpCertification`, `irbApproval`, etc.), `hasIRB`, Site Performance Metric, the System usage relationships (next section).
- **Traverse via Study**: Visit, Participant, CRF, Adverse Event, SAE, Informed Consent, Enrollment, Discrepancy/Query, Sample. These are Participant-scoped or Study-scoped; the Site-side query "show me my site's open queries" is a SPARQL traversal through `?study top:participatesIn ?site`, not a direct edge on Site. Documenting this as an architectural decision keeps Site compact and honors the same discipline that kept Sponsor compact.
- **Sub-object decision**: Site Performance Metric stays as a tracked open issue rather than landing in this pass. Metric definitions are role-specific (the Sponsor's "site performance" view differs from the SMO operator's view) and belong with reference-pattern projections (v0.3 work) rather than the core schema.

This is a real architectural decision the spec needs to defend. Two countervailing pressures: (a) operator UX wants "show me Site X's everything" without authoring a graph traversal; (b) schema cleanliness wants the OWL-style "Site has Person, Person has Visit, Visit has CRF" path to stay sparse. The Sponsor spec resolved this in (b)'s favor and documented it in §5 (query patterns by persona). Site spec should do the same.

## ISF alignment

ROADMAP.md and Bo's request call for alignment with the **CDISC Investigator Site File (ISF) v1 (Provisional)**. The CDISC PDF could not be fetched in the current sandbox (network egress restricted), so this alignment is grounded in the ISF Table of Contents Bo pasted (23 sections, sourced from a Singapore HSA-flavored ISF that mirrors the international ICH E6 essential-documents structure). The ISF section structure is internationally consistent; section 10 (HSA) is country-specific and demonstrates exactly the multi-jurisdiction regulator pattern TOP's `RegulatoryAuthority` flagged-missing horizontal needs to support. **Re-validate against the actual CDISC Provisional document when accessible** — section names and counts may differ; the alignment table will need a refresh pass.

The ISF is the canonical inventory of artifacts that live at the investigator site under GCP. Its inversion onto an ontology is exactly what Site relationships should align with on the Document side and what Person relationships should align with on the Site Staff / delegation-of-authority side.

### Alignment table (ISF → TOP)

| ISF § | ISF Artifact | Primary TOP Object(s) | TOP Relationship Path | Coverage |
| --- | --- | --- | --- | --- |
| 1.1 | Site staff contact details | Person, Site | Site → hasStaff → Person (with PersonRole, contact attrs) | **GAP** — Site needs `hasStaff` |
| 1.2 | External vendor contact details | Organization (type=VENDOR, LABORATORY, CRO) | Site → engagesVendor → Organization | **GAP** — Site needs `engagesVendor` |
| 2.1, 2.2 | Investigator's Brochure (current + prior) | Document (subtype=INVESTIGATOR_BROCHURE) | Study → publishesDocument; Site has Document | PARTIAL — needs Document subtype enum |
| 3.1, 3.2 | Protocol (current + prior approved versions) | Protocol, Document | Study → hasProtocol; Protocol has versionedDocuments | PARTIAL — Protocol horizontal still flagged-missing |
| 3.3 | Protocol Signature Page(s) | Document, Person | Site has Document(subtype=PROTOCOL_SIGNATURE); Person signs | PARTIAL — needs Document subtype + signature relationship |
| 4.1, 4.2 | ICF current + prior approved versions (with translations) | InformedConsent, Document | Study → hasInformedConsent; Document has translations | PARTIAL — needs Document.translations array |
| 4.3 | Translation Certificates | Document (subtype=TRANSLATION_CERTIFICATE) | Site has Document | PARTIAL — Document subtype |
| 4.4 | Signed ICFs | InformedConsent (per Participant) | InformedConsent traversed via Study → Participant | FULL via traversal |
| 4.5 | Signed ICF Tracking Log | aggregate query, no entity | SPARQL: ICF entries WHERE site = ?site | **traversal-only** — surfaces in Site spec query patterns |
| 5.1 | Patient Card / Diary / Questionnaires (current + prior, translations) | Questionnaire, Document | Study → hasQuestionnaire (flagged-missing) | **GAP** — Questionnaire horizontal needed |
| 6 | Recruitment advertisement (current + prior, translations) | Document (subtype=RECRUITMENT_AD) | Site has Document | PARTIAL — Document subtype |
| 7.1, 7.2 | Blank CRF (current + prior) | CRF (template) | Study → hasCRFTemplate | **GAP** — CRF horizontal not yet in source |
| 7.3 | CRF Completion Guidelines | Document (subtype=CRF_GUIDELINES) | Site has Document | PARTIAL — Document subtype |
| 7.4 | Signed, dated, completed CRFs | CRF (per Participant per Visit) | traversed via Study → Participant → Visit | FULL via traversal |
| 7.5 | CRF Corrections Documentation | Discrepancy/Query, audit trail | traversed via Study → Query | FULL via traversal |
| 8 | Source Documents | Document (subtype=SOURCE_DOCUMENT) | Site has Document; per Participant | PARTIAL — Document subtype |
| 9.1 | IRB Submission and Approval Documents | Document, OversightBody | Site → hasIRB → OversightBody; Site has Document | **GAP** — Site needs `hasIRB` |
| 9.2 | Progress Reports to IRB | Report, Document | Site → submitsReportTo → OversightBody | **GAP** — relationship not modeled |
| 9.3 | IRB Composition | OversightBody attributes | OversightBody.members already in OOUX | FULL when OversightBody horizontal lifts |
| 9.4 | Notification of Safety Reports to IRB | Document, link to AE/SAE | Site has Document; AE/SAE → reportedTo → OversightBody | PARTIAL |
| 9.5 | Notification of Non-compliance to IRB | Document, Deviation | Deviation → reportedTo → OversightBody | PARTIAL |
| 9.6 | Correspondences with IRB | CommunicationLog (or Document subtype) | Site → hasCorrespondence → OversightBody | **GAP** — CommunicationLog not modeled |
| 10.1 | HSA / Regulator submissions and approvals | RegulatorySubmission, RegulatoryAuthority | Site → submitsTo → RegulatoryAuthority (per jurisdiction) | **GAP** — RegulatoryAuthority flagged-missing in current source |
| 10.2 | Trial Status Reports to HSA | Report, RegulatorySubmission | Sponsor.files → RegulatorySubmission already exists; Site-level mirror | PARTIAL |
| 10.3 | CTM Import Permit | Document (subtype=IMPORT_PERMIT) | Site has Document; ties to Shipment | PARTIAL |
| 10.4 | Expedited Safety Reports to HSA | RegulatorySubmission, SAE | SAE → reportedTo → RegulatoryAuthority | PARTIAL |
| 10.5 | Notification of Serious Breaches | Document, Deviation | Deviation → reportedTo → RegulatoryAuthority | PARTIAL |
| 10.6 | Correspondences with HSA | CommunicationLog | as 9.6 | **GAP** |
| 11.1 | Signature Sheet | Person, PersonRole, Site | Site → delegatesAuthorityTo → Person (with role, dates) | **GAP** — Delegation of Authority Record not modeled |
| 11.2 | CV of Study Personnel (incl. CITI/GCP/Medical Licensure) | Person, Credential, Document | Person → hasCredential → Credential; Credential.documentRef | PARTIAL — Credential not yet in source |
| 11.3 | Training Log/Documentation | TrainingRecord, Person | Person → hasTrainingRecord; Site → hasTrainingLog (aggregate) | PARTIAL — TrainingRecord flagged-missing in Sponsor source |
| 12.1 | Signed Confidentiality Agreement | Contract (subtype=CONFIDENTIALITY) | Site → hasContract → Contract | PARTIAL — Contract subtype enum |
| 12.2 | Signed Clinical Trial Agreement | Contract (subtype=CTA) | Site → hasContract → Contract | PARTIAL — Contract subtype enum |
| 12.3 | Other Agreements | Contract (subtype=OTHER) | Site → hasContract → Contract | PARTIAL |
| 12.4 | Insurance Certificate | Document (subtype=INSURANCE_CERT) | Site has Document | PARTIAL — Document subtype |
| 13.1 | Subject Screening Log | aggregate query | SPARQL over Screen Fail + Enrollment WHERE site = ?site | FULL via traversal |
| 13.2 | Subject Enrolment Log | aggregate query | SPARQL over Enrollment WHERE site = ?site | FULL via traversal |
| 13.3 | Subject Identification Log | aggregate query | SPARQL over Participant WHERE site = ?site | FULL via traversal |
| 13.4 | Subject Visit Tracking Log | aggregate query | SPARQL over Visit WHERE site = ?site | FULL via traversal |
| 14.1 | IP Handling Instructions | Document (subtype=IP_HANDLING) | Site has Document; ties to InvestigationalProduct | PARTIAL |
| 14.2 | IP Shipping and Receipt Records | Shipment, Document | Site has Shipment (sent + received) | **GAP** — Shipment not yet in source; need Site `receivesShipment` / `sendsShipment` |
| 14.3 | IP Dispensing and Accountability Logs | Log, Participant, IP | Log object with logType=ACCOUNTABILITY | **GAP** — Log horizontal not modeled |
| 14.4 | IP Destruction Documentation | Document (subtype=IP_DESTRUCTION), Log | Site has Document | PARTIAL |
| 14.5 | IP Storage Temperature Logs | Log, Equipment | Log + Equipment(type=FREEZER, REFRIGERATOR) | **GAP** — Log horizontal |
| 15.1 | Decoding Procedures (blinded) | Document (subtype=BLINDING_PROCEDURES) | Site has Document; ties to InvestigationalProduct | PARTIAL |
| 16.1 | Site Visit Log (monitoring) | MonitoringVisit | Site → hasMonitoringVisit | **GAP** — MonitoringVisit relationship from Site needed |
| 16.2 | Visit Correspondences | CommunicationLog, Document | Site has Document; CommunicationLog | **GAP** |
| 17.1 | Lab normal values/ranges | Document (subtype=LAB_NORMAL_RANGES) | Site → usesLaboratory → Organization (type=LABORATORY); Document | **GAP** — Site needs `usesLaboratory` |
| 17.2 | Lab Certification/Accreditation | Credential (lab-level), Document | Organization (lab) → hasCredential | PARTIAL |
| 18.1 | Biological Sample Handling Log | Log | Sample-related Log | **GAP** — Log horizontal |
| 18.2 | Biological Sample Handling Manual | Document (subtype=SAMPLE_HANDLING_MANUAL) | Site has Document | PARTIAL |
| 18.3 | Biological Samples Shipping Records | Shipment, Sample | Sample → shipped via Shipment | PARTIAL |
| 18.4 | Sample Destruction/Return Records | Document, Sample, Log | Sample → status=DESTROYED with Document trail | PARTIAL |
| 19.1 | SAE Tracking Log | aggregate query | SPARQL over SAE WHERE site = ?site | FULL via traversal |
| 19.2 | SAE Reports Submitted to Sponsor | SAE, Document | SAE → reportedToSponsor; Document | PARTIAL |
| 19.3 | Expedited Safety Reports (CIOMS) | RegulatorySubmission, Document | as 10.4 | PARTIAL |
| 20.1 | Interim Report / DSMB Reports | Report, OversightBody | Study → hasReport; OversightBody.publishesReport | PARTIAL |
| 20.2 | Final Clinical Study Report | Report (subtype=CSR) | Study → hasReport | PARTIAL |
| 20.3 | Study Publications/References | Publication | Sponsor.publishesPublication exists; Site-level mirror? | PARTIAL — Publication still flagged-missing |
| 21.1 | Investigator Meeting (agenda, attendance) | Meeting, Document | Study → hasMeeting (Meeting horizontal flagged) | **GAP** — Meeting horizontal not modeled |
| 21.2 | Site Initiation Visit (agenda, attendance, report) | MonitoringVisit (visitType=SITE_INITIATION) | Site → hasMonitoringVisit | resolves with 16.1 |
| 21.3 | Other Meeting Documentation | Meeting, Document | as 21.1 | **GAP** |
| 22.1 | Correspondences with Sponsor | CommunicationLog | Site → hasCorrespondence → Sponsor | **GAP** — CommunicationLog horizontal |
| 22.2 | Correspondences with Site Staff | CommunicationLog | Site → hasCorrespondence → Person | **GAP** |
| 22.3 | Correspondences with Central Lab/Vendors | CommunicationLog | Site → hasCorrespondence → Organization | **GAP** |
| 22.4 | Other Correspondences | CommunicationLog | catchall | **GAP** |
| 23 | Miscellaneous | Document (no subtype) | Site has Document | FULL (catchall) |

### Key findings from the alignment

Six recurring gaps surface, in rough order of how much they touch:

1. **`Document.documentType` enum needs the ISF section taxonomy folded in.** Today the source intermediate's Document has minimal typing. The Site spec should propose a Document subtype enum that mirrors the ISF section identifiers (PROTOCOL, INVESTIGATOR_BROCHURE, ICF, FORM_1572, IRB_APPROVAL, CTA, INSURANCE_CERT, SOURCE_DOCUMENT, IP_HANDLING, IP_DESTRUCTION, BLINDING_PROCEDURES, LAB_NORMAL_RANGES, SAMPLE_HANDLING_MANUAL, RECRUITMENT_AD, TRANSLATION_CERTIFICATE, …). This is the single highest-leverage change because every "PARTIAL" cell in the alignment table that says "Document subtype" closes when the enum lands.
2. **`Log` horizontal needs to lift.** ISF sections 14.3, 14.5, 18.1, plus several others, are operational logs (drug accountability log, temperature log, sample handling log, training log, IP storage temperature log, screening log). OOUX has Log as a separate object with `logType` discriminator and many cross-relationships. Right now TOP has nothing for it. Two options: (a) lift Log as its own horizontal with a `logType` enum (matches OOUX); (b) treat all logs as Document subtypes with a Log structure embedded. Recommendation: (a) — Logs have lifecycle behavior (entries appended, entries reviewed, entries cannot be retroactively edited per GCP) that Documents do not.
3. **`CommunicationLog` (or `Correspondence`) horizontal needs to lift.** ISF sections 9.6, 10.6, 22.x are all correspondence records. OOUX has Communication Log as a separate object. Today TOP has nothing for it. Could fold under Log with `logType=COMMUNICATION`; recommended approach if Log lifts as a horizontal.
4. **Site → Person delegation needs explicit modeling (`delegatesAuthorityTo`).** ISF 1.1 (staff contact details) and ISF 11 (Signature Sheet, CVs, Training Log) are the canonical Delegation of Authority artifact set. Site spec needs a `delegatesAuthorityTo → Person` relationship with role, validFrom, validUntil. The Person horizontal is itself flagged-missing today and lifts on its own track, but Site spec should *define the inverse from Site's side* now so the lift is unblocked.
5. **`RegulatoryAuthority` per-jurisdiction.** ISF section 10 is country-specific (HSA in this TOC, FDA / EMA / PMDA / NMPA / etc. in others). The source intermediate's `RegulatoryAuthority` is flagged-missing on Sponsor's `regulatoryAuthorityScope` relationship. Site spec needs `Site → submitsTo → RegulatoryAuthority` (cardinality 1..N for multi-jurisdiction sites, common in EU CTR contexts and decentralized hubs). RegulatoryAuthority horizontal needs `country` attribute and possibly `jurisdictionType` enum (NATIONAL, REGIONAL, FEDERAL, EU_CTR).
6. **Site → relationships not yet in source intermediate that the ISF demands**: `hasIRB → OversightBody`, `hasStaff` / `delegatesAuthorityTo → Person`, `engagesVendor → Organization`, `usesLaboratory → Organization`, `hasMonitoringVisit → MonitoringVisit`, `hasContract → Contract` (site-level), `hasShipment` (sender + receiver), `submitsTo → RegulatoryAuthority`. These all close ISF coverage and need to land in the source-intermediate lift step.

The alignment also **validates the direct-vs-traversed decision** in the OOUX section above. Eight ISF entries (4.5, 7.4, 7.5, 13.1–13.4, 19.1) are aggregates — log-style queries over per-Participant or per-Visit entries. None of these need a direct relationship on Site; all resolve through Study → Participant → Visit traversal. The ISF table itself is the operational view that the Site spec's query-patterns section should make formal.

The alignment table has an explicit gap that is **out of scope for the Site spec but needs a tracked roadmap entry**: ISF artifacts that are workflow ceremonies (Investigator Meeting, Site Initiation Visit) need a `Meeting` or `Ceremony` horizontal. Site Initiation Visit can be captured under MonitoringVisit (visitType=SITE_INITIATION); Investigator Meeting cannot. Adding a stub roadmap item.

## The System question (the central architectural concern)

ROADMAP.md says Site lifting "forces a confrontation with the parked System work (the three-layer ownership-versus-use pattern from the eTMF insight)." The Sponsor v0.1.3 closure log parked it differently — for the Study spec, with `Sponsor.operatesSystem` carrying the per-Study operational ownership view as a simplification. The two notes disagree on where the work lands.

Bo's framing sharpens the problem. The System question is not two-layer (ownership vs use). It is **three-axis**:

1. **Ownership** — who owns the System instance (the Site, the Sponsor, the CRO, a vendor).
2. **Use** — who interacts with the System on this Study.
3. **Visibility** — what each role can see about the System, even when ownership and use are resolved.

A worked example to ground it. Memorial Sloan Kettering (Site) uses Veeva Vault (eTMF) for Study X, sponsored by Pfizer.

- The Site sees the full record: `vendor=Veeva`, `productName=Vault`, `instanceId=mskcc-prod`, `baseUrl=https://veeva.mskcc.org/...`, `version`, `validatedFor21CFRPart11=true`.
- The Sponsor sees that the Site uses an eTMF (existence + `systemType=ETMF`), probably `vendor` and `productName`, **not** `instanceId` or `baseUrl`.
- The Regulator sees that an eTMF exists at the Site and meets 21 CFR Part 11 — typically through Site qualification documentation rather than direct system access.

The visibility axis is not just role-based redaction. The Sponsor genuinely may not know the Site's eTMF URL. There is no place in the audit trail where that fact was recorded for the Sponsor to read.

### Three options for handling visibility in the schema

**Option A — single System instance, multiple roles point at it; visibility is a projection-layer concern.** The graph carries the union of what is known. The Site's record of the eTMF is one System entity with all the attributes the Site knows. The Sponsor's `operatesSystem` and the Site's `usesEtmfSystem` (or whatever the predicates settle as) reference the same System URI when they refer to the same instance. The role-specific projection (a v0.3 reference-pattern artifact, deferred per ROADMAP.md) filters which attributes a Sponsor portal renders. Schema stays compact.

**Option B — separate System records per role; each role records what it knows.** The Sponsor's System record is a stub (`vendor`, `systemType`); the Site's System record is the full thing. They are linked via `aliasOf` or similar. Matches operational reality (the Sponsor often genuinely does not know the URL) but multiplies entities and loses graph join elegance.

**Option C — single System instance with per-attribute access-control markers.** Each attribute carries a visibility marker (e.g., `_visibleTo: [SITE_ROLE, SPONSOR_ROLE]`). Heavyweight; bleeds RBAC into the schema; couples the ontology to a specific access-control regime.

**Recommendation: Option A**, with one nuance. The graph carries truth as known by whoever populated the System record. If the Site populated, the record is full; if the Sponsor populated, the record is a stub. A second Sponsor query that joins through to the Site's record returns the union, but a Sponsor portal renders only the projection contract. Visibility is a presentation concern, not a schema concern. This dovetails with the existing v0.3 reference-architecture roadmap item ("role-specific projections and views") rather than expanding it.

The catch is that Option A pushes a real concern into the projection layer that does not yet exist. The site-spec.html should call this out as a tracked open issue rather than pretending the projection layer is sufficient today. The Sponsor spec already documents per-persona query patterns in §5; Site spec will do the same. The visibility constraint becomes "this query is what a Sponsor sees; this query is what the Site sees" — visible in the spec text, deferred for formalization.

## Scope decision for this pass

Recommend the following lift, in this order:

1. Expand Site in `top-strawman.json` to full attribute coverage from the OOUX-listed 21 attributes plus the address fields, qualification attributes (`gcpQualified`, `irbApprovalStatus`), and lifecycle status enum (recommend `PLANNED`, `IN_QUALIFICATION`, `ACTIVE`, `ON_HOLD`, `CLOSED` — broader than OOUX's three but matching operational reality).
2. Lift Site relationships to close the ISF gaps: `hasIRB → OversightBody`, `delegatesAuthorityTo → Person` (with role/dates), `engagesVendor → Organization`, `usesLaboratory → Organization`, `hasMonitoringVisit → MonitoringVisit`, `hasContract → Contract`, `submitsTo → RegulatoryAuthority`. Flag-miss the targets that are not yet in the source intermediate (Person, MonitoringVisit, Contract, RegulatoryAuthority) — same pattern Sponsor uses for its flagged-missing targets.
3. Land the `System` horizontal minimally with `vendor`, `productName`, `instanceId`, `baseUrl`, `systemType` (enum: `EDC`, `CTMS`, `ETMF`, `IRT`, `SAFETY_DB`, `EMR`, `ELN`, `OTHER`), `version`, `validatedFor21CFRPart11`. Resolves the flag-missing target on Sponsor's `operatesSystem` and Site's new `usesSystem` predicates.
4. Add Site → System relationships split per system type (`usesEtmfSystem`, `usesEdcSystem`, `usesCtmsSystem`, etc.) following the polysemous-verb-split discipline from Sponsor v0.1.2.
5. Expand `Document.documentType` enum to fold in the ISF section taxonomy (PROTOCOL, INVESTIGATOR_BROCHURE, ICF, FORM_1572, IRB_APPROVAL, CTA, INSURANCE_CERT, SOURCE_DOCUMENT, IP_HANDLING, IP_DESTRUCTION, BLINDING_PROCEDURES, LAB_NORMAL_RANGES, SAMPLE_HANDLING_MANUAL, RECRUITMENT_AD, TRANSLATION_CERTIFICATE, …). This is the single highest-leverage change for ISF coverage; closes ~15 PARTIAL cells in the alignment table.
6. Defer Site Performance Metric — capture as tracked open issue. Defer Site Staff full sub-object — `delegatesAuthorityTo` placeholder serves it for now.
7. Defer the `Log` and `CommunicationLog` horizontal lift — capture as ROADMAP additions (high-priority follow-on, several ISF gaps depend on Log).
8. Write `site-spec.html` following the Sponsor spec template: TL;DR, model summary, architectural decisions (especially the System three-axis decision and the direct-vs-traversed decision), ISF alignment as its own section, stress-test scenarios, query patterns by persona, NLP-to-NGSI-LD translation, SHACL invariants, cross-walks (FHIR, USDM, CDASH, **ISF**), tracked open issues.
9. Encode SHACL-SPARQL domain invariants. Candidate invariants: (a) hard violation when a Site has `siteType=DECENTRALIZED_HUB` but `belongsToOrganization` is absent or has type `INDIVIDUAL`; (b) hard violation when a Site claims `partOfSiteNetwork` pointing at an Organization whose `organizationType` is not `SITE_NETWORK` or `SMO`; (c) soft warning when a Site's `parentSite` and `partOfSiteNetwork` both resolve to entities that disagree on the network parent; (d) hard violation when a Site has `status=ACTIVE` but no `delegatesAuthorityTo` (no Principal Investigator on the Delegation Sheet); (e) soft warning when a Site has `submitsTo → RegulatoryAuthority` whose `country` does not match `belongsToOrganization → isLocatedIn`. Four to five invariants total, mirroring Sponsor's pattern.
10. Author one worked example mirroring `sponsor-pfizer-iqvia.ttl`: a multi-site SMO-managed network (Elevate Research operating three sites, one of which is Memorial Sloan Kettering) running a Pfizer-sponsored study, validating clean against pyshacl, exercising the ISF-derived relationships (`hasIRB`, `delegatesAuthorityTo`, `usesLaboratory`, `submitsTo`).
11. Add a `site-verification-history.html` mirroring `sponsor-verification-history.html` once Bo's verification questions for Site are answered.

## Stress-test scenarios

The scenarios that need to validate cleanly:

- A satellite clinic Site shares Equipment with its parent Site (`parentSite` + Equipment binding).
- An SMO (Elevate Research) with N member Sites, each with `partOfSiteNetwork` pointing at the Elevate Research Organization, and Organization → `managesSite` returning the full set.
- A Site changes principal investigator mid-study (temporal `hasPrincipalInvestigator`, mirrors Sponsor's `validFrom`/`validUntil` pattern).
- A `DECENTRALIZED_HUB` Site serving multiple geographic regions (no fixed address; address as 0..N rather than 1..1).
- A Site participating in twelve concurrent Studies; Sponsor wants the workload view across that Site.
- A Site uses a Sponsor-provisioned EDC and a Site-owned eTMF; the System ownership visibility split shows up in queries.
- Site qualification expires and is renewed; Site moves through `IN_QUALIFICATION → ACTIVE → ON_HOLD → ACTIVE` as the Sponsor reauthorizes.

## Open questions to resolve before sealing

1. Is `hasPrincipalInvestigator` a hard 1..1 constraint, or temporal (PI changes mid-study, like Sponsor's M&A handoff)? Recommendation: temporal, with `validFrom`/`validUntil` on the relationship.
2. Site Staff: full sub-object now, separate Person horizontal, or `delegatesTo` relationships pointing at a flagged-missing Person? Recommendation: `delegatesTo` + flagged-missing Person; Person lifts as a horizontal on its own track.
3. Status enum values and lifecycle transitions — what are the legal transitions and which need SHACL guarding?
4. CTA-mediated Study entry — does Site reference the CTA Document, or just the Study? Recommendation: just Study (`participatesIn`); CTA reference lives on the Sponsor side via `holds` relationship to Contract.
5. Site Performance Metric — sub-object now, or parked? Recommendation: parked. Surface as a tracked open issue with the rationale (metric definitions are role-specific and belong with reference-pattern projections, not the core schema).
6. Address modeling — single embedded object (mirroring Organization.legalAddress) or 0..N for multi-location decentralized hubs? Recommendation: 0..N for Site, since the decentralized-hub case is real and the multi-site-network-as-single-Organization case already exists.

## Pointers

- [`site-spec.html`](site-spec.html) — to be written; this note seeds it.
- [`ooux-hierarchy.html`](ooux-hierarchy.html) — Site OOUX entry at lines 214–224.
- [`top-strawman.json`](../source/top-strawman.json) — Site entry at line 134, partial scaffold.
- [`sponsor-spec.html`](sponsor-spec.html) — template the Site spec follows.
- [`ROADMAP.md`](../../../ROADMAP.md) — Site listed as the next top-level to lift.
