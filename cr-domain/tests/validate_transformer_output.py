#!/usr/bin/env python3
"""US-900-003: Validate USDM transformer output against CR SHACL shapes.

Usage:
    python3 tests/validate_transformer_output.py

Exit codes:
    0 — transformer output conforms (zero violations)
    1 — one or more violations found (transformer regression)
"""
import sys
from pathlib import Path

import pyshacl
import rdflib

BASE = Path(__file__).parent.parent
SHAPES_FILE = BASE / "docs" / "dist" / "top-cr-shapes-v1.ttl"
TRANSFORMER_OUTPUT = BASE / "examples" / "usdm-cdisc-pilot-ingested.ttl"


def main() -> int:
    if not SHAPES_FILE.exists():
        print(f"ERROR: {SHAPES_FILE} not found — run python3 docs/build_dist.py first.")
        return 1
    if not TRANSFORMER_OUTPUT.exists():
        print(f"ERROR: {TRANSFORMER_OUTPUT} not found.")
        return 1

    shapes_graph = rdflib.Graph()
    shapes_graph.parse(str(SHAPES_FILE), format="turtle")

    data_graph = rdflib.Graph()
    data_graph.parse(str(TRANSFORMER_OUTPUT), format="turtle")

    _, results_graph, _ = pyshacl.validate(
        data_graph, shacl_graph=shapes_graph,
        abort_on_first=False, allow_warnings=True, inference="none",
    )

    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    violations = list(results_graph.subjects(
        rdflib.URIRef("http://www.w3.org/ns/shacl#resultSeverity"), SH.Violation))
    warnings = list(results_graph.subjects(
        rdflib.URIRef("http://www.w3.org/ns/shacl#resultSeverity"), SH.Warning))

    print(f"Transformer output: {TRANSFORMER_OUTPUT.name}")
    print(f"  Violations : {len(violations)}")
    print(f"  Warnings   : {len(warnings)}")

    if warnings:
        print("\nWarnings (triaged — expected for optional properties):")
        for w in warnings:
            msg = results_graph.value(w, rdflib.URIRef("http://www.w3.org/ns/shacl#resultMessage"))
            print(f"  - {msg}")

    if violations:
        print("\nVIOLATIONS (unexpected):")
        for v in violations:
            msg = results_graph.value(v, rdflib.URIRef("http://www.w3.org/ns/shacl#resultMessage"))
            path = results_graph.value(v, rdflib.URIRef("http://www.w3.org/ns/shacl#resultPath"))
            print(f"  - {msg}  [path: {path}]")
        print("\nFAIL — transformer output has violations.")
        return 1

    print("\nPASS — transformer output conforms (zero violations).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
