#!/usr/bin/env python3
"""Generate the reference entity-view corpus from the OOUX object catalog.

Reads docs/ooux-object-catalog-v0.2.md and emits, per object, one Turtle file
under views/entity/<slug>.ttl declaring a cr:<Object>EntityView: the exhaustive,
flat menu of everything that object can express in a view —

  * its own attributes            -> sh:property with sh:datatype (identity set flagged)
  * its provenance metadata        -> sh:property flagged cr:isMetadata
  * its relationships as POINTERS  -> sh:property with sh:node cr:<Target>EntityView
                                      and native SHACL cardinality (sh:minCount/maxCount)

REFERENCE, NOT RUNTIME. The corpus carries NO prominence, rank, ordering, or
role scoping: those are an application's arrangement, recorded per person per day
in the runtime graph, never in the commons. A pointer only RESOLVES to the
target's view; it never inlines it. The depth-0 render of a pointer is the
target's identity set (its cr:isIdentity fields). Deeper is navigation.

Deterministic and byte-reproducible: same catalog in, same TTL out. Run:
    python3 cr-domain/tools/gen_entity_views.py            # write corpus
    python3 cr-domain/tools/gen_entity_views.py --check    # report only, no write
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "docs", "ooux-object-catalog-v0.2.md")
OUT_DIR = os.path.join(ROOT, "views", "entity")

CARD_RE = re.compile(r"^\d+(?:\.\.(?:N|\d+))?$")
HEADER_RE = re.compile(r"^##\s+\*\*(\d+)\\?\.\s+(.+?)\*\*\s*$")
SECTION_RE = re.compile(r"^###\s+\*\*(.+?)\*\*\s*$")
ATTR_RE = re.compile(r"^\*\s+\*\*(.+?)\*\*\s*(?:\(([^)]*)\))?\s*:\s*(.*)$")
REL_RE = re.compile(r"^\*\s+\*\*(.+?)\*\*\s*:\s*(.+?)\s*;\s*(.*)$")

# clean scalar catalog types -> xsd datatype. Everything else (object{...},
# GeoProperty, enum value lists, opaque) is emitted as a typeless property whose
# raw catalog type is preserved in rdfs:comment — nothing is silently dropped.
XSD = {
    "string": "xsd:string", "integer": "xsd:integer", "int": "xsd:integer",
    "boolean": "xsd:boolean", "bool": "xsd:boolean", "date": "xsd:date",
    "datetime": "xsd:dateTime", "decimal": "xsd:decimal", "float": "xsd:decimal",
    "number": "xsd:decimal", "duration": "xsd:duration", "enum": "xsd:string",
}


def clean(s):
    """Strip markdown escaping (\\< \\> \\_) so comments read as authored."""
    return re.sub(r"\\([<>_&])", r"\1", s or "").strip()


def safe_local(name):
    """A minted cr: predicate local name valid as a Turtle PN_LOCAL. Valid catalog
    names (cr:enrols, cr:conductedAt) pass through unchanged; oddballs like
    '@context' or 'ngsi-ld@context' are camel-folded (true name kept in sh:name)."""
    if re.match(r"^[A-Za-z][A-Za-z0-9_-]*$", name):
        return name
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", name) if p]
    if not parts:
        return "field"
    loc = parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])
    return loc if re.match(r"^[A-Za-z]", loc) else "x" + loc


def camel(name):
    """Object/target name -> CamelCase local name (CRF, CAPA kept as-is)."""
    parts = re.split(r"[^A-Za-z0-9]+", name.strip())
    parts = [p for p in parts if p]
    out = []
    for p in parts:
        out.append(p if p.isupper() else p[:1].upper() + p[1:])
    return "".join(out)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def canon(name):
    """Normalize an object or relationship-target name for matching: drop any
    trailing parenthetical qualifier, collapse whitespace, lowercase."""
    n = re.sub(r"\s*\(.*\)\s*$", "", name).strip()
    return re.sub(r"\s+", " ", n).lower()


def parse_type(raw):
    """(xsd_or_None, multi_valued, note) from a catalog type string."""
    if not raw:
        return None, False, ""
    note = raw.strip()
    low = note.lower()
    multi = low.startswith("array")
    # element type inside array<...>
    m = re.match(r"array\s*<\s*([a-z0-9_]+)\s*>", low)
    head = m.group(1) if m else re.split(r"[ ,<({]", low, 1)[0]
    return XSD.get(head), multi, note


def cardinality(card):
    """'1'|'0..1'|'1..N'|'0..N' -> (minCount, maxCount) as strings or None."""
    card = card.strip()
    if not CARD_RE.match(card):
        return None, None
    if ".." not in card:
        return card, card                      # exactly n
    lo, hi = card.split("..", 1)
    mn = lo if lo != "0" else None
    mx = None if hi == "N" else hi
    return mn, mx


def pick_identity(attrs):
    """The minimal fields that identify the object anywhere it is a pointer."""
    names = [a["name"] for a in attrs]
    ident = []
    idf = None
    for a in attrs:
        if "unique" in a["quals"].lower() or re.search(
                r"(?i)(^id$|Id$|Number$|Code$|Identifier$)", a["name"]):
            idf = a["name"]
            break
    if idf is None and names:
        idf = names[0]
    if idf:
        ident.append(idf)
    for a in attrs:                            # one human label
        if a["name"] not in ident and re.search(
                r"(?i)(Title$|Name$|^title$|^label$|Acronym$)", a["name"]):
            ident.append(a["name"])
            break
    for a in attrs:                            # one status/phase
        if a["name"] not in ident and a["is_enum"] and re.search(
                r"(?i)(Status$|Phase$|State$)", a["name"]):
            ident.append(a["name"])
            break
    return ident[:4]


def parse_catalog():
    objects = []
    cur = None
    section = None
    for line in open(CATALOG, encoding="utf-8"):
        line = line.rstrip("\n")
        h = HEADER_RE.match(line)
        if h:
            if cur:
                objects.append(cur)
            cur = {"num": int(h.group(1)), "raw": h.group(2).strip(),
                   "name": re.sub(r"\s*\(.*\)\s*$", "", h.group(2)).strip(),
                   "attrs": [], "meta": [], "rels": []}
            section = None
            continue
        if cur is None:
            continue
        s = SECTION_RE.match(line)
        if s:
            section = s.group(1).strip().lower()
            continue
        if section in ("attributes", "metadata"):
            m = ATTR_RE.match(line)
            if m:
                nm, typ, desc = m.group(1).strip(), (m.group(2) or "").strip(), m.group(3).strip()
                bucket = cur["attrs"] if section == "attributes" else cur["meta"]
                bucket.append({"name": nm, "type": typ, "quals": typ,
                               "desc": desc, "is_enum": "enum" in typ.lower()})
        elif section == "relationships":
            m = REL_RE.match(line)
            if not m:
                continue
            relname, mid, desc = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            cards = re.findall(r"\(([^()]+)\)", mid)
            card = next((c for c in reversed(cards) if CARD_RE.match(c.strip())), "")
            target = mid
            if card:
                # strip the trailing cardinality parenthetical only
                target = re.sub(r"\s*\(" + re.escape(card) + r"\)\s*$", "", mid).strip()
            cur["rels"].append({"rel": relname, "target": target,
                                "card": card.strip(), "desc": desc})
    if cur:
        objects.append(cur)
    return objects


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


HEADER = """\
# ---------------------------------------------------------------------------
# REFERENCE ENTITY VIEW  (generated — do not edit by hand)
# Source: docs/ooux-object-catalog-v0.2.md  |  Generator: tools/gen_entity_views.py
#
# REFERENCE, NOT RUNTIME. This is the exhaustive, FLAT menu of everything a
# {label} can express in a view: its own attributes, its provenance metadata,
# and its relationships as POINTERS to other objects' views. It carries NO
# prominence, rank, ordering, or role scoping — that arrangement is an
# application's choice, recorded per person per day in the runtime graph, never
# in the commons. A pointer RESOLVES to the target's view; it never inlines it.
# The depth-0 render of a pointer is the target's identity set (cr:isIdentity).
# See the entity-view ADR and RFC 0001.
# ---------------------------------------------------------------------------
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix cr:   <https://top.scientix.ai/cr/v1#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

