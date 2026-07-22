#!/usr/bin/env python3
"""Generate the exhaustive USDM structural menu as entity views.

The Protocol object is, in operator terms, USDM. So its page must be able to
expose the ENTIRETY of USDM and let the operator pick — the viewer must not
limit them. This renders the vendored CDISC USDM v4 OWL
(ontology/vendor/usdm/usdm-v4.ttl, adopted from kerfors/usdm-rdf — see
ontology/vendor/usdm/PROVENANCE.md) into the same reference
entity-view pattern as the OOUX corpus:

  * one cr:USDM_<Class>EntityView per USDM class
  * datatype properties -> attributes (identity set = id + name/label)
  * object properties    -> pointers (sh:node) to the range class's view
  * cardinality           -> native SHACL, read from the USDM owl:Restrictions

It also links cr:ProtocolEntityView -> the USDM root via cr:usdmProjection, so
the Protocol page can traverse the whole model. USDM is a mechanical projection
of CDISC's model (CC-BY-4.0, not TOP-owned); this is a reference recipe over it,
not a runtime dependency. Deterministic: same vendored OWL in, same TTL out.

    python3 cr-domain/tools/gen_usdm_views.py
"""
import os

from rdflib import Graph, OWL, RDF, RDFS, URIRef, Namespace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USDM_TTL = os.path.join(ROOT, "ontology", "vendor", "usdm", "usdm-v4.ttl")
OUT = os.path.join(ROOT, "views", "entity", "usdm.ttl")
USDM = Namespace("https://w3id.org/cdisc/usdm/v4/")
XSD = "http://www.w3.org/2001/XMLSchema#"
# The USDM root an operator lands on from a Protocol.
ROOT_CLASS = "StudyDefinitionDocument"
IDENT_LABELS = {"id", "name", "label", "instanceType"}

HEADER = """\
# ---------------------------------------------------------------------------
# USDM STRUCTURAL MENU — the entirety of CDISC USDM v4.0 as reference entity
# views (generated — do not edit by hand).
# Source: ontology/vendor/usdm/usdm-v4.ttl (adopted from kerfors/usdm-rdf, the
#   canonical community USDM-RDF — see vendor/usdm/PROVENANCE.md). Generator: tools/gen_usdm_views.py
#
# The Protocol object IS USDM in operator terms, so its page must be able to
# expose ALL of USDM and let the operator pick — the viewer must not limit them.
# Every USDM class is one cr:USDM_<Class>EntityView; object properties are
# pointers, datatype properties are attributes, cardinality is native SHACL read
# from the USDM owl:Restrictions. cr:ProtocolEntityView projects into the root.
#
# REFERENCE, NOT RUNTIME. A recipe over CDISC's (CC-BY-4.0) model, carrying no
# prominence or arrangement. See the entity-view ADR and RFC 0001.
# ---------------------------------------------------------------------------
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix cr:   <https://top.scientix.ai/cr/v1#> .
@prefix usdm: <https://w3id.org/cdisc/usdm/v4/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

"""


def local(uri):
    return str(uri).split("#")[-1].split("/")[-1]


def esc(s):
    return (s or "").replace("\\", "\\\\").replace('"', '\\"')


def restrictions(g, cls):
    """propIRI -> (minCount, maxCount) from the class's owl:Restrictions."""
    out = {}
    for r in g.objects(cls, RDFS.subClassOf):
        p = g.value(r, OWL.onProperty)
        if p is None:
            continue
        card = g.value(r, OWL.cardinality) or g.value(r, OWL.qualifiedCardinality)
        mn = g.value(r, OWL.minCardinality) or g.value(r, OWL.minQualifiedCardinality)
        mx = g.value(r, OWL.maxCardinality) or g.value(r, OWL.maxQualifiedCardinality)
        if card is not None:
            out[p] = (int(card), int(card))
        else:
            out[p] = (int(mn) if mn is not None else None,
                      int(mx) if mx is not None else None)
    return out


def main():
    g = Graph().parse(USDM_TTL, format="turtle")
    classes = sorted((c for c in g.subjects(RDF.type, OWL.Class)
                      if str(c).startswith(str(USDM))), key=local)
    class_set = set(classes)

    def view_iri(cls):
        return f"cr:USDM_{local(cls)}EntityView"

    blocks = [HEADER]
    n_attr = n_ptr = 0
    for c in classes:
        props = sorted(
            (p for p in g.subjects(RDFS.domain, c)
             if isinstance(p, URIRef) and str(p).startswith(str(USDM))),
            key=local)
        cards = restrictions(g, c)
        comment = g.value(c, RDFS.comment)
        rows_attr, rows_ptr = [], []
        picked_id, picked_label = False, False
        for p in props:
            plabel = str(g.value(p, RDFS.label) or local(p))
            rng = g.value(p, RDFS.range)
            mn, mx = cards.get(p, (None, None))
            is_obj = (p, RDF.type, OWL.ObjectProperty) in g and rng in class_set
            seg = [f"sh:path usdm:{local(p)}", f'sh:name "{esc(plabel)}"']
            if is_obj:
                seg.append(f"sh:node {view_iri(rng)}")
            else:
                if rng is not None and str(rng).startswith(XSD):
                    seg.append(f"sh:datatype xsd:{local(rng)}")
            if mn is not None:
                seg.append(f"sh:minCount {mn}")
            if mx is not None:
                seg.append(f"sh:maxCount {mx}")
            # identity: the id, plus the first of name/label
            if not is_obj and plabel == "id" and not picked_id:
                seg.append("cr:isIdentity true"); picked_id = True
            elif not is_obj and plabel in ("name", "label") and not picked_label:
                seg.append("cr:isIdentity true"); picked_label = True
            (rows_ptr if is_obj else rows_attr).append(seg)
        # guarantee a non-empty identity set
        if not picked_id and not picked_label and rows_attr:
            rows_attr[0].append("cr:isIdentity true")
        n_attr += len(rows_attr); n_ptr += len(rows_ptr)

        head = [f"{view_iri(c)} a sh:NodeShape, cr:EntityView ;",
                f"    sh:targetClass usdm:{local(c)} ;",
                f'    rdfs:label "{esc(local(c))}" ;']
        if comment:
            head.append(f'    rdfs:comment "{esc(str(comment))}" ;')
        all_rows = rows_attr + rows_ptr
        body = []
        for i, seg in enumerate(all_rows):
            term = " ." if i == len(all_rows) - 1 else " ;"
            body.append(f"    sh:property [ {' ; '.join(seg)} ]{term}")
        if not all_rows:
            head[-1] = head[-1].rstrip(" ;") + " ."
        blocks.append("\n".join(head + body) + "\n")

    # link Protocol -> the USDM root so the Protocol page can traverse all of USDM
    blocks.append(
        "# The Protocol object projects into the entirety of USDM from this root.\n"
        f"cr:ProtocolEntityView cr:usdmProjection cr:USDM_{ROOT_CLASS}EntityView .\n")

    open(OUT, "w", encoding="utf-8").write("\n".join(blocks))
    print(f"USDM views: {len(classes)} classes  attributes: {n_attr}  pointers: {n_ptr}")
    print(f"-> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
