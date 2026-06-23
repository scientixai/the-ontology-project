#!/usr/bin/env python3
"""Operator-screen mockups for the docs: a workflow 'train line' where each stop shows
the operator-facing screen next to the NGSI-LD JSON (derived from the real worked
examples) that drives it. Imported by build_docs.py.

Adding a stop = adding a spec to SPECS (example file + screen rows + entity IRIs for JSON).
"""
import json
import os
from rdflib import Graph, RDF, RDFS, URIRef, Literal

TOP = "https://top.scientix.ai/core/v1#"
PROV = "http://www.w3.org/ns/prov#"
RDFVAL = "http://www.w3.org/1999/02/22-rdf-syntax-ns#value"
E = "https://top.scientix.ai/examples/"


def _ln(uri):
    return str(uri).split("#")[-1].split("/")[-1]


def ngsild(g, iri):
    """Render one graph entity as NGSI-LD-style JSON (truthful: straight from the TTL)."""
    iri = URIRef(iri)
    types = [_ln(t) for t in g.objects(iri, RDF.type)]
    pref = [t for t in types if t not in ("ProvenancedEntity", "Observation", "Agent", "Person")]
    d = {"id": "urn:" + _ln(iri), "type": (pref or types or ["Thing"])[0]}
    for p, o in g.predicate_objects(iri):
        ps = str(p)
        if p == RDF.type:
            continue
        if ps == str(RDFS.label):
            d["name"] = {"type": "Property", "value": str(o)}
        elif ps == TOP + "observedAt":
            d["observedAt"] = str(o)
        elif ps == TOP + "recordedAt":
            d["recordedAt (createdAt)"] = str(o)
        elif ps == TOP + "supersededAt":
            d["supersededAt"] = str(o)
        elif ps == RDFVAL:
            d["value"] = {"type": "Property", "value": str(o)}
        elif ps == PROV + "wasAttributedTo":
            d["attributedTo"] = {"type": "Relationship", "object": "urn:" + _ln(o)}
        elif ps == PROV + "wasDerivedFrom":
            d["derivedFrom"] = {"type": "Relationship", "object": "urn:" + _ln(o)}
        elif isinstance(o, URIRef):
            d[_ln(p)] = {"type": "Relationship", "object": "urn:" + _ln(o)}
        elif isinstance(o, Literal):
            d[_ln(p)] = {"type": "Property", "value": str(o)}
    return d


