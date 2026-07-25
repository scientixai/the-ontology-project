# TOP HCLS · Clinical-Research v1

The first workflow extension TOP ships — the load-bearing demonstrator that Core composes
into a real, regulated-industry reference graph without distorting Core. Scope, patterns,
and worked examples live in the seed:
[`governance/planning/top-hcls-clinical-research.md`](../../../governance/planning/top-hcls-clinical-research.md).
This directory is the implementation.

- **Prefix:** `topcr:` → `https://w3id.org/top/hcls/clinical-research/v1#`
- **Namespace:** authored against the w3id base per
  [RFC-0001](../../../governance/rfcs/proposed/0001-namespace-migration-w3id.md). All new
  work uses `w3id.org/top` from the start so nothing is written against the old base.
- **Status:** seed directory. Anchor classes from the three worked examples are in place;
  the full 12-area class catalog ships in subsequent PRs (per the seed, the catalog is
  authored area-by-area, not in one drop).

---

## Definition of Done — clinical-research v1

> Resolves the seed's Open Question #5 ("what concrete demo readiness counts as *TOP
> ships clinical-research v1*") and the cycle-planning blocker "T.O.P. clinical research
> v1, defined in one paragraph." This is the launch envelope. On ratification it becomes
> **ADR-0025**; until the Clinical Research WG forms, Bo signs as sole signatory.

**In one paragraph.** Clinical-research v1 is *done* when the `hcls/clinical-research/v1/`
directory publishes a SHACL-valid reference graph in which **all twelve functional areas
are represented by at least one operator-grounded anchor class**, every class is
**anchored to NCIt** (Tier-1 `skos:exactMatch`) and, where it crosses into care,
**declares a Pattern-B `subClassOf` against a `topcd:` stub with a one-line operator
justification**; the **three worked examples** (Pharmacovigilance AE family, Intervention
oncology overlap, Study-Design USDM alignment) are authored as real triples; **at least
one full walkthrough TTL** runs end to end; the **site-SOP vocabulary ships as a separate
aligned file** (Path b); the alignment machinery (NCIt subset whitelist, EVS mapsets as
pinned SSSOM, Tier-4 FDA attachments) is **present and version-stamped**; and a **spec
page** presents all of the above — such that the JPM Healthcare Week 2027 audience can
read it as serious and practitioner-grounded.

### Done checklist (the launch envelope)

- [ ] **12 functional areas, ≥1 anchor class each** — Study Design, Regulatory Affairs,
      Finance, Setup, Site Management, Clinical Supply, Recruitment, Intervention,
      Pharmacovigilance, Data Management, Monitoring, Quality Management.
- [ ] **NCIt Tier-1 anchoring** — every class carries `skos:exactMatch ncit:*`,
      `skos:prefLabel`, and operator `skos:altLabel`s.
- [ ] **Pattern-B cross-workflow discipline** — every class that crosses into care
      declares `rdfs:subClassOf topcd:*` (stub) with a one-line operator-grounded
      `rdfs:comment`. No cross-declaration that fails the operator test (e.g. `Sponsor
      subClassOf Organization`).
- [ ] **Three worked examples authored as triples** — PV AE family
      (AdverseEvent → SeriousAdverseEvent → SUSAR), Intervention oncology overlap
      (Study/Concomitant MedicationAdministration), Study Design
      (Protocol, ScheduleOfActivities, EligibilityCriterion).
- [ ] **≥1 full walkthrough TTL** end to end (candidate: Maria's Cycle 1 Day 1 visit).
- [ ] **Site-SOP vocabulary** shipped as `site-sop-vocabulary.ttl` (Path b), with
      `skos:closeMatch` bridges and its own source provenance.
- [ ] **Alignment machinery present & pinned** — NCIt subset whitelist (10 subsets),
      EVS REST mapsets (8) imported as SSSOM at pinned versions, Tier-4 FDA attachments
      (UNII, SPL, GUDID, ICSR).
- [ ] **clinical-care Pattern-B stubs** exist in `hcls/clinical-care/v1/` — enough
      structure for SHACL to pass; honest about being stubs.
- [ ] **SHACL validation green** — one shapes file per functional area; the four-layer
      enforcement (ADR-0010) passes on the whole directory.
- [ ] **Spec page** following the `core/v1/index.html` shape (summary, layering,
      functional areas, alignment summary, cross-workflow declarations, SHACL, deferred).

### Explicitly NOT required for v1 (deferred — do not let these block done)

FHIR R5 alignment · RxNorm & LOINC (UMLS dependency) · Bioregistry registration ·
oncology Pattern-C escalation · full clinical-care extension · pharmacovigilance
graduation to its own extension · the NGSI-LD JSON-LD `@context` (ADR-0014 deferred).

---

## Directory layout

```
hcls/clinical-research/v1/
  README.md                      this file (spec + Definition of Done)
  clinical-research.ttl          ontology header, prefixes, anchor classes,
                                 12 functional-area sections (worked examples filled;
                                 remaining areas marked TODO for subsequent PRs)
  shapes.ttl                     SHACL — one shape section per functional area (skeleton)
  crosswalks/
    README.md                    how mapsets are pinned and refreshed
    ncit-to-meddra.sssom.tsv     SSSOM template (metadata block + example rows)
hcls/clinical-care/v1/
  README.md                      stub note
  clinical-care-stubs.ttl        topcd:* placeholder classes clinical-research crosses into
```

## How to extend

Author one functional area per PR. Each class: `a owl:Class`; `rdfs:subClassOf` a Core
primitive (and `prov:*`); `skos:exactMatch` an NCIt code; `skos:prefLabel` +
operator `skos:altLabel`s; a Pattern-B `topcd:` cross-declaration with justification only
where it genuinely crosses into care. Add its SHACL shape to `shapes.ttl`. This is
WG-directory work and does not need an RFC unless it touches Core.
