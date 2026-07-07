#!/usr/bin/env python3
"""Build TOP Core v1 as a versioned, checksummed, consumable artifact.

Merges core/v1/modules/*.ttl into one self-describing artifact, stamps it with
masthead metadata, and serializes it to three byte-reproducible formats
(Turtle, JSON-LD, N-Triples). Also bundles the Core SHACL shapes
(shapes.ttl + shapes/*.ttl) as their own artifact. Emits SHA256SUMS so
domain repositories can PIN the exact Core release they build against —
the mechanical prerequisite for the hub-and-spoke topology (ADR-0023).

Outputs to core/v1/dist/. Run: python3 core/v1/build_core_dist.py
Reuses the deterministic-serialization discipline of cr-domain/docs/build_dist.py.
"""
import glob
import hashlib
import json
import os

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.compare import to_canonical_graph
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD

V1 = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(V1, "dist")

MAST = dict(
    title="TOP Core",
    version="v1",
    namespace="https://top.scientix.ai/v1#",
    ontology_iri="https://top.scientix.ai/v1",
    version_iri="https://top.scientix.ai/v1/core-v1",
    license_label="Apache-2.0",
    license_iri="https://www.apache.org/licenses/LICENSE-2.0",
    creator="ScientixAI",
    publisher="ScientixAI",
    issued="2026-07-07",
    cite_as="ScientixAI (2026). TOP Core (v1). The Ontology Project.",
    description=("The universal foundation of The Ontology Project: one root "
                 "(top:CommonEntity), eight Category-Level Objects, the Universal DNA "
                 "(identifier / observedAt / status), the ADR-0021 bitemporal vocabulary, "
                 "and the ADR-0019 extension-flavor contract. Domain reference graphs "
                 "(e.g. TOP-CR) specialize this artifact and pin it by checksum."),
)


def _merge(patterns):
    g = Graph()
    for pat in patterns:
        for f in sorted(glob.glob(os.path.join(V1, pat))):
            g.parse(f, format="turtle")
    return g


def _stamp(g):
    onto = URIRef(MAST["ontology_iri"])
    g.add((onto, RDF.type, OWL.Ontology))
    g.add((onto, RDFS.label, Literal(MAST["title"])))
    g.add((onto, OWL.versionInfo, Literal(MAST["version"])))
    g.add((onto, OWL.versionIRI, URIRef(MAST["version_iri"])))
    g.add((onto, DCTERMS.title, Literal(MAST["title"])))
    g.add((onto, DCTERMS.description, Literal(MAST["description"])))
    g.add((onto, DCTERMS.license, URIRef(MAST["license_iri"])))
    g.add((onto, DCTERMS.creator, Literal(MAST["creator"])))
    g.add((onto, DCTERMS.publisher, Literal(MAST["publisher"])))
    g.add((onto, DCTERMS.issued, Literal(MAST["issued"], datatype=XSD.date)))
    g.add((onto, DCTERMS.bibliographicCitation, Literal(MAST["cite_as"])))
    return g


def _bind(g):
    g.bind("top", Namespace("https://top.scientix.ai/v1#"))
    g.bind("prov", Namespace("http://www.w3.org/ns/prov#"))
    g.bind("bfo", Namespace("http://purl.obolibrary.org/obo/bfo#"))
    g.bind("sh", Namespace("http://www.w3.org/ns/shacl#"))
    g.bind("dcterms", DCTERMS)
    g.bind("owl", OWL)


def _canonical(g):
    canon = to_canonical_graph(g)
    assert len(canon) == len(g), f"canonicalization changed triple count: {len(g)} -> {len(canon)}"
    cg = Graph()
    for t in canon:
        cg.add(t)
    _bind(cg)
    return cg


def _norm_json(x):
    if isinstance(x, list):
        return sorted((_norm_json(i) for i in x), key=lambda v: json.dumps(v, sort_keys=True))
    if isinstance(x, dict):
        return {k: _norm_json(v) for k, v in x.items()}
    return x


def _write(g, base):
    cg = _canonical(g)
    cg.serialize(destination=os.path.join(DIST, f"{base}.ttl"), format="turtle")
    lines = sorted(l for l in cg.serialize(format="nt").splitlines() if l.strip())
    with open(os.path.join(DIST, f"{base}.nt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    doc = _norm_json(json.loads(cg.serialize(format="json-ld")))
    with open(os.path.join(DIST, f"{base}.jsonld"), "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True)
        fh.write("\n")


def write_checksums():
    names = sorted(
        f for f in os.listdir(DIST)
        if os.path.isfile(os.path.join(DIST, f)) and f != "SHA256SUMS"
    )
    lines = []
    for name in names:
        with open(os.path.join(DIST, name), "rb") as fh:
            lines.append(f"{hashlib.sha256(fh.read()).hexdigest()}  {name}")
    with open(os.path.join(DIST, "SHA256SUMS"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(names)


def build():
    os.makedirs(DIST, exist_ok=True)

    core = _merge(["modules/*.ttl"])
    _stamp(core)
    _bind(core)
    _write(core, "top-core-v1")

    shapes = _merge(["shapes.ttl", "shapes/*.ttl"])
    _bind(shapes)
    _write(shapes, "top-core-shapes-v1")

    print(f"Wrote serializations to {DIST}/")
    for base, n in (("top-core-v1", len(core)), ("top-core-shapes-v1", len(shapes))):
        print(f"  {base}.{{ttl,jsonld,nt}}  ({n} triples)")
    n = write_checksums()
    print(f"  SHA256SUMS  ({n} artifacts pinned for domain consumers)")


if __name__ == "__main__":
    build()
