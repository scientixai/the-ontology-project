# TOP Clinical Research — Product Backlog

*Generated July 2026. Covers current, refactor, and net-new work across the TOP CR domain.*

## Legend

**Type:** `current` (built, tracking baseline) | `refactor` (exists, needs improvement) | `net-new` (not yet built)  
**Tier:** `ontology` | `shapes` | `sparql` | `crosswalk` | `transformer` | `docs`  
**Status:** `done` | `in-progress` | `todo`

---

## Epic CORE-100: TOP Core OWL Completeness

*Formal correctness of the TOP Core foundation layer — disjointness, identity patterns, naming, extensibility enforcement.*

---

### US-100-001: Disjoint L2 categories

**type:** net-new | **tier:** ontology + shapes | **status:** todo

> As an ontology consumer, I want the eight L2 categories declared mutually disjoint so that an OWL reasoner can detect class membership violations and a SHACL validator can enforce instance-level separation.

#### Tasks
- T-100-001-001: Add `owl:disjointWith` axioms between all pairs of the eight L2 categories in `top-root.ttl`
- T-100-001-002: Add a SHACL `sh:not / sh:class` constraint for each L2 pair in a new `core/v1/shapes/top-disjoint.ttl`
- T-100-001-003: Write one conformant and one violation example per category pair (spot-check 3 pairs)
- T-100-001-004: Run pyshacl against examples; confirm violations fire
- T-100-001-005: Update `foundation.html` narrative to explain the disjointness axioms and their role in closed-world validation

#### Success Criteria
- [x] Every pair of L2 categories has an explicit `owl:disjointWith` triple in the OWL graph
- [x] An entity typed as both `top:Agent` and `top:Resource` produces a SHACL violation
- [x] pyshacl confirms violation on the cross-typed example; conformant examples remain clean
- [x] Build pipeline (`build_dist.py`) produces updated N-Triples with disjointness triples included

---

### US-100-002: VersionSeries as stable identity root

**type:** net-new | **tier:** ontology + shapes | **status:** todo

> As a knowledge engineer, I want a `top:VersionSeries` class that acts as the stable identity root for `top:Versioned` nodes so that the `prov:specializationOf` pattern is computable and the identity root is explicitly typed.

#### Tasks
- T-100-002-001: Add `top:VersionSeries` class to `top-bitemporal.ttl` with `rdfs:comment` explaining it as the stable identity root
- T-100-002-002: Pin `prov:specializationOf` range to `top:VersionSeries` via `rdfs:range`
- T-100-002-003: Update the `top:BitemporalShape` to require `prov:specializationOf` on every `top:Versioned` instance
- T-100-002-004: Update existing walkthroughs (`consent-bitemporal.ttl`) to include a `top:VersionSeries` node
- T-100-002-005: Update `rdfs:comment` on `top:Versioned` to reference `top:VersionSeries`
- T-100-002-006: Update `foundation.html` bitemporal section to explain `top:VersionSeries` as the stable identity root; include a diagram or code block showing the versioned node pattern

#### Success Criteria
- [x] `top:VersionSeries` exists with correct superclass, label, and comment
- [x] `prov:specializationOf` range is declared as `top:VersionSeries` in the OWL graph
- [x] `top:BitemporalShape` produces a violation when `prov:specializationOf` is absent or points to a non-`top:VersionSeries` node
- [x] Walkthrough examples validate cleanly under the updated shape

---

### US-100-003: Self-declaring module files

**type:** refactor | **tier:** ontology | **status:** todo

> As a tooling integrator, I want each `top-*.ttl` module file to carry its own minimal `owl:Ontology` declaration so that a tool loading a single module gets a parseable ontology with the correct IRI.

#### Tasks
- T-100-003-001: Add a minimal `owl:Ontology` triple to each of the 10 module files (IRI pattern: `<https://top.scientix.ai/core/v1/modules/top-{name}>`)
- T-100-003-002: Add `owl:imports <https://top.scientix.ai/core/v1/modules/top-root>` to each non-root module
- T-100-003-003: Verify `shapes.ttl` aggregator still resolves correctly after module ontology declarations are added
- T-100-003-004: Add a build check that asserts each module file contains exactly one `owl:Ontology` triple
- T-100-003-005: Update `foundation.html` module-split section to reference the self-declaring module IRI pattern and how tools can load individual modules

#### Success Criteria
- [x] Loading any single `top-*.ttl` file in rdflib returns at least one `owl:Ontology` triple
- [x] The aggregator `shapes.ttl` produces the same merged graph as before (N-Triples line count unchanged)
- [x] Build check passes in CI

---

### US-100-004: Flavor enforcement via SKOS and SHACL

**type:** net-new | **tier:** ontology + shapes | **status:** todo

> As an ontology extender, I want `top:flavor` constrained to a SKOS concept scheme so that invalid flavor values are caught at build time rather than silently accepted.

#### Tasks
- T-100-004-001: Create a `top:FlavorScheme` SKOS concept scheme in `top-root.ttl` with three `skos:Concept` individuals: `top:FlavorInvariant`, `top:FlavorTightenable`, `top:FlavorAdditive`
- T-100-004-002: Add `skos:prefLabel` and `skos:definition` to each flavor concept
- T-100-004-003: Add a SHACL `sh:in` constraint on `top:flavor` to the existing `top:UniversalDNAShape` or a new shape
- T-100-004-004: Update all existing `top:flavor` literal values to use the concept IRIs (not strings)
- T-100-004-005: Update `foundation.html` extensibility section to document the three flavor values with their definitions and a downstream ontology example

#### Success Criteria
- [x] `top:flavor` accepts only `top:FlavorInvariant`, `top:FlavorTightenable`, or `top:FlavorAdditive`
- [x] A resource with `top:flavor "Mutable"` produces a SHACL violation
- [x] All existing usages of `top:flavor` in the modules use the concept IRI form
- [x] `top:FlavorScheme` is included in the dist bundle

---

### US-100-005: Reclassify top:Organism

**type:** refactor | **tier:** ontology | **status:** todo

> As an ontology expert, I want `top:Organism` removed from `prov:Agent` and aligned to `bfo:MaterialEntity` so that the class does not imply causal responsibility, which is semantically incorrect for laboratory animals.

#### Tasks
- T-100-005-001: Remove `prov:Agent` from the superclass chain of `top:Organism` in `top-agent.ttl`
- T-100-005-002: Add `bfo:MaterialEntity` as superclass (light-edge, consistent with ADR-0013)
- T-100-005-003: Add a new `top:subjectOf` object property (domain `top:Organism`, range `top:Scope`) for experimental subject relationships
- T-100-005-004: Update `rdfs:comment` on `top:Organism` to explain the BFO alignment
- T-100-005-005: Check that no existing examples or CR domain files depend on `top:Organism rdfs:subClassOf prov:Agent`
- T-100-005-006: Update `foundation.html` agent taxonomy section to reflect the reclassification and note the BFO alignment rationale

#### Success Criteria
- [x] `top:Organism` no longer has `prov:Agent` in its superclass chain
- [x] `bfo:MaterialEntity` is declared as superclass
- [x] `top:subjectOf` exists with correct domain/range
- [x] No existing SHACL shapes or examples break as a result of the change
- [x] `rdfs:comment` updated to explain the BFO alignment rationale

---

## Epic CRVOCAB-200: CR Domain Vocabulary Completeness

*Properties missing from existing classes: Assessment, Arm, Endpoint, RegulatoryInteraction, site operations.*

---

### US-200-001: Assessment properties

**type:** net-new | **tier:** ontology + shapes | **status:** todo

> As an oncologist and as a CDM, I want `cr:Assessment` to carry coded assessment type, method, and result so that clinical acts are queryable by what was done, not just that something happened.

#### Tasks
- T-200-001-001: Add `cr:assessmentCode` (ObjectProperty, range `skos:Concept` — SNOMED CT or LOINC IRI)
- T-200-001-002: Add `cr:assessmentMethod` (DatatypeProperty, xsd:string or coded)
- T-200-001-003: Add `cr:assessmentResult` (ObjectProperty, range `hcls:Observation`)
- T-200-001-004: Add `cr:assessmentScale` (ObjectProperty — for CTCAE, RECIST, ECOG, etc.)
- T-200-001-005: Add a `cr:AssessmentShape` SHACL shape requiring `assessmentCode` and `performedBy`
- T-200-001-006: Write a conformant assessment example and a violation example (missing code)
- T-200-001-007: Rebuild docs; verify `cr:Assessment` properties appear in `reference.html`; add assessment property table to `visit.html` clinical act section

