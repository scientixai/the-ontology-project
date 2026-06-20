# Lessons from FIWARE Smart Data Models: what TOP inverts, what it still risks

*Status: pre-RFC strategic planning. Author: Bo Lora (BDFL). Audience: Bo, future working-group leads, founding signatories, and anyone evaluating whether TOP repeats the adoption failure of its nearest neighbor.*

*Companion to the [Architectural Strategy Brief](top-strategy-brief.md), to [first-principles.md § 4](../../first-principles.md), and to [ADR-0021](../decision-log.md#adr-0021-bitemporal-model-valid-time-and-transaction-time-on-core).*

---

## Why this document exists

The closest thing to TOP in the NGSI-LD world is the FIWARE **Smart Data Models** initiative — a large open catalog of domain entity schemas (`WeatherObserved`, `ParkingSpot`, `AgriCrop`, `Device`, …) maintained under the FIWARE Foundation / TM Forum / IUDX / OASC. By several accounts adoption has been weak: many model repositories have sat untouched for years, and the "smart city" demand signal that was meant to pull them forward cooled.

If the nearest neighbor underdelivered, due diligence demands we name *why*, and check our own design against each cause. This note is that check. It is deliberately honest about the risks TOP still carries — it is not a victory lap.

## Why Smart Data Models underdelivered (the pattern)

These are the commonly-cited causes, not a citation-backed study; treat them as the shape of the problem, not a measurement.

1. **Breadth without depth.** Thousands of concrete models, contributed unevenly, thinly curated. The long tail goes stale because nobody owns it and nothing depends on it.
2. **Shallow semantics.** JSON Schema validates *structure*, not *meaning*. Two models of the same concept still do not interoperate, so the standard never repays the cost of adopting it.
3. **Weak forcing function.** The downstream consumer was mostly smart-city dashboards via a context broker. Nobody *had* to conform.
4. **Funding-tied stewardship.** Momentum rode project funding cycles; when grants ebbed, maintenance stalled.
5. **Wrong altitude, too soon.** Hundreds of specific entity types were standardized before a small, stable, shared core existed. Concrete models date fast; with no invariant center they drift apart.

## What TOP structurally inverts

- **Against breadth-without-depth and wrong-altitude (1, 5).** TOP is foundation-first and deliberately small — one root, eight categories, twenty-nine leaves; domains compose on top via `subClassOf`. ADR-0004 explicitly rejected the flat sibling-catalog pattern. There is no long tail of concrete models to rot; there is a minimal core meant to stay stable.
- **Against shallow semantics (2).** OWL + SHACL + PROV-O + light BFO + SKOS means two extensions of the same Core concept *do* interoperate — they share the lattice and the ADR-0019 extension contract. This is the semantic payback Smart Data Models never delivered.
- **Against the weak forcing function (3).** TOP's forcing function is regulated audit (21 CFR Part 11, GxP) and trustworthy AI grounding on high-consequence data. In pharma the audit trail is not optional. The Tier-1 enforcement in ADR-0021 (a cryptographically anchored value *must* be an immutable version) is a regulator-required capability, not a nicety. This is a far stronger adoption pull than a city dashboard.

On the two deepest causes — sprawl and shallow semantics — TOP is close to a direct inversion, by design.

## What TOP still risks (carry-over and mirror-image)

1. **NGSI-LD niche-ness (inherited).** To the extent TOP leans on NGSI-LD, it shares NGSI-LD's smaller implementer community. Mitigation is built in: TOP is primarily RDF/OWL/SHACL/SKOS with PROV-O / BFO / schema.org alignment — reachable from the much larger semantic-web and OBO worlds — and it *projects to* NGSI-LD rather than being defined by it. Keep the projection a profile, never the master.
2. **Stewardship sustainability (the people problem).** Cause (4) was not technical. TOP has the governance scaffolding (ADR-0017 directory-scoped ownership, working groups, RFCs) but scaffolding is not sustained effort. A foundation with no maintainers goes stale regardless of architecture.
3. **Cold-start — the mirror-image failure.** Smart Data Models were *too concrete*; the inverse risk for a foundation-first project is being *too abstract* — an elegant upper layer nobody instantiates against real operator data. The guard is at least one real workflow extension used end-to-end by a real organization. That is exactly the clinical-research stack being replanned; it makes getting that lighthouse right urgent, not merely tidy.

## Design implications (what this changes about how we build)

1. **Keep Core minimal; make every addition earn its place.** The bitemporal model (ADR-0021) is defensible *because* it is tethered to the forcing function (audit / non-repudiation), not to abstract completeness. Resist gold-plating it: opt-in, semantically triggered, only as much machinery as a real regulated consumer needs. Do not let it grow into a temporal-logic showcase.
2. **Prioritize the lighthouse over breadth.** Do not enumerate domains. Drive both the bitemporal model and Core's adequacy from one real clinical-research extension. If Core survives contact with that, it is real; if it does not, learn it now rather than across a catalog.

## In one line

Smart Data Models failed mainly from breadth without depth, shallow semantics, and a weak forcing function. TOP inverts the first two by construction and picks a domain with a far stronger forcing function — but it still must earn sustained stewardship and prove itself against one real consumer before it earns the right to scale.
