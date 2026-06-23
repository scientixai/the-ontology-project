#!/usr/bin/env python3
"""Deterministic USDM v4.0 controlled-terminology -> SKOS generator (TOP-owned).

Renders the DDF valid value sets (from the vendored usdm_ct.json) as SKOS concept
schemes: one skos:ConceptScheme per codelist (bound to the usdm property it constrains,
NCIt-anchored), and one skos:Concept per permissible value (prefLabel, definition,
NCIt-anchored). Byte-reproducible (sorted). CC-BY-4.0 (mirrors the DDF-RA CT source).

Run:  python3 tools/usdm-rdf-gen/generate_ct.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CT = json.load(open(os.path.join(HERE, "ddf-ra-v4.0.0", "usdm_ct.json")))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "ontology", "vendor", "usdm", "usdm-ct-v4.ttl"))

NS = "https://w3id.org/cdisc/usdm/v4/"
CTNS = "https://w3id.org/cdisc/usdm/v4/ct/"
NCIT = "http://purl.obolibrary.org/obo/NCIT_"


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def main():
    codelists = CT["codelists"]
    # dedupe concepts across codelists; track which schemes each appears in
    concepts = {}
    for cl in sorted(codelists):
        for v in codelists[cl]["values"]:
            c = concepts.setdefault(v["ccode"], {"pref": v["pref"], "defn": v["defn"], "schemes": set()})
            c["schemes"].add(cl)

    lines = []
    w = lines.append
    w("@prefix ct:   <%s> ." % CTNS)
    w("@prefix usdm: <%s> ." % NS)
    w("@prefix skos: <http://www.w3.org/2004/02/skos/core#> .")
    w("@prefix owl:  <http://www.w3.org/2002/07/owl#> .")
    w("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    w("")
    w("<%s> a owl:Ontology ;" % CTNS)
    w('    rdfs:label "CDISC USDM v4.0 controlled terminology (SKOS)" ;')
    w('    rdfs:comment "The DDF valid value sets rendered as SKOS concept schemes, generated '
      'from USDM_CT.xlsx (tag v4.0.0). One scheme per codelist (bound to the usdm property it '
      'constrains), one concept per permissible value, all NCIt-anchored. A mechanical '
      'projection of CDISC\'s controlled terminology — NOT authoritative. CC-BY-4.0." .')
    w("")
    w("#" * 70)
    w("# %d codelists (concept schemes), %d distinct values (concepts)." % (len(codelists), len(concepts)))
    w("#" * 70)

    for cl in sorted(codelists):
        info = codelists[cl]
        binding = "%s.%s" % (info["entity"], info["attr"])
        prop = "usdm:%s-%s" % (info["entity"], info["attr"])
        w("")
        w("ct:%s a skos:ConceptScheme ;" % cl)
        w('    rdfs:label "%s value set" ;' % esc(binding))
        w('    skos:prefLabel "%s" ;' % esc(binding))
        w("    skos:exactMatch <%s%s> ;" % (NCIT, cl))
        w("    rdfs:seeAlso %s ;" % prop)
        w('    rdfs:comment "Valid values for usdm:%s." .' % esc(binding))

    w("")
    w("#" * 70)
    w("# Concepts (permissible values)")
    w("#" * 70)
    for c in sorted(concepts):
        rec = concepts[c]
        schemes = ", ".join("ct:%s" % s for s in sorted(rec["schemes"]))
        parts = ["a skos:Concept",
                 'skos:prefLabel "%s"' % esc(rec["pref"]),
                 "skos:inScheme %s" % schemes,
                 "skos:exactMatch <%s%s>" % (NCIT, c)]
        if rec["defn"]:
            parts.append('skos:definition "%s"' % esc(rec["defn"]))
        w("")
        w("ct:%s %s ." % (c, " ;\n    ".join(parts)))

    out = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(out)
    print("wrote %s: %d schemes, %d concepts" % (OUT, len(codelists), len(concepts)))


if __name__ == "__main__":
    main()
