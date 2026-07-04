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
| **`devices-clinical-research`** | Device trials: IDE vs IND, 510(k)/PMA vs NDA/BLA, UDI, device-deficiency/malfunction safety model | the **device study** |

### Devices — the recommendation

**A separate `devices-clinical-research` domain, not additions to `cr:`.** Device trials
share the *spine* (sites, subjects, consent, AEs, submission) but diverge hard on the parts
that carry the regulatory weight: IDE vs IND, 510(k)/PMA vs NDA/BLA, MDR/technical-file
vaults, UDI, and a device-deficiency / malfunction safety model that is not the drug PV
model. A sibling domain that **reuses** TOP Core + the shared CR spine keeps both the drug
and device semantics clean, and mirrors the boundary already drawn for commercialization.

## How the boundary is enforced in the model

- The study is referenced **by IRI** across closeout graphs (`cr:decidesStudy`,
  `cr:csrForStudy`, `cr:submissionForStudy`, `cr:locksStudy`) — never re-typed — so a
  downstream graph consumes the study without re-authoring it.
- `cr:eCTDSubmission` is a **manifest** (`cr:includesReport` / `cr:includesDataset` /
  `cr:includesDefine`), not a new source of truth — it references locked, already-produced
  content and stops there.
- The scope note is repeated in the `cr-core-closeout.ttl` and `cr-core-submission.ttl`
  module headers, so it travels with the ontology.
