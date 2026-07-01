# Changelog — TOP Clinical Research Domain Ontology

All notable changes to this ontology package are documented here.

## Versioning Policy

- **MAJOR**: Breaking change — IRI renames, shape constraint tightening that invalidates previously conformant data, removal of classes/properties
- **MINOR**: Additive — new classes, properties, shapes, crosswalks, projections, examples that do not break existing valid data
- **PATCH**: Non-semantic — comment corrections, label fixes, example clarifications, documentation updates

Deprecation pattern: add `owl:deprecated true` and `rdfs:comment "Deprecated: use <replacement> instead."` for one MAJOR version before removal.

---

## [1.0.0] — 2026-07-01

### Summary

Initial production release of the TOP Clinical Research (CR) domain ontology, covering all 40 user stories across US-100 through US-900.

### Added

**US-100 — CR Core Classes**
- `cr:Study`, `cr:Site`, `cr:Subject`, `cr:Enrollment`, `cr:Protocol`, `cr:ProtocolVersion`
- `cr:EligibilityCriterion` with `cr:criterionText`, `cr:criterionType` (inclusion/exclusion)
- `cr:studyPhase`, `cr:sponsorName`, `cr:therapeuticArea`, `cr:protocolVersion` datatype properties

**US-200 — Safety & Pharmacovigilance**
- `cr:AdverseEvent`, `cr:SeriousAdverseEvent`, `cr:DoselimitingToxicity`
- `cr:SUSARReport` with `cr:sponsorAwarenessDate`, `cr:reportingDeadline`, `cr:submissionDate`
- SHACL shapes: AE severity, SAE seriousness criteria, SUSAR timeliness gate (15-day rule)
- CTCAE grade vocabulary (1–5)

**US-300 — GCP Compliance & Essential Records**
- `cr:Deviation`, `cr:CAPA`, `cr:CertifiedCopy`, `cr:TrialMasterFile`
- `cr:DelegationAct` with `cr:delegatesCapability`
- `cr:ConsentWithdrawal` with `cr:withdrawalReason` (controlled vocab)
- SHACL: deviation root-cause requirement, CAPA linkage, certified-copy chain

**US-400 — RBQM & Site Activation**
- `cr:RiskFactor`, `cr:MonitoringAllocation`, `cr:SiteActivation`
- `cr:SiteSelectionDecision` (institutional intelligence — WHY a site was or was not selected)
- Site status codelist: activated, pending, not-selected, RESERVE
- SHACL: RBQM SDV intensity in [0,1]; site activation timeline completeness

**US-500 — Scheduling & SoA**
- `cr:PlannedVisit`, `cr:RealizedVisit`, `cr:ScheduleOfActivities`
- Bitemporal time properties (`top:validFrom`, `top:validTo`, `top:recordedAt`, `top:correctedAt`)
- SHACL: planned-vs-actual window compliance

**US-600 — Privacy & GDPR**
- `cr:DataProcessingAgreement`, `cr:DataSubjectRequest`, `cr:LawfulBasis`
- SHACL: post-withdrawal observation gate, DPA completeness, EU GDPR lawful-basis requirement
- DSR type codelist: access, erasure, rectification, portability

**US-700 — Crosswalks & SSSOM**
- Crosswalk vocabulary (`cx:Mapping`, `cx:subjectId`, `cx:predicateId`, etc.)
- `crosswalks/cr-to-external.ttl` — CR core → OAE, NCIt, SNOMED CT, RxNorm, LOINC
- `crosswalks/cr-to-meddra.ttl` — AE hierarchy: LLT / PT / SOC (BYOL)
- SHACL shape `cx:MappingShape` enforcing full SSSOM provenance on every mapping
- SPARQL projection `sssom_export.rq` — TSV-ready SSSOM export

**US-800 — AI Inference & Provenance**
- `top:promptTemplate`, `top:sourceContext`, `top:modelVersion` on `top:Conclusion`
- `cx:inferredBy`, `cx:confirmedBy`, `cx:mappingMethod` on `cx:Mapping`
- SHACL HITL gate: Violation if `cx:inferredBy` present without `cx:confirmedBy`
- SHACL Warning: `cx:mappingMethod` must be `"LLMInference"` for LLM-produced mappings
- Violation example: `examples/crosswalk-mapping-llm-unconfirmed-violation.ttl`
- GraphRAG recipe: `examples/graphrag/eligibility-rag-recipe.md`

**US-900 — Test Harnesses & Distribution**
- `tests/run_shacl.py` — SHACL conformance harness (reads `manifest.json`, uses pyshacl)
- `tests/run_projections.py` — SPARQL projection harness (reads `projections/expectations.json`)
- `tests/validate_transformer_output.py` — validates USDM ingestion output against shapes
- `tests/manifest.json` — 66-entry test manifest for all example files
- `projections/expectations.json` — 19-entry projection expectation registry
- `docs/dist/` — 10 distribution artifacts:
  - `top-cr-ontology-v1.ttl` / `.jsonld` / `.nt` (3 371 triples)
  - `top-cr-shapes-v1.ttl` / `.jsonld` / `.nt` (~959 triples)
  - `top-cr-crosswalks-v1.ttl` / `.jsonld` / `.nt` (~610 triples)
  - `ngsi-context.jsonld` (370 NGSI-LD terms)
  - `SHA256SUMS`

### Distribution Artifacts

Built by `docs/build_dist.py`. Canonical context URL:
`https://top.scientix.ai/cr/v1.ngsi-context.jsonld`

### Dependencies

- pyshacl >= 0.31.0
- rdflib >= 7.6.0
- MedDRA licence required for `cr-to-meddra.ttl` (BYOL — see registry.md §5)
