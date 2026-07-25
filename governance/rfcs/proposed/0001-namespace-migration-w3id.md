# RFC 0001: Migrate the canonical namespace to `w3id.org/top` and host on a standalone domain

- **Status:** Proposed
- **Date:** 2026-07-25
- **Authors:** @bolora
- **Affected groups:** Core Stewards (all downstream consumers cite these URIs); every future Working Group inherits the new base
- **Required quorum:** Core stewards (Bo as sole signatory until stewards are seated), per [`README.md`](../README.md)
- **Supersedes:** n/a (extends ADR-0003 and ADR-0005, which set the current URI structure)
- **ADR on acceptance:** ADR-0023

## Motivation

Every concept TOP publishes is identified by a URI, and today every one of those URIs
is anchored to a host the project does not want to be permanently bound to:

```
https://top.scientix.ai/v1#Person
https://top.scientix.ai/hcls/clinical-research/v1#AdverseEvent
```

Two problems follow, and TOP's whole value proposition — being *stable provenance
infrastructure* — depends on fixing both.

1. **Identity is coupled to hosting.** `top.scientix.ai` is a subdomain of the company.
   The moment the ontology needs to move — a new domain, a different static host, a
   foundation takes stewardship — every published URI breaks, or the company subdomain
   must be maintained forever as a hostage to past decisions. An ontology whose
   identifiers can rot is not infrastructure anyone should build regulated-data systems
   on. **Much hinges on TOP stability**; this is the root of it.

2. **Identity is coupled to the company.** TOP's creed is *monetize the runtime, not
   the commons* — the commons is public, Apache-2.0, and must be legibly independent of
   Scientix.AI. A namespace that literally reads `scientix.ai` undercuts that on its
   face to exactly the audience (regulators, standards bodies, contributors) who need to
   trust the commons is not a company asset.

The fix is the standard one for permanent web identifiers: put the canonical URIs behind
a **community-run permanent-identifier redirect** (`w3id.org`, run by the W3C Permanent
Identifier Community Group) and let it redirect to wherever the project happens to host.
Identity (the w3id URI) is then decoupled from hosting (the domain), permanently. This is
the same mechanism BFO, OBO Foundry, SSSOM, and much of the ontology world already rely
on — and TOP already aligns to several of them.

## Proposal

### 1. Canonical namespace moves to `https://w3id.org/top/`

The `top` path on w3id.org is **confirmed available** (no `top/` directory exists in
`perma-id/w3id.org` as of 2026-07-25). It mirrors the `top:` prefix already used
throughout the ontology, so the prefix↔path correspondence stays intact.

Global rewrite rule for the ontology's own URLs:

```
https://top.scientix.ai/   →   https://w3id.org/top/
```

Concept and ontology URIs after migration:

| Before | After |
|---|---|
| `https://top.scientix.ai/v1#Person` | `https://w3id.org/top/v1#Person` |
| `https://top.scientix.ai/v1#Core` | `https://w3id.org/top/v1#Core` |
| `https://top.scientix.ai/core/v1` (owl:Ontology) | `https://w3id.org/top/core/v1` |
| `https://top.scientix.ai/v1#TaxonomyV1` | `https://w3id.org/top/v1#TaxonomyV1` |
| `https://top.scientix.ai/hcls/clinical-research/v1#AdverseEvent` | `https://w3id.org/top/hcls/clinical-research/v1#AdverseEvent` |

Prefix declarations (`@prefix top:`, `topcr:`, `topcd:`, `example:` …) update to the
`w3id.org/top` base. The `top:` / `topcr:` short forms are unchanged.

### 2. w3id redirects to a standalone hosting domain

w3id.org is **only** a redirector; it holds no content. It needs a target. Per the
betting decision (2026-07-25), TOP moves off `top.scientix.ai` onto a **standalone domain
`<TOP_DOMAIN>`** (to be provided — see Open Questions) served by GitHub Pages from this
repo's `main`, exactly as today (ADR-0017, and the "GitHub Pages stays simple" note in
the decision log). Only `CNAME` changes.

The w3id registration is a single `.htaccess` submitted as a PR to
`perma-id/w3id.org` under `top/`. The prepared config lives in this repo at
[`governance/w3id/top/.htaccess`](../../w3id/top/.htaccess) as the source of truth, so
the upstream PR is a copy and future edits are version-controlled here. It redirects the
whole path space (so `w3id.org/top/**` resolves), with content negotiation so a Turtle
request lands on `.ttl` and a browser lands on the HTML spec page.

### 3. Backward compatibility — old URIs must not rot

The point of this RFC is that URIs never break, so the *old* URIs cannot break either:

- **`top.scientix.ai` keeps serving and 301-redirects** to `w3id.org/top/**` (or
  directly to `<TOP_DOMAIN>`), indefinitely. A permanent redirect, not a teardown. Any
  triple already published against `top.scientix.ai` continues to resolve.
- The migration is a **major version boundary in identity but not in semantics**: the
  same concepts, same `v1`, new base. We document the base change prominently in the
  README, the Core spec page, and the decision log so downstream consumers re-point.