# Each stop: (name, example file, screen title, subtitle, badge, [(label, valueHTML)...], [entity localnames])
SPECS = [
    ("Site activation", "site-activation-conformant.ttl",
     "Site activation &mdash; green light", "Denver Cancer Center", "CTMS",
     [("Site", "Denver Cancer Center"), ("IRB/IEC approval", "&#10003; 2026-01-15"),
      ("CTA", "&#10003; executed 2026-01-20"), ("Site initiation visit", "&#10003; 2026-02-01"),
      ("Activated", "<span class='pill ok'>2026-02-05</span>"), ("Target accrual", "20 subjects")],
     ["act1"]),
    ("Delegation", "oncology-fih-conformant.ttl",
     "Delegation of authority", "Study OPP-101", "eReg",
     [("Principal investigator", "Dr. Ana Rivera, PI"), ("Delegate", "Tom Nguyen, RN &mdash; Study Nurse"),
      ("Capability", "Obtain informed consent"), ("Credential", "&#10003; GCP + consent training"),
      ("Effective", "2026-02-03"), ("Attested", "<span class='pill ok'>via SMS, by PI</span>")],
     ["deleg-consent-001", "attest-deleg-001"]),
    ("Enrollment", "oncology-fih-conformant.ttl",
     "Enrollment", "Study OPP-101", "EDC",
     [("Person", "Jane Doe, Participant <span class='muted'>(PII &mdash; stays at site)</span>"),
      ("Subject", "OPP-101 S-001 <span class='muted'>(pseudonymous)</span>"),
      ("Study", "OPP-101 (Phase 1 FIH)"), ("Enrolled", "2026-02-05"),
      ("Enrolled by", "Jo Santos, CRC")],
     ["enroll-001"]),
    ("Informed consent", "oncology-fih-conformant.ttl",
     "Informed consent", "Subject OPP-101 S-001", "eConsent",
     [("Subject", "OPP-101 S-001"), ("Obtained by", "Tom Nguyen, RN &mdash; Study Nurse"),
      ("Under delegation", "<span class='pill ok'>&#10003; consent delegation</span>"),
      ("Obtained", "2026-02-05 09:45")],
     ["consent-001"]),
    ("Blood draw", "lims-specimen-conformant.ttl",
     "Specimen &mdash; chain of custody", "Site: Denver Cancer Center", "LIMS",
     [("Subject", "LIMS-S-001 <span class='muted'>(pseudonymous)</span>"),
      ("Collected at", "Cycle 1 Day 1 visit (blood draw)"), ("Primary specimen", "Whole blood"),
      ("Custody status", "<span class='pill ok'>Published</span>"), ("Aliquot", "Serum aliquot -P01"),
      ("Assay result", "NAb titer = 1:320"), ("Attested by", "Lab technician")],
     ["spec-1", "res-nab"]),
    ("EDC capture", "edc-conformant.ttl",
     "EDC &mdash; Vitals CRF", "Visit: Cycle 1 Day 1", "EDC",
     [("Subject", "EDC-S-001 <span class='muted'>(pseudonymous)</span>"),
      ("Item", "Systolic Blood Pressure"), ("Value", "<b>128</b> mmHg"), ("PHI class", "NotPHI"),
      ("SDV", "<span class='pill ok'>Verified</span> by Silvia Rodriguez, CRA"),
      ("Open query", "<span class='pill warn'>Confirm SBP units</span>"), ("Entered by", "Jo Santos, CRC")],
     ["obs1", "q1"]),
    ("Adverse event", "oncology-fih-conformant.ttl",
     "Adverse event", "Subject OPP-101 S-001", "Safety",
     [("Subject", "OPP-101 S-001"), ("Event", "Grade 3 neutropenia"),
      ("Type", "<span class='pill warn'>Dose-limiting toxicity</span>"), ("Onset", "2026-02-09"),
      ("Reported by", "Dr. Ana Rivera, PI")],
     ["ae-001"]),
    ("EOP2 gate", "eop2-conformant.ttl",
     "End-of-Phase-2 gate", "Study OPP-201", "Regulatory",
     [("Study", "OPP-201 (Phase 2)"), ("Primary result", "ORR = 0.42"),
      ("Estimand", "<span class='pill ok'>&#10003; pre-specified</span>"),
      ("Analyzed under", "&#10003; SAP v1.0"), ("FDA agreement", "primary endpoint = OS"),
      ("Phase 3 design", "RP2D (Project Optimus)")],
     ["res-orr", "eop2"]),
    ("Study start-up", "startup-package-conformant.ttl",
     "Study start-up &mdash; package &amp; work streams", "Site 701 — Denver", "eReg",
     [("Start-up package", "6 documents, all typed"),
      ("Regulatory", "<span class='pill ok'>complete</span> &mdash; ICF, DoA, 1572, IRB"),
      ("Budget &amp; contracting", "<span class='pill ok'>complete</span> &mdash; signed CTA"),
      ("Clinical operations", "<span class='pill warn'>active</span>"),
      ("Activation gate", "<span class='pill ok'>Reg + Budget complete &rarr; SIV</span>"),
      ("Activated", "2026-02-05 &middot; Start-up manager")],
     ["sp-pkg", "ws-reg"]),
]


