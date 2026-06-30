#!/usr/bin/env python3
"""Generate the TOP CR documentation as a multi-page site:
  index.html (hub) + foundation.html + one page per flow/sub-domain + reference.html
Narrative leads; entity/constraint/projection reference is auto-generated from the model.
Run: python3 cr-domain/docs/build_docs.py
"""
import glob
import html
import json
import os
import sys

from rdflib import Graph, RDF, RDFS, OWL, URIRef, Literal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_screens import render_stop, SCREEN_CSS  # noqa: E402
from build_dist import MAST  # noqa: E402  (masthead: single source of truth for version/license/authorship)

TOP = "https://top.scientix.ai/v1#"
CLOS = ["Agent", "Location", "Resource", "Scope", "Temporal", "Evidence", "Outcome", "Constraint"]
SH = "http://www.w3.org/ns/shacl#"


def esc(x):
    return html.escape(str(x)) if x is not None else ""


def qn(uri):
    u = str(uri)
    for pfx, ns in (("top:", TOP), ("hcls:", "https://top.scientix.ai/hcls/v1#"),
                    ("cr:", "https://top.scientix.ai/cr/v1#"), ("cx:", "https://top.scientix.ai/crosswalk/v1#"),
                    ("tmf:", "https://top.scientix.ai/tmf/v1#")):
        if u.startswith(ns):
            return pfx + u[len(ns):]
    return u


# ---------------------------------------------------------------- model load
PER_FILE = {}        # filename -> [class iris]
IDX = {}             # localname -> iri
MERGED = Graph()
for f in sorted(glob.glob(os.path.join(ROOT, "ontology", "*.ttl"))):
    g = Graph(); g.parse(f, format="turtle"); MERGED += g
    iris = [s for s in g.subjects(RDF.type, OWL.Class) if isinstance(s, URIRef)]
    PER_FILE[os.path.basename(f)] = iris
    for s in iris:
        IDX[str(s).split("#")[-1]] = s


def clo_of(cls):
    seen, fr = set(), [cls]
    while fr:
        c = fr.pop()
        if c in seen:
            continue
        seen.add(c)
        if str(c).startswith(TOP) and str(c).split("#")[-1] in CLOS:
            return str(c).split("#")[-1]
        for p in MERGED.objects(c, RDFS.subClassOf):
            if isinstance(p, URIRef):
                fr.append(p)
    return "—"


def all_shapes():
    g = Graph()
    for f in glob.glob(os.path.join(ROOT, "shapes", "*.ttl")):
        g.parse(f, format="turtle")
    SHN = lambda t: URIRef(SH + t)
    out = {}
    for s in g.subjects(RDF.type, SHN("NodeShape")):
        target = (g.value(s, SHN("targetClass")) or g.value(s, SHN("targetObjectsOf"))
                  or g.value(s, SHN("targetSubjectsOf")))
        sev = g.value(s, SHN("severity"))
        msgs = []
        for _, _, n in g.triples((s, SHN("property"), None)):
            msgs += [str(m) for m in g.objects(n, SHN("message"))]
        for _, _, n in g.triples((s, SHN("sparql"), None)):
            msgs += [str(m) for m in g.objects(n, SHN("message"))]
        msgs += [str(m) for m in g.objects(s, SHN("message"))]
        out[qn(s)] = (qn(target) if target else "—",
                      str(sev).split("#")[-1] if sev else "Violation", sorted(set(msgs)))
    return out


SHAPES = all_shapes()


def projections():
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "projections", "*.rq"))):
        head = []
        for line in open(f):
            if line.strip().startswith("#"):
                head.append(line.strip("#").strip())
            elif line.strip():
                break
        out[os.path.basename(f)] = " ".join(head)
    return out


PROJ = projections()

# House brand: TOP (The Ontology Project) wordmark — matches top.scientix.ai.
LOGO = '<img class="toplogo" src="assets/top-logo.svg" alt="The Ontology Project">'


# ---------------------------------------------------------------- flows
FLOWS = [
    dict(id="setup", title="Study &amp; site set-up",
         blurb="Define the study and bring a site from feasibility to first-patient-in &mdash; with activation gated on its essential documents, and enrollment that can&#8217;t precede activation.",
         onto=["cr-core-startup.ttl"],
         entities=["Study", "Arm", "Cohort", "DoseLevel", "Endpoint", "ProtocolVersion",
                   "EligibilityCriterion", "StoppingRule", "InvestigationalProduct",
                   "Sponsor", "CRO", "StudySite", "RegulatoryInteraction"],
         shapes=["cr:StudyShape", "cr:ProtocolEligibilityShape", "cr:SiteActivationShape"],
         proj=["usdm_study.rq", "site_activation_tracker.rq"], screens=["Site activation"]),
    dict(id="startup-package", title="Study start-up package",
         blurb="A site is awarded a study and receives a start-up package &mdash; not one file, but a set of typed documents (often downloaded one-by-one from a portal). The site's response splits into three work streams &mdash; regulatory, budget &amp; contracting, clinical operations &mdash; each consuming package documents and producing site-specific outputs (customized ICF, the DoA log, a signed CTA). Regulatory + budget completion gates the SIV and activation.",
         onto=["cr-core-startup-package.ttl"],
         shapes=["cr:StartupArtifactTypeShape", "cr:WorkStreamShape",
                 "cr:ActivationReadinessShape", "cr:OutputLineageShape"],
         proj=["startup_package_status.rq", "doa_log.rq"], screens=["Study start-up"],
         note="Documents are typed via the existing TMF artifact-type scheme; every produced output traces (<code>prov:wasDerivedFrom</code>) to the document it was built from &mdash; the data trail from package to site-specific output. The site-operations companion to the sponsor-side protocol model."),
    dict(id="delegation", title="Delegation &amp; attestation",
         blurb="The PI delegates each task to credentialed staff by attestation &mdash; and the delegation-of-authority log is a <i>projection</i> of those acts, not a maintained spreadsheet.",
         entities=["Delegation", "Capability", "Credential", "Attestation"],
         shapes=["cr:DelegationShape", "cr:CapabilityDelegationShape", "cr:DelegationTimingShape"],
         proj=["doa_log.rq"], screens=["Delegation"]),
    dict(id="enrollment", title="Enrollment &amp; consent",
         blurb="Bind a real person to a pseudonymous study subject (the only legal PII bridge), and obtain consent under a valid delegation.",
         entities=["Enrollment", "StudySubject", "InformedConsent", "Visit"],
         shapes=["cr:EnrollmentShape", "cr:InformedConsentShape"],
         proj=["fhir_research_subject.rq", "sdtm_dm.rq"], screens=["Enrollment", "Informed consent"]),
    dict(id="schedule", title="Schedule of Activities",
         blurb="The visit schedule most systems flatten into a 2D table with the timing buried in footnotes &mdash; modeled as a timeline: a planned template (windows, relative timing, ordering, repeats), projected onto a participant once the anchor is known, then reconciled against what actually happened.",
         onto=["cr-core-schedule.ttl"],
         shapes=["cr:PlannedEncounterTimingShape", "cr:PlannedActivityPositionShape",
                 "cr:PlannedVisitWindowShape", "cr:VisitWindowShape", "cr:ActivityOrderingShape"],
         proj=["soa_table.rq", "planned_vs_actual.rq"], screens=[],
         note="The bitemporal payoff a static SoA can&#8217;t give: the planned schedule is reconstructable <i>as-of</i> any protocol amendment, and a missed (planned-but-unrealized) visit is a detective query. Out-of-window is a Warning (deviation candidate); broken hard ordering is a Violation."),
    dict(id="edc", title="Data capture (EDC) &amp; fidelity",
         blurb="Capture values against variable definitions (CDISC ODM EAV), verify by risk (SDV), and manage queries &mdash; with PHI classified at the source.",
         onto=["cr-core-edc.ttl"],
         shapes=["cr:ClinicalObservationShape", "cr:DataElementPHIShape", "cr:QueryShape"],
         proj=["datamart_itemdata.rq", "sdtm_ae.rq", "sdtm_ex.rq"], screens=["EDC capture"]),
    dict(id="lims", title="Biospecimen &amp; LIMS custody",
         blurb="Track a specimen&#8217;s chain of custody as a bitemporal state machine, its aliquot lineage, and assays &mdash; so any result traces back to the blood draw.",
         onto=["cr-core-lims.ttl"], entities=["Specimen"],
         shapes=["cr:SpecimenOriginShape", "cr:CustodyEventShape", "cr:AssayResultShape"],
         proj=["specimen_lineage.rq"], screens=["Blood draw"]),
    dict(id="safety", title="Safety &amp; pharmacovigilance",
         blurb="Adverse events and serious adverse events, with the expedited 15-day reporting clock measured bitemporally (awareness &rarr; submission).",
         onto=["cr-core-safety.ttl"], entities=["AdverseEvent", "DoseLimitingToxicity"],
         shapes=[], proj=[], screens=["Adverse event"],
         note="The 15-day SAE reporting clock is a bitemporal compliance check (a detective query over awareness vs submission), not a structural shape &mdash; the structure stays valid; the timeline is the signal."),
    dict(id="rbqm", title="Risk-based monitoring (RBQM)",
         blurb="Target monitoring by risk: a high-risk critical-to-quality factor must be mitigated; 100% SDV on a low-risk factor is flagged as over-monitoring.",
         onto=["cr-core-rbqm.ttl"],
         shapes=["cr:RiskAssessmentShape", "cr:HighRiskMitigationShape", "cr:OverMonitoringShape"],
         proj=["rbqm_monitoring.rq"], screens=["Risk-based monitoring"]),
    dict(id="deviation", title="Deviations &amp; CAPA",
         blurb="The chain most CR models skip: a critical-to-quality factor is threatened by a latent operational condition (the <i>antecedent</i> &mdash; the missing middle), which manifests as a deviation, which triggers a CAPA. Model the cause, not just the event.",
         onto=["cr-core-deviation.ttl"],
         shapes=["cr:DeviationEventShape", "cr:SignificantDeviationCAPAShape", "cr:UncapturedAntecedentShape"],
         proj=["deviation_lineage.rq"], screens=["Deviation &amp; CAPA"],
         note="A leading <code>cr:RiskSignal</code> can flag an antecedent before it manifests, and the RBQM risk assessment can identify it &mdash; so the deviation becomes foreseeable, and a CAPA traces back to the quality factor it ultimately protects."),
    dict(id="preind", title="Pre-IND gate",
         blurb="The front bracket: an IND-enabling narrative where every animal toxicity is addressed by a clinical safety assessment, plus the 30-day review clock.",
         onto=["cr-core-preind.ttl"],
         shapes=["cr:INDNarrativeShape", "cr:VagueQuestionShape", "cr:PreINDReadinessShape"],
         proj=[], screens=[],
         note="The IND 30-day review clock (may-proceed vs on-hold) is a bitemporal detective check."),
    dict(id="eop2", title="EOP2 &amp; analysis",
         blurb="The back bracket: efficacy results that trace to their estimand and SAP (overstatement guard), the EOP2 readiness gate, and ADaM analysis traceable to native source.",
         onto=["cr-core-eop2.ttl", "cr-core-adam.ttl"],
         shapes=["cr:EndpointResultTraceShape", "cr:EOP2ReadinessShape", "cr:ADaMTraceabilityShape"],
         proj=["adam_traceability.rq"], screens=["EOP2 gate"]),
    dict(id="gcp", title="GCP &amp; essential records",
         blurb="The ICH E6(R3) governance vocabulary no existing ontology owns &mdash; essential records, source data/documents, audit trail, certified copy, plus the institutional actors &mdash; cited to E6(R3), defined descriptively (the obligations live in the shapes, not the classes).",
         onto=["cr-core-gcp.ttl"],
         shapes=["cr:CertifiedCopyShape", "cr:SourceDataAuditTrailShape"],
         proj=["certified_copy_register.rq"], screens=["Essential records"],
         note="Descriptive vs deontic: we encode what E6(R3) <i>defines</i> (entities, terms) as classes/SKOS with <code>rdfs:isDefinedBy</code>; what it <i>requires</i> (“should/shall”) becomes graded shapes. ALCOA++ is realized by the bitemporal + PROV envelope; an explicit <code>cr:AuditTrail</code> is the stronger auditor-facing assertion."),
    dict(id="tmf", title="TMF document binding",
         blurb="Classify a document to its artifact type (a SKOS scheme aligned to the DIA TMF Reference Model), then bind what its facts <i>mean</i> to the domain class &mdash; the comprehension layer the eTMF world omits.",
         onto=["tmf-reference.ttl"],
         shapes=["tmf:ContentBindingShape"],
         proj=["tmf_binding_map.rq"], screens=[],
         note="Two bindings, kept distinct: document-type (&#8220;this is a Protocol Deviation Log&#8221;) and content (&#8220;its facts mean <code>cr:DeviationEvent</code>&#8221;). The commons owns the map (align + build); the consuming system classifies, extracts, and asserts <code>prov:wasDerivedFrom</code> at runtime &mdash; that seam is deliberate, and the runtime is out of scope."),
    dict(id="roles", title="Roles, phases &amp; actions",
         blurb="Who can do what, when &mdash; the operator-grounding layer that turns the reference graph into a system of record for authorization, delegation, and Jobs to Be Done.",
         onto=["cr-core-roles.ttl", "cr-core-phases.ttl", "cr-core-actions.ttl"],
         shapes=[], proj=[]),
    dict(id="interop", title="Interoperability",
         blurb="Owned, provenance-tagged crosswalks to external ontologies (verified IRIs), and every standard view the graph emits &mdash; the standards are projections, not the source of truth.",
         onto=["crosswalk-vocab.ttl"],
         shapes=["cx:MappingShape"], proj="ALL", screens=[]),
]

