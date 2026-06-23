#!/usr/bin/env python3
"""One-time extractor: USDM_CT.xlsx -> usdm_ct.json (vendored).

Pulls the NCI C-code, preferred name, and CDISC definition for every USDM entity
and attribute from the DDF-RA controlled-terminology workbook, into a small JSON the
generator consumes (so generate.py stays stdlib-only and the build stays hermetic).
Requires openpyxl (a generation-time tool dependency, not a runtime one).

Run:  python3 tools/usdm-rdf-gen/extract_ct.py
"""
import json
import os

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "ddf-ra-v4.0.0", "USDM_CT.xlsx")
OUT = os.path.join(HERE, "ddf-ra-v4.0.0", "usdm_ct.json")
SHEET = "DDF Entities&Attributes"
# 0-based column indices in that sheet
C_ENTITY, C_ROLE, C_LDM, C_CODE, C_PREF, C_DEFN = 1, 2, 4, 5, 6, 8


def clean(v):
    return " ".join(str(v).split()) if v is not None else ""


def main():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb[SHEET]
    entities, attributes = {}, {}
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        ent, role, ldm, code = clean(row[C_ENTITY]), clean(row[C_ROLE]), clean(row[C_LDM]), clean(row[C_CODE])
        if not ent or not code:
            continue
        rec = {"ccode": code, "pref": clean(row[C_PREF]), "defn": clean(row[C_DEFN])}
        if role == "Entity":
            entities[ent] = rec
        elif role == "Attribute" and ldm:
            attributes[f"{ent}.{ldm}"] = rec
    data = {"entities": entities, "attributes": attributes}
    with open(OUT, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {OUT}: {len(entities)} entities, {len(attributes)} attributes")


if __name__ == "__main__":
    main()