# The blood draw decomposed into its evidentiary chain. Each checkpoint is green
# because the model carries the exact parameters behind it — addressable, not buried.
# (Illustrative values, drawn from the LIMS + delegation + schedule worked examples.)
BLOOD_DRAW_CHAIN = [
    {"check": "Participant verified &amp; consent current", "who": "Jo Santos, CRC",
     "params": [("Subject", "LIMS-S-001 (pseudonymous)"),
                ("Consent obtained", "2026-02-05 by Tom Nguyen, RN"),
                ("Valid at draw", "&#10003; not withdrawn as-of 2026-03-02")],
     "shape": "cr:InformedConsent (bitemporal)"},
    {"check": "Phlebotomist authorized for venipuncture", "who": "Mary Smith, Phlebotomist",
     "params": [("Capability", "Venipuncture / specimen collection"),
                ("Delegated by", "Dr. Ana Rivera, PI"),
                ("Credential", "&#10003; phlebotomy cert + GCP"),
                ("Effective window", "2026-01-28 &rarr; (open); active at draw")],
     "shape": "cr:CapabilityDelegationShape (hard) + cr:DelegationTimingShape"},
    {"check": "Drawn in-window, after the ECG", "who": "Mary Smith, Phlebotomist",
     "params": [("SoA rule", "bloods 2h after the ECG (ordering)"),
                ("ECG performed", "2026-03-02 09:00"), ("Blood drawn", "2026-03-02 11:00"),
                ("Visit window", "&#10003; within Cycle 1 Day 1")],
     "shape": "cr:ActivityOrderingShape + cr:VisitWindowShape"},
    {"check": "Specimen collected &amp; custody opened", "who": "Mary Smith, Phlebotomist",
     "params": [("Primary specimen", "Whole blood"),
                ("Collected (valid time)", "2026-03-02 11:00"),
                ("Recorded (txn time)", "2026-03-02 11:05"),
                ("Attributed to", "Mary Smith, Phlebotomist"), ("Custody state", "Received")],
     "shape": "cr:SpecimenOriginShape + cr:CustodyEventShape"},
    {"check": "Aliquot traces back to the draw", "who": "Raj Patel, Lab Technician",
     "params": [("Aliquot", "Serum aliquot -P01"),
                ("Derived from", "whole-blood primary &rarr; collection event"),
                ("Lineage view", "projections/specimen_lineage.rq")],
     "shape": "prov:wasDerivedFrom* (custody chain)"},
    {"check": "Assay result attributed &amp; current", "who": "Raj Patel, Lab Technician",
     "params": [("Result", "NAb titer = 1:320"),
                ("Custody current-state", "<span class='pill ok'>Published</span> (bitemporal)"),
                ("Attributed to", "Raj Patel, Lab Technician")],
     "shape": "bitemporal custody current-state derivation"},
    {"check": "Audit trail present (ALCOA++)", "who": "System of record",
     "params": [("Every step carries", "observedAt + recordedAt + wasAttributedTo"),
                ("Reconstructable", "&#10003; as-of any date")],
     "shape": "cr:SourceDataAuditTrailShape + top:BitemporalProvShape"},
]


def _provenance_screen(title, subtitle, badge, chain):
    rows = ""
    for c in chain:
        params = "".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in c["params"])
        params += f'<tr><td>gated by</td><td><code>{c["shape"]}</code></td></tr>'
        rows += (f'<div class="chk"><div class="chk-head"><span class="ck">&#10003;</span>'
                 f'<b>{c["check"]}</b><span class="who">{c["who"]}</span></div>'
                 f'<details><summary>why it&rsquo;s green</summary>'
                 f'<table class="prov">{params}</table></details></div>')
    return (f'<div class="screen"><div class="scr-head">{title}<span class="badge">{badge}</span>'
            f'<div class="scr-sub">{subtitle}</div></div>'
            f'<div class="chk-intro">Each check is backed by addressable model facts &mdash; '
            f'open one to see the exact parameters that make it green.</div>{rows}</div>')


def _screen(title, subtitle, rows, badge):
    rh = "".join(f'<div class="scr-row"><span>{k}</span><b>{v}</b></div>' for k, v in rows)
    return (f'<div class="screen"><div class="scr-head">{title}<span class="badge">{badge}</span>'
            f'<div class="scr-sub">{subtitle}</div></div>{rh}</div>')


SPEC_BY_NAME = {s[0]: s for s in SPECS}


def render_stop(root, name):
    """Render one stop's split view (operator screen + NGSI-LD from its example)."""
    spec = SPEC_BY_NAME.get(name)
    if not spec:
        return ""
    _name, fname, title, sub, badge, rows, ids = spec
    g = Graph(); g.parse(os.path.join(root, "examples", fname), format="turtle")
    objs = [ngsild(g, E + i) for i in ids]
    body = json.dumps(objs if len(objs) > 1 else objs[0], indent=2)
    if name == "Blood draw":
        left = _provenance_screen("Specimen &mdash; evidentiary chain",
                                  "Subject LIMS-S-001 &middot; Denver Cancer Center", "LIMS",
                                  BLOOD_DRAW_CHAIN)
    else:
        left = _screen(title, sub, rows, badge)
    return (f'<div class="splitstop"><div class="split"><div>{left}</div>'
            f'<div><div class="jsoncap">the data behind the screen &mdash; NGSI-LD, from the graph</div>'
            f'<pre class="json">{body}</pre></div></div></div>')


