# TOP CR — Domain Boundaries

What this domain covers, where it stops, and what lives in **sibling domains** instead.
Recorded here so the scope decision is a first-class artifact, not a comment buried in a
module header.

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

## Where it stops (and why)

The domain **stops at the edge of eCTD** — the TFL/CSR/submission package a regulator
receives. It deliberately does **not** model what happens *after* the regulator acts.
Everything past submission is a different unit of analysis (the **product** or the
**market**, not the study) with different actors, obligations, and lifecycles — folding
it in would blur the study-trial semantics that are currently crisp.

## Sibling domains (out of scope — deliberately)

These compose *with* TOP Core and the shared CR spine the same way `hcls:` and `cr:`
compose; they are not additions to `cr:`.

| Sibling domain (proposed)      | Owns                                                              | Unit of analysis |
|--------------------------------|------------------------------------------------------------------|------------------|
| **`product-lifecycle`**        | Label / USPI, REMS, PSUR/PBRER, post-marketing commitments, safety signal management post-approval | the **product** |
| **`commercialization`**        | HTA / market-access dossiers, payer evidence, pricing & reimbursement | the **market** |

Both genuinely change the **unit of analysis** (to the product / the market) and both sit
*outside* USDM's scope — so a sibling domain is the right shape.

### Devices — stay in-model, aligned with USDM (decision reversed)

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
already uses everywhere:

| Layer | Divergence | How it's modeled (in-domain) |
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

1. **Substrate — genuinely one.** TOP Core + W3C PROV + open standards (NGSI-LD, CDISC, IDMP, GS1)
   are the shared "nervous system." Sibling domains are **not** Company-A silos — they federate
   through that shared provenance/identity fabric. "Already a single graph" is substrate-unity, not
   a monolithic module.
2. **Within `cr:` — devices are not a sibling.** The auto-injector is the *same study, same product,
   same signal* as the clinical event, so `cr:DeviceDeficiency` sits next to `cr:AdverseEvent` in one
   safety model. Bifurcate them and the DSMB can no longer see one subject-level safety picture — you
   have rebuilt Company A *inside* one domain.

A separate `devices:` domain with a hand-maintained `cr:` ↔ `devices:` crosswalk would be exactly the
"point-to-point, brittle, expensive" integration the narrative indicts. **Non-bifurcation is the
thesis, not a detail.**

## How the boundary is enforced in the model

- The study is referenced **by IRI** across closeout graphs (`cr:decidesStudy`,
  `cr:csrForStudy`, `cr:submissionForStudy`, `cr:locksStudy`) — never re-typed — so a
  downstream graph consumes the study without re-authoring it.
- `cr:eCTDSubmission` is a **manifest** (`cr:includesReport` / `cr:includesDataset` /
  `cr:includesDefine`), not a new source of truth — it references locked, already-produced
  content and stops there.
- The scope note is repeated in the `cr-core-closeout.ttl` and `cr-core-submission.ttl`
  module headers, so it travels with the ontology.