### 4. Cutover recipe (ready to run once `<TOP_DOMAIN>` + the w3id PR are live)

The rewrite is mechanical and must land as one coordinated cutover **after** the w3id
`top/` redirect is registered and `<TOP_DOMAIN>` resolves — never before, or resolution
breaks in the gap. Files touched: `core/v1/*.ttl`, `core/v1/walkthroughs/*.ttl`,
`taxonomy/taxonomy.ttl`, `taxonomy/taxonomy.csv`, `core/v1/index.html`, the
`governance/planning/*.md` that carry example prefixes, and any JSON-LD `@context`.

```sh
# 1. Rewrite ontology URLs (NOT the company link https://scientix.ai)
grep -rlZ 'https://top\.scientix\.ai/' --include='*.ttl' --include='*.csv' \
     --include='*.jsonld' --include='*.html' --include='*.md' . \
  | xargs -0 sed -i 's#https://top\.scientix\.ai/#https://w3id.org/top/#g'

# 2. Point hosting at the new domain
echo '<TOP_DOMAIN>' > CNAME

# 3. Update display/branding text (README badge, index.html header chip) by hand —
#    these read "top.scientix.ai" as a label, not a URL.
```

A follow-up validation runs the existing SHACL/`pyshacl` and link checks (ADR-0010's
four-layer enforcement) against the rewritten graph before merge.

## Alternatives considered

- **Do nothing — keep `top.scientix.ai`.** *Preserves* zero migration cost. *Changes*
  nothing. *Rejected* because it permanently welds the commons' identity to a company
  subdomain and leaves every URI hostage to that host. This is the status quo the RFC
  exists to end.
- **Move to a standalone domain, but make the domain itself the namespace** (e.g.
  `https://<TOP_DOMAIN>/v1#`). *Changes* the base once. *Preserves* nothing against the
  next move — it just relocates the coupling from one host to another. If `<TOP_DOMAIN>`
  ever changes (foundation, rebrand), everything breaks again. w3id is the layer of
  indirection that makes the domain swappable. *Rejected.*
- **PURL (`purl.org`).** Comparable indirection, but w3id is the de-facto standard in the
  ontology/linked-data community TOP aligns with, has a healthier maintenance story, and
  supports the `.htaccess` content negotiation TOP needs. *Rejected in favor of w3id.*
- **Bioregistry prefix now.** Complementary, not a substitute — Bioregistry can point at
  the w3id base later (already a deferred item in `top-hcls-strategy.md`). Not this RFC.

## Open questions

1. **`<TOP_DOMAIN>` — the standalone hosting domain.** This is the one input the cutover
   is blocked on. Bo to provide the domain he owns/registers (strawman candidates:
   `theontologyproject.org`, `top-commons.org`). It becomes the `CNAME` and the w3id
   redirect target.
2. **Redirect chain shape.** Should `top.scientix.ai` 301 → `w3id.org/top` →
   `<TOP_DOMAIN>` (single source of truth, one extra hop), or `top.scientix.ai` 301 →
   `<TOP_DOMAIN>` directly (fewer hops, but two hosts must both know the redirect map)?
   Recommendation: everything through w3id, so there is exactly one canonical form.
3. **Content negotiation granularity.** Confirm the `.htaccess` maps `Accept: text/turtle`
   to `.ttl` and default to the HTML spec page at each `v1` path.

## Consequences

- **Easier:** re-hosting the commons ever again (zero URI churn); presenting the commons
  as company-independent; aligning with the ontology ecosystem's identifier norms.
- **Harder / cost:** a one-time coordinated cutover; a permanent obligation to keep the
  `top.scientix.ai` 301 alive; a dependency on w3id.org's community infrastructure (well
  established, but now in the critical path for resolution).
- **Downstream consumers must adapt:** anyone who has cited `top.scientix.ai/...` should
  re-point to `w3id.org/top/...`. The 301 keeps them working in the meantime.
- **Follow-on work:** submit the `perma-id/w3id.org` PR; stand up `<TOP_DOMAIN>` on GitHub
  Pages; run the cutover recipe; append ADR-0023; **all new work (starting with the
  clinical-research v1 seed directory) authors against `w3id.org/top` from the start** so
  nothing is written against the old base.
- **Forecloses:** casual future base changes — once consumers trust `w3id.org/top`, it is
  the permanent contract. That permanence is the entire point.

## References

- ADR-0003 (namespace is the project), ADR-0005 (drop `/onto/` from paths), ADR-0017
  (monorepo, GitHub Pages from `main`) in [`../decision-log.md`](../decision-log.md)
- W3C Permanent Identifier Community Group — `perma-id/w3id.org`
- `governance/planning/top-hcls-strategy.md` (Bioregistry deferred item)

## Notes for reviewers

Bo: the parts I most want your read on are **Open Question 1 (the domain)** — the cutover
is blocked only on that — and **Open Question 2 (redirect chain shape)**. Everything else
is mechanical once those are settled.

---

*Template version 1.0.*
