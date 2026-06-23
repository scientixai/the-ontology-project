#!/usr/bin/env python3
"""Verify the USDM-OWL + CT NCIt anchors against a current NCI Thesaurus FLAT file.

Joins every NCI C-code the generators anchor (classes/attributes from usdm_ct.json, plus
codelist + permissible-value codes) against a current NCIt release and checks that each
(a) resolves, (b) where CDISC gives a preferred label, that label is a valid NCIt synonym,
(c) reports the CDISC DDF terminology-subset tag.

The NCIt FLAT file (evs.nci.nih.gov/evs-download/thesaurus-downloads) is large and NOT
vendored; the small verification result IS, so the check stays durable and auditable.

Usage:  python3 tools/usdm-rdf-gen/verify_ncit.py /path/to/Thesaurus.txt
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CT = json.load(open(os.path.join(HERE, "ddf-ra-v4.0.0", "usdm_ct.json")))
OUT_JSON = os.path.normpath(os.path.join(HERE, "..", "..", "ontology", "vendor", "usdm", "ncit-verification.json"))
OUT_MD = os.path.normpath(os.path.join(HERE, "..", "..", "ontology", "vendor", "usdm", "NCIT_VERIFICATION.md"))
NCIT_VERSION = "26.05d"  # pinned NCI Thesaurus release the anchors were verified against


def anchored_codes():
    """code -> (usdm term, CDISC preferred label). Entities/attributes take precedence;
    codelist codes carry no CDISC preferred label (binding only)."""
    codes = {}
    for name in sorted(CT["entities"]):
        v = CT["entities"][name]
        codes.setdefault(v["ccode"], (f"entity:{name}", v["pref"]))
    for key in sorted(CT["attributes"]):
        v = CT["attributes"][key]
        codes.setdefault(v["ccode"], (f"attr:{key}", v["pref"]))
    for cl in sorted(CT.get("codelists", {})):
        info = CT["codelists"][cl]
        bind = f"{info['entity']}.{info['attr']}"
        codes.setdefault(cl, (f"codelist:{bind}", ""))
        for val in info["values"]:
            codes.setdefault(val["ccode"], (f"value:{bind}", val["pref"]))
    return codes


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: verify_ncit.py /path/to/Thesaurus.txt  (NCIt FLAT)")
    codes = anchored_codes()
    ncit = {}
    for raw in open(sys.argv[1], encoding="utf-8"):
        col = raw.rstrip("\n").split("\t")
        if col and col[0] in codes:
            ncit[col[0]] = {
                "syns": [s for s in (col[3].split("|") if len(col) > 3 else []) if s],
                "ddf": "CDISC DDF" in (col[8] if len(col) > 8 else ""),
            }
    results = {}
    for code in sorted(codes):
        term, pref = codes[code]
        rec = ncit.get(code)
        synl = {s.strip().lower() for s in rec["syns"]} if rec else set()
        results[code] = {
            "usdm": term, "cdisc_pref": pref,
            "resolved": rec is not None,
            "has_pref": bool(pref),
            "label_ok": bool(rec) and bool(pref) and pref.strip().lower() in synl,
            "ddf_tagged": bool(rec) and rec["ddf"],
            "ncit_pref": rec["syns"][0] if rec and rec["syns"] else "",
        }
    total = len(results)
    resolved = sum(1 for r in results.values() if r["resolved"])
    label_total = sum(1 for r in results.values() if r["has_pref"])
    label_match = sum(1 for r in results.values() if r["label_ok"])
    ddf = sum(1 for r in results.values() if r["ddf_tagged"])
    summary = {"ncit_version": NCIT_VERSION, "verified_on": datetime.date.today().isoformat(),
               "total": total, "resolved": resolved, "label_total": label_total,
               "label_match": label_match, "ddf_tagged": ddf}
    with open(OUT_JSON, "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=1, sort_keys=True)
        f.write("\n")
    review = [c for c in sorted(results)
              if results[c]["resolved"] and results[c]["has_pref"] and not results[c]["label_ok"]]
    with open(OUT_MD, "w") as f:
        f.write(
            f"# NCIt anchor verification\n\n"
            f"The {total} NCI C-codes anchored by the USDM-OWL + CT generators "
            f"(`skos:exactMatch` to `NCIT_*`) were verified against **NCI Thesaurus "
            f"{NCIT_VERSION}** (verified {summary['verified_on']}).\n\n"
            f"| check | result |\n|---|---|\n"
            f"| codes resolve in NCIt {NCIT_VERSION} | {resolved} / {total} |\n"
            f"| CDISC preferred label is an NCIt synonym | {label_match} / {label_total} |\n"
            f"| tagged into the CDISC DDF terminology subset | {ddf} / {total} |\n\n"
            f"(Codelist codes carry no CDISC preferred label; permissible-value codes are general "
            f"NCIt concepts, so not all are DDF-tagged. The binding check is **resolution**.)\n\n"
            f"Reproduce: download the NCIt FLAT file from "
            f"evs.nci.nih.gov/evs-download/thesaurus-downloads and run "
            f"`python3 tools/usdm-rdf-gen/verify_ncit.py Thesaurus.txt`. The flat file is not "
            f"vendored (size); `ncit-verification.json` is the durable record.\n")
        if review:
            f.write("\n## Labels to review (resolved, but CDISC pref not an exact synonym)\n")
            for c in review:
                f.write(f"- `{c}` {results[c]['usdm']}: CDISC \"{results[c]['cdisc_pref']}\" "
                        f"vs NCIt \"{results[c]['ncit_pref']}\"\n")
    print(f"NCIt {NCIT_VERSION}: resolved {resolved}/{total}, "
          f"label_match {label_match}/{label_total}, ddf_tagged {ddf}/{total}")


if __name__ == "__main__":
    main()
