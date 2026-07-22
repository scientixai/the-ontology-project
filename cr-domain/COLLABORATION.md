# TOP — Collaboration & external-ontology principle

> Ratified as [ADR-0029](../governance/decision-log.md#adr-0029-adopt-sound-external-ontologies-dont-reinvent--usdm-rdf-via-kerforsusdm-rdf).

TOP is a **collaborative** effort. It does not reinvent what already exists well.

## Leverage, don't reinvent

When a sound external ontology, vocabulary, or model already covers a space, TOP
**adopts and crosswalks to it** rather than authoring a rival. We stand on other
people's good work and credit it. Concretely:

- **Adopt the canonical artifact** — vendor it verbatim, sha-pinned, with provenance
  (source repo, version, retrieval date, license). Do not maintain a parallel
  rendering at someone else's IRIs; that is a drift hazard, not reuse.
- **Crosswalk, don't fork** — TOP's own classes map to the external model via SSSOM
  (`skos:exactMatch` / `closeMatch` / `relatedMatch`) with confidence + justification,
  never by duplicating and diverging.
- **Credit the author** — name them in provenance. Adoption is a relationship.

**First worked instance:** the USDM RDF/OWL layer is adopted verbatim from Kerstin
Forsberg's `github.com/kerfors/usdm-rdf` (the `w3id.org/cdisc/usdm/v4/` namespace's
registered target), not generated in-house — see `ontology/vendor/usdm/PROVENANCE.md`.
Our earlier local generator is retired. Related: NCIt anchors, LOINC/UCUM/QUDT, FHIR,
CDISC SDTM, MedDRA are all consumed as inputs/crosswalk targets, never re-authored.

## TOP as a testing ground that feeds upstream

The adopt-and-crosswalk posture makes a **two-way** relationship possible, not just
consumption:

1. **Pull collaborators toward the adjacent, unmodeled space.** Where a standard stops
   (e.g. USDM stops at study definition; it does not model transfer cadence, chain of
   custody, closeout, or submission), TOP already has a provenance-native, bitemporal
   model of that adjacent territory. That is a natural place to invite the standard's
   authors into work that ventures beyond their current scope.
2. **Run ahead as a proving ground.** Because TOP is not bound by a standards body's
   ballot cycle, it can model and *test* an extension (in real worked examples, under a
   regression-gated shape suite) before the standard formally adopts it.
3. **Feed it back.** What proves out in TOP — an IRI-minting convention, a shape, a
   modeled gap the community hadn't yet formalized — becomes a concrete artifact the
   upstream can point to and, if they choose, ratify. TOP moves ahead *so that* the
   standard can follow with evidence, not instead of it.

The measure of success is not that TOP owns the model. It is that the ecosystem ends up
with **one** good, shared model — and TOP helped get it there faster.