#### Success Criteria
- [x] `cr:Assessment` has at minimum `assessmentCode`, `performedBy`, and `assessmentResult` as declared properties
- [x] `cr:AssessmentShape` enforces presence of `assessmentCode` and `performedBy`
- [x] A SPARQL query `SELECT ?a ?code WHERE { ?a a cr:Assessment ; cr:assessmentCode ?code }` returns results against the conformant example
- [x] Conformant and violation examples validate correctly under pyshacl

---

### US-200-002: Arm enrichment

**type:** net-new | **tier:** ontology | **status:** todo

> As a biostatistician, I want `cr:Arm` to carry randomization ratio, stratification factors, and planned enrollment count so that power calculations and analysis population definitions have their structural inputs in the graph.

#### Tasks
- T-200-002-001: Add `cr:randomizationRatio` (DatatypeProperty, xsd:string — e.g., "2:1")
- T-200-002-002: Add `cr:stratificationFactor` (ObjectProperty, range `cr:EligibilityCriterion` or xsd:string)
- T-200-002-003: Add `cr:plannedEnrollment` (DatatypeProperty, xsd:integer)
- T-200-002-004: Add `cr:actualEnrollment` (DatatypeProperty, xsd:integer) — for plan-vs-actual
- T-200-002-005: Update the `usdm-to-cr.ttl` arm mapping to note these additional properties
- T-200-002-006: Update LY900018 transformer to extract randomization ratio if present in USDM
- T-200-002-007: Rebuild docs; verify `cr:Arm` enriched properties appear in `reference.html`; add arm design table to `setup.html` study design section

#### Success Criteria
- [x] `cr:Arm` has `randomizationRatio`, `plannedEnrollment`, `actualEnrollment` as declared datatype properties
- [x] `cr:stratificationFactor` is declared as an object property
- [x] USDM-to-CR crosswalk comment updated noting arm property coverage
- [x] At least one example Arm entity in the transformer output includes `plannedEnrollment`

---

### US-200-003: Endpoint enrichment

**type:** net-new | **tier:** ontology | **status:** todo

> As a biostatistician and as a regulatory affairs specialist, I want `cr:Endpoint` to carry type (primary/secondary/exploratory), analysis method, and timepoint so that the protocol's statistical intent is computable.

#### Tasks
- T-200-003-001: Add `cr:endpointType` (DatatypeProperty — coded: primary/key-secondary/secondary/exploratory)
- T-200-003-002: Add `cr:analysisMethod` (DatatypeProperty, xsd:string or STATO IRI)
- T-200-003-003: Add `cr:endpointTimepoint` (ObjectProperty, range `cr:Visit` or xsd:duration)
- T-200-003-004: Add `cr:endpointEstimand` (ObjectProperty, range `cr:Estimand`) — links endpoint to its estimand
- T-200-003-005: Add `cr:endpointType` to the `eop2.ttl` SHACL shape for EndpointResult
- T-200-003-006: Rebuild docs; verify `cr:Endpoint` properties appear in `reference.html`; update `eop2.html` endpoint table to show type and estimand link

#### Success Criteria
- [x] `cr:Endpoint` has `endpointType`, `analysisMethod`, `endpointTimepoint`, `endpointEstimand` as declared properties
- [x] `cr:endpointType` value constrains to the four coded types (SHACL `sh:in`)
- [x] `cr:endpointEstimand` is used in the conformant `eop2-conformant.ttl` example
- [x] SPARQL query for "primary endpoints in this study with their estimands" runs successfully

---

### US-200-004: RegulatoryInteraction enrichment

**type:** net-new | **tier:** ontology + shapes | **status:** todo

> As a regulatory affairs specialist and as a CRO PM, I want `cr:RegulatoryInteraction` to carry meeting type, agency IRI, meeting date, and outcome so that regulatory touchpoints are queryable first-class events.

#### Tasks
- T-200-004-001: Add `cr:meetingAgency` (ObjectProperty, range `top:RegulatoryLaw` or agency IRI)
- T-200-004-002: Add `cr:meetingDate` (DatatypeProperty, xsd:date)
- T-200-004-003: Add `cr:meetingOutcome` (DatatypeProperty, xsd:string)
- T-200-004-004: Confirm `cr:meetingType` already declared in `cr-core-eop2.ttl`; add coded values
- T-200-004-005: Add a SHACL shape requiring `meetingDate` and `meetingType` on every `cr:RegulatoryInteraction`
- T-200-004-006: Update `preind-conformant.ttl` and `eop2-conformant.ttl` examples to use the new properties
- T-200-004-007: Rebuild docs; verify properties appear in `reference.html`; update `preind.html` and `eop2.html` to show meeting properties in the regulatory interaction sections

#### Success Criteria
- [x] `cr:RegulatoryInteraction` has `meetingAgency`, `meetingDate`, `meetingType`, `meetingOutcome` as declared properties
- [x] SHACL shape fires violation when `meetingDate` is absent
- [x] Both Pre-IND and EOP2 conformant examples include the new properties
- [x] "List all regulatory meetings for this study, by date and type" SPARQL query returns results

---

### US-200-005: Site performance metrics

**type:** net-new | **tier:** ontology + shapes | **status:** todo

> As a CRO PM and as a sponsor CMO, I want `cr:SiteMetrics` as a periodic snapshot entity so that site KPIs are queryable time-series data rather than values in a spreadsheet.

#### Tasks
- T-200-005-001: Create `cr:SiteMetrics` class, `rdfs:subClassOf top:Evidence, top:Versioned`
- T-200-005-002: Add `cr:screenFailureRate` (DatatypeProperty, xsd:decimal)
- T-200-005-003: Add `cr:enrollmentRate` (DatatypeProperty, xsd:decimal — subjects per month)
- T-200-005-004: Add `cr:dataQueryRate` (DatatypeProperty, xsd:decimal)
- T-200-005-005: Add `cr:daysToQueryResolution` (DatatypeProperty, xsd:decimal)
- T-200-005-006: Add `cr:protocolDeviationRate` (DatatypeProperty, xsd:decimal)
- T-200-005-007: Add `cr:metricsForSite` (ObjectProperty, domain `cr:SiteMetrics`, range `cr:StudySite`)
- T-200-005-008: Add a SHACL shape requiring `metricsForSite`, `top:observedAt` (snapshot date), and at least one metric
- T-200-005-009: Write a site-metrics conformant example
- T-200-005-010: Add a SPARQL projection `site_kpi_timeseries.rq`
- T-200-005-011: Rebuild docs; verify `cr:SiteMetrics` appears in `reference.html`; add a site KPI snapshot section to `rbqm.html` with a sample query and explanation

#### Success Criteria
- [x] `cr:SiteMetrics` exists with five KPI properties and the `metricsForSite` relationship
- [x] SHACL shape enforces presence of `metricsForSite` and `top:observedAt`
- [x] Bitemporal: `top:observedAt` records when the snapshot was taken; `top:validFrom` records the reporting period start
- [x] `site_kpi_timeseries.rq` returns ordered metric history for a given site

---

### US-200-006: Study milestone with plan/actual

**type:** net-new | **tier:** ontology + sparql | **status:** todo

> As a CRO PM, I want `cr:StudyMilestone` with coded milestone types and a plan-vs-actual date comparison so that schedule deviation is computable from the graph.

