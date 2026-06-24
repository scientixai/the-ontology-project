#!/usr/bin/env python3
"""OWL DL well-formedness lint for the TOP CR-domain ontology — the *ingredients* gate.

The reference graph deliberately does NOT run a reasoner: classification, materialization
and entailment are the *consumer's* job (see the Implementation guide). But "we ship the
ingredients, not the baked cake" only means something if the ingredients are actually
sound — i.e. if a consumer who points HermiT / ELK / owlready2 at this OWL gets correct
entailments instead of garbage.

This is that guarantee, made cheaply: a pure-Python, STRUCTURAL gate (no reasoner, no
Java) that proves the OWL we author is well-formed for someone else's reasoner. It checks
the OWL 2 DL typing discipline the modules actually rely on — it does NOT perform
inference, and it is not a substitute for a full OWL 2 DL profile validator.

  P1  No illegal punning ........ an IRI is at most one of {Class, Datatype,
                                   ObjectProperty, DatatypeProperty, AnnotationProperty}
                                   (OWL 2 DL typing constraint; class/individual punning OK)
  P2  No undeclared class ....... every OWNED IRI used as a class (subClassOf / domain /
                                   owned range / rdf:type object) is declared owl:Class
  P3  No undeclared property .... every OWNED IRI used as a property (predicate /
                                   subPropertyOf end / inverseOf end) is typed as a property
  P4  Range/domain kind sane .... object properties do not range at a datatype; datatype
                                   properties do not range at a class; domains are classes
  P5  No self-contradiction ..... no class is both rdfs:subClassOf and owl:disjointWith
                                   the same class (it would be unsatisfiable)

"Owned" = any IRI in the https://top.scientix.ai/ space (top / cr / hcls / tmf / cx). We
authored those, so we are responsible for declaring them. External vocabulary (prov, skos,
dcterms, xsd, rdf(s), owl) is referenced, not authored, and is not required to be declared
here.

Run standalone (author / CI):   python3 cr-domain/tools/owl_lint.py
Self-test (prove the gate bites): python3 cr-domain/tools/owl_lint.py --selftest
The harness (tests/run_tests.py) calls lint() + selftest() as a regression section.
"""
import glob
import os
import sys

from rdflib import Graph, RDF, RDFS, OWL, URIRef
from rdflib.namespace import XSD

OWNED = "https://top.scientix.ai/"
XSD_NS = str(XSD)

# The five OWL 2 DL structural entity kinds that must be pairwise disjoint per IRI
# (named individuals are exempt — class/individual punning is permitted in OWL 2 DL).
KINDS = {OWL.Class, RDFS.Datatype, OWL.ObjectProperty, OWL.DatatypeProperty,
         OWL.AnnotationProperty}
