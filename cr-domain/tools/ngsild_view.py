#!/usr/bin/env python3
"""Resolve SHACL retrieval-views into single, self-contained NGSI-LD entities.

The point this proves, for every applicable operator screen: pull ONE entity and
get every fact the green check needs, with NO recursive lookups by the UI. A
*view* (views/*.ttl) declares which linked entities inline and how deep; this
walker follows it over a worked example and emits exactly the object a context
broker returns for a shape-bounded `?join=inline` retrieval.

Faithful to ETSI GS CIM 009 (NGSI-LD API) Linked Entity Retrieval:
  - join=inline embeds each linked Entity as the `entity` sub-attribute of its
    Relationship (clause 4.5.23.2, Table 5.2.6-2);
  - traversal follows a Relationship's `object` FORWARD only (clause 4.5.23.1) —
    so every view here uses forward paths, and the data carries forward edges.

Usage:
  python3 cr-domain/tools/ngsild_view.py                 # list views
  python3 cr-domain/tools/ngsild_view.py blood-draw      # print query + object
  python3 cr-domain/tools/ngsild_view.py --all           # every view

Truthful: every value comes from the TTL by graph traversal, nothing hand-typed.
"""
import glob
import json
import os
import sys

from rdflib import Graph, RDF, RDFS, URIRef, Literal
from rdflib.namespace import SH

CR = "https://top.scientix.ai/cr/v1#"
TOP = "https://top.scientix.ai/core/v1#"
RDFVAL = "http://www.w3.org/1999/02/22-rdf-syntax-ns#value"
E = "https://top.scientix.ai/examples/"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWS_DIR = os.path.join(ROOT, "views")

# name -> (example file, root entity localname, view NodeShape localname)
VIEWS = {
    "site-activation": ("site-activation-conformant.ttl", "act1", "SiteActivationView"),
    "delegation":      ("oncology-fih-conformant.ttl", "deleg-consent-001", "DelegationFullView"),
    "enrollment":      ("oncology-fih-conformant.ttl", "enroll-001", "EnrollmentView"),
    "consent":         ("oncology-fih-conformant.ttl", "consent-001", "ConsentView"),
    "blood-draw":      ("blood-draw-context-conformant.ttl", "bd-coll", "BloodDrawAdmissibilityView"),
    "edc":             ("edc-conformant.ttl", "obs1", "EDCObservationView"),
    "adverse-event":   ("oncology-fih-conformant.ttl", "ae-001", "AdverseEventView"),
    "eop2":            ("eop2-conformant.ttl", "eop2", "EOP2GateView"),
    "startup-package": ("startup-package-conformant.ttl", "sp-act", "StartupActivationView"),
}

# NGSI-LD system/core terms that render bare; everything else literal -> Property.
_OBSERVED_AT = TOP + "observedAt"


def _ln(uri):
    return str(uri).split("#")[-1].split("/")[-1]


def _urn(uri):
    return "urn:" + _ln(uri)


def _types(g, node):
    return [t for t in g.objects(node, RDF.type) if isinstance(t, URIRef)]


def _primary_type(g, node):
    skip = {"ProvenancedEntity", "Observation", "Temporal", "Evidence", "Outcome", "Constraint", "Agent"}
    names = [_ln(t) for t in _types(g, node)]
    pref = [n for n in names if n not in skip]
    return (pref or names or ["Entity"])[0]


def _scalars(g, node):
    """All literal facts on the node, as NGSI-LD attributes. observedAt is the
    core Temporal Property (renders bare); every other domain literal renders as
    a Property so the object is self-contained."""
    d = {"id": _urn(node), "type": _primary_type(g, node)}
    for p, o in sorted(g.predicate_objects(node), key=lambda po: str(po[0])):
        if not isinstance(o, Literal):
            continue
        ps = str(p)
        if ps == _OBSERVED_AT:
            d["observedAt"] = str(o)
        elif ps == str(RDFS.label):
            d["name"] = {"type": "Property", "value": str(o)}
        elif ps == RDFVAL:
            d["value"] = {"type": "Property", "value": str(o)}
        else:
            d[_ln(p)] = {"type": "Property", "value": str(o)}
    return d


