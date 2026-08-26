# Clinical-research v1 launch envelope (folded from the seed)

**Status:** source prose only. Not ratified. Not an ADR.
**Folded:** 26 Aug 2026 from `claude/clinical-research-v1-seed` `hcls/clinical-research/v1/README.md` (PR 44, closed unmerged).
**Canonical line:** `claude/clinical-research`. Defective `hcls/` TTL and placeholder SSSOM were **not** folded.
**Numbering:** the seed said this would become ADR-0025. On this line ADR-0025 is already the OOUX object catalog. Do not reuse that number.

The campaign Definition of Done is a separate Phase B draft (desk findings, not this file). This page keeps the seed's launch-envelope words so they are not lost when the seed branch is retired.

---

## Definition of Done — clinical-research v1 (seed text)

> Resolves the seed's Open Question #5 ("what concrete demo readiness counts as *TOP ships clinical-research v1*") and the cycle-planning blocker "T.O.P. clinical research v1, defined in one paragraph." This is the launch envelope.

**In one paragraph.** Clinical-research v1 is *done* when the published directory is a SHACL-valid reference graph in which **all twelve functional areas are represented by at least one operator-grounded anchor class**, every class is **anchored to NCIt** (Tier-1 `skos:exactMatch`) and, where it crosses into care, **declares a Pattern-B `subClassOf` against a care stub with a one-line operator justification**; the **three worked examples** (Pharmacovigilance AE family, Intervention oncology overlap, Study-Design USDM alignment) are authored as real triples; **at least one full walkthrough TTL** runs end to end; the **site-SOP vocabulary ships as a separate aligned file** (Path b); the alignment machinery (NCIt subset whitelist, EVS mapsets as pinned SSSOM, Tier-4 FDA attachments) is **present and version-stamped**; and a **spec page** presents all of the above — such that the JPM Healthcare Week 2027 audience can read it as serious and practitioner-grounded.

### Done checklist (the launch envelope)

- [ ] **12 functional areas, ≥1 anchor class each** — Study Design, Regulatory Affairs, Finance, Setup, Site Management, Clinical Supply, Recruitment, Intervention, Pharmacovigilance, Data Management, Monitoring, Quality Management.
- [ ] **NCIt Tier-1 anchoring** — every class carries `skos:exactMatch ncit:*`, `skos:prefLabel`, and operator `skos:altLabel`s.
- [ ] **Pattern-B cross-workflow discipline** — every class that crosses into care declares `rdfs:subClassOf` a care stub with a one-line operator-grounded `rdfs:comment`. No cross-declaration that fails the operator test (e.g. Sponsor as a care Organization).
- [ ] **Three worked examples authored as triples** — PV AE family (AdverseEvent → SeriousAdverseEvent → SUSAR), Intervention oncology overlap (Study/Concomitant MedicationAdministration), Study Design (Protocol, ScheduleOfActivities, EligibilityCriterion).
- [ ] **≥1 full walkthrough TTL** end to end (candidate: Maria's Cycle 1 Day 1 visit).
- [ ] **Site-SOP vocabulary** shipped as a separate aligned file (Path b), with `skos:closeMatch` bridges and its own source provenance.
- [ ] **Alignment machinery present and pinned** — NCIt subset whitelist, EVS REST mapsets imported as SSSOM at pinned versions, Tier-4 FDA attachments (UNII, SPL, GUDID, ICSR).
- [ ] **Care Pattern-B stubs** exist with enough structure for SHACL to pass; honest about being stubs.
- [ ] **SHACL validation green** — one shapes file per functional area; four-layer enforcement (ADR-0010) on the whole directory.
- [ ] **Spec page** (summary, layering, functional areas, alignment summary, cross-workflow declarations, SHACL, deferred).

### Explicitly not required in the seed text

FHIR R5 alignment · RxNorm and LOINC (UMLS dependency) · Bioregistry registration · oncology Pattern-C escalation · full clinical-care extension · pharmacovigilance graduation to its own extension · the NGSI-LD JSON-LD `@context` (ADR-0014 deferred).

### Chair notes (not part of the seed)

- "Every class `skos:exactMatch` NCIt" is not an honest bar. SUSAR has no NCIt class of that name. Some peers are `closeMatch` only. Phase B will not ratify exactMatch-everywhere.
- Path names in the seed (`hcls/clinical-research/v1/`, `topcd:`, w3id prefix) are seed-line paths. On this line the live TBox is `cr-domain/`. Do not recreate the defective TTL to satisfy the old path.
- w3id namespace (PR 43/45) stays off this line until Bo unlocks cutover. Live IRIs remain `https://top.scientix.ai/`.
