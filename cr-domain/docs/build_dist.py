#!/usr/bin/env python3
"""Build the downloadable serializations (the 'rigor layer').

Merges the ontology modules into one self-describing artifact, stamps it with
masthead metadata (version / license / creator / namespace / cite-as), and
serializes it to the four canonical RDF formats. Also bundles the SHACL shapes
and the external crosswalks as their own artifacts.

Outputs to docs/dist/. Run: python3 cr-domain/docs/build_dist.py
Masthead constants here are the single source of truth, imported by build_docs.py.
"""
import glob
import hashlib
import json
import os

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.compare import to_canonical_graph
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "docs", "dist")

# ---- Masthead: the single source of truth for version / license / authorship ----
MAST = dict(
    title="TOP — Clinical Research Reference Graph",
    version="v1",
    namespace="https://top.scientix.ai/cr/v1#",
    ontology_iri="https://top.scientix.ai/cr/v1",
    license_label="Apache-2.0",
    license_iri="https://www.apache.org/licenses/LICENSE-2.0",
    creator="ScientixAI",
    contributor="TOP Clinical Research working group",
    publisher="ScientixAI",
    issued="2026-06-22",
    cite_as="ScientixAI (2026). TOP — Clinical Research Reference Graph (v1). The Ontology Project.",
    description=("An inheritable, provenance-native, bitemporal reference knowledge graph for the "
                 "clinical-research lifecycle (Pre-IND through End-of-Phase-2, plus site operations). "
                 "The founding domain of TOP (The Ontology Project)."),
    notice=("Includes an independent derivative adaptation of the ICH E6(R3) Good Clinical Practice "
            "Guideline (Step 4, 2025; Principles, Glossary, Annex 1) — paraphrased, not endorsed or "
            "sponsored by ICH, original copyright © ICH. TMF artifact types align by name to the DIA "
            "TMF Reference Model (licensed; no text reproduced). See the repository NOTICE file."),
)

# Published in three byte-reproducible formats: Turtle, JSON-LD, N-Triples.
# RDF/XML is deliberately NOT published: rdflib's RDF/XML serializer is not
# byte-reproducible (irreducible node ordering), which would defeat the SHA256SUMS
# pin and churn the repo on every rebuild. Turtle is OWL-complete and human-readable.


def _merge(globs):
    g = Graph()
    for pat in globs:
        for f in sorted(glob.glob(os.path.join(ROOT, pat))):
            g.parse(f, format="turtle")
    return g


def _stamp(g):
    """Add owl:Ontology masthead metadata so each serialization is self-describing."""
    onto = URIRef(MAST["ontology_iri"])
    g.add((onto, RDF.type, OWL.Ontology))
    g.add((onto, RDFS.label, Literal(MAST["title"])))
    g.add((onto, OWL.versionInfo, Literal(MAST["version"])))
    g.add((onto, OWL.versionIRI, URIRef(MAST["ontology_iri"])))
    g.add((onto, DCTERMS.title, Literal(MAST["title"])))
    g.add((onto, DCTERMS.description, Literal(MAST["description"])))
    g.add((onto, DCTERMS.license, URIRef(MAST["license_iri"])))
    g.add((onto, DCTERMS.creator, Literal(MAST["creator"])))
    g.add((onto, DCTERMS.contributor, Literal(MAST["contributor"])))
    g.add((onto, DCTERMS.publisher, Literal(MAST["publisher"])))
    g.add((onto, DCTERMS.issued, Literal(MAST["issued"], datatype=XSD.date)))
    g.add((onto, DCTERMS.bibliographicCitation, Literal(MAST["cite_as"])))
    g.add((onto, DCTERMS.rights, Literal(MAST["notice"])))
    return g


def _bind(g):
    g.bind("top", Namespace("https://top.scientix.ai/core/v1#"))
    g.bind("hcls", Namespace("https://top.scientix.ai/hcls/v1#"))
    g.bind("cr", Namespace("https://top.scientix.ai/cr/v1#"))
    g.bind("cx", Namespace("https://top.scientix.ai/crosswalk/v1#"))
    g.bind("prov", Namespace("http://www.w3.org/ns/prov#"))
    g.bind("dcterms", DCTERMS)
    g.bind("owl", OWL)


def _canonical(g):
    """Isomorphic copy with deterministic blank-node labels, prefixes rebound.

    Blank-node ids are otherwise random per parse (rdflib), making serializations
    differ byte-for-byte across builds. Canonicalizing fixes the labels; we assert
    the triple count is preserved (relabel only, no merge/loss)."""
    canon = to_canonical_graph(g)
    assert len(canon) == len(g), f"canonicalization changed triple count: {len(g)} -> {len(canon)}"
    cg = Graph()  # to_canonical_graph is read-only; copy into a bindable graph
    for triple in canon:
        cg.add(triple)
    _bind(cg)
    return cg