#### Tasks
- T-200-006-001: Create `cr:StudyMilestone` class, `rdfs:subClassOf top:Temporal, top:Versioned`
- T-200-006-002: Add `cr:milestoneType` (DatatypeProperty — coded: FPI/LPLV/DBL/NDA/Submission/SIV)
- T-200-006-003: Add `cr:plannedDate` (DatatypeProperty, xsd:date)
- T-200-006-004: Add `cr:actualDate` (DatatypeProperty, xsd:date)
- T-200-006-005: Add `cr:milestoneVariance` (DatatypeProperty, xsd:integer — days; positive = late)
- T-200-006-006: Add `cr:milestoneForStudy` (ObjectProperty, range `cr:Study`)
- T-200-006-007: Add SHACL shape: `milestoneType` and `plannedDate` required; `milestoneVariance` must equal `actualDate - plannedDate` when both are present (SPARQL constraint)
- T-200-006-008: Add `planned_vs_milestone.rq` projection showing milestone status table
- T-200-006-009: Rebuild docs; verify `cr:StudyMilestone` appears in `reference.html`; add milestone timeline section to `setup.html` with the milestone type codes and plan-vs-actual pattern explained

#### Success Criteria
- [x] `cr:StudyMilestone` with six coded milestone types is queryable from the graph
- [x] SHACL constraint fires when `milestoneVariance` does not match the date arithmetic
- [x] SPARQL projection returns a milestone table with planned date, actual date, and variance in days
- [x] At least one milestone entity appears in the LY900018 fixture

---

## Epic SAFETY-300: Pharmacovigilance Ontology

*Clinical coding, expedited reporting, causality, and aggregate safety — the layer that makes AEs submission-ready.*

---

### US-300-001: MedDRA properties on AdverseEvent

**type:** net-new | **tier:** ontology | **status:** todo

> As a drug safety officer and as a regulatory affairs specialist, I want MedDRA coded term references on `cr:AdverseEvent` so that adverse events carry submission-ready terminology without reproducing licensed dictionary content.

#### Tasks
- T-300-001-001: Add `cr:meddraPreferredTerm` (ObjectProperty — IRI reference into MedDRA PT namespace)
- T-300-001-002: Add `cr:meddraSystemOrganClass` (ObjectProperty — IRI reference into MedDRA SOC namespace)
- T-300-001-003: Add `cr:meddraDictionaryVersion` (DatatypeProperty, xsd:string — e.g., "26.0")
- T-300-001-004: Add NOTICE comment in ontology file that MedDRA is a licensed terminology; IRIs reference, not reproduce
- T-300-001-005: Add SHACL shape: serious AEs (`cr:SeriousAdverseEvent`) require `meddraPreferredTerm` (severity: Warning for non-serious AEs)
- T-300-001-006: Update `safety-sae.ttl` example to include MedDRA IRI references
- T-300-001-007: Rebuild docs; verify MedDRA properties appear in `reference.html`; update `safety.html` to explain the MedDRA IRI reference pattern and licensing notice

#### Success Criteria
- [x] `cr:meddraPreferredTerm`, `cr:meddraSystemOrganClass`, `cr:meddraDictionaryVersion` declared on `cr:AdverseEvent`
- [x] SHACL Warning fires when a `cr:SeriousAdverseEvent` lacks `meddraPreferredTerm`
- [x] NOTICE comment present in the ontology file
- [x] Example SAE includes plausible MedDRA PT and SOC IRI references
- [x] SPARQL query "list all SAEs by MedDRA SOC" returns results against the example

---

### US-300-002: CTCAE grading on AdverseEvent

**type:** net-new | **tier:** ontology + shapes | **status:** todo

> As an oncologist and as a drug safety officer, I want CTCAE grade as a coded property on `cr:AdverseEvent` so that severity is computable and linked to the NCI Thesaurus.

#### Tasks
- T-300-002-001: Add `cr:ctcaeGrade` (ObjectProperty — range NCI Thesaurus CTCAE grade IRI or integer 1–5)
- T-300-002-002: Add `cr:ctcaeTerm` (ObjectProperty — NCI Thesaurus CTCAE term IRI)
- T-300-002-003: Add `cr:ctcaeVersion` (DatatypeProperty, xsd:string — e.g., "5.0")
- T-300-002-004: Add SHACL `sh:in` constraint on `cr:ctcaeGrade` values (1–5 as typed literals or NCI IRIs)
- T-300-002-005: Add SHACL shape: `cr:DoseLimitingToxicity` requires `ctcaeGrade` ≥ 3 (SPARQL constraint)
- T-300-002-006: Update `safety-sae.ttl` and oncology examples with CTCAE grade
- T-300-002-007: Rebuild docs; verify CTCAE properties appear in `reference.html`; update `safety.html` to show the CTCAE grading pattern and NCI Thesaurus IRI structure

#### Success Criteria
- [x] `cr:ctcaeGrade`, `cr:ctcaeTerm`, `cr:ctcaeVersion` declared on `cr:AdverseEvent`
- [x] SHACL shape fires violation when a `cr:DoseLimitingToxicity` has `ctcaeGrade` < 3
- [x] `sh:in` constraint rejects grade values outside 1–5
- [x] Example DLT carries CTCAE grade 3 or higher

---

### US-300-003: cr:SUSAR class and reporting clock

**type:** net-new | **tier:** ontology + shapes | **status:** todo

> As a drug safety officer, I want `cr:SUSAR` as a subclass of `cr:SeriousAdverseEvent` with regulatory submission timeline properties so that expedited reporting deadlines are computable from the graph.

#### Tasks
- T-300-003-001: Create `cr:SUSAR` class, `rdfs:subClassOf cr:SeriousAdverseEvent`
- T-300-003-002: Add `cr:reportingDeadline` (DatatypeProperty, xsd:dateTime — computed from `cr:sponsorAwareAt` + 7 or 15 days)
- T-300-003-003: Add `cr:submittedTo` (ObjectProperty — range `top:RegulatoryLaw` individual or agency IRI)
- T-300-003-004: Add `cr:submissionDate` (DatatypeProperty, xsd:date)
- T-300-003-005: Add `cr:susarUnexpected` (DatatypeProperty, xsd:boolean — whether the reaction was unexpected per IB)
- T-300-003-006: Add SHACL shape: if `submissionDate` > `reportingDeadline`, fire a Violation with message "SUSAR submitted after regulatory deadline"
- T-300-003-007: Write a conformant SUSAR example and an out-of-deadline violation example
- T-300-003-008: Rebuild docs; verify `cr:SUSAR` appears in `reference.html`; update `safety.html` with a SUSAR reporting clock diagram showing the sponsorAwareAt → reportingDeadline → submissionDate chain

#### Success Criteria
- [x] `cr:SUSAR` class exists with all required properties
- [x] SHACL violation fires when `submissionDate` exceeds `reportingDeadline` (SPARQL arithmetic constraint)
- [x] Conformant example (submitted within 15 days) validates cleanly
- [x] Violation example (submitted late) produces the deadline message
- [x] SPARQL query "all open SUSARs with deadline in the next 7 days" returns results against fixtures

---

### US-300-004: Causality assessment as top:Conclusion

**type:** net-new | **tier:** ontology + shapes | **status:** todo

> As a drug safety officer, I want `cr:CausalityAssessment` as a `top:Conclusion` subclass so that the physician's causality judgment is recorded with provenance, rationale, and a coded verdict.

#### Tasks
- T-300-004-001: Create `cr:CausalityAssessment` class, `rdfs:subClassOf top:Conclusion`
- T-300-004-002: Add `cr:causalityVerdict` (DatatypeProperty — coded: unrelated/possible/probable/definite)
- T-300-004-003: Wire to `top:concludesAbout` → `cr:AdverseEvent` and `top:confidence` + `top:rationale`
- T-300-004-004: Add `cr:assessedBy` (ObjectProperty, range `hcls:Person` — the reporting physician)
- T-300-004-005: Add SHACL `sh:in` constraint on `cr:causalityVerdict`
- T-300-004-006: Add SHACL shape: every `cr:SeriousAdverseEvent` should have at least one `cr:CausalityAssessment` (severity: Warning)
- T-300-004-007: Update `safety-sae.ttl` example to include a causality assessment
- T-300-004-008: Rebuild docs; verify `cr:CausalityAssessment` appears in `reference.html`; update `safety.html` to explain the causality-as-Conclusion pattern and how the four coded verdicts relate to ICH E2A

#### Success Criteria
- [x] `cr:CausalityAssessment` exists with `causalityVerdict`, `assessedBy`, and inherited `top:Conclusion` properties
- [x] `sh:in` constraint rejects verdicts outside the four coded values
- [x] SHACL Warning fires when an SAE lacks a causality assessment
- [x] Example SAE includes a causality assessment with `top:rationale` text

