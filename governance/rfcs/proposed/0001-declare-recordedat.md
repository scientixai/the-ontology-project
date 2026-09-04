# RFC 0001: Declare `top:recordedAt` in Core (reconcile the shipped artifact with ADR-0021's erratum)

- **Status:** Proposed
- **Date:** 2026-09-04
- **Authors:** @bo-lora (convener); drafted with Claude Code at the convener's direction
- **Affected groups:** Core Stewards
- **Required quorum:** Core steward (the convener is the review pool of one today)
- **Supersedes:** n/a
- **ADR on acceptance:** to be assigned by the convener (a ratification note under ADR-0021, or a short ADR citing this RFC)

## Motivation

ADR-0021 and its erratum of 2026-09-01 (Issue #52; commits `c8af769` and `b3c9394`) define two clocks on Core: `top:observedAt` is valid time (when a fact was observed to hold in the world) and `top:recordedAt` is transaction time (when the system first knew it). The erratum states that `top:recordedAt` "was promoted to Core from the CR domain (2026-07)" and that "with two distinct temporal properties now at Core, they cannot share one semantic role."

The shipped Core artifact does not agree with the recorded decision. `core/v1/shapes.ttl` references `top:recordedAt` twice in comments (on `top:observedAt` and on `top:validFrom`) and never declares it. The consent walkthrough (`core/v1/walkthroughs/consent-bitemporal.ttl`) says the explicit record clock "arrives with the modular Core." The comment block that introduces the bitemporal section still assigns transaction time to `top:observedAt`, which the erratum corrected. So a consumer reading the artifact finds the semantics decided, the property named, and nothing to attach a value to.

The forcing case is a downstream consumer that needs both clocks on every object from its first day: Scientix.AI running its own operations on a private, TOP-compatible operational-management vocabulary as the first customer of its runtime. Without a Core declaration, that consumer must declare its own transaction-time property and remap later, which is exactly the drift the extension contract exists to prevent.

This is a reconciliation, not a new ontology-design question. The semantics are settled by ADR-0021 as corrected; only the declaration is missing.

## Proposal

Declare `top:recordedAt` in `core/v1/shapes.ttl`, consistent with the erratum, and correct the one stale comment block that still says transaction time is `top:observedAt`.

```turtle
top:recordedAt a owl:DatatypeProperty ;
    rdfs:label "recorded at"@en ;
    top:flavor "Invariant" ;
    rdfs:domain top:CommonEntity ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "Transaction time: when the system first recorded this entity or entity-version (as we knew it at T1). Complements top:observedAt (valid time: the instant the fact was observed to hold in the world) and top:validFrom / top:validUntil (the valid-time interval on versioned values). ADR-0021 as corrected by the 2026-09-01 erratum. Optional at Universal DNA: the cardinality of the always-on contract is unchanged, and workflows and consumers may require it by tightening (ADR-0019)."@en .
```

Properties of the declaration:

- **Domain:** `top:CommonEntity`. Any entity may carry it.
- **Range:** `xsd:dateTime`.
- **Flavor:** Invariant, like `top:observedAt`, `top:validFrom`, and `top:validUntil`. The semantics of a clock cannot drift.
- **Cardinality at Core:** optional. The erratum keeps Universal DNA unchanged (exactly one `top:observedAt` per entity); this RFC adds no requirement to `top:UniversalDNAShape` or `top:BitemporalShape`. A consumer that needs transaction time on every object requires it by tightening in its own shapes, which is the ADR-0019 path.
- **Demonstration:** the consent walkthrough gains `top:recordedAt` on both versions so the artifact shows both clocks side by side, and its header comment stops saying the record clock is still to come.

The Core pull request implementing this is prepared on branch `core/declare-recordedat` and is opened only if this RFC is accepted.

## Alternatives considered

- **Do nothing.** Preserves the artifact as shipped. Rejected: every consumer that needs transaction time declares its own property, and two consumers end up with two names for one clock. The FIWARE failure mode, at Core.
- **Make `top:recordedAt` a fourth Universal DNA property, required on every entity.** Preserves symmetry with `top:observedAt`. Rejected: the erratum explicitly keeps Universal DNA cardinality unchanged, and a new required property would invalidate every existing instance and every walkthrough.
- **Require `top:recordedAt` on `top:Versioned` through `top:BitemporalShape`.** Attractive, since a version without a record clock is half a version. Not proposed here so that the RFC stays a reconciliation; raised as an open question for the accepting ADR.
- **Convener commits the declaration directly.** The omission is easy to fix and the convener owns `/core/`. Rejected by the convener: TOP's governance is worth exercising precisely when bypassing it would be easiest.

## Open questions

1. **PROV-O alignment.** `prov:generatedAtTime` is the time an entity was completely created, which is transaction time for a version node. Should `top:recordedAt` be declared `rdfs:subPropertyOf prov:generatedAtTime`, or is that a declared absence like `top:validFrom` (ADR-0021: PROV models system time, not valid time)? The draft declaration leaves it out; the accepting ADR decides.
2. **Tightening at Core for versioned nodes.** Should `top:BitemporalShape` require `top:recordedAt` (exactly one) on `top:Versioned`? If yes, the Tier-1 shapes inherit it and every Attestation and StatusChange must carry a record clock, which is arguably what "immutable version" means.
3. **The flavor count.** ADR-0019 lists five Invariant properties. Acceptance makes six; the accepting ADR should say so rather than leave the list stale.

## Consequences

- **What gets easier.** Two clocks, two declared properties. A consumer attaches transaction time without inventing a name. The artifact and the decision log agree.
- **What gets harder.** Nothing at Core; the property is optional.
- **What downstream consumers must adapt to.** Nothing required. A consumer that declared its own transaction-time property may map it by `owl:equivalentProperty`.
- **Follow-on work.** The accepting ADR; the spec page (`core/v1/index.html`) property list; the controlled-vocabulary record for the property when the CV layer lands (ADR-0018); a decision on open question 2.
- **What this forecloses.** The name. `top:recordedAt` was already chosen by the erratum; this RFC makes it citable.

## References

- ADR-0021 and its erratum of 2026-09-01 in [`../../decision-log.md`](../../decision-log.md); Issue #52; commits `c8af769` and `b3c9394`.
- ADR-0019 (flavors) and [`../../extension-contract.md`](../../extension-contract.md).
- [`../../../first-principles.md`](../../../first-principles.md) § 4, "Bitemporal by construction."
- [`../../../core/v1/shapes.ttl`](../../../core/v1/shapes.ttl) (comments on `top:observedAt` and `top:validFrom`), [`../../../core/v1/walkthroughs/consent-bitemporal.ttl`](../../../core/v1/walkthroughs/consent-bitemporal.ttl) (header comment).

## Notes for reviewers

Bo: open question 2 is the one with teeth. Everything else is bookkeeping.
