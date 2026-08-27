# Work B: Versioned Class Audit Ledger

This ledger documents the keep/demote decision for every CR/HCLS class that is currently `rdfs:subClassOf top:Versioned`.

## Decision Criterion
A class KEEPS `top:Versioned` if it needs an append-only version chain for one of these reasons:
- Append-only judgments whose correction history matters
- Locked/signed/hashed regulatory records
- GCP-critical audit trails (21 CFR Part 11, ICH E6)
- IMP accountability chain (GMP requirements)

Otherwise, DEMOTE: the class remains `top:CommonEntity` (carries DNA: identifier + observedAt + status) but drops the bitemporal envelope (validFrom + prov:specializationOf → VersionSeries).

## Worked Cases (from instructions)
- **cr:CodeAssignment** → **KEEP** — append-only judgment, correction history matters
- **cr:CausalityAssessment** → NOT Versioned (already top:Conclusion only) — no change needed

---

## KEEP (46 classes)

### Regulatory/Locked Documents
1. **cr:AnalysisDataset** → KEEP — locked for regulatory submission, signed/hashed for Define-XML
2. **cr:ClinicalStudyReport** → KEEP — regulatory document (ICH E3), locked after completion
3. **cr:ProtocolVersion** → KEEP — regulatory document, protocol amendments require version history
4. **cr:SafetyReport** → KEEP — regulatory submission (expedited SAE reporting), immutable after filing
5. **cr:INDApplication** → KEEP — regulatory submission to FDA
6. **cr:GLPToxReport** → KEEP — GLP-governed preclinical toxicology report
7. **cr:Publication** → KEEP — published scientific output, immutable after publication
8. **cr:RegistryRecord** → KEEP — ClinicalTrials.gov / EudraCT posting, regulatory requirement
9. **cr:IntegratedSummary** → KEEP — ISS/ISE regulatory document
10. **cr:eCTDSubmission** → KEEP — regulatory filing

### Append-only Judgments & Decisions
11. **cr:CodeAssignment** → KEEP — (worked case) append-only judgment, correction history matters
12. **cr:AnalysisDecision** → KEEP — statistical decision with authority, audit trail required
13. **cr:DatabaseLock** → KEEP — pivotal decision, triggers lockdown
14. **cr:DatabaseUnlock** → KEEP — controlled reopening with reason, audit critical
15. **cr:SiteSelectionDecision** → KEEP — site selection/rejection with rationale, revision tracking explicit in class comment
16. **cr:UnblindingEvent** → KEEP — critical for trial integrity, emergency unblinding must be immutable
17. **cr:RandomizationEvent** → KEEP — critical for trial integrity, randomization must never be silently changed
18. **cr:RiskAssessment** → KEEP — RBQM judgment, re-assessments supersede (class comment: "bitemporal: re-assessments supersede, never overwrite")
19. **cr:LimitBreach** → KEEP — promoted judgment (P6), root-cause determination, CSR reporting
20. **cr:IRBApproval** → KEEP — regulatory gate, approval decisions require version history
21. **cr:EndpointResult** → KEEP — analysis result for primary/secondary endpoints, locked for publication

### GCP-Critical Audit Records (21 CFR Part 11, ICH E6)
22. **cr:Enrollment** → KEEP — PII-sensitive bridge (hcls:Person ↔ cr:StudySubject), GCP-critical
23. **cr:Delegation** → KEEP — GCP audit trail (delegation of authority log)
24. **cr:InformedConsent** → KEEP — subject rights, regulatory record
25. **cr:Credential** → KEEP — GCP qualification/training record gating delegation
26. **cr:AuditTrail** → KEEP — ICH E6(R3) ALCOA++ record, must be immutable by definition
27. **cr:EssentialRecord** → KEEP — ICH E6(R3) essential document for trial reconstruction
28. **cr:SourceData** → KEEP — ICH E6(R3) original recorded information, audit trail required
29. **cr:CertifiedCopy** → KEEP — ICH E6(R3) verified copy, must be immutable once certified
30. **cr:ConsentWithdrawal** → KEEP — subject rights, regulatory record
31. **cr:DeviationEvent** → KEEP — GCP deviation record, bitemporal + attested (class comment explicit)
32. **cr:CAPA** → KEEP — QMS corrective action, bitemporal + attested (class comment explicit)
33. **cr:DataProcessingAgreement** → KEEP — GDPR/privacy legal agreement, immutable once executed
34. **cr:DataTransferAgreement** → KEEP — DTA legal agreement, versioned + ratified (class comment explicit)
35. **cr:ClinicalTrialAgreement** → KEEP — legal contract, immutable once executed

