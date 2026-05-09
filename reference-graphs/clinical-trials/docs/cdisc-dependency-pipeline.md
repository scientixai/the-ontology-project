# CDISC dependency tracking + assessed-refactor pipeline (working draft)

> Working document. Captures the architectural pattern for keeping TOP aligned with evolving CDISC standards (USDM, COSMoS, Controlled Terminology, SDTMIG, NCIt, FHIR) without breaking GxP change-control. Output: a forward-looking design that sequences into v0.4–v0.6 milestones; not implementation now.
> Last touched 2026-05-09.

## Why this matters

TOP is a downstream consumer of CDISC and adjacent standards. Those standards evolve:

- **USDM** ships major releases (v3 → v4 with substantive shape changes; v5 is on the horizon).
- **COSMoS** ships quarterly r-numbered releases (`20251216_r15`, `20260331_r16`, `20260630_r17` visible in the repo).
- **CDISC Controlled Terminology** ships quarterly (codes added, decodes occasionally edited, codes deprecated).
- **SDTMIG** ships every several years; major releases reshape variable expectations.
- **NCIt** ships continuous updates (mostly additive new concepts).
- **FHIR R5 → R6** is multi-year cadence with substantive resource-shape evolution.

Without explicit dependency tracking:
- TOP cross-walks silently drift out of date
- Sponsor/regulator users find mismatches when they try to validate TOP outputs against current CDISC tooling
- The TOP ↔ CDISC story (which is half of TOP's value proposition) erodes

With *naive* auto-update (Dependabot-style):
- TOP breaks GxP change-control: every upstream code change becomes an unassessed change to a TOP-substrate artifact
- 21 CFR Part 11 audit trails would mark TOP as non-compliant for treating regulated reference data as a passively-tracked dependency
- Sponsors can't validate against TOP if TOP's reference codes silently shifted under them between yesterday and today

The right pattern is **automated detection + human-gated assessment + tracked refactor**.

## The dependency surface

What TOP actually depends on, by CDISC-ecosystem layer:

| Dependency | Cadence | Format | What changes track | Severity |
| --- | --- | --- | --- | --- |
| USDM model | Major: ~yearly. Minor: quarterly | Pydantic + JSON schema | New entities, deprecated fields, shape changes (e.g., StudyVersion structure), new Code categories | High — affects ingester directly |
| USDM example documents | Continuous | JSON | New patterns to validate against | Low — informational |
| COSMoS BC catalog | Quarterly (r-numbered) | LinkML YAML | New BCs, definition changes, deprecated BCs, NCIt code reassignments | Medium — affects Activity reach when lifted |
| COSMoS Dataset Specializations | Quarterly | LinkML YAML | New per-instrument specializations, SDTMIG-version-bound updates | Low (substrate); High (deployment export pipelines) |
| CDISC Controlled Terminology | Quarterly | XML / Excel / RDF / API | New codes added, codes deprecated, decodes occasionally renamed, hierarchy changes | High — affects every Code→enum mapping |
| SDTMIG | Major (multi-year) | PDF + structured XML | New domains, variable additions, expected-value changes, role reassignments | High — affects all SDTM cross-walks |
| CDASH IG | Major | PDF + structured | Acquisition-side variable evolution | Medium — affects CDASH cross-walks |
| FHIR R5 | Patch: rolling. Minor: ~yearly | FHIR JSON / XML | ResearchSubject / Patient / Consent shape evolution | Medium — affects FHIR cross-walks |
| FHIR R6 | When released | FHIR JSON / XML | Multi-year jump | High — when R6 lands, full cross-walk audit |
| NCIt | Continuous | OWL | New concepts (mostly additive); rare retirement | Low — additive |
| ICH E6(R3) / E8(R1) / E9(R1) / M11 | ICH cycle (multi-year) | PDF | Process-and-narrative changes; some structural language | Medium — affects spec-doc anchors |

TOP's pinned dependency set spans 11 distinct upstreams. Most are quarterly or slower cadence, but the surface is real.

## Proposed architecture

```
┌────────────────────────────────────────────────────────────────┐
│ TOP repository                                                 │
│                                                                │
│  reference-graphs/clinical-trials/                             │
│    cdisc-dependencies.yaml   ◀─── pinned versions manifest     │
│    cdisc-changelog/          ◀─── one-file-per-assessment      │
└────────────────────────────────────────────────────────────────┘
                          ▲
                          │ creates assessment PR
                          │
┌────────────────────────────────────────────────────────────────┐
│ GitHub Actions: cdisc-dependency-watcher (cron + webhook)      │
│                                                                │
│  for each dependency in cdisc-dependencies.yaml:               │
│    fetch upstream latest                                       │
│    compare to pinned version                                   │
│    if different:                                               │
│       generate diff (semantic, not just textual)               │
│       run impact-analyzer on diff                              │
│       generate assessment artifact (markdown)                  │
│       open PR with: bumped pin + assessment + suggested patch  │
│       request review (Bo / TOP maintainers)                    │
└────────────────────────────────────────────────────────────────┘
                          ▲
                          │ subscribes to / polls
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│ Upstream sources                                               │
│  - github.com/cdisc-org/usdm releases + main commits           │
│  - github.com/cdisc-org/COSMoS releases + main commits         │
│  - CDISC Library API (CT)                                      │
│  - github.com/HL7/fhir releases                                │
│  - NCIt EVS API                                                │
│  - ICH publication RSS / mailing list                          │
└────────────────────────────────────────────────────────────────┘
```

### Components

**1. Dependency manifest (`cdisc-dependencies.yaml`)**

A pinned-versions file. Single source of truth for what TOP currently aligns with. Example shape:

```yaml
dependencies:
  usdm:
    upstream: github.com/cdisc-org/usdm
    pinned_version: "v4.0.0"
    pinned_commit: "abc123..."
    pinned_at: "2026-05-09"
    consumed_by:
      - tools/ingest_usdm.py
      - reference-graphs/clinical-trials/source/top-strawman.json
    crosswalk_files:
      - reference-graphs/clinical-trials/docs/usdm-ingest-audit.md
  cosmos_bcs:
    upstream: github.com/cdisc-org/COSMoS
    pinned_release: "20260331_r16"
    pinned_at: "2026-04-15"
    consumed_by:
      - reference-graphs/clinical-trials/docs/cdisc-ecosystem-alignment.md
  cdisc_ct:
    upstream: cdisc.org/library/api
    pinned_release: "2025-09-26"
    consumed_by:
      - reference-graphs/clinical-trials/docs/code-enum-mappings.md  # future
  sdtmig:
    upstream: cdisc.org/standards/foundational/sdtmig
    pinned_version: "v3.4"
    consumed_by:
      - reference-graphs/clinical-trials/docs/participant-planning.md
      - reference-graphs/clinical-trials/docs/usdm-ingest-audit.md
  fhir:
    upstream: hl7.org/fhir/R5
    pinned_version: "5.0.0"
    consumed_by:
      - reference-graphs/clinical-trials/docs/participant-planning.md
```

The manifest is itself versioned in git, so changes to *what we track* are also auditable.

**2. Watcher (GitHub Actions)**

Cron-based (daily? weekly?) plus webhook-triggered for GitHub-hosted upstreams. Steps:

- Fetch upstream `main` (or latest release)
- Compare to pinned commit/version
- If different: trigger differ + impact-analyzer
- If unchanged: log heartbeat ("upstream stable as of {date}")

**3. Differ (per-dependency)**

Each dependency type needs its own differ because the artifacts are heterogeneous:

- **USDM differ**: compare Pydantic class definitions; identify added/removed/renamed fields, added/removed classes, type changes
- **COSMoS differ**: compare LinkML schemas + diff individual BC YAMLs; identify new BCs, modified BCs, deprecated BCs
- **CDISC CT differ**: compare CT exports; identify added codes, deprecated codes, decode renames, hierarchy changes
- **SDTMIG differ**: compare structured XML; identify variable additions, expected-value changes
- **FHIR differ**: compare resource StructureDefinitions; identify field additions, cardinality changes, type evolution
- **NCIt differ**: compare OWL; identify new concepts, deprecated concepts

Where the upstream is LinkML (COSMoS), `linkml diff` is built-in. Where the upstream is Pydantic (USDM), a JSON-Schema diff via auto-generated schemas is the cheapest path. Custom differs needed for CT and SDTMIG.

**4. Impact analyzer**

Given a diff, identify *what TOP artifacts are affected*:

- Cross-reference the diff against the manifest's `consumed_by` lists
- For each consuming file, identify which lines/fields are affected
- For Code-changes specifically: search TOP for the C-code; surface every TOP entity/attribute/enum-value that references it
- Output: structured impact report (Markdown + JSON)

**5. Assessment artifact**

The watcher opens a PR with:
- The bumped pin in `cdisc-dependencies.yaml`
- A new file in `cdisc-changelog/{dep}-{date}.md` capturing the assessment
- Suggested patches to consuming files (where deterministic)

The assessment file template:
```markdown
# {Dependency} update assessment: {old_version} → {new_version}

## Detected changes
- {change 1, classified as Cosmetic / Additive / Breaking / Semantic}
- {change 2, ...}

## TOP artifacts impacted
- {file:line — description of affected cross-walk / code reference / shape mismatch}

## Suggested refactor
- {auto-generated patch for deterministic fixes}
- {flagged-for-human items requiring SME judgment}

## Compliance posture
- Validation impact: {none / minor / major}
- Spec docs requiring update: {list}
- SHACL invariants requiring update: {list}

## Reviewer decision
- [ ] Apply suggested refactor as-is
- [ ] Apply with modifications
- [ ] Defer (document deferral reason)
- [ ] Reject (document reason)
```

The assessment IS the GxP change-control artifact. Reviewer signs off (PR approval), and the merged PR + the assessment file form the audit-trail record.

**6. Human gate (PR review)**

Bo or TOP maintainers review the assessment PR. Decision options:
- **Apply** — merge the suggested refactor
- **Apply with edits** — adjust the patch, then merge
- **Defer** — keep TOP pinned to old version, document why (e.g., "USDM v5 RC; wait for stable release")
- **Reject** — document why TOP is intentionally diverging from upstream

The merged assessment PR becomes immutable history. The deferred and rejected ones live in `cdisc-changelog/` too — this is part of the audit trail.

**7. Refactor execution**

For deterministic changes (renamed Code decode, additive enum value), the watcher's suggested patch IS the refactor. For non-deterministic changes (new entity that needs cross-walk discussion, breaking shape change), the assessment surfaces the work for human-driven follow-up PR(s).

## Change classification (assessment criteria)

The differ + impact analyzer classify each change into one of four categories:

| Category | Examples | Default action |
| --- | --- | --- |
| **Cosmetic** | Decode rename ("Phase II Trial" → "Phase 2 Trial"); whitespace; doc-string change | Fast-track auto-merge after smoke test |
| **Additive** | New CDISC CT code added; new USDM field with default; new optional FHIR field; new BC published | Review + extend cross-walks; merge after sign-off |
| **Breaking** | USDM field removed; CDISC CT code deprecated; SDTM domain restructured; FHIR field cardinality tightened | Migration plan required; deprecation-shim period; staged rollout |
| **Semantic** | Same Code, but its clinical interpretation changes (rare, but happens with some CDISC C-codes); ICH guideline reinterpretation | SME review required; assessment may take weeks; document carefully |

The classification is heuristic + sometimes-imperfect. Reviewers can reclassify during assessment.

## GxP / 21 CFR Part 11 implications

Why this matters more for TOP than for typical software dependency tracking:

1. **Reference data IS controlled documentation.** A code controlled-terminology file is a regulated artifact under GxP/21 CFR Part 11; updating it is a "change to controlled documents" subject to formal change control.
2. **Auto-update without assessment is non-compliant.** Dependabot-style behavior (silent merge of upstream changes) breaks change-control discipline. Sponsors deploying TOP-derived data products in regulated workflows would be unable to validate.
3. **The assessment PR IS the change-control record.** Auditors looking for "how did TOP handle the 2027-Q1 CT update?" find the assessment file in `cdisc-changelog/cdisc_ct-2027-01-15.md` with the impact analysis, the reviewer decision, and the resulting refactor PR. Closes the audit loop.
4. **Validation impact is mandatory.** Each assessment includes "Validation impact: none / minor / major". Major-impact updates trigger re-validation cycles (which deployments-side; but TOP substrate must surface the trigger).

This pattern is **more robust than typical software dependency management** because the assessment is mandatory, not optional. It's also closer to how regulated industries actually want to consume open dependencies — they don't want unbounded automation, they want assisted decision-making.

## LinkML adjacency

If TOP eventually adopts LinkML for source-intermediate ([CDISC ecosystem alignment note](cdisc-ecosystem-alignment.md), open question 1), the change-tracking pipeline gets dramatically easier:

- LinkML has built-in `linkml diff` and `linkml lint` for schema-comparison
- COSMoS upstream IS LinkML — direct schema-vs-schema diffing, not artifact-level
- Generated artifacts (JSON-LD context, JSON Schema, OWL, SHACL) regenerate cleanly when source changes
- Impact analysis becomes "what classes/slots changed in upstream LinkML?"

If TOP stays custom (`top-strawman.json` + `build_shacl.py`), schema-diffing requires hand-rolled tooling for each dependency. Doable, but more code to maintain.

This is one reason the LinkML question (PR #5 ecosystem-alignment open question 1) deserves deliberate evaluation — the dependency-tracking pipeline efficiency is one of the gain levers.

## Relationship to the in-flight ingester work

The USDM ingester (audit PR #4) operates on a *pinned USDM version*. The first-pass ingester targets USDM v4.0.0 specifically, with the conventions documented in the audit.

When USDM v5 lands:
- The watcher fires
- The differ identifies shape changes
- The impact analyzer flags `tools/ingest_usdm.py` as affected
- Assessment PR opens with a list of changed fields
- Bo (or TOP team) decides: bump ingester to v5, support both v4 and v5, or stay on v4 with a deprecation note

The ingester is **versioned alongside its USDM target**, not floating. This keeps the GxP discipline intact even as upstream evolves.

## Recommended sequencing

| Milestone | Deliverable | Notes |
| --- | --- | --- |
| **v0.4** | USDM ingester for v4.0.0 (per audit PR #4 decisions) | Operates on pinned version |
| **v0.5** | Dependency manifest + watcher prototype (one dep, USDM, as proof) | Manual differ acceptable; auto-watch is the goal |
| **v0.5** | LinkML evaluation per ecosystem alignment open question 1 | If yes, schema-diffing leverages LinkML tooling |
| **v0.6** | Full watcher pipeline (USDM + COSMoS + CT + SDTMIG + FHIR) | Cron-based; assessment-PR template lives in repo |
| **v0.7** | Impact analyzer matures (deterministic patches for the easy 80%) | Cosmetic + Additive auto-patched; Breaking + Semantic surface for human |
| **Long term** | Public dashboard showing pinned versions and recent assessments | Community visibility into TOP's CDISC-currency posture |

Each milestone is independently valuable; the manifest alone (v0.5) gives TOP a "what version of CDISC are we aligned with right now?" answer that the project doesn't have today.

## Open questions for Bo

1. **Pinning policy**: should TOP pin to the latest stable CDISC release as soon as it's stable (aggressive currency), or deliberately lag by one release (conservative, gives the ecosystem time to stabilize)?
2. **Assessment SLA**: how long do we have between "watcher detects change" and "assessment PR is decided"? A week? A month? Indefinite?
3. **Multi-dependency coordination**: USDM v5 + COSMoS r20 + CT 2027-Q1 sometimes land within weeks of each other. Do we batch the assessments (one mega-assessment per quarter), or process each as it arrives (more PRs, finer granularity)?
4. **Public vs internal change-tracker**: is `cdisc-changelog/` public-by-default (community-visible record of TOP's currency posture), or internal-by-default (only TOP maintainers see it)? Public is the operator-grade move; internal is the typical software-team move.
5. **Assessment author**: who has authority to approve an assessment PR? Bo solo, or the broader TOP community once that's mature?
6. **Defer-to-deployment escape hatch**: some CDISC changes might be *deliberately not* propagated to TOP substrate because they're deployment-specific (e.g., a per-sponsor CT extension). Do we model that as a "deferred to deployment" classification?

## What this note does NOT cover

- **Implementation specifics** (action YAML, differ algorithm details, patch-generation logic) — those come during v0.5 when the prototype is built.
- **Adjacent-non-CDISC dependencies** (OBO Foundry alignment, OMOP CDM versions, FHIR profile updates) — same architectural pattern applies; if/when TOP picks them up, they go in the manifest.
- **Reverse-direction publishing** (when TOP itself publishes versioned releases that downstreams consume) — that's a separate concern; TOP-as-publisher rather than TOP-as-consumer.

## Pointers

- [`cdisc-ecosystem-alignment.md`](cdisc-ecosystem-alignment.md) — what we depend on; this note is its forward-looking complement.
- [`usdm-ingest-audit.md`](usdm-ingest-audit.md) — the first concrete dependency that warrants the manifest.
- [LinkML diff documentation](https://linkml.io/linkml/) — relevant if LinkML adoption goes ahead.
- [21 CFR Part 11](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11) — the regulatory frame for "controlled documents" change discipline.