PROP_KINDS = {OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ont_files():
    """The authored ontology modules — the same non-recursive set the harness parses.
    Vendored/generated ontologies (ontology/vendor/**) are external and checked separately."""
    return sorted(glob.glob(os.path.join(ROOT, "ontology", "*.ttl")))


def owned(t):
    return isinstance(t, URIRef) and str(t).startswith(OWNED)


def local(t):
    s = str(t)
    return s.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def load(paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g


def _supers(c, sup, seen):
    for x in sup.get(c, ()):
        if x not in seen:
            seen.add(x)
            _supers(x, sup, seen)
    return seen


def lint_graph(g):
    """Return a list of (code, term-localname, detail) problems for an ontology graph."""
    problems = []

    # ---- declarations -------------------------------------------------------
    kinds = {}  # subject -> set of declared KINDS
    for s, _, o in g.triples((None, RDF.type, None)):
        if o in KINDS:
            kinds.setdefault(s, set()).add(o)

    # owl:inverseOf types both ends as object properties by use (a valid DL typing).
    inv_objprops = set()
    for s, _, o in g.triples((None, OWL.inverseOf, None)):
        inv_objprops.update((s, o))

    declared_props = {s for s, k in kinds.items() if k & PROP_KINDS} | inv_objprops
    declared_classes = {s for s, k in kinds.items() if OWL.Class in k}
    declared_datatypes = {s for s, k in kinds.items() if RDFS.Datatype in k}

    def is_datatype(t):
        return (isinstance(t, URIRef) and str(t).startswith(XSD_NS)) \
            or t in (RDFS.Literal,) or t in declared_datatypes

    def is_class(t):
        return t in declared_classes or t == OWL.Thing

    # ---- P1: illegal punning -----------------------------------------------
    for s, ks in kinds.items():
        if len(ks) > 1:
            problems.append(("P1-PUNNING", local(s),
                             "typed as " + ", ".join(sorted(local(x) for x in ks))))

    # ---- P2: undeclared class (owned IRIs used in class positions) ----------
    class_pos = {}  # term -> context (first seen)
    def note_class(term, ctx):
        if owned(term):
            class_pos.setdefault(term, ctx)

    for s, _, o in g.triples((None, RDFS.subClassOf, None)):
        note_class(s, "subClassOf subject"); note_class(o, "subClassOf object")
    for _, _, o in g.triples((None, RDFS.domain, None)):
        note_class(o, "rdfs:domain")
    for _, _, o in g.triples((None, RDFS.range, None)):
        note_class(o, "rdfs:range")          # owned ranges are always classes here
    for _, _, o in g.triples((None, RDF.type, None)):
        if o not in KINDS and o != OWL.Ontology:
            note_class(o, "rdf:type object")
    for term, ctx in class_pos.items():
        if term not in declared_classes:
            problems.append(("P2-UNDECLARED-CLASS", local(term),
                             f"used as a class ({ctx}) but never declared owl:Class"))

    # ---- P3: undeclared property (owned IRIs used in property positions) ----
    prop_pos = {}
    def note_prop(term, ctx):
        if owned(term):
            prop_pos.setdefault(term, ctx)

    for _, p, _ in g:
        note_prop(p, "predicate")
    for s, _, o in g.triples((None, RDFS.subPropertyOf, None)):
        note_prop(s, "subPropertyOf subject"); note_prop(o, "subPropertyOf object")
    for s, _, o in g.triples((None, OWL.inverseOf, None)):
        note_prop(s, "inverseOf subject"); note_prop(o, "inverseOf object")
    for term, ctx in prop_pos.items():
        if term not in declared_props:
            problems.append(("P3-UNDECLARED-PROP", local(term),
                             f"used as a property ({ctx}) but never typed as a property"))

    # ---- P4: range/domain kind sanity --------------------------------------
    for p in g.subjects(RDF.type, OWL.ObjectProperty):
        for o in g.objects(p, RDFS.range):
            if is_datatype(o):
                problems.append(("P4-OBJPROP-DATATYPE-RANGE", local(p),
                                 f"object property ranges at datatype {local(o)}"))
        for d in g.objects(p, RDFS.domain):
            if is_datatype(d):
                problems.append(("P4-BAD-DOMAIN", local(p),
                                 f"domain is a datatype {local(d)}"))
    for p in g.subjects(RDF.type, OWL.DatatypeProperty):
        for o in g.objects(p, RDFS.range):
            if is_class(o) and not is_datatype(o):
                problems.append(("P4-DATAPROP-CLASS-RANGE", local(p),
                                 f"datatype property ranges at class {local(o)}"))
        for d in g.objects(p, RDFS.domain):
            if is_datatype(d):
                problems.append(("P4-BAD-DOMAIN", local(p),
                                 f"domain is a datatype {local(d)}"))

    # ---- P5: subClassOf ∩ disjointWith (asserted) -> unsatisfiable ----------
    sup = {}
    for s, _, o in g.triples((None, RDFS.subClassOf, None)):
        sup.setdefault(s, set()).add(o)
    for a, _, b in g.triples((None, OWL.disjointWith, None)):
        if b in _supers(a, sup, set()) or a in _supers(b, sup, set()):
            problems.append(("P5-UNSAT-DISJOINT", local(a),
                             f"is disjointWith {local(b)} yet in a subclass relation with it"))

    return problems


def lint(paths=None):
    return lint_graph(load(paths or ont_files()))


# ---- self-test: a crafted broken ontology MUST trip every check -------------
_BROKEN = """
@prefix ex:  <https://top.scientix.ai/cr/v1#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:<http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ex:Good   a owl:Class .
ex:Punned a owl:Class, owl:ObjectProperty .                 # P1
ex:Child  a owl:Class ; rdfs:subClassOf ex:Undeclared .     # P2 (ex:Undeclared owned, undeclared)
ex:relTo  a owl:ObjectProperty ; rdfs:range xsd:string .     # P4 object prop -> datatype range
ex:countOf a owl:DatatypeProperty ; rdfs:range ex:Good .     # P4 datatype prop -> class range
ex:A a owl:Class ; rdfs:subClassOf ex:B ; owl:disjointWith ex:B .  # P5
ex:B a owl:Class .
"""


def selftest():
    g = Graph(); g.parse(data=_BROKEN, format="turtle")
    codes = {c for c, _, _ in lint_graph(g)}
    expected = {"P1-PUNNING", "P2-UNDECLARED-CLASS",
                "P4-OBJPROP-DATATYPE-RANGE", "P4-DATAPROP-CLASS-RANGE",
                "P5-UNSAT-DISJOINT"}
    missing = expected - codes
    return (not missing), missing


def main():
    if "--selftest" in sys.argv:
        ok, missing = selftest()
        print("[PASS] lint self-test: gate bites on a broken ontology" if ok
              else f"[FAIL] lint self-test missed: {sorted(missing)}")
        sys.exit(0 if ok else 1)
    files = ont_files()
    problems = lint(files)
    print(f"OWL DL well-formedness lint — {len(files)} ontology modules, "
          f"{len(problems)} problem(s)")
    for code, term, detail in problems:
        print(f"  [{code}] {term}: {detail}")
    if problems:
        sys.exit(1)
    print("ALL WELL-FORMED")
    sys.exit(0)


if __name__ == "__main__":
    main()
