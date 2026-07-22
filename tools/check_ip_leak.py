#!/usr/bin/env python3
"""IP-hygiene gate — keep internal runtime-engine detail out of this PUBLIC repo.

PUBLIC (fine): the reference graph, SHACL, projections, open standards incl. pure
NGSI-LD, ADRs, the technical *why*. GATED (never committed): the internal runtime
engine — the PNE Bridge, the Factual/Adaptive layer architecture, and any
runtime-engine detail beyond the open NGSI-LD standard. Denylist: tools/ip-denylist.json.

Modes:
  (default)      scan every git-tracked text file           — CI / full sweep
  --staged       scan the staged content of changed files   — pre-commit hook
  --msg FILE     scan a commit-message file                 — commit-msg hook

Exit 0 = clean; 1 = a gated term was found (blocks the commit / push / CI).
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip() or "."
CFG = os.path.join(ROOT, "tools", "ip-denylist.json")


def load_cfg():
    c = json.load(open(CFG, encoding="utf-8"))
    pats = [re.compile(p, re.IGNORECASE) for p in c["patterns"]]
    return pats, set(c.get("exclude", []))


def scan_text(text, path, pats):
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        for p in pats:
            if p.search(line):
                hits.append((path, i, p.pattern, line.strip()[:120]))
    return hits


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def tracked_files():
    return [f for f in git("ls-files").stdout.splitlines() if f]


def staged_files():
    return [f for f in git("diff", "--cached", "--name-only",
                           "--diff-filter=ACM").stdout.splitlines() if f]


def read_tracked(path):
    p = os.path.join(ROOT, path)
    try:
        return open(p, encoding="utf-8").read()
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
        return None  # binary / gone


def read_staged(path):
    r = subprocess.run(["git", "show", f":{path}"], cwd=ROOT,
                       capture_output=True)          # bytes (staged blob)
    if r.returncode != 0:
        return None
    try:
        return r.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--msg")
    args = ap.parse_args()
    pats, exclude = load_cfg()
    hits = []

    if args.msg:
        text = open(args.msg, encoding="utf-8").read()
        hits = scan_text(text, args.msg, pats)
    else:
        files = staged_files() if args.staged else tracked_files()
        reader = read_staged if args.staged else read_tracked
        for f in files:
            if f in exclude:
                continue
            text = reader(f)
            if text is not None:
                hits += scan_text(text, f, pats)

    if not hits:
        print("IP-hygiene: clean.")
        return 0

    print("IP-HYGIENE VIOLATION — gated (internal runtime-engine) terms found.\n"
          "This is a PUBLIC repo; keep runtime detail out of committed content and\n"
          "commit messages (see CLAUDE.md). Fix the content — do not weaken the denylist.\n")
    for path, ln, pat, snippet in hits:
        print(f"  {path}:{ln}  /{pat}/  →  {snippet}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
