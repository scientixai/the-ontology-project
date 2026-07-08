#!/usr/bin/env python3
"""TOP CR-domain test harness.

(a) Structurally parses every ontology/ and shapes/ Turtle file.
(b) SHACL-validates every example in tests/manifest.json, asserting a severity
    outcome: 'conform' (0 violations, 0 warnings), 'warn' (0 violations, >=1
    warning), or 'violate' (>=1 violation). Negative/graded tests prove shapes bite.
(c) Runs bitemporal SPARQL detective tests (as-of reconstruction; back-dating).

Regression gate: must exit 0 before new work lands.
Usage: python3 cr-domain/tests/run_tests.py
"""
import glob
import json
import os
import sys
from datetime import datetime, timedelta

from rdflib import Graph, Namespace, RDF, URIRef
from pyshacl import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SH = Namespace("http://www.w3.org/ns/shacl#")
TOP = Namespace("https://top.scientix.ai/v1#")
CR = Namespace("https://top.scientix.ai/cr/v1#")
EX = Namespace("https://top.scientix.ai/examples/")


def load_graph(paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g


def severity_counts(report):
    v = w = i = 0
    for r in report.subjects(RDF.type, SH.ValidationResult):
        sev = report.value(r, SH.resultSeverity)
        if sev == SH.Violation:
            v += 1
        elif sev == SH.Warning:
            w += 1
        elif sev == SH.Info:
            i += 1
    return v, w, i


def outcome(v, w):
    if v >= 1:
        return "violate"
    if w >= 1:
        return "warn"
    return "conform"


def main():
    ont_files = sorted(glob.glob(os.path.join(ROOT, "ontology", "*.ttl")))
    shape_files = sorted(glob.glob(os.path.join(ROOT, "shapes", "*.ttl")))
    failures = []

    # (a) structural parse check
    for f in ont_files + shape_files:
        try:
            Graph().parse(f, format="turtle")
        except Exception as e:  # noqa: BLE001
            failures.append(("PARSE", os.path.relpath(f, ROOT), str(e)))
    if [x for x in failures if x[0] == "PARSE"]:
        _report([("parse", 0, 0)], failures)

    shapes_graph = load_graph(shape_files) if shape_files else Graph()
    ont_graph = load_graph(ont_files) if ont_files else Graph()

    # (a2) T-box coherence: no duplicate class definitions across modules,
    # no dangling top:/cr:/hcls: references. Catches the participant-module
    # class of drift (dangling upper class, re-defined classes) mechanically.
    co_passed, co_total = coherence_checks(ont_files, ont_graph, failures)

    # (a3) Core seam: the local top-core stub must stay aligned with the PINNED
    # TOP Core artifact (upstream-pin.json), modulo the documented divergences.
    sm_passed, sm_total = seam_checks(failures)

    # (b) SHACL cases (severity-aware)
    cases = json.load(open(os.path.join(ROOT, "tests", "manifest.json")))
    passed = 0
    for c in cases:
        data = Graph()
        data.parse(os.path.join(ROOT, c["file"]), format="turtle")
        # Merge the ontology into the validated graph (not just inference): shapes that
        # reach commons-resident nodes (e.g. a document's tmf:TMFArtifactType and its
        # content bindings) must see those triples, not only use them for entailment.
        for t in ont_graph:
            data.add(t)
        _, report, _ = validate(
            data, shacl_graph=shapes_graph,
            inference="rdfs", advanced=True,
        )
        v, w, _i = severity_counts(report)
        got = outcome(v, w)
        # manifest uses the long forms (conformant/violation/warning)
        norm = {"conformant": "conform", "violation": "violate", "warning": "warn"}
        ok = got == norm.get(c["expect"], c["expect"])
        if ok:
            passed += 1
        else:
            failures.append(("SHACL", c["file"],
                             f"expected {c['expect']}, got {got} (V={v} W={w})"))
        print(f"[{'PASS' if ok else 'FAIL'}] "
              f"{c.get('desc', c['file'])}  [{got}]")

    # (c) bitemporal detective tests
    bt_passed, bt_total = bitemporal_checks(ont_graph, failures)

    # (d) edge-projection tests (standards as views of the native graph)
    pj_passed, pj_total = projection_checks(ont_graph, failures)

    # (e) integration demo (projection views + regulator query)
    dm_passed, dm_total = demo_checks(failures)

    # (f) safety — expedited SAE reporting clock (bitemporal compliance)
    sf_passed, sf_total = safety_checks(ont_graph, failures)

    # (g) pre-IND — IND 30-day review clock (bitemporal)
    pi_passed, pi_total = preind_checks(ont_graph, failures)

    # (h) LIMS — specimen custody current-state derivation (bitemporal)
    lm_passed, lm_total = lims_checks(ont_graph, failures)

    # (i) start-up — enrollment must not precede site activation (preventive, bitemporal)
    su_passed, su_total = startup_checks(ont_graph, failures)

    # (j) schedule — SoA as-of reconstruction across an amendment + missed-visit detection
    sd_passed, sd_total = schedule_checks(ont_graph, failures)

    # (k) vendored USDM-OWL — the generated external interop layer parses + is complete
    uv_passed, uv_total = usdm_vendor_checks(failures)

    # (l) NCIt anchor verification — anchors resolve + match against a pinned NCIt release
    nv_passed, nv_total = ncit_verification_checks(failures)

    # (m) single-pull retrieval view — one entity carries every green-check fact (no recursive lookups)
    vw_passed, vw_total = view_checks(failures)

    # (n) competency questions — the reusable business queries answer as documented
    cq_passed, cq_total = competency_checks(ont_graph, failures)

    # (o) vocabulary — the thesaurus layer holds its ADR-0024 contract
    vb_passed, vb_total = vocab_checks(ont_graph, failures)

    _report([
        ("coherence", co_passed, co_total),
        ("seam", sm_passed, sm_total),
        ("SHACL", passed, len(cases)),
        ("bitemporal", bt_passed, bt_total),
        ("projections", pj_passed, pj_total),
        ("demo", dm_passed, dm_total),
        ("safety", sf_passed, sf_total),
        ("pre-IND", pi_passed, pi_total),
        ("lims", lm_passed, lm_total),
        ("startup", su_passed, su_total),
        ("schedule", sd_passed, sd_total),
        ("usdm", uv_passed, uv_total),
        ("ncit", nv_passed, nv_total),
        ("view", vw_passed, vw_total),
        ("competency", cq_passed, cq_total),
        ("vocab", vb_passed, vb_total),
    ], failures)


def vocab_checks(ont_graph, failures):
    """The thesaurus layer (ontology/cr-thesaurus.ttl) holds its ADR-0024 contract:
    (1) every subject carrying a SKOS label is a term defined in the ontology (or a
        reified skosxl:Label / the watch-list collection) — no labels on phantom IRIs;
    (2) skos:prefLabel is unique per concept and no two concepts share one;
    (3) every watch-list member carries an anti-synonym / routing skos:scopeNote;
    (4) no BFO IRIs leak into domain modules (alignment is carried at Core — ADR-0024)."""
    from rdflib import Namespace, OWL
    SKOS_NS = Namespace("http://www.w3.org/2004/02/skos/core#")
    SKOSXL = Namespace("http://www.w3.org/2008/05/skos-xl#")
    path = os.path.join(ROOT, "ontology", "cr-thesaurus.ttl")
    if not os.path.exists(path):
        return 0, 0
    th = Graph(); th.parse(path, format="turtle")
    defined = set(ont_graph.subjects(RDF.type, OWL.Class)) | \
        set(ont_graph.subjects(RDF.type, OWL.ObjectProperty)) | \
        set(ont_graph.subjects(RDF.type, OWL.DatatypeProperty))
    xl_labels = set(th.subjects(RDF.type, SKOSXL.Label))
    collections = set(th.subjects(RDF.type, SKOS_NS.Collection))
    ontologies = set(th.subjects(RDF.type, OWL.Ontology))
    total = passed = 0

    # (1) labels attach only to defined terms
    total += 1
    labeled = set()
    for p in (SKOS_NS.prefLabel, SKOS_NS.altLabel, SKOS_NS.hiddenLabel,
              SKOS_NS.scopeNote, SKOSXL.altLabel):
        labeled |= set(th.subjects(p, None))
    phantoms = sorted(str(s) for s in labeled
                      if s not in defined and s not in xl_labels
                      and s not in collections and s not in ontologies)
    if not phantoms:
        passed += 1; print(f"[PASS] vocab: all {len(labeled)} labeled subjects are defined terms")
    else:
        failures.append(("VOCAB", "phantom-labels", str(phantoms)))
        print(f"[FAIL] vocab: labels on undefined terms: {phantoms}")

    # (2) prefLabel unique per concept, and no two concepts share one
    total += 1
    problems = []
    seen = {}
    for s in set(th.subjects(SKOS_NS.prefLabel, None)):
        prefs = list(th.objects(s, SKOS_NS.prefLabel))
        if len(prefs) > 1:
            problems.append(f"{s} has {len(prefs)} prefLabels")
        for pl in prefs:
            key = str(pl).lower()
            if key in seen and seen[key] != s:
                problems.append(f"prefLabel '{pl}' shared by {seen[key]} and {s}")
            seen[key] = s
    if not problems:
        passed += 1; print(f"[PASS] vocab: {len(seen)} prefLabels, one per concept, none shared")
    else:
        failures.append(("VOCAB", "prefLabel", str(problems)))
        print(f"[FAIL] vocab: prefLabel problems: {problems}")

    # (3) watch-list members carry routing scope notes
    total += 1
    wl = URIRef(str(CR) + "AmbiguousTermsWatchList")
    members = list(th.objects(wl, SKOS_NS.member))
    unnoted = sorted(str(m) for m in members if th.value(m, SKOS_NS.scopeNote) is None)
    if members and not unnoted:
        passed += 1; print(f"[PASS] vocab: watch-list has {len(members)} gated terms, all with routing notes")
    else:
        failures.append(("VOCAB", "watch-list", f"members={len(members)} unnoted={unnoted}"))
        print(f"[FAIL] vocab: watch-list unnoted members: {unnoted}")

    # (4) BFO stays at Core — no bfo: IRIs in domain modules
    total += 1
    leaks = []
    for f in sorted(glob.glob(os.path.join(ROOT, "ontology", "*.ttl"))):
        g = Graph(); g.parse(f, format="turtle")
        for s, p, o in g:
            for term in (s, p, o):
                if isinstance(term, URIRef) and "purl.obolibrary.org/obo/bfo" in str(term):
                    leaks.append(os.path.basename(f))
                    break
    leaks = sorted(set(leaks))
    if not leaks:
        passed += 1; print("[PASS] vocab: no bfo: IRIs in domain modules (alignment carried at Core, ADR-0024)")
    else:
        failures.append(("VOCAB", "bfo-leak", str(leaks)))
        print(f"[FAIL] vocab: bfo: IRIs leaked into domain modules: {leaks}")

    return passed, total


def competency_checks(ont_graph, failures):
    """The curated competency-question library (competency/*.rq + competency.json)
    must answer as documented — so the reusable business queries a consumer copies
    are guaranteed to run and return the stated result, not decorative snippets."""
    manifest = os.path.join(ROOT, "competency", "competency.json")
    if not os.path.exists(manifest):
        return 0, 0
    cqs = json.load(open(manifest))
    total = passed = 0

    def rows_for(source, query_path):
        g = Graph()
        for t in ont_graph:
            g.add(t)
        g.parse(os.path.join(ROOT, source), format="turtle")
        q = open(os.path.join(ROOT, query_path)).read()
        res = g.query(q)
        return [{str(v): str(r[v]) for v in res.vars if r[v] is not None} for r in res]

    for cq in cqs:
        total += 1
        rows = rows_for(cq["source"], cq["query"])
        problems = []
        for exp in cq.get("expect_rows", []):
            if not any(all(r.get(k) == v for k, v in exp.items()) for r in rows):
                problems.append(f"missing row {exp}")
        if "expect_min_rows" in cq and len(rows) < cq["expect_min_rows"]:
            problems.append(f"expected >={cq['expect_min_rows']} rows, got {len(rows)}")
        # a discriminating CQ must return NOTHING on its conformant counterpart
        if cq.get("also_empty_on"):
            if rows_for(cq["also_empty_on"], cq["query"]):
                problems.append(f"expected empty on {cq['also_empty_on']}")
        if not problems:
            passed += 1
            print(f"[PASS] competency {cq['id']}: {cq['question'][:64]}")
        else:
            failures.append(("CQ", cq["id"], f"{problems}; got {rows}"))
            print(f"[FAIL] competency {cq['id']}: {problems}")
    return passed, total


def coherence_checks(ont_files, ont_graph, failures):
    """T-box coherence across the module set (vendor/ excluded by the glob):

    (1) A class is defined (typed owl:Class) in at most ONE module file —
        duplicate definitions merge into contradictory superclass sets.
    (2) Every top:/cr:/hcls: IRI used as a superclass, domain, or range in a
        module resolves to a class defined somewhere in the merged set — no
        dangling upper references (the top-core.ttl stub closes the top: terms).
    (3) No two module files claim the same owl:Ontology IRI.
    """
    from rdflib import OWL, RDFS
    owned = ("https://top.scientix.ai/v1#",
             "https://top.scientix.ai/cr/v1#",
             "https://top.scientix.ai/hcls/v1#")
    total = passed = 0

    # (1) duplicate class definitions
    total += 1
    defined_in = {}
    for f in ont_files:
        g = Graph(); g.parse(f, format="turtle")
        for c in set(g.subjects(RDF.type, OWL.Class)):
            defined_in.setdefault(c, []).append(os.path.basename(f))
    dups = {c: fs for c, fs in defined_in.items() if len(fs) > 1}
    if not dups:
        passed += 1; print(f"[PASS] coherence: {len(defined_in)} classes, each defined in exactly one module")
    else:
        for c, fs in sorted(dups.items()):
            failures.append(("COHERENCE", "duplicate-class", f"{c} defined in {fs}"))
        print(f"[FAIL] coherence: {len(dups)} classes defined in more than one module: "
              f"{ {str(c): fs for c, fs in dups.items()} }")

    # (2) dangling superclass / domain / range references in owned namespaces
    total += 1
    defined = set(defined_in)
    dangling = set()
    for pred in (RDFS.subClassOf, RDFS.domain, RDFS.range):
        for o in set(ont_graph.objects(None, pred)):
            if isinstance(o, URIRef) and str(o).startswith(owned) and o not in defined:
                dangling.add(o)
    if not dangling:
        passed += 1; print("[PASS] coherence: no dangling top:/cr:/hcls: superclass, domain, or range references")
    else:
        for d in sorted(dangling):
            failures.append(("COHERENCE", "dangling-ref", str(d)))
        print(f"[FAIL] coherence: dangling references: {sorted(str(d) for d in dangling)}")

    # (3) unique owl:Ontology IRIs per module file
    total += 1
    ont_iris = {}
    for f in ont_files:
        g = Graph(); g.parse(f, format="turtle")
        for oi in set(g.subjects(RDF.type, OWL.Ontology)):
            ont_iris.setdefault(oi, []).append(os.path.basename(f))
    oidups = {oi: fs for oi, fs in ont_iris.items() if len(fs) > 1}
    if not oidups:
        passed += 1; print(f"[PASS] coherence: {len(ont_iris)} owl:Ontology headers, no IRI claimed twice")
    else:
        for oi, fs in sorted(oidups.items()):
            failures.append(("COHERENCE", "duplicate-ontology-iri", f"{oi} in {fs}"))
        print(f"[FAIL] coherence: ontology IRI claimed by multiple files: "
              f"{ {str(o): fs for o, fs in oidups.items()} }")

    return passed, total


def seam_checks(failures):
    """Core↔domain seam (ADR-0023): verify (1) the pinned Core artifact's checksum,
    and (2) that every top: term in the local stub (ontology/top-core.ttl) exists in
    that pinned artifact — except the divergences upstream-pin.json documents.
    Skips silently when the pin file or Core artifact is absent (post-extraction,
    the pin will point at a fetched release instead of a sibling directory)."""
    import hashlib
    pin_path = os.path.join(ROOT, "upstream-pin.json")
    if not os.path.exists(pin_path):
        return 0, 0
    pin = json.load(open(pin_path))
    core_path = os.path.join(os.path.dirname(ROOT), pin["artifact"])
    if not os.path.exists(core_path):
        print("[SKIP] seam: pinned Core artifact not present (extracted repo?)")
        return 0, 0
    total = passed = 0

    total += 1
    sha = hashlib.sha256(open(core_path, "rb").read()).hexdigest()
    if sha == pin["sha256"]:
        passed += 1; print(f"[PASS] seam: Core artifact matches pin ({sha[:12]}…)")
    else:
        failures.append(("SEAM", "pin", f"expected {pin['sha256']}, got {sha} — "
                         "Core changed; re-review the stub, then update upstream-pin.json deliberately"))
        print("[FAIL] seam: Core artifact does not match upstream-pin.json")

    total += 1
    from rdflib import OWL
    core = Graph(); core.parse(core_path, format="turtle")
    core_terms = {s for s in core.subjects(None, None) if isinstance(s, URIRef)}
    stub = Graph(); stub.parse(os.path.join(ROOT, pin["stub"]), format="turtle")
    allowed = set(pin["documented_divergences"]["classes"]) | \
        set(pin["documented_divergences"]["properties"])
    top_ns = "https://top.scientix.ai/v1#"
    undocumented = sorted(
        str(s) for s in stub.subjects(RDF.type, None)
        if isinstance(s, URIRef) and str(s).startswith(top_ns)
        and s not in core_terms and str(s) not in allowed)
    if not undocumented:
        passed += 1; print("[PASS] seam: every stub top: term exists in pinned Core (divergences documented)")
    else:
        failures.append(("SEAM", "stub-alignment", f"stub terms missing from Core and undocumented: {undocumented}"))
        print(f"[FAIL] seam: undocumented stub divergences: {undocumented}")
    return passed, total


def ncit_verification_checks(failures):
    """The USDM-OWL NCIt anchors must resolve and match against the pinned NCIt release
    (durable record in ontology/vendor/usdm/ncit-verification.json; flat file not vendored)."""
    path = os.path.join(ROOT, "ontology", "vendor", "usdm", "ncit-verification.json")
    if not os.path.exists(path):
        return 0, 0
    s = json.load(open(path))["summary"]
    lt = s.get("label_total", s["total"])
    ok = (s["resolved"] == s["total"] and s["label_match"] >= lt - 3)
    if ok:
        print(f"[PASS] USDM NCIt anchors verified vs NCIt {s['ncit_version']} "
              f"({s['resolved']}/{s['total']} resolve, {s['label_match']}/{lt} labels, "
              f"{s['ddf_tagged']}/{s['total']} DDF-tagged)")
        return 1, 1
    failures.append(("NCIT", "verify", str(s)))
    print(f"[FAIL] NCIt anchor verification regressed: {s}")
    return 0, 1


def usdm_vendor_checks(failures):
    """The vendored, generated USDM v4.0 OWL (external interop layer, crosswalk target)
    must parse and carry the full class footprint. Kept separate from the cr graph."""
    path = os.path.join(ROOT, "ontology", "vendor", "usdm", "usdm-v4.ttl")
    if not os.path.exists(path):
        return 0, 0
    try:
        g = Graph()
        g.parse(path, format="turtle")
    except Exception as e:  # noqa: BLE001
        failures.append(("USDM", "parse", str(e)))
        print(f"[FAIL] vendored USDM-OWL failed to parse: {e}")
        return 0, 1
    owl_class = URIRef("http://www.w3.org/2002/07/owl#Class")
    nclass = len(set(g.subjects(RDF.type, owl_class)))
    if nclass < 80:
        failures.append(("USDM", "classes", f"expected >=80, got {nclass}"))
        print(f"[FAIL] vendored USDM-OWL has only {nclass} classes")
        return 0, 1
    # CT SKOS concept schemes (codelists + permissible values)
    ctpath = os.path.join(ROOT, "ontology", "vendor", "usdm", "usdm-ct-v4.ttl")
    skos = "http://www.w3.org/2004/02/skos/core#"
    nsch = ncon = 0
    if os.path.exists(ctpath):
        try:
            cg = Graph()
            cg.parse(ctpath, format="turtle")
        except Exception as e:  # noqa: BLE001
            failures.append(("USDM", "ct-parse", str(e)))
            print(f"[FAIL] vendored USDM CT SKOS failed to parse: {e}")
            return 0, 1
        nsch = len(set(cg.subjects(RDF.type, URIRef(skos + "ConceptScheme"))))
        ncon = len(set(cg.subjects(RDF.type, URIRef(skos + "Concept"))))
        if nsch < 25 or ncon < 100:
            failures.append(("USDM", "ct-counts", f"schemes={nsch} concepts={ncon}"))
            print(f"[FAIL] USDM CT SKOS thin: {nsch} schemes, {ncon} concepts")
            return 0, 1
    print(f"[PASS] vendored USDM v4.0 OWL ({nclass} classes) + CT SKOS "
          f"({nsch} codelists, {ncon} values) parse")
    return 1, 1


def schedule_checks(ont_graph, failures):
    """SoA bitemporal differentiators: reconstruct the planned schedule as-of a
    transaction time across an amendment, and detect a missed (unrealized) visit."""
    g = Graph()
    for t in ont_graph:
        g.add(t)
    g.parse(os.path.join(ROOT, "examples", "schedule-amendment-asof.ttl"), format="turtle")
    ENC_V2 = "https://top.scientix.ai/examples/asof-enc-v2"

    def window_end_asof(tt):
        q = f"""
        PREFIX cr:  <https://top.scientix.ai/cr/v1#>
        PREFIX top: <https://top.scientix.ai/v1#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?we WHERE {{
          ?pv a cr:PlannedVisit ; cr:projectsEncounter <{ENC_V2}> ;
              cr:windowEnd ?we ; top:recordedAt ?r .
          OPTIONAL {{ ?pv top:supersededAt ?s }}
          FILTER ( ?r <= "{tt}"^^xsd:dateTime
                   && ( !BOUND(?s) || ?s > "{tt}"^^xsd:dateTime ) )
        }}"""
        return sorted(str(row.we)[:10] for row in g.query(q))

    total = passed = 0

    # (a) as-of before the amendment: V2 window end is the original 03-11
    total += 1
    got = window_end_asof("2026-01-15T00:00:00Z")
    if got == ["2026-03-11"]:
        passed += 1; print("[PASS] SoA as-of 2026-01-15 -> V2 window ends 2026-03-11 (pre-amendment)")
    else:
        failures.append(("SCHED", "asof-pre", f"expected ['2026-03-11'], got {got}"))
        print(f"[FAIL] SoA as-of pre-amendment got={got}")

    # (b) as-of after the amendment: the widened 03-14 is in force
    total += 1
    got = window_end_asof("2026-03-01T00:00:00Z")
    if got == ["2026-03-14"]:
        passed += 1; print("[PASS] SoA as-of 2026-03-01 -> V2 window ends 2026-03-14 (post-amendment)")
    else:
        failures.append(("SCHED", "asof-post", f"expected ['2026-03-14'], got {got}"))
        print(f"[FAIL] SoA as-of post-amendment got={got}")

    # (c) missed-visit detection: V3 planned but never realized
    total += 1
    missed = {str(row.pv) for row in g.query("""
        PREFIX cr: <https://top.scientix.ai/cr/v1#>
        SELECT ?pv WHERE {
          <https://top.scientix.ai/examples/asof-sched> cr:hasPlannedVisit ?pv .
          FILTER NOT EXISTS { ?v cr:realizes ?pv }
        }""")}
    if missed == {"https://top.scientix.ai/examples/asof-pv-v3"}:
        passed += 1; print("[PASS] missed-visit detector flags only the unrealized planned V3")
    else:
        failures.append(("SCHED", "missed", f"flagged={sorted(missed)}"))
        print(f"[FAIL] missed-visit detector flagged={sorted(missed)}")

    return passed, total


def view_checks(failures):
    """Single-pull retrieval views: prove EVERY applicable operator screen resolves
    into ONE self-contained NGSI-LD object that carries its green-check facts — so
    the consuming UI never needs a recursive lookup. Guards 'modeled correctly'
    across the whole workflow line."""
    import importlib.util
    p = os.path.join(ROOT, "tools", "ngsild_view.py")
    spec = importlib.util.spec_from_file_location("ngsild_view", p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    total = passed = 0

    def check(desc, fn):
        nonlocal total, passed
        total += 1
        try:
            ok = fn()
        except (KeyError, TypeError, IndexError) as e:
            ok = False; desc = f"{desc} [{type(e).__name__}: {e}]"
        if ok:
            passed += 1; print(f"[PASS] single-pull: {desc}")
        else:
            failures.append(("VIEW", desc, "single-pull object missing required fact"))
            print(f"[FAIL] single-pull: {desc}")

    def val(node, attr):
        return node[attr]["value"]

    # Blood draw — the deep showcase (every green check is one field of one object)
    bd = mod.build_view("blood-draw")
    check("blood-draw: hub + current consent + venipuncture authority",
          lambda: bd["id"] == "urn:bd-coll"
          and val(bd["consent"]["entity"], "status") == "active"
          and bd["authority"]["entity"]["capability"]["object"] == "urn:bd-cap-venip")
    check("blood-draw: ordering held + custody Published + result",
          lambda: bd["afterAct"]["entity"]["observedAt"] < bd["observedAt"]
          and "Published" in [c["entity"]["toState"]["value"] for c in bd["specimen"]["entity"]["custodyChain"]]
          and val(bd["result"]["entity"], "value") == "1:320")

    # Site activation — site + three dated milestones + activator
    sa = mod.build_view("site-activation")
    check("site-activation: IRB + CTA + SIV milestones and site all inlined",
          lambda: sa["irb"]["entity"]["observedAt"][:10] == "2026-01-15"
          and sa["cta"]["entity"]["observedAt"][:10] == "2026-01-20"
          and sa["siv"]["entity"]["observedAt"][:10] == "2026-02-01"
          and sa["site"]["object"] == "urn:site-act")

    # Delegation — parties, capability, credential, attestation
    dg = mod.build_view("delegation")
    check("delegation: delegate+capability+credential+attestation inlined",
          lambda: dg["delegate"]["object"] == "urn:person-nguyen"
          and dg["capability"]["object"] == "urn:cap-consent"
          and dg["credential"]["object"] == "urn:cred-nguyen-gcp"
          and dg["attestation"]["entity"]["attestedBy"]["object"] == "urn:person-rivera")

    # Enrollment — PII person, pseudonymous subject, study
    en = mod.build_view("enrollment")
    check("enrollment: person + subject + study + enroller inlined",
          lambda: en["person"]["object"] == "urn:person-doe"
          and en["subject"]["object"] == "urn:subj-001"
          and en["study"]["object"] == "urn:study-opp101"
          and en["enrolledBy"]["entity"]["name"]["value"].startswith("Nurse"))

    # Consent — subject, performer, authorizing delegation
    co = mod.build_view("consent")
    check("consent: subject + obtainedBy + authorizing delegation inlined",
          lambda: co["forSubject"]["object"] == "urn:subj-001"
          and co["obtainedBy"]["object"] == "urn:person-nguyen"
          and co["authority"]["object"] == "urn:deleg-consent-001")

    # EDC capture — value, PHI class, SDV, the open query
    ed = mod.build_view("edc")
    check("edc: value + PHI class + SDV + open query inlined",
          lambda: val(ed, "value") == "128"
          and val(ed["item"]["entity"], "phiClassification") == "NotPHI"
          and val(ed, "sdvStatus") == "verified"
          and val(ed["query"]["entity"], "resolutionStatus") == "open")

    # Adverse event — subject, type (DLT), onset, reporter
    ae = mod.build_view("adverse-event")
    check("adverse-event: subject + DLT type + onset + reporter inlined",
          lambda: ae["subject"]["object"] == "urn:subj-001"
          and ae["type"] == "DoseLimitingToxicity"
          and ae["observedAt"][:10] == "2026-02-09"
          and ae["reportedBy"]["entity"]["name"]["value"].startswith("Dr."))

    # EOP2 gate — result(+estimand+SAP), agreement, Phase 3 design->dose-opt
    eo = mod.build_view("eop2")
    check("eop2: result+estimand+SAP, agreement, design->dose-opt inlined",
          lambda: val(eo["result"]["entity"], "value") == "0.42"
          and eo["result"]["entity"]["estimand"]["object"] == "urn:est-orr"
          and eo["result"]["entity"]["sap"]["object"] == "urn:sap201"
          and "OS" in eo["agreement"]["entity"]["name"]["value"]
          and "doseOptimization" in eo["phase3Design"]["entity"])

    # Study start-up — 6 typed docs + the three work-stream statuses
    su = mod.build_view("startup-package")
    arts = su["package"]["entity"]["artifacts"]
    ws = {w["entity"]["type"]: w["entity"]["streamStatus"]["value"] for w in su["workStreams"]}
    check("startup: 6 typed package docs + reg/budget complete, clinops active",
          lambda: len(arts) == 6 and all("artifactType" in a["entity"] for a in arts)
          and ws["RegulatoryWorkStream"] == "complete"
          and ws["BudgetContractingWorkStream"] == "complete"
          and ws["ClinOpsWorkStream"] == "active")

    # RBQM — the CtQ factor and the mitigation/monitoring intensity inlined
    rb = mod.build_view("rbqm")
    check("rbqm: high-risk factor + targeted 100% SDV mitigation inlined",
          lambda: val(rb, "riskLevel") == "high"
          and rb["factor"]["object"] == "urn:ctq-pe"
          and val(rb["mitigation"]["entity"], "monitoringStrategy") == "targeted-SDV"
          and val(rb["mitigation"]["entity"], "sdvIntensity") == "1.0")

    # Deviation — the CAPA and the captured antecedent (the missing middle) inlined
    dv = mod.build_view("deviation")
    check("deviation: major + CAPA + captured antecedent (CtQ + signal) inlined",
          lambda: val(dv, "deviationCategory") == "major"
          and val(dv["capa"]["entity"], "capaStatus") == "open"
          and dv["antecedent"]["entity"]["threatens"]["object"] == "urn:ctq-sched"
          and dv["antecedent"]["entity"]["flaggedBy"]["object"] == "urn:sig-late")

    # GCP essential records — source data, audit trail, TMF filing, certified copy
    gc = mod.build_view("gcp")
    check("gcp: source data + audit trail + TMF + certified copy inlined",
          lambda: gc["sourceData"]["object"] == "urn:sd-001"
          and gc["auditTrail"]["object"] == "urn:at-001"
          and gc["tmf"]["object"] == "urn:tmf-001"
          and gc["certifiedCopy"]["object"] == "urn:cc-001")

    # Pre-IND gate — briefing book + the question carrying its proposed position
    pi = mod.build_view("preind")
    check("preind: briefing book + question with proposed position inlined",
          lambda: pi["briefingBook"]["object"] == "urn:bb"
          and pi["question"]["object"] == "urn:q1"
          and val(pi["question"]["entity"], "proposedPosition").startswith("Propose 10 mg"))

    # CSR (A3) — the efficacy section presents the pre-specified TLF AND reports the result
    cs = mod.build_view("csr")
    eff = next(s["entity"] for s in cs["sections"]
               if val(s["entity"], "sectionKind") == "efficacy-results")
    check("csr: efficacy section presents pre-specified TLF + reports its result inlined",
          lambda: eff["presentsTLF"]["entity"]["prespecifiedIn"]["object"] == "urn:sap-a3"
          and val(eff["presentsTLF"]["entity"]["presentsResult"]["entity"], "value") == "0.42"
          and eff["reportsResult"]["object"] == "urn:res-orr-a3")

    # Database lock (A1) — the post-lock value legitimized by a recorded unlock -> the HARD lock
    db = mod.build_view("dblock")
    check("dblock: post-lock value + unlock reopening the hard lock inlined",
          lambda: db["subject"]["object"] == "urn:subj"
          and val(db["underUnlock"]["entity"], "unlockReason").startswith("Late-arriving")
          and val(db["underUnlock"]["entity"]["reopens"]["entity"], "lockType") == "hard")

    # Submission (B1) — the manifest: HARD lock + report + dataset + Define, all inlined
    sb = mod.build_view("submission")
    check("submission: eCTD manifest rests on HARD lock + report + dataset + Define inlined",
          lambda: val(sb["builtOnLock"]["entity"], "lockType") == "hard"
          and sb["includesReport"]["object"] == "urn:csr-b1"
          and sb["includesDataset"]["object"] == "urn:adsl-b1"
          and sb["includesDefine"]["object"] == "urn:define-b1")

    # Recruitment funnel — campaign attribution + eligible screening + conversion
    rc = mod.build_view("recruitment")
    check("recruitment: campaign + eligible screening + conversion to subject inlined",
          lambda: rc["campaign"]["object"] == "urn:rf-campaign"
          and val(rc["screening"]["entity"], "screeningOutcome") == "eligible"
          and rc["conversion"]["entity"]["subject"]["object"] == "urn:rf-subject")

    # Randomization — the blinded kit carries its randomization (arm + subject)
    rz = mod.build_view("randomization")
    check("randomization: kit -> randomization (number + arm + subject) inlined",
          lambda: val(rz, "kitNumber") == "K-1187"
          and val(rz["randomization"]["entity"], "randomizationNumber") == "R-0042"
          and rz["randomization"]["entity"]["arm"]["object"] == "urn:rz-arm")

    # IMP accountability — dispensing to the pseudonymous subject, from the lot
    sp = mod.build_view("supply")
    check("supply: dispensing -> subject + lot + quantity inlined",
          lambda: sp["subject"]["object"] == "urn:sp-subject"
          and sp["lot"]["object"] == "urn:sp-lot"
          and val(sp, "quantityDispensed") == "30")

    # Medical coding — verbatim + code + version + human review
    cg = mod.build_view("coding")
    check("coding: verbatim + assigned code + dictionary version + review inlined",
          lambda: val(cg, "verbatimTerm") == "achy joints"
          and val(cg, "codingDictionaryVersion") == "27.0"
          and val(cg["review"]["entity"], "reviewVerdict") == "approved")

    # Site closeout — closure rests on the COV + balanced reconciliations
    sc = mod.build_view("site-closeout")
    recons = sc["reconciliations"]
    recons = recons if isinstance(recons, list) else [recons]
    check("site-closeout: closure -> COV + balanced reconciliations inlined",
          lambda: sc["closeOutVisit"]["object"] == "urn:sc-cov"
          and len(recons) == 2
          and all(val(r["entity"], "reconciliationOutcome") == "balanced" for r in recons))

    return passed, total


def startup_checks(ont_graph, failures):
    g = Graph()
    for t in ont_graph:
        g.add(t)
    g.parse(os.path.join(ROOT, "examples", "site-activation-enrollment-timing.ttl"), format="turtle")
    act = {}
    for row in g.query("""
        PREFIX cr: <https://top.scientix.ai/cr/v1#>
        PREFIX top: <https://top.scientix.ai/v1#>
        SELECT ?site ?d WHERE { ?a a cr:SiteActivation ; cr:activates ?site ; top:observedAt ?d }"""):
        act[row.site] = row.d.toPython()
    early = set()
    for row in g.query("""
        PREFIX cr: <https://top.scientix.ai/cr/v1#>
        PREFIX top: <https://top.scientix.ai/v1#>
        SELECT ?e ?site ?d WHERE { ?e a cr:Enrollment ; cr:atSite ?site ; top:observedAt ?d }"""):
        a = act.get(row.site)
        if a is not None and row.d.toPython() < a:
            early.add(row.e)
    total = passed = 0
    total += 1
    if EX["enroll-ok"] not in early:
        passed += 1; print("[PASS] enrollment after activation is allowed")
    else:
        failures.append(("STARTUP", "enroll-ok", "should not be flagged")); print("[FAIL] enroll-ok flagged")
    total += 1
    if EX["enroll-early"] in early:
        passed += 1; print("[PASS] enrollment BEFORE site activation is flagged (preventive)")
    else:
        failures.append(("STARTUP", "enroll-early", "should be flagged")); print("[FAIL] enroll-early not flagged")
    return passed, total


def lims_checks(ont_graph, failures):
    g = Graph()
    for t in ont_graph:
        g.add(t)
    g.parse(os.path.join(ROOT, "examples", "lims-specimen-conformant.ttl"), format="turtle")
    # Current state = the toState of the latest custody event (by valid time) for spec-1.
    rows = list(g.query("""
        PREFIX cr: <https://top.scientix.ai/cr/v1#>
        PREFIX top: <https://top.scientix.ai/v1#>
        SELECT ?st ?t WHERE {
          ?ce a cr:CustodyEvent ; cr:specimen <https://top.scientix.ai/examples/spec-1> ;
              cr:toState ?st ; top:observedAt ?t . }"""))
    latest = max(rows, key=lambda r: r.t.toPython()).st.toPython() if rows else None
    if latest == "Published":
        print("[PASS] specimen custody current-state derives to 'Published' (bitemporal chain)")
        return 1, 1
    failures.append(("LIMS", "custody-state", f"expected Published, got {latest}"))
    print(f"[FAIL] custody current-state = {latest}")
    return 0, 1


def preind_checks(ont_graph, failures):
    g = Graph()
    for t in ont_graph:
        g.add(t)
    g.parse(os.path.join(ROOT, "examples", "ind-clock.ttl"), format="turtle")
    inds = {row.ind: row.sub.toPython() for row in g.query("""
        PREFIX cr: <https://top.scientix.ai/cr/v1#>
        PREFIX top: <https://top.scientix.ai/v1#>
        SELECT ?ind ?sub WHERE { ?ind a cr:INDApplication ; top:observedAt ?sub }""")}
    holds = {}
    for row in g.query("""
        PREFIX cr: <https://top.scientix.ai/cr/v1#>
        PREFIX top: <https://top.scientix.ai/v1#>
        SELECT ?ind ?hd WHERE { ?h a cr:ClinicalHold ; cr:placedOn ?ind ; top:observedAt ?hd }"""):
        holds.setdefault(row.ind, []).append(row.hd.toPython())
    on_hold, may_proceed = set(), set()
    for ind, sub in inds.items():
        mpd = sub + timedelta(days=30)
        (on_hold if any(hd <= mpd for hd in holds.get(ind, [])) else may_proceed).add(ind)
    total = passed = 0
    total += 1
    if EX["ind-ok"] in may_proceed:
        passed += 1; print("[PASS] IND with no hold in 30-day window -> may proceed")
    else:
        failures.append(("PREIND", "ind-ok", "expected may-proceed"))
        print("[FAIL] ind-ok should may-proceed")
    total += 1
    if EX["ind-hold"] in on_hold:
        passed += 1; print("[PASS] IND with clinical hold inside 30-day window -> on hold")
    else:
        failures.append(("PREIND", "ind-hold", "expected on-hold"))
        print("[FAIL] ind-hold should be on hold")
    return passed, total


def safety_checks(ont_graph, failures):
    g = Graph()
    for t in ont_graph:
        g.add(t)
    g.parse(os.path.join(ROOT, "examples", "safety-sae.ttl"), format="turtle")
    q = """
        PREFIX cr: <https://top.scientix.ai/cr/v1#>
        SELECT ?rep ?sub ?aware WHERE {
          ?rep a cr:SafetyReport ; cr:submittedAt ?sub ; cr:reportsEvent ?sae .
          ?sae cr:sponsorAwareAt ?aware .
        }"""
    late = set()
    compliant = set()
    for row in g.query(q):
        gap = row.sub.toPython() - row.aware.toPython()
        (late if gap > timedelta(days=15) else compliant).add(row.rep)
    total = passed = 0
    total += 1
    if EX["rep-1"] in compliant and EX["rep-1"] not in late:
        passed += 1; print("[PASS] SAE rep-1 within 15-day expedited clock (compliant)")
    else:
        failures.append(("SAFETY", "rep-1", "expected compliant"))
        print("[FAIL] SAE rep-1 should be compliant")
    total += 1
    if EX["rep-2"] in late:
        passed += 1; print("[PASS] SAE rep-2 breaches 15-day clock (24d) -> flagged")
    else:
        failures.append(("SAFETY", "rep-2", "expected late/flagged"))
        print("[FAIL] SAE rep-2 should be flagged late")
    return passed, total


def demo_checks(failures):
    sys.path.insert(0, os.path.join(ROOT, "demo"))
    try:
        import demo  # noqa: WPS433
        r = demo.run_demo()
    except Exception as e:  # noqa: BLE001
        failures.append(("DEMO", "run", str(e)))
        print(f"[FAIL] demo run: {e}")
        return 0, 1
    ok = bool(r["sdtm_ae"]) and bool(r["doa_log"]) and bool(r["regulator_q"])
    if ok:
        print("[PASS] integration demo emits SDTM AE + DOA log + regulator-query results")
        return 1, 1
    failures.append(("DEMO", "empty", f"{ {k: len(v) for k, v in r.items()} }"))
    print("[FAIL] integration demo produced an empty view")
    return 0, 1


def projection_checks(ont_graph, failures):
    spec_path = os.path.join(ROOT, "projections", "expectations.json")
    if not os.path.exists(spec_path):
        return 0, 0
    specs = json.load(open(spec_path))
    passed = total = 0
    for spec in specs:
        total += 1
        g = Graph()
        for t in ont_graph:
            g.add(t)
        g.parse(os.path.join(ROOT, spec["source"]), format="turtle")
        query = open(os.path.join(ROOT, spec["query"])).read()
        res = g.query(query)
        rows = [{str(v): str(row[v]) for v in res.vars if row[v] is not None}
                for row in res]
        problems = []
        if "expect_rows" in spec:
            problems += [f"missing row {exp}" for exp in spec["expect_rows"]
                         if not any(all(r.get(k) == val for k, val in exp.items())
                                    for r in rows)]
        if "expect_min_rows" in spec and len(rows) < spec["expect_min_rows"]:
            problems.append(f"expected >={spec['expect_min_rows']} rows, got {len(rows)}")
        if "expect_vars" in spec:
            got_vars = {str(v) for v in res.vars}
            problems += [f"missing var ?{v}" for v in spec["expect_vars"]
                         if v not in got_vars]
        if not problems:
            passed += 1
            print(f"[PASS] {spec['desc']}")
        else:
            failures.append(("PROJ", spec["query"], f"{problems}; got {rows}"))
            print(f"[FAIL] {spec['desc']}  {problems}")
    return passed, total


def bitemporal_checks(ont_graph, failures):
    g = Graph()
    for t in ont_graph:
        g.add(t)
    g.parse(os.path.join(ROOT, "examples", "bitemporal-asof.ttl"), format="turtle")
    total = passed = 0

    def asof(tt):
        q = f"""
        PREFIX cr:  <https://top.scientix.ai/cr/v1#>
        PREFIX top: <https://top.scientix.ai/v1#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?val WHERE {{
          ?o cr:forSubject <https://top.scientix.ai/examples/subj-bt> ;
             rdf:value ?val ; top:recordedAt ?r .
          OPTIONAL {{ ?o top:supersededAt ?s }}
          FILTER ( ?r <= "{tt}"^^xsd:dateTime
                   && ( !BOUND(?s) || ?s > "{tt}"^^xsd:dateTime ) )
        }}"""
        return sorted(str(row.val) for row in g.query(q))

    # as-of 2026-02-17: the system believed 4.2
    total += 1
    got = asof("2026-02-17T00:00:00Z")
    if got == ["4.2"]:
        passed += 1; print("[PASS] bitemporal as-of 2026-02-17 -> 4.2 (pre-correction)")
    else:
        failures.append(("BITEMP", "as-of-02-17", f"expected ['4.2'], got {got}"))
        print(f"[FAIL] bitemporal as-of 2026-02-17  got={got}")

    # as-of 2026-02-21: after the correction, it believes 5.1
    total += 1
    got = asof("2026-02-21T00:00:00Z")
    if got == ["5.1"]:
        passed += 1; print("[PASS] bitemporal as-of 2026-02-21 -> 5.1 (post-correction)")
    else:
        failures.append(("BITEMP", "as-of-02-21", f"expected ['5.1'], got {got}"))
        print(f"[FAIL] bitemporal as-of 2026-02-21  got={got}")

    # back-dating detector: flag provenanced entities with >30d valid/transaction gap
    total += 1
    flagged = set()
    for s in set(g.subjects(TOP.observedAt, None)):
        vf = g.value(s, TOP.observedAt)
        ra = g.value(s, TOP.recordedAt)
        if vf is None or ra is None:
            continue
        gap = ra.toPython() - vf.toPython()
        if gap > timedelta(days=30):
            flagged.add(s)
    # ProtocolVersion/Attestation are ProvenancedEntity; only the suspicious one has a >30d gap
    if flagged == {EX["attest-suspicious"]}:
        passed += 1; print("[PASS] back-dating detector flags only attest-suspicious (~73d gap)")
    else:
        failures.append(("BITEMP", "back-dating", f"flagged={sorted(map(str,flagged))}"))
        print(f"[FAIL] back-dating detector  flagged={sorted(map(str,flagged))}")

    return passed, total


def _report(sections, failures):
    summary = " | ".join(f"{name}: {p}/{t}" for name, p, t in sections)
    print(f"\n{summary} | parse errors: {len([x for x in failures if x[0]=='PARSE'])}")
    if failures:
        print("\nFAILURES:")
        for typ, f, msg in failures:
            print(f"  {typ} {f}: {msg}")
        sys.exit(1)
    print("ALL GREEN")
    sys.exit(0)


if __name__ == "__main__":
    main()
