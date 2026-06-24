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

from rdflib import Graph, RDF, RDFS, OWL, URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_screens import render_stop, SCREEN_CSS  # noqa: E402
from build_dist import MAST  # noqa: E402  (masthead: single source of truth for version/license/authorship)

TOP = "https://top.scientix.ai/core/v1#"
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
    items = [("index.html", "Overview", "hub"), ("foundation.html", "Foundation", "foundation"),
             ("implementation.html", "Implementation guide", "implementation")]
    flowitems = [(f"{fl['id']}.html", fl["title"], fl["id"]) for fl in FLOWS]
    out = ['<b>Start</b>']
    for href, t, i in items:
        out.append(f'<a class="{"on" if i==active else ""}" href="{href}">{t}</a>')
    out.append('<b>Flows / sub-domains</b>')
    for href, t, i in flowitems:
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
    howto = """
<div class="step"><span class="num">1</span><div><h4>Map your entities to the model</h4>
<p>Point your concepts at the shared ones (patient&rarr;<code>hcls:Person</code>, your subject&rarr;<code>cr:StudySubject</code>, a value&rarr;<code>cr:ClinicalObservation</code>). You align, you don't redesign.</p></div></div>
<div class="step"><span class="num">2</span><div><h4>Attach the envelope</h4>
<pre>ex:obs1 a cr:ClinicalObservation ; rdf:value "128" ;
    cr:forSubject ex:subj-001 ;            <span class="c"># pseudonymous, never a Person</span>
    top:observedAt  "2026-03-10T09:00:00Z" ; <span class="c"># true-in-world time</span>
    top:recordedAt "2026-03-10T09:05:00Z" ; <span class="c"># when the system knew it</span>
    prov:wasAttributedTo ex:coordinator .</pre></div></div>
<div class="step"><span class="num">3</span><div><h4>Validate &mdash; the graph catches PII leaks, undelegated work, orphan data, premature activation, unmitigated risk.</h4></div></div>
<div class="step"><span class="num">4</span><div><h4>Emit what you need</h4><p>Run a projection &rarr; SDTM, USDM, FHIR, the DOA log, a data mart, ADaM lineage &mdash; provenance intact.</p></div></div>
<div class="step"><span class="num">5</span><div><h4>Ask questions across time</h4><p>As-of reconstruction, lineage walks, and bitemporal compliance ("reported within 15 days?") are queries, not reconstructions.</p></div></div>
"""
    limits = """<ul>
<li><b>Not here:</b> agent orchestration, the runtime/broker &mdash; those consume the reference; they aren't part of it.</li>
<li><b>Pseudonymized, not anonymized:</b> identifiable data is kept from flowing downstream, but statistical anonymization is an upstream/runtime responsibility.</li>
<li><b>Scope today:</b> oncology, Pre-IND &rarr; End-of-Phase-2, plus the site-operations layer. The architecture generalizes; the content is bounded.</li></ul>"""
    return (
        "<h1>TOP &mdash; Clinical Research Reference Graph</h1>"
        "<p class='tag'>An inheritable, provenance-native, bitemporal model of how a clinical trial runs. Open commons &middot; organized by flow.</p>"
        f"<div class='stats'><div><b>{stats['c']}</b><br>entities</div><div><b>{stats['s']}</b><br>rules</div>"
        f"<div><b>{stats['p']}</b><br>views</div><div><b>{stats['e']}</b><br>examples</div><div><b>{stats['t']}</b><br>tested</div></div>"
        f"{download_badges('top-cr-v1', 'Download the model')}"
        "<p class='muted' style='font-size:12px;margin-top:4px'>Apache-2.0 &middot; "
        f"<code>{esc(MAST['namespace'])}</code> &middot; see <a href='foundation.html'>Foundation</a> for full masthead &amp; citation.</p>"
        "<h2 id='what'>What this is</h2>"
        "<p class='lead'>A ready-made, shared model of how a clinical trial actually runs &mdash; from a site's first activation through an End-of-Phase-2 decision. "
        "Instead of every organization re-inventing how to represent studies, subjects, visits, samples, consent and safety data, <b>you inherit a model the industry can share, and your own data plugs into it.</b></p>"
        "<p>Because it captures <i>who did what, when, and on what evidence</i> &mdash; and remembers every version of the truth over time &mdash; the documents you already owe (SDTM, USDM, a delegation log, an analysis dataset) come out as <b>views</b>, and a regulator's question becomes a <b>query</b>.</p>"
        "<h2 id='value'>The value</h2>"
        f"<div class='cards'>{cardhtml}</div>"
        "<h2 id='line'>The trial as a workflow &mdash; click a stop</h2>"
        f"<div class='trainline'>{chips}</div>"
        f"<div class='flowgrid'>{flowcards}</div>"
        "<h2 id='howto'>How to put it to work on your data</h2>"
        f"{howto}"
        "<p class='note'>You brought thin data in your own shape; you got a validated, provenanced, regulator-ready graph &mdash; and the documents you owe come out as views.</p>"
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
        "<p class='lead'>Everything specializes <b>eight universal categories</b> (the Category-Level Objects), all rooted in a single <code>top:Core</code>. A small shared top keeps the model legible; the richness lives in the domain leaves.</p>"
        "<p>Layers add specificity: <code>top</code> (universal) &rarr; <code>hcls</code> (health &amp; life sciences) &rarr; <code>cr</code> (clinical research). Each flow page below specializes these.</p>"
        "<h2>Universal DNA</h2>"
        "<p>Every entity, whatever its category, carries three strands: <b>identity</b> (<code>top:identifier</code>), "
        "<b>time</b> (<code>top:observedAt</code> &mdash; the canonical NGSI-LD valid-time term), and <b>lifecycle</b> "
        "(<code>top:status</code>). <code>top:UniversalDNAShape</code> enforces it. This is what makes any two TOP "
        "graphs line up by construction.</p>"
        "<h2>The eight categories</h2>"
        f"<table><tr><th>category</th><th>specialized into (examples across the domain)</th></tr>{clo_rows}</table>"
        "<h2>The non-negotiable spine</h2>"
        "<ul><li><b>Bitemporal:</b> every assertion carries valid time (true-in-world) and transaction time (system knowledge); the past is reconstructable and back-dating is impossible.</li>"
        "<li><b>Provenance:</b> W3C PROV on every fact &mdash; who, when, on what evidence.</li>"
        "<li><b>PII containment:</b> identifiable <code>hcls:Person</code> is boundary-only; downstream attaches to the pseudonymous <code>cr:StudySubject</code>; the only legal bridge is the attested Enrollment.</li></ul>"
        "<h2>HCLS-core entities (shared across HCLS domains)</h2>"
        f"{entities_table(found)}")


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
<tr><td>OWL-DL well-formedness gate</td><td><code>tools/owl_lint.py</code></td><td>CI-enforced proof the ontology is sound &ldquo;ingredients&rdquo; for your reasoner (&sect;5)</td></tr>
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
<p><b>Pick a serialization.</b> Every bundle ships in three byte-equivalent forms:
<code>.ttl</code> (Turtle &mdash; read, author, load), <code>.jsonld</code> (JSON-LD &mdash; web/JS
toolchains; the separate <code>*.ngsi-context.jsonld</code> is the broker term map), and
<code>.nt</code> (N-Triples &mdash; one canonical triple per line: stream-load into large stores,
line-diff cleanly across versions, and the form the <code>SHA256SUMS</code> hashes over). Same
triples, different envelope &mdash; choose by tool, not by content.</p>

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
<p>The broker is the <b>runtime serving layer</b> &mdash; not another triplestore for the model.
You load <i>instance entities</i> into it (after reasoning and validating offline); see
<b>&sect;6&nbsp;&mdash;&nbsp;Serve it</b> below for the <code>@context</code> and the term mapping.</p>

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
test harness <code>tests/run_tests.py</code> is a worked example of validating instance data.
The shapes are vended in all three serializations (<code>top-cr-shapes-v1.{ttl,nt,jsonld}</code>)
and pinned by <code>SHA256SUMS</code> &mdash; same graded rules, whichever your engine prefers.</p>

