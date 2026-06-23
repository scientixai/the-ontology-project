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


# The flat single-entity renderer that used bare Relationship->URN refs (and so
# implied recursive lookups) has been retired: every stop now renders the actual
# shape-bounded `?join=inline` object produced by tools/ngsild_view.py, where the
# linked entities are inlined. See render_stop().


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
# because the ONE returned object carries the exact field behind it — `reads` is
# the JSON path into that single object (no second query). Every value here is
# present in examples/blood-draw-context-conformant.ttl and surfaced by the
# shape-bounded view (views/blood-draw-admissibility.ttl).
BLOOD_DRAW_CHAIN = [
    {"check": "Participant verified &amp; consent current", "who": "Tom Nguyen, RN",
     "params": [("Subject", "BD-S-001 (pseudonymous)"),
                ("Consent for", "<code>consent.forSubject == urn:bd-subj</code>"),
                ("Consent current", "<code>consent.status == &quot;active&quot;</code>")],
     "reads": "consent.entity",
     "shape": "cr:InformedConsentShape (bitemporal)"},
    {"check": "Phlebotomist authorized for venipuncture", "who": "Mary Smith, Phlebotomist",
     "params": [("Delegate", "<code>authority.delegate == urn:bd-phleb</code>"),
                ("Capability", "<code>authority.capability == urn:bd-cap-venip</code>"),
                ("Credential", "<code>authority.credential == urn:bd-cred-phleb</code>")],
     "reads": "authority.entity",
     "shape": "cr:CapabilityDelegationShape (hard)"},
    {"check": "Drawn after the ECG (ordering held)", "who": "Mary Smith, Phlebotomist",
     "params": [("ECG act", "<code>afterAct.observedAt == 2026-03-02T09:00</code>"),
                ("Draw", "<code>observedAt == 2026-03-02T11:00</code>"),
                ("Order", "&#10003; 09:00 &lt; 11:00")],
     "reads": "afterAct.entity + (root).observedAt",
     "shape": "cr:ActivityOrderingShape"},
    {"check": "Specimen collected &amp; custody opened", "who": "Mary Smith, Phlebotomist",
     "params": [("Primary specimen", "<code>specimen.id == urn:bd-spec</code>"),
                ("Collected (valid)", "<code>(root).observedAt</code>"),
                ("Recorded (txn)", "<code>(root).recordedAt</code>")],
     "reads": "specimen.entity + (root)",
     "shape": "cr:SpecimenOriginShape + cr:CustodyEventShape"},
    {"check": "Custody current-state = Published", "who": "Raj Patel, Lab Technician",
     "params": [("Chain", "Received &rarr; Verified &rarr; Published"),
                ("Current", "<code>specimen.custodyChain[*].toState</code> &#8715; "
                            "<span class='pill ok'>Published</span>")],
     "reads": "specimen.custodyChain",
     "shape": "bitemporal custody current-state derivation"},
    {"check": "Aliquot &amp; result trace to the draw", "who": "Raj Patel, Lab Technician",
     "params": [("Aliquot", "<code>specimen.aliquot == urn:bd-aliquot</code>"),
                ("Result", "<code>result.value == &quot;1:320&quot;</code>"),
                ("Lineage", "result &rarr; derivedFromCollection &rarr; this draw")],
     "reads": "specimen.aliquot + result.entity",
     "shape": "prov:wasDerivedFrom* (cr:derivedFromCollection)"},
    {"check": "Audit trail present (ALCOA++)", "who": "System of record",
     "params": [("Every inlined entity carries", "<code>observedAt + createdAt + status</code>"),
                ("Reconstructable", "&#10003; as-of any date, from this one object")],
     "reads": "(every entity in the object)",
     "shape": "top:BitemporalProvShape"},
]


def _provenance_screen(title, subtitle, badge, chain):
    rows = ""
    for c in chain:
        params = "".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in c["params"])
        if c.get("reads"):
            params += f'<tr><td>reads (from the one object)</td><td><code>{c["reads"]}</code></td></tr>'
        params += f'<tr><td>gated by</td><td><code>{c["shape"]}</code></td></tr>'
        rows += (f'<div class="chk"><div class="chk-head"><span class="ck">&#10003;</span>'
                 f'<b>{c["check"]}</b><span class="who">{c["who"]}</span></div>'
                 f'<details><summary>why it&rsquo;s green</summary>'
                 f'<table class="prov">{params}</table></details></div>')
    return (f'<div class="screen"><div class="scr-head">{title}<span class="badge">{badge}</span>'
            f'<div class="scr-sub">{subtitle}</div></div>'
            f'<div class="chk-intro">Every check reads a field of the <b>single object</b> on the right '
            f'(its <code>reads</code> path) &mdash; the UI issues one query, never a recursive lookup.</div>{rows}</div>')