# train-line stop -> flow page
STOP_FLOW = {"Site activation": "setup", "Delegation": "delegation", "Enrollment": "enrollment",
             "Informed consent": "enrollment", "Blood draw": "lims", "EDC capture": "edc",
             "Adverse event": "safety", "EOP2 gate": "eop2"}
STOP_ORDER = ["Site activation", "Delegation", "Enrollment", "Informed consent",
              "Blood draw", "EDC capture", "Adverse event", "EOP2 gate"]


def flow_entities(flow):
    s = set()
    for f in flow.get("onto", []):
        s |= set(PER_FILE.get(f, []))
    for n in flow.get("entities", []):
        if n in IDX:
            s.add(IDX[n])
    return [i for i in s if not (str(i).startswith(TOP) and str(i).split("#")[-1] in CLOS)]


# ---------------------------------------------------------------- render bits
def entities_table(iris):
    rows = ""
    for s in sorted(iris, key=lambda x: str(MERGED.value(x, RDFS.label) or x)):
        rows += (f"<tr><td><code>{esc(qn(s))}</code></td><td>{esc(MERGED.value(s, RDFS.label))}</td>"
                 f"<td class='clo'>{clo_of(s)}</td><td>{esc(MERGED.value(s, RDFS.comment))}</td></tr>")
    return (f"<table class='ref'><tr><th>entity</th><th>label</th><th>category</th><th>meaning</th></tr>{rows}</table>"
            if rows else "<p class='muted'>&mdash;</p>")


def constraints_table(names):
    rows = ""
    for n in names:
        if n not in SHAPES:
            continue
        target, sev, msgs = SHAPES[n]
        ml = "".join(f"<li>{esc(m)}</li>" for m in msgs)
        rows += (f"<tr><td><code>{esc(n)}</code></td><td><code>{esc(target)}</code></td>"
                 f"<td><span class='sev {sev.lower()}'>{sev}</span></td><td><ul>{ml}</ul></td></tr>")
    return (f"<table><tr><th>rule</th><th>applies to</th><th>severity</th><th>requires</th></tr>{rows}</table>"
            if rows else "")


def projections_table(fnames):
    files = sorted(PROJ) if fnames == "ALL" else fnames
    rows = "".join(f"<tr><td><code>{esc(f)}</code></td><td>{esc(PROJ.get(f, ''))}</td></tr>"
                   for f in files if f in PROJ)
    return f"<table><tr><th>projection</th><th>produces</th></tr>{rows}</table>" if rows else ""


# ---------------------------------------------------------------- shell / nav
CSS = """
:root{--ink:#111;--sec:#2a2a2a;--mut:#777;--acc:#0e7490;--accent:#0e7490;--bg:#fafaf6;--card:#fff;--line:#d6d6cf;--line2:#c8c8c0;--ok:#1e8e6f;--warn:#c08410;--danger:#b23a48;--pale:#eef0ed}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{display:flex;max-width:1200px;margin:0 auto}
nav{position:sticky;top:0;align-self:flex-start;width:240px;padding:24px 18px;height:100vh;overflow:auto;font-size:13px;border-right:1px solid var(--line)}
nav b{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin:18px 0 5px}
nav a{display:block;color:var(--sec);padding:3px 0}
nav a.on{color:var(--acc);font-weight:700}
.brandmark{padding-bottom:14px;border-bottom:1px solid var(--line);margin-bottom:6px}
.toplogo{width:172px;height:auto;display:block}
.brandsub{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:11px;color:var(--mut);margin-top:8px;letter-spacing:.02em}
main{flex:1;padding:26px 40px;max-width:900px}
h1{font-size:24px;margin:0 0 4px;letter-spacing:-.01em}
h2{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink);margin:34px 0 12px;padding-bottom:5px;border-bottom:1px solid var(--line2)}
h4{margin:0 0 6px;font-size:15px}
.lead{background:#fff;border-left:3px solid var(--acc);padding:14px 18px;margin:0 0 14px;font-size:15px;line-height:1.6}
.tag{font-family:ui-monospace,"SF Mono",Menlo,monospace;color:var(--acc);font-size:12px;margin:0 0 16px}
.muted{color:var(--mut)}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.card{background:#fff;border:1px solid var(--line);border-radius:3px;padding:15px}.card h4{color:var(--acc)}
.step{display:flex;gap:14px;margin:14px 0;background:#fff;border:1px solid var(--line);border-radius:3px;padding:15px}
.step .num{flex:none;width:28px;height:28px;border-radius:50%;background:var(--acc);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center}
pre{background:#fafaf6;border:1px solid var(--line);border-left:3px solid var(--acc);border-radius:0 3px 3px 0;color:var(--sec);padding:13px 16px;overflow:auto;font:12px/1.7 ui-monospace,"SF Mono",Menlo,monospace}
pre .c{color:#888;font-style:italic}
code{background:var(--pale);border-radius:3px;padding:1px 5px;font:12px ui-monospace,"SF Mono",Menlo,monospace}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px;background:#fff}
th,td{text-align:left;padding:7px 10px;border:1px solid var(--line);vertical-align:top}
th{background:var(--pale);font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:var(--mut)}
table.map td:first-child{color:var(--mut)}.ref td.clo{color:var(--acc);font-size:12px;white-space:nowrap;font-family:ui-monospace,Menlo,monospace}
.ref ul,td ul{margin:0;padding-left:16px}
.sev{font-size:11px;font-weight:700;padding:1px 7px;border-radius:3px}
.sev.violation{background:#f4e3e4;color:var(--danger)}.sev.warning{background:#f4ebd9;color:var(--warn)}
.stats{display:flex;gap:14px;flex-wrap:wrap;margin:10px 0 0}.stats div{background:#fff;border:1px solid var(--line);border-radius:3px;padding:8px 14px;font-size:12px;color:var(--mut)}.stats b{display:block;font-size:20px;color:var(--acc)}
.note{background:#f4faf7;border:1px solid #cde4d8;border-left:3px solid var(--ok);border-radius:0 3px 3px 0;padding:12px 15px}
.flowgrid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0}
.flowgrid a{display:block;background:#fff;border:1px solid var(--line);border-radius:3px;padding:13px 15px;color:var(--sec)}
.flowgrid a:hover{border-color:var(--acc);text-decoration:none}.flowgrid b{color:var(--acc)}
footer{color:var(--mut);font-size:12px;margin:44px 0 20px;border-top:1px solid var(--line);padding-top:14px}
.masthead{background:#fff;border:1px solid var(--line);border-radius:3px;padding:16px 18px;margin:0 0 18px}
dl.mast{display:grid;grid-template-columns:130px 1fr;gap:4px 14px;margin:0 0 12px;font-size:13px}
dl.mast dt{color:var(--mut);text-transform:uppercase;font-size:11px;letter-spacing:.04em;padding-top:2px}
dl.mast dd{margin:0}
.downloads{border-top:1px solid var(--line);padding-top:12px}
.dlhead{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);margin-bottom:8px}
.dlrow{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin:5px 0}
.dllabel{font-size:12px;color:var(--sec);width:96px;flex:none}
a.fmt{display:inline-block;font:11px ui-monospace,Menlo,monospace;background:var(--pale);border:1px solid var(--line);border-radius:3px;padding:2px 9px;color:var(--acc)}
a.fmt:hover{background:var(--acc);color:#fff;text-decoration:none;border-color:var(--acc)}
.citeas{border-top:1px solid var(--line);margin-top:12px;padding-top:12px;font-size:13px;color:var(--sec)}
.citeas.attribution{font-size:12px;color:var(--mut)}
"""


def nav(active):
    NAV = [
        ("", [
            ("index.html",          "Overview",              "hub"),
            ("foundation.html",     "Foundation",            "foundation"),
            ("implementation.html", "Implementation guide",  "implementation"),
        ]),
        ("Start-up", [
            ("preind.html",         "Pre-IND gate",          "preind"),
            ("setup.html",          "Study &amp; site set-up", "setup"),
            ("startup-package.html","Start-up package",      "startup-package"),
            ("delegation.html",     "Delegation &amp; DoA",  "delegation"),
        ]),
        ("Conduct", [
            ("enrollment.html",     "Enrollment &amp; consent", "enrollment"),
            ("schedule.html",       "Schedule of Activities", "schedule"),
            ("edc.html",            "Data capture (EDC)",    "edc"),
            ("lims.html",           "Biospecimen &amp; LIMS","lims"),
            ("safety.html",         "Safety &amp; PV",       "safety"),
            ("rbqm.html",           "Risk-based monitoring", "rbqm"),
            ("deviation.html",      "Deviations &amp; CAPA", "deviation"),
        ]),
        ("Closeout", [
            ("eop2.html",           "EOP2 &amp; analysis",   "eop2"),
        ]),
        ("Cross-cutting", [
            ("roles.html",          "Roles, phases &amp; actions", "roles"),
            ("gcp.html",            "GCP &amp; essential records", "gcp"),
            ("tmf.html",            "TMF document binding",  "tmf"),
            ("interop.html",        "Interoperability",      "interop"),
            ("ingestion.html",      "Ingestion example",     "ingestion"),
        ]),
    ]
    out = []
    for section, items in NAV:
        if section:
            out.append(f'<b>{section}</b>')
        for href, t, i in items:
            out.append(f'<a class="{"on" if i==active else ""}" href="{href}">{t}</a>')
    out.append('<b>Detail</b>')
    out.append(f'<a class="{"on" if active=="reference" else ""}" href="reference.html">Full reference</a>')
    return "\n".join(out)


DRAFT_CSS = (
    ".draft-ribbon{position:fixed;top:16px;right:-52px;transform:rotate(45deg);"
    "background:#b00020;color:#fff;font:700 11px/1 ui-sans-serif,system-ui,sans-serif;"
    "letter-spacing:.14em;padding:6px 60px;z-index:2000;box-shadow:0 1px 5px rgba(0,0,0,.3)}"
    ".draft-banner{background:#fff3f3;border-bottom:1px solid #b00020;color:#7a0016;"
    "font:600 12px/1.5 ui-sans-serif,system-ui,sans-serif;text-align:center;padding:8px 14px}"
    ".draft-banner b{letter-spacing:.08em}"
)
DRAFT_BANNER = (
    "<div class='draft-banner'><b>DRAFT &mdash; PRE-RELEASE.</b> "
    "The TOP Clinical Research reference graph is a work in progress and not yet finalized; "
    "content, identifiers, and constraints may change.</div>"
)
DRAFT_RIBBON = "<div class='draft-ribbon'>DRAFT</div>"


def shell(title, active, body):
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>[DRAFT] {title}</title><style>{CSS}{SCREEN_CSS}{DRAFT_CSS}</style></head><body>"
            f"{DRAFT_RIBBON}{DRAFT_BANNER}<div class='wrap'>"
            f"<nav><div class='brandmark'>{LOGO}<div class='brandsub'>Clinical Research reference graph</div></div>{nav(active)}</nav>"
            f"<main>{body}"
            "<footer><b>Draft / pre-release</b> &mdash; not finalized. Auto-generated by "
            "<code>cr-domain/docs/build_docs.py</code> from the ontology, shapes, "
            "and projections &mdash; regenerate after model changes.</footer></main></div></body></html>")