<h2>5 &middot; Reason over it &mdash; bring your own reasoner</h2>
<p>This reference ships the <b>ingredients, not the baked cake</b>: it does <b>not</b> run a
reasoner. Classification, materialization, and entailment are the consumer's job &mdash; which
reasoner, at what profile, and when you materialize are <i>your</i> deployment decisions, not the
reference's. What the reference guarantees is that the ingredients are <b>sound</b>: the OWL is
authored to the OWL&nbsp;2&nbsp;DL typing discipline, and a CI gate
(<code>tools/owl_lint.py</code>) proves it on every change &mdash; no illegal punning, every term
declared, every <code>domain</code>/<code>range</code> well-typed &mdash; so a reasoner you point
at it returns sound entailments, not garbage.</p>
<p><b>Profile.</b> The model is deliberately light: one rooted class hierarchy, object/datatype
properties with <code>rdfs:domain</code>/<code>rdfs:range</code>, and a few
<code>owl:inverseOf</code> pairs. That sits inside <b>both</b> OWL&nbsp;2&nbsp;RL and
OWL&nbsp;2&nbsp;DL, so it runs unchanged in rule reasoners (owlrl, RDFox, GraphDB&nbsp;rules) and
in tableau/EL reasoners (HermiT, ELK, Pellet). Layer your own restrictions, equivalences, or
property chains on top as your use demands &mdash; the reference stays the shared base.</p>
<p><b>What reasoning gives you</b> over the reference&nbsp;+&nbsp;your data:</p>
<ul>
<li><b>Subclass entailment</b> &mdash; a <code>cr:DoseLimitingToxicity</code> is entailed a
<code>cr:AdverseEvent</code> &rarr; <code>top:Outcome</code> &rarr; <code>top:Core</code>, so it
carries the Universal DNA.</li>
<li><b>Domain/range typing</b> &mdash; asserting <code>ex:s cr:sponsoredBy ex:o</code> types
<code>ex:s</code> a <code>cr:Study</code> and <code>ex:o</code> a <code>cr:Sponsor</code>.</li>
<li><b>Inverse fills</b> &mdash; <code>cr:hasQuery</code>&harr;<code>cr:queryOn</code>,
<code>cr:specimen</code>&harr;<code>cr:hasCustodyEvent</code>, and the other inverse pairs.</li>
<li><b>Whatever you add</b> &mdash; defined classes (necessary&amp;sufficient), property chains,
or <code>owl:disjointWith</code> (whose violation a DL reasoner reports as an inconsistency).</li>
</ul>
<h4>Python &mdash; OWL&nbsp;2&nbsp;RL, pure-Python (no Java)</h4>
<pre>from rdflib import Graph
from owlrl import DeductiveClosure, OWLRL_Semantics
g = Graph().parse("dist/top-cr-v1.ttl", format="turtle")
g.parse("my-study-data.ttl", format="turtle")
DeductiveClosure(OWLRL_Semantics).expand(g)   <span class="c"># forward-chain; g now holds the entailed triples</span></pre>
<h4>Python &mdash; OWL&nbsp;2&nbsp;DL via HermiT (owlready2, needs Java)</h4>
<pre>from owlready2 import get_ontology, sync_reasoner
onto = get_ontology("dist/top-cr-v1.ttl").load()
onto.load("my-study-data.ttl")
with onto: sync_reasoner()                     <span class="c"># HermiT: classify + detect inconsistency</span></pre>
<h4>Java / CLI &mdash; ELK or HermiT</h4>
<pre>robot reason --reasoner ELK --input top-cr-v1.ttl --output inferred.ttl
<span class="c"># or drive HermiT / ELK directly through the OWL API</span></pre>
<p class='note'><b>Reason offline, then serve.</b> Forward-chain once, persist the entailed
triples, and load <i>those</i> into your runtime store or broker &mdash; the broker doesn't reason
(next section). Re-materialize when the model or your data changes.</p>

<h2>6 &middot; Serve it &mdash; NGSI-LD as the runtime</h2>
<p>The runtime is an <b>NGSI-LD context broker</b> (e.g. Scorpio on AWS&nbsp;Garnet) &mdash; not a
reasoner, not a validator. It <b>stores entities and serves them</b>: relationships,
temporal/&ldquo;as-of&rdquo; queries, subscriptions, federation, and <b>single-pull retrieval</b>.
It does <b>not</b> load OWL axioms, classify, or run SHACL.</p>
<p>So the division of labor is clean: <b>reason</b> (&sect;5) and <b>validate</b> (&sect;4)
<i>offline</i>; load the resulting asserted&nbsp;+&nbsp;entailed&nbsp;+&nbsp;validated entities into
the broker; the broker serves them fast at the glass.</p>
<pre><span class="c"># load entities under the published @context so JSON terms resolve to cr:/top: IRIs</span>
Link: &lt;https://&lt;host&gt;/dist/top-cr-v1.ngsi-context.jsonld&gt;; rel="http://www.w3.org/ns/json-ld#context"
<span class="c"># top:observedAt -> NGSI-LD core observedAt (valid time)</span>
<span class="c"># top:recordedAt / top:supersededAt -> createdAt / modifiedAt</span></pre>
<p><b>Single-pull retrieval.</b> The model is shaped so each operator screen resolves to <b>one
self-contained entity</b> that already carries its green-check facts &mdash; no recursive lookups
at the glass. <code>tools/ngsild_view.py</code> builds these views, and the per-flow pages show
the screen each one feeds.</p>
<p class='muted'>A deployable Garnet / NGSI-LD CDK stack and a mapping workbench ship with the
community release; this section is the architecture, not that deployment.</p>

<h2>7 &middot; Project to standards (define once, view many)</h2>
<p>The standards are <b>queries</b>, not separate databases. Run a projection over your graph to
emit that view &mdash; e.g. <code>projections/sdtm_dm.rq</code> (CDISC SDTM demographics),
<code>projections/usdm_study.rq</code>, <code>projections/soa_table.rq</code> (the SoA table as a
view of the timeline), or <code>projections/planned_vs_actual.rq</code> (visit reconciliation).
Same native graph, many standardized outputs, guaranteed consistent.</p>

<h2>8 &middot; Ingest an M11 / USDM protocol</h2>
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

<h2>9 &middot; Honor the conventions (so graphs line up)</h2>
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


def build():
    n_cls = len([1 for iris in PER_FILE.values() for i in iris
                 if not (str(i).startswith(TOP) and str(i).split("#")[-1] in CLOS)])
    man = json.load(open(os.path.join(ROOT, "tests", "manifest.json")))
    stats = dict(c=n_cls, s=len(SHAPES), p=len(PROJ), e=len(glob.glob(os.path.join(ROOT, "examples", "*.ttl"))), t=len(man))
    out = os.path.join(ROOT, "docs")
    pages = {"index.html": ("TOP CR &mdash; Overview", "hub", hub_body(stats)),
             "foundation.html": ("Foundation", "foundation", foundation_body()),
             "implementation.html": ("Implementation guide", "implementation", implementation_body()),
             "reference.html": ("Full reference", "reference", reference_body())}
    for fl in FLOWS:
        pages[f"{fl['id']}.html"] = (fl["title"], fl["id"], flow_body(fl))
    for fname, (title, active, body) in pages.items():
        open(os.path.join(out, fname), "w").write(shell(title, active, body))
    print(f"Wrote {len(pages)} pages to {out}/")
    print("  " + ", ".join(sorted(pages)))


if __name__ == "__main__":
    build()
