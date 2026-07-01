#!/usr/bin/env python3
"""US-900-001: pyshacl test harness for all CR-domain example files.

Usage:
    python3 tests/run_shacl.py

Exit codes:
    0 — all examples produced the expected outcome
    1 — one or more examples produced an unexpected outcome
"""
import json
import os
import sys
from pathlib import Path

import pyshacl
import rdflib

BASE = Path(__file__).parent.parent
SHAPES_FILE = BASE / "docs" / "dist" / "top-cr-shapes-v1.ttl"
MANIFEST_FILE = Path(__file__).parent / "manifest.json"


def check(entry: dict, shapes_graph: rdflib.Graph) -> tuple[bool, str]:
    path = BASE / entry["file"]
    expect = entry["expect"]

    if not path.exists():
        return False, f"MISSING  — file not found"

    data_graph = rdflib.Graph()
    try:
        data_graph.parse(str(path), format="turtle")
    except Exception as e:
        return False, f"PARSE_ERR — {e}"

    conforms, _, _ = pyshacl.validate(
        data_graph,
        shacl_graph=shapes_graph,
        abort_on_first=False,
        allow_warnings=True,
        inference="none",
    )

    # Gather result severities
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    results_graph = rdflib.Graph()
    _, results_graph_text, _ = pyshacl.validate(
        data_graph,
        shacl_graph=shapes_graph,
        abort_on_first=False,
        allow_warnings=True,
        inference="none",
        serialize_report_graph="turtle",
    )
    results_graph.parse(data=results_graph_text, format="turtle")
    violations = list(results_graph.subjects(
        rdflib.URIRef("http://www.w3.org/ns/shacl#resultSeverity"),
        SH.Violation,
    ))
    warnings = list(results_graph.subjects(
        rdflib.URIRef("http://www.w3.org/ns/shacl#resultSeverity"),
        SH.Warning,
    ))

    has_violations = len(violations) > 0
    has_warnings = len(warnings) > 0

    if expect == "conformant":
        ok = not has_violations
        status = "PASS" if ok else f"FAIL (got {len(violations)} violations, expected 0)"
    elif expect == "violation":
        ok = has_violations
        status = "PASS" if ok else "FAIL (expected ≥1 violation, got 0)"
    elif expect == "warning":
        ok = has_warnings and not has_violations
        if not ok:
            if has_violations:
                status = f"FAIL (got violations, expected only warnings)"
            else:
                status = "FAIL (expected ≥1 warning, got 0)"
        else:
            status = "PASS"
    else:
        return False, f"UNKNOWN expect value '{expect}'"

    return ok, status


def main() -> int:
    if not SHAPES_FILE.exists():
        print(f"ERROR: shapes file not found at {SHAPES_FILE}")
        print("Run python3 docs/build_dist.py first.")
        return 1

    shapes_graph = rdflib.Graph()
    shapes_graph.parse(str(SHAPES_FILE), format="turtle")

    with open(MANIFEST_FILE) as f:
        manifest = json.load(f)

    rows = []
    failures = 0
    for entry in manifest:
        ok, status = check(entry, shapes_graph)
        if not ok:
            failures += 1
        rows.append((entry["file"], entry["expect"], status))

    # Print summary table
    col_file = max(len(r[0]) for r in rows)
    col_exp  = max(len(r[1]) for r in rows)
    print(f"\n{'File':<{col_file}}  {'Expect':<{col_exp}}  Status")
    print("-" * (col_file + col_exp + 12))
    for file_, expect, status in rows:
        print(f"{file_:<{col_file}}  {expect:<{col_exp}}  {status}")

    print(f"\n{len(manifest)} examples checked — {failures} unexpected results.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
