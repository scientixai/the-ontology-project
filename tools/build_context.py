#!/usr/bin/env python3
"""
TOP build_context.py
Reads a JSON intermediate that describes the OOUX-derived ontology and emits a JSON-LD
@context file (NGSI-LD compatible) for the reference graph.

Stdlib only. No pip installs. Unzip and run.

Usage:
  python tools/build_context.py source/top-strawman.json contexts/clinical-trials-context.jsonld

Federation pattern:
  - Top-level objects and their sub-objects use the clinical-trials prefix (default "top").
  - Cross-cutting horizontals use the commons prefix (default "topc"), so when other functional
    graphs (CMC, drug discovery, regulatory, etc.) are added later, they import the same
    commons context for shared concepts (Document, Person, Audit Trail Entry, etc.).
"""

import json
import sys
from pathlib import Path

NGSI_LD_CORE = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"

DEFAULT_NAMESPACES = {
    "top":    "https://top.scientix.ai/onto/clinical/v1#",
    "topc":   "https://top.scientix.ai/onto/commons/v1#",
    "fhir":   "http://hl7.org/fhir/",
    "usdm":   "https://www.cdisc.org/standards/usdm/v3#",
    "cdash":  "https://www.cdisc.org/standards/cdashig/v2-1#",
    "sdtm":   "https://www.cdisc.org/standards/sdtmig/v3-4#",
    "ncit":   "http://purl.obolibrary.org/obo/NCIT_",
    "snomed": "http://snomed.info/sct/",
    "loinc":  "http://loinc.org/",
    "prov":   "http://www.w3.org/ns/prov#",
    "skos":   "http://www.w3.org/2004/02/skos/core#",
    "owl":    "http://www.w3.org/2002/07/owl#",
    "xsd":    "http://www.w3.org/2001/XMLSchema#",
    "ngsi-ld": "https://uri.etsi.org/ngsi-ld/"
}


def emit_class(name, prefix, crosswalks):
    """Emit one JSON-LD class term, with cross-walks as owl:equivalentClass annotations."""
    term = {
        "@id": f"{prefix}:{name}",
        "@type": "@id"
    }
    equiv = []
    for std, target in (crosswalks or {}).items():
        if target:
            equiv.append({"@id": target})
    if equiv:
        term["owl:equivalentClass"] = equiv
    return term


def emit_attribute(name, prefix, attr_type):
    """Emit one JSON-LD property term with optional XSD type."""
    term = {"@id": f"{prefix}:{name}"}
    if attr_type and attr_type.startswith("xsd:"):
        term["@type"] = attr_type
    return term


def emit_relationship(name, prefix):
    """Emit one JSON-LD relationship term (NGSI-LD style: @type @id)."""
    return {"@id": f"{prefix}:{name}", "@type": "@id"}


def check_no_polysemous_verbs(source):
    """Fail loudly when a focus class has two relationships (or two attributes) with
    the same name. JSON-LD @context maps each term to one definition; SHACL property
    paths must be unambiguous. Two predicates with the same name and different targets
    on the same class silently overwrite at emission time and corrupt the artifacts.
    Catch it before we emit, not after.

    Each polysemous verb must be split (e.g. publishes -> publishesDocument,
    publishesPublication) so each predicate carries one target type. This is the path
    USDM and FHIR took; it preserves clean one-pass projection from TOP into either
    standard without query-time gymnastics.
    """
    issues = []

    def check_class(cls, scope_label):
        seen_attrs = {}
        for attr in cls.get("attributes", []):
            n = attr.get("name")
            if n in seen_attrs:
                issues.append(f"{scope_label} {cls.get('id')}: duplicate attribute '{n}'")
            seen_attrs[n] = True

        seen_rels = {}
        for rel in cls.get("relationships", []):
            n = rel.get("name")
            target = rel.get("target")
            if n in seen_rels:
                prior_target = seen_rels[n]
                issues.append(
                    f"{scope_label} {cls.get('id')}: polysemous verb '{n}' fires against "
                    f"both '{prior_target}' and '{target}'. Split into "
                    f"'{n}{prior_target}' and '{n}{target}' so each predicate carries one target type."
                )
            seen_rels[n] = target

    for tlo in source.get("top_levels", []):
        check_class(tlo, "top-level")
        for sub in tlo.get("sub_objects", []):
            check_class(sub, "sub-object")
    for h in source.get("horizontals", []):
        check_class(h, "horizontal")

    if issues:
        msg = "Source intermediate has polysemous verbs (will corrupt emission):\n  - " + "\n  - ".join(issues)
        raise ValueError(msg)


def build(source):
    """Build a JSON-LD @context document from a TOP intermediate."""
    check_no_polysemous_verbs(source)
    namespaces = dict(DEFAULT_NAMESPACES)
    namespaces.update(source.get("namespaces", {}))

    inner = {}
    inner.update(namespaces)

    cls_prefix = source.get("prefix", "top")
    hor_prefix = source.get("horizontal_prefix", cls_prefix)

    for tlo in source.get("top_levels", []):
        inner[tlo["id"]] = emit_class(tlo["id"], cls_prefix, tlo.get("crosswalks"))
        for attr in tlo.get("attributes", []):
            inner[attr["name"]] = emit_attribute(attr["name"], cls_prefix, attr.get("type"))
        for rel in tlo.get("relationships", []):
            inner[rel["name"]] = emit_relationship(rel["name"], cls_prefix)
        for sub in tlo.get("sub_objects", []):
            inner[sub["id"]] = emit_class(sub["id"], cls_prefix, sub.get("crosswalks"))
            for attr in sub.get("attributes", []):
                inner[attr["name"]] = emit_attribute(attr["name"], cls_prefix, attr.get("type"))

    for h in source.get("horizontals", []):
        inner[h["id"]] = emit_class(h["id"], hor_prefix, h.get("crosswalks"))
        for attr in h.get("attributes", []):
            inner[attr["name"]] = emit_attribute(attr["name"], hor_prefix, attr.get("type"))

    return {
        "@context": [NGSI_LD_CORE, inner],
        "_meta": {
            "source_version": source.get("version", "unspecified"),
            "top_levels": [t["id"] for t in source.get("top_levels", [])],
            "horizontals": [h["id"] for h in source.get("horizontals", [])]
        }
    }


def main():
    if len(sys.argv) != 3:
        print("usage: build_context.py <source.json> <output.jsonld>", file=sys.stderr)
        sys.exit(2)

    src_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    src = json.loads(src_path.read_text())
    out = build(src)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {out_path}")
    print(f"  top-levels: {', '.join(out['_meta']['top_levels'])}")
    print(f"  horizontals: {', '.join(out['_meta']['horizontals'])}")


if __name__ == "__main__":
    main()
