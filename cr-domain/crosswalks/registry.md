# Crosswalk & curation registry (v1, oncology Pre-IND→EOP2)

Crosswalks are **owned, provenance-tagged SSSOM mappings** we curate — never imports. Each is a
`cx:Mapping` validated by the hardened curation gate (`shapes/crosswalk.ttl`): SKOS
predicate (controlled), semapv justification (controlled), confidence, mapping date, author,
**verification status**, transaction time, and PROV. An SSSOM TSV (`projections/sssom_export.rq`)
is an edge projection of these mappings.

## Curation pipeline
`Proposed → Validated → Production` — promotion requires structural compatibility, licensing
clarity, provenance completeness, a verified target IRI, and a maintenance commitment.

## Verified mappings (target IRIs confirmed against primary sources, 2026-06-20)
| cr-core subject | predicate | external target (verified IRI) | conf | source |
|---|---|---|---|---|
| `cr:AdverseEvent` | exactMatch | `obo:OAE_0000001` "adverse event" | 0.95 | OAE-ontology/OAE `oae.owl` |
| `cr:InformedConsent` | closeMatch | `obo:OBI_0000810` "informed consent process" | 0.85 | obi-ontology/obi `obi.owl` |
| `cr:Study` | broadMatch | `obo:OBI_0000066` "investigation" | 0.80 | obi-ontology/obi `obi.owl` |
| `cr:ProtocolVersion` | closeMatch | `obo:OBI_0000272` "protocol" | 0.80 | obi-ontology/obi `obi.owl` |

Each verified against the OWL source fetched from GitHub raw and parsed (OAE adverse-event class;
OBI labels). EBI OLS and OBO PURL were unreachable from the build environment (403), so GitHub raw
sources were used as the primary of record.

## CDISC USDM v4.0 crosswalk (`crosswalks/usdm-to-cr.ttl`)
Maps cr-core to the generated, vendored USDM v4.0 OWL layer (`ontology/vendor/usdm/`). Target IRIs
verified against the pinned primary source (DDF-RA `USDM_API.json` @ tag `v4.0.0`, sha `dc4303bc`).
The curation respects the **plan↔execution boundary**: USDM is a design-time *definition* model;
cr-core is operator/execution + provenance + bitemporal.

| cr-core subject | predicate | USDM target | conf | note |
|---|---|---|---|---|
| `cr:Study` | closeMatch | `usdm:Study` | 0.90 | |
| `cr:ProtocolVersion` | closeMatch | `usdm:StudyVersion` | 0.85 | |
| `cr:Arm` / `cr:Cohort` | closeMatch | `usdm:StudyArm` / `usdm:StudyCohort` | 0.90 / 0.85 | |
| `cr:EligibilityCriterion` | exactMatch | `usdm:EligibilityCriterion` | 0.95 | |
| `cr:Endpoint` / `cr:Estimand` | closeMatch | `usdm:Endpoint` / `usdm:Estimand` | 0.90 | |
| `cr:DataElementDef` | closeMatch | `usdm:BiomedicalConcept` | 0.80 | |
| `cr:StudySite` | exactMatch | `usdm:StudySite` | 0.95 | |
| `hcls:Organization` | closeMatch | `usdm:Organization` | 0.90 | |
| `cr:ScheduleTimeline` | closeMatch | `usdm:ScheduleTimeline` | 0.85 | cr adds bitemporal/as-of + reconciliation |
| `cr:PlannedEncounter` | closeMatch | `usdm:Encounter` | 0.90 | SoA bridge |
| `cr:PlannedActivity` | closeMatch | `usdm:ScheduledActivityInstance` | 0.85 | SoA bridge |
| `cr:Timing` | closeMatch | `usdm:Timing` | 0.85 | SoA bridge |
| `cr:Capability` | relatedMatch | `usdm:Activity` | 0.60 | action-type vs planned-activity definition |
| `cr:Administration` | **relatedMatch** | `usdm:Administration` | 0.50 | **plan vs execution** (see below) |
| `cr:Enrollment` | **relatedMatch** | `usdm:SubjectEnrollment` | 0.40 | **plan vs execution** (see below) |

### Corrections to the early USDM analysis (the curation judgment)
The early integration analysis proposed several `skos:exactMatch` mappings across the plan/execution
boundary. These are deliberately re-graded or rejected here:
- **`usdm:Administration` is a *planned regimen*** (carries `dose`/`route`/`frequency`), not an
  executed dosing event → `relatedMatch` (0.50), not `exactMatch` (0.95).
- **`usdm:SubjectEnrollment` is a *planned enrollment quantity*** (carries `quantity`,
  `forStudyCohortId`, `forStudySiteId`), not the executed Person↔Subject act → `relatedMatch`
  (0.40), not `exactMatch` (1.00).
- **"Activity (Adverse Event)" → `cr:AdverseEvent` rejected:** USDM is design-time and has no
  executed-AE class; `cr:AdverseEvent` is an execution outcome. No mapping.
- **`InformedConsent` → `cr:InformedConsent` rejected:** no `InformedConsent` class exists in
  USDM v4.0.0 (verified against the pinned spec).

## Not mapped (honest gaps)
- **CTO (Clinical Trial Ontology):** its core defines registry-identifier terms, not a clean
  "clinical trial" class (the concept is imported) — no defensible target, mapping dropped.
- **OCRe (Ontology of Clinical Research):** source not reachable from the build environment;
  deferred until a primary source can be parsed.
- **MedDRA / SNOMED / CDISC programmatic:** BYOL — added per customer license.
- **Manufacturing/supply (AFO, MCBO, CMC Process, IDMP-O, GS1) and heavy PV (PVONTO):** later domains.
- **SULO / BFO:** optional outbound crosswalk, lossy on bitemporality — deferred past v1.