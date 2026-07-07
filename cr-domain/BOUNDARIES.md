# TOP CR — Domain Boundaries

What this domain covers, where it stops, and what lives in **sibling domains** instead.
Recorded here so the scope decision is a first-class artifact, not a comment buried in a
module header.

## Read this first: reference graph vs. customer graph

There are **two graphs**, and every boundary in this document applies to only one of them.

- **The reference graph** — what we author here: TOP Core + `cr:` + the sibling domains. It is
  **modular by design, for authoring and governance**: who owns a module, how it versions, how it
  is reviewed and released. These module boundaries are the reference model's *package structure*,
  **not a runtime wall**. `build_dist.py` already proves it — it merges the `cr:` modules into one
  `top-cr-v1.ttl` on build; the modularity dissolves on load.
- **The customer graph** — what a customer builds by instantiating the reference model against
  their systems. It is **one cohesive, unified graph.** The auto-injector's clinical AE, device
  deficiency, CMC batch, and supply-chain lot are simply connected nodes; the engineer asking
  "show me device signals linked to tooling adjustments" neither knows nor cares which reference
  module each class came from. **This is Company B's "one graph."**

Consequence: **the sibling-domain distinction is a reference-authoring partition, not a boundary in
the customer's world.** Cross-domain "federation" is not a point-to-point integration between
siblings (that would be Company A) — in the customer graph there is nothing to integrate, it is
already one graph. So we do **not** need to be precious about sibling boundaries. They are a
convenience for how *we* author and govern, and they vanish the moment the customer graph is built.

The modeling already assumes this: entities are referenced **by IRI** across module lines (a
closeout graph names the study by IRI, never re-typing it), and `cr:eCTDSubmission` is a
**manifest** of references — both patterns let a customer graph stitch modules into one fabric with
no seam.

## The scope, in one line

**TOP-CR runs the trial from the front bracket (pre-IND) to the back bracket
(regulatory submission — eCTD Module 5).** The unit of analysis is the **study**.

```
pre-IND ──▶ start-up ──▶ conduct ──▶ closeout ──▶ regulatory submission (eCTD)
  A0            │            │           │                    │
             set-up      enrollment   database lock       CSR ─▶ eCTD  ◀── TERMINAL
             delegation  EDC / LIMS   analysis & EOP2                       (B1)
             (start-up)  DTA / safety  reporting (CSR)
                         RBQM / dev.   submission
```

The closeout arc that terminates the domain:

| Slice  | What it models                                             | Terminal invariant |
|--------|------------------------------------------------------------|--------------------|
| **A1** | Database lock (soft/hard), LPLV, post-lock control, follow-up | No clinical value after a HARD lock without a recorded `cr:DatabaseUnlock`. |
| **A2** | Analysis: `TableListingFigure`, the EOP2 **decision node**  | A TLF must be reproducible-to-source **and** pre-specified in the SAP; a gate decision must rest on evidence. |
| **A3** | Reporting: the ICH E3 Clinical Study Report                | A results section must trace to the TLF/result it concludes from. |
| **B1** | Submission: the eCTD manifest (**terminal node**)          | A submission must rest on a **HARD** `cr:DatabaseLock` (`cr:builtOnLock`). |

The B1 `cr:builtOnLock` edge is the seam that ties the terminal node back to A1 — the
whole trial converges on one frozen basis, and the filing must rest on it.

## Where this module's authoring stops (and why)

The `cr:` reference module is **authored** from pre-IND to the edge of eCTD — the TFL/CSR/submission
package a regulator receives. It does not *author* what happens after the regulator acts: that is a
different unit of analysis (the **product** or the **market**, not the study), with different owners
and review cadences, so it is a different reference module. This is an **authoring** boundary, not a
customer-graph wall — a customer graph continues straight past eCTD into label, REMS, and HTA as one
fabric (see "reference vs. customer graph" above). Keeping the study-trial semantics in their own
module is what keeps them crisp to author and govern.

## Sibling reference modules (authored elsewhere, unified in the customer graph)

These are **separate reference modules for authoring/governance reasons** — they compose *with* TOP
Core the same way `hcls:` and `cr:` do. They are not additions to `cr:`, and (per the frame above)
they are **not** walls in the customer graph.

| Sibling module (proposed)      | Owns                                                              | Unit of analysis |
|--------------------------------|------------------------------------------------------------------|------------------|
| **`product-lifecycle`**        | Label / USPI, REMS, PSUR/PBRER, post-marketing commitments, safety signal management post-approval | the **product** |
| **`commercialization`**        | HTA / market-access dossiers, payer evidence, pricing & reimbursement | the **market** |

