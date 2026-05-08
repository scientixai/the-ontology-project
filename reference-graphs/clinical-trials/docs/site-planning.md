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

## ICH E6(R3) alignment (canonical anchor)

ICH E6(R3) Step 4 Final (January 2025) is the current GCP standard and **supersedes R2**, including R2 Section 8 (Essential Documents). Anchoring TOP's Site spec to R3 — rather than to the legacy ISF section taxonomy — keeps the model aligned with what GCP actually requires today. The ISF section view (next subsection) becomes a legacy operational mapping that projects onto R3, not the canonical axis.

R3 PDF could not be fetched in the current sandbox (egress restricted; `host_not_allowed` on database.ich.org). This subsection is grounded in the R3 extracts Bo pasted (Section 2 Investigator, Section 3 Sponsor, Section 4 Data Governance, Appendix C Essential Records, Annex 2 framing). **Re-validate against the full R3 PDF when accessible** — Appendix C's purpose-categorized records table is the single highest-value reference for the Document horizontal lift and was not in the extracts.

### What R3 Section 2 establishes about Site (Investigator)

R3's Section 2 is the canonical definition of what a Site IS under current GCP. The thirteen subsections (2.1 Qualifications and Training, 2.2 Resources, 2.3 Responsibilities/Delegation, 2.4 IRB/IEC Communication, 2.5 Protocol Compliance, 2.6 Premature Termination, 2.7 Participant Care and Safety Reporting, 2.8 Informed Consent, 2.9 End of Participation, 2.10 IP Management, 2.11 Randomization/Unblinding, 2.12 Records, 2.13 Reports) directly inform TOP's Site model:

- **2.1 + 2.2** ground the qualification attributes (`gcpQualified`, `irbApprovalStatus`, `recruitmentPotential`, `staffingAdequate`, `facilitiesAdequate`) and tie Site qualification to *Investigator* qualification (Person, with credentials). The Investigator IS the qualified GCP entity; the Site (Institution) provides the facilities. Two roles often overlap but conceptually distinct — TOP's `hasPrincipalInvestigator → Person` already captures this.
- **2.3.3 mandates a delegation record** ("the investigator should ensure a record is maintained of the persons and parties to whom the investigator has delegated trial-related activities"). This is **GCP-required**, not optional — it hardens the planning note's `delegatesAuthorityTo` recommendation from "should have" to "must have." The Delegation of Authority Log (ISF §11.1 Signature Sheet) is the operational artifact; the relationship `delegatesAuthorityTo → Person` (with role, validFrom, validUntil, scope) is the schema modeling.
- **2.3.4 mandates documented service-provider agreements** ("Agreements with service providers should be documented"). Hardens `engagesVendor → Organization` and `usesLaboratory → Organization` from "should have" to "must have," each carrying a Contract reference.
- **2.3.5 mandates the Site permit monitoring (Sponsor), auditing (Sponsor), and inspection (Regulator)**. Hardens `hasMonitoringVisit → MonitoringVisit`, `hasAudit → Audit`, `hasInspection → RegulatorInspection` (the third is a new sub-pattern not in OOUX; capture as tracked item).
- **2.4 + 2.5 + 2.6** anchor the relationships to OversightBody (IRB/EC) and Protocol/Amendment.
- **2.7 + 2.8 + 2.9** anchor the relationships traversed via Study (Participant care, ICF, end of participation).
- **2.10 + 2.11** ground the Site's relationship to InvestigationalProduct, Randomization, Blinding.
- **2.12 + 2.13** ground the Records and Reports relationships — the records side maps to Document (per Appendix C purpose taxonomy below); the reports side maps to Report.

### R3 Section 3 reframes the System three-axis

R3 Section 3 (Sponsor responsibilities) carries the keys to the System ownership/use/visibility question:

- **3.6 Agreements** mandate documented agreements between Sponsor and any service provider (CRO, vendor, central lab, technology provider). The Sponsor's *agreement* is what grounds Sponsor oversight over a Sponsor-provisioned System.
- **3.9 Sponsor oversight** mandates that the Sponsor maintain proportionate oversight over delegated activities. The Sponsor's *oversight responsibility* is what entitles the Sponsor to visibility over the activities that fulfill a Sponsor-delegated function.

This **reframes the System three-axis cleanly**:

