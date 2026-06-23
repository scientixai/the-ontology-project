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
TOP = Namespace("https://top.scientix.ai/core/v1#")
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

    # (b) SHACL cases (severity-aware)
    cases = json.load(open(os.path.join(ROOT, "tests", "manifest.json")))
    passed = 0
    for c in cases:
        data = Graph()
        data.parse(os.path.join(ROOT, c["file"]), format="turtle")
        _, report, _ = validate(
            data, shacl_graph=shapes_graph, ont_graph=ont_graph,
            inference="rdfs", advanced=True,
        )
        v, w, _i = severity_counts(report)
        got = outcome(v, w)
        ok = got == c["expect"]
        if ok:
            passed += 1
        else:
            failures.append(("SHACL", c["file"],
                             f"expected {c['expect']}, got {got} (V={v} W={w})"))
        print(f"[{'PASS' if ok else 'FAIL'}] "
              f"{c['desc']}  [{got}]")

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

    _report([
        ("SHACL", passed, len(cases)),
        ("bitemporal", bt_passed, bt_total),
        ("projections", pj_passed, pj_total),
        ("demo", dm_passed, dm_total),
        ("safety", sf_passed, sf_total),
        ("pre-IND", pi_passed, pi_total),
        ("lims", lm_passed, lm_total),
        ("startup", su_passed, su_total),
        ("schedule", sd_passed, sd_total),
    ], failures)


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
        PREFIX top: <https://top.scientix.ai/core/v1#>
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


def startup_checks(ont_graph, failures):
    g = Graph()
    for t in ont_graph:
        g.add(t)
    g.parse(os.path.join(ROOT, "examples", "site-activation-enrollment-timing.ttl"), format="turtle")
    act = {}
    for row in g.query("""
        PREFIX cr: <https://top.scientix.ai/cr/v1#>
        PREFIX top: <https://top.scientix.ai/core/v1#>
        SELECT ?site ?d WHERE { ?a a cr:SiteActivation ; cr:activates ?site ; top:observedAt ?d }"""):
        act[row.site] = row.d.toPython()
    early = set()
    for row in g.query("""
        PREFIX cr: <https://top.scientix.ai/cr/v1#>
        PREFIX top: <https://top.scientix.ai/core/v1#>
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
        PREFIX top: <https://top.scientix.ai/core/v1#>
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
        PREFIX top: <https://top.scientix.ai/core/v1#>
        SELECT ?ind ?sub WHERE { ?ind a cr:INDApplication ; top:observedAt ?sub }""")}
    holds = {}
    for row in g.query("""
        PREFIX cr: <https://top.scientix.ai/cr/v1#>
        PREFIX top: <https://top.scientix.ai/core/v1#>
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
        missing = [exp for exp in spec["expect_rows"]
                   if not any(all(r.get(k) == val for k, val in exp.items())
                              for r in rows)]
        if not missing:
            passed += 1
            print(f"[PASS] {spec['desc']}")
        else:
            failures.append(("PROJ", spec["query"], f"missing rows {missing}; got {rows}"))
            print(f"[FAIL] {spec['desc']}  missing={missing}")
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
        PREFIX top: <https://top.scientix.ai/core/v1#>
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
