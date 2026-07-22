# Vendored artifact provenance — USDM v4 RDF/OWL

**Not authoritative.** The authoritative USDM source is CDISC DDF-RA. The RDF/OWL
rendering below is **vendored from the canonical community artifact**, not generated
locally — TOP is an *adopter* of that work, not a parallel author (leverage, don't
reinvent).

**Namespace status (`https://w3id.org/cdisc/usdm/v4/`).** CDISC has **no ratified
official USDM-RDF**; the RDF representation is a community effort (championed by
Kerstin Forsberg / the CDISC-RDF lineage), and `w3id.org/cdisc/usdm/` is that
**community convention**, not an official CDISC namespace. Draft / not-yet-normative,
so the pin is explicit and re-verified on each of her releases.

## Source of record — `github.com/kerfors/usdm-rdf` (Kerstin Forsberg)

The `w3id.org/cdisc/usdm/v4/` namespace's registered target. Her `usdm_v4.ttl` is
itself a mechanical rendering of CDISC DDF-RA `dataStructure.yml` @ tag **v4.0.0** —
the same USDM source our retired local generator used, so the NCIt CT anchoring (below)
is unaffected by the swap. Vendored verbatim (byte-exact), CC-BY-4.0:

| vendored file | upstream file | sha256 | notes |
|---|---|---|---|
| `usdm-v4.ttl` | `usdm_v4.ttl` (v0.6.0) | `1a66fa39d4387a67ffb61da0605edbd380263f5df8b12e9ff5664c2e1a871e43` | 90 classes, 693 properties. Kept at our filename to avoid consumer churn; content is hers, byte-exact. |
| `usdm_v4.shapes.ttl` | `usdm_v4.shapes.ttl` (v0.6.0) | `ae6da5fdca59822eb2a9943c9cbbf0a529bdff4b04145d1ee51e80adecb93bfb` | her SHACL structural shapes (new asset) |
| `usdm_v4.shapes-ct.ttl` | `usdm_v4.shapes-ct.ttl` (v0.6.0) | `898449dd9cea9631da96ebacfe64c4c6717ab8b2d98c14d830e856600a8fe4ca` | her SHACL CT shapes (new asset) |
| `usdm_v4.context.jsonld` | `usdm_v4.context.jsonld` (v0.6.0) | `1919be9f0b24b3db80f2e1815f7057cae08b32e9c28b2ad07fecbe65f91694eb` | her JSON-LD 1.1 instance context (new asset) |

| field | value |
|---|---|
| upstream repo | github.com/kerfors/usdm-rdf |
| upstream version | v0.6.0 (versionIRI `w3id.org/cdisc/usdm/v4/0.6.0`) |
| upstream branch | main |
| retrieved | 2026-07-22 (via raw.githubusercontent.com) |
| ultimate USDM source | CDISC DDF-RA `dataStructure.yml` @ v4.0.0 |
| license | CC-BY-4.0 |

**Re-verify on update:** re-fetch her files, re-compare sha256, and re-run the
crosswalk resolution check (every `usdm:` IRI in `crosswalks/usdm-to-cr.ttl` must
resolve in `usdm-v4.ttl`). Her class names can differ from our old local generation —
the crosswalk was remapped on adoption (`Amendment`→`StudyAmendment`,
`EstimandPopulation`→`AnalysisPopulation`, `EstimandVariable`→`Endpoint` relatedMatch,
`IntercurrentEventStrategy`→`IntercurrentEvent` relatedMatch).

## CT layer — still ours (complementary)

Her artifact renders the OWL model + shapes but **not** the CT codelists as SKOS. We
continue to generate the CT SKOS from DDF-RA, so `usdm-ct-v4.ttl` + the NCIt
verification remain TOP-produced and are a genuine complement, not a duplication:

| field | value |
|---|---|
| CT source | github.com/cdisc-org/DDF-RA `Deliverables/CT/USDM_CT.xlsx` @ v4.0.0 |
| CT sha256 | `a9efa740abc41299efa83607a0880012ac8dcc8df7db60259c2a7e96f42cd94f` |
| CT output | `ontology/vendor/usdm/usdm-ct-v4.ttl` (SKOS) |
| CT generator | `tools/usdm-rdf-gen/extract_ct.py` + `generate_ct.py` (still active) |
| NCIt verification | `ncit-verification.json` (NCIt anchors are a property of the DDF-RA CT, independent of the OWL rendering — unaffected by the swap) |

## Retired

`tools/usdm-rdf-gen/generate.py` (the OWL generator) is **superseded** by vendoring
`kerfors/usdm-rdf`. It is retained for history and marked superseded in its header;
do not run it to (re)produce `usdm-v4.ttl`. The CT tooling (`extract_ct.py`,
`generate_ct.py`, `verify_ncit.py`) remains active.
