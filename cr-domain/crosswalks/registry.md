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

## Not mapped (honest gaps)
- **CTO (Clinical Trial Ontology):** its core defines registry-identifier terms, not a clean
  "clinical trial" class (the concept is imported) — no defensible target, mapping dropped.
- **OCRe (Ontology of Clinical Research):** source not reachable from the build environment;
  deferred until a primary source can be parsed.
- **MedDRA / SNOMED / CDISC programmatic:** BYOL — added per customer license.
- **Manufacturing/supply (AFO, MCBO, CMC Process, IDMP-O, GS1) and heavy PV (PVONTO):** later domains.
- **SULO / BFO:** optional outbound crosswalk, lossy on bitemporality — deferred past v1.
