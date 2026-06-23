#!/usr/bin/env python3
"""Deterministic USDM v4.0 -> OWL generator (TOP-owned).

Reads the pinned CDISC DDF-RA OpenAPI model (USDM_API.json) and emits a faithful
structural OWL rendering of the USDM v4.0 class model: one owl:Class per entity,
class-scoped owl:Object/DatatypeProperty per attribute, and owl:Restriction
cardinality derived from the schema (required / nullable / array). The mapping is
mechanical, not semantic (cf. the community usdm-rdf project) — so the artifact
regenerates byte-for-byte on each USDM release and TOP never hand-owns USDM.

Output is byte-reproducible: classes and properties are emitted in sorted order.
Scope (v1): structure only. NCIt anchoring from USDM_CT.xlsx is a follow-up.

Run:  python3 tools/usdm-rdf-gen/generate.py
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "ddf-ra-v4.0.0", "USDM_API.json")
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "ontology", "vendor", "usdm", "usdm-v4.ttl"))
PROV = os.path.normpath(os.path.join(HERE, "..", "..", "ontology", "vendor", "usdm", "PROVENANCE.md"))

NS = "https://w3id.org/cdisc/usdm/v4/"
DDF_RA_TAG = "v4.0.0"
DDF_RA_COMMIT = "aa303cb32f5d3ceecc68a16803e26720d2c1fc26"
GEN_VERSION = "0.1.0"

XSD = {"string": "xsd:string", "integer": "xsd:integer", "number": "xsd:decimal",
       "boolean": "xsd:boolean"}


def cls_name(schema_name):
    """Strip the -Output suffix to get the bare class name."""
    return schema_name[:-7] if schema_name.endswith("-Output") else schema_name


def resolve(pv):
    """Classify a property -> (kind, range, multi) where kind is 'obj'|'dat'.
    range is a class name (obj) or an xsd type (dat); multi True if array-valued."""
    if "$ref" in pv:
        return "obj", cls_name(pv["$ref"].split("/")[-1]), False
    if pv.get("type") == "array":
        items = pv.get("items", {})
        if "$ref" in items:
            return "obj", cls_name(items["$ref"].split("/")[-1]), True
        return "dat", XSD.get(items.get("type", "string"), "xsd:string"), True
    if "anyOf" in pv:  # nullable scalar — take the first non-null member
        for m in pv["anyOf"]:
            if m.get("type") and m["type"] != "null":
                return "dat", XSD.get(m["type"], "xsd:string"), False
        return "dat", "xsd:string", False
    if "type" in pv:
        return "dat", XSD.get(pv["type"], "xsd:string"), False
    return "dat", "xsd:string", False


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def generate(spec):
    schemas = spec["components"]["schemas"]
    classes = sorted(cls_name(s) for s in schemas if s.endswith("-Output"))
    known = set(classes)
    lines = []
    w = lines.append

    w("@prefix usdm: <%s> ." % NS)
    w("@prefix owl:  <http://www.w3.org/2002/07/owl#> .")
    w("@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    w("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    w("@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .")
    w("")
    w("<%s> a owl:Ontology ;" % NS)
    w('    rdfs:label "CDISC USDM v4.0 (generated)" ;')
    w('    owl:versionInfo "%s" ;' % spec["info"]["version"])
    w('    rdfs:comment "Structural OWL rendering of the CDISC Unified Study Definitions '
      'Model v4.0, generated deterministically from the DDF-RA OpenAPI model (tag %s). '
      'A mechanical projection of CDISC\'s model — NOT authoritative and NOT TOP-owned; '
      'the authoritative source is github.com/cdisc-org/DDF-RA. Crosswalked to TOP cr-core '
      'in crosswalks/. CC-BY-4.0 (mirrors the DDF-RA source)." .' % DDF_RA_TAG)
    w("")
    w("#" * 70)
    w("# %d classes, generated from USDM_API.json. Do not hand-edit." % len(classes))
    w("#" * 70)

    for c in classes:
        schema = schemas[c + "-Output"]
        required = set(schema.get("required", []))
        props = schema.get("properties", {})
        w("")
        w('usdm:%s a owl:Class ; rdfs:label "%s" .' % (c, c))
        for p in sorted(props):
            kind, rng, multi = resolve(props[p])
            piri = "usdm:%s-%s" % (c, p)
            ptype = "owl:ObjectProperty" if kind == "obj" else "owl:DatatypeProperty"
            rangeval = ("usdm:" + rng) if (kind == "obj" and rng in known) else (
                rng if kind == "dat" else "owl:Thing")
            w('%s a %s ; rdfs:domain usdm:%s ; rdfs:range %s ; rdfs:label "%s" .'
              % (piri, ptype, c, rangeval, esc(p)))
            # cardinality restriction (faithful to the schema)
            req = p in required
            if multi and req:
                restr = "owl:minCardinality 1"
            elif multi:
                restr = None  # 0..* — no restriction
            elif req:
                restr = "owl:cardinality 1"
            else:
                restr = "owl:maxCardinality 1"
            if restr:
                w('usdm:%s rdfs:subClassOf [ a owl:Restriction ; owl:onProperty %s ; %s ] .'
                  % (c, piri, restr))
    return "\n".join(lines) + "\n", len(classes)


def main():
    raw = open(SRC, "rb").read()
    spec = json.loads(raw)
    ttl, nclasses = generate(spec)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(ttl)
    src_sha = hashlib.sha256(raw).hexdigest()
    out_sha = hashlib.sha256(ttl.encode()).hexdigest()
    nprops = ttl.count(" a owl:ObjectProperty") + ttl.count(" a owl:DatatypeProperty")
    with open(PROV, "w") as f:
        f.write(
            "# Vendored artifact provenance — USDM v4.0 OWL\n\n"
            "Generated, **not authoritative**. The authoritative USDM source is CDISC DDF-RA.\n\n"
            "| field | value |\n|---|---|\n"
            "| source | github.com/cdisc-org/DDF-RA `Deliverables/API/USDM_API.json` |\n"
            "| pinned tag | %s |\n| pinned commit | %s |\n"
            "| source sha256 | %s |\n"
            "| generator | tools/usdm-rdf-gen/generate.py v%s |\n"
            "| output | ontology/vendor/usdm/usdm-v4.ttl |\n"
            "| output sha256 | %s |\n"
            "| classes | %d |\n| properties | %d |\n"
            "| license | CC-BY-4.0 (mirrors DDF-RA source) |\n\n"
            "Regenerate: `python3 tools/usdm-rdf-gen/generate.py` (byte-reproducible).\n"
            % (DDF_RA_TAG, DDF_RA_COMMIT, src_sha, GEN_VERSION, out_sha, nclasses, nprops))
    print("wrote %s: %d classes, %d properties" % (OUT, nclasses, nprops))
    print("output sha256:", out_sha)


if __name__ == "__main__":
    main()