# ---------------------------------------------------------------- narrative (hub)
def hub_body(stats):
    cards = [
        ("Inherit, don't rebuild", "Your graph starts with the industry's operator model already in place &mdash; the cold-start tax becomes a one-time inheritance."),
        ("One model, many views", "CDISC SDTM/ADaM, USDM, FHIR, a delegation log, a data mart &mdash; all <b>projected</b> from one graph. The standards are views, not the source of truth."),
        ("Remembers everything", "Every fact carries two clocks &mdash; when it was true, and when you knew it. Reconstruct any past state &ldquo;as of&rdquo; a date; back-dating is structurally impossible."),
        ("Provable by construction", "Every assertion records who attested it, when, and on what evidence (W3C PROV) &mdash; attestation, not just a citation."),
        ("Safe &amp; proportionate", "Identifiable data is contained by design; compliance is graded by materiality; monitoring is targeted by risk, not blanket."),
        ("Organized by flow", "Each sub-domain below is its own page &mdash; the screen, the data, the rules, the views &mdash; so you read only the part you operate."),
    ]
    cardhtml = "".join(f'<div class="card"><h4>{t}</h4><p>{d}</p></div>' for t, d in cards)
    # train line linking to flow pages
    chips = ""
    for i, name in enumerate(STOP_ORDER):
        chips += f'<a class="tstop live" href="{STOP_FLOW[name]}.html" style="text-decoration:none">{name}</a>'
        if i < len(STOP_ORDER) - 1:
            chips += '<div class="trail"></div>'
    flowcards = "".join(
        f'<a href="{fl["id"]}.html"><b>{fl["title"]}</b><br><span class="muted" style="font-size:13px">{fl["blurb"]}</span></a>'
        for fl in FLOWS)

    hero = """
<div style="background:#fff;border:1px solid var(--line);border-radius:3px;padding:20px 22px;margin:0 0 14px">
<p style="margin:0 0 6px"><b>Natural language question</b></p>
<p style="font-size:18px;margin:0 0 16px;color:var(--acc)">&ldquo;How is GLP1-TRIAL-27 doing?&rdquo;</p>
<p style="margin:0 0 10px;color:var(--mut);font-size:13px">Sounds simple. The reality: 149 participants are simultaneously in different sub-phases of the trial &mdash; some still in screening, some mid-treatment, some in follow-up. Twelve sites are at different lifecycle stages (three still activating, one just closed). There are two protocol amendments; a participant&rsquo;s visit-3 eligibility may have been evaluated under version 1 or version 2 of the protocol depending on when they enrolled. Two SAEs are in the 15-day reporting window.</p>
<p style="margin:0 0 6px"><b>What the broker answers (NGSI-LD entity query)</b></p>
<pre style="margin:0 0 12px">GET /ngsi-ld/v1/entities?type=cr:Study&amp;id=urn:ngsi-ld:top-cr:Study:GLP1-TRIAL-27
  &amp;attrs=identifier,status,conductedAt,hasProtocolVersion
  &amp;options=keyValues</pre>
<p style="margin:0 0 6px"><b>What the reasoner adds when the broker returns null or incomplete</b></p>
<p style="font-size:13px;color:var(--mut)">The broker holds the runtime state (current entity versions). When a query crosses a temporal boundary &mdash; &ldquo;which protocol version was in effect for Subject 042 at Visit 3?&rdquo; &mdash; the OWL reasoner resolves the bitemporal join. The LLM agent routes: broker first, reasoner on null or temporal qualifier, human escalation on conflict.</p>
<p style="margin:4px 0 0" class="note" style="font-size:13px"><b>The hard truth:</b> answering &ldquo;how is a trial doing&rdquo; correctly requires bitemporality (what was true when), concurrent state (149 participants &times; their individual temporal planes), and provenance (which amendment governed which visit). No flat table gives you all three. This is why the model exists.</p>
</div>"""

    tradeoffs = """
<table>
<tr><th>dimension</th><th>RDF / OWL / SPARQL</th><th>NGSI-LD (broker)</th><th>LPG / Neo4j</th></tr>
<tr><td><b>Bitemporality</b></td>
    <td>Possible via reification or named graphs; verbose, non-standard; query complexity is high</td>
    <td><b>Native</b> &mdash; <code>observedAt</code> is a first-class attribute on every Property/Relationship; no plumbing required</td>
    <td>Requires custom plumbing (shadow nodes or separate timestamp properties); no standard</td></tr>
<tr><td><b>OWL reasoning</b></td>
    <td><b>Native</b> &mdash; subclass inference, property restrictions, consistency checking</td>
    <td>RDF/OWL compatible (NGSI-LD is JSON-LD over RDF); use a companion triple store for inference</td>
    <td>No OWL; Cypher property rules are procedural, not declarative</td></tr>
<tr><td><b>Runtime / IoT scale</b></td>
    <td>Triple stores scale but are batch-oriented; not designed for high-frequency entity updates</td>
    <td><b>Designed for this</b> &mdash; entity lifecycle, subscriptions, geo-queries; ETSI standard</td>
    <td>Good for connected data at scale; no subscription or geo-query standard</td></tr>
<tr><td><b>Standards alignment</b></td>
    <td>W3C / OWL / SHACL; import-ready by ontologists</td>
    <td>ETSI GS CIM 009; used by EU data spaces (Gaia-X, IDS)</td>
    <td>Proprietary (Neo4j); openCypher is emerging but not finalized</td></tr>
<tr><td><b>Query language</b></td>
    <td>SPARQL &mdash; powerful, temporal joins possible, steep learning curve</td>
    <td>NGSI-LD query API (q= filter, geo-query, temporal API) &mdash; REST, learnable</td>
    <td>Cypher &mdash; very readable for graph traversal; limited temporal support</td></tr>
<tr><td><b>Cold-start cost</b></td>
    <td>High &mdash; requires ontology expertise to build a domain model from scratch</td>
    <td>High without a reference model; low <b>with TOP as the @context</b></td>
    <td>Medium &mdash; schema-on-write but flexible; harder to share across organizations</td></tr>
</table>
<p class="note"><b>TOP&rsquo;s position:</b> the OWL model is the design-time specification and the source of the @context. NGSI-LD is the preferred runtime substrate because bitemporality is native and the standard is broker-agnostic. LPG / Neo4j is a valid implementation choice; the same entity model applies, and this reference graph can serve as the property graph schema. All three benefit from the shared vocabulary; none requires the others.</p>"""

    ngsi_owl = """
<p>NGSI-LD is JSON-LD &mdash; a serialization of RDF. Every NGSI-LD entity, when expanded, is a valid RDF graph. The TOP CR <code>@context</code> (<a href="dist/top-cr-v1.ngsi-context.jsonld" download>download</a>) maps the short names used in broker payloads (<code>cr:Study</code>, <code>hasProtocolVersion</code>) to their full IRIs, and annotates ObjectProperty terms with <code>@type: @id</code> so relationship values compact correctly.</p>
<p><b>What this means in practice:</b></p>
<ul>
<li>An entity stored in a Scorpio / Orion-LD broker can be loaded into a triple store by expanding its JSON-LD &mdash; no conversion required.</li>
<li>OWL reasoning over broker data works: load the expanded triples into a reasoner alongside <code>core/v1/shapes.ttl</code>; the class hierarchy and property restrictions apply.</li>
<li>SHACL validation works on the same graph: run <code>top-cr-shapes-v1.ttl</code> against the expanded triples to validate any broker payload.</li>
<li><b>The gap:</b> NGSI-LD&rsquo;s Property-of-Property model (metadata on a Property node) does not map to a single RDF triple; it requires reification. This is the one place where the two models diverge structurally. TOP handles this by using <code>top:observedAt</code> on the entity (transaction time) and <code>top:validFrom</code> / <code>top:validUntil</code> on versioned nodes (valid time), which round-trip cleanly through JSON-LD expansion.</li>
</ul>"""

    limits = """<ul>
<li><b>Not here:</b> agent orchestration, the runtime/broker &mdash; those consume the reference; they aren&rsquo;t part of it.</li>
<li><b>Pseudonymized, not anonymized:</b> identifiable data is kept from flowing downstream, but statistical anonymization is an upstream/runtime responsibility.</li>
<li><b>Scope today:</b> oncology, Pre-IND &rarr; End-of-Phase-2, plus the site-operations layer. The architecture generalizes; the content is bounded.</li>
<li><b>Multi-source provenance:</b> different sponsors run EDC on different platforms (S3/ODM, Databricks, Snowflake, Veeva). The crosswalk layer handles field mapping; but when provenance logs live in different systems, reconciliation is an unsolved problem at the industry level. TOP gives you the vocabulary; the pipeline is implementation work.</li></ul>"""

    howto = """
<div class="step"><span class="num">1</span><div><h4>Ingest a protocol</h4>
<p>Parse an ICH M11 / USDM v4 JSON. Map each entity type to its TOP CR equivalent. POST as NGSI-LD entities to your broker with the TOP @context. See the <a href="ingestion.html">Ingestion worked example</a> for the LY900018 nasal glucagon protocol.</p></div></div>
<div class="step"><span class="num">2</span><div><h4>Subscribe to a data source</h4>
<p>Point the runtime at an S3 bucket (ODM/XML), a Kafka stream (Castor EDC), or a Veeva DDA export. The crosswalk layer maps vendor fields to TOP CR terms; unknown fields route to LLM inference with a confidence score.</p></div></div>
<div class="step"><span class="num">3</span><div><h4>Validate</h4>
<p>Run <code>top-cr-shapes-v1.ttl</code> over the expanded triples. The SHACL contract catches PII leaks, undelegated work, orphan data, premature activation, unmitigated risk.</p></div></div>
<div class="step"><span class="num">4</span><div><h4>Query across time</h4>
<p>Broker queries answer &ldquo;what is the current state?&rdquo;. Temporal API queries answer &ldquo;what was true at T?&rdquo;. For cross-amendment joins, route to the triple store + reasoner.</p></div></div>
<div class="step"><span class="num">5</span><div><h4>Emit what you need</h4>
<p>Run a projection &rarr; SDTM, USDM, FHIR, the DOA log, a data mart, ADaM lineage &mdash; provenance intact.</p></div></div>"""

    return (
        "<h1>TOP &mdash; Clinical Research Reference Graph</h1>"
        "<p class='tag'>An inheritable, provenance-native, bitemporal reference model for the clinical trial lifecycle. Technology-agnostic &middot; NGSI-LD native &middot; open commons.</p>"
        f"<div class='stats'><div><b>{stats['c']}</b><br>entities</div><div><b>{stats['s']}</b><br>rules</div>"
        f"<div><b>{stats['p']}</b><br>views</div><div><b>{stats['e']}</b><br>examples</div><div><b>{stats['t']}</b><br>tested</div></div>"
        f"{download_badges('top-cr-v1', 'Download the model')}"
        "<p class='muted' style='font-size:12px;margin-top:4px'>Apache-2.0 &middot; "
        f"<code>{esc(MAST['namespace'])}</code> &middot; see <a href='foundation.html'>Foundation</a> for full masthead &amp; citation.</p>"

        "<h2 id='what'>What this is</h2>"
        "<p class='lead'>A ready-made, shared model of how a clinical trial actually runs &mdash; from a site&rsquo;s first activation through an End-of-Phase-2 decision. "
        "Instead of every organization re-inventing how to represent studies, subjects, visits, samples, consent and safety data, <b>you inherit a model the industry can share, and your own data plugs into it.</b></p>"
        "<p>Because it captures <i>who did what, when, and on what evidence</i> &mdash; and remembers every version of the truth over time &mdash; the documents you already owe (SDTM, USDM, a delegation log, an analysis dataset) come out as <b>views</b>, and a regulator&rsquo;s question becomes a <b>query</b>.</p>"

        "<h2 id='hero'>Why bitemporality is hard &mdash; a real example</h2>"
        f"{hero}"

        "<h2 id='value'>The value</h2>"
        f"<div class='cards'>{cardhtml}</div>"

        "<h2 id='tradeoffs'>Technology tradeoffs &mdash; honest</h2>"
        "<p>TOP is technology-agnostic. The OWL model is the canonical specification; NGSI-LD is the preferred runtime substrate; LPG / Neo4j is a valid alternative. Each has real tradeoffs.</p>"
        f"{tradeoffs}"

        "<h2 id='ngsi-owl'>NGSI-LD and OWL &mdash; how they fit together</h2>"
        f"{ngsi_owl}"

        "<h2 id='line'>The trial as a workflow &mdash; click a stop</h2>"
        f"<div class='trainline'>{chips}</div>"
        f"<div class='flowgrid'>{flowcards}</div>"

        "<h2 id='howto'>How to put it to work</h2>"
        f"{howto}"

        "<h2 id='limits'>Honest limits</h2>"
        f"{limits}")


def download_badges(base, label):
    """A row of format pills linking to the serializations in dist/."""
    fmts = [("ttl", "Turtle"), ("owl", "RDF/XML"), ("jsonld", "JSON-LD"), ("nt", "N-Triples")]
    pills = "".join(f'<a class="fmt" href="dist/{base}.{ext}" download>{name}</a>' for ext, name in fmts)
    return f'<div class="dlrow"><span class="dllabel">{label}</span>{pills}</div>'


def masthead():
    """WIDOCO/PKO-style metadata header: version, namespace, license, authorship, downloads, cite-as."""
    m = MAST
    rows = [
        ("This version", f'<code>{esc(m["ontology_iri"])}</code> &middot; {esc(m["version"])}'),
        ("Namespace", f'<code>{esc(m["namespace"])}</code>'),
        ("Issued", esc(m["issued"])),
        ("License", f'<a href="{esc(m["license_iri"])}">{esc(m["license_label"])}</a>'),
        ("Authors", esc(m["creator"])),
        ("Contributors", esc(m["contributor"])),
    ]
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    ngsi = ('<div class="dlrow"><span class="dllabel">NGSI-LD</span>'
            '<a class="fmt" href="dist/top-cr-v1.ngsi-context.jsonld" download>@context</a>'
            '<span class="muted" style="font-size:11px">broker-facing; RDF/JSON-LD above is the model itself</span></div>')
    downloads = (download_badges("top-cr-v1", "Ontology")
                 + ngsi
                 + download_badges("top-cr-shapes-v1", "SHACL shapes")
                 + download_badges("top-cr-crosswalks-v1", "Crosswalks"))
    return (
        '<div class="masthead">'
        f'<dl class="mast">{dl}</dl>'
        f'<div class="downloads"><div class="dlhead">Download serializations</div>{downloads}'
        '<div class="muted" style="font-size:11px;margin-top:8px">Served from this site&rsquo;s '
        '<code>dist/</code> and mirrored in the repository; pin by <code>SHA256SUMS</code>. '
        'See the <a href="implementation.html">Implementation guide</a>.</div></div>'
        f'<div class="citeas"><b>Cite as</b><br>{esc(m["cite_as"])}</div>'
        f'<div class="citeas attribution"><b>Attribution</b><br>{esc(m["notice"])}</div>'
        '</div>')