- **Operated by** — the party that runs the System and is responsible for its validation, security, access (R3 Section 4.3 elements). This is the *operational ownership* axis.
- **Used by** — the parties that interact with the System for trial activities. Sites, Sponsors, CRAs, central labs, etc. all use Systems; multiple roles per System.
- **Oversight held by** — the party with GCP-mandated oversight responsibility. For trial-critical Systems (EDC, CTMS, IRT, eTMF for sponsor records) this is typically the Sponsor under R3 Section 3.9 even when the System is operated by a Site or vendor. For Site-internal Systems (the Site's hospital EMR, the Site's local source-document repository) the Site holds GCP responsibility under R3 Section 2.12.

The "visibility" Bo raised maps to the **oversight axis**, not to a presentation-layer projection. Sponsor sees the URL/instanceId of the Sponsor-provisioned EDC because Sponsor operates and holds oversight; Sponsor *does not* see the URL of the Site-owned eTMF because Sponsor has no oversight right under R3 Section 3.9 — that record set is the Site's responsibility under Section 2.12. This is a *schema-level fact*, not a presentation filter.

### R3 Section 4 Data Governance — System horizontal attributes

R3 Section 4.3 (Computerised Systems) explicitly enumerates what a System must carry to be GCP-compliant:

- **4.3.1 procedures** — `proceduresDocumentRef → Document`
- **4.3.2 training** — `trainingProgramRef → TrainingProgram`
- **4.3.3 security** — `securityAssessmentRef → Document` plus security attributes
- **4.3.4 validation (risk-based)** — `validationStatus` enum, `validationRecordRef → Document`, `lastValidationDate`, `validationApproach` enum
- **4.3.5 release** — `releaseStatus` enum (UAT, PRODUCTION, RETIRED)
- **4.3.6 failure contingencies** — `contingencyPlanRef → Document`
- **4.3.7 technical support** — `supportContactId → Person`
- **4.3.8 user management / access controls** — `accessControlPolicyRef → Document`, ties to UserRole

R3 Section 4.2 Data Life Cycle adds the lifecycle stages that data flowing through a System must traverse: CAPTURE, METADATA_REVIEW, DATA_REVIEW, CORRECTION, TRANSFER, FINALIZATION, RETENTION, DESTRUCTION. This is informational at the System level (a System supports certain stages) but more directly informs the DataTransfer flagged-missing horizontal and the audit-trail / metadata aspects of every record.

The System horizontal lift in scope-decision step 3 needs to expand its attribute set to include validation status, release status, and the documentRefs above, not just `vendor`/`productName`/`instanceId`/`baseUrl`/`systemType`/`version`/`validatedFor21CFRPart11`. This is a real expansion. R3 strengthens the case that the System horizontal is heavyweight enough to deserve its own spec eventually (a v0.2 task, not v0.1).

### R3 Appendix C — Essential Records taxonomy

R3 Appendix C is **the** canonical record taxonomy. It supersedes R2 Section 8's prescriptive document list. Records are categorized along two axes:

1. **Purpose** — what the record contributes to (trial evaluation, GCP compliance, regulatory compliance, data reliability). Specific purposes named in R3 extracts: qualifications, delegation, training, IP management, monitoring, data handling, systems validation. The full purpose enum lives in Appendix C and was not in the pasted extracts; this is a follow-on transcription task.
2. **Responsible party** — INVESTIGATOR_INSTITUTION, SPONSOR, IRB_IEC, REGULATORY_AUTHORITY. R3 explicitly categorizes essential records by party.

This drives a Document horizontal change: instead of (or alongside) the ISF-section-taxonomy `documentType` enum, TOP's Document carries:

- `essentialRecordPurpose` enum (R3 Appendix C purposes) — primary axis
- `responsibleParty` enum (R3 Appendix C parties) — primary axis
- `isfSection` (string or enum, optional) — legacy operational view, maps onto R3 purpose
- `documentType` (legacy enum, optional) — operational/UX label

The R3 framing is cleaner because it captures the *function* of the record under GCP rather than a paperwork bucket. Two records that fulfill the same purpose (qualification record, training record) can have different document types (CV, certificate, training log entry) but share the same `essentialRecordPurpose` and the same GCP retention requirements.

### R3 Annex 2 — non-traditional / decentralized

R3 doesn't enumerate DCT modalities formally; it places decentralized aspects within the principles and Annex 1 applicability with proportionate/risk-based approaches across resources, oversight, data capture, computerised systems, and records. This means TOP's existing `siteType` enum (HOSPITAL, CLINIC, ACADEMIC_MEDICAL_CENTER, RESEARCH_CENTER, COMMUNITY_PRACTICE, DECENTRALIZED_HUB, VIRTUAL) is sufficient — no new `siteModality` attribute is needed. The flexibility lives in *how* the existing relationships are populated (a VIRTUAL Site has no physical address; a DECENTRALIZED_HUB Site has 0..N addresses; a HOSPITAL Site has exactly 1 address) rather than in a new enum.

