#!/usr/bin/env python3
"""US-900-002: SPARQL projection test harness.

Runs each .rq file listed in projections/expectations.json against its
designated fixture and asserts minimum result counts.

Usage:
    python3 tests/run_projections.py

Exit codes:
    0 — all projections met expectations
    1 — one or more projections returned fewer rows than expected
"""
import json
import sys
from pathlib import Path

import rdflib

BASE = Path(__file__).parent.parent
EXPECTATIONS_FILE = BASE / "projections" / "expectations.json"


def run_query(query_path: Path, source_path: Path) -> list[dict]:
    g = rdflib.ConjunctiveGraph()
    g.parse(str(source_path), format="turtle")

    with open(query_path) as f:
        sparql = f.read()

    results = g.query(sparql)
    rows = []
    for row in results:
        rows.append({str(k): str(v) for k, v in zip(results.vars, row)})
    return rows


def check_row_match(expected_rows: list[dict], actual_rows: list[dict]) -> bool:
    for exp in expected_rows:
        matched = any(
            all(str(row.get(k, "")) == v for k, v in exp.items())
            for row in actual_rows
        )
        if not matched:
            return False
    return True


def main() -> int:
    with open(EXPECTATIONS_FILE) as f:
        expectations = json.load(f)

    failures = 0
    rows_out = []

    for entry in expectations:
        query_path  = BASE / entry["query"]
        source_path = BASE / entry["source"]
        desc = entry["desc"]

        if not query_path.exists():
            rows_out.append((entry["query"], "MISSING_QUERY", desc))
            failures += 1
            continue
        if not source_path.exists():
            rows_out.append((entry["query"], "MISSING_SOURCE", desc))
            failures += 1
            continue

        try:
            actual = run_query(query_path, source_path)
        except Exception as e:
            rows_out.append((entry["query"], f"ERROR: {e}", desc))
            failures += 1
            continue

        n = len(actual)

        if "expect_rows" in entry:
            ok = check_row_match(entry["expect_rows"], actual)
            status = f"PASS ({n} rows)" if ok else f"FAIL — expected rows not found in {n} results"
            if not ok:
                failures += 1
        elif "expect_min_rows" in entry:
            min_r = entry["expect_min_rows"]
            ok = n >= min_r
            status = f"PASS ({n} rows)" if ok else f"FAIL ({n} rows, expected ≥{min_r})"
            if not ok:
                failures += 1

            if "expect_vars" in entry:
                actual_vars = set(actual[0].keys()) if actual else set()
                expected_vars = set(entry["expect_vars"])
                if not expected_vars.issubset(actual_vars) and actual:
                    status += f" | WARN: missing vars {expected_vars - actual_vars}"
        else:
            status = f"OK ({n} rows, no row assertion)"

        rows_out.append((entry["query"], status, desc))

    col_q = max(len(r[0]) for r in rows_out)
    print(f"\n{'Query':<{col_q}}  Status")
    print("-" * (col_q + 40))
    for q, st, _ in rows_out:
        print(f"{q:<{col_q}}  {st}")

    print(f"\n{len(expectations)} projections checked — {failures} failures.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
