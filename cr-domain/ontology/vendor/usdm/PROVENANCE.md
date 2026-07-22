# Vendored artifact provenance — USDM v4.0 OWL

Generated, **not authoritative**. The authoritative USDM source is CDISC DDF-RA.

**Namespace status (`https://w3id.org/cdisc/usdm/v4/`).** CDISC has **no ratified
official USDM-RDF**; the RDF representation is a community effort (championed by
Kerstin Forsberg / the CDISC-RDF lineage), and the `w3id.org/cdisc/usdm/` namespace
is that **community convention**, not an official CDISC artifact.

**Canonical community artifact: `github.com/kerfors/usdm-rdf`** (Kerstin Forsberg) —
the w3id namespace's registered target. Verified aligned with this vendored file:
same namespace `w3id.org/cdisc/usdm/v4/`, same `{Class}-{attribute}` property IRI
scheme (e.g. `usdm:Administration-dose`, `usdm:BiomedicalConcept-code`), same DDF-RA
source, same CC-BY-4.0 license. Her repo additionally ships a JSON-LD 1.1 context and
SHACL shapes (`usdm_v4.shapes.ttl`, `usdm_v4.shapes-ct.ttl`) this file does not.

**Recommended path: consume hers, don't maintain a parallel rendering.** This file was
generated locally from DDF-RA (below) and happens to match her IRIs — but two renderings
at one namespace is a latent drift risk. The clean move is to **vendor `kerfors/usdm-rdf`
at a pinned release (sha-pinned) as the source of truth**, inherit her shapes + JSON-LD
context, and retire our generator — making TOP an adopter of the canonical community
artifact rather than a parallel author. Her repo is draft / not-yet-normative, so keep
the pin explicit and re-verify on each of her releases.

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
