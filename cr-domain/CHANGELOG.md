# Changelog

All notable changes to the TOP Clinical Research (CR) domain ontology follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versioning Policy

| Version component | Trigger |
|---|---|
| **MAJOR** | Breaking change to an existing IRI, class removal, property removal, range/domain narrowing, SHACL severity escalation |
| **MINOR** | New additive class, property, SHACL shape, crosswalk, or projection that is backward-compatible |
| **PATCH** | `rdfs:comment`/`rdfs:label` corrections, documentation edits, example file updates |

### Deprecation pattern

```turtle
cr:oldProperty a owl:DatatypeProperty ;
    owl:deprecated true ;
    rdfs:comment "Deprecated in v1.2: use cr:newProperty instead." .
```

Deprecated terms remain in the dist bundle for two MINOR versions before removal (MAJOR bump).

---

## [Unreleased]

### Changed — Trial phase vs. lifecycle stage disambiguation (convener sanity review)

- **`cr-core-phases.ttl` rewritten**: the old file conflated two concepts under
  one word. Now split: **Trial Phase** (`cr:TrialPhase` + `cr:trialPhase` on
  `cr:Study`; individuals `cr:Phase1`–`cr:Phase4` and `cr:BESH`, each with
  purpose/size/site comments and device-world altLabels — feasibility/pilot,
  pivotal, post-market surveillance) classifies the study itself; **Lifecycle
  Stage** (startup/conduct/closeout) is the position in the trial's execution.
  Veterinary phases 1–3 noted as out of scope (separate domain).
- **`hcls:Phase` → `hcls:LifecycleStage`** (deprecated equivalent-class alias
  kept per policy); `hcls:contains`/`hcls:precedes`/`hcls:occursIn`
  domains/ranges and comments now speak stage language.
- **Stage individuals renamed** (`*Phase`/`*SubPhase` → `*Stage`):
  `cr:StartupStage` (contains `cr:StudyDesignStage`, `cr:SiteSelectionStage`,
  `cr:SiteRegulatoryStage`, `cr:SiteActivationStage`), `cr:ConductStage`
  (Recruitment/VisitExecution/DataCollection/Safety/Oversight stages),
  `cr:CloseoutStage` (FollowUp/DataAnalysis/Reporting/Archival stages).
  All 78 action-catalog `hcls:occursIn` references updated.
- **Watch-list**: `cr:xl-phase` added to the ambiguous-terms watch-list with
  trial-phase vs. lifecycle-stage routing; roles docs page retitled
  "Roles, stages &amp; actions".

### Changed — Convener sanity-review fixes, round 2 (P6 booleans + ambiguity)

- **Boolean census + P6 promotions** (only 3 booleans existed repo-wide, all
  claims-in-disguise): `cr:susarUnexpected` → `cr:ExpectednessAssessment`
  (a judgment against the reference safety information, with
  `cr:expectednessVerdict` + `cr:assessedAgainstRSI` — the CausalityAssessment
  pattern); `cr:mandatoryElement` → `cr:requirementLevel`
  ('required'|'expected'|'permissible', SDTM core-designation discipline);
  `cr:derivedFlag` → `cr:elementOrigin` ('collected'|'derived', Define-XML
  origin discipline). All three old properties deprecated per policy.
- **LIMS ambiguity renames** (collision-prone names → operator vocabulary):
  `cr:AnalysisRequest` → `cr:LabOrder`; `cr:AnalysisService` →
  `cr:AssayDefinition`; `cr:fromService` → `cr:resultOfAssay`;
  `cr:requestsService` → `cr:ordersAssay`; `cr:onSample` → `cr:onSpecimen`.
  'Analysis request' collides with every non-lab sense (a manager requesting a
  site-performance analysis is not a lab order); 'service' collides with
  cr:ServiceProvider and API senses. Deprecated class aliases kept
  (`owl:equivalentClass`); all shapes/examples/projections/crosswalks updated;
  bare LIMS properties (specimen, collectedAt, ...) gained labels + comments.
- **`cr:CSR` deprecated** — unused duplicate of `cr:ClinicalStudyReport`.
- **Watch-list grows**: 'analysis' and 'service' join the ADR-0024
  ambiguous-terms watch-list with context-routing notes.

### Changed — Convener sanity-review fixes, round 1 (first-principles P2)