---

### US-300-005: Aggregate safety SPARQL projections

**type:** net-new | **tier:** sparql | **status:** todo

> As a drug safety officer, I want SPARQL projections for aggregate safety summaries so that DSUR-level tables can be generated directly from the graph.

#### Tasks
- T-300-005-001: Write `safety_ae_by_soc.rq` — all AEs grouped by MedDRA SOC and PT, with subject counts
- T-300-005-002: Write `safety_susar_dashboard.rq` — open SUSARs, deadline, submission status
- T-300-005-003: Write `safety_dlt_by_cohort.rq` — DLTs per cohort/dose level with CTCAE grade
- T-300-005-004: Add expectations to `projections/expectations.json` for each new query
- T-300-005-005: Validate queries against the updated `safety-sae.ttl` example
- T-300-005-006: Rebuild docs; verify new projections appear in the `reference.html` projections table; add aggregate safety query examples to `safety.html`

#### Success Criteria
- [x] Three SPARQL projections exist and return expected results against fixture data
- [x] `safety_ae_by_soc.rq` groups by MedDRA SOC and returns correct subject count
- [x] `safety_dlt_by_cohort.rq` filters to grade ≥ 3 and groups by dose level
- [x] All three queries included in `expectations.json`

---

## Epic ANALYSIS-400: Statistical Analysis Layer

*The SAP, estimand, data cut, and analysis population — the layer between clinical data and regulatory submission.*

---

### US-400-001: Statistical Analysis Plan completeness

**type:** refactor | **tier:** ontology + shapes | **status:** todo

> As a biostatistician, I want `cr:StatisticalAnalysisPlan` to be versioned and carry protocol governance links so that the SAP is a first-class provenance node, not just a named class.

#### Tasks
- T-400-001-001: Confirm `cr:StatisticalAnalysisPlan rdfs:subClassOf top:Evidence` in `cr-core-eop2.ttl` — add `top:Versioned` if absent
- T-400-001-002: Add `cr:sapVersion` (DatatypeProperty, xsd:string)
- T-400-001-003: Add `cr:sapGovernsStudy` (ObjectProperty, range `cr:Study`)
- T-400-001-004: Add `cr:sapAmends` (ObjectProperty, range `cr:StatisticalAnalysisPlan` — for amended SAPs)
- T-400-001-005: Add SHACL shape: `cr:StatisticalAnalysisPlan` requires `sapVersion`, `sapGovernsStudy`, and `top:observedAt`
- T-400-001-006: Update `eop2-conformant.ttl` to include a versioned SAP entity
- T-400-001-007: Rebuild docs; verify `cr:StatisticalAnalysisPlan` properties appear in `reference.html`; update `eop2.html` to explain the SAP-versioning pattern and the `sapAmends` chain

#### Success Criteria
- [x] `cr:StatisticalAnalysisPlan` subclasses both `top:Evidence` and `top:Versioned`
- [x] SHACL shape enforces `sapVersion` and `sapGovernsStudy`
- [x] `eop2-conformant.ttl` includes an SAP with version and study link
- [x] An amended SAP linked via `cr:sapAmends` validates cleanly

---

### US-400-002: Estimand property completeness

**type:** refactor | **tier:** ontology + shapes | **status:** todo

> As a biostatistician and as a regulatory affairs specialist, I want `cr:Estimand` to carry all four ICH E9(R1) components so that the estimand framework is computable, not just named.

#### Tasks
- T-400-002-001: Add `cr:estimandPopulation` (ObjectProperty, range `cr:EligibilityCriterion` set or `cr:AnalysisPopulation`)
- T-400-002-002: Add `cr:estimandVariable` (ObjectProperty, range `cr:Endpoint`)
- T-400-002-003: Add `cr:intercurrentEventStrategy` (DatatypeProperty — coded: treatment-policy/hypothetical/composite/while-on-treatment/principal-stratum)
- T-400-002-004: Add `cr:populationLevelSummary` (DatatypeProperty, xsd:string — the statistical estimand statement)
- T-400-002-005: Add SHACL `sh:in` on `cr:intercurrentEventStrategy` (five ICH E9R1 strategies)
- T-400-002-006: Add SHACL shape requiring all four components on `cr:Estimand`
- T-400-002-007: Update `eop2-conformant.ttl` estimand example with all four components
- T-400-002-008: Rebuild docs; verify estimand properties appear in `reference.html`; update `eop2.html` with a four-component estimand worked example linking to ICH E9(R1)

#### Success Criteria
- [x] `cr:Estimand` has all four ICH E9(R1) components as declared properties
- [x] `sh:in` constraint rejects intercurrent event strategies outside the five ICH values
- [x] SHACL shape fires when any component is missing
- [x] Example estimand includes all four components and validates cleanly

---

### US-400-003: DataCut entity

**type:** net-new | **tier:** ontology | **status:** todo

> As a biostatistician, I want `cr:DataCut` as a named temporal entity so that "the analysis population as of the primary data cut" is a computable graph query.

#### Tasks
- T-400-003-001: Create `cr:DataCut` class, `rdfs:subClassOf top:Temporal, top:Versioned`
- T-400-003-002: Add `cr:cutDate` (DatatypeProperty, xsd:date — the database lock date)
- T-400-003-003: Add `cr:cutForStudy` (ObjectProperty, range `cr:Study`)
- T-400-003-004: Add `cr:cutType` (DatatypeProperty — coded: primary/interim/safety-review)
- T-400-003-005: Add SHACL shape requiring `cutDate`, `cutForStudy`, and `cutType`
- T-400-003-006: Write a DataCut example entity
- T-400-003-007: Write a SPARQL query `enrollment_as_of_cut.rq` — subjects enrolled (validFrom ≤ cutDate and validUntil absent or > cutDate)
- T-400-003-008: Rebuild docs; verify `cr:DataCut` appears in `reference.html`; update `eop2.html` to explain the data cut as the bitemporal anchor for analysis population queries

#### Success Criteria
- [x] `cr:DataCut` class exists with `cutDate`, `cutForStudy`, `cutType`
- [x] SHACL shape enforces all three required properties
- [x] `enrollment_as_of_cut.rq` returns the correct enrolled subjects for the example data cut date
- [x] Bitemporal semantics: enrollment valid at cut date is correctly filtered using `top:validFrom`/`top:validUntil`

---

### US-400-004: AnalysisPopulation entity

**type:** net-new | **tier:** ontology + sparql | **status:** todo

> As a biostatistician, I want `cr:AnalysisPopulation` (ITT, mITT, PP, safety population) so that the population definition is a named, versioned entity that analysis results can trace to.

#### Tasks
- T-400-004-001: Create `cr:AnalysisPopulation` class, `rdfs:subClassOf top:Scope, top:Versioned`
- T-400-004-002: Add `cr:populationType` (DatatypeProperty — coded: ITT/mITT/PP/safety/other)
- T-400-004-003: Add `cr:populationForCut` (ObjectProperty, range `cr:DataCut`)
- T-400-004-004: Add `cr:populationCriteria` (ObjectProperty, range `cr:EligibilityCriterion` — the inclusion rules defining the population)
- T-400-004-005: Add SHACL shape requiring `populationType` and `populationForCut`
- T-400-004-006: Add `cr:analysisBasis` (ObjectProperty, domain `cr:EndpointResult`, range `cr:AnalysisPopulation`) to `cr-core-eop2.ttl`
- T-400-004-007: Write SPARQL `analysis_population_membership.rq` — subjects in a named population at the data cut
- T-400-004-008: Rebuild docs; verify `cr:AnalysisPopulation` appears in `reference.html`; update `eop2.html` to show ITT/PP/safety population definitions with the data cut anchor pattern

#### Success Criteria
- [x] `cr:AnalysisPopulation` exists with four coded population types
- [x] `cr:EndpointResult` has `cr:analysisBasis` linking to the population used
- [x] SPARQL query returns correct subject list for each population type
- [x] `eop2-conformant.ttl` updated to include an ITT population linked to the data cut

---

## Epic FHIR-500: FHIR Interoperability Bridge

*Crosswalk file, transformer, and property completeness — the path for EHR data entering the graph.*

