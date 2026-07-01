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
