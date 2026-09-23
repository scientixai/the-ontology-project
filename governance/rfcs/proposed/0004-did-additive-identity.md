# RFC 0004: DID as additive identity for TOP Core (PROV-aligned; no mint)

- **Status:** Proposed (draft PR; no mint until Core stewards accept)
- **Date:** 2026-09-22
- **Authors:** Sophia Briet (Acting CKO, digital) <sophia@scientix.ai> (drafted at Bo Lora's direction)
- **Affected groups:** Core Stewards
- **Required quorum:** Core steward (convener)
- **Supersedes:** n/a
- **ADR on acceptance:** ADR-NNNN (filled when the RFC ratifies)
- **No mint** of TOP classes or properties in this RFC. Guidance + optional annotation posture only.

## Motivation

TOP Core already answers *what something means* in the shared commons (concepts, shapes, Universal DNA, PROV-native provenance posture — see `governance/planning/composition-projection-provenance.md`). Operators and autonomous or semi-autonomous actors additionally need a portable answer to *who or what controls an identity that may act, sign, amend, or publish* against those meanings — without inventing a second meaning layer or minting concept URIs from runtime ids.

W3C Decentralized Identifiers ([DIDs](https://www.w3.org/TR/did-1.1/)) supply that layer: a `did:` URI that resolves to a DID document carrying `controller`, verification methods, and verification relationships (`assertionMethod`, `authentication`, `keyAgreement`, …). The document is a **public key directory and control surface**, not a secret store and not a domain ontology.

A practical pattern: an organizational **mandate** (charter, role, or policy instrument) is often the **controller** of an actor identity that may act under that authority. Sketch:

```json
{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:example:agent:operator-a",
  "controller": "did:example:mandate:123"
}
```

The same pattern applies across trust domains: company overlay packs, pack amends, gated evidence packets, and cross-org handoffs need stable subject ids and rotatable keys under clear controller authority — while TOP URIs continue to name the *claim type* and PROV continues to name the *trail*.

## Non-goals

This RFC does **not**:

1. Replace TOP concept URIs with DIDs (anything can be a DID subject; that does not make a DID a shared-meaning URI).
2. Mint TOP classes, properties, or namespaces from DID documents or Jev runs.
3. Define a new DID method (`did:mandate` remains an illustrative sketch, not a method registration).
4. Make DID resolution a Core runtime requirement for reading TOP graphs.
5. Conflate cryptographic standing (key authorized under a DID) with correctness of reasoning or quality of Evidence (Agent-DID and related work already draw this line; we adopt it).
6. Treat Jev (or any extractor) as a system of record.

## Proposal

### 1. Three-layer posture (normative guidance)

| Layer | Answers | Primary URI family |
| --- | --- | --- |
| **TOP Core / WG vocab** | What does this mean? | `top:` / WG prefixes (HTTP URIs in the TOP commons) |
| **DID** | Who/what is the identity, who controls it, which keys may act? | `did:` |
| **PROV** | What happened, who was responsible, what was derived? | `prov:` (already native to TOP's provenance posture) |

Additive rule: a single artifact may carry all three. Example: a gated eligibility claim is typed by a TOP concept URI, attributed in PROV to a `prov:Agent` whose id is a DID, and signed with a key listed under that DID's `assertionMethod`.

**PROV-DM adjacency.** [PROV-DM](https://www.w3.org/TR/prov-dm/) is adjacent to DID in the sense that matters for Core: both are about *agency and control*, not about shared meaning. DID answers *who controls an identity and which keys may act*. PROV-DM answers *what happened under that agency* (Entity / Activity / Agent, attribution, association, delegation). They compose; neither substitutes for TOP concept URIs.

### 2. DID subjects and controllers as PROV agents (the join)

Adopt the compositional join already latent in the standards (no new ontology required for v0), with PROV-DM as the trail model and DID as the portable agent/controller identifier:

- A DID **subject** MAY be typed / used as a `prov:Agent` (person, organization, software agent).
- A DID **controller** MAY be a distinct `prov:Agent` that the subject `prov:actedOnBehalfOf` (or that is `prov:wasAssociatedWith` activities that mutate the subject's DID document).
- Activities (resolve, rotate key, amend pack, gate evidence) are `prov:Activity` nodes; outputs are `prov:Entity` nodes; responsibility uses `prov:wasAssociatedWith` / `prov:wasAttributedTo` / qualified forms with `prov:hadRole` when role matters.

Illustrative Turtle (informative):

```turtle
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix ex:   <https://example.org/> .

<did:example:agent:operator-a> a prov:Agent ;
    prov:actedOnBehalfOf <did:example:mandate:123> .

ex:amend-pack-a1 a prov:Activity ;
    prov:wasAssociatedWith <did:example:agent:operator-a> .

ex:pack-a1-v2 a prov:Entity ;
    prov:wasGeneratedBy ex:amend-pack-a1 ;
    prov:wasAttributedTo <did:example:agent:operator-a> .
```

### 3. Verification relationships → act classes (informative mapping)

| DID verification relationship | Typical TOP / evidence use |
| --- | --- |
| `assertionMethod` | Sign pack amends, gated Evidence packets, published overlays |
| `authentication` | Prove control of the identity at a boundary |
| `keyAgreement` | Confidential handoff / encryption to the subject |
| `capabilityInvocation` / `capabilityDelegation` | Future: capability tokens; out of scope for v0 beyond naming |

Keys appear as **pointers or embedded verification methods** in the DID document. Private material stays in the operator's secret store (SoR for secrets is outside TOP). Rotation updates the DID document under controller authority; the DID itself stays stable.

### 4. Controller / mandate pattern

RECOMMENDED pattern for autonomous or semi-autonomous actors:

1. Actor has a stable DID.
2. `controller` points at a mandate identity (organization DID, charter DID, or other mandate DID) — not at an unbound personal key alone when organizational standing matters.
3. PROV records delegation (`prov:actedOnBehalfOf`) so "under what authority" is queryable, not tribal knowledge.

Method choice is deferred: `did:web` / `did:webvh` are sufficient defaults to think with; ledger-native methods are optional deployment profiles, not Core doctrine.

### 5. What lands in the TOP repo if this RFC accepts

On acceptance, Core stewards add a short **interop guidance** page (path strawman: `core/v1/docs/did-additive-identity.md` or under `governance/planning/` if preferred) that:

- States the three-layer posture and non-goals above.
- Shows the PROV join examples.
- Links W3C DID Core, PROV-O, and this RFC.
- Explicitly says: no TOP mint from DID documents.

No change to `shapes.ttl` is required for v0 unless a later RFC proposes optional annotation properties (e.g., documenting a `top:controlledByDid` style tip). Prefer reuse of DID JSON-LD + PROV before minting.

## Alternatives considered

1. **Do nothing (HTTP agent URIs only).** Preserves simplicity. Rejected as the long-term answer for cross-org signing and key rotation; kept as the valid interim for single-trust-domain deployments that already have stable HTTPS agent URIs.
2. **Mint DID-shaped classes into Core now.** Rejected: premature; violates no-mint discipline; DID Core already defines the document graph.
3. **Replace TOP URIs with DIDs for concepts.** Rejected: collapses meaning into identity control; breaks the commons thesis.
4. **Require DID on every `prov:Agent`.** Rejected for v0: optional additive; tighten in deployment profiles / customer overlays when needed.

## Open questions (for Core stewards)

1. Guidance page under `core/v1/docs/` vs `governance/planning/` for the accepted artifact?
2. Should a follow-on RFC propose any optional Core annotation properties, or stay documentation-only indefinitely?
3. Is `did:webvh` the recommended default method in TOP prose, or method-agnostic with `did:web` examples only?
4. How concrete should the public mandate-controller worked example be (abstract sketch only vs richer illustrative DID documents)?

## Consequences

- **Easier:** Clear story for identity + meaning + trail; portable signer identity for amends and gated packets; key rotation without renaming TOP concepts.
- **Harder:** Authors must keep the three layers distinct; reviewers must reject DID-as-ontology creep.
- **Downstream:** Evidence infrastructure and company overlays MAY attach DIDs; TOP graphs remain readable without DID resolution.
- **Follow-on:** Optional method profile note; possible VC Data Integrity pairing RFC; operator-local DID issuance runbooks (out of TOP Core scope).
- **Forecloses:** Treating DID documents as a substitute for TOP WG vocabularies.

## Prior art (DID ∩ PROV)

There is **no single W3C Recommendation** titled "DID+PROV." The productive join is compositional:

| Source | Claim strength | One-line |
| --- | --- | --- |
| [DID Core 1.1](https://www.w3.org/TR/did-1.1/) | Normative (identity) | Subject, controller, verification methods/relationships |
| [PROV-O](https://www.w3.org/TR/prov-o/) | Normative (trail) | `Agent` / `Activity` / `Entity` + attribution/association/delegation |
| [PROV-DM](https://www.w3.org/TR/prov-dm/) | Normative | Agents bear responsibility; bundles for provenance-of-provenance |
| [Agent-DID RFC-001](https://github.com/edisonduran/agent-did/blob/main/docs/RFC-001-Agent-DID-Specification.md) | Community pattern | Agent DID + required `controller`; explicit split: identity standing ≠ decision provenance (signed receipts separate) |
| [GenesisGraph](https://github.com/Semantic-Infrastructure-Lab/genesisgraph) | Spec draft | Maps PROV Entity/Activity/Agent; "verifiable" tier = signatures tied to DIDs/VCs |
| STAC liability extension (`liability:prov` + VCs) | Domain practice | PROV-JSON alongside Verifiable Credentials (DID-bearing issuers typical in VC stack) |
| [PAV](https://pmc.ncbi.nlm.nih.gov/articles/PMC4177195/) | Related | Authoring/versioning specialization of PROV-O (roles); not DID-specific |

**Finding for reviewers:** prior art supports *using DIDs as agent identifiers inside PROV graphs* and *pairing VCs for signed claims*; it does not support collapsing TOP meaning into DID documents.

## References

- This conversation's layering: TOP meaning ‖ DID identity/control/keys ‖ PROV trail
- `governance/planning/composition-projection-provenance.md` (copy-free provenance posture)
- TOP RFC process: `governance/rfcs/README.md`
- Related open Core RFCs: 0002 (HCLS shared acts), 0003 (`top:partOf`) — orthogonal; no conflict expected

## Notes for reviewers

Load-bearing asks for Core stewards: (1) is guidance-only (no Core mint) the right acceptance bar for 0004? (2) keep PROV-DM named explicitly as the adjacent trail model beside DID (this draft's posture)? (3) method-agnostic prose with `did:web` examples, or a recommended default method in TOP guidance?
