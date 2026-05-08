# Site spec planning note (working draft)

> Working document. Edited as Site lifts from partial scaffold to full spec discipline. Folds into `site-spec.html` once the scope decisions below are sealed.
> Last touched 2026-05-08.

## Purpose

Site is the second top-level to lift to full spec discipline (per ROADMAP.md). This note captures the scope, the open architectural questions, and the recommendations to resolve before drafting `site-spec.html` and expanding the source intermediate. Deliberately short — a working artifact, not a sealed spec.

## Current state

The Site entry in `top-strawman.json` carries three attributes (`siteId`, `siteName`, `siteType`) and five relationships (`belongsToOrganization`, `partOfSiteNetwork`, `parentSite`, `hasPrincipalInvestigator`, `participatesIn`), with a `_partialEntry` note flagging that the rest of OOUX Section 3 entry #1 has not been transcribed. There is no `site-spec.html`, no Site examples, and no Site SHACL invariants. The OOUX hierarchy entry (`docs/ooux-hierarchy.html`, lines 214–224) names five sub-objects/relationships that have not been modeled yet: Site Staff (delegated), Site Network membership, Equipment (site-bound), Storage Location (site-bound), Site Performance Metric. The hierarchy also notes "Sites can exist independently of any single Study; they enter Studies through CTAs."

## The System question (the central architectural concern)

ROADMAP.md says Site lifting "forces a confrontation with the parked System work (the three-layer ownership-versus-use pattern from the eTMF insight)." The Sponsor v0.1.3 closure log parked it differently — for the Study spec, with `Sponsor.operatesSystem` carrying the per-Study operational ownership view as a simplification. The two notes disagree on where the work lands.

Bo's framing sharpens the problem. The System question is not two-layer (ownership vs use). It is **three-axis**:

1. **Ownership** — who owns the System instance (the Site, the Sponsor, the CRO, a vendor).
2. **Use** — who interacts with the System on this Study.
3. **Visibility** — what each role can see about the System, even when ownership and use are resolved.

A worked example to ground it. Memorial Sloan Kettering (Site) uses Veeva Vault (eTMF) for Study X, sponsored by Pfizer.

- The Site sees the full record: `vendor=Veeva`, `productName=Vault`, `instanceId=mskcc-prod`, `baseUrl=https://veeva.mskcc.org/...`, `version`, `validatedFor21CFRPart11=true`.
- The Sponsor sees that the Site uses an eTMF (existence + `systemType=ETMF`), probably `vendor` and `productName`, **not** `instanceId` or `baseUrl`.
- The Regulator sees that an eTMF exists at the Site and meets 21 CFR Part 11 — typically through Site qualification documentation rather than direct system access.

The visibility axis is not just role-based redaction. The Sponsor genuinely may not know the Site's eTMF URL. There is no place in the audit trail where that fact was recorded for the Sponsor to read.

### Three options for handling visibility in the schema

**Option A — single System instance, multiple roles point at it; visibility is a projection-layer concern.** The graph carries the union of what is known. The Site's record of the eTMF is one System entity with all the attributes the Site knows. The Sponsor's `operatesSystem` and the Site's `usesEtmfSystem` (or whatever the predicates settle as) reference the same System URI when they refer to the same instance. The role-specific projection (a v0.3 reference-pattern artifact, deferred per ROADMAP.md) filters which attributes a Sponsor portal renders. Schema stays compact.

**Option B — separate System records per role; each role records what it knows.** The Sponsor's System record is a stub (`vendor`, `systemType`); the Site's System record is the full thing. They are linked via `aliasOf` or similar. Matches operational reality (the Sponsor often genuinely does not know the URL) but multiplies entities and loses graph join elegance.

**Option C — single System instance with per-attribute access-control markers.** Each attribute carries a visibility marker (e.g., `_visibleTo: [SITE_ROLE, SPONSOR_ROLE]`). Heavyweight; bleeds RBAC into the schema; couples the ontology to a specific access-control regime.

**Recommendation: Option A**, with one nuance. The graph carries truth as known by whoever populated the System record. If the Site populated, the record is full; if the Sponsor populated, the record is a stub. A second Sponsor query that joins through to the Site's record returns the union, but a Sponsor portal renders only the projection contract. Visibility is a presentation concern, not a schema concern. This dovetails with the existing v0.3 reference-architecture roadmap item ("role-specific projections and views") rather than expanding it.

The catch is that Option A pushes a real concern into the projection layer that does not yet exist. The site-spec.html should call this out as a tracked open issue rather than pretending the projection layer is sufficient today. The Sponsor spec already documents per-persona query patterns in §5; Site spec will do the same. The visibility constraint becomes "this query is what a Sponsor sees; this query is what the Site sees" — visible in the spec text, deferred for formalization.

## Scope decision for this pass

Recommend the following lift, in this order:

