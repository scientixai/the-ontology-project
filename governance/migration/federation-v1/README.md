# Federation v1 — migration runbook

This bundle carves the monorepo (`scientixai/the-ontology-project`) into the five-repo
federation defined in [RFC 0002](../../rfcs/proposed/0002-repository-federation.md), extending
[ADR-0023](../../decision-log.md#adr-0023-hub-and-spoke-domains-core-owns-the-contract-and-the-registry-each-domain-owns-its-repo).

**Nothing here mutates `origin`.** Every extraction runs against a local **mirror clone**.
The new repositories are produced as local bare/working repos; *you* push them to the new
org after inspecting them. No force-push, no history rewrite on the live monorepo.

## Prerequisites

- `git` ≥ 2.35
- [`git-filter-repo`](https://github.com/newren/git-filter-repo) on `PATH`
  (`pip install git-filter-repo`). Directory-level extraction could use `git subtree split`,
  but `hcls-core.ttl` is a **single file inside `cr-domain/ontology/`**, so path-level
  `filter-repo` is required — subtree cannot carve a file.
- The neutral GitHub org **`the-ontology-project`** created (Free plan, public repos — see RFC
  §Open-Questions and the plan discussion). Five empty repos: `core`, `hcls`,
  `clinical-research`, `standards`, `site`.

## Order of operations (matches ADR-0023 sequencing)

1. **Finish CR V1 on its branch** — consistency fixes, docs, release discipline. Prerequisite
   regardless of topology. *Not automated here.*
2. **Publish Core as a versioned, checksummed consumable** and resolve the known Core↔CR seam
   conflicts (duplicate `top:UniversalDNAShape` IRI, dangling upper-class refs). *Not automated
   here — this is ontology work, tracked separately.*
3. **Run `./federate.sh`** — produces the five repos locally, history preserved.
4. **Inspect** each produced repo (`git log`, `git verify`, parse-check the TTL).
5. **Push** each to the org (the script prints the exact `git remote add` + `git push` lines;
   it does not run them).
6. **Register** — commit `domain-registry.seed.ttl` into `core` as `registry/domains.ttl`.
7. **Wire deploy-time site assembly** for `top.scientix.ai`. *Not automated here.*

## What lands where

| New repo | Paths extracted from the monorepo | Then removed from `core` |
| --- | --- | --- |
| `core` | *everything not extracted below* (the monorepo minus the carve-outs) | — |
| `hcls` | `cr-domain/ontology/hcls-core.ttl` | n/a (also removed from `clinical-research`) |
| `clinical-research` | `cr-domain/` **minus** `hcls-core.ttl` and the top-core stub | `cr-domain/` |
| `standards` | *seeded fresh* — no history to preserve yet; receives the `w5`-axis + AFO work | — |
| `site` | `index.html`, `manifesto.html`, `roadmap.html`, `first-principles*.html`, `styles.css`, `images/`, `CNAME` | those paths |

**Guarding the seam:** `clinical-research`'s `cr-core` references `hcls:` and `top:` by
namespace **string** (no `owl:imports` today), so extraction breaks nothing mechanically. The
executable contract *adds* the version pins afterward — it does not depend on them existing at
carve time. The hand-rolled `top-core` **stub** inside `cr-domain/ontology/` is deleted, not
migrated: `clinical-research` pins the real published `core` instead.

## Reversibility

The monorepo is untouched until you push. If any produced repo looks wrong, delete the local
`build/` directory and re-run. The only one-way step is downstream: once workflow repos pin an
`hcls` release, hcls cannot move back inside a workflow (RFC §Consequences).
