#!/usr/bin/env python3
"""Watch kerfors/usdm-rdf (the canonical USDM-RDF we adopt per ADR-0029) and, when a
new release appears, produce an ABSORB/REVIEW assessment so a human can decide whether
to pull it in.

What it does:
  1. Reads the pin (ontology/vendor/usdm/upstream-pin.json): version + per-file sha256.
  2. Fetches the upstream files at a ref (default: the pinned branch, i.e. main) and
     compares sha256 + owl:versionInfo against the pin.
  3. If anything changed, assesses IMPACT against TOP:
       - class-level diff (added / removed) vs our vendored model
       - property-count delta
       - CROSSWALK IMPACT — the decision-critical signal: which usdm: IRIs that
         crosswalks/usdm-to-cr.ttl references would BREAK (dangle) under the new release
  4. Prints a Markdown assessment and a recommendation (LOW-RISK / REVIEW / BREAKING).

Exit code: 0 = up to date (or --soft); 1 = a new release is available (so a scheduled
CI job goes red and surfaces the assessment). Network fetch uses `curl` for portability
(works on CI runners and behind this repo's egress proxy).

Usage:
  python3 cr-domain/tools/usdm-rdf-gen/check_upstream.py            # assess main vs pin
  python3 cr-domain/tools/usdm-rdf-gen/check_upstream.py --ref v0.7.0
  python3 cr-domain/tools/usdm-rdf-gen/check_upstream.py --report /tmp/usdm-assessment.md
  python3 cr-domain/tools/usdm-rdf-gen/check_upstream.py --soft     # always exit 0
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))            # cr-domain/
VENDOR = os.path.join(ROOT, "ontology", "vendor", "usdm")
PIN = os.path.join(VENDOR, "upstream-pin.json")
VENDORED_TTL = os.path.join(VENDOR, "usdm-v4.ttl")                 # our current vendored model
CROSSWALK = os.path.join(ROOT, "crosswalks", "usdm-to-cr.ttl")
USDM_NS = "https://w3id.org/cdisc/usdm/v4/"
RAW = "https://raw.githubusercontent.com/{repo}/{ref}/{path}"


def fetch(url):
    """Fetch bytes via curl (portable across CI + the egress proxy). None on failure."""
    r = subprocess.run(["curl", "-fsSL", "--max-time", "60", url],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def parse_usdm(graph_bytes):
    """(class local-names, property count, ALL local-names of usdm: subjects)."""
    from rdflib import Graph, RDF, OWL
    g = Graph(); g.parse(data=graph_bytes.decode("utf-8"), format="turtle")
    ns_subj = {str(s)[len(USDM_NS):] for s in set(g.subjects())
               if str(s).startswith(USDM_NS)}
    classes = {str(s)[len(USDM_NS):] for s in g.subjects(RDF.type, OWL.Class)
               if str(s).startswith(USDM_NS)}
    nprops = len({s for s in g.subjects(RDF.type, OWL.ObjectProperty)} |
                 {s for s in g.subjects(RDF.type, OWL.DatatypeProperty)})
    return classes, nprops, ns_subj


def version_info(graph_bytes):
    m = re.search(r'owl:versionInfo\s+"([^"]+)"', graph_bytes.decode("utf-8"))
    return m.group(1) if m else "(unknown)"


def crosswalk_targets():
    """The actual usdm: mapping TARGETS (cx:objectId usdm:X) — not comment mentions."""
    if not os.path.exists(CROSSWALK):
        return set()
    t = open(CROSSWALK, encoding="utf-8").read()
    tgts = set(re.findall(r'cx:objectId\s+usdm:([A-Za-z0-9_-]+)', t))
    tgts |= set(re.findall(r'cx:objectId\s+<' + re.escape(USDM_NS) + r'([A-Za-z0-9_-]+)>', t))
    return tgts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", help="upstream git ref to assess (default: pinned branch)")
    ap.add_argument("--report", help="also write the Markdown assessment to this path")
    ap.add_argument("--soft", action="store_true", help="always exit 0 (annotate, don't fail)")
    args = ap.parse_args()

    pin = json.load(open(PIN, encoding="utf-8"))
    repo = pin["upstream_repo"]
    ref = args.ref or pin.get("upstream_branch", "main")
    out = [f"# USDM-RDF upstream assessment — `{repo}` @ `{ref}`",
           "",
           f"Pinned: **{pin['pinned_version']}** (retrieved {pin.get('retrieved','?')}). "
           f"Source of truth per ADR-0029.", ""]

    # 1) per-file sha256 comparison. The model file (usdm_v4.ttl) is required to assess;
    #    an ancillary file that 404s at this ref is itself a signal (added/removed across
    #    versions), not a hard error.
    changed, missing, fetched = {}, {}, {}
    for fname, meta in pin["files"].items():
        b = fetch(RAW.format(repo=repo, ref=ref, path=fname))
        if b is None:
            missing[fname] = True
            changed[fname] = True
            continue
        fetched[fname] = b
        changed[fname] = sha256(b) != meta["sha256"]

    if "usdm_v4.ttl" not in fetched:
        out.append(f"> ⚠️ could not fetch the model `usdm_v4.ttl` at `{ref}` — "
                   "network or bad ref; cannot assess.")
        print("\n".join(out))
        return 3

    up_ver = version_info(fetched["usdm_v4.ttl"])
    any_changed = any(changed.values())

    if not any_changed:
        out += [f"## ✅ UP TO DATE",
                "",
                f"Upstream `{ref}` is **{up_ver}**; every pinned file matches its sha256. "
                "Nothing to absorb.", ""]
        report = "\n".join(out)
        print(report)
        if args.report:
            open(args.report, "w").write(report)
        return 0

    # 2) something changed → assess
    out += [f"## 🔔 UPDATE AVAILABLE — pinned {pin['pinned_version']} → upstream {up_ver}",
            "",
            "| vendored file | status |", "|---|---|"]
    for fname, meta in pin["files"].items():
        st = ("**missing upstream**" if missing.get(fname)
              else "**changed**" if changed[fname] else "unchanged")
        out.append(f"| `{meta['vendored_as']}` | {st} |")
    out.append("")

    # 3) deep diff of the model (only if the model file changed)
    breakers, added, removed, dprop = set(), set(), set(), 0
    if changed.get("usdm_v4.ttl"):
        up_classes, up_props, up_subj = parse_usdm(fetched["usdm_v4.ttl"])
        our_classes, our_props, _ = parse_usdm(open(VENDORED_TTL, "rb").read())
        added = up_classes - our_classes
        removed = our_classes - up_classes
        dprop = up_props - our_props
        targets = crosswalk_targets()
        breakers = {t for t in targets if t not in up_subj}  # mapping targets that vanish
        out += ["### Model diff",
                f"- classes: {len(our_classes)} → {len(up_classes)} "
                f"(**+{len(added)}**, **−{len(removed)}**)",
                f"- properties: Δ {dprop:+d}", ""]
        if added:
            out.append(f"- **added classes** ({len(added)}): "
                       + ", ".join(f"`{c}`" for c in sorted(added)[:40])
                       + (" …" if len(added) > 40 else ""))
        if removed:
            out.append(f"- **removed classes** ({len(removed)}): "
                       + ", ".join(f"`{c}`" for c in sorted(removed)))
        out.append("")
        out += ["### Crosswalk impact (the decision-critical signal)",
                f"`crosswalks/usdm-to-cr.ttl` maps to **{len(targets)}** usdm: targets."]
        if breakers:
            out.append(f"- ❌ **{len(breakers)} would BREAK** under {up_ver} (no longer "
                       "resolve — must remap before absorbing): "
                       + ", ".join(f"`usdm:{b}`" for b in sorted(breakers)))
        else:
            out.append("- ✅ **0 break** — every crosswalk target still resolves.")
        out.append("")

    # 4) recommendation
    if breakers or removed:
        rec = ("**REVIEW / BREAKING** — the update removes classes and/or breaks "
               f"{len(breakers)} crosswalk reference(s). Do not absorb blindly: re-vendor, "
               "remap the crosswalk, re-run the suite, then update the pin.")
    elif changed.get("usdm_v4.ttl"):
        rec = ("**LOW RISK (additive)** — model changed but no crosswalk target breaks and "
               "no referenced class was removed. Safe to absorb: re-vendor the files, run "
               "the suite, update the pin.")
    else:
        rec = ("**LOW RISK** — only ancillary files (shapes / context) changed; the model "
               "is unchanged. Re-vendor the changed assets and update the pin.")
    out += ["### Recommendation", rec, "",
            "_To absorb:_ re-fetch the files into `ontology/vendor/usdm/`, update "
            "`upstream-pin.json` (version + sha256s) and `PROVENANCE.md`, re-run the "
            "crosswalk resolution check + full suite. See ADR-0029."]

    report = "\n".join(out)
    print(report)
    if args.report:
        open(args.report, "w").write(report)
    return 0 if args.soft else 1


if __name__ == "__main__":
    sys.exit(main())