def _norm_json(x):
    """Recursively sort a JSON-LD document so array order is deterministic."""
    if isinstance(x, list):
        return sorted((_norm_json(i) for i in x), key=lambda v: json.dumps(v, sort_keys=True))
    if isinstance(x, dict):
        return {k: _norm_json(v) for k, v in x.items()}
    return x


def _write(g, base):
    """Serialize to the three byte-reproducible formats."""
    cg = _canonical(g)
    # Turtle — nests/labels deterministically once blank nodes are canonical.
    cg.serialize(destination=os.path.join(DIST, f"{base}.ttl"), format="turtle")
    # N-Triples — canonical blank nodes + sorted lines = stable bytes.
    lines = sorted(l for l in cg.serialize(format="nt").splitlines() if l.strip())
    with open(os.path.join(DIST, f"{base}.nt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    # JSON-LD — canonical blank nodes + recursively sorted keys/arrays.
    doc = _norm_json(json.loads(cg.serialize(format="json-ld")))
    with open(os.path.join(DIST, f"{base}.jsonld"), "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True)
        fh.write("\n")


# Prefixes the NGSI-LD @context exposes (domain terms compact against these).
NGSI_PREFIXES = {
    "top": "https://top.scientix.ai/core/v1#",
    "hcls": "https://top.scientix.ai/hcls/v1#",
    "cr": "https://top.scientix.ai/cr/v1#",
    "cx": "https://top.scientix.ai/crosswalk/v1#",
    "prov": "http://www.w3.org/ns/prov#",
}
# The NGSI-LD core context (brokers ship with it; referenced, not inlined).
NGSI_CORE = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.8.jsonld"
# Terms we deliberately DO NOT remap: they coincide with NGSI-LD core reserved
# terms and the coincidence is the intended alignment. top:observedAt IS the
# NGSI-LD core observedAt (valid time); rdf:value/id/type resolve to core too.
NGSI_RESERVED = {"observedAt", "value", "type", "id", "object", "createdAt", "modifiedAt"}


def build_ngsi_context(onto):
    """Emit an NGSI-LD @context: a term->IRI dictionary for the domain vocabulary,
    layered over the NGSI-LD core context. This is the broker-facing companion to the
    plain RDF/JSON-LD serialization (which stays as top-cr-v1.jsonld). Generic, not IP;
    entity *shaping* (Property/Relationship nodes) is downstream integration work."""
    def split(u):
        u = str(u)
        for pfx, ns in NGSI_PREFIXES.items():
            if u.startswith(ns):
                return pfx, u[len(ns):]
        return None, u

    terms = {}
    for s in onto.subjects(RDF.type, OWL.Class):
        if isinstance(s, URIRef):
            pfx, local = split(s)
            if pfx and local and local not in NGSI_RESERVED:
                terms[local] = f"{pfx}:{local}"
    for t in (OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, RDF.Property):
        for s in onto.subjects(RDF.type, t):
            if isinstance(s, URIRef):
                pfx, local = split(s)
                if pfx and local and local not in NGSI_RESERVED:
                    terms[local] = f"{pfx}:{local}"

    local_ctx = dict(NGSI_PREFIXES)
    local_ctx.update(dict(sorted(terms.items())))
    doc = {"@context": [NGSI_CORE, local_ctx]}
    path = os.path.join(DIST, "top-cr-v1.ngsi-context.jsonld")
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")
    return len(terms)


def write_checksums():
    """Emit SHA256SUMS over every published artifact so consumers can pin by checksum.

    Standard `sha256sum`-compatible format ('<hexdigest>  <filename>'), sorted by name.
    A downstream consumer pins these digests and
    verifies them on fetch, so 'valid here' means 'this exact released artifact'."""
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

    onto = _merge(["ontology/*.ttl"])
    _stamp(onto)
    _bind(onto)
    _write(onto, "top-cr-v1")
    n_terms = build_ngsi_context(onto)

    shapes = _merge(["shapes/*.ttl"])
    _bind(shapes)
    _write(shapes, "top-cr-shapes-v1")

    cross = _merge(["crosswalks/*.ttl"])
    _bind(cross)
    _write(cross, "top-cr-crosswalks-v1")

    print(f"Wrote serializations to {DIST}/")
    for base, n in (("top-cr-v1", len(onto)), ("top-cr-shapes-v1", len(shapes)),
                    ("top-cr-crosswalks-v1", len(cross))):
        print(f"  {base}.{{ttl,jsonld,nt}}  ({n} triples)")
    print(f"  top-cr-v1.ngsi-context.jsonld  (NGSI-LD @context, {n_terms} domain terms)")
    n_sums = write_checksums()
    print(f"  SHA256SUMS  ({n_sums} artifacts pinned for downstream consumers)")


if __name__ == "__main__":
    build()
