# Conventions — Universal DNA + the bitemporal + PROV envelope

## Universal DNA (TOP Core)
Everything modeled is, ultimately, a kind of `top:Core` (the single root above the eight
Category-Level Objects). Every TOP entity carries **three strands of Universal DNA**:
- **identity** — `top:identifier` (a stable identifier);
- **time** — `top:observedAt` (valid-time instant; the canonical NGSI-LD term);
- **lifecycle** — `top:status` (e.g. `active`, `superseded`, `retired`).

`cr:UniversalDNAShape` (the domain application of core's `top:UniversalDNAShape`) enforces identity + lifecycle; the bitemporal envelope below
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
> In this reference model we encode the convention explicitly so SHACL can test it.

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

## Vocabulary — operator dialects through the pipeline (ADR-0024)

The operator names the entity; the pipeline makes it rigorous (manifesto; first-principles P1/P2/P7).
The dialect layer lives in `ontology/cr-thesaurus.ttl` and follows four rules:

1. **Cover dialects generously.** Every known practitioner term for a modeled concept lands as a
   `skos:altLabel` (acronyms, spelling variants, workplace shorthand). Coverage is the point —
   findability in the operator's own words. `skos:prefLabel` equals `rdfs:label` (one preferred
   name; "Participant" for `cr:StudySubject` per ADR-0024).
2. **Route, don't promote, the borrowed registers.** Standards jargon (`ResearchSubject`,
   `ItemData`, `Encounter`) and lay terms ("side effect") are `skos:hiddenLabel`s — searchable,
   never displayed. Standards vocabulary belongs to the projection layer.
3. **Gate the watch-list, nothing else.** Terms with high ambiguity or high cross-pattern
   matching (`agent`, `subject`, `monitor`, `arm`, `site`, `screen`) live in
   `cr:AmbiguousTermsWatchList` as SKOS-XL labels; each carries an anti-synonym / context-routing
   `skos:scopeNote`, and **no new label matching a watch-list term lands without one**. Calls are
   made per term; there is deliberately no general restriction rule.
4. **Provenance where it matters.** A label whose origin is load-bearing (who says this, which
   document) is reified as a `skosxl:Label` with `dct:source`. The first seeding source is the
   Clinical Trial Operating Model practitioner document (2026-07).

**Class-creation gate (P5/P6, ADR-0024).** Before minting a class, ask one question: *is this a
distinct thing, or a classification of a thing?* A real workflow boundary or distinct structure
earns a class (`cr:InformedConsent`, `cr:DatabaseLock`). A judgment-against-criteria is a
**promoted fact** with the "type" derived as a view — never a subclass. Known deviations
(recorded, not yet refactored): `cr:SeriousAdverseEvent`, `cr:DoseLimitingToxicity`, `cr:SUSAR`.

**`hasX` names a relationship, never a flag.** The sentence form is the point:
`ex:bd-coll cr:hasConsent ex:bd-consent` reads subject–predicate–object — "the
collection has consent consent-123." Booleans are banned outright (P6), so a
`has*` value is always an entity reference; the linter fails any `has*`/`is*`
property with a datatype range, making a flag-shaped `hasX` structurally
impossible. Display layers strip the `has` (the retrieval views project
`sh:name "consent"`), so operators see nouns while the graph keeps sentences.

**BFO (ADR-0024).** Full alignment, carried at the Core layer: the CLO→BFO bridge lives in
`core/v1` (CLO-level where the category is BFO-homogeneous, leaf-level where it is not). Domain
modules align to Core only and inherit BFO transitively — a `bfo:` IRI in a `cr:` module is a
review-time defect.