def _view_props(sg, shape):
    """The (predicate, is_inverse, subShape, attrName) expansions a view declares."""
    out = []
    for prop in sg.objects(shape, SH.property):
        path = sg.value(prop, SH.path)
        inverse = sg.value(path, SH.inversePath) if path is not None else None
        pred = inverse if inverse is not None else path
        sub = sg.value(prop, SH["node"])
        name = sg.value(prop, SH.name)
        key = str(name) if name is not None else _ln(pred)
        out.append((pred, inverse is not None, sub, key))
    return out


def expand(g, sg, node, shape):
    """Render `node` as an NGSI-LD entity, inlining linked entities per `shape`."""
    obj = _scalars(g, node)
    for pred, is_inverse, sub, attr in _view_props(sg, shape):
        targets = list(g.subjects(pred, node)) if is_inverse else list(g.objects(node, pred))
        if not targets:
            continue
        rendered = []
        for t in sorted(targets, key=str):
            ref = {"type": "Relationship", "object": _urn(t)}
            if sub is not None and isinstance(t, URIRef):
                ref["entity"] = expand(g, sg, t, sub)
            rendered.append(ref)
        obj[attr] = rendered[0] if len(rendered) == 1 else rendered
    return obj


def _views_graph():
    sg = Graph()
    for f in sorted(glob.glob(os.path.join(VIEWS_DIR, "*.ttl"))):
        sg.parse(f, format="turtle")
    return sg


def build_view(name):
    example, root_ln, shape_ln = VIEWS[name]
    g = Graph().parse(os.path.join(ROOT, "examples", example), format="turtle")
    sg = _views_graph()
    return expand(g, sg, URIRef(E + root_ln), URIRef(CR + shape_ln))


# Back-compat for callers importing build()/QUERY (the blood-draw showcase).
def build():
    return build_view("blood-draw")


def query_for(name):
    _, root_ln, shape_ln = VIEWS[name]
    return (
        f"GET /ngsi-ld/v1/entities/{ _urn(URIRef(E + root_ln)) }?join=inline&joinLevel=3\n"
        f"Accept: application/ld+json\n"
        f'Link: <https://top.scientix.ai/cr/v1/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"\n'
        f"\n"
        f"# ETSI GS CIM 009 Linked Entity Retrieval: join=inline embeds each linked\n"
        f"# Entity as the `entity` sub-attribute of its Relationship (clause 4.5.23.2);\n"
        f"# joinLevel follows relationships FORWARD only (clause 4.5.23.1). Every fact\n"
        f"# is forward-reachable from this entity -> ONE stock-broker call, no recursive\n"
        f"# lookups. cr:{shape_ln} is the attribute projection (the `pick` the screen reads)."
    )


QUERY = ("GET /ngsi-ld/v1/entities/urn:bd-coll?join=inline&joinLevel=3\n"
         "Accept: application/ld+json\n"
         'Link: <https://top.scientix.ai/cr/v1/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"\n'
         "\n"
         "# ETSI GS CIM 009 Linked Entity Retrieval: join=inline embeds each linked Entity\n"
         "# as the `entity` sub-attribute of its Relationship (clause 4.5.23.2, Table\n"
         "# 5.2.6-2); joinLevel=3 follows relationships forward to depth 3 (clause 4.5.23.1\n"
         "# — forward, via each Relationship's `object`). Every fact is forward-reachable\n"
         "# from the collection act, so this is ONE stock-broker call, no recursive lookups.\n"
         "# cr:BloodDrawAdmissibilityView is the attribute projection (the `pick`/`attrs`\n"
         "# the screen consumes) over that forward neighbourhood.")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--all" in sys.argv:
        names = list(VIEWS)
    elif args:
        names = args
    else:
        print("views:", ", ".join(VIEWS))
        return
    for name in names:
        print("=" * 78)
        print(query_for(name))
        print()
        print(json.dumps(build_view(name), indent=2))
        print()


if __name__ == "__main__":
    main()
