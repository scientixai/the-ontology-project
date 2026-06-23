# usdm-rdf-gen — deterministic USDM v4.0 → OWL generator

TOP-owned tooling that renders the CDISC USDM v4.0 class model into a structural
OWL ontology. The conversion is **mechanical, not semantic**: it regenerates
byte-for-byte from the pinned CDISC source, so TOP never hand-owns (or has to
chase) the USDM model — we own only the generator and the USDM↔cr crosswalk.

```
ddf-ra-v4.0.0/USDM_API.json   # pinned CDISC DDF-RA OpenAPI model (CC-BY-4.0, vendored source)
ddf-ra-v4.0.0/USDM_CT.xlsx     # pinned CDISC controlled terminology (NCIt codes + definitions)
ddf-ra-v4.0.0/usdm_ct.json     # CT extracted to JSON (so generate.py stays stdlib-only)
extract_ct.py                  # one-time CT extractor (requires openpyxl)
verify_ncit.py                 # verify the NCIt anchors against a current NCIt FLAT file
generate.py                    # the class-model generator (Apache-2.0, stdlib-only)
generate_ct.py                 # the controlled-terminology -> SKOS generator (stdlib-only)
```

`generate_ct.py` emits `ontology/vendor/usdm/usdm-ct-v4.ttl`: the DDF valid value sets as
SKOS concept schemes (one per codelist, bound to its `usdm:` property, NCIt-anchored), one
`skos:Concept` per permissible value.

The NCIt anchors are verified against a current NCI Thesaurus release (the FLAT file from
evs.nci.nih.gov/evs-download/thesaurus-downloads — large, not vendored). The durable result
lives in `ontology/vendor/usdm/ncit-verification.json` + `NCIT_VERIFICATION.md`; the harness
gates it.

Run:

```
python3 tools/usdm-rdf-gen/extract_ct.py   # only when re-pinning CT (needs openpyxl)
python3 tools/usdm-rdf-gen/generate.py
```

Emits `ontology/vendor/usdm/usdm-v4.ttl` (the vendored artifact, CC-BY-4.0) plus
`PROVENANCE.md` (pinned tag/commit, source + output sha256, class/property counts).
Output is byte-reproducible (classes and properties emitted in sorted order); the
test harness parses it and asserts the full class footprint.

**Scope:** one `owl:Class` per entity, class-scoped `owl:Object`/`DatatypeProperty`
per attribute, `owl:Restriction` cardinality from the schema (required / nullable /
array); **NCIt anchoring** (`skos:exactMatch` to `NCIT_*`) + `skos:prefLabel` +
CDISC **definitions** on classes and properties from `USDM_CT.xlsx`; and inline enum
allowed-values. Remaining follow-up: rendering the full CT **valid value sets**
(codelists) as SKOS concept schemes (a separate artifact).

**Namespace:** `https://w3id.org/cdisc/usdm/v4/` — CDISC-scoped, deliberately not a
`top:` namespace, because this renders CDISC's model (the external side of the
crosswalk), not TOP's.

**Re-pinning a new USDM release:** drop the new `USDM_API.json` into a new
`ddf-ra-<tag>/`, update the tag/commit constants in `generate.py`, regenerate,
and review the crosswalk for any class changes.
