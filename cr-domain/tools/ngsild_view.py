#!/usr/bin/env python3
"""Resolve a SHACL retrieval-view into a single, self-contained NGSI-LD entity.

The point this proves: an operator can pull ONE entity and get every fact the
green check needs, with NO recursive lookups by the UI. The *shape*
(views/blood-draw-admissibility.ttl) declares which linked entities inline and
how deep; this walker follows it over a worked example and emits exactly the
object a context broker returns for a shape-bounded `?join=inline` retrieval.

Usage:
  python3 cr-domain/tools/ngsild_view.py            # prints query + object
  python3 cr-domain/tools/ngsild_view.py --emit     # also writes docs/dist artifact

Truthful: every value comes from the TTL by graph traversal, nothing is hand-typed.
"""
import json
import os
import sys

from rdflib import Graph, RDF, RDFS, URIRef, Literal
from rdflib.namespace import SH

CR = "https://top.scientix.ai/cr/v1#"
TOP = "https://top.scientix.ai/core/v1#"
PROV = "http://www.w3.org/ns/prov#"
RDFVAL = "http://www.w3.org/1999/02/22-rdf-syntax-ns#value"
E = "https://top.scientix.ai/examples/"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE = os.path.join(ROOT, "examples", "blood-draw-context-conformant.ttl")
VIEW = os.path.join(ROOT, "views", "blood-draw-admissibility.ttl")
HUB = E + "bd-coll"
VIEW_SHAPE = CR + "BloodDrawAdmissibilityView"

# Predicates rendered as scalar NGSI-LD attributes (everything else that is a
# literal becomes a generic Property; relationships are followed only via the view).
# observedAt is the NGSI-LD core Temporal Property (valid time) and renders bare;
# recordedAt/status/identifier are DOMAIN properties and render as NGSI-LD
# Properties. (NGSI-LD `createdAt`/`modifiedAt` are broker-assigned system attrs
# surfaced by ?options=sysAttrs — they are NOT our transaction time, so we do not
# masquerade recordedAt as createdAt.)
SCALAR_LABEL = {
    str(RDFS.label): "name",
    TOP + "status": "status",
    TOP + "identifier": "identifier",
    TOP + "observedAt": "observedAt",
    TOP + "recordedAt": "recordedAt",
    RDFVAL: "value",
    CR + "toState": "custodyState",
    CR + "fromState": "fromState",
}


def _ln(uri):
    return str(uri).split("#")[-1].split("/")[-1]


def _urn(uri):
    return "urn:" + _ln(uri)


def _types(g, node):
    return [t for t in g.objects(node, RDF.type) if isinstance(t, URIRef)]


def _primary_type(g, node):
    skip = {"ProvenancedEntity", "Observation", "Temporal", "Evidence", "Outcome", "Constraint"}
    names = [_ln(t) for t in _types(g, node)]
    pref = [n for n in names if n not in skip]
    return (pref or names or ["Entity"])[0]


def _scalars(g, node):
    """All literal facts on the node, as NGSI-LD attributes."""
    d = {"id": _urn(node), "type": _primary_type(g, node)}
    for p, o in sorted(g.predicate_objects(node), key=lambda po: str(po[0])):
        if not isinstance(o, Literal):
            continue
        key = SCALAR_LABEL.get(str(p))
        if key == "observedAt":
            d[key] = str(o)            # NGSI-LD core Temporal Property — renders bare
        elif key:
            d[key] = {"type": "Property", "value": str(o)}
        # unmapped literals are intentionally dropped to keep the object tight
    return d


def _view_props(g, shape):
    """The (path, subShape) expansions a view declares, in declared order."""
    out = []
    for prop in g.objects(shape, SH.property):
        path = g.value(prop, SH.path)
        inverse = g.value(path, SH.inversePath) if path is not None else None
        pred = inverse if inverse is not None else path
        sub = g.value(prop, SH["node"])
        name = g.value(prop, SH.name)
        key = str(name) if name is not None else _ln(pred)
        out.append((pred, inverse is not None, sub, key))
    return out


def expand(g, sg, node, shape, depth=0):
    """Render `node` as an NGSI-LD entity, inlining linked entities per `shape`."""
    obj = _scalars(g, node)
    for pred, is_inverse, sub, attr in _view_props(sg, shape):
        targets = list(g.subjects(pred, node)) if is_inverse else list(g.objects(node, pred))
        if not targets:
            continue
        rendered = []
        for t in sorted(targets, key=str):
            ref = {"type": "Relationship", "object": _urn(t)}
            if sub is not None:
                ref["entity"] = expand(g, sg, t, sub, depth + 1)
            rendered.append(ref)
        obj[attr] = rendered[0] if len(rendered) == 1 else rendered
    return obj


def build():
    g = Graph().parse(EXAMPLE, format="turtle")
    sg = Graph().parse(VIEW, format="turtle")
    return expand(g, sg, URIRef(HUB), URIRef(VIEW_SHAPE))


QUERY = """\
GET /ngsi-ld/v1/entities/urn:bd-coll?join=inline&joinLevel=3
Accept: application/ld+json
Link: <https://top.scientix.ai/cr/v1/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"

# ETSI GS CIM 009 Linked Entity Retrieval: join=inline embeds each linked Entity
# as the `entity` sub-attribute of its Relationship (clause 4.5.23.2, Table
# 5.2.6-2); joinLevel=3 follows relationships forward to depth 3 (clause 4.5.23.1
# — forward, via each Relationship's `object`). Every fact is forward-reachable
# from the collection act, so this is ONE stock-broker call, no recursive lookups.
# cr:BloodDrawAdmissibilityView is the attribute projection (the `pick`/`attrs`
# the screen consumes) over that forward neighbourhood."""


def main():
    obj = build()
    print(QUERY)
    print()
    print(json.dumps(obj, indent=2))
    if "--emit" in sys.argv:
        out_dir = os.path.join(ROOT, "docs", "dist")
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "blood-draw-admissibility.ngsild.json"), "w") as f:
            json.dump(obj, f, indent=2)
            f.write("\n")
        print("\n# wrote docs/dist/blood-draw-admissibility.ngsild.json", file=sys.stderr)


if __name__ == "__main__":
    main()
