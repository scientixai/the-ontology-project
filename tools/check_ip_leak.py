#!/usr/bin/env python3
"""IP-hygiene gate — keep internal runtime-engine detail out of this PUBLIC repo.

PUBLIC (fine): the reference graph, SHACL, projections, open standards incl. pure
NGSI-LD, ADRs, the technical *why*. GATED (never committed): internal runtime-engine
component names and any runtime internals beyond the open NGSI-LD standard.

The gate must not itself disclose what it protects, so the denylist patterns are NOT
stored in this public repo. They are provisioned out-of-band:
  * CI:    a repo secret exported as env IP_DENYLIST_PATTERNS (one regex per line), or
  * local: a gitignored file tools/ip-denylist.local.json (see tools/ip-denylist.example.json).
If no denylist is configured, the gate prints a notice and passes (exit 0) — it never
blocks a build for lack of the secret; the CLAUDE.md rule + local hooks are the primary
control, CI is the backstop. Match output is REDACTED (file:line only) so neither the
logs nor this file ever echo a gated term.

Modes:  (default) tracked files · --staged staged blobs · --msg FILE a commit message.
Exit 0 = clean / unconfigured; 1 = a gated term was found.
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip() or "."
LOCAL = os.path.join(ROOT, "tools", "ip-denylist.local.json")
EXAMPLE = os.path.join(ROOT, "tools", "ip-denylist.example.json")
# Never scan the gate's own machinery (paths only — no sensitive strings here).
BASE_EXCLUDE = {"tools/ip-denylist.local.json", "tools/ip-denylist.example.json",
                "tools/check_ip_leak.py"}


def load_patterns():
    """(compiled patterns, exclude set). Patterns come from the env secret or the
    gitignored local file — never from a committed file."""
    exclude = set(BASE_EXCLUDE)
    raw = []
    env = os.environ.get("IP_DENYLIST_PATTERNS", "").strip()
    if env:
        raw = [ln.strip() for ln in env.splitlines() if ln.strip() and not ln.startswith("#")]
    elif os.path.exists(LOCAL):
        cfg = json.load(open(LOCAL, encoding="utf-8"))
        raw = cfg.get("patterns", [])
        exclude |= set(cfg.get("exclude", []))
    pats = [re.compile(p, re.IGNORECASE) for p in raw]
    return pats, exclude


def scan_text(text, path, pats):
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if any(p.search(line) for p in pats):
            hits.append((path, i))          # REDACTED: location only, never the term/line
    return hits


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)


def read_tracked(path):
    try:
        return open(os.path.join(ROOT, path), encoding="utf-8").read()
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
        return None


def read_staged(path):
    r = subprocess.run(["git", "show", f":{path}"], cwd=ROOT, capture_output=True)
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

    pats, exclude = load_patterns()
    if not pats:
        print("IP-hygiene: no denylist configured (set the IP_DENYLIST_PATTERNS secret "
              "or provide tools/ip-denylist.local.json) — gate inactive, passing.")
        return 0

    hits = []
    if args.msg:
        hits = scan_text(open(args.msg, encoding="utf-8").read(), args.msg, pats)
    else:
        if args.staged:
            files = [f for f in git("diff", "--cached", "--name-only",
                                    "--diff-filter=ACM").stdout.splitlines() if f]
            reader = read_staged
        else:
            files = [f for f in git("ls-files").stdout.splitlines() if f]
            reader = read_tracked
        for f in files:
            if f in exclude:
                continue
            text = reader(f)
            if text is not None:
                hits += scan_text(text, f, pats)

    if not hits:
        print("IP-hygiene: clean.")
        return 0

    print("IP-HYGIENE VIOLATION — a gated (internal runtime-engine) term was found.\n"
          "This is a PUBLIC repo; keep runtime detail out of committed content and commit\n"
          "messages (see CLAUDE.md). Locations below are redacted — fix the content:\n")
    for path, ln in hits:
        print(f"  {path}:{ln}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
