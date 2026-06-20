# Related work: the First Principles Framework (FPF), and what TOP should harvest

*Status: pre-RFC strategic planning. Author: Bo Lora (BDFL), with AI-agent assistance. Audience: Bo, future working-group leads, anyone evaluating whether to borrow from FPF.*

*Companion to [composition-projection-provenance.md](composition-projection-provenance.md), [first-principles.md](../../first-principles.md), and the decision log.*

> **Source caveat.** This analysis is based on a *summary* of the FPF specification ([github.com/ailev/FPF](https://github.com/ailev/FPF)), not a line-by-line read of the full spec. Section identifiers (A.6.3, A.14, B.3, …) and quoted phrases are as summarized; verify against the source before any of it is treated as settled. FPF is authored by Anatoly Levenchuk with AI-agent assistance.

---

## What FPF is

FPF (First Principles Framework) is a "standards-style pattern language for turning difficult engineering, research, management, and mixed human/AI work into explicit, reviewable, improvable reasoning." By its own statement it does **not** aim to catalog reality (a descriptive ontology) but to **orchestrate thought** — auditability, evolvability, falsifiability of reasoning across people, tools, time, and AI agents.

That is a different altitude from TOP, and the difference is the whole point of this note.

| | FPF | TOP |
| --- | --- | --- |
| Kind | meta-framework for reasoning / work-coherence | reference (descriptive) ontology for regulated data |
| Altitude | abstract, methodological | concrete, instantiable |
| Audience | systems thinkers, methodologists | operators / practitioners |
| Size | maximal (Parts A–E, dozens of CALs/mechanisms) | minimal (1 root, 8 categories, 29 leaves) |
| Root | `U.Holon` (part-whole unit) made load-bearing | `top:CommonEntity` + Universal DNA; "holon" not a keyword |

Note the naming collision: both projects use the phrase "first principles," but TOP's `first-principles.md` is a short set of *design rules for a reference ontology*, while FPF *is* an extensive reasoning architecture. Different things; worth stating so nobody conflates them.

## Convergences (FPF independently arrived at our composition/projection thread)

Several ideas TOP derived bottom-up are first-class named primitives in FPF. This is reassuring — a rigorous independent framework converged on the same shapes:

- **Holon as part-whole root** (`U.Holon`) — the whole/part structure behind our entity-composition discussion.
- **Projection, formalized** — `A.6.3 Epistemic Viewing`: "EntityOfConcern-preserving, effect-free projection… `entityOfConcernRef` stays fixed," and `E.17 MVPK`: "views are projections, not alternative facts." This is our fit-for-purpose-projection-without-forking, stated more rigorously.
- **Boundary crossing with explicit loss** — `A.6.4 Epistemic Retargeting` + Bridges / Congruence Levels: changing the referent requires an explicit bridge and **loss accounting**. This is our federation caveat (provenance-carrying signed projection; declare what does not transfer).
- **Strict thing-vs-description** — `EntityOfConcern ≠ Description episteme`; epistemes bear claims but do not act.
- **Fail-closed tri-state** (pass | degrade | abstain) — the generalized form of our Tier-1 "fail-closed at ingestion."

## What TOP should harvest (specific tools, not the apparatus)

Three FPF ideas sharpen known TOP gaps. Take the tools; leave the alphabet.

### The mereology fork (the immediately actionable one)

FPF's `A.14 Advanced Mereology` distinguishes four part-of relations. Mapped against TOP's current coverage:

| FPF relation | Meaning | TOP today | Verdict |
| --- | --- | --- | --- |
| **MemberOf** | set membership | `top:memberOf` (Agent→Agent only); `prov:hadMember` (via Collection, per ADR-0021) | **covered** for aggregation; `memberOf` is narrowly Agent-scoped by design |
| **PhaseOf** | temporal phase of a process | `precededBy` (sequence) + `containsActivity` (Scope→Temporal) | **partially covered**; no explicit "phase-of-this-process" whole relation |
| **ComponentOf** | functional part of a system | — | **gap**: no Resource/System component-of in Core |
| **PortionOf** | material portion of a substance | — | **gap**: no Material portion-of (aliquots!) in Core |

The blood draw exposes the gaps concretely: an **aliquot** is a `PortionOf` a specimen, and a **kit** has `ComponentOf` parts. Neither has a clean Core relation today; aggregation (`prov:hadMember`), spatial containment (`withinLocation`), and origin (`prov:wasGeneratedBy`) cover most cases but not portions or functional components.

**Recommendation (consistent with keep-Core-small, ADR-0019, and the FIWARE lesson):**

1. **Do not import all four relations.** That is FPF's altitude, not TOP's.
2. **Let the clinical-research lighthouse force the need.** `PortionOf` (aliquots, sample splits) is the most likely genuine requirement; `ComponentOf` (kits, instrument assemblies) second. If the extension demonstrably needs them across more than one domain, *then* evaluate promoting a single, well-flavored Core relation — using FPF's typology as the design vocabulary — rather than a speculative four-way mereology.
3. **Anchor any future part-whole to BFO.** TOP now carries light-edge BFO leaf alignment (the completed BFO work), and BFO 2020 has formal mereology (`continuant part of` / `has continuant part`, `occurrent part of`). A future `top:partOf` could align there for OBO interop, keeping the edge light.

### Bridge + Congruence Level / loss accounting

FPF's `Bridges` with `CL` (Congruence Level) penalties make cross-context mapping loss *explicit and first-class*. TOP already has the seed: `skos:exactMatch` vs `skos:closeMatch` in the PROV-O / schema.org crosswalks is a two-level congruence signal. **Harvest:** when TOP projects to or ingests peer ontologies (FHIR, USDM, SDTM), declare the bridge and the loss rather than pretending the mapping is lossless. This is directly relevant to the Broker/projection layer named in ADR-0021's ingestion-edge cost.

### F–G–R trust grading

FPF's `B.3 Trust & Assurance Calculus` grades claims on Formality, Scope, and Reliability. TOP's Evidence category carries traceability (`integrityHash`, `signedBy`, `verifiesOutcome`) but no graded *assurance*. **Harvest (later):** a possible future *assurance* extension over the Evidence category — "how much do we trust this claim, and on what warrant" — layered on top of, not inside, Core.

## Deliberate divergences (where TOP should *not* follow FPF)

- **Agent as type vs. agency as role.** FPF refuses a universal `U.Agent`; agency is a graded contextual role (`Holder#Role:Context`), substrate-neutral across human/AI. TOP does the opposite: `top:Agent` is an L2 category with leaves (Person, Organization, Group, AutonomousAgent, Organism), aligned to `prov:Agent`. TOP's choice is practitioner-grounded (operators name *the person*, *the system*); FPF's is rigorous-abstract. Keep TOP's — but the role-vs-type tension is real and is the same one behind ADR-0020; a future "role" concept in workflow extensions can recover much of FPF's flexibility without retyping Core.
- **Altitude and size.** FPF is maximal and methodological. Adopting its altitude would betray TOP's central bet (small, concrete, practitioner-first) and walk into the mirror-image of the FIWARE failure — *too abstract, nobody instantiates*. Mine it; do not merge it.
- **"Holon" as a load-bearing word.** FPF makes it the kernel root. TOP keeps it as credited lineage only (its audience will not learn a philosophy to read a spec).

## Positioning: complementary layers, not competitors

The honest framing: TOP is precisely the kind of *descriptive ontology* FPF contrasts itself with — which means TOP could sit **inside an FPF bounded context** as the domain vocabulary, while FPF's reasoning/assurance discipline wraps TOP data. They are different layers of the same stack, not rivals. We do not need to take a position for or against FPF to borrow its three sharp tools.

## Recommendation summary

1. **Cite FPF as prior art** for projection/viewing and bridge/CL — more rigorous language than the holon framing for those points.
2. **Track the mereology fork** as the live decision; resolve it from the clinical-research lighthouse, anchored to BFO, not by importing FPF's four relations.
3. **Bank** bridge/CL loss-accounting (for peer-ontology projection) and F–G–R assurance grading (a future Evidence extension) as candidate harvests.
4. **Hold the line** on agent-as-type, minimal Core, and operator-plain naming.

## Status

Proposed planning note. Nothing binding. Based on a spec summary; verify FPF specifics against the source before acting on any harvest.