def foundation_body():
    clo_rows = ""
    for clo in CLOS:
        specials = sorted({qn(s) for s in IDX.values()
                           if clo_of(s) == clo and not str(s).startswith(TOP)})
        clo_rows += f"<tr><td><b>{clo}</b></td><td>{esc(', '.join(specials[:16]))}{' …' if len(specials)>16 else ''}</td></tr>"
    found = [IDX[n] for n in IDX if str(IDX[n]).startswith("https://top.scientix.ai/hcls")]
    return (
        "<h1>Foundation &mdash; the shared model</h1>"
        f"{masthead()}"

        # ── Three-layer architecture ────────────────────────────────────────────
        "<h2>Three layers, one coherent system</h2>"
        "<p class='lead'>TOP is technology-agnostic by design. The same vocabulary is expressed "
        "in three complementary layers: each serves a different audience and can be used "
        "independently, but they compose into a single coherent system.</p>"
        "<table>"
        "<tr><th>Layer</th><th>Artifact</th><th>What it does</th><th>Who uses it</th></tr>"
        "<tr><td><b>OWL ontology</b><br><span class='muted'>design-time spec</span></td>"
        "<td><code>ontology/*.ttl</code></td>"
        "<td>Defines every class, property, and relationship. Enables OWL reasoning: "
        "if a <code>cr:Delegation</code> has a <code>cr:delegatedCapability</code>, "
        "the reasoner infers the person holds that capability. Machine-checkable axioms "
        "catch modelling errors before any data arrives.</td>"
        "<td>Ontology engineers, architects, tool vendors defining interop contracts</td></tr>"
        "<tr><td><b>SHACL shapes</b><br><span class='muted'>validation layer</span></td>"
        "<td><code>shapes/*.ttl</code></td>"
        "<td>Graded constraints over instance data. <code>sh:Violation</code> = structural "
        "rules (a <code>cr:Delegation</code> without a <code>cr:delegator</code> fails GCP audit). "
        "<code>sh:Warning</code> = risk-proportionate rules (missing delegation log triggers a "
        "finding, not a hard stop). Runs in pySHACL, Jena, or any SHACL processor.</td>"
        "<td>Data engineers, QA, sponsor data management running validation pipelines</td></tr>"
        "<tr><td><b>NGSI-LD entities</b><br><span class='muted'>runtime substrate</span></td>"
        "<td><code>dist/top-cr-v1.ngsi-context.jsonld</code></td>"
        "<td>JSON-LD over RDF. Every entity is an NGSI-LD entity; every property is a "
        "NGSI-LD Property or Relationship. The <code>@context</code> maps short names to "
        "OWL IRIs — so <code>sponsoredBy</code> in the broker is the same node as "
        "<code>cr:sponsoredBy</code> in the triple store. Scalable, REST-native, "
        "IoT-battle-tested (Scorpio, Orion-LD, FIWARE ecosystem).</td>"
        "<td>Application developers, integration engineers, context broker operators</td></tr>"
        "</table>"
        "<p class='muted'>The three layers do not require each other at runtime: you can run "
        "OWL reasoning offline, validate with SHACL at ingest time, and serve entities through "
        "the broker — or use any single layer alone.</p>"

        # ── Ingestion pipeline ──────────────────────────────────────────────────
        "<h2>Ingestion pipeline</h2>"
        "<p>A reference community runtime (AWS Garnet / Scorpio NGSI-LD CDK) ships separately. "
        "The canonical ingestion flow is:</p>"
        "<pre>"
        "Source                 Parse           Crosswalk              Emit\n"
        "─────────────────────  ──────────────  ─────────────────────  ─────────────────────────\n"
        "ICH M11 / USDM v4 JSON  → usdm→cr.py  → TOP cr-core entities  → NGSI-LD POST to Scorpio\n"
        "Veeva DDA export (S3)   → odm→cr.py   → bulk catch-up load    → NGSI-LD batch upsert\n"
        "Castor EDC (Kafka)      → edcstream.py → streaming ingest      → NGSI-LD PATCH (live)\n"
        "Medidata Rave (API)     → rave→cr.py   → X_WHATEVER fields     → OperationalRecord + conf\n"
        "eTMF (Veeva Vault API)  → tmf→cr.py    → TMF artefact types    → cr:Evidence subclasses\n"
        "</pre>"
        "<p>Every emitted entity carries the <b>Universal DNA</b> "
        "(<code>top:identifier</code>, <code>top:observedAt</code>, <code>top:status</code>) "
        "and is validated against the SHACL shapes before the broker accepts it. "
        "Sponsor-specific fields (<code>X_WHATEVER</code>) go into <code>cr:OperationalRecord</code> "
        "with an LLM-inferred <code>cx:mappingConfidence</code> score; a human reviewer promotes "
        "them to canonical mappings once confirmed.</p>"
        "<p>The downstream stack serves three consumers simultaneously:</p>"
        "<ul>"
        "<li><b>Scorpio context broker</b> &mdash; REST/NGSI-LD queries for operational dashboards "
        "and EDC integrations (latency &lt;50 ms, IoT-scale throughput)</li>"
        "<li><b>Triple store</b> (e.g. Apache Jena TDB2) &mdash; SPARQL 1.1 queries and OWL "
        "reasoning; receives every entity as N-Triples via the broker's notification stream</li>"
        "<li><b>OWL reasoner</b> (e.g. HermiT / ELK) &mdash; materialises inferred facts "
        "(capability delegations, protocol eligibility) and writes them back as asserted triples</li>"
        "</ul>"

        # ── Universal DNA ───────────────────────────────────────────────────────
        "<h2>Universal DNA</h2>"
        "<p>Every entity, whatever its category, carries three strands:</p>"
        "<ul>"
        "<li><b>Identity</b> &mdash; <code>top:identifier</code>: a stable, system-independent "
        "string key. In NGSI-LD the entity <code>id</code> is always "
        "<code>urn:ngsi-ld:top-cr:{Type}:{localId}</code>.</li>"
        "<li><b>Time</b> &mdash; <code>top:observedAt</code>: the NGSI-LD core "
        "<code>observedAt</code> term. Transaction time — when this assertion entered the system. "
        "Always present, set by the ingest pipeline, not editable after write.</li>"
        "<li><b>Lifecycle</b> &mdash; <code>top:status</code>: a named individual from the "
        "relevant codelist (e.g. <code>cr:SiteStatusActive</code>). "
        "Referenced by IRI so SHACL and OWL rules can reason over it, not just filter strings.</li>"
        "</ul>"
        "<p><code>top:UniversalDNAShape</code> enforces all three on every entity. "
        "This is what makes any two TOP graphs line up by construction &mdash; "
        "before any domain-specific alignment.</p>"
        "<p><b>Bitemporality (opt-in via <code>top:Versioned</code>):</b> entities that record "
        "facts about the world (not just about the system) also carry "
        "<code>top:validFrom</code> / <code>top:validUntil</code> &mdash; when the fact was "
        "true in the world, independently of when the system recorded it. In NGSI-LD, "
        "Property-of-Property nodes carry both timestamps natively. "
        "<code>cr:ProtocolVersion</code>, <code>cr:Enrollment</code>, "
        "<code>cr:Delegation</code>, and <code>cr:InformedConsent</code> are all bitemporal.</p>"

        # ── Eight categories ─────────────────────────────────────────────────────
        "<h2>The eight categories</h2>"
        f"<table><tr><th>category</th><th>specialized into (examples across the domain)</th></tr>{clo_rows}</table>"

        # ── Non-negotiable spine ─────────────────────────────────────────────────
        "<h2>The non-negotiable spine</h2>"
        "<ul>"
        "<li><b>Bitemporal by default:</b> every assertion carries valid time (true-in-world) "
        "and transaction time (system knowledge); the past is reconstructable and back-dating "
        "is impossible.</li>"
        "<li><b>Provenance on every fact:</b> W3C PROV on every node &mdash; who asserted it, "
        "when, on what evidence, under which delegation. LLM-inferred mappings carry "
        "<code>cx:inferredBy</code> pointing to the autonomous agent that generated them.</li>"
        "<li><b>PII containment:</b> identifiable <code>hcls:Person</code> lives at the "
        "boundary only. Downstream logic attaches to the pseudonymous "
        "<code>cr:StudySubject</code>. The only legal bridge is the attested, bitemporal "
        "<code>cr:Enrollment</code> act &mdash; deliberately designed to be revocable and auditable.</li>"
        "<li><b>Delegation invariant:</b> every performed act (<code>cr:Assessment</code>, "
        "<code>cr:Administration</code>, &hellip;) links to the <code>cr:Delegation</code> that "
        "authorised it via <code>cr:underDelegation</code>. There is no performed act without "
        "an authorising delegation on record.</li>"
        "</ul>"

        # ── HCLS entities table ──────────────────────────────────────────────────
        "<h2>HCLS-core entities (shared across HCLS domains)</h2>"
        f"{entities_table(found)}"
    )


def flow_body(flow):
    parts = [f"<h1>{flow['title']}</h1><p class='lead'>{flow['blurb']}</p>"]
    for name in flow.get("screens", []):
        parts.append(f"<h2>Operator screen &mdash; {name}</h2>" + render_stop(ROOT, name))
    if flow.get("note"):
        parts.append(f"<p class='note'>{flow['note']}</p>")
    ents = flow_entities(flow)
    if ents:
        parts.append("<h2>Entities</h2>" + entities_table(ents))
    ct = constraints_table(flow.get("shapes", []))
    if ct:
        parts.append("<h2>What it validates</h2>" + ct)
    pt = projections_table(flow.get("proj", []))
    if pt:
        parts.append("<h2>Views it emits</h2>" + pt)
    return "".join(parts)


