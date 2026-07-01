#!/usr/bin/env python3
"""crosswalk_check.py — IRI reachability checker for TOP CR crosswalk files.

US-700-004: Verifies that every cx:objectId IRI in a crosswalk TTL file is
reachable (HTTP 200 or 303) or whitelisted as a known BYOL/licensed term IRI
that cannot be resolved without a licence (e.g. MedDRA).

Usage:
    python3 crosswalk_check.py [--crosswalk PATH_TO_TTL] [--timeout 10]

Exit codes:
    0  All IRIs reachable or whitelisted.
    1  One or more IRIs unreachable (non-whitelisted).
"""

import argparse
import re
import sys
import urllib.request
import urllib.error
from typing import Optional

# IRIs whose hosts require a BYOL licence and cannot be resolved publicly.
# These are skipped with a BYOL notice rather than treated as failures.
BYOL_PREFIXES = (
    "https://www.meddra.org/term/",
)

# HTTP status codes that count as "reachable"
REACHABLE_STATUSES = {200, 301, 302, 303, 307, 308}


def extract_object_iris(ttl_text: str) -> list[str]:
    """Return all cx:objectId IRI values from a TTL file (simple regex, not full parse)."""
    pattern = re.compile(r'cx:objectId\s+<([^>]+)>', re.MULTILINE)
    return pattern.findall(ttl_text)


def check_iri(iri: str, timeout: int) -> tuple[bool, Optional[int], str]:
    """
    Returns (ok, status_code, note).
    ok is True if reachable or BYOL-whitelisted.
    """
    for prefix in BYOL_PREFIXES:
        if iri.startswith(prefix):
            return True, None, "BYOL-whitelisted (licence required)"

    try:
        req = urllib.request.Request(iri, method="HEAD",
                                     headers={"User-Agent": "TOP-CR-crosswalk-check/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            ok = status in REACHABLE_STATUSES
            return ok, status, ""
    except urllib.error.HTTPError as e:
        ok = e.code in REACHABLE_STATUSES
        return ok, e.code, str(e.reason)
    except Exception as e:
        return False, None, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description="IRI reachability checker for TOP CR crosswalks")
    parser.add_argument("--crosswalk", required=True, help="Path to a crosswalk .ttl file")
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout in seconds (default: 10)")
    args = parser.parse_args()

    try:
        with open(args.crosswalk, "r", encoding="utf-8") as fh:
            ttl_text = fh.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {args.crosswalk}", file=sys.stderr)
        return 1

    iris = extract_object_iris(ttl_text)
    if not iris:
        print("No cx:objectId IRIs found in the crosswalk file.")
        return 0

    print(f"Checking {len(iris)} cx:objectId IRI(s) from: {args.crosswalk}\n")
    failures = 0
    for iri in iris:
        ok, status, note = check_iri(iri, args.timeout)
        status_str = str(status) if status is not None else "N/A"
        marker = "OK  " if ok else "FAIL"
        note_str = f"  [{note}]" if note else ""
        print(f"  {marker}  [{status_str:>3}]  {iri}{note_str}")
        if not ok:
            failures += 1

    print(f"\nResult: {len(iris) - failures}/{len(iris)} IRIs reachable or whitelisted.")
    if failures:
        print(f"  {failures} IRI(s) FAILED reachability check.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