---

### US-500-001: FHIR R4 crosswalk file

**type:** net-new | **tier:** crosswalk | **status:** todo

> As a FHIR expert and as a CDM, I want `cr-to-fhir.ttl` mapping core CR entities to their FHIR R4 counterparts so that FHIR-native integrators have a machine-readable alignment starting point.

#### Tasks
- T-500-001-001: Create `crosswalks/cr-to-fhir.ttl` with `cx:Mapping` instances for the core correspondences
- T-500-001-002: Map: `cr:Study` → `fhir:ResearchStudy`, `cr:Enrollment` → `fhir:ResearchSubject`, `cr:Visit` → `fhir:Encounter`, `hcls:Observation` → `fhir:Observation`, `cr:AdverseEvent` → `fhir:AdverseEvent`, `cr:InformedConsent` → `fhir:Consent`, `hcls:Person` → `fhir:Patient`
- T-500-001-003: Add FHIR R4 prefix declaration and `owl:Ontology` header with `dct:source` pointing to HL7 FHIR R4 IRI
- T-500-001-004: Add `cx:targetSchemaVersion "R4"` and `cx:verificationStatus` on each mapping
- T-500-001-005: Note property-level gaps (e.g., `cr:Assessment` needs `assessmentCode` before FHIR Procedure mapping is viable)
- T-500-001-006: Update `crosswalks/registry.md` to include the FHIR crosswalk
- T-500-001-007: Rebuild dist to include `cr-to-fhir.ttl` in the crosswalk bundle
- T-500-001-008: Rebuild docs; update `interop.html` to include FHIR crosswalk table showing the seven mapped entity pairs with mapping predicates and confidence scores

#### Success Criteria
- [x] `cr-to-fhir.ttl` exists with at minimum 7 mapped entity pairs
- [x] Each mapping carries `skos:mappingRelation`, `cx:confidence`, `cx:verificationStatus`, `cx:targetSchemaVersion`
- [x] `registry.md` updated
- [x] Crosswalk bundle dist artifact includes FHIR mappings
- [x] SSSOM export query includes FHIR mappings in its output

---

### US-500-002: FHIR ResearchStudy projection expansion

**type:** refactor | **tier:** sparql | **status:** todo

> As a FHIR expert, I want `fhir_research_subject.rq` expanded to cover Study, Arms, and EligibilityCriteria so that a FHIR ResearchStudy bundle can be reconstructed from the graph.

#### Tasks
- T-500-002-001: Review current `fhir_research_subject.rq` — document what it covers and what is missing
- T-500-002-002: Expand to include `fhir:ResearchStudy` fields: title, status, phase, category
- T-500-002-003: Add arm projection: `fhir:ResearchStudy.arm` from `cr:Arm`
- T-500-002-004: Add enrollment criteria projection: `fhir:ResearchStudy.enrollment` from `cr:EligibilityCriterion`
- T-500-002-005: Add subject projection: `fhir:ResearchSubject` from `cr:Enrollment`
- T-500-002-006: Add to `expectations.json`; validate against LY900018 fixture
- T-500-002-007: Rebuild docs; verify expanded projection appears in `reference.html` projections table; update `interop.html` FHIR section to show the ResearchStudy bundle reconstruction pattern

#### Success Criteria
- [x] Projection covers ResearchStudy + arm + enrollment criteria + ResearchSubject
- [x] Output structure is valid FHIR R4 JSON-LD when run against LY900018 fixture
- [x] `expectations.json` updated with expected entity count
- [x] Cross-reference with `cr-to-fhir.ttl` — projection uses the same mapped predicates

---

### US-500-003: InformedConsent property completeness

**type:** net-new | **tier:** ontology | **status:** todo

> As a FHIR expert, a DPO, and a patient stakeholder, I want `cr:InformedConsent` to carry version, form IRI, witness, and withdrawal date so that it has parity with FHIR `Consent` and can support GDPR consent management.

#### Tasks
- T-500-003-001: Add `cr:consentVersion` (DatatypeProperty, xsd:string)
- T-500-003-002: Add `cr:consentFormIRI` (ObjectProperty — IRI reference to the consented document in the TMF)
- T-500-003-003: Add `cr:witnessedBy` (ObjectProperty, range `hcls:Person`)
- T-500-003-004: Add `cr:withdrawalDate` (DatatypeProperty, xsd:date — sets the `top:validUntil` close event)
- T-500-003-005: Add SHACL shape: `withdrawalDate` must be ≥ `top:validFrom` (SPARQL constraint)
- T-500-003-006: Update `participant-conformant.ttl` to use the enriched consent properties
- T-500-003-007: Rebuild docs; verify `cr:InformedConsent` properties appear in `reference.html`; update `participant.html` consent section to show version, form IRI, witness, and withdrawal date as a complete consent record pattern

#### Success Criteria
- [x] `cr:InformedConsent` has `consentVersion`, `consentFormIRI`, `witnessedBy`, `withdrawalDate`
- [x] SHACL violation fires when `withdrawalDate` precedes the consent `validFrom`
- [x] Participant conformant example uses the enriched consent
- [x] FHIR crosswalk `cr:InformedConsent → fhir:Consent` mapping is viable (noted in `cr-to-fhir.ttl`)

---

### US-500-004: FHIR Bundle to NGSI-LD transformer

**type:** net-new | **tier:** transformer | **status:** todo

> As a FHIR expert and as a CDM, I want a transformer that reads a FHIR R4 ResearchStudy Bundle and emits `cr:Study`, `cr:Arm`, and `cr:EligibilityCriterion` NGSI-LD entities so that protocol data originating in an HL7 FHIR server can enter the graph without a manual crosswalk step.

#### Tasks
- T-500-004-001: Create `examples/fhir/to-ngsi-ld.py` modelled on the USDM transformer structure
- T-500-004-002: Implement `map_research_study()` → `cr:Study`
- T-500-004-003: Implement `map_arm()` → `cr:Arm`
- T-500-004-004: Implement `map_enrollment()` → `cr:EligibilityCriterion` (from `Group.characteristic`)
- T-500-004-005: Implement `map_research_subject()` → `cr:Enrollment` + `cr:StudySubject`
- T-500-004-006: Create a minimal FHIR R4 fixture JSON (`examples/fhir/sample-research-study.json`)
- T-500-004-007: Run transformer against fixture; validate output with pyshacl against CR shapes
- T-500-004-008: Document entity count and coverage in a SOURCES.md-style note
- T-500-004-009: Rebuild docs; update `interop.html` to add a FHIR ingestion worked example alongside the USDM transformer example, showing the parallel structure and entity mapping

#### Success Criteria
- [x] Transformer exists and runs without errors against the fixture
- [x] Output entities pass pyshacl validation with zero violations
- [x] Emitted entity types: at minimum `cr:Study`, `cr:Arm`, `cr:EligibilityCriterion`
- [x] Universal DNA (identifier, status, observedAt) present on every emitted entity
- [x] Coverage note documents which FHIR Bundle elements are mapped and which are out of scope

---

## Epic PRIVACY-600: Privacy & Compliance Architecture

*GDPR-aligned data model: consent withdrawal, lawful basis, DPA, retention, DSAR.*

---

### US-600-001: ConsentWithdrawal with cascade semantics

**type:** net-new | **tier:** ontology + shapes | **status:** todo

> As a patient stakeholder and as a DPO, I want `cr:ConsentWithdrawal` to close the `cr:InformedConsent` valid-time interval and flag post-withdrawal observations for review so that consent withdrawal has computable downstream consequences.

#### Tasks
- T-600-001-001: Create `cr:ConsentWithdrawal` class, `rdfs:subClassOf top:Temporal, top:Versioned`
- T-600-001-002: Add `cr:closesConsent` (ObjectProperty, range `cr:InformedConsent`)
- T-600-001-003: Add `cr:withdrawalReason` (DatatypeProperty — coded: subject-decision/AE/lost-to-follow-up/other)
- T-600-001-004: Add SHACL SPARQL shape: if a `hcls:Observation` has `top:validFrom` after the linked consent's `withdrawalDate`, fire a Violation
- T-600-001-005: Update `participant-conformant.ttl` to include a withdrawal entity
- T-600-001-006: Write `participant-withdrawal-violation.ttl` — an observation recorded after withdrawal date
- T-600-001-007: Rebuild docs; verify `cr:ConsentWithdrawal` appears in `reference.html`; update `participant.html` to show the consent withdrawal event closing the valid-time interval and flagging post-withdrawal observations

