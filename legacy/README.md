# Pre-Core legacy archive

> The artifacts in this directory predate **TOP Core** — the three-layer architecture (1 root, 8 categories, 28 leaves) that landed via ADRs 0012–0014 and shipped in `core/v1/` and `taxonomy/taxonomy.ttl`. They are preserved for historical reference and to keep the reasoning that produced them queryable.

**Do not load these against current Core.** The namespaces, shapes, and design assumptions conflict with the current architecture. They will not validate against `core/v1/shapes.ttl`. They should not be referenced from new specs.

## What's here

| Path | What it was | Why archived |
| --- | --- | --- |
| `reference-graphs/clinical-trials/` | The pre-Core clinical-research work — Sponsor / Study / Site / Participant / Recruit / Visit / OversightBody / InvestigationalProduct / Event lifts across PRs #1–#14. Includes spec HTMLs, planning MDs, the v0.7.0-strawman JSON intermediate, SHACL shapes, worked examples, verification histories. | Authored before Core landed; uses pre-Core namespaces (`topc:` mixed with `top:` for clinical-research) and pre-rename file paths. Bo's call: *"all the clinical work we did, it's trash with the new core — we have to refactor the entire reference graph."* The clinical-research workflow rebuilds from scratch against Core. |
| `onto/clinical/v1/`, `onto/commons/v1/` | The published mirrors at `top.scientix.ai/onto/...` from before the `/onto/` path was dropped (ADR-0014). | Superseded by `core/v1/`. |
| `clinical-research-owl-classes.ttl` | An early draft of clinical-research workflow OWL classes (formerly `clinical-research/source/owl-classes.ttl`). | Uses stale `topc:` prefix, references the old `commons/source/core.ttl` path that no longer exists. Predates the namespace collapse. |
| `tools/` | The JSON-intermediate translator scaffold — `build_context.py` and `build_shacl.py`. Consumed `top-strawman.json` and emitted JSON-LD `@context` + SHACL Turtle. | Tied to the pre-Core authoring pattern (JSON intermediate → emitted artifacts). The new pattern authors OWL/SHACL directly in `core/v1/shapes.ttl`. The translator may revive in some form if the clinical-research rebuild adopts a similar intermediate; that decision rides with the rebuild. |

## What's valuable here

The shape of these artifacts is wrong; the reasoning isn't. Specifically:

- **Operator-vocabulary work.** The spec HTMLs name entities, attributes, and enums in the language operators actually use. That naming is durable — the rebuild against Core preserves the names and re-roots them as workflow-extension subclasses of Core leaves.
- **Lifecycle insights.** Participant's 11-state lifecycle, Visit's template-vs-occurrence split, Site's operational hierarchy (`Site → StudySite → Study → Protocol → SOA`), Event's discriminator-not-class pattern — all surfaced from real operational scenarios and remain useful design references.
- **Cross-walks.** FHIR / SDTM / CDASH / USDM / OMOP mappings in each spec doc document what projection adapters will emit. The mappings themselves don't change because Core changed; they get reattached to the rebuilt classes.
- **Audit + dependency work.** `cdisc-dependency-pipeline.md`, `cdisc-ecosystem-alignment.md`, `usdm-ingest-audit.md`, `temporal-prov-native.md` — discipline that informs how the clinical-research workflow will handle upstream-standard churn.

## What's stale and should not be carried forward

- The OWL/SHACL artifacts (`shapes.ttl`, the JSON intermediate, the `@context.jsonld`) — wrong namespaces, wrong inheritance, wrong shape.
- The boolean flags on Sponsor (`isSponsorOfRecord`, `hasRegulatoryResponsibility`, …) — per ADR-0015 these reify to `top:Attestation` instances. The rebuild does not carry forward the flags.
- The OOUX-locked-9 framing — superseded by the 12-functional-area framing (Bo's reframe, 2026-05-11; not yet documented as an ADR but it's how the rebuild will be organized).
- The verification questions left open against Sponsor (8 closed; 0 open), Site/StudySite (14 pending), Study (12 pending) — moot under the rebuild. The conversations that produced them are still in the spec HTMLs for reference.

## Cross-references repaired

Cross-references from `index.html`, `README.md`, `roadmap.md`, `roadmap.html`, and `first-principles.md` that pointed at these artifacts have been updated to either point here under `legacy/`, drop the link entirely, or replace with a current-state reference. Anchor links inside the archived HTMLs still work within this directory.

## Provenance

Archived 2026-05-12 per ADR (the cleanup PR introducing this directory). The git history retains the original paths and the move commits; `git log --follow` against any archived file reaches back to its original lift commit.