### IMP Accountability Chain (GMP)
36. **cr:DispensingEvent** → KEEP — pivotal IMP accountability event (class comment: "pivotal accountability event")
37. **cr:DestructionEvent** → KEEP — IMP destruction must be authorized + immutable (class comment: "authorized destruction...closing its accountability chain")

### Operational Events with Regulatory/Audit Requirements
38. **cr:LastPatientLastVisit** → KEEP — study milestone that opens closeout, triggers regulatory timelines
39. **cr:KitAssignment** → KEEP — blinded kit assignment, critical for trial integrity
40. **cr:TableListingFigure** → KEEP — analysis output artifact, locked for CSR/submission
41. **cr:SiteActivation** → KEEP — regulatory gate (site ready to enroll), approval decision
42. **cr:SiteClosure** → KEEP — regulatory closeout milestone
43. **cr:InvestigatorSiteFile** → KEEP — ISF archival, GCP essential document
44. **cr:ArchivalEvent** → KEEP — long-term retention event, regulatory requirement (21 CFR 312.62)

### HCLS-wide Consent Framework (Bo ruling, 27 Aug 2026)
45. **hcls:Consent** → KEEP — promotion to HCLS deliberate; consent has HCLS-wide specializations (research ICF, HIPAA authorization, e-sign, treatment). Durable auditable authorization with valid and transaction time; withdrawal/correction must stay reconstructable. (Bo)

---

## DEMOTE (38 classes)

These classes are operational events or data points where correction is a new observation/event, not a version supersession:

### Operational Events (correction = new event)
1. **cr:Administration** → DEMOTE — dosing event; correction is a new observation, not a version chain
2. **cr:AdverseEvent** → DEMOTE — event occurrence; correction is a new observation (note: coding judgments about the AE are separate cr:CodeAssignment entities that DO version)
3. **cr:ActivityOccurrence** → DEMOTE — visit activity; operational data capture
4. **cr:VisitOccurrence** → DEMOTE — visit; operational execution record
5. **cr:Shipment** → DEMOTE — IMP shipment; operational logistics event
6. **cr:ReturnEvent** → DEMOTE — IMP return; operational accountability (less critical than dispense/destroy)
7. **cr:TemperatureExcursion** → DEMOTE — promoted fact (good!), but the excursion event itself doesn't need version chain
8. **cr:ClinicalObservation** → DEMOTE — clinical data point; correction is a new observation
9. **cr:Query** → DEMOTE — eCRF query; operational data-management workflow
10. **cr:CustodyEvent** → DEMOTE — specimen custody transfer; operational chain event
11. **cr:AssayResult** → DEMOTE — lab result; operational data (though traceable via PROV)
12. **cr:LabOrder** → DEMOTE — lab test order; operational
13. **cr:AssayDefinition** → DEMOTE — assay protocol/definition; specification, not a locked judgment
14. **cr:TransferFile** → DEMOTE — file delivery event; operational DTA execution
15. **cr:PreScreening** → DEMOTE — preliminary eligibility check; operational screening step
16. **cr:ScreeningRecord** → DEMOTE — formal screening outcome is recorded, but doesn't need version chain (the screening decision is a value on the record)
17. **cr:ItemGroup** → DEMOTE — eCRF form/section; data structure, not a locked record
18. **cr:MitigationPlan** → DEMOTE — RBQM mitigation strategy; a Constraint/plan, not a judgment requiring version history

