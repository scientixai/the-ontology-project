# RFC 0004: DID as additive identity for TOP Core (PROV-aligned; no mint)

- **Status:** Proposed
- **Date:** 2026-09-22
- **Authors:** @bo-lora (convener); drafted with Sophia Briet (Acting CKO, digital) at the convener's direction
- **Affected groups:** Core Stewards
- **Required quorum:** Core steward (convener)
- **Supersedes:** n/a
- **ADR on acceptance:** ADR-NNNN (filled when the RFC ratifies)
- **No mint** of TOP classes or properties in this RFC. Guidance + walkthrough only.

## Motivation

TOP Core already answers *what something means* in the shared commons (concepts, shapes, Universal DNA, PROV-native provenance posture — see [`governance/planning/composition-projection-provenance.md`](../../planning/composition-projection-provenance.md)). Operators still need a portable answer to *which agent identity signed, authorized, or published* when that answer must survive an organizational boundary.

The forcing case is already in-repo. The composition–projection–provenance note names Tier-1 integrity across a lab or sponsor boundary: a consent `top:Attestation` (or other Evidence) carries `top:signedBy` to the signing `top:Agent` and may carry `top:integrityHash`. No-copy projection keeps that cryptographic anchor meaningful end to end; ETL that rewrites identifiers breaks it. 21 CFR Part 11 (and related GxP audit-trail discipline) requires that *who* attested be answerable from the data. Today `top:signedBy` ranges over `top:Agent`, and every agent already carries exactly one `top:identifier` (`xsd:anyURI`). When the signer is outside the publisher's HTTPS namespace — a CRO investigator, a partner QA lead, a contracted medical monitor — a portable, rotatable agent URI is the operator cost this RFC addresses.

ADR-0013 (practitioner-first) sends autonomous-actor convenience to the edge. This RFC does **not** motivate Core guidance from an AI agent's preference for a DID. Autonomous or semi-autonomous actors MAY reuse the same additive pattern; they are not the primary customer of this decision.