- **25 Jobs-to-Be-Done renamed** from jargon-coded IRIs (`cr:PI-J01`,
  `cr:COORD-J03`, ...) to operator-vocabulary names
  (`cr:OverseeStudyConductAtSite`, `cr:CaptureDataAndResolveQueries`, ...).
  The OOUX map coordinate is preserved as `skos:notation` — provenance, not
  identity. P2's own rule: nobody says "PI-J01" aloud.
- **`tools/naming_check.py` extended to named individuals** — jargon-coded
  instance IRIs are now mechanically impossible, with a principled exception
  for regulatory citations (`ICH_E6_R3`, `CFR_21_Part_11`), where the
  citation IS the operator name.
- **Success-signal jargon removed**: "Form 1572 (US studies)" restated
  jurisdiction-neutrally; system-field prose ("electronicSignatureStatus =
  SIGNED", "Person.delegatedBy") restated in operator language.
- **`cr-core-ai.ttl` promoted to Core** (`core/v1/modules/top-ai.ttl`): the
  LLM-provenance properties (`top:promptTemplate`/`sourceContext`/
  `modelVersion`) are domain-agnostic — the AI face of P4 — now with a PII
  scope note; the `cx:` HITL-gate properties moved to `crosswalk-vocab.ttl`
  (IRIs unchanged). Core dist rebuilt; upstream pin updated deliberately.
- **Blinding error corrected in the action catalog**:
  `cr:AssignParticipantsToArm` (authorized: Site Coordinator — impossible in
  a blinded study) is now `cr:RequestRandomization`; the assignment itself is
  the randomization system's act (`cr:RandomizationEvent`).

### Added — Seven in-scope sub-domains (the deferral register, shipped)

Every entry from the BOUNDARIES.md "Deferred within scope" register that was
in reach for v1, shipped the standard way: module + graded shapes + conformant
and violation examples + gated tests + a docs page at the operator-screen bar
+ thesaurus dialects. All classifications ride as values, never subclasses
(ADR-0024 one-question gate).

- **`cr-core-recruitment.ttl` + `shapes/recruitment.ttl`** — the funnel
  (Operating Model §2.2–2.3): campaign → `cr:Recruit` (site-boundary, PII-side)
  → pre-screening → `cr:ScreeningRecord` (outcome as value; screen-failure must
  cite the failed criterion by IRI) → conversion gated on 'eligible'
  (Violation). Retires the legacy undefined `cr:Recruit`/`cr:ScreeningRecord`.
- **`cr-core-randomization.ttl` + `shapes/randomization.ttl`** — IxRS/RTSM
  events as facts: `cr:RandomizationEvent`, blinded `cr:KitAssignment`,
  audited `cr:UnblindingEvent` (reason + authorizer required — the
  DatabaseUnlock discipline applied to the blind).
- **`cr-core-supply.ttl` + `shapes/supply.ttl` +
  `projections/accountability_log.rq`** — IMP custody events on `hcls:Lot`
  (ship/dispense/return/destroy) with the drug log as a projection;
  `cr:TemperatureExcursion` quarantine (dispensing from a quarantined lot =
  Violation; unauthorized destruction = Violation).
- **`cr-core-coding.ttl` + `shapes/coding.ttl`** — the coding workflow:
  `cr:CodeAssignment` as a promoted judgment (verbatim, BYOL dictionary IRI,
  version required, method as value) + `cr:CodingReview`; unreviewed autocode
  = Warning. WHODrug BYOL reference properties join the MedDRA set.
- **`cr-core-adam.ttl` v1.1** — ADaM structure classes (ADSL/BDS/OCCDS) as
  controlled values, `cr:AnalysisVariable` (PARAMCD), structure-enum shape.
- **`cr-core-disclosure.ttl` + `shapes/disclosure.ttl`** — `cr:IntegratedSummary`
  (ISS/ISE kind as value; ≥1 `cr:integratesStudy`; must derive from the
  per-study datasets), `cr:RegistryRecord` (NCT; posted results must cite
  results by IRI), `cr:Publication` (+`cr:disclosesResult`), and the
  `cr:includesSummary` eCTD manifest edge.
- **`cr-core-site-closeout.ttl` + `shapes/site-closeout.ttl`** — COV,
  `cr:Reconciliation` (one class, four scope values), `cr:InvestigatorSiteFile`,
  archival with retention clock, and `cr:SiteClosure` that must rest on the
  COV + balanced reconciliations (closed by evidence, not declaration).
- **Docs**: five new flow pages at the full bar (claim, train-stops, operator
  screen + API tabs over real single-pull views, entities, validates tables);
  ISS/disclosure folded into the submission page, ADaM structure into EOP2.
- **Suite**: SHACL 79→91, projections 23→24, single-pull views 17→22.

### Added — Operator thesaurus & vocabulary discipline (ADR-0024)

The Pipeline layer-1/layer-4 build: operator dialects through the pipeline.

- **`ontology/cr-thesaurus.ttl`** — the dialect layer: `skos:prefLabel`/`altLabel`/
  `hiddenLabel` for ~60 concepts (acronyms, spelling variants, workplace shorthand;
  standards jargon and lay terms routed as hidden labels, never promoted), with
  SKOS-XL reified labels carrying `dct:source` where provenance is load-bearing.
  Seeded from the Clinical Trial Operating Model practitioner document (2026-07).
- **`cr:AmbiguousTermsWatchList`** — the ADR-0024 gate: six high-ambiguity terms
  (agent, subject, monitor, arm, site, screen), each with an anti-synonym /
  context-routing scope note; new labels matching a member require one.
- **"Participant" is the preferred label** for `cr:StudySubject` (ADR-0024;
  first-principles P2). IRI unchanged; "patient" routed, not promoted; the PII
  boundary held by homonym routing (`hcls:Person` scope note).
- **ADR-0024 known deviations recorded in-file**: `cr:SeriousAdverseEvent`,
  `cr:DoseLimitingToxicity`, `cr:SUSAR` are classifications-as-subclasses,
  slated for a promote-to-fact refactor in a dedicated safety-module pass.
- **`conventions.md`** — vocabulary conventions (cover dialects generously; route
  borrowed registers; gate only the watch-list; provenance where it matters) +
  the one-question class-creation gate + BFO-carried-at-Core policy.
- **Harness `vocab` gate (4 checks)** — labels attach only to defined terms;
  prefLabel unique per concept and unshared; watch-list members carry routing
  notes; no `bfo:` IRIs leak into domain modules.
- **Docs** — glossary gains an "also known as" column rendered live from the
  thesaurus.

### Changed — V1 hardening: Core↔CR seam, coherence gates, docs parity

Consistency and interface work toward a credible v1 (ADR-0023). No breaking IRI
changes; all additive or corrective.

- **`ontology/top-core.ttl`** — the local TOP Core stub the README always
  described now exists: `top:CommonEntity` root + 8 CLOs + Universal DNA + the
  cr-conventions bitemporal envelope, with divergences from `core/v1` documented
  in-file. Closes every dangling `top:` reference in the merged graph.
- **`ontology/cr-core-participant.ttl`** — reduced to a property-only module;
  the duplicate class definitions (`cr:InformedConsent`, `cr:StudySubject`,
  `cr:Enrollment`, `cr:EligibilityCriterion`) that diverged from `cr-core.ttl`
  (and subclassed the undefined `top:BitemporalEntity`) are removed. Single
  authoritative definition per class.
- **`ontology/cr-core-visit-execution.ttl`** — removed the duplicate
  `cr:ClinicalObservation` (authoritative in `cr-core-edc.ttl`); `cr:forParticipant`
  now ranges over `cr:StudySubject` (the retired `cr:Participant` is gone).
- **`shapes/universal-dna.ttl`** — renamed the domain shape to
  `cr:UniversalDNAShape` so it no longer collides with `core/v1`'s
  `top:UniversalDNAShape` (which targets a different class with a different contract).
- **`core/v1/build_core_dist.py` + `cr-domain/upstream-pin.json`** — TOP Core is
  now a versioned, byte-reproducible, checksummed artifact, and the CR domain
  pins it. New harness **seam** gate verifies the pin + stub↔Core alignment.
- **`tests/run_tests.py`** — new **coherence** gate (no duplicate class defs, no
  dangling `top:/cr:/hcls:` refs, unique ontology-IRI headers) and **seam** gate;
  single-pull **view** guard grown 13→17 (preind, csr, dblock, submission).
- **Docs** — `preind`/`csr`/`dblock`/`submission` brought to the operator-screen
  + API-tab bar with real retrieval views; `@context` IRI unified to
  `https://top.scientix.ai/cr/v1/ngsi-context.jsonld`; entity URNs unified to the
  ETSI `urn:ngsi-ld:top-cr:` convention; broken RDF/XML download removed; scenario
  pages get model-table parity; orphan `participant.html`/`visit.html` deleted;
  hub gains a "reference graph, not a runtime" frame (Providence Neural Engine
  pointer for the operational path).
- **`BOUNDARIES.md`** — device modeling reframed as decided-but-not-yet-built
  (v1 status), plus a new "Deferred within scope" register (randomization/IxRS,
  drug supply/IMP accountability, medical coding/WHODrug, eCOA/imaging/DHT
  domains, query reconciliation, DCT, RWE) so in-scope omissions read as
  decisions, not gaps.

### Added — DTA / DTS reference-ontology extension (non-CRF vendor data transfer)

An additive, governed extension for Data Transfer Agreements / Specifications.
Nothing in Core or existing CR classes changes. Grounded in the CDISC DDF5a DTA
working-group corpus; models the transfer as a fact graph rather than a document.

- **`ontology/dta-module.ttl`** — new leaves, each subclassing a Core leaf:
  `cr:DataTransferAgreement`, `cr:TransferSpecification`,
  `cr:DataElementSpecification`, `cr:TransferProfile`,
  `cr:VendorConnectorProfile`, `cr:BiomedicalConcept`, `cr:VendorAlias`,
  `cr:BlindingConstraint`, `cr:TransferScope`, `cr:TransferAmendment`,
  `cr:TransferFile`; transfer-lifecycle bitemporal properties; `cr:resolvedFrom`
  binding provenance; `cr:backedByCredential` authorization edge.
- **`shapes/dta-content.ttl`, `dta-resolution.ttl`, `dta-profile.ttl`,
  `dta-agreement.ttl`** — the "Data Validation & Quality" layer the DTA MVP
  deferred, as executable SHACL graded Violation / Warning / Info (concept-bound
  + UCUM unit, alias resolved-or-attested, CT-enforced operational attrs,
  credential-backed signatory gate, explicit amendment propagation).
- **`crosswalks/dta-to-external.ttl`** — LOINC 2951-2, QUDT/UCUM `mmol/L`, and
  SDTM LB variable mappings; gate-validated (`shapes/crosswalk.ttl`).
- **`crosswalks/dta-encounter-alias.sssom.tsv`** — the compounding vendor-visit
  alias corpus (resolve once, next sponsor auto-resolves).
- **`projections/dta_sdtm_lb.rq`, `dta_document.rq`** — SDTM LB row and the
  human-readable DTA document, rendered from the graph (never authored).
- **`examples/dta-lab-safety/`** — the Sodium worked example (conformant),
  its deliberately-broken counterpart, a graded-warning fixture, and a
  vendor-connector catalog (Castor, Veeva, Medidata, Oracle Clinical One).
- **`docs/dta-design-notes.md`** — answers to the six open modeling questions,
  the vendor-API research grounding, and honest T1/T2 tiering.
- **`examples/dta-lab-safety/fhir-lab-connectors.ttl`** — the corrected vendor
  tier for the central-lab safety-lab MVP: FHIR R4 megalabs (Labcorp, Quest),
  QHIN/aggregators (Health Gorilla, Redox, Particle), and developer-first EHRs
  (Canvas, Medplum, Akute, Elation), grounded in the CDISC 360i lab-API analysis.
- FHIR R4 lab request-report triad → SDTM LB crosswalk rows (`Observation` →
  `LBSTRESN`/`LBLOINC`, `Specimen` → `LBSPEC`, `ServiceRequest`); `FHIR-API` and
  `Webhook` added to the `cr:transmissionMethod` controlled terminology.

### Fixed

- Repaired the test harness (`tests/run_tests.py`) and unified the TOP Core
  namespace (`https://top.scientix.ai/v1#`) across examples, projections, and
  tools, which had drifted to a parallel `/core/v1#` namespace and split the
  shapes from the example vocabulary. Full suite green.

---

## [v1.0.0] — 2025-11-15

### Overview

First stable release of the TOP Clinical Research domain ontology.
Covers 39 user stories across 9 epics, building on the TOP Core
foundational classes (`top:Evidence`, `top:Constraint`, `top:Outcome`,
`top:Temporal`, `top:Versioned`, `top:Conclusion`, `top:Scope`).

### Added

#### Ontology files (`cr-domain/ontology/`)

- **cr-core.ttl** — core CR classes and properties: `cr:Study`, `cr:Arm`,
  `cr:Participant`, `cr:Endpoint`, `cr:Assessment`, `cr:SiteMetrics`,
  `cr:StudySite`, `cr:ProtocolVersion`, `cr:Protocol`, and ~80 properties
- **cr-core-participant.ttl** — participant lifecycle state machine, informed
  consent sub-object pattern, screening/randomization/withdrawal records
- **cr-core-eop2.ttl** — EOP2/regulatory meeting model: `cr:RegulatoryInteraction`,
  `cr:StatisticalAnalysisPlan`, `cr:Estimand`, `cr:DataCut`,
  `cr:AnalysisPopulation`, `cr:Phase3Design`
- **cr-core-safety.ttl** — safety model: `cr:AdverseEvent`, `cr:SeriousAdverseEvent`,
  `cr:SUSAR`, `cr:SafetyReport`, `cr:CausalityAssessment`; MedDRA + CTCAE
  terminology anchors (BYOL)
- **cr-core-privacy.ttl** — GDPR compliance model: `cr:ConsentWithdrawal`,
  `cr:LawfulBasis`, `cr:DataProcessingAgreement`, `cr:RetentionPolicy`,
  `cr:DataSubjectRequest`
- **cr-core-ai.ttl** — AI inference provenance: `top:promptTemplate`,
  `top:sourceContext`, `top:modelVersion` on `top:Conclusion`;
  `cx:inferredBy`, `cx:confirmedBy`, `cx:mappingMethod` on `cx:Mapping`

#### SHACL shapes (`cr-domain/shapes/`)

42+ invariants across: assessment, crosswalk (SSSOM + HITL gate),
deviation/CAPA, EDC, EOP2/SAP/estimand, GCP records, LIMS, participant
lifecycle, privacy/GDPR, RBQM, safety (MedDRA/CTCAE/SUSAR/causality),
schedule, site activation/start-up, site metrics, TMF, visit execution.

#### Crosswalks (`cr-domain/crosswalks/`)

- **usdm-to-cr.ttl** — USDM v4 ↔ CR-core (14 verified mappings)
- **cr-to-external.ttl** — OAE/OBI/STATO/NCIT/Biolink mappings
- **cr-to-fhir.ttl** — FHIR R4 mappings (7 verified, skos:exactMatch)
- **cr-to-meddra.ttl** — MedDRA IRI-pattern mappings (BYOL, 5 anchors)
- **cr-to-sdtm.ttl** — CDISC SDTM domain/variable mappings (8 mappings)

#### Projections (`cr-domain/projections/`)

21 SPARQL projection queries covering: deviation lineage, TMF binding,
SDTM DM/AE/EX, USDM study, FHIR ResearchSubject, DOA log, ADaM
traceability, SSSOM export, data mart, specimen lineage, RBQM monitoring,
site activation, SoA table, planned-vs-actual, start-up package,
safety AE by SOC, SUSAR dashboard, DLT by cohort, enrollment as of cut,
analysis population membership, GDPR data map, overdue DSAR.

#### Examples (`cr-domain/examples/`)

66 Turtle example files demonstrating conformant data, violations, and
warnings across all major epics. Plus FHIR JSON fixture and NGSI-LD
transformer (`examples/fhir/`), GraphRAG recipe
(`examples/graphrag/eligibility-rag-recipe.md`).

#### Tests (`cr-domain/tests/`)

- `run_shacl.py` — pyshacl harness for all 66 examples
- `run_projections.py` — rdflib harness for all 21 projections
- `manifest.json` — expected outcomes for SHACL harness

#### Dist artifacts (`cr-domain/docs/dist/`)

Built from `build_dist.py`:

| Artifact | Contents |
|---|---|
| `top-cr-v1.ttl` | 3374 ontology triples |
| `top-cr-shapes-v1.ttl` | 920 SHACL shape triples |
| `top-cr-crosswalks-v1.ttl` | 522 crosswalk triples |
| `top-cr-v1.ngsi-context.jsonld` | 376 NGSI-LD domain terms |
| `SHA256SUMS` | SHA-256 pins for all 10 artifacts |

Each artifact also available as `.jsonld` and `.nt`.
