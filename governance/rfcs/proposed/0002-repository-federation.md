# RFC 0002: Repository federation — three-tier hub-and-spoke, the standards node, and the neutral org

- **Status:** Proposed
- **Date:** 2026-07-10
- **Authors:** @bo-lora (convener)
- **Affected groups:** Core Stewards, HCLS umbrella WG (forming), Clinical Research WG
- **Required quorum:** Core stewards + one Clinical Research WG maintainer (convener as review pool of one today)
- **Supersedes:** n/a — **extends** [ADR-0023](../../decision-log.md#adr-0023-hub-and-spoke-domains-core-owns-the-contract-and-the-registry-each-domain-owns-its-repo)
- **ADR on acceptance:** ADR-0027 (ADR-0026 is the entity-view corpus)

## Motivation

[ADR-0023](../../decision-log.md#adr-0023-hub-and-spoke-domains-core-owns-the-contract-and-the-registry-each-domain-owns-its-repo) (Proposed) already decided the direction: TOP goes hub-and-spoke, each domain owns its repo, Core owns exactly three things — the upper ontology, the executable extension contract, and the domain registry. That ADR answered *domains*. It did not answer three questions that the next wave of work forces now:

> "Imagine if you had 20 different domains feeding into the top, all in a single repo. That would be chaotic and non-functional." — the convener, ADR-0023

1. **The bucket mid-layer.** `hcls-core` (Person, Observation, Condition, Specimen, Consent, …) is a shared base that clinical-research, clinical-care, and pharmacovigilance all specialize from. Today it is **embedded inside `cr-domain/ontology/hcls-core.ttl`**, next to a hand-rolled `top-core` stub and cr-core. ADR-0023's flat Core→domain model has no home for it. A shared healthcare base cannot live inside one of its own consumers.

2. **The standards / alignment layer.** The workshop that produced this RFC evaluated the two anchor standards for HCLS — HL7 FHIR (`fhir.ttl`, R4) and the Allotrope Foundation Ontology (`afo.ttl`). They are **license-encumbered third-party artifacts on their own refresh cadence**, and their owned crosswalks (the FHIR `w5`-axis binding, the AFO/BFO binding, the NCIt→MedDRA/ICD SSSOM mapsets) are **shared across HCLS workflows**. Commingling them with the Apache-2.0 authored spine mixes license regimes and release cadences in one tree. ADR-0023 does not mention crosswalks at all.

3. **The org container.** ADR-0023 still names the core repo `scientixai/the-ontology-project`. The manifesto's stance is *community-governed, sponsor at the edge*. A sponsor-owned monorepo — or even a sponsor-owned set of federated repos — contradicts that structurally. The moment we federate is the cheapest moment to also move to a neutral org.

The forcing function is concrete: the FHIR/AFO binding work is ready to start, clinical-care and pharmacovigilance are queued, and CR is at its V1 extraction milestone. All three want to land against a federation topology, not into the monorepo we are about to deprecate.

## Proposal

### 0. Rebase the namespace to a permanent, host-independent identifier (do this first)

The neutral org removes sponsor coupling from *governance*; it does nothing for the coupling baked into every term IRI. `https://top.scientix.ai/v1#Person` names the sponsor's domain in the identity of every class and property — permanently, in the data. This RFC closes that in the same move, because it is logically prior to every repo carve-out (the registry entries and each `.ttl`'s `@base` encode the namespace).

**Term IRIs rebase to `https://w3id.org/top/…`** — a permanent, hosting-independent identifier operated by the W3C Permanent Identifier Community Group (the OBO / W3C best practice). w3id is the *identity*; it redirects to whatever host serves the content:

| layer | before | after |
| --- | --- | --- |
| Core | `https://top.scientix.ai/v1#` | `https://w3id.org/top/v1#` |
| HCLS | `https://top.scientix.ai/hcls/v1#` | `https://w3id.org/top/hcls/v1#` |
| CR | `https://top.scientix.ai/cr/v1#` | `https://w3id.org/top/cr/v1#` |
| standards | (new) | `https://w3id.org/top/standards/v1#` |

The **host** is `the-ontology-project.org` (owned by the project; `top.scientix.ai` 301-redirects to it). w3id → host is a redirect the project controls and can retarget anytime **without changing a single IRI**. That is why the rebase is a true one-time event: after it, hosting, domain name, and sponsor can all change and the identifiers never move again.

**Timing is the whole point.** Per ADR-0023 the IRIs don't resolve yet and nothing external pins them — today's blast radius is purely internal (`@base` / prefix rewrite across the repos + this RFC + the registry). This is the last cheap moment; after Core ships as a consumable, it becomes a breaking migration.

**Cost:** one PR to the `perma-id/w3id.org` repository adding a `top/.htaccess` redirect rule (drafted at [`governance/migration/federation-v1/w3id-top.htaccess`](../../migration/federation-v1/w3id-top.htaccess)). *Prerequisite:* confirm `w3id.org/top` is unclaimed — if taken, fall back to `w3id.org/top-ontology`.

### 1. Generalize ADR-0023's two tiers into three

ADR-0023's hub-and-spoke is **recursive, not flat**. Core is the hub. A **bucket base** (hcls, later manufacturing, supply-chain, energy) is a *sub-hub*: it pins Core, and it re-publishes the same three Core-owned things **scoped to its bucket** — a bucket upper layer, a bucket-scoped extension contract, and a sub-registry of the workflows under it. A **workflow** (clinical-research, clinical-care, …) is a spoke that pins its bucket base.

```
core            (hub)        owns: upper ontology · extension contract · domain registry
  └─ hcls       (sub-hub)    pins core; owns: hcls base · bucket contract · workflow sub-registry
       ├─ clinical-research  (spoke) pins hcls + core
       ├─ clinical-care      (spoke) pins hcls + core
       └─ pharmacovigilance  (spoke) pins hcls + core
  standards     (node)       pins hcls + core; owns: shared alignments; quarantines third-party licenses
  site          (node)       pins nothing; assembles top.scientix.ai from published releases
```

The dependency graph stays a **DAG that never cycles**: `spoke → sub-hub → hub`; `standards → sub-hub → hub`; `site → (published artifacts of all)`. Nothing upstream ever imports anything downstream. This is ADR-0023's rule ("a Core release plus per-domain upgrade PRs against pinned versions"), applied at each tier.

**The IRIs rebase exactly once — now — then never again (§0).** After the w3id rebase, namespaces are `https://w3id.org/top/v1#`, `/hcls/…`, `/cr/…`; they resolve (via the w3id redirect to `the-ontology-project.org`) to *published release artifacts*, not repo paths — consistent with ADR-0023's deploy-time assembly and the fact that cr-core already references `top:` by namespace string with no import closure. Federation repackages the containers; the §0 rebase is the single, deliberate IRI change, taken at the last moment before anything external pins them.

### 2. Phase 1 — five repos in a new neutral org

Create the GitHub org **`the-ontology-project`** and these five repositories. Scientix remains the sponsor, named in each `NOTICE`, owning none of the governance surface.

| Repo | Tier | Contents (from today's monorepo) | Pins | Owner · cadence · license |
| --- | --- | --- | --- | --- |
| **`core`** | hub | `core/`, `taxonomy/`, `first-principles*.md`, `governance/`, root `README`/`LICENSE`, `tools/naming_check.py` | — | Core stewards · slow · Apache-2.0 |
| **`hcls`** | sub-hub | `cr-domain/ontology/hcls-core.ttl` (+ any `hcls:` shapes), the 4-segment/13-domain HCLS map, the four-tier NCIt strategy | core | HCLS umbrella WG · medium · Apache-2.0 |
| **`clinical-research`** | spoke | all of `cr-domain/` **minus** hcls-core and the top-core stub | hcls, core | Clinical Research WG · fast · Apache-2.0 |
| **`standards`** | node | the FHIR `w5`-axis binding, the AFO/BFO binding, NCIt SSSOM mapsets, pinned-source **manifests** (not blobs) | hcls, core | HCLS umbrella WG · quarterly (upstream cadence) · **mixed / BYOL — quarantined** |
| **`site`** | node | `index.html`, `manifesto.html`, `roadmap.html`, `first-principles*.html`, `styles.css`, `images/`, `CNAME` | published releases | Convener · independent · content licenses |

**Two allocation rules the table encodes:**

- **hcls extracts *before* clinical-research can pin it.** The migration lifts `hcls-core.ttl` out of `cr-domain/ontology/` into `hcls`, deletes the hand-rolled top-core stub (clinical-research pins the real published Core instead), and leaves cr-core in `clinical-research`. cr-core's `hcls:`/`top:` references resolve by namespace string today, so nothing breaks mechanically at extraction; the executable contract *adds* the version pins that ADR-0023 requires.
- **Shared-or-encumbered → `standards`; workflow-owned-and-clean → the workflow repo.** The narrow, CR-owned crosswalks (`cr→SDTM`, `cr→FHIR-ResearchStudy`, `cr→external`) stay in `clinical-research`. The shared HCLS alignments and anything vendoring third-party licensed content go to `standards`. `standards` starts mostly greenfield — seeded with the `w5`-axis and AFO work — precisely because those are the artifacts this workshop was about to author.

### 3. Core owns the domain registry (ADR-0023's third thing), now tiered

`core` gains `registry/domains.ttl` — the machine-readable registry ADR-0023 specified (name, owning org/WG, repo URL, namespace, pinned Core version, contract-conformance status). Bucket sub-hubs carry a workflow sub-registry (`hcls/registry/workflows.ttl`). The public site is assembled at deploy time from Core plus registered entries. A seed registry ships with this RFC's migration bundle (`governance/migration/federation-v1/domain-registry.seed.ttl`).

### 4. Migration is history-preserving and non-destructive to origin

The migration bundle (`governance/migration/federation-v1/`) carves the new repos out of a **mirror clone**, never mutating `origin` until the convener pushes. It uses `git filter-repo` for path-level extraction (hcls is a single file inside cr-domain, so directory subtree-split will not carve it) and preserves full commit history and the ADR trail. See `federate.sh` and its `README.md`. Sequencing follows ADR-0023: finish CR V1 → publish Core as a versioned consumable → extract per this bundle → register → wire deploy-time assembly.

## Alternatives considered

- **Stay monorepo (ADR-0017's answer, do nothing).** *Changes:* nothing. *Preserves:* atomic cross-cutting commits, one review surface. *Not chosen:* ADR-0023 already invoked ADR-0017's own reassessment trigger; cr-domain (53 commits, its own LICENSE/NOTICE/CHANGELOG/harness) is a complete project embedded in another, and "ownership as write-access to someone else's repo" will never be accepted by an external consortium. This RFC does not relitigate that — it operationalizes the decision already taken.

- **Flat federation (ADR-0023 literally — Core→domain, no bucket tier).** *Changes:* extract each domain, but leave hcls somewhere ambiguous. *Preserves:* a simpler two-level mental model. *Not chosen:* there is nowhere clean to put a shared healthcare base. Left in `clinical-research`, every other HCLS workflow would pin a *clinical-research* release to get `hcls:Person` — a cycle-in-waiting where care-delivery depends on a trials repo. The bucket sub-hub is the minimal fix.

- **Crosswalks/standards inside each workflow repo.** *Changes:* no `standards` node; each workflow vendors its own FHIR/AFO pins. *Preserves:* fewer repos. *Not chosen:* the HCLS alignments are shared across workflows (the strategy doc says so), and they mix license regimes (HL7, Allotrope, BYOL MedDRA/SNOMED) that must not commingle with Apache-2.0 authored spine. N workflows would each re-vendor and re-pin the same third-party artifacts — the N×N maintenance failure the four-tier NCIt strategy exists to avoid.

- **git submodules.** Rejected here as in ADR-0017 and ADR-0023 — the registry gives discoverability without the coupling.

- **Keep everything under `scientixai/`.** *Changes:* federate but don't move org. *Preserves:* zero org-migration cost. *Not chosen:* structurally ties project governance to the sponsor company, against the manifesto. Namespaces (top.scientix.ai) don't move either way, so the org migration stays cheap and is best done once, now.

## Open questions

1. **Governance repo timing.** This RFC keeps `governance/` inside `core` (the constitution lives with the hub, where structural RFCs already concentrate). Promote it to its own `governance` repo only when cross-repo RFCs become routine — proposed trigger: the moment clinical-care ships and the first genuinely cross-workflow RFC lands. Reviewer guidance wanted on the trigger.
2. **`tools` repo timing.** The shared validators (`naming_check.py`, the future `lint_extension.py` executable-contract linter) live in `core` for now and are copied into spokes' CI. Promote to a `tools` dev-dependency repo when a second spoke needs them un-forked. Proposed trigger: clinical-care CI stand-up.
3. **Vendored third-party blobs.** This RFC commits `standards` to pinned *manifests* + owned mappings, with large licensed source files (FHIR 4.7 MB, AFO 1 MB) fetched at build time rather than committed. Reviewer confirmation wanted that this satisfies the "never import" doctrine while still enabling `w5`-axis derivation.
4. **`manufacturing` bucket.** CMC & Supply Chain (the AFO home) is the second bucket sub-hub. Out of scope for Phase 1, but the tier structure is designed to accept it without rework — confirm the recursion holds before we depend on it.

## Consequences

- **What gets easier.** Democratized ownership becomes real (a consortium owns `hcls` or a workflow from day one by conforming + registering). Per-repo cadence, permissions, and CODEOWNERS. License quarantine is structural, not a policy note. Downstream consumers pull just the tier they need.
- **What gets harder.** Cross-tier changes lose atomicity — a Core rename is a Core release plus per-tier upgrade PRs against pinned versions (ADR-0023's deliberate price). Three-tier pinning is more machinery than two-tier.
- **What downstream consumers must adapt to.** The one-time IRI rebase to `w3id.org/top` (§0) — but nothing has pinned the old `top.scientix.ai` IRIs yet (they don't resolve today), so the blast radius is internal. After the rebase, IRIs never move again regardless of host, domain, or sponsor changes. Consumers that cloned the monorepo repoint at `core` (+ whichever tiers they use). Release artifacts and checksums become the integration surface.
- **Follow-on work.** Publish Core as a versioned, checksummed consumable and resolve the known Core↔CR seam conflicts (ADR-0023 already lists this as blocking); build the executable-contract CI template once and adopt per repo; stand up deploy-time site assembly; author the `w5`-axis and AFO bindings into `standards`.
- **What this forecloses.** Atomic monorepo commits across tiers (deliberately). Re-homing hcls back inside a workflow (the extraction is one-way once workflows pin the `hcls` release). The namespace host (`top.scientix.ai`) as an *identity* — after §0 it is only ever a redirect target, freely retargetable.

## References

- ADRs: [ADR-0017](../../decision-log.md#adr-0017-monorepo-with-directory-scoped-ownership) (monorepo, superseded for topology by ADR-0023), [ADR-0023](../../decision-log.md#adr-0023-hub-and-spoke-domains-core-owns-the-contract-and-the-registry-each-domain-owns-its-repo) (hub-and-spoke — this RFC extends it), [ADR-0004](../../decision-log.md) (domains as composable extensions), [ADR-0019](../../decision-log.md#adr-0019-open-core-constrained-extension-three-flavors-per-core-property) (open Core / constrained extension — the executable contract).
- Governance: [`extension-contract.md`](../../extension-contract.md), [`working-groups.md`](../../working-groups.md), [`branch-protection.md`](../../branch-protection.md).
- Migration bundle: [`governance/migration/federation-v1/`](../../migration/federation-v1/).
- Prior art: OBO Foundry (hub + conformance contract + registry; independently owned spoke repos).
- Standards evaluated in the originating workshop: HL7 FHIR RDF (`fhir.ttl`, R4, the `w5` upper ontology), Allotrope Foundation Ontology (`afo.ttl`, BFO-grounded).

## Notes for reviewers

Bo: the two parts I most want your read on are **§Proposal.1 (the recursive third tier)** — whether hcls-as-sub-hub is the right generalization of ADR-0023 or one tier too many for today — and **Open Question 3 (vendored blobs vs. pinned manifests)**, since it governs how the FHIR/AFO binding work physically lands in `standards`.

---

*Extends ADR-0023. On acceptance, moves to `accepted/0002-repository-federation.md` and appends ADR-0027 to the decision log.*