def ingestion_body():
    study_json = """{
  "id": "urn:ngsi-ld:top-cr:Study:LY900018",
  "type": "cr:Study",
  "@context": [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.8.jsonld",
    "https://top.scientix.ai/cr/v1.ngsi-context.jsonld"
  ],
  "identifier":  { "type": "Property",      "value": "LY900018" },
  "status":      { "type": "Property",      "value": "active" },
  "observedAt":  { "type": "Property",      "value": "2026-06-30T00:00:00Z" },
  "sponsoredBy": { "type": "Relationship",  "object": "urn:ngsi-ld:top-cr:Sponsor:EliLilly" }
}"""
    proto_json = """{
  "id": "urn:ngsi-ld:top-cr:ProtocolVersion:StudyVersion_1",
  "type": "cr:ProtocolVersion",
  "@context": [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.8.jsonld",
    "https://top.scientix.ai/cr/v1.ngsi-context.jsonld"
  ],
  "identifier":        { "type": "Property",     "value": "1" },
  "status":            { "type": "Property",     "value": "active" },
  "observedAt":        { "type": "Property",     "value": "2026-06-30T00:00:00Z" },
  "versionIdentifier": { "type": "Property",     "value": "1" },
  "validFrom":         { "type": "Property",     "value": "2017-12-05" },
  "hasProtocolVersionOf": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:top-cr:Study:LY900018"
  },
  "rationale": {
    "type": "Property",
    "value": "Nasal glucagon (LY900018) is a powder formulation of human glucagon for the rescue treatment of hypoglycaemia..."
  }
}"""
    ec_json = """{
  "id": "urn:ngsi-ld:top-cr:EligibilityCriterion:EligibilityCriterion_1",
  "type": "cr:EligibilityCriterion",
  "@context": [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.8.jsonld",
    "https://top.scientix.ai/cr/v1.ngsi-context.jsonld"
  ],
  "identifier":      { "type": "Property", "value": "INC1" },
  "status":          { "type": "Property", "value": "active" },
  "observedAt":      { "type": "Property", "value": "2026-06-30T00:00:00Z" },
  "criterionCategory": { "type": "Property", "value": "inclusion" },
  "criterionNumber": { "type": "Property", "value": "1" },
  "criterionText": {
    "type": "Property",
    "value": "have had a diagnosis of either: [1a] T1DM based on WHO diagnostic criteria and on daily insulin therapy for at least 1 year — multiple daily injection of long-acting insulin analog or continuous subcutaneous insulin infusion; OR [1b] T2DM based on WHO diagnostic criteria and on daily insulin therapy with or without OAMs for at least 1 year..."
  }
}"""
    visit_json = """{
  "id": "urn:ngsi-ld:top-cr:Visit:Encounter_1",
  "type": "cr:Visit",
  "@context": [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.8.jsonld",
    "https://top.scientix.ai/cr/v1.ngsi-context.jsonld"
  ],
  "identifier":           { "type": "Property",    "value": "SCREENING" },
  "status":               { "type": "Property",    "value": "active" },
  "observedAt":           { "type": "Property",    "value": "2026-06-30T00:00:00Z" },
  "label":                { "type": "Property",    "value": "Screening" },
  "visitType": {
    "type": "Property",
    "value": { "code": "C25716", "codeSystem": "http://www.cdisc.org", "decode": "Visit" }
  },
  "nextVisit":            { "type": "Relationship", "object": "urn:ngsi-ld:top-cr:Visit:Encounter_2" },
  "contactModes":         { "type": "Property",    "value": ["In Person"] },
  "environmentalSettings":{ "type": "Property",    "value": ["Ambulatory Care Facility"] }
}"""

    return (
        "<h1>Ingestion worked example &mdash; LY900018 (USDM&nbsp;v4 &rarr; NGSI-LD)</h1>"
        "<p class='lead'>"
        "Eli Lilly <b>LY900018</b> is a nasal glucagon rescue treatment for hypoglycaemia in "
        "T1DM / T2DM patients. Its USDM v4 JSON protocol is the reference fixture for the "
        "TOP ingestion pipeline. The transformer (<code>examples/usdm/to-ngsi-ld.py</code>) "
        "reads the raw USDM document and emits <b>102 NGSI-LD entities</b> across 10 type "
        "buckets, each carrying the Universal DNA and ready to POST to a Scorpio broker."
        "</p>"

        "<h2>What USDM gives you</h2>"
        "<p>USDM v4 (CDISC Unified Study Definitions Model) is a structured JSON export of a "
        "protocol: study versions, arms, epochs, encounters (visits), eligibility criteria, "
        "objectives, endpoints, and governance history. It is the ICH M11 machine-readable "
        "equivalent &mdash; the canonical protocol source.</p>"
        "<p>The transformer does three things:</p>"
        "<ol>"
        "<li><b>Structural mapping</b> &mdash; USDM <code>StudyVersion</code> → "
        "<code>cr:ProtocolVersion</code>; USDM <code>Encounter</code> → "
        "<code>cr:Visit</code>; USDM <code>EligibilityCriterion</code> → "
        "<code>cr:EligibilityCriterion</code>; etc.</li>"
        "<li><b>Bitemporality injection</b> &mdash; extracts <code>GovernanceDate</code> "
        "from the USDM StudyVersion and uses it as <code>top:validFrom</code> on the "
        "emitted <code>cr:ProtocolVersion</code>. When the protocol is amended, a new "
        "ProtocolVersion entity with a later <code>validFrom</code> is POSTed; the broker "
        "keeps both, and a SPARQL query can reconstruct which version was in force on any "
        "given date.</li>"
        "<li><b>URN assignment</b> &mdash; every entity gets a stable "
        "<code>urn:ngsi-ld:top-cr:{Type}:{localId}</code> built from the USDM object "
        "identifier, so the same study ingested twice produces the same URNs and the broker "
        "can upsert idempotently.</li>"
        "</ol>"

        "<h2>Entity walk-through</h2>"
        "<h3>1&ensp;Study &mdash; the anchor node</h3>"
        "<p>One entity per study. All other entities hang off it via Relationship nodes. "
        "The <code>sponsoredBy</code> Relationship uses <code>@type: @id</code> in the "
        "<code>@context</code> so the broker serialises it as a URI reference — enabling "
        "traversal in a single NGSI-LD request with the <code>options=keyValues&amp;attrs=sponsoredBy</code> "
        "query parameter.</p>"
        f"<pre>{esc(study_json)}</pre>"

        "<h3>2&ensp;ProtocolVersion &mdash; bitemporal protocol snapshot</h3>"
        "<p><code>cr:ProtocolVersion</code> is a <code>top:Versioned</code> entity. "
        "The <code>validFrom</code> property records when this version of the protocol "
        "was authorised in the world (extracted from the USDM <code>GovernanceDate</code>), "
        "independently of when the system ingested it (<code>observedAt</code>). "
        "Querying the broker with <code>q=validFrom&lt;=2018-03-01</code> returns the "
        "protocol version that was in force on that date &mdash; essential for reconstructing "
        "what rules governed a specific visit.</p>"
        f"<pre>{esc(proto_json)}</pre>"

        "<h3>3&ensp;EligibilityCriterion &mdash; full text, structured category</h3>"
        "<p>The transformer strips HTML tags from USDM criterion text and maps the "
        "USDM <code>InclusionExclusion</code> flag to <code>criterionCategory: inclusion | exclusion</code>. "
        "Criteria are linked to the <code>cr:ProtocolVersion</code> they belong to via "
        "<code>cr:hasEligibilityCriterion</code> (not shown in this abbreviated payload; "
        "the full transformer also emits that relationship on the ProtocolVersion entity).</p>"
        f"<pre>{esc(ec_json)}</pre>"

        "<h3>4&ensp;Visit &mdash; relationship chain across the SoA</h3>"
        "<p><code>cr:Visit</code> entities form a linked list via <code>nextVisit</code> "
        "Relationships — enabling a broker to traverse the schedule of activities in sequence "
        "without a SPARQL join. The <code>visitType</code> Property carries a structured "
        "object with a CDISC CT code reference (<code>C25716</code> = &ldquo;Visit&rdquo;). "
        "<code>contactModes</code> and <code>environmentalSettings</code> are arrays, "
        "serialised as NGSI-LD multi-value Properties.</p>"
        f"<pre>{esc(visit_json)}</pre>"

        "<h2>Output summary</h2>"
        "<table>"
        "<tr><th>Entity type</th><th>Count</th><th>Key relationships</th></tr>"
        "<tr><td><code>cr:Study</code></td><td>1</td><td><code>sponsoredBy</code> → Sponsor</td></tr>"
        "<tr><td><code>cr:Sponsor</code></td><td>1</td><td>anchor for all sponsor-level data</td></tr>"
        "<tr><td><code>cr:ProtocolVersion</code></td><td>1</td><td><code>hasProtocolVersionOf</code> → Study; <code>validFrom</code> bitemporal</td></tr>"
        "<tr><td><code>cr:Arm</code></td><td>2</td><td><code>hasArm</code> (on Study)</td></tr>"
        "<tr><td><code>cr:Visit</code></td><td>varies</td><td><code>nextVisit</code> chain; linked to Epoch</td></tr>"
        "<tr><td><code>cr:EligibilityCriterion</code></td><td>varies</td><td><code>hasEligibilityCriterion</code> on ProtocolVersion</td></tr>"
        "<tr><td><code>cr:Endpoint</code></td><td>varies</td><td>linked to Arm via Objective</td></tr>"
        "<tr><td>Others (Scope, Temporal, &hellip;)</td><td>varies</td><td>biomedical concepts, amendments</td></tr>"
        "</table>"

        "<h2>Running the transformer yourself</h2>"
        "<pre>"
        "# from repo root\n"
        "python3 examples/usdm/to-ngsi-ld.py \\\n"
        "    examples/usdm/ly900018-usdm-v4.json \\\n"
        "    --out examples/usdm/out/\n"
        "\n"
        "# POST to a local Scorpio broker\n"
        "for f in examples/usdm/out/*.json; do\n"
        "  curl -s -X POST http://localhost:9090/ngsi-ld/v1/entities \\\n"
        "    -H 'Content-Type: application/ld+json' \\\n"
        "    -d @$f\n"
        "done\n"
        "</pre>"
        "<p class='muted'>The transformer is idempotent: POST the same file twice and the broker "
        "upserts (no duplicate entities). Entities that differ only in <code>observedAt</code> "
        "are treated as updates; entities that differ in <code>validFrom</code> or other "
        "bitemporal properties create a new version snapshot.</p>"

        "<h2>What&rsquo;s next</h2>"
        "<ul>"
        "<li><b>EDC streaming</b> &mdash; a Kafka consumer subscribing to a Castor EDC "
        "topic ingests subject-level <code>cr:Assessment</code> and <code>cr:Enrollment</code> "
        "entities as they are CRF-captured, linking them to the <code>cr:StudySubject</code> "
        "anchor. The PII bridge (<code>cr:Enrollment</code> → <code>hcls:Person</code>) stays "
        "encrypted at rest and is not written to the broker.</li>"
        "<li><b>Veeva DDA catch-up</b> &mdash; a bulk loader reads an ODM-XML export from S3, "
        "resolves subjects and visits against the already-loaded protocol graph, and emits "
        "clinical <code>hcls:Observation</code> entities timestamped with the original "
        "collection date (<code>validFrom</code>) vs the import date (<code>observedAt</code>).</li>"
        "<li><b>LLM field mapping</b> &mdash; sponsor-specific <code>X_WHATEVER</code> fields "
        "in Medidata are emitted as <code>cr:OperationalRecord</code> entities with a "
        "<code>cx:mappingConfidence</code> score from the LLM inference step. A human reviewer "
        "promotes confirmed mappings to canonical <code>cx:Mapping</code> records.</li>"
        "</ul>"
    )