1. Expand Site in `top-strawman.json` to full attribute and relationship coverage from OOUX entry #1 — including the Status enum (likely `ACTIVE`, `IN_QUALIFICATION`, `ON_HOLD`, `CLOSED`), address fields, and a handful of qualification attributes (`gcpQualified`, `irbApprovalStatus`, etc., names TBD).
2. Land the `System` horizontal minimally with `vendor`, `productName`, `instanceId`, `baseUrl`, `systemType` (enum: `EDC`, `CTMS`, `ETMF`, `IRT`, `SAFETY_DB`, `EMR`, `ELN`, `OTHER`), `version`, `validatedFor21CFRPart11`. Adds the target Sponsor's `operatesSystem` and Site's new `usesSystem` predicates point at — current relationships flag-miss the target.
3. Add the Site → System relationships split per system type (`usesEtmfSystem`, `usesEdcSystem`, `usesCtmsSystem`, etc.) following the polysemous-verb-split discipline from Sponsor v0.1.2.
4. Defer Site Staff to a `delegatesTo` relationship pointing at a flagged-missing Person horizontal (Site Staff as a full sub-object is a follow-on pass).
5. Defer Storage Location and Site Performance Metric details — flag-miss them on Site relationships, capture as tracked open issues in the spec.
6. Write `site-spec.html` following the Sponsor spec template: TL;DR, model summary, architectural decisions, stress-test scenarios, query patterns by persona, NLP-to-NGSI-LD translation, SHACL invariants, cross-walks, tracked open issues.
7. Encode SHACL-SPARQL domain invariants. Candidate invariants: (a) hard violation when a Site has `siteType=DECENTRALIZED_HUB` but `belongsToOrganization` is absent or has type `INDIVIDUAL`; (b) hard violation when a Site claims `partOfSiteNetwork` pointing at an Organization whose `organizationType` is not `SITE_NETWORK` or `SMO`; (c) soft warning when a Site's `parentSite` and `partOfSiteNetwork` both resolve to entities that disagree on the network parent. Three to five invariants total, mirroring Sponsor's pattern.
8. Author one worked example mirroring `sponsor-pfizer-iqvia.ttl`: a multi-site SMO-managed network running a Pfizer-sponsored study, validating clean against pyshacl.
9. Add a `site-verification-history.html` mirroring `sponsor-verification-history.html` once Bo's verification questions for Site are answered.

## Stress-test scenarios

The scenarios that need to validate cleanly:

- A satellite clinic Site shares Equipment with its parent Site (`parentSite` + Equipment binding).
- An SMO (Elevate Research) with N member Sites, each with `partOfSiteNetwork` pointing at the Elevate Research Organization, and Organization → `managesSite` returning the full set.
- A Site changes principal investigator mid-study (temporal `hasPrincipalInvestigator`, mirrors Sponsor's `validFrom`/`validUntil` pattern).
- A `DECENTRALIZED_HUB` Site serving multiple geographic regions (no fixed address; address as 0..N rather than 1..1).
- A Site participating in twelve concurrent Studies; Sponsor wants the workload view across that Site.
- A Site uses a Sponsor-provisioned EDC and a Site-owned eTMF; the System ownership visibility split shows up in queries.
- Site qualification expires and is renewed; Site moves through `IN_QUALIFICATION → ACTIVE → ON_HOLD → ACTIVE` as the Sponsor reauthorizes.

## Open questions to resolve before sealing

1. Is `hasPrincipalInvestigator` a hard 1..1 constraint, or temporal (PI changes mid-study, like Sponsor's M&A handoff)? Recommendation: temporal, with `validFrom`/`validUntil` on the relationship.
2. Site Staff: full sub-object now, separate Person horizontal, or `delegatesTo` relationships pointing at a flagged-missing Person? Recommendation: `delegatesTo` + flagged-missing Person; Person lifts as a horizontal on its own track.
3. Status enum values and lifecycle transitions — what are the legal transitions and which need SHACL guarding?
4. CTA-mediated Study entry — does Site reference the CTA Document, or just the Study? Recommendation: just Study (`participatesIn`); CTA reference lives on the Sponsor side via `holds` relationship to Contract.
5. Site Performance Metric — sub-object now, or parked? Recommendation: parked. Surface as a tracked open issue with the rationale (metric definitions are role-specific and belong with reference-pattern projections, not the core schema).
6. Address modeling — single embedded object (mirroring Organization.legalAddress) or 0..N for multi-location decentralized hubs? Recommendation: 0..N for Site, since the decentralized-hub case is real and the multi-site-network-as-single-Organization case already exists.

## Pointers

- [`site-spec.html`](site-spec.html) — to be written; this note seeds it.
- [`ooux-hierarchy.html`](ooux-hierarchy.html) — Site OOUX entry at lines 214–224.
- [`top-strawman.json`](../source/top-strawman.json) — Site entry at line 134, partial scaffold.
- [`sponsor-spec.html`](sponsor-spec.html) — template the Site spec follows.
- [`ROADMAP.md`](../../../ROADMAP.md) — Site listed as the next top-level to lift.