"""


def render(obj, view_iri_of):
    cam = camel(obj["name"])
    view = f"cr:{cam}EntityView"
    ident = set(pick_identity(obj["attrs"]))
    lines = [HEADER.format(label=esc(obj["name"]))]
    lines.append(f"{view} a sh:NodeShape, cr:EntityView ;")
    lines.append(f'    sh:targetClass cr:{cam} ;')
    lines.append(f'    rdfs:label "{esc(obj["name"])}" ;')
    lines.append(f'    cr:catalogNumber {obj["num"]} ;')

    def prop(path, name, *, datatype=None, node=None, mn=None, mx=None,
             multi=False, identity=False, metadata=False, comment=None, last=False):
        seg = [f'sh:path cr:{path}', f'sh:name "{esc(name)}"']
        if datatype:
            seg.append(f'sh:datatype {datatype}')
        if node:
            seg.append(f'sh:node {node}')
        if mn is not None:
            seg.append(f'sh:minCount {mn}')
        if mx is not None:
            seg.append(f'sh:maxCount {mx}')
        elif multi is False and node is None and datatype and not metadata and mn is None:
            pass
        if identity:
            seg.append("cr:isIdentity true")
        if metadata:
            seg.append("cr:isMetadata true")
        if comment:
            seg.append(f'rdfs:comment "{esc(comment)}"')
        term = " ." if last else " ;"
        lines.append(f"    sh:property [ { ' ; '.join(seg) } ]{term}")

    # relationships last so the file reads attributes -> metadata -> pointers
    def combine(a):
        t, d = clean(a["type"]), clean(a["desc"])
        return (t + (": " + d if d else "")) if t else (d or None)

    rows = []
    for a in obj["attrs"]:
        dt, multi, _ = parse_type(a["type"])
        rows.append(dict(kind="attr", path=safe_local(a["name"]), name=a["name"], datatype=dt,
                         multi=multi, identity=a["name"] in ident,
                         comment=combine(a), mx=("1" if (dt and not multi) else None)))
    for a in obj["meta"]:
        dt, multi, _ = parse_type(a["type"])
        rows.append(dict(kind="meta", path=safe_local(a["name"]), name=a["name"], datatype=dt,
                         multi=multi, metadata=True, comment=combine(a),
                         mx=("1" if (dt and not multi) else None)))
    unresolved = []
    for r in obj["rels"]:
        tgt_iri, resolved = view_iri_of(r["target"])
        if not resolved:
            unresolved.append(r["target"])
        mn, mx = cardinality(r["card"])
        tgt_label = re.sub(r"\s*\(.*\)\s*$", "", r["target"]).strip()
        label = f'{r["rel"]} -> {tgt_label}'
        card_note = f'[{r["card"]}] ' if r["card"] else ""
        rows.append(dict(kind="rel", path=safe_local(r["rel"]), name=label, node=tgt_iri,
                         mn=mn, mx=mx, comment=(card_note + clean(r["desc"])).strip() or None))

    for i, r in enumerate(rows):
        prop(r["path"], r["name"], datatype=r.get("datatype"), node=r.get("node"),
             mn=r.get("mn"), mx=r.get("mx"), multi=r.get("multi", False),
             identity=r.get("identity", False), metadata=r.get("metadata", False),
             comment=r.get("comment"), last=(i == len(rows) - 1))
    if len(rows) == 0:
        # object with no attributes/relationships: still a valid (empty) menu
        lines[-1] = lines[-1].rstrip(" ;") + " ."
    return "\n".join(lines) + "\n", unresolved, len(ident)


def main():
    check = "--check" in sys.argv
    objects = parse_catalog()
    by_canon = {canon(o["name"]): camel(o["name"]) for o in objects}

    def view_iri_of(target):
        cam = by_canon.get(canon(target))
        if cam:
            return f"cr:{cam}EntityView", True
        return f"cr:{camel(target)}EntityView", False

    if not check:
        os.makedirs(OUT_DIR, exist_ok=True)
    total_unresolved = {}
    n_rel = n_attr = 0
    written = []
    for o in objects:
        ttl, unresolved, nident = render(o, view_iri_of)
        n_rel += len(o["rels"])
        n_attr += len(o["attrs"]) + len(o["meta"])
        if nident == 0 and (o["attrs"] or o["rels"]):
            print(f"  WARN: {o['name']} has empty identity set")
        for u in unresolved:
            total_unresolved.setdefault(u, []).append(o["name"])
        path = os.path.join(OUT_DIR, f"{slug(o['name'])}.ttl")
        written.append(os.path.relpath(path, ROOT))
        if not check:
            open(path, "w", encoding="utf-8").write(ttl)

    print(f"objects: {len(objects)}  attributes: {n_attr}  relationships: {n_rel}")
    print(f"files: {len(written)}  -> views/entity/")
    if total_unresolved:
        print(f"\nunresolved relationship targets (no catalog object — pointer minted, "
              f"resolves once the object is added): {len(total_unresolved)}")
        for t, srcs in sorted(total_unresolved.items()):
            print(f"  - {t}  (referenced by: {', '.join(sorted(set(srcs)))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