def reference_body():
    parts = ["<h1>Full reference</h1><p class='muted'>Every entity, constraint, and projection &mdash; auto-generated from the model.</p><h2>Entities by module</h2>"]
    for fname, iris in PER_FILE.items():
        ents = [i for i in iris if not (str(i).startswith(TOP) and str(i).split("#")[-1] in CLOS)]
        if ents:
            parts.append(f"<h4 class='muted' style='font-family:monospace'>{fname}</h4>" + entities_table(ents))
    parts.append("<h2>All constraints</h2>" + constraints_table(list(SHAPES.keys())))
    parts.append("<h2>All projections</h2>" + projections_table("ALL"))
    return "".join(parts)


def implementation_body():
    return """
<h1>Implementation guide &mdash; build your own graph</h1>
<p class='lead'>This is a <b>reference asset</b>, not a runtime: standard W3C artifacts
(RDF / OWL / SHACL / SPARQL / SKOS / PROV) you load into <i>any</i> graph store to give your
own clinical-research knowledge graph the operator model, the constraints, and the standard
views &mdash; out of the box. Nothing here is vendor-specific.</p>
<p class='note'>A deployable <b>reference architecture and demo</b> (an AWS Garnet / NGSI-LD CDK
deployment plus a mapping workbench) ship separately with the community release. This page is
about leveraging the reference <i>on your own stack</i> &mdash; today, with tools you already have.</p>

<h2>1 &middot; What you get</h2>
<table>
<tr><th>artifact</th><th>where</th><th>what it's for</th></tr>
<tr><td>Ontology modules</td><td><code>ontology/*.ttl</code></td><td>the layered model (top &rarr; hcls &rarr; cr), incl. the bitemporal Schedule of Activities</td></tr>
<tr><td>SHACL shapes</td><td><code>shapes/*.ttl</code></td><td>graded constraints (Violation / Warning) you validate your data against</td></tr>
<tr><td>SPARQL projections</td><td><code>projections/*.rq</code></td><td>standard views (SDTM, USDM, FHIR, SoA, planned-vs-actual&hellip;) as queries</td></tr>
<tr><td>Crosswalks</td><td><code>crosswalks/*.ttl</code></td><td>owned SSSOM mappings (incl. USDM&nbsp;v4.0&nbsp;&harr;&nbsp;cr-core)</td></tr>
<tr><td>USDM&nbsp;v4.0 OWL + CT</td><td><code>ontology/vendor/usdm/</code></td><td>generated USDM class model + SKOS codelists, NCIt-anchored (the crosswalk target)</td></tr>
<tr><td>Merged bundles</td><td><code>docs/dist/</code></td><td>byte-reproducible Turtle / JSON-LD / N-Triples of the model, shapes, and crosswalks, plus a <code>SHA256SUMS</code></td></tr>
<tr><td>NGSI-LD context</td><td><code>dist/top-cr-v1.ngsi-context.jsonld</code></td><td>a term&rarr;IRI dictionary to load entities into any NGSI-LD broker</td></tr>
</table>

<h2>2 &middot; Get the artifacts</h2>
<p>Two equivalent sources. The <b>repository</b> (<code>cr-domain/</code>) holds the source
modules &mdash; clone or vendor them. The <b>prebuilt bundles</b> in <code>dist/</code> are a
single merged file per layer, regenerated deterministically by <code>docs/build_dist.py</code>
and <b>pinned by checksum</b>:</p>
<pre>sha256sum -c SHA256SUMS        # verify the bundle you pinned, in dist/</pre>
<p class='muted'>The download links above are served from this site's <code>dist/</code> folder
(and mirrored in the repo). When self-hosting, serve <code>dist/</code> alongside these pages,
or reference the repository directly &mdash; the <code>SHA256SUMS</code> lets consumers pin an
exact version regardless of where they fetched it.</p>

<h2>3 &middot; Load it into your store</h2>
<p>It's standard RDF, so any triplestore or RDF-capable graph DB works. A few concrete starts:</p>
<h4>Python (RDFLib + pySHACL)</h4>
<pre>from rdflib import Graph
g = Graph().parse("dist/top-cr-v1.ttl", format="turtle")   # the merged model
g.parse("my-study-data.ttl", format="turtle")              # your instance data</pre>
<h4>Neo4j (neosemantics / n10s)</h4>
<pre>CALL n10s.graphconfig.init({handleVocabUris:'SHORTEN'});
CALL n10s.rdf.import.fetch('https://&lt;host&gt;/dist/top-cr-v1.ttl','Turtle');
CALL n10s.rdf.import.fetch('https://&lt;host&gt;/dist/top-cr-shapes-v1.ttl','Turtle');</pre>
<h4>Apache Jena / Fuseki, GraphDB, Blazegraph, &hellip;</h4>
<pre># load the Turtle bundle into a dataset, then query with SPARQL 1.1
fuseki> :data UPLOAD dist/top-cr-v1.ttl
# or RDF4J / GraphDB: import top-cr-v1.ttl into a repository</pre>
<h4>NGSI-LD broker (e.g. Scorpio)</h4>
<pre># load entities using the published @context so terms resolve to cr:/top: IRIs
Link: &lt;https://&lt;host&gt;/dist/top-cr-v1.ngsi-context.jsonld&gt;; rel="http://www.w3.org/ns/json-ld#context"
# top:observedAt resolves to NGSI-LD core observedAt (valid time)</pre>

<h2>4 &middot; Validate with the shapes</h2>
<p>Run the graded SHACL shapes against your data &mdash; hard structural rules surface as
<code>Violation</code>, risk-proportionate ones as <code>Warning</code>:</p>
<pre>from pyshacl import validate
conforms, _, report = validate(
    my_data_graph,
    shacl_graph="dist/top-cr-shapes-v1.ttl",
    ont_graph="dist/top-cr-v1.ttl",
    inference="rdfs", advanced=True)   # advanced=True enables the SPARQL constraints</pre>
<p class='muted'>Any SHACL engine works (pySHACL, Apache Jena <code>shacl</code>, TopBraid). The
test harness <code>tests/run_tests.py</code> is a worked example of validating instance data.</p>

<h2>5 &middot; Project to standards (define once, view many)</h2>
<p>The standards are <b>queries</b>, not separate databases. Run a projection over your graph to
emit that view &mdash; e.g. <code>projections/sdtm_dm.rq</code> (CDISC SDTM demographics),
<code>projections/usdm_study.rq</code>, <code>projections/soa_table.rq</code> (the SoA table as a
view of the timeline), or <code>projections/planned_vs_actual.rq</code> (visit reconciliation).
Same native graph, many standardized outputs, guaranteed consistent.</p>

<h2>6 &middot; Ingest an M11 / USDM protocol</h2>
<p>To turn a protocol into a TOP-grounded graph: load the vendored
<code>ontology/vendor/usdm/usdm-v4.ttl</code> (the USDM class model) and apply
<code>crosswalks/usdm-to-cr.ttl</code> to map USDM constructs onto cr-core &mdash; respecting the
<b>plan&harr;execution boundary</b> (USDM is design-time; cr-core is execution + provenance).
<code>tools/usdm-rdf-gen/ingest_usdm.py</code> does exactly this for real on the public, MIT-licensed
CDISC Pilot (LZZT) study &mdash; emitting <code>examples/usdm-cdisc-pilot-ingested.ttl</code>,
which validates green &mdash; and <code>examples/usdm-cdisc-pilot-conformant.ttl</code> is a
clean hand-authored illustration of the target shape. USDM classes and codelists are
NCIt-anchored (verified against the NCI Thesaurus), so your graph inherits a verifiable
terminology spine.</p>

<h2>7 &middot; Honor the conventions (so graphs line up)</h2>
<ul>
<li><b>Universal DNA</b> on every entity: <code>top:identifier</code> + <code>top:observedAt</code>
(valid time) + <code>top:status</code>. This is what makes any two TOP graphs align by construction.</li>
<li><b>Bitemporal envelope:</b> add <code>top:recordedAt</code> (and <code>top:supersededAt</code> on
correction) so you can reconstruct any past state &ldquo;as of&rdquo; a date. Corrections are new
assertions, never rewrites.</li>
<li><b>Provenance:</b> <code>prov:wasAttributedTo</code> on every fact &mdash; who asserted it.</li>
<li><b>NGSI-LD mapping:</b> <code>top:observedAt</code> &asymp; NGSI-LD <code>observedAt</code>;
<code>top:recordedAt</code>/<code>supersededAt</code> &asymp; <code>createdAt</code>/<code>modifiedAt</code>.</li>
</ul>
<p>See the <a href="foundation.html">Foundation</a> page for the model and the
<code>conventions.md</code> file for the full envelope.</p>

<h2>What's out of scope here</h2>
<p>The runtime, automated data mapping, and a one-command deployable stack are <b>not</b> part of
this reference &mdash; they come with the community release's reference architecture and workbench.
This guide is deliberately tool-agnostic: it shows how to stand the <i>reference</i> up anywhere.</p>
"""


