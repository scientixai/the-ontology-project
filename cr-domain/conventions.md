# Conventions — Universal DNA + the bitemporal + PROV envelope

## Universal DNA (TOP Core)
Everything modeled is, ultimately, a kind of `top:Core` (the single root above the eight
Category-Level Objects). Every TOP entity carries **three strands of Universal DNA**:
- **identity** — `top:identifier` (a stable identifier);
- **time** — `top:observedAt` (valid-time instant; the canonical NGSI-LD term);
- **lifecycle** — `top:status` (e.g. `active`, `superseded`, `retired`).

`top:UniversalDNAShape` enforces identity + lifecycle; the bitemporal envelope below
enforces the time strand (`observedAt`) plus transaction time and provenance.

Every assertion that a regulator could ever ask about carries **two time axes** and
**provenance**. This is the non-negotiable spine (v1-plan Principle 4).

## Two time axes
- **Valid time** — when the fact is true *in the world*: `top:observedAt`, `top:validTo`.
- **Transaction time** — when the *system knew it* (append-only, immutable):
  `top:recordedAt`, `top:supersededAt`.

A statement may be valid-from Monday but recorded Tuesday; both are kept, so the gap
is visible and back-dating is structurally impossible (transaction time is never rewritten —
a correction is a *new* assertion with a later `recordedAt`, and the prior one gets
`supersededAt`).

> Runtime mapping (NGSI-LD): `top:observedAt/validTo` ≈ `observedAt`;
> `top:recordedAt/supersededAt` ≈ `createdAt`/`modifiedAt`; queried via the Temporal API.
> In this TTL workspace we model the convention explicitly so SHACL can test it.

## Provenance (W3C PROV)
- `prov:wasAttributedTo` — the responsible/attesting agent (≥1, IRI).
- `prov:wasGeneratedBy` / `prov:generatedAtTime` — the activity/act that produced it.

## The marker class
Anything carrying the envelope is typed `top:ProvenancedEntity`. The `top:BitemporalProvShape`
(in `shapes/`) enforces: exactly one `observedAt`, exactly one `recordedAt`, ≥1 `wasAttributedTo`.

## "As-of" reconstruction
Because both axes are present, the inspector's question — *"show me the state on the day X
happened"* — is a filter (`observedAt ≤ T` and the assertion not yet `supersededAt` as-of the
transaction time of interest), not an excavation.

## No reified Role
Roles are bitemporal relationships/qualifiers (`Person —isPI-of→ Study`), never first-class
`Role` objects (bitemporality supersedes the only rationale).

## Privacy boundary — pseudonymization & PII containment
Clinical data is **pseudonymized, not anonymized**: re-identification is deliberately preserved
but controlled (adverse-event follow-up, emergency unblinding). Under GDPR it remains personal data.

- `hcls:Person` is the **boundary-only / PII layer** — an identifiable person lives inside the
  source/site sovereign boundary.
- `cr:StudySubject` is the **pseudonymous** in-study identity used everywhere downstream.
- The **only legal Person↔Subject link is the attested Enrollment bridge** (`cr:enrolledPerson`),
  which is the controlled re-identification edge (the cross-federation identity binding).
- **`cr:forSubject` must reference a `StudySubject`, never a `Person`** — enforced by
  `cr:PIIContainmentShape`. Any dataset/result/act pointing at a Person is a structural leak,
  caught at validation.
- **Pseudonymization happens upstream at the site**, before data crosses a boundary. The
  reference encodes the *invariant* (containment); the *mechanism* is runtime/IP, out of scope.
- **Limit:** validation catches structural leaks, not PII smuggled into free-text labels/values —
  that is an upstream redaction responsibility.