Both change the **unit of analysis** (to the product / the market) and sit *outside* USDM's scope —
so authoring them as their own modules is the right partition. It carries no cost at customer-graph
time, where they merge with `cr:` into one graph.

### Devices — stay in-model, aligned with USDM (decision reversed)

**Why devices are decided at all, if everything unifies in the customer graph anyway.** For
`product-lifecycle` and `commercialization`, the sibling-vs-in-`cr:` choice barely matters — it is
an authoring convenience that vanishes at customer-graph time. Devices are the exception because
the argument is at the **reference/authoring layer**, and specifically about **USDM**: USDM models
`MedicalDevice` inside the one study model, and we crosswalk `cr:` → USDM. Authoring devices as a
sibling would make our reference structure **diverge from USDM's for no benefit and fracture the
crosswalk** — shooting ourselves in the foot. So this is a USDM-alignment decision, not an instance
of the general unification principle (which is satisfied automatically downstream).

**Devices are modeled as first-class nodes WITHIN `cr:`, not a separate domain.** An earlier
draft of this file recommended a `devices-clinical-research` sibling; that was wrong, and the
vendored USDM is the reason.

USDM v4.0 (`ontology/vendor/usdm/usdm-v4.ttl`) does **not** bifurcate devices — it keeps them
in the one study model:

- `usdm:MedicalDevice` is a first-class class (EU MDR 2017/745), with `hardwareVersion`,
  `softwareVersion`, `embeddedProductId`, `sourcing`, `identifiers`.
- `usdm:MedicalDeviceIdentifier` carries a type value set including **UDI**.
- `usdm:StudyVersion‑medicalDevices` — the top study container **owns** the devices directly.
- `usdm:StudyIntervention` is defined as *"Any agent, **device**, or procedure…"* — the
  intervention concept already spans devices; device-ness is a role/type, not a parallel class.
- `usdm:Administration‑medicalDeviceId` weaves device usage into the same dosing node.

Because we **crosswalk `cr:` → USDM**, a separate device domain would fracture that mapping: a
USDM `StudyVersion` carrying both a drug and a device intervention could not map to two disjoint
domains. **Combination products** (autoinjector, drug-eluting stent) are the clincher — they are
one study with both a drug and a device intervention, which is exactly why USDM keeps devices
in-model; a bifurcated domain makes them unrepresentable without cross-domain surgery.

The divergence that *is* real — IDE vs IND, 510(k)/PMA vs NDA/BLA, MDR technical file, device
deficiency/malfunction reporting — is **depth within the lifecycle, not breadth across a separate
spine.** It is handled as **leaf specializations on the shared spine**, the pattern the domain
already uses everywhere.

> **Status — decided design, not yet built (v1).** The device classes below are the *committed
> plan* for how device depth is added when it is added; they are **not present in the v1 ontology**.
> This table records the decision (in-model, per USDM), not shipped code. Tracked as a deferral in
> "Deferred within scope" below; when implemented, each row lands as an additive leaf, and the
> coherence gate (`tests/run_tests.py`) will hold it to a single non-duplicate definition.

| Layer | Divergence | How it will be modeled (in-domain, when built) |
|-------|------------|------------------------------|
| Product | device vs drug | `cr:MedicalDevice` (sibling of `cr:InvestigationalProduct`) + `cr:DeviceIdentifier` (UDI), crosswalked 1:1 to `usdm:MedicalDevice` |
| Regulatory front | IDE vs IND | generalize `cr:INDApplication` to admit an IDE pathway |
| Submission | 510(k) / PMA / De Novo vs NDA/BLA | extend the `cr:submissionType` enum; a `cr:eCTDSubmission` sibling only if the manifest shape genuinely differs |
| Safety | malfunction / device deficiency | `cr:DeviceDeficiency` alongside `cr:AdverseEvent` |

Rule of thumb: **if USDM models it in the one study model, so do we** — divergence rides on the
shared spine as subtypes, enum values, and graded shapes, never a fork.

### The narrative test (Two Worlds)

The Scientix "Two Worlds" narrative is the reference case for this whole boundary, and it turns
on a **combination product**: a subcutaneous auto-injector delivering a partial dose. That single
event is at once an adverse event (clinical), a plunger-performance observation (device), a
tooling/silicone root cause (CMC), a lot→batch trace (supply chain), and a DSMB/MDR interaction
(regulatory).

- **Company A** loses because those readings live in **separate systems joined after the fact** —
  22 days of email chains, ServiceNow tickets, and a 47-page PDF to rebuild the provenance. That
  cross-silo reconstruction *is* a domain boundary expressed as org chart.
