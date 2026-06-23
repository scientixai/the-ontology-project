# usdm-rdf-gen — deterministic USDM v4.0 → OWL generator

TOP-owned tooling that renders the CDISC USDM v4.0 class model into a structural
OWL ontology. The conversion is **mechanical, not semantic**: it regenerates
byte-for-byte from the pinned CDISC source, so TOP never hand-owns (or has to
chase) the USDM model — we own only the generator and the USDM↔cr crosswalk.

```
ddf-ra-v4.0.0/USDM_API.json   # pinned CDISC DDF-RA OpenAPI model (CC-BY-4.0, vendored source)
generate.py                   # the generator (Apache-2.0)
```

Run:

```
python3 tools/usdm-rdf-gen/generate.py
```

Emits `ontology/vendor/usdm/usdm-v4.ttl` (the vendored artifact, CC-BY-4.0) plus
`PROVENANCE.md` (pinned tag/commit, source + output sha256, class/property counts).
Output is byte-reproducible (classes and properties emitted in sorted order); the
test harness parses it and asserts the full class footprint.

**Scope (v1):** structure only — one `owl:Class` per entity, class-scoped
`owl:Object`/`DatatypeProperty` per attribute, `owl:Restriction` cardinality from
the schema (required / nullable / array). NCIt anchoring from `USDM_CT.xlsx` and
enumeration/codelist rendering are planned follow-ups.

**Namespace:** `https://w3id.org/cdisc/usdm/v4/` — CDISC-scoped, deliberately not a
`top:` namespace, because this renders CDISC's model (the external side of the
crosswalk), not TOP's.

**Re-pinning a new USDM release:** drop the new `USDM_API.json` into a new
`ddf-ra-<tag>/`, update the tag/commit constants in `generate.py`, regenerate,
and review the crosswalk for any class changes.