def render_stops(root):
    chips = ""
    names = [s[0] for s in SPECS]
    for i, name in enumerate(names):
        chips += f'<div class="tstop live">{name}</div>'
        if i < len(names) - 1:
            chips += '<div class="trail"></div>'
    intro = ('<p>The reference graph isn\'t an abstraction &mdash; it\'s what powers the screens an '
             'operator actually uses. Below is the trial as a <b>workflow line</b>; each stop is a '
             'screen, and the panel beside it is the <b>real data behind it</b> &mdash; generated from the '
             'worked examples, in the NGSI-LD runtime shape, carrying its own time and provenance.</p>')
    out = [intro, f'<div class="trainline">{chips}</div>']
    for name in names:
        out.append(f'<div class="splitstop"><h4 class="stopname">&#128205; {name}</h4>' + render_stop(root, name)[len('<div class="splitstop">'):])
    return "\n".join(out)


SCREEN_CSS = """
.trainline{display:flex;align-items:center;flex-wrap:wrap;gap:4px 0;margin:14px 0 26px}
.tstop{font-size:12px;padding:6px 10px;border:1px solid var(--line);border-radius:16px;background:var(--card);color:var(--mut);white-space:nowrap}
.tstop.live{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
.trail{width:14px;height:2px;background:var(--accent);opacity:.55}
.splitstop{margin:22px 0}
.stopname{margin:0 0 8px;color:var(--ink)}
.split{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start}
.screen{border:1px solid var(--line);border-radius:12px;background:var(--card);overflow:hidden;box-shadow:0 1px 3px rgba(20,40,80,.06)}
.scr-head{background:linear-gradient(180deg,#0e7490,#0b5563);color:#fff;padding:12px 14px;font-weight:600;position:relative}
.scr-sub{font-weight:400;font-size:12px;opacity:.85;margin-top:2px}
.badge{position:absolute;right:12px;top:12px;background:rgba(255,255,255,.2);font-size:11px;padding:2px 8px;border-radius:10px}
.scr-row{display:flex;justify-content:space-between;gap:10px;padding:9px 14px;border-top:1px solid var(--line);font-size:14px}
.scr-row span{color:var(--mut)}
.muted{color:var(--mut);font-weight:400;font-size:12px}
.pill{font-size:12px;font-weight:600;padding:1px 8px;border-radius:10px}
.pill.ok{background:#e7f6ee;color:var(--ok)}.pill.warn{background:#fdf4e3;color:var(--warn)}
.jsoncap{font-size:12px;color:var(--mut);margin-bottom:4px}
pre.json{margin:0;max-height:420px}
.chk-intro{padding:8px 14px;font-size:12px;color:var(--mut);background:var(--pale);border-top:1px solid var(--line)}
.chk{border-top:1px solid var(--line);padding:9px 14px}
.chk-head{display:flex;align-items:center;gap:8px;font-size:14px}
.chk .ck{color:var(--ok);font-weight:700}
.chk .who{margin-left:auto;font-size:12px;color:var(--mut);white-space:nowrap}
.chk details{margin-top:5px}
.chk summary{cursor:pointer;font-size:12px;color:var(--accent);list-style:none}
.chk summary::-webkit-details-marker{display:none}
.chk summary::before{content:'\\25B8 ';color:var(--accent)}
.chk details[open] summary::before{content:'\\25BE '}
table.prov{width:100%;border-collapse:collapse;margin:6px 0 2px}
table.prov td{border-top:1px solid var(--line);padding:4px 6px;font-size:12px;color:var(--ink);vertical-align:top}
table.prov td:first-child{color:var(--mut);width:40%;white-space:nowrap}
@media(max-width:760px){.split{grid-template-columns:1fr}}
"""