#### Success Criteria
- [x] `cr:ConsentWithdrawal` exists and links to the consent it closes
- [x] SHACL SPARQL constraint detects observations recorded after withdrawal date
- [x] Conformant example (no post-withdrawal observations) validates cleanly
- [x] Violation example (post-withdrawal observation) produces the expected violation message
- [x] `withdrawalReason` constrained to coded values via `sh:in`

---

### US-600-002: Lawful basis declaration model

**type:** net-new | **tier:** ontology | **status:** todo

> As a DPO, I want `cr:LawfulBasis` as a `top:RegulatoryLaw` subclass with GDPR Article instances so that every study processing EU subject data declares its lawful basis in the graph.

#### Tasks
- T-600-002-001: Create `cr:LawfulBasis` class, `rdfs:subClassOf top:RegulatoryLaw`
- T-600-002-002: Add named individuals for key GDPR articles: `cr:GDPR_Art6_1_a` (consent), `cr:GDPR_Art9_2_j` (scientific research), `cr:GDPR_Art9_2_a` (explicit consent)
- T-600-002-003: Add `cr:lawfulBasisDescription` (DatatypeProperty, xsd:string) on `cr:LawfulBasis`
- T-600-002-004: Wire `cr:Study` to lawful basis via `top:governedBy → cr:LawfulBasis`
- T-600-002-005: Add SHACL shape: studies with `top:governedBy cr:EU_GDPR` must also have `top:governedBy` pointing to a `cr:LawfulBasis` individual
- T-600-002-006: Update a study example to declare `cr:GDPR_Art9_2_j`
- T-600-002-007: Rebuild docs; verify `cr:LawfulBasis` individuals appear in `reference.html`; add a GDPR lawful basis section to `foundation.html` or a new compliance page explaining Article 9(2)(j) and the `top:governedBy` pattern

#### Success Criteria
- [x] `cr:LawfulBasis` and three GDPR Article individuals exist
- [x] SHACL shape fires when an EU-governed study lacks a lawful basis declaration
- [x] Study example includes `top:governedBy cr:GDPR_Art9_2_j`
- [x] SPARQL query "list all studies with their GDPR lawful basis" returns results

---

### US-600-003: Data Processing Agreement model

**type:** net-new | **tier:** ontology | **status:** todo

> As a DPO, I want `cr:DataProcessingAgreement` as a versioned evidence entity so that CRO and central lab agreements are queryable artifacts with their processor, controller, and effective date.

#### Tasks
- T-600-003-001: Create `cr:DataProcessingAgreement` class, `rdfs:subClassOf top:Evidence, top:Versioned`
- T-600-003-002: Add `cr:processorOrg` (ObjectProperty, range `hcls:Organization`)
- T-600-003-003: Add `cr:controllerOrg` (ObjectProperty, range `cr:Sponsor`)
- T-600-003-004: Add `cr:dpaEffectiveDate` (DatatypeProperty, xsd:date)
- T-600-003-005: Add `cr:processingPurposes` (ObjectProperty, range `cr:LawfulBasis`)
- T-600-003-006: Add SHACL shape requiring `processorOrg`, `controllerOrg`, and `dpaEffectiveDate`
- T-600-003-007: Write a conformant DPA example linking a CRO and sponsor
- T-600-003-008: Rebuild docs; verify `cr:DataProcessingAgreement` appears in `reference.html`; add a Data Processing Agreement section to `foundation.html` or a new compliance page showing the controller/processor/lawful-basis pattern

#### Success Criteria
- [x] `cr:DataProcessingAgreement` exists with four required properties
- [x] SHACL shape enforces all required fields
- [x] Conformant example validates cleanly
- [x] SPARQL query "list all DPAs for a given study" returns the example DPA

---

### US-600-004: Retention policy and data subject request

**type:** net-new | **tier:** ontology + sparql | **status:** todo

> As a DPO and as a patient, I want `cr:RetentionPolicy` and `cr:DataSubjectRequest` so that ICH E6(R3) retention periods and GDPR data subject rights are modeled with deadlines that are computable from the graph.

#### Tasks
- T-600-004-001: Create `cr:RetentionPolicy` class, `rdfs:subClassOf top:Constraint`
- T-600-004-002: Add `cr:retentionPeriod` (DatatypeProperty, xsd:duration — e.g., "P15Y")
- T-600-004-003: Add `cr:retentionBasis` (ObjectProperty, range `top:RegulatoryLaw`)
- T-600-004-004: Create `cr:DataSubjectRequest` class, `rdfs:subClassOf top:Temporal`
- T-600-004-005: Add `cr:dsrType` (DatatypeProperty — coded: access/erasure/rectification/portability)
- T-600-004-006: Add `cr:dsrDeadline` (DatatypeProperty, xsd:date — 30 days from request under GDPR)
- T-600-004-007: Add `cr:dsrStatus` (DatatypeProperty — coded: open/in-progress/fulfilled/rejected)
- T-600-004-008: Write SPARQL `gdpr_data_map.rq` — given a `hcls:Person` IRI, return all graph entities linked to that person transitively
- T-600-004-009: Write SPARQL `overdue_dsar.rq` — DSARs where `dsrDeadline` has passed and status is not fulfilled
- T-600-004-010: Rebuild docs; verify `cr:RetentionPolicy` and `cr:DataSubjectRequest` appear in `reference.html`; update `participant.html` to explain the data subject rights model and show the overdue-DSAR query

#### Success Criteria
- [x] `cr:RetentionPolicy` and `cr:DataSubjectRequest` exist with all declared properties
- [x] `gdpr_data_map.rq` returns all transitively linked entities for a given person IRI in the participant example
- [x] `overdue_dsar.rq` correctly identifies overdue requests in a fixture
- [x] `dsrType` constrained to four coded values via `sh:in`

---

## Epic XWALK-700: Crosswalk Coverage

*Expanding the mapping surface: USDM depth, MedDRA reference, SDTM, crosswalk governance.*

---

### US-700-001: USDM crosswalk expansion

**type:** refactor | **tier:** crosswalk | **status:** todo

> As a CDM and as a knowledge engineer, I want the USDM-to-CR crosswalk to cover the full study design layer (not just the 18 current mappings) so that the coverage gap against the 693-property USDM standard is documented and progressively closed.

#### Tasks
- T-700-001-001: Audit `usdm-to-cr.ttl` against the USDM v4 class list — produce a coverage gap table
- T-700-001-002: Add crosswalk entries for: `usdm:Estimand` components (population, variable, intercurrent event strategy, summary)
- T-700-001-003: Add crosswalk entries for: `usdm:Biomedical Concept` property mappings to `cr:DataElementDef`
- T-700-001-004: Add crosswalk entries for: `usdm:Amendment` → `cr:ProtocolVersion` (amendment subtype)
- T-700-001-005: Add `cx:targetSchemaVersion "4.0"` and `cx:targetSchemaIRI` to the crosswalk `owl:Ontology` header
- T-700-001-006: Add a gap table comment block in the file header listing unmapped USDM classes with rationale (out-of-scope vs. future)
- T-700-001-007: Update `registry.md` to record coverage percentage
- T-700-001-008: Rebuild dist; update `interop.html` to show the USDM coverage gap table and the expanded mapping count

#### Success Criteria
- [x] `cx:targetSchemaVersion` declared on the crosswalk file
- [x] At least 5 new mapping entries added
- [x] Gap table comment lists all USDM classes with status: mapped/partial/out-of-scope/future
- [x] SSSOM export query output reflects the new mappings
- [x] `registry.md` coverage percentage updated

---

### US-700-002: MedDRA crosswalk reference file

**type:** net-new | **tier:** crosswalk | **status:** todo

> As a drug safety officer and as a CDM, I want `cr-to-meddra.ttl` as a reference crosswalk with licensing notice so that MedDRA term IRI patterns are documented without reproducing licensed content.