- **Company B** wins because "the graph already contains the relationships": the device observation
  and the clinical AE are **nodes in one graph**, so the lot trace is one query, not three weeks.

The lesson has **two levels**, and the boundary honors both:

1. **The customer graph — genuinely one.** Company B's "already a single graph" is the *customer
   graph*, built on TOP Core + W3C PROV + open standards (NGSI-LD, CDISC, IDMP, GS1). It does not
   federate its reference modules at runtime — it merges them; there is nothing to integrate because
   it is one fabric. The reference modules (`cr:`, `product-lifecycle`, a future CMC module) are the
   *authoring* partition, invisible to the engineer querying the customer graph.
2. **Within the reference graph — devices are authored in `cr:`, not a sibling.** The auto-injector
   is the *same study, same product, same signal* as the clinical event **in USDM's own structure**,
   so `cr:DeviceDeficiency` is authored next to `cr:AdverseEvent`. Author them as separate reference
   modules and you diverge from USDM and hand-maintain a `cr:` ↔ `devices:` crosswalk — which is the
   "point-to-point, brittle, expensive" integration the narrative indicts, reintroduced at the
   *authoring* layer for no downstream benefit.

**Non-bifurcation is the thesis, not a detail** — at the customer-graph level always, and at the
reference-authoring level wherever a standard we crosswalk to (here, USDM) already keeps it whole.

## Deferred within scope (decided, not yet modeled)

The boundaries above say what lives in a **sibling** module (a different unit of analysis). This
section is different: it lists sub-domains that are **squarely in scope** — same unit of analysis,
the study — but **not yet modeled in v1**. They are recorded here as first-class **decisions**, so
an outside reader sees a deliberate deferral, not an oversight. Each is additive: it lands on the
shared spine the same way every shipped sub-domain did, gated green before it merges.

| Deferred sub-domain | What it covers | Why deferred / entry point when built |
|---------------------|----------------|----------------------------------------|
| **Randomization / IxRS·RTSM** | randomization events, kit/IMP assignment, stratification, emergency unblinding | design carries `cr:randomizationRatio` today; the *events* (assignment, dispensing) are the increment — a `cr:RandomizationEvent` on the enrollment/visit spine |
| **Drug supply & IMP accountability** | depot→site resupply, dispensing/return/destruction logs, DEA reconciliation, temperature excursions | a supply-chain leaf under the LIMS custody pattern (state machine + bitemporal custody already exist) |
| **Medical coding (MedDRA/WHODrug)** | the coding *workflow* — autocoder, medical-coding review, coding queries; WHODrug entirely | today `crosswalks/cr-to-meddra.ttl` maps AE→MedDRA by IRI (a term crosswalk, not a workflow); the increment is `cr:CodingActivity` + WHODrug crosswalk |
| **eCOA / ePRO, imaging, DHT as domains** | instrument definitions, ePRO item libraries, imaging read workflows (BICR), wearable signal | present today only as DTA *transfer profiles* (vendor data sources); first-class instrument/read models are the increment |
| **Query management depth** | SAE↔EDC reconciliation, cross-vendor reconciliation, query aging/escalation | EDC query/discrepancy + SDV exist; reconciliation across sources is the increment |
| **Decentralized trials (DCT)** | televisit, remote consent, home nursing, direct-to-patient supply | the visit/consent spine generalizes; DCT-specific modes are the increment |
| **Real-world evidence (RWD/RWE)** | external comparator, registry linkage, RWD source provenance | out of the interventional core today; a decision to model (or declare a sibling) is itself deferred |

These are **not** promises for v1; they are the map of where the reference goes next, kept honest and
visible. A consumer building their own graph today extends the model into any of these using the same
additive `top:flavor "Additive"` leaf pattern the shipped sub-domains use — the `dta-module` is the
worked precedent for a governed in-scope extension.

## How the boundary is enforced in the model

- The study is referenced **by IRI** across closeout graphs (`cr:decidesStudy`,
  `cr:csrForStudy`, `cr:submissionForStudy`, `cr:locksStudy`) — never re-typed — so a
  downstream graph consumes the study without re-authoring it.
- `cr:eCTDSubmission` is a **manifest** (`cr:includesReport` / `cr:includesDataset` /
  `cr:includesDefine`), not a new source of truth — it references locked, already-produced
  content and stops there.
- The scope note is repeated in the `cr-core-closeout.ttl` and `cr-core-submission.ttl`
  module headers, so it travels with the ontology.