def roles_body():  # noqa: C901
    CR = "https://top.scientix.ai/cr/v1#"
    HCLS = "https://top.scientix.ai/hcls/v1#"
    HCLS_NS = URIRef(HCLS)

    hcls_action = URIRef(HCLS + "Action")
    hcls_phase = URIRef(HCLS + "Phase")
    hcls_jtbd = URIRef(HCLS + "JobToBeDone")
    p_authz = URIRef(HCLS + "authorizedAgentType")
    p_occurs = URIRef(HCLS + "occursIn")
    p_operates = URIRef(HCLS + "operatesOn")
    p_contains = URIRef(HCLS + "contains")
    p_precedes = URIRef(HCLS + "precedes")
    p_job_of = URIRef(HCLS + "jobOfAgentType")
    p_trigger = URIRef(HCLS + "jobTrigger")
    p_signal = URIRef(HCLS + "successSignal")
    p_executes = URIRef(HCLS + "executesAction")
    p_involves = URIRef(HCLS + "involvesObject")

    # ---- agent type table ----
    agent_hier = [
        ("cr:Investigator", "hcls:Clinician", "Site"),
        ("cr:SiteCoordinator", "hcls:Practitioner", "Site"),
        ("cr:ClinicalResearchAssociate", "hcls:Person", "CRO / Sponsor"),
        ("cr:SponsorProjectManager", "hcls:Person", "Sponsor"),
        ("cr:SponsorOperationsStaff", "hcls:Person", "Sponsor"),
        ("cr:DataManager", "hcls:Person", "Sponsor / CRO"),
        ("cr:SponsorQualityStaff", "hcls:Person", "Sponsor"),
        ("cr:RegulatoryAffairsSpecialist", "hcls:Person", "Sponsor"),
        ("cr:PharmacovigilianceSpecialist", "hcls:Person", "Sponsor / CRO"),
        ("cr:FinanceStaff", "hcls:Person", "Sponsor"),
    ]
    agent_rows = ""
    for qname, parent, org in agent_hier:
        local = qname.split(":")[1]
        iri = URIRef(CR + local)
        label = str(MERGED.value(iri, RDFS.label) or local)
        comment = str(MERGED.value(iri, RDFS.comment) or "")
        # count authorized actions
        n_actions = len(list(MERGED.subjects(p_authz, iri)))
        agent_rows += (
            f"<tr><td><code>{esc(qname)}</code></td>"
            f"<td>{esc(label)}</td>"
            f"<td><code>{esc(parent)}</code></td>"
            f"<td>{esc(org)}</td>"
            f"<td style='text-align:center'>{n_actions}</td>"
            f"<td style='font-size:12px'>{esc(comment[:120])}{'&hellip;' if len(comment)>120 else ''}</td></tr>"
        )
    agent_table = (
        "<table><tr><th>class</th><th>label</th><th>superclass</th>"
        "<th>org boundary</th><th>actions</th><th>description</th></tr>"
        f"{agent_rows}</table>"
    )

    # ---- phase tree ----
    def phase_rows(phase_iri, depth=0):
        label = str(MERGED.value(phase_iri, RDFS.label) or phase_iri)
        comment = str(MERGED.value(phase_iri, RDFS.comment) or "")
        qname = qn(phase_iri)
        indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * depth
        n_act = len(list(MERGED.subjects(p_occurs, phase_iri)))
        rows = (f"<tr><td>{indent}<code>{esc(qname)}</code></td>"
                f"<td>{esc(label)}</td>"
                f"<td style='text-align:center'>{n_act if n_act else '&mdash;'}</td>"
                f"<td style='font-size:12px'>{esc(comment[:100])}{'&hellip;' if len(comment)>100 else ''}</td></tr>")
        for child in MERGED.objects(phase_iri, p_contains):
            rows += phase_rows(child, depth + 1)
        return rows

    root_phase = URIRef(CR + "TrialLifecycle")
    phase_table = (
        "<table><tr><th>phase</th><th>label</th><th>actions</th><th>description</th></tr>"
        + phase_rows(root_phase)
        + "</table>"
    )

    # ---- actions by role/phase summary ----
    # Build a matrix: role -> phase -> [action labels]
    from collections import defaultdict
    role_phase_actions = defaultdict(lambda: defaultdict(list))
    for action in MERGED.subjects(RDF.type, hcls_action):
        action_label = str(MERGED.value(action, RDFS.label) or qn(action))
        phase = MERGED.value(action, p_occurs)
        phase_label = str(MERGED.value(phase, RDFS.label) or qn(phase)) if phase else "—"
        for role in MERGED.objects(action, p_authz):
            role_label = str(MERGED.value(role, RDFS.label) or qn(role))
            role_phase_actions[role_label][phase_label].append(action_label)

    action_rows = ""
    for role_label in sorted(role_phase_actions):
        for phase_label in sorted(role_phase_actions[role_label]):
            acts = sorted(role_phase_actions[role_label][phase_label])
            pills = " ".join(f"<code style='margin:1px 2px;display:inline-block'>{esc(a)}</code>" for a in acts)
            action_rows += (
                f"<tr><td><b>{esc(role_label)}</b></td>"
                f"<td>{esc(phase_label)}</td>"
                f"<td style='font-size:12px'>{pills}</td></tr>"
            )
    action_table = (
        "<table><tr><th>role</th><th>phase</th><th>authorized actions</th></tr>"
        f"{action_rows}</table>"
    )

    # ---- JTBD ----
    jtbd_rows = ""
    current_role = None
    for jtbd in sorted(MERGED.subjects(RDF.type, hcls_jtbd), key=lambda x: str(x)):
        label = str(MERGED.value(jtbd, RDFS.label) or qn(jtbd))
        role_iri = MERGED.value(jtbd, p_job_of)
        role_label = str(MERGED.value(role_iri, RDFS.label) or qn(role_iri)) if role_iri else "—"
        trigger = str(MERGED.value(jtbd, p_trigger) or "")
        signals = [str(s) for s in MERGED.objects(jtbd, p_signal)]
        sig_html = "<ul>" + "".join(f"<li>{esc(s)}</li>" for s in signals) + "</ul>" if signals else ""
        if role_label != current_role:
            current_role = role_label
            jtbd_rows += f"<tr style='background:var(--pale)'><td colspan='3'><b>{esc(role_label)}</b></td></tr>"
        jtbd_rows += (
            f"<tr><td>{esc(label)}</td>"
            f"<td style='font-size:12px'>{esc(trigger)}</td>"
            f"<td style='font-size:12px'>{sig_html}</td></tr>"
        )
    jtbd_table = (
        "<table><tr><th>job to be done</th><th>trigger</th><th>success signals</th></tr>"
        f"{jtbd_rows}</table>"
    )

    sparql = (
        "SELECT ?action ?label WHERE {\n"
        "  ?action hcls:authorizedAgentType cr:SiteCoordinator ;\n"
        "          hcls:occursIn ?phase ;\n"
        "          rdfs:label ?label .\n"
        "  # include sub-phases:\n"
        "  cr:ConductPhase hcls:contains+ ?phase .\n"
        "}"
    )

    return (
        "<h1>Roles, phases &amp; actions</h1>"
        "<p class='lead'>Who can do what, when &mdash; the operator-grounding layer. "
        "Authorization binds directly to OWL agent type classes; no separate Role intermediary. "
        "A real <code>hcls:Person</code> is typed as one of these classes; their contextual title "
        "within a Study is a plain string (<code>hcls:actsAs</code>).</p>"

        "<h2>Design principles</h2>"
        "<ul>"
        "<li><b>Agent types are OWL classes</b>, not named individuals. A Person typed as "
        "<code>cr:Investigator</code> inherits all authorizations declared on that class.</li>"
        "<li><b>Delegation at instance time</b>: the PI delegates to staff via <code>cr:Delegation</code> "
        "acts; <code>top:authorizedBy</code> on the Person records who delegated to them. "
        "The DoA log is a SPARQL projection of those acts, not a maintained spreadsheet.</li>"
        "<li><b>Credentials at instance time</b>: <code>top:hasCredential</code> on Person "
        "&rarr; <code>top:Credential</code>. A delegated task requires both delegation and "
        "the matching credential before it may proceed.</li>"
        "<li><b>Regulatory constraint is additive</b>: some actions carry a "
        "<code>top:RegulatoryLaw</code> individual (e.g. ICH E6(R3) mandate to delegate "
        "at the site level). Most do not.</li>"
        "</ul>"

        "<h2>Agent type taxonomy</h2>"
        "<p>Ten OWL classes organized into site-boundary (delegated from PI) and "
        "sponsor/CRO-boundary roles.</p>"
        f"{agent_table}"

        "<h2>Trial lifecycle phases</h2>"
        "<p>Three top-level phases (<code>cr:StartupPhase</code>, <code>cr:ConductPhase</code>, "
        "<code>cr:CloseoutPhase</code>) form a containment tree and a precedence chain. "
        "Actions bind to sub-phases via <code>hcls:occursIn</code>; the <code>hcls:contains+</code> "
        "transitive closure lets you query all actions within a top-level phase.</p>"
        f"{phase_table}"

        "<h2>Authorization query pattern</h2>"
        "<p>To answer <i>\"What am I authorized to do right now?\"</i> given an agent type and phase:</p>"
        f"<pre>{esc(sparql)}</pre>"

        "<h2>Actions by role and phase</h2>"
        "<p>All authorized actions from <code>cr-core-actions.ttl</code>, grouped by role and sub-phase. "
        "Multi-role actions appear in each authorized role&rsquo;s row.</p>"
        f"{action_table}"

        "<h2>Jobs to Be Done</h2>"
        "<p>Each JTBD is a bounded unit of operator intent: the goal an agent type is trying to achieve, "
        "the event that triggers it, and the measurable signals that confirm it&rsquo;s done. "
        "Derived from the OOUX JTBD blocks in the OOUX Map v0.2.</p>"
        f"{jtbd_table}"
    )


def build():
    n_cls = len([1 for iris in PER_FILE.values() for i in iris
                 if not (str(i).startswith(TOP) and str(i).split("#")[-1] in CLOS)])
    man = json.load(open(os.path.join(ROOT, "tests", "manifest.json")))
    stats = dict(c=n_cls, s=len(SHAPES), p=len(PROJ), e=len(glob.glob(os.path.join(ROOT, "examples", "*.ttl"))), t=len(man))
    out = os.path.join(ROOT, "docs")
    pages = {"index.html": ("TOP CR &mdash; Overview", "hub", hub_body(stats)),
             "foundation.html": ("Foundation", "foundation", foundation_body()),
             "implementation.html": ("Implementation guide", "implementation", implementation_body()),
             "ingestion.html": ("Ingestion example", "ingestion", ingestion_body()),
             "reference.html": ("Full reference", "reference", reference_body())}
    for fl in FLOWS:
        body = roles_body() if fl["id"] == "roles" else flow_body(fl)
        pages[f"{fl['id']}.html"] = (fl["title"], fl["id"], body)
    for fname, (title, active, body) in pages.items():
        open(os.path.join(out, fname), "w").write(shell(title, active, body))
    print(f"Wrote {len(pages)} pages to {out}/")
    print("  " + ", ".join(sorted(pages)))


if __name__ == "__main__":
    build()