#### Tasks
- T-700-002-001: Create `crosswalks/cr-to-meddra.ttl` with `owl:Ontology` header
- T-700-002-002: Add NOTICE block: MedDRA is a licensed terminology; mappings are IRI patterns, not reproduced content
- T-700-002-003: Map `cr:AdverseEvent` → MedDRA LLT/PT/SOC IRI pattern (as `skos:closeMatch` with `cx:confidence 0.90`)
- T-700-002-004: Map `cr:DoseLimitingToxicity` → MedDRA PT pattern (domain: oncology AEs)
- T-700-002-005: Map `cr:SeriousAdverseEvent` → MedDRA seriousness criteria terms
- T-700-002-006: Add `cx:targetSchemaVersion` for MedDRA version 26.0 and a note that the version pin must be updated annually
- T-700-002-007: Update `registry.md`
- T-700-002-008: Rebuild dist; add a MedDRA section to `interop.html` (or `safety.html`) explaining the licensing constraint, the IRI-pattern-only approach, and the annual version-pin update process

#### Success Criteria
- [x] `cr-to-meddra.ttl` exists with NOTICE block and at least 5 mapping entries
- [x] `cx:targetSchemaVersion "26.0"` declared
- [x] Licensing notice present and accurate
- [x] SSSOM export query includes MedDRA mappings in output
- [x] `registry.md` updated with MedDRA entry and licensing note

---

### US-700-003: SDTM crosswalk file

**type:** net-new | **tier:** crosswalk | **status:** todo

> As a CDM and as a regulatory affairs specialist, I want `cr-to-sdtm.ttl` mapping CR entities to SDTM domains and variables so that the relationship between the graph and the submission dataset is formally declared rather than implied by the SPARQL projections.

#### Tasks
- T-700-003-001: Create `crosswalks/cr-to-sdtm.ttl`
- T-700-003-002: Map domain-level correspondences: `cr:AdverseEvent` → SDTM AE domain, `cr:Enrollment` → SDTM DM domain, `cr:Administration` → SDTM EX domain, `cr:Visit` → SDTM SV domain, `cr:StudySubject` → SDTM DM.USUBJID
- T-700-003-003: Map key variable-level correspondences (at least 5 per domain)
- T-700-003-004: Align crosswalk predicates with SDTM IG CDISC IRIs where published
- T-700-003-005: Add `cx:targetSchemaVersion "3.4"` (SDTM IG version)
- T-700-003-006: Cross-reference to the corresponding SPARQL projection for each domain
- T-700-003-007: Update `registry.md`
- T-700-003-008: Rebuild dist; add an SDTM section to `interop.html` showing the domain-level mapping table and cross-referencing the corresponding SPARQL projections

#### Success Criteria
- [x] `cr-to-sdtm.ttl` exists with domain-level and variable-level mappings
- [x] At least 4 SDTM domain mappings (AE, DM, EX, SV)
- [x] Each domain mapping notes the corresponding SPARQL projection file
- [x] SSSOM export includes SDTM mappings
- [x] `cx:targetSchemaVersion` declared

---

### US-700-004: Crosswalk versioning governance

**type:** refactor | **tier:** crosswalk | **status:** todo

> As a knowledge engineer, I want every crosswalk file to declare its target schema version and a CI check that detects when a crosswalk's target IRI stops resolving so that broken mappings are caught automatically.

#### Tasks
- T-700-004-001: Add `cx:targetSchemaVersion` and `cx:targetSchemaIRI` to all existing crosswalk files
- T-700-004-002: Add a `crosswalk_check.py` script to `cr-domain/docs/` that fetches each `cx:targetSchemaIRI` and checks HTTP 200
- T-700-004-003: Add `cx:lastVerifiedDate` to each crosswalk `owl:Ontology` header
- T-700-004-004: Document the versioning policy in `crosswalks/registry.md`: when a target schema updates, all affected mappings move to `cx:reviewStatus "needs-review"`
- T-700-004-005: Update `registry.md` docs to include the full versioning governance section; add a crosswalk maintenance callout to `interop.html` explaining the review-on-schema-update policy

#### Success Criteria
- [x] All crosswalk files have `cx:targetSchemaVersion` and `cx:targetSchemaIRI` declared
- [x] `crosswalk_check.py` runs without error and reports HTTP status for each target IRI
- [x] Policy section added to `registry.md`
- [x] Running `crosswalk_check.py` on the existing files returns 200 for all resolvable IRIs

---

## Epic AI-800: Inference & Provenance Model

*Completing the AI provenance design: prompt capture, model identity, reproducibility, and design documentation.*

---

### US-800-001: top:Conclusion reproducibility properties

**type:** refactor | **tier:** ontology | **status:** todo

> As a knowledge engineer and as an AI/ML engineer, I want `top:Conclusion` to carry the prompt template and source context so that LLM-generated conclusions are reproducible and auditable in regulated contexts.

#### Tasks
- T-800-001-001: Add `top:promptTemplate` (ObjectProperty — IRI reference to a versioned prompt template; range `top:Evidence`)
- T-800-001-002: Add `top:sourceContext` (DatatypeProperty, xsd:string — the input excerpt the model reasoned over, or a hash reference)
- T-800-001-003: Add `top:modelVersion` (ObjectProperty — IRI of the model used; pattern: `anthropic:claude-{version}`)
- T-800-001-004: Add SHACL shape: `top:Conclusion` subclasses require `top:promptTemplate` or `top:sourceContext` (severity: Warning — not all conclusions are LLM-generated)
- T-800-001-005: Update `cx:CausalityAssessment` (SAFETY-300-004) and any existing `top:Conclusion` examples to include the new properties
- T-800-001-006: Add `top:modelVersion` property to `top:AutonomousAgent`
- T-800-001-007: Rebuild docs; update `foundation.html` AI/provenance section to show the `top:Conclusion` reproducibility properties and the `top:AutonomousAgent` model identity pattern

#### Success Criteria
- [x] `top:Conclusion` has `top:promptTemplate`, `top:sourceContext`, `top:modelVersion` as declared properties
- [x] `top:AutonomousAgent` has `top:modelVersion`
- [x] SHACL Warning fires when an LLM-generated conclusion (detected by `cx:inferredBy`) lacks `top:promptTemplate`
- [x] Example conclusion entity includes all three new properties

---

### US-800-002: cx:inferredBy / cx:confirmedBy SHACL shape

**type:** net-new | **tier:** shapes | **status:** todo

> As a knowledge engineer, I want a SHACL shape enforcing that LLM-inferred mappings are never promoted to `confirmed` without a `cx:confirmedBy` human reviewer so that the human-in-the-loop requirement is machine-enforceable.

#### Tasks
- T-800-002-001: Add SHACL shape to `shapes/crosswalk.ttl`: if `cx:reviewStatus "confirmed"` then `cx:confirmedBy` must be present (severity: Violation)
- T-800-002-002: Add SHACL shape: if `cx:inferredBy` is present (LLM origin) then `cx:mappingMethod "LLMInference"` must be set (severity: Warning)
- T-800-002-003: Add SHACL shape: `cx:reviewStatus "confirmed"` with `cx:inferredBy` but without `cx:confirmedBy` → Violation
- T-800-002-004: Write a crosswalk-mapping-llm-unconfirmed-violation.ttl example
- T-800-002-005: Update `crosswalk-mapping-violation.ttl` to cover the new shape
- T-800-002-006: Rebuild docs; add the human-in-the-loop constraint to `reference.html` under the crosswalk shapes section; update `interop.html` to explain the `cx:inferredBy` / `cx:confirmedBy` promotion gate

#### Success Criteria
- [x] A `cx:Mapping` with `reviewStatus "confirmed"` but no `cx:confirmedBy` produces a SHACL Violation
- [x] A `cx:Mapping` with `cx:inferredBy` but `reviewStatus "confirmed"` and no `cx:confirmedBy` produces a Violation
- [x] Violation example validates as expected under pyshacl
- [x] Existing `crosswalk-mapping-violation.ttl` example is not broken by the new shapes

---

### US-800-003: GraphRAG recipe documentation

**type:** net-new | **tier:** docs | **status:** todo

> As an AI/ML engineer, I want a worked GraphRAG recipe for eligibility criterion retrieval so that the canonical graph-augmented inference pattern is documented and reproducible.

