# First Principles, Illustrated

*Companion to [first-principles.md](first-principles.md). The canonical document states the nine principles; this one makes each concrete — the real-world challenge in plain English, how the industry does it today and why that hurts, and how TOP's approach is different. Examples point at artifacts you can open and run.*

> If `first-principles.md` is the law, this is the case law: the same rules, shown working against real operator problems.

---

## 1. The Inversion: Human-Down, not Standards-Up

**The challenge.** A clinical research coordinator finishing a patient visit knows exactly what happened: she enrolled a *participant*, ran a *visit*, collected *consent*. But the screen in front of her is shaped like the regulatory submission — it wants `USUBJID`, `ARMCD`, an `Encounter`. She spends her day translating her work into a database's language, and every translation is a chance to get it wrong.

**How it's done today, and why it hurts.** Most ontologies are built *standards-up*: the regulatory schema (SDTM, USDM, ISO 20022) dictates the data shape, and humans act as translators between their work and the database. The cost is permanent — training burden, transcription error, and a UX that fights the operator forever because the foundation itself is shaped like the standard, not the work.

**TOP's approach.** Invert the gravity. The foundation is shaped like the *work*; the standard becomes a *projection layer* emitted at the edge. Operators read and write `Participant`, `Visit`, `Site`; the Broker projects to SDTM/USDM/FHIR for the regulator. When the standard moves from v4 to v5, the projection changes and the foundation doesn't.

**See it.** [`taxonomy/taxonomy.ttl`](taxonomy/taxonomy.ttl) — the Core concepts are named for what entities *are* to a practitioner, not for any submission format; standards alignment lives in the crosswalks, not the foundation.

---

## 2. Naming from the Workday (the concrete inversion)

**The challenge.** A field labeled `USUBJID` means nothing to the nurse who filled it. A join-table entity called `ResearchSubjectProgressEntry` matches no moment in anyone's day. The people who *generate* the data can't read the model of it.

**How it's done today, and why it hurts.** Names are inherited from the database schema or the standard: `LOT_QTY_HEX`, `ARMCD`, `RelationalAuditMapping`. Sub-objects are modeled as database join tables rather than human milestones. The result is a model only a data engineer can navigate — and a permanent interpreter tax between the work and the system.

**TOP's approach.** Three naming rules, all from operator vocabulary: entities are what the person calls them (`Participant`, `Part`, `Trade`); attributes match what they say or type (`firstName`, `batchNumber`, `randomizationNumber`); sub-objects are workflow *milestones* (`InformedConsent`, `SafetyInspection`, `TradeConfirmation`), not relational plumbing. Standards are ephemeral — systems *project*, they don't *transform*.

**See it.** [`first-principles.md` § 2](first-principles.md) lists the Yes/No naming pairs; the [taxonomy](taxonomy/taxonomy.ttl) leaves follow them.

---

## 3. The Decision Rule: settling debates by operator reality

**The challenge.** A modeling debate stalls: the database "needs" a join entity, so someone proposes adding `RelationalAuditMapping` to Core. It's convenient for the store and invisible to every operator. Do you add it?

**How it's done today, and why it hurts.** Without an explicit tie-breaker, database convenience wins by default, and the model slowly fills with entities no human recognizes. Each one is a small betrayal of the inversion, and they compound.

**TOP's approach.** A three-test sequence anyone can run in a review: the **Verbal Test** (does an operator say this term out loud during their workday?), the **Boundary Test** (does it match a real workflow boundary?), and the **Origin Test** (am I shaping the foundation, or shaping a projection?). `RelationalAuditMapping` fails all three — so it's a projection-layer detail, not a Core entity.

**See it.** [`first-principles.md` § 3](first-principles.md); the rule is cited by name in spec PRs to keep Core honest.

---

## 4. Temporal & Provenance: native, not sidecars (bitemporal)

