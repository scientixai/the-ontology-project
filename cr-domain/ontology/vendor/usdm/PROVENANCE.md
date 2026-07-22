# Vendored artifact provenance — USDM v4.0 OWL

Generated, **not authoritative**. The authoritative USDM source is CDISC DDF-RA.

**Namespace status (`https://w3id.org/cdisc/usdm/v4/`).** CDISC has **no ratified
official USDM-RDF**; the RDF representation is a community effort (championed by
Kerstin Forsberg / the CDISC-RDF lineage), and the `w3id.org/cdisc/usdm/` namespace
is that **aspirational community convention**, not an official CDISC artifact. This
vendored file is therefore an **early, faithful implementation** of that convention —
derived deterministically from the authoritative DDF-RA source below — not a mirror of
a canonical RDF (none exists). If/when CDISC ratifies an official USDM-RDF, align this
rendering (and our IRI-minting scheme — currently the `usdm:Class-property` pattern) to
it. Coordinate the scheme with the CDISC-RDF effort so this stays forward-compatible.

| field | value |
|---|---|
| model source | github.com/cdisc-org/DDF-RA `Deliverables/API/USDM_API.json` |
| CT source | github.com/cdisc-org/DDF-RA `Deliverables/CT/USDM_CT.xlsx` |
| pinned tag | v4.0.0 |
| pinned commit | aa303cb32f5d3ceecc68a16803e26720d2c1fc26 |
| model sha256 | dc4303bca26256c56e5cb83222e898a09a5244472f7fd092b425cc2b7568fe19 |
| CT sha256 | a9efa740abc41299efa83607a0880012ac8dcc8df7db60259c2a7e96f42cd94f |
| generator | tools/usdm-rdf-gen/generate.py v0.2.0 |
| output | ontology/vendor/usdm/usdm-v4.ttl |
| output sha256 | 424e3a433e0e7dee3cfb67bf325fe1b4a81b42789f3f4fa2fcc5a56c401d7d14 |
| classes | 81 |
| properties | 783 |
| NCIt anchors | 317 |
| license | CC-BY-4.0 (mirrors DDF-RA source) |

Regenerate: `python3 tools/usdm-rdf-gen/extract_ct.py && python3 tools/usdm-rdf-gen/generate.py` (byte-reproducible).