#### Tasks
- T-800-003-001: Write `examples/graphrag/eligibility-rag-recipe.md` documenting the query pattern: given a patient's FHIR Observations, retrieve `cr:EligibilityCriterion` nodes by semantic similarity and pass as LLM context
- T-800-003-002: Document the SPARQL retrieval step (structured retrieval over `criterionText`)
- T-800-003-003: Document the vector retrieval step (semantic similarity over embedded criterion text)
- T-800-003-004: Document the LLM prompt template and output schema (`top:Conclusion` with `causalityVerdict`)
- T-800-003-005: Specify which entity properties to embed: `rdfs:label`, `rdfs:comment`, `criterionText`, `top:rationale`
- T-800-003-006: Add a code sketch (pseudocode or Python) of the hybrid retrieval loop
- T-800-003-007: Add a new `ai.html` page (or `graphrag.html`) via `build_docs.py` surfacing the recipe; link from the main nav under Cross-cutting; ensure `foundation.html` references the AI/provenance model page

#### Success Criteria
- [x] Recipe document exists with all five sections (retrieval, vector step, LLM template, output schema, code sketch)
- [x] SPARQL query in the recipe runs against the LY900018 EligibilityCriterion fixture
- [x] Output schema references `top:Conclusion` with `top:promptTemplate`, `top:confidence`, and `top:rationale`
- [x] Document is referenced from `AI-900` section of documentation site

---

## Epic DIST-900: Distribution & Developer Experience

*Test harness, validation pipeline, versioning strategy, and context URL — the infrastructure that makes the artifacts trustworthy.*

---

### US-900-001: pyshacl test harness for all examples

**type:** net-new | **tier:** transformer | **status:** todo

> As a software engineer and as an ontology expert, I want a test runner that validates all 98 example files against the SHACL shapes bundle and asserts expected outcomes so that shape regressions are caught at build time.

#### Tasks
- T-900-001-001: Create `cr-domain/tests/run_shacl.py` that loads `top-cr-shapes-v1.ttl` and runs pyshacl against each example file
- T-900-001-002: Read expected outcomes from `tests/manifest.json` (conformant → no violations, violation → ≥1 violation with expected message, warning → ≥1 warning)
- T-900-001-003: Populate `tests/manifest.json` with entries for all 98 current example files
- T-900-001-004: Output a summary table: pass/fail per example, total violations found vs. expected
- T-900-001-005: Exit non-zero if any example produces unexpected results
- T-900-001-006: Document run instructions in `cr-domain/README.md`
- T-900-001-007: Update `cr-domain/README.md` to include a Testing section with `python3 tests/run_shacl.py` as the primary validation command and a description of the manifest format

#### Success Criteria
- [x] `run_shacl.py` runs against all 98 examples with zero unexpected failures on current codebase
- [x] `manifest.json` has an entry for every example file
- [x] Script exits 0 on the current codebase; exits non-zero when a violation example produces no violation (regression test)
- [x] README documents `python3 tests/run_shacl.py` as the test command

---

### US-900-002: SPARQL projection test harness

**type:** net-new | **tier:** sparql | **status:** todo

> As a software engineer, I want a test runner that executes all 21 SPARQL projection queries against fixture data and asserts minimum result counts so that broken projections are caught when the ontology changes.

#### Tasks
- T-900-002-001: Create `cr-domain/tests/run_projections.py` using rdflib to load fixture data and execute each `.rq` file
- T-900-002-002: Read expected minimum result counts from `projections/expectations.json`
- T-900-002-003: Populate `expectations.json` with minimum row counts for all 21 existing projections against the LY900018 fixture
- T-900-002-004: Output a summary: query name, rows returned, expected minimum, pass/fail
- T-900-002-005: Exit non-zero on any projection returning fewer rows than expected
- T-900-002-006: Update `cr-domain/README.md` Testing section to include `python3 tests/run_projections.py` and document how to update `expectations.json` after adding new fixture data

#### Success Criteria
- [x] All 21 projections run without SPARQL syntax errors
- [x] Every projection returns at least the expected minimum row count against LY900018 fixture
- [x] `expectations.json` fully populated
- [x] Script exits 0 on current codebase

---

### US-900-003: USDM transformer SHACL validation

**type:** net-new | **tier:** transformer | **status:** todo

> As a software engineer, I want the USDM transformer output validated against the CR SHACL shapes so that a regression in the transformer is immediately visible as a shape violation rather than a silent data quality issue.

#### Tasks
- T-900-003-001: Extend `to-ngsi-ld.py` (or add `tests/validate_transformer_output.py`) to load the emitted NGSI-LD entities into rdflib via the JSON-LD context and run pyshacl
- T-900-003-002: Assert zero violations (not warnings) on the current LY900018 output
- T-900-003-003: Document any warnings and whether they are expected (e.g., optional properties absent)
- T-900-003-004: Add to the test runner sequence: dist build → transformer → validate output
- T-900-003-005: Update `ingestion.html` to include a validation step in the LY900018 worked example showing the SHACL conformance result and any triaged warnings

#### Success Criteria
- [x] Transformer output for LY900018 produces zero SHACL violations
- [x] Any warnings are documented and triaged
- [x] Validation runs automatically after `build_dist.py` in the test sequence

---

### US-900-004: Semantic versioning strategy

**type:** net-new | **tier:** docs | **status:** todo

> As a software engineer and as a DevOps engineer, I want a documented versioning policy with a `CHANGELOG.md` so that consumers can detect breaking changes and plan migrations.

#### Tasks
- T-900-004-001: Create `CHANGELOG.md` at `cr-domain/CHANGELOG.md` with `v1.0.0` entry for current state
- T-900-004-002: Document the versioning policy: `MAJOR` = breaking IRI or shape changes; `MINOR` = additive classes/properties; `PATCH` = comment/label corrections
- T-900-004-003: Add `owl:versionIRI` to the dist ontology header pointing to `<https://top.scientix.ai/cr/v1.0.0>`
- T-900-004-004: Add `owl:priorVersion` pattern for future use
- T-900-004-005: Document the deprecation pattern: `owl:deprecated true` + `rdfs:comment "Deprecated in v1.x: use {replacement} instead"`
- T-900-004-006: Add versioning policy section to the Foundation documentation page
- T-900-004-007: Update `foundation.html` to include the semantic versioning policy (MAJOR/MINOR/PATCH definitions), the deprecation pattern, and a link to `CHANGELOG.md`

#### Success Criteria
- [x] `CHANGELOG.md` exists with `v1.0.0` entry listing current capabilities
- [x] `owl:versionIRI` present in dist bundle
- [x] Versioning policy documented in Foundation page
- [x] Deprecation pattern example present in documentation

---

### US-900-005: Context URL hosting plan

**type:** net-new | **tier:** docs | **status:** todo

> As an NGSI-LD expert and as a software engineer, I want a documented plan for hosting `top-cr-v1.ngsi-context.jsonld` at its canonical URL so that any Scorpio broker can resolve the `@context` reference without a 404.

#### Tasks
- T-900-005-001: Document the canonical URL: `https://top.scientix.ai/cr/v1.ngsi-context.jsonld`
- T-900-005-002: Document the hosting options: GitHub Pages (current domain), S3 + CloudFront, or CDN
- T-900-005-003: Add the context URL to the Foundation page with a live/not-yet-live status note
- T-900-005-004: Add a `Content-Type: application/ld+json` requirement and long-lived `Cache-Control` header recommendation
- T-900-005-005: Add a fallback pattern to the transformer: `if context URL 404, fall back to local file path`
- T-900-005-006: Add context URL resolution test to `run_projections.py` or a separate `check_context_url.py`
- T-900-005-007: Update `foundation.html` and `implementation.html` with the canonical context URL, hosting options comparison, the fallback pattern, and a live/not-yet-live status indicator

#### Success Criteria
- [x] Context URL hosting plan documented in Foundation page
- [x] Fallback pattern implemented in the USDM transformer
- [x] `check_context_url.py` correctly distinguishes live URL from 404
- [x] Build pipeline warns (not errors) when context URL is not yet live

---

*End of backlog — 9 epics, 39 user stories. Last updated July 2026.*
