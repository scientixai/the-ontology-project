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
