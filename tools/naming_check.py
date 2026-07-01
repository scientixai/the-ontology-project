#!/usr/bin/env python3
"""Naming convention linter for TOP ontology IRIs.

Classes must use UpperCamelCase local names.
Properties (datatype, object, annotation) must use lowerCamelCase local names.

Usage:
    python3 tools/naming_check.py [dist-file-or-glob ...]

Exits 0 if all names conform, non-zero if any violations found.
"""
import glob
import re
import sys
from rdflib import Graph, RDF, OWL, URIRef

TOP_NAMESPACES = (
    "https://top.scientix.ai/v1#",
    "https://top.scientix.ai/cr/v1#",
    "https://top.scientix.ai/crosswalk/v1#",
    "https://top.scientix.ai/hcls/v1#",
    "https://top.scientix.ai/tmf/v1#",
)

UPPER_CAMEL = re.compile(r"^[A-Z][A-Za-z0-9]*$")
LOWER_CAMEL = re.compile(r"^[a-z][A-Za-z0-9]*$")

# Industry-standard names where leading-lowercase is an established convention.
UPPER_CAMEL_EXCEPTIONS = {"eCRF"}  # electronic Case Report Form


def local_name(iri: str) -> str | None:
    """Return the local name after # or the last / segment, or None if not a project IRI."""
    for ns in TOP_NAMESPACES:
        if iri.startswith(ns):
            return iri[len(ns):]
    return None


def check_files(paths: list[str]) -> list[tuple[str, str, str]]:
    """Return list of (iri, expected_case, local) violation tuples."""
    g = Graph()
    for p in paths:
        for f in glob.glob(p):
            g.parse(f)

    violations = []
    seen: set[str] = set()

    def check(iri: str, kind: str) -> None:
        if iri in seen:
            return
        seen.add(iri)
        local = local_name(iri)
        if local is None:
            return
        if kind == "class" and not UPPER_CAMEL.match(local) and local not in UPPER_CAMEL_EXCEPTIONS:
            violations.append((iri, "UpperCamelCase (class)", local))
        elif kind == "property" and not LOWER_CAMEL.match(local):
            violations.append((iri, "lowerCamelCase (property)", local))

    for s in g.subjects(RDF.type, OWL.Class):
        check(str(s), "class")
    for s in g.subjects(RDF.type, OWL.DatatypeProperty):
        check(str(s), "property")
    for s in g.subjects(RDF.type, OWL.ObjectProperty):
        check(str(s), "property")
    for s in g.subjects(RDF.type, OWL.AnnotationProperty):
        check(str(s), "property")

    return violations


def main() -> int:
    paths = sys.argv[1:] if len(sys.argv) > 1 else [
        "cr-domain/ontology/*.ttl",
        "core/v1/modules/*.ttl",
    ]
    violations = check_files(paths)
    if violations:
        print(f"NAMING VIOLATIONS ({len(violations)}):")
        for iri, expected, local in sorted(violations):
            print(f"  [{expected}] {local!r}  →  {iri}")
        return 1
    print(f"OK — all IRIs conform to naming conventions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
