#!/usr/bin/env python3
"""Layer-discipline linter — the executable rule against OOUX layer-blindness.

Prevents the failure documented in docs/ooux-layer-blindness.md: a domain minting
a concept the parent layers (Core, a mid-layer) already own, because an OOUX object
catalog has no import statement and reads operator-completeness as self-containment.

Two violations, both mechanical:

  SHADOW  a domain term (a `cr:X` class or `sh:targetClass`) whose LOCAL NAME equals
          an existing parent-layer class local name (`top:X` / `hcls:X`). The domain
          is re-minting a parent concept instead of inheriting it.

  ORPHAN  a domain term that is neither declared with an `rdfs:subClassOf` chain to a
          parent-layer class, nor recorded in the tier map. It floats with no
          parent-world citation.

Resolution is recorded in cr-domain/views/tier-map.json — every catalog object gets a
verdict:
  dedupe   -> bind to an existing parent class (resolve: top:X / hcls:X)          PASS
  subclass -> domain-native, but rdfs:subClassOf a named existing parent           PASS
  promote  -> a cross-domain primitive with no parent yet; needs a Core/mid class   WARN (RFC backlog)
  review   -> tier not yet decided                                                  WARN (tracked)

A domain term that is NOT in the tier map is an untriaged SHADOW/ORPHAN -> FAIL. That
is the gate: it cannot regress, because any newly introduced object must be triaged
into the map before it lands. Known backlog (promote/review) warns but does not block.

Exit 0 = no untriaged violations. Exit 1 = at least one. Usage:
    python3 tools/lint_layering.py            # from repo root
    python3 tools/lint_layering.py --strict   # promote/review also fail (federation-ready check)
"""
import glob
import json
import os
import sys

from rdflib import Graph, RDF, OWL, URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOP = "https://top.scientix.ai/v1#"
HCLS = "https://top.scientix.ai/hcls/v1#"
CR = "https://top.scientix.ai/cr/v1#"
SH_TARGET = URIRef("http://www.w3.org/ns/shacl#targetClass")
RDFS_SUBCLASS = URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf")

PARENT_GLOBS = [
    "core/v1/modules/*.ttl",
    "core/v1/shapes.ttl",
    "cr-domain/ontology/hcls-core.ttl",
]
DOMAIN_ONTOLOGY_GLOBS = ["cr-domain/ontology/cr*.ttl"]
DOMAIN_VIEW_GLOBS = ["cr-domain/views/**/*.ttl"]
TIER_MAP = "cr-domain/views/tier-map.json"


def localname(iri):
    s = str(iri)
    return s.split("#")[-1] if "#" in s else s.rsplit("/", 1)[-1]


def parse(paths):
    g = Graph()
    for p in paths:
        try:
            g.parse(p, format="turtle")
        except Exception as e:  # a parse error is a different gate's problem; note and skip
            print(f"  ! could not parse {os.path.relpath(p, ROOT)}: {e}", file=sys.stderr)
    return g


def files(globs):
    out = []
    for pat in globs:
        out += glob.glob(os.path.join(ROOT, pat), recursive=True)
    return sorted(set(out))


def parent_classes():
    g = parse(files(PARENT_GLOBS))
    names = {}
    for c in g.subjects(RDF.type, OWL.Class):
        s = str(c)
        if s.startswith(TOP):
            names[localname(c)] = "top:" + localname(c)
        elif s.startswith(HCLS):
            names[localname(c)] = "hcls:" + localname(c)
    return names


def domain_terms():
    """Return {localname: {'as': set(roles), 'chains_to_parent': bool}}.

    chains_to_parent follows rdfs:subClassOf TRANSITIVELY — a cr: class may reach a
    parent layer through intermediate cr: classes, and that is a valid extension.
    """
    terms = {}
    og = parse(files(DOMAIN_ONTOLOGY_GLOBS))

    def reaches_parent(c):
        for anc in og.transitive_objects(c, RDFS_SUBCLASS):
            s = str(anc)
            if anc != c and (s.startswith(TOP) or s.startswith(HCLS)):
                return True
        return False

    for c in og.subjects(RDF.type, OWL.Class):
        if not str(c).startswith(CR):
            continue
        ln = localname(c)
        rec = terms.setdefault(ln, {"as": set(), "chains_to_parent": False})
        rec["as"].add("class")
        if reaches_parent(c):
            rec["chains_to_parent"] = True
    # view targetClasses in cr:
    vg = parse(files(DOMAIN_VIEW_GLOBS))
    for t in vg.objects(None, SH_TARGET):
        if str(t).startswith(CR):
            ln = localname(t)
            terms.setdefault(ln, {"as": set(), "chains_to_parent": False})["as"].add("view-target")
    return terms


def load_tier_map():
    path = os.path.join(ROOT, TIER_MAP)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f).get("objects", {})


def main():
    strict = "--strict" in sys.argv
    parents = parent_classes()
    terms = domain_terms()
    tmap = load_tier_map()

    fails, warns = [], []
    for ln in sorted(terms):
        roles = ",".join(sorted(terms[ln]["as"]))
        entry = tmap.get(ln)
        if entry:
            v = entry.get("verdict")
            if v in ("dedupe", "subclass"):
                # sanity: a dedupe/subclass target must actually exist upstream
                tgt = entry.get("resolve", "")
                tln = tgt.split(":")[-1]
                if v == "dedupe" and tln not in parents:
                    fails.append((ln, roles, f"tier-map dedupe target {tgt} is not a real parent class"))
                continue  # resolved -> PASS
            warns.append((ln, roles, f"{v}: {entry.get('note','tier decision pending (RFC)')}"))
            continue
        # not in the tier map -> untriaged
        if ln in parents:
            fails.append((ln, roles, f"SHADOW of parent class {parents[ln]} — dedupe or subclass, do not re-mint"))
        elif not terms[ln]["chains_to_parent"]:
            fails.append((ln, roles, "ORPHAN — no subClassOf to a parent layer and no tier-map entry"))
        # (a cr class that already chains to a parent and isn't a name-shadow is fine)

    print(f"layer-discipline lint — {len(terms)} domain terms, {len(parents)} parent classes")
    print(f"  tier-map resolved: {sum(1 for ln in terms if tmap.get(ln,{}).get('verdict') in ('dedupe','subclass'))}")
    if warns:
        print(f"\n  {len(warns)} tracked (WARN — triaged, decision/RFC pending):")
        for ln, roles, msg in warns:
            print(f"    ~ {ln:<24} [{roles}]  {msg}")
    if fails:
        print(f"\n  {len(fails)} UNTRIAGED VIOLATIONS (FAIL):")
        for ln, roles, msg in fails:
            print(f"    ✗ {ln:<24} [{roles}]  {msg}")
    else:
        print("\n  no untriaged shadows or orphans.")

    hard = fails + (warns if strict else [])
    if hard:
        print(f"\nFAIL: {len(hard)} blocking issue(s)" + (" (--strict)" if strict and warns else ""))
        return 1
    print("\nPASS" + (f" ({len(warns)} tracked, non-blocking)" if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