**The challenge.** A coordinator records a participant's weight as 80 kg. Five days later a monitor catches a transcription error — it was 85 kg — and corrects it. Months later an auditor asks two questions that *sound* identical but aren't: "What weight did the system show the day the dose was calculated?" and "What was the participant's *actual* weight that day?" The honest answers differ — 80 kg (what we knew) and 85 kg (what was true). Confuse them and you've either hidden an error or rewritten history.

**How it's done today, and why it hurts.** Most systems keep one current value and overwrite on correction; history lives in a separate audit-log table, reconstructed afterward by joining logs — if they captured it at all. The two timelines collapse into one timestamp or vanish, and every boundary crossing (EDC → warehouse → submission) drops the trail. Provenance becomes forensics.

**TOP's approach.** Two clocks, native: `observedAt` (when the system recorded it — transaction time) and `validFrom`/`validUntil` (when it was true — valid time). A correction never overwrites; it appends an immutable version (`prov:wasRevisionOf`) and closes the old one. Both auditor questions become a one-line query, not a reconstruction. And a signed or hashed value *cannot* be left mutable — SHACL refuses it — so the trail can't be silently broken.

**See it run.** [`core/v1/walkthroughs/consent-bitemporal.ttl`](core/v1/walkthroughs/consent-bitemporal.ttl) — a signed consent corrected through an append-only version chain. Validate it; try to mutate it; watch it fail closed. ([ADR-0021](governance/decision-log.md#adr-0021-bitemporal-model-valid-time-and-transaction-time-on-core).)

---

## 5. Specialization is Content, not Shape

**The challenge.** A platform supports oncology imaging studies, then cardiology studies, then a registry, then an animal study. Each "type" arrives as a request for a new entity class — `OncologyImagingStudy`, `ForexTradeRecord` — and within a year there are hundreds of bespoke shapes, no two systems agree, and a cross-study query has to know all of them to ask one question.

**How it's done today, and why it hurts.** Every operational variant becomes a new subtype *class*. The class hierarchy explodes, analytics fragment, and integration becomes an exercise in enumerating special cases. The shape of the data carries information that should have been content.

**TOP's approach.** One universal operational pattern — a universal `Activity` carrying a concept code that identifies the specialization. "Oncology imaging study" is an `Activity` with a code, not a new shape. The *content* (the code) varies; the *shape* stays uniform, so a query spans every variant without knowing any of them in advance. (Workflow extensions still specialize structurally via `subClassOf` where a real new category exists — but operational variety rides as coded content, not class sprawl.)

**See it.** `top:Activity` in [`core/v1/shapes.ttl`](core/v1/shapes.ttl), and the specialization discipline in [ADR-0009](governance/decision-log.md#adr-0009-specialization-pattern-workflow-concepts-extend-commons-primitives-via-subclassof).

---

## 6. Promote Facts to Entities: no bespoke flags

**The challenge.** A record carries `isConsented = true`. An auditor asks the only questions that matter: *who* said so, *when*, and *on what basis*? The boolean has no answer — it threw all three away the moment it was set. A true/false can't be trusted, signed, or corrected.

**How it's done today, and why it hurts.** Status and authority live as boolean flags scattered across records (`isSponsor`, `isClosed`, `isRestricted`). Each flag is a claim stripped of its authority, time, and reason — exactly the things a regulated audit needs. Reconstructing them later is guesswork.

**TOP's approach.** Every "is X" flag is a claim in disguise — so model the evidence, not the flag. An authority claim becomes an `Attestation` (signed, time-stamped, versioned); a state transition becomes a `StatusChange` (previous → new, with trigger); a rule becomes a `Constraint` (with severity and who enforces it). The fact now carries its own provenance and can be signed, queried as-of, and audited.

**See it.** The signed consent `Attestation` in [`consent-bitemporal.ttl`](core/v1/walkthroughs/consent-bitemporal.ttl); the `top:StatusChange` and `top:Constraint` leaves in [`shapes.ttl`](core/v1/shapes.ttl). ([ADR-0015](governance/decision-log.md#adr-0015-promote-facts-to-entities-no-bespoke-flags).)

---

## 7. Build the Pipeline in Order

**The challenge.** Two data feeds both send a "Subject." In one it's a human patient; in the other it's a laboratory animal. A team that jumped straight to building the knowledge graph merges them silently — and now the graph asserts things about people that are only true of animals. The error is invisible until it isn't.

**How it's done today, and why it hurts.** Teams skip the unglamorous early layers — controlled vocabulary, taxonomy — and model the ontology or graph first. Homonyms (*Subject*), false friends (*agent* in pharmacology vs. an acting `Agent`), and missing crosswalks surface in production, where they're expensive and dangerous to fix.

**TOP's approach.** Six layers, in order, each the precondition for the next: Controlled Vocabulary → Taxonomy → Metadata Schema → Thesaurus → Ontology → Knowledge Graph. The CV layer carries three obligations that prevent exactly the disaster above: context routing for homonyms (*Subject* → `Person` in human research, `Organism` in animal research), anti-synonyms for false friends, and SSSOM crosswalks as first-class artifacts.

**See it.** [ADR-0018](governance/decision-log.md#adr-0018-adopt-the-six-stage-ontology-pipeline-as-tops-build-discipline) (the pipeline) and [ADR-0020](governance/decision-log.md#adr-0020-add-toporganism-as-the-fifth-agent-leaf) (the *Subject* homonym resolved with `top:Organism`).

---

## 8. Open Core, Constrained Extension

**The challenge.** Two CROs both extend `Document` for their needs. One adds a `signatories` list; the other redefines what `Document` requires entirely. Now the "same" concept means two incompatible things, an AI agent trained on one can't read the other, and nobody can safely reuse either extension. This is the FHIR drift story, lived again.

**How it's done today, and why it hurts.** Standards are extensible but un-contracted: anyone can extend any concept any way. Over a decade the same logical concept gets modeled multiple incompatible ways, extensions proliferate without discoverability, and profiles diverge. It's nobody's fault — it's what an unspecified extension surface produces.

**TOP's approach.** The Core is open to *extension* but closed to *redefinition*, enforced per-property by a flavor declared in the artifact and machine-checked at PR time: **Invariant** (cannot drift — e.g., `identifier`, `observedAt`), **Tightenable** (consumers may require/narrow but not loosen — e.g., `status`), **Additive** (designed for downstream addition). Extensions live in the consumer's namespace and chain to Core via `subClassOf` / `subPropertyOf`. Two extensions of `Document` stay mutually intelligible by construction.

**See it.** The `top:flavor` annotations in [`core/v1/shapes.ttl`](core/v1/shapes.ttl), [ADR-0019](governance/decision-log.md#adr-0019-open-core-constrained-extension-three-flavors-per-core-property), and [`governance/extension-contract.md`](governance/extension-contract.md).

---

## 9. Why Human-Centered Wins

**The challenge.** A sponsor employs a small army of data managers whose entire job is reshaping operator-generated data into submission formats. The work is expensive, slow, error-prone, and adds no clinical value — it exists only because the foundation was built for the regulator instead of the work.

**How it's done today, and why it hurts.** Standards-up systems push the complexity onto people. Compliance headcount scales with data volume, and the translation layer is a permanent tax. Worse, it's structural: an incumbent who built standards-up cannot rebuild around the human without discarding their entire data model.

**TOP's approach.** TOP eats the complexity so operators don't have to: humans work in their own vocabulary, and the foundation handles the logic and the projection to standards at the edge. The advantage compounds — anyone anchored standards-up starts from behind, because they'd have to throw away their model to catch up. TOP starts at the finish line.

**See it.** This is the cumulative payoff of principles 1–8; the [README](README.md) frames the problem and the [manifesto](manifesto.html) the stance.

---

*Apache License 2.0. Examples reference artifacts in this repository; open them and run the validations to see the principle hold.*