def _screen(title, subtitle, rows, badge):
    rh = "".join(f'<div class="scr-row"><span>{k}</span><b>{v}</b></div>' for k, v in rows)
    return (f'<div class="screen"><div class="scr-head">{title}<span class="badge">{badge}</span>'
            f'<div class="scr-sub">{subtitle}</div></div>{rh}</div>')


SPEC_BY_NAME = {s[0]: s for s in SPECS}


# Each operator screen maps to a retrieval view in tools/ngsild_view.py — so
# every stop shows the ONE query + the single self-contained object it returns.
SCREEN_VIEW = {
    "Site activation": "site-activation",
    "Delegation": "delegation",
    "Enrollment": "enrollment",
    "Informed consent": "consent",
    "Blood draw": "blood-draw",
    "EDC capture": "edc",
    "Adverse event": "adverse-event",
    "EOP2 gate": "eop2",
    "Study start-up": "startup-package",
}

_VIEW_MOD = None


def _view_mod(root):
    """Load tools/ngsild_view.py once (the real traversal that emits the objects)."""
    global _VIEW_MOD
    if _VIEW_MOD is None:
        import importlib.util
        p = os.path.join(root, "tools", "ngsild_view.py")
        spec = importlib.util.spec_from_file_location("ngsild_view", p)
        _VIEW_MOD = importlib.util.module_from_spec(spec); spec.loader.exec_module(_VIEW_MOD)
    return _VIEW_MOD


def render_stop(root, name):
    """Render one stop's split view: operator screen + the one NGSI-LD query and
    the single self-contained object that drives it (no recursive lookups)."""
    import html as _html
    spec = SPEC_BY_NAME.get(name)
    if not spec:
        return ""
    _name, fname, title, sub, badge, rows, ids = spec
    if name == "Blood draw":
        left = _provenance_screen("Specimen &mdash; admissibility at the bench",
                                  "Subject BD-S-001 &middot; one entity, fully expanded", "LIMS",
                                  BLOOD_DRAW_CHAIN)
    else:
        left = _screen(title, sub, rows, badge)
    vkey = SCREEN_VIEW[name]
    mod = _view_mod(root)
    query = mod.query_for(vkey)
    objbody = _html.escape(json.dumps(mod.build_view(vkey), indent=2))
    right = (f'<div class="jsoncap">the <b>one</b> query the screen issues</div>'
             f'<pre class="json q">{_html.escape(query)}</pre>'
             f'<div class="jsoncap">the <b>single object</b> it returns &mdash; related entities '
             f'inlined per the shape (ETSI GS CIM 009 <code>join=inline</code>), '
             f'<b>zero recursive lookups</b></div>'
             f'<pre class="json">{objbody}</pre>')
    return (f'<div class="splitstop"><div class="split"><div>{left}</div>'
            f'<div>{right}</div></div></div>')


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
             'worked examples, in the NGSI-LD runtime shape, carrying its own time and provenance.</p>'
             '<p class="principle">The test of the model: an operator should pull <b>one</b> entity and get '
             'every fact behind the green check &mdash; no recursive lookups. <b>Every stop below</b> proves it: '
             'beside each screen is the single NGSI-LD <code>?join=inline</code> query it issues and the one '
             'self-contained object it returns, whose related entities are inlined <b>per a SHACL retrieval '
             'view</b> (<code>views/</code>), faithfully to ETSI GS CIM 009 (forward traversal only). The '
             '<b>Blood draw</b> stop is the deep dive: each check there cites the <code>reads</code> path it '
             'pulls from that one object.</p>')
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
.jsoncap{font-size:12px;color:var(--mut);margin:10px 0 4px}
.jsoncap:first-child{margin-top:0}
pre.json{margin:0;max-height:420px}
pre.json.q{max-height:none;background:#0b2530;color:#cde8ef;border-color:#0b2530}
p.principle{background:var(--pale);border-left:3px solid var(--accent);padding:10px 12px;border-radius:0 8px 8px 0;font-size:14px}
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
