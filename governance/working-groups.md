# TOP Working Groups

> A working group (WG) is the steward of a workflow extension or a cross-cutting governance area. It owns a directory in the monorepo, owns the technical decisions inside that directory, and operates under the broader project conventions in [`decision-log.md`](decision-log.md) and [`rfcs/README.md`](rfcs/README.md).

Per [ADR-0015](decision-log.md#adr-0015-monorepo-with-directory-scoped-ownership), TOP is a single repository with directory-scoped ownership. A working group's authority and accountability map to a directory tree.

## Standing groups

| Group | Owns | Status |
| --- | --- | --- |
| **Core Stewards** | `/core/`, `/taxonomy/`, `/governance/`, project-level documents | Active (convener-led; review pool of one) |
| **Clinical Research WG** | `/clinical-research/` | Forming |
| **Care Delivery WG** | `/care-delivery/` (when directory lifts) | Proposed |
| **Manufacturing WG** | `/manufacturing/` (when directory lifts) | Proposed |
| **Supply Chain WG** | `/supply-chain/` (when directory lifts) | Proposed |

The convener (currently Bo Lora) holds Core stewardship until a Core stewards committee forms. As workflow WGs activate, they take ownership of their directories per `.github/CODEOWNERS`.

## What a WG does

- **Owns the spec.** The taxonomy, OWL/SHACL definitions, SKOS, and operator-facing documentation under its directory.
- **Owns the cadence.** Each WG releases its directory on its own schedule (versioned subdirectories like `/clinical-research/v0.2/`). Other WGs do not block its progress.
- **Owns the operator vocabulary.** The names of entities, attributes, and relationships in its workflow. Practitioner-grounded per [ADR-0013](decision-log.md#adr-0013-practitioner-first-tops-primary-customer).
- **Reviews its own PRs.** Pull requests touching only the WG's directory need only WG approval per `.github/CODEOWNERS`.
- **Co-reviews cross-cutting PRs.** Pull requests touching Core, governance, or another WG's directory require the affected owners' approval.
- **Files RFCs** when changes affect Core or cross multiple WGs, per [`rfcs/README.md`](rfcs/README.md).

## What a WG does NOT do

- **Modify Core unilaterally.** Core changes require Core-steward review and typically an RFC.
- **Define a duplicate of an existing Core leaf.** If a clinical Investigator is a `top:Person`, declare it `rdfs:subClassOf top:Person`. Don't mint a parallel class.
- **Define an entity that belongs in Core.** When two or more WGs need the same concept with the same shape, the concept belongs in Core. The WG that surfaces the need files an RFC to lift it into Core.
- **Make architectural decisions affecting multiple WGs without consultation.** Naming conventions, URI structure, cross-workflow relationship patterns — these are RFC-class decisions.

## Lifecycle

A WG progresses through five states. Movement between states is a governance event; the convener (or a quorum once one exists) makes the call.

### 1. Proposed

A new domain is on the radar but no formal WG exists. Anyone may propose a WG by filing an RFC. The proposal names the domain, identifies the initial maintainers, and explains the operational need.

The convener accepts or defers the proposal. Acceptance moves the WG to Forming.

### 2. Forming

The WG has acceptance but has not yet shipped artifacts. During this state:

- The WG's directory is created (e.g., `/clinical-research/`).
- A WG `README.md` documents intended scope and the initial maintainers.
- Early artifacts are authored under Core stewards' guidance.
- `.github/CODEOWNERS` still resolves to the convener; the WG team handle is registered but not yet active.

A WG stays in Forming until it has (a) shipped at least one stable release of its directory and (b) ratified its first RFC.

### 3. Active

The WG owns its directory. `.github/CODEOWNERS` resolves the WG's directory to the WG team. The WG reviews its own PRs, ships its own releases, and represents itself in cross-WG RFC discussions.

Active is the steady state. Most ongoing work happens here.

### 4. Mature

The WG's primary artifacts are stable. Changes are routine — incremental refinements, new sub-objects, cross-walk updates. Breaking changes are rare and well-telegraphed.

A WG reaches Mature by demonstrated cadence: a year or more of steady releases, no recent breaking changes, an active maintainer group.

### 5. Archived

The WG dissolves. Reasons vary — the domain merges with another, the operational need recedes, the maintainer group disbands. The directory may be frozen (read-only, kept for reference) or sunset (deprecation notice; removal scheduled).

Archived WGs do not block Core or other WGs. Their directory stays in the repo for historical reference unless explicitly removed.

## Membership and decision-making

Until working groups beyond Core Stewards exist, the convener is the review pool of one. As WGs form, the following conventions apply:

- A WG must name at least two maintainers before reaching Active state. This prevents single-maintainer collapse.
- Decisions inside a WG follow the WG's own conventions, declared in the WG's `README.md`.
- Decisions affecting Core or crossing WGs go through the RFC process. Two affirmative WGs (Core Stewards + the proposing WG) are the minimum for cross-cutting acceptance.
- The convener retains final authority over Core decisions until a Core stewards committee forms (a future ADR will record that transition).

## How a WG comes into being

1. Author an RFC under [`rfcs/`](rfcs/) proposing the WG. Use the template at [`rfcs/0000-template.md`](rfcs/0000-template.md).
2. The proposal names: the domain, the operational need, the initial maintainers (at least one, ideally two), the scope of artifacts the WG will own, and the relationship to Core.
3. The convener reviews. If accepted, the RFC is moved to `rfcs/accepted/` and the WG enters Forming state.
4. The WG creates its directory, drafts its `README.md`, and begins authoring artifacts.
5. When the WG ships its first stable release, the convener moves it to Active and reassigns its directory in `.github/CODEOWNERS`.

## How a WG dissolves

1. Maintainers (or the convener) propose archival via RFC.
2. RFC documents the reason, the disposition of the directory (frozen vs sunset), and any downstream impact.
3. After ratification, the directory is either frozen (CODEOWNERS keeps maintainers for read-only updates) or removed on a stated timeline.