W3C Decentralized Identifiers ([DIDs](https://www.w3.org/TR/did-1.1/)) supply a portable `did:` URI that resolves to a DID document carrying `controller`, verification methods, and verification relationships (`assertionMethod`, `authentication`, `keyAgreement`, …). The document is a **public key directory and control surface**, not a secret store and not a domain ontology.

## Non-goals

This RFC does **not**:

1. Replace TOP concept URIs with DIDs (anything can be a DID subject; that does not make a DID a shared-meaning URI).
2. Mint TOP classes, properties, or namespaces from DID documents or from any extractor's output.
3. Define a new DID method (`did:mandate` remains an illustrative sketch, not a method registration).
4. Make DID resolution a Core runtime requirement for reading TOP graphs.
5. Conflate cryptographic standing (key authorized under a DID) with correctness of reasoning or quality of Evidence.
6. Treat any extractor as a system of record.
7. Claim that a DID alone makes a TOP graph cryptographically verifiable end to end. Core today has `top:integrityHash` and `top:signedBy` but no proof / Data Integrity slot; verifiable signed claims in-graph wait on a follow-on.

## Proposal

### 1. Three-layer posture (normative guidance)

| Layer | Answers | Primary URI family |
| --- | --- | --- |
| **TOP Core / WG vocab** | What does this mean? | `top:` / WG prefixes (HTTP URIs in the TOP commons) |
| **DID** | Who/what is the identity, who controls it, which keys may act? | `did:` |
| **PROV-O (binding) / PROV-DM (conceptual)** | What happened, who was responsible, what was derived? | `prov:` as already aligned in Core |

Additive rule: a single artifact may carry all three. Example: an eligibility attestation is typed by a TOP concept URI, linked with `top:signedBy` to a `top:Agent` whose `top:identifier` is a DID, and recorded in the PROV trail via the Core⊑PROV class and property alignments already in `core/v1/shapes.ttl`.

**PROV binding.** Per ADR-0013 and the Core shapes, **PROV-O is the binding vocabulary** for trail alignment (`rdfs:subClassOf` / `rdfs:subPropertyOf` into `prov:*`). [PROV-DM](https://www.w3.org/TR/prov-dm/) is cited only as the conceptual model (Entity / Activity / Agent; attribution, association, delegation). DID answers *who controls an identity and which keys may act*; PROV answers *what happened under that agency*. Neither substitutes for TOP concept URIs.

### 2. Engage Core terms already in `shapes.ttl` (not bare PROV)

This RFC sits on the compositional join **already shipped** in [`core/v1/shapes.ttl`](../../../core/v1/shapes.ttl). Guidance MUST be written against these Core terms; bare `prov:*` appears only as the alignment target Core already declares.

| Core term | Alignment already in shapes | Role in this RFC |
| --- | --- | --- |
| `top:Agent` | `⊑ prov:Agent` | Accountable actor that may sign, authorize, or be attributed |
| `top:Person` / `top:Organization` / `top:Group` | `⊑ top:Agent` (+ PROV peers where declared) | Ordinary operator and org identities |
| `top:AutonomousAgent` | `⊑ top:Agent`, `⊑ prov:SoftwareAgent` | Software with delegated authority — edge-primary per ADR-0013; same DID pattern allowed, not the forcing case |
| `top:identifier` | Functional `xsd:anyURI` on Universal DNA | **Where the DID attaches** (see §5) |
| `top:memberOf` | `⊑ prov:actedOnBehalfOf` | Org / group hierarchy; delegation path in Core terms |
| `top:authorizedBy` | Agent → Agent | Who granted permission to act in a scope |
| `top:signedBy` | `⊑ prov:wasAttributedTo`; Evidence → Agent | Part 11–shaped attestation link — primary operator join |
| `top:hasCredential` | Agent → `top:Credential` | Qualification / identity proof already modeled as Evidence |
| `top:integrityHash` | on Evidence | Fingerprint; with `top:signedBy` forces Versioned immutability shapes |

Illustrative Turtle (informative; Core terms first):

```turtle
@prefix top:  <https://top.scientix.ai/v1#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix ex:   <https://example.org/> .

ex:investigator-a a top:Person ;
    top:identifier "did:web:research.example:investigators:a"^^xsd:anyURI ;
    top:memberOf ex:cro-org .

ex:cro-org a top:Organization ;
    top:identifier "did:web:cro.example"^^xsd:anyURI .

ex:consent-v1 a top:Attestation ;
    top:signedBy ex:investigator-a ;
    top:integrityHash "sha256-…" .
```

`top:Person ⊑ top:Agent ⊑ prov:Agent` and `top:signedBy ⊑ prov:wasAttributedTo` supply the PROV view without authors writing bare PROV as if Core were empty.

### 3. Verification relationships → act classes (informative mapping)

| DID verification relationship | Typical TOP use |
| --- | --- |
| `assertionMethod` | Keys that may produce material attested via `top:signedBy` / published Evidence |
| `authentication` | Prove control of the agent identity at a boundary |
| `keyAgreement` | Confidential handoff / encryption to the subject |
| `capabilityInvocation` / `capabilityDelegation` | Future capability tokens; out of scope for v0 beyond naming |

Keys appear as pointers or embedded verification methods in the DID document. Private material stays in the operator's secret store (out of TOP). Rotation updates the DID document under controller authority; the DID URI used as `top:identifier` stays stable.

### 4. Controller / mandate pattern (DID document side)

RECOMMENDED pattern when organizational standing matters:

1. Actor `top:Agent` has a stable DID as `top:identifier` (per §5).
2. In the DID document, `controller` points at a mandate identity (organization DID, charter DID, or other mandate DID) — not at an unbound personal key alone.
3. **Controller mapping:** DID document `controller` maps to `top:memberOf` when the mandate is the organization the agent belongs to, and to `top:authorizedBy` when the mandate is a scoped grant from another agent.
4. In the TOP graph, org relationship and permission use Core properties (`top:memberOf`, `top:authorizedBy`); PROV delegation is inherited via existing subProperty alignments.

### 5. Load-bearing design: DID **is** the agent's `top:identifier` (no mint)

`top:identifier` is an `owl:FunctionalProperty` with range `xsd:anyURI`. A `did:` URI is already a legal value **with zero mint**.

**Decision (this RFC):** When an adopter uses a DID for an agent, that DID **is** the agent's `top:identifier`. This RFC does **not** mint a second Core property (e.g. `top:did`).

**Consequence of functionality:** an entity has exactly one `top:identifier`. **An agent's `top:identifier` is never rewritten.** The RDF subject IRI and `top:identifier` literal already coexist separately (an agent may have an HTTPS subject IRI and a DID as `top:identifier`), so coexistence requires no identifier migration. Options for adopters:

1. **New agents:** Use a DID as `top:identifier` when minting agents after adoption (recommended when Part 11 cross-org signing is the driver).
2. **Existing agents:** Keep the existing HTTPS (or other) `top:identifier` and leave DID correlation to edge/overlay indexes or non-Core aliases until a future mint RFC proposes an optional second property.

v0 guidance and the walkthrough demonstrate option 1 for greenfield and cross-org signer agents. Option 2 is acknowledged, not solved by minting here.

### 6. What lands in the TOP repo if this RFC accepts

On acceptance, Core stewards land:

1. This RFC under `governance/rfcs/accepted/` (the durable record per [`governance/rfcs/README.md`](../README.md)).
2. Walkthrough **`core/v1/walkthroughs/agent-did.ttl`** that validates with `pyshacl` against `core/v1/shapes.ttl` (draft ships with this PR). There is no `core/v1/docs/` tree; do not add a separate guidance page for v0.

No change to `shapes.ttl` in v0. Prefer DID documents + existing Core/PROV join before any mint.

**Method posture:** method-agnostic prose with **`did:web` examples only**. Do not recommend `did:webvh` (or other methods) in TOP prose in this RFC.

## Alternatives considered

1. **Do nothing (HTTPS agent URIs only).** Preserves simplicity. Rejected as the long-term answer for cross-org Part 11 signing and key rotation; kept as valid for single-trust-domain deployments that already have stable HTTPS agent URIs as `top:identifier`.
2. **Mint a second property for DIDs.** Would allow HTTPS `top:identifier` and DID to coexist in Core. Rejected for v0: premature mint; functional `top:identifier` already accepts `did:` URIs; revisit only with a concrete multi-identifier operator requirement.
3. **Replace TOP concept URIs with DIDs.** Rejected: collapses meaning into identity control.
4. **Require a DID on every `top:Agent`.** Rejected for v0: optional additive.
5. **Motivate from autonomous-agent portability.** Rejected as primary motivation per ADR-0013; edge may still reuse the pattern.

## Open questions (for Core stewards)

1. After acceptance, any follow-on mint of an optional second identifier property for dual HTTPS+DID agents, or keep edge aliases indefinitely?
2. How concrete should public DID-document examples be beyond the walkthrough (abstract sketch vs richer controller documents)?
3. Should a later RFC add a Data Integrity / proof slot so `top:signedBy` + DID keys become verifiable in-graph?

## Consequences

- **Easier:** Portable signer identity for cross-org `top:signedBy` without renaming TOP concepts; key rotation without minting Core terms; clear three-layer story (TOP meaning ‖ DID control ‖ PROV trail via Core alignments).
- **Harder:** Authors must keep the layers distinct; reviewers must reject DID-as-ontology creep; functional `top:identifier` forces an explicit migrate-or-edge-alias choice when an HTTPS id already exists.
- **Scope honesty:** This RFC gives the signer a portable **identifier**. It does not by itself make signed claims in a TOP graph cryptographically verifiable; that waits on a proof / Data Integrity follow-on. `top:integrityHash` + Versioned immutability remain the in-Core integrity tools today.
- **Downstream:** Evidence tooling and overlays MAY use DIDs as `top:identifier`; TOP graphs remain readable without DID resolution.
- **Follow-on:** Optional method profile note; possible VC Data Integrity pairing RFC; operator-local DID issuance runbooks (out of TOP Core scope).
- **Forecloses:** Treating DID documents as a substitute for TOP WG vocabularies; minting DID-shaped Core terms in this RFC.

## Prior art (DID ∩ PROV)

There is **no single W3C Recommendation** titled "DID+PROV." The productive join is compositional:

| Source | Claim strength | One-line |
| --- | --- | --- |
| [DID Core 1.1](https://www.w3.org/TR/did-1.1/) | Normative (identity) | Subject, controller, verification methods/relationships |
| [PROV-O](https://www.w3.org/TR/prov-o/) | Normative (binding trail vocab) | Agent / Activity / Entity + attribution/association/delegation |
| [PROV-DM](https://www.w3.org/TR/prov-dm/) | Conceptual model | Agents bear responsibility; bundles for provenance-of-provenance |

**Finding for reviewers:** standards support *using DIDs as agent identifiers inside PROV-aligned graphs* and *pairing VCs for signed claims*; they do not support collapsing TOP meaning into DID documents. Non-normative community drafts are omitted here until they have stable, citable URLs and access dates.

## References

- [`core/v1/shapes.ttl`](../../../core/v1/shapes.ttl) — Core⊑PROV join this RFC engages
- [`core/v1/walkthroughs/agent-did.ttl`](../../../core/v1/walkthroughs/agent-did.ttl) — acceptance artifact (draft)
- [`governance/planning/composition-projection-provenance.md`](../../planning/composition-projection-provenance.md) — Tier-1 `top:signedBy` / no-copy boundary cost
- [ADR-0013](../../decision-log.md#adr-0013-practitioner-first-tops-primary-customer) — practitioner-first; autonomous convenience to the edge
- TOP RFC process: [`governance/rfcs/README.md`](../README.md)
- Related open Core RFCs: 0002 (HCLS shared acts), 0003 (`top:partOf`) — orthogonal; no conflict expected

## Notes for reviewers

Load-bearing asks answered in this draft per review:

1. **Guidance bar:** yes — accepted RFC is the durable record; land `core/v1/walkthroughs/agent-did.ttl` that passes `pyshacl` against `shapes.ttl` (no `core/v1/docs/` page).
2. **PROV:** PROV-O binding; PROV-DM conceptual only.
3. **Method:** method-agnostic with `did:web` examples; do not recommend `did:webvh` in TOP prose yet.
4. **Attachment:** DID **is** `top:identifier` (no second-property mint; never rewritten); new agents use DIDs, existing agents keep their identifier and use edge aliases.