### Operational Metrics & Monitoring
19. **cr:SiteMetrics** → DEMOTE — periodic KPI snapshot; operational monitoring (snapshot time is in DNA observedAt, not bitemporal)
20. **cr:MetricObservation** → DEMOTE — computed monitoring value; operational output (the metric value at a point in time is DNA-sufficient)
21. **cr:RiskSignal** → DEMOTE — leading indicator; operational signal (flagged antecedents are the promoted fact, signal itself is transient)

### Planning & Specifications (not locked records)
22. **cr:Endpoint** → DEMOTE — endpoint definition; protocol specification, not a locked record
23. **cr:ParticipantSchedule** → DEMOTE — schedule instance; operational planning
24. **cr:PlannedEncounter** → DEMOTE — protocol visit definition; specification
25. **cr:ScheduleTimeline** → DEMOTE — timeline instance; operational schedule
26. **cr:TimingWindow** → DEMOTE — visit timing window; protocol specification
27. **cr:TransferSpecification** → DEMOTE — DTA content spec (the PLAN); the executed DTA is what versions
28. **cr:TransferAmendment** → DEMOTE — DTA amendment event; operational change (the resulting DTA version is what matters)

### RBQM Living Documents (reviewed/updated, not locked)
29. **cr:RiskManagementPlan** → DEMOTE — living RBQM document, updated as circumstances change; not a locked judgment
30. **cr:RiskReview** → DEMOTE — periodic RBQM review cycle; operational review (the review outcome is a value, not a locked record)
31. **cr:DeviationAntecedent** → DEMOTE — latent operational condition; detected over time but doesn't need version chain
32. **cr:Phase3Design** → DEMOTE — EOP2 design proposal; planning document, not locked until protocol

### Entities That Should Not Be Versioned at All
33. **cr:StudySite** → DEMOTE — should not be Versioned at all (it's an Organization, not a time-based record)
34. **cr:StudySubject** → DEMOTE — should not be Versioned at all (it's an Agent/identity, not a time-based record; the Enrollment is what versions)
35. **hcls:Specimen** → DEMOTE — specimen identity/instance; the custody chain events are separate

### Operational Site Visit Events (Bo rulings, 27 Aug 2026)
36. **cr:SiteInitiationVisit** → DEMOTE — cr:SiteActivation is the Versioned green-light; the activation shape requires an SIV as evidence. The SIV is the operational visit, not the gate. (Bo)
37. **cr:CloseOutVisit** → DEMOTE — cr:SiteClosure is the Versioned gate (parallel to SiteActivation). The class comment in cr-core-site-closeout.ttl states CloseOutVisit is "the same shape as cr:SiteInitiationVisit." No distinction exists. Demote both visits or document a real distinction — both are operational. (Bo)
38. **cr:Reconciliation** → DEMOTE — the class is an act; reconciliationOutcome says a discrepancy is resolved by a later balanced reconciliation (a new event/computation, not a revision of the same act). SiteClosure stays Versioned. A signed reconciliation certificate, if needed later, is a Versioned attestation/report, not Versioning the activity. (Bo)

---

## AMBIGUOUS (0 classes)

All classes have been ruled KEEP or DEMOTE by domain-expert review (Bo, 27 Aug 2026).

---

## Summary
- **KEEP**: 46 classes (regulatory/locked documents, append-only judgments, GCP audit, IMP accountability, HCLS consent framework)
- **DEMOTE**: 38 classes (operational events, metrics, planning specs, operational site visits)
- **AMBIGUOUS**: 0 classes
- **Total audited**: 84 classes

## Implementation Notes
- Demoting a class: remove `top:Versioned` from its `rdfs:subClassOf` list in the ontology
- Update examples: demoted classes drop validFrom + prov:specializationOf → VersionSeries; keep DNA (identifier + observedAt + status)
- All classes ruled: implementation deferred to follow-on PR