### R3-grounded Site relationship map

Bo's R3 Annex 1 synthesis provides the OOUX-style relationship map that lifts directly into the source intermediate. Captured here with how each line resolves against the model:

**Site definition (R3 Annex 1)**: "The location(s) where trial-related activities are conducted and/or coordinated under the investigator's/institution's oversight." Goes into the `Site.description` field in the source intermediate.

**Site attributes (R3-derived, on top of the OOUX 21)**:

- `oversightTier` (LOW, MEDIUM, HIGH) — captures R3's risk-based monitoring discipline (Section 3.10 quality management). Drives the proportionate-monitoring Sponsor decisions and matters for the Sponsor's per-Site monitoring frequency view.
- `essentialRecordsRetentionUntil` (xsd:date or xsd:duration) — R3 retention requirements vary by jurisdiction and contract; surfacing as a per-Site attribute lets retention queries roll up cleanly.
- The OOUX 21 attributes already cover the rest (qualifications via `gcpQualified` + tied Person credentials; resources via `enrollmentTarget`/`actualEnrollment`/`staffingAdequate`/`facilitiesAdequate`; status lifecycle via `siteStatus`; modality via `siteType`).

**Site relationships (R3-grounded, 11 clusters from Bo's map)**:

1. **Investigator** (core ownership) — Site → `hasPrincipalInvestigator` → Person (1..1, GCP-required by R3 Section 2). The cardinality is hard-required: under R3 a Site without a qualified Investigator cannot conduct a trial. Bo's map says "Strong containment: Investigator → Site" — this is the R3 framing where Investigator is the GCP-responsible entity. The current `belongsToOrganization` (legal owner) and `hasPrincipalInvestigator` (GCP-responsible) split is the right two-relationship resolution; Investigator is the primary GCP entity, Organization is the legal entity. Site spec should articulate this as an architectural decision.
2. **Sponsor** (engagement + oversight) — Site engaged by Sponsor (already covered: inverse of `Sponsor.engages → Site`). NEW: `Site.reportsTo → Sponsor` (0..N, for safety/data/noncompliance reporting per R3 Section 2.7, 2.13). Sponsor oversight is captured through MonitoringVisit and Audit relationships (already in the lift plan).
3. **Service Providers / Vendors** — `Site.engagesVendor → Organization` (already in the lift plan); `Site.usesLaboratory → Organization` (already in the lift plan). R3 nuance: the Investigator retains final decision on appropriateness of Sponsor-engaged service providers — this is a stress-test scenario, not a separate schema relationship (over-modeling).
4. **IRB/IEC** — `Site.hasIRB → OversightBody` (already in the lift plan, 1..1 typically, 1..N for multi-IRB cases); `Site.submitsTo → OversightBody` (or fold into hasIRB with submission-tracking attributes — see open question below).
5. **Regulatory Authorities** — `Site.submitsTo → RegulatoryAuthority` (already in the lift plan, 1..N for multi-jurisdiction).
6. **Trial / Protocol** — `Site.participatesIn → Study` (already in the source); `Site.compliesWithProtocol → Protocol` is implicit through participatesIn — over-modeling to add a separate relationship.
7. **Participants** — TRAVERSED via Study (per direct-vs-traversed decision in the OOUX section); R3 confirms this is correct — Site's relationship to Participants is *operationally* through Study membership, not as a direct entity link.
8. **Investigational Product** — `Site.usesInvestigationalProduct → InvestigationalProduct` (or split: `dispensesIP`, `storesIP`, `accountsForIP` per the polysemous-verb-split discipline). Recommend single `usesInvestigationalProduct` relationship in v0.1; split if behavior diverges.
9. **Computerised Systems & Data** — covered by the System three-axis decision above. Site has `operatedBy → Site`/`usedBy → Site`/`oversightHeldBy → Site` per System instance.
10. **Essential Records** — covered by the Document horizontal with `essentialRecordPurpose` + `responsibleParty=INVESTIGATOR_INSTITUTION` (per R3 Appendix C). No separate `maintainsEssentialRecords` predicate needed; standard `Site → has Document` traversal with appropriate filters serves it.
11. **Decentralized / Non-Traditional Modalities** — captured by existing `siteType` enum (no separate `siteModality` attribute, per the R3 Annex 2 framing).

**New relationships introduced by the R3 synthesis** (beyond what was already in the lift plan):

- `Site.reportsTo → Sponsor` (0..N) — bidirectional safety/data/noncompliance reporting per R3 2.7, 2.13. Captures the operational reverse of Sponsor's monitoring/oversight.

**R3 lift plan delta** (vs. the scope decision section): step 2 of the scope decision adds `reportsTo → Sponsor` to the Site relationship lift. Step 1 adds `oversightTier` and `essentialRecordsRetentionUntil` to the attribute lift.

### Role conflation: Investigator-Initiated Trials (IITs)

In an IIT (sometimes IIS, investigator-initiated study), the Investigator is the Sponsor. The Site at which the Investigator works is operationally also the Sponsor's "office." This is a real and common pattern (academic single-PI trials, hospital IITs, rare-disease patient-foundation-funded trials) and the schema needs to handle it without special-casing.

**R3 does not relax sponsor obligations in IITs.** The Investigator-Sponsor still owes Section 3.10 quality management, Section 3.11 monitoring, Section 3.13 safety reporting, Section 3.14 insurance, Section 3.6 documented agreements with any service providers. These obligations often get under-resourced in IITs and create regulatory risk; the schema's job is to make them visible by keeping the Sponsor entity present, not collapsed into the Site.

**The schema already supports this** through the existing relationships:

- The same `Organization` plays both `playsSponsorRole → Sponsor` AND `managesSite → Site`. The Organization horizontal does not need to know it is "playing both roles" — it just plays whichever roles its sub-entities point at.
- The same `Person` is `Site.hasPrincipalInvestigator` AND a key contact on the `Sponsor` (`primaryContactId`, `regulatoryContactId`).
- The Sponsor entity carries `sponsorType=ACADEMIC` (or `INVESTIGATOR_SPONSOR`, depending on how the existing Sponsor enum settles) and `isInitiator=true`. The Sponsor spec's v0.1 already models this — Site spec inherits it.

**No new relationship needed for IITs.** The role conflation is captured by the *same entity* (Organization, Person) appearing on both sides, not by a new "isAlsoSponsor" predicate on Site. This is a deliberate architectural decision: special-casing IITs in the schema would force every consumer to know about the special case; using the same Organization-plays-multiple-roles pattern keeps the schema general and lets queries discover IIT structure naturally ("WHERE the Sponsor's `belongsToOrganization` equals the Site's `belongsToOrganization`").

**The System three-axis pattern interacts in interesting ways under IIT.** When the Investigator-Sponsor uses an EDC, the System's `operatedBy`, `usedBy`, and `oversightHeldBy` all may resolve to the same Organization. This is *not a bug* — it correctly reflects that the same party owns and uses and oversees the System. SHACL invariant (f) (hard violation when `oversightHeldBy → Site` for `systemType=EDC|CTMS|IRT|SAFETY_DB`) needs an IIT-aware exception: when the Site's `belongsToOrganization` equals a Sponsor's `belongsToOrganization` for the same Study, the invariant should not fire. Capture this as a stress test and a SHACL refinement (a SPARQL CONSTRAINT with the IIT-equality test).

**Implications for direct-vs-traversed**: the Site spec's recommended discipline (traverse to Visit/CRF/AE/etc. via Study) holds in IITs because the Sponsor → Study → Site → Visit path is unchanged. The same query that gets a Sponsor PM their workload view for a multi-site trial gets the Investigator-Sponsor their workload view for an IIT. No bifurcation needed.

**Action for Site spec**: include an explicit "IIT pattern" worked example in the architectural-decisions section. Memorial Sloan Kettering as Investigator-Sponsor of an IIT — same Organization (MSKCC), same Person (Dr. X) playing PI on Site and primary contact on Sponsor, Sponsor.sponsorType=ACADEMIC and Sponsor.isInitiator=true. Validate that the SHACL invariants behave correctly (none fire wrongly) and that the multi-Sponsor-of-record-per-jurisdiction edge cases (a US IIT that adds an EU site requires the Sponsor entity to handle EU CTR Article 74 legal-rep — which the Sponsor spec already covers via `parentSponsor`).

## ISF alignment (legacy operational view)

The ISF section taxonomy is the **legacy operational view** that maps onto R3 Appendix C. Maintaining the alignment is still valuable: many sponsors, CROs, and sites operate against the ISF as the day-to-day artifact organization, and any Site spec ignoring the ISF would be operationally awkward. But the canonical anchor is R3 Appendix C; ISF mappings are secondary.

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

Bo's framing sharpened the problem to **three axes**: ownership / use / visibility. R3 Section 3 (above) sharpens it further: the third axis is *oversight*, not visibility. Visibility *follows from* oversight under GCP — Sponsor sees what Sponsor has agreement-grounded oversight over (R3 3.6, 3.9); Site sees what Site is GCP-responsible for (R3 2.12, 2.13). This is a **schema-level fact**, not a presentation filter.

The reframed three axes:

1. **Operated by** — the party that runs the System and is responsible for its R3 Section 4.3 obligations (validation, security, access controls, release, contingency, support).
2. **Used by** — the parties that interact with the System for trial activities (Sites, Sponsors, CRAs, central labs, etc. — multiple roles per System instance).
3. **Oversight held by** — the party with GCP-mandated oversight responsibility under R3 Section 3.9 (Sponsor for trial-critical Sponsor-delegated Systems even when operated by a Site or vendor) or under R3 Section 2.12 (Site for Site-internal records like the Site's source-document repository).

A worked example to ground it. Memorial Sloan Kettering (Site) uses two eTMF-class systems for Study X, sponsored by Pfizer.

- *Veeva Vault Sponsor eTMF* — operated by Pfizer (or Pfizer's CRO under documented agreement, R3 3.6); used by Pfizer staff and authorized MSKCC staff; oversight held by Pfizer (R3 3.9). Schema: System instance with `operatedBy → Sponsor (Pfizer)`, `usedBy → Site (MSKCC)`, `oversightHeldBy → Sponsor (Pfizer)`. MSKCC sees the full instance details by virtue of being a `usedBy` — Pfizer has authorized them. Pfizer sees everything by virtue of operating and holding oversight.
- *MSKCC ISF (Site source-document repository)* — operated by MSKCC; used by MSKCC; oversight held by MSKCC under R3 2.12. Schema: System instance with `operatedBy → Site (MSKCC)`, `usedBy → Site (MSKCC)`, `oversightHeldBy → Site (MSKCC)`. Pfizer's monitor accesses *records* during monitoring visits (R3 2.3.5) but does not access the System instance directly — there is no Pfizer triple in the graph for this System.

What this resolves: the Sponsor genuinely does not know the URL of the Site-owned ISF *because there is no triple linking Pfizer to that System*. It's not a presentation-layer filter; it's the schema's truth. Conversely, the Sponsor knows the URL of the Sponsor-operated eTMF *because Pfizer is the `operatedBy`*. This is much cleaner than the original "Option A — visibility as projection" recommendation.

### Three options for handling the System pattern in the schema (revised)

**Option A — single System instance, three role-relationships (`operatedBy`, `usedBy`, `oversightHeldBy`).** The schema captures GCP responsibility allocation. Visibility follows from the relationships: a party sees a System if there is a triple connecting them. The presentation layer adds attribute-level filtering on top (per-role projection), but the *existence* of the relationship is what determines whether a System is "visible" at all. Recommended.

**Option B — separate System records per role (the original "Option B").** Each role records what it knows. Multiplies entities and loses join elegance. Now strictly worse than Option A under the R3 reframe — no operational case where it wins.

**Option C — single System instance with per-attribute access-control markers (the original "Option C").** Bleeds RBAC into the schema. Now strictly worse — R3 framing is *responsibility allocation*, not access control.

**Recommendation: revised Option A.** The R3-aligned three-relationship pattern (`operatedBy`, `usedBy`, `oversightHeldBy`) replaces the original visibility-as-projection framing. Three benefits:

1. **Schema-level truth** matches GCP truth. A System's responsibility allocation IS a GCP fact under R3 — it deserves to be in the graph.
2. **Sponsor visibility into Site systems is no longer mysterious.** Sponsor either has an oversight triple (entitled to see) or does not (not entitled). The Site-owned eTMF case where Sponsor doesn't know the URL is correctly modeled as "no Sponsor → System triple" rather than as "Sponsor's projection filters out the URL."
3. **The Site's `usesSystem` predicate split** (`usesEtmfSystem`, `usesEdcSystem`, etc., per the polysemous-verb-split discipline) carries one role per relationship, with the System instance carrying its own `operatedBy` and `oversightHeldBy`. Clean.

The presentation layer still has work to do (rendering only the attributes a particular user is authorized to see), but that work is **per-role projection on already-visible Systems**, not visibility-as-presentation. The v0.3 reference-pattern roadmap item retains its scope; it just becomes finer-grained projection rather than schema-substitute.

This is a **non-trivial change to the planning recommendation**. The earlier "Option A — visibility as projection" stance is now superseded by "Option A revised — visibility as oversight relationship." Site spec needs to document the supersession explicitly (the architectural-decisions section should carry both framings for traceability — "we considered X then revised to Y when R3 grounded the framing").

## Scope decision for this pass

Recommend the following lift, in this order:

1. Expand Site in `top-strawman.json` to full attribute coverage. Lift the OOUX-listed 21 attributes plus: address fields (0..N for decentralized hubs), qualification attributes (`gcpQualified`, `irbApprovalStatus`, `recruitmentPotential`, `staffingAdequate`, `facilitiesAdequate`), R3-derived attributes (`oversightTier` enum LOW/MEDIUM/HIGH, `essentialRecordsRetentionUntil`), and lifecycle status enum (recommend `PLANNED`, `IN_QUALIFICATION`, `ACTIVE`, `ON_HOLD`, `CLOSED` — broader than OOUX's three but matching operational reality and R3 Section 2.6 termination/suspension framing). Anchor the Site description in the source intermediate to R3 Annex 1's Site definition.
2. Lift Site relationships to close ISF and R3 gaps: `hasIRB → OversightBody`, `delegatesAuthorityTo → Person` (with role/dates, GCP-required by R3 2.3.3), `engagesVendor → Organization` (R3 2.3.4), `usesLaboratory → Organization`, `hasMonitoringVisit → MonitoringVisit`, `hasContract → Contract`, `submitsTo → RegulatoryAuthority`, `reportsTo → Sponsor` (R3 2.7, 2.13). Flag-miss the targets that are not yet in the source intermediate (Person, MonitoringVisit, Contract, RegulatoryAuthority) — same pattern Sponsor uses for its flagged-missing targets.
3. Land the `System` horizontal with R3-aligned attributes: `vendor`, `productName`, `instanceId`, `baseUrl`, `systemType` (enum: `EDC`, `CTMS`, `ETMF`, `IRT`, `SAFETY_DB`, `EMR`, `ELN`, `OTHER`), `version`, `validatedFor21CFRPart11`, plus R3 Section 4.3 attributes (`validationStatus`, `validationApproach`, `lastValidationDate`, `releaseStatus`, `proceduresDocumentRef`, `securityAssessmentRef`, `accessControlPolicyRef`, `contingencyPlanRef`, `supportContactId`). System.attributes will be the heaviest single change in this lift; the System spec ultimately deserves its own first-class spec doc (a v0.2 task, not v0.1, but flag it).
4. Add the System role-relationships per the revised three-axis: `operatedBy → Sponsor|Site|Organization`, `usedBy → Sponsor|Site|Organization` (0..N), `oversightHeldBy → Sponsor|Site` (1..1, GCP-required). Add Site → System relationships split per system type (`usesEtmfSystem`, `usesEdcSystem`, `usesCtmsSystem`, etc.) following the polysemous-verb-split discipline from Sponsor v0.1.2.
5. Expand `Document` horizontal with R3 Appendix C alignment: add `essentialRecordPurpose` enum (R3 purposes — full enum requires Appendix C transcription, not in the pasted extracts; placeholder values: `QUALIFICATION`, `DELEGATION`, `TRAINING`, `IP_MANAGEMENT`, `MONITORING`, `DATA_HANDLING`, `SYSTEMS_VALIDATION`, plus more from Appendix C); add `responsibleParty` enum (`INVESTIGATOR_INSTITUTION`, `SPONSOR`, `IRB_IEC`, `REGULATORY_AUTHORITY`); add `isfSection` (string, optional, legacy mapping); keep `documentType` for legacy operational view. R3 Appendix C purpose taxonomy is the canonical primary axis; ISF section is the legacy operational view. This is the single highest-leverage change for both R3 and ISF coverage.
6. Defer Site Performance Metric — capture as tracked open issue. Defer Site Staff full sub-object — `delegatesAuthorityTo` placeholder serves it for now.
7. Defer the `Log` and `CommunicationLog` horizontal lift — capture as ROADMAP additions (high-priority follow-on, several ISF gaps depend on Log).
8. Write `site-spec.html` following the Sponsor spec template: TL;DR, model summary, **R3 alignment** as a first-class section (with the System three-axis decision documented as an explicit architectural decision, including the supersession trace from "visibility-as-projection" to "oversight-as-relationship"), **ISF alignment** as a legacy-operational-view section, stress-test scenarios, query patterns by persona, NLP-to-NGSI-LD translation, SHACL invariants, cross-walks (FHIR, USDM, CDASH, **ICH E6(R3)**, **ISF**), tracked open issues.
9. Encode SHACL-SPARQL domain invariants. Candidate invariants: (a) hard violation when a Site has `siteType=DECENTRALIZED_HUB` but `belongsToOrganization` is absent or has type `INDIVIDUAL`; (b) hard violation when a Site claims `partOfSiteNetwork` pointing at an Organization whose `organizationType` is not `SITE_NETWORK` or `SMO`; (c) soft warning when a Site's `parentSite` and `partOfSiteNetwork` both resolve to entities that disagree on the network parent; (d) hard violation when a Site has `status=ACTIVE` but no `delegatesAuthorityTo` with role=PRINCIPAL_INVESTIGATOR (R3 2.3.3 — no PI on the Delegation Sheet means no GCP-compliant Site); (e) soft warning when a Site has `submitsTo → RegulatoryAuthority` whose `country` does not match `belongsToOrganization → isLocatedIn`; (f) hard violation when a System has `oversightHeldBy → Site` but is `systemType=EDC|CTMS|IRT|SAFETY_DB` **with an IIT exception** (the constraint does not fire when the Site's `belongsToOrganization` equals a Sponsor's `belongsToOrganization` for the same Study — the IIT case where one party plays both roles is legitimate; SPARQL CONSTRAINT carries the equality test); (g) soft warning when a Sponsor-engaged service provider (Site's `engagesVendor → Organization` where the Organization plays a CRO role on the Sponsor side) does not have a Site-side documented agreement (R3 2.3.4 requires it; the Investigator's right of refusal under R3 2.3 means absence is meaningful). Five to seven invariants total.
10. Author one worked example mirroring `sponsor-pfizer-iqvia.ttl`: a multi-site SMO-managed network (Elevate Research operating three sites, one of which is Memorial Sloan Kettering) running a Pfizer-sponsored study, validating clean against pyshacl, exercising the R3- and ISF-derived relationships (`hasIRB`, `delegatesAuthorityTo`, `usesLaboratory`, `submitsTo`, `reportsTo`, the System three-axis pattern with one Sponsor-operated EDC and one Site-operated ISF).
11. Add a `site-verification-history.html` mirroring `sponsor-verification-history.html` once Bo's verification questions for Site are answered.

## Stress-test scenarios

The scenarios that need to validate cleanly:

- A satellite clinic Site shares Equipment with its parent Site (`parentSite` + Equipment binding).
- An SMO (Elevate Research) with N member Sites, each with `partOfSiteNetwork` pointing at the Elevate Research Organization, and Organization → `managesSite` returning the full set.
- A Site changes principal investigator mid-study (temporal `hasPrincipalInvestigator`, mirrors Sponsor's `validFrom`/`validUntil` pattern).
- A `DECENTRALIZED_HUB` Site serving multiple geographic regions (no fixed address; address as 0..N rather than 1..1).
- A Site participating in twelve concurrent Studies; Sponsor wants the workload view across that Site.
- A Site uses a Sponsor-provisioned EDC (`operatedBy → Sponsor`, `oversightHeldBy → Sponsor`) and a Site-owned ISF (`operatedBy → Site`, `oversightHeldBy → Site`); the Sponsor's portal correctly shows the EDC details but no Site-ISF triple, validating the R3 oversight-as-relationship framing.
- Site qualification expires and is renewed; Site moves through `IN_QUALIFICATION → ACTIVE → ON_HOLD → ACTIVE` as the Sponsor reauthorizes.
- **R3 2.3 Investigator's right to refuse a Sponsor-engaged service provider**: Sponsor engages CRO ABC for monitoring; Site refuses (R3 2.3 nuance) and the schema must support the Site having `engagesVendor → CRO XYZ` instead, with documented disagreement captured via Document(essentialRecordPurpose=DELEGATION, responsibleParty=INVESTIGATOR_INSTITUTION).
- **R3 4.3 Computerized Systems validation lifecycle**: A Site uses an EDC that moves through validation states (DEVELOPMENT → UAT → PRODUCTION → REVALIDATION → RETIRED); the System's `validationStatus` and `releaseStatus` carry the lifecycle, with linked `validationRecordRef → Document` per stage.
- **R3 Appendix C essential record retention**: A Site closes a Study; essential records must be retained until `essentialRecordsRetentionUntil`, after which destruction is permitted; the Site's Document(essentialRecordPurpose=*) entries carry the retention attribute.
- **Investigator-Initiated Trial (IIT) pattern**: MSKCC plays both Sponsor and Site roles; Dr. Patel is `Site.hasPrincipalInvestigator` and `Sponsor.primaryContactId`/`Sponsor.regulatoryContactId`. Sponsor.sponsorType=ACADEMIC, Sponsor.isInitiator=true. The same EDC has `operatedBy → Sponsor (MSKCC-as-Sponsor)`, `usedBy → Site (MSKCC-as-Site)`, `oversightHeldBy → Sponsor (MSKCC-as-Sponsor)` — all resolving to the same Organization. SHACL invariant (f) does NOT fire (IIT exception). Sponsor obligations under R3 Section 3 (QMS, monitoring, safety reporting, insurance) are still enforceable through the Sponsor entity's relationships (commissions Audit, operatesSystem for safety database, etc.).

## Open questions to resolve before sealing

1. Is `hasPrincipalInvestigator` a hard 1..1 constraint, or temporal (PI changes mid-study, like Sponsor's M&A handoff)? Recommendation: hard-required 1..1 (R3 2.1, 2.3.1 grounds the requirement), with `validFrom`/`validUntil` on the relationship for temporal handoffs (a Site cannot be `status=ACTIVE` without a current PI).
2. Site Staff: full sub-object now, separate Person horizontal, or `delegatesAuthorityTo` relationships pointing at a flagged-missing Person? Recommendation: `delegatesAuthorityTo` + flagged-missing Person; Person lifts as a horizontal on its own track. R3 2.3.3 mandates the delegation record exists; the relationship covers it.
3. Status enum values and lifecycle transitions — recommendation `PLANNED → IN_QUALIFICATION → ACTIVE → (ON_HOLD ↔ ACTIVE) → CLOSED`. SHACL invariants on (a) Active without PI; (b) re-activation from CLOSED (illegal — Sites that close stay closed).
4. CTA-mediated Study entry — does Site reference the CTA Document, or just the Study? Recommendation: just Study (`participatesIn`); CTA reference lives on the Sponsor side via `holds` relationship to Contract, with the Site's `hasContract → Contract` (CTA subtype) capturing the Site-side view.
5. Site Performance Metric — sub-object now, or parked? Recommendation: parked. Surface as a tracked open issue with the rationale (metric definitions are role-specific and belong with reference-pattern projections, not the core schema).
6. Address modeling — single embedded object (mirroring Organization.legalAddress) or 0..N for multi-location decentralized hubs? Recommendation: 0..N for Site, since the decentralized-hub case is real and the multi-site-network-as-single-Organization case already exists.
7. **Is `belongsToOrganization` (legal owner) AND `hasPrincipalInvestigator` (GCP-responsible) the right two-relationship resolution, or does R3's "Strong containment: Investigator → Site" framing argue for collapsing?** Recommendation: keep both. They model different facts — legal entity vs GCP-responsible person — and R3 itself uses both ("investigator/institution" throughout). Articulate as architectural decision in spec.
8. **Does the System horizontal need its own spec doc, or does it stay as a horizontal supporting Site/Sponsor/Study?** Recommendation: stays as a horizontal in v0.1 (the Site spec covers the System three-axis pattern in its architectural-decisions section); promote to its own spec in v0.2 (the System horizontal will accumulate enough mass — R3 4.3 alone gives it ~10 attributes — that a dedicated spec is warranted).
9. **R3 Appendix C purpose enum — what's the canonical list?** The pasted extracts named seven purposes (qualifications, delegation, training, IP management, monitoring, data handling, systems validation) but the full list lives in Appendix C of the R3 PDF. Action: transcribe Appendix C when the PDF is accessible; for v0.1 use the seven named purposes as the placeholder enum and flag the enum as `_partialEnum` in the source intermediate (analogous to `_targetMissing`).
10. **Site-vs-Investigator approval of Sponsor-engaged service providers** (R3 2.3 nuance) — does this need a schema relationship (`acceptsServiceProvider`/`refusesServiceProvider`) or is it captured operationally through the *presence* of `Site.engagesVendor → Organization` (the Site's own engagement triple)? Recommendation: operational — no separate schema relationship; the absence of a Site engagement triple where the Sponsor expected one is the refusal. Stress-test it (above).

## Pointers

- [`site-spec.html`](site-spec.html) — to be written; this note seeds it.
- [`ooux-hierarchy.html`](ooux-hierarchy.html) — Site OOUX entry at lines 214–224.
- [`top-strawman.json`](../source/top-strawman.json) — Site entry at line 134, partial scaffold.
- [`sponsor-spec.html`](sponsor-spec.html) — template the Site spec follows.
- [`ROADMAP.md`](../../../ROADMAP.md) — Site listed as the next top-level to lift.
