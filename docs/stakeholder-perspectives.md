# TOP Clinical Research Reference Graph — Stakeholder Perspectives

*A tour of the project through the eyes of the people who would use, fund, or be affected by it. Written June 2026 at the close of the v1 CR-domain milestone.*

---

## What the project is, in one paragraph

TOP (The Ontology Project) is a reference knowledge graph for the clinical research lifecycle. It defines a shared vocabulary — OWL classes, SHACL validation rules, and NGSI-LD runtime entities — that lets systems from different vendors talk to each other without a human translator in the middle. The first domain is oncology clinical trials, Pre-IND through End-of-Phase 2. The reference runtime is a community deployment on AWS Garnet (Scorpio NGSI-LD context broker), ingestible from USDM v4 protocols, Medidata/Veeva EDC exports, and Kafka streams. The LY900018 nasal glucagon trial is the worked example.

---

## 1. Oncologist / Principal Investigator

**What they see when they look at the graph:**  
A model that represents their world more faithfully than any EDC they have ever used. The trial protocol is not a PDF buried in a TMF — it is a live knowledge object with versioned eligibility criteria, a schedule of assessments linked to each visit, and a bitemporal audit trail of every amendment. The subject they enrolled last Tuesday is a `cr:StudySubject` linked to a `cr:Enrollment` act, not a row in a spreadsheet.

**Pros:**
- Protocol amendments are not "a new PDF replaces the old one." They are new `cr:ProtocolVersion` nodes with `validFrom` timestamps, so the question *"which protocol was in force when subject 007 had their Week 4 visit?"* is answerable in a single graph query rather than a document archaeology exercise.
- Dose-limiting toxicity (`cr:DoseLimitingToxicity`) is a first-class entity in the ontology, linked to the dose decision that follows — the connection between a DLT event and a cohort dose recommendation is explicit, not implied.
- The delegation invariant: every clinical act (assessment, administration, consent) links to the `cr:Delegation` that authorized it. A PI can, for the first time, answer *"who performed that procedure, under what authority, with what training on record?"* without emailing the CRO.

**Cons / Gaps:**
- There is no concept of a *patient outcome* beyond `hcls:Observation` and `cr:AdverseEvent`. Response criteria (RECIST, iRECIST, Lugano), progression-free survival, overall survival — these are not in the current model. Oncology-specific efficacy endpoints are unmodeled.
- The `cr:Assessment` class exists but has no properties yet. What was assessed, with what instrument, at what result, graded by what scale (CTCAE, NCI-CTEP) — all absent.
- There is nothing yet for the *clinical reasoning* layer: why a subject was taken off study, what triggered the stopping rule, what the DSMB reviewed. The graph captures *that* things happened, not *why* decisions were made (except for site selection decisions, which are a notable exception).

**Wishlist:**
- CTCAE grade as a codified property on `cr:AdverseEvent`, linked to the NCI Thesaurus IRI.
- `cr:DoseDecision` — the formal cohort dose recommendation that follows DLT review, linking to the DLT events and the DSMB meeting that produced it.
- A `cr:ResponseAssessment` class with RECIST 1.1 coded outcomes, linked to the imaging visit.
- Stopping rule trigger as a computable event: when `cr:StoppingRule` fires, the graph should record *what threshold was crossed*, not just that the rule exists.

---

## 2. Pharma Sponsor Data Manager / Clinical Data Manager

**What they see when they look at the graph:**  
A potential end to the "field mapping meeting." Today, reconciling Medidata fields against SDTM variables against USDM data elements is a manual, meeting-heavy, error-prone process that happens on every study. This project proposes that the mapping is a *first-class artifact* (`cx:Mapping`) with a confidence score, a provenance trail, and LLM-assisted inference for sponsor-specific extensions (`cr:OperationalRecord`). That is a genuine productivity offer.

**Pros:**
- The crosswalk layer (`cr-to-external.ttl`, `usdm-to-cr.ttl`) is owned, provenance-tagged, and SSSOM-compatible. Mappings carry `cx:verificationStatus`, `cx:confidence`, `cx:mappingMethod`, and a `cx:reviewStatus` lifecycle. This is not a spreadsheet that lives on someone's desktop.
- `cr:OperationalRecord` is the right abstraction for the `X_WHATEVER` problem — sponsor-specific CRF fields that have no CDISC home. Modeling them as entities with a `cx:mappingConfidence` score, pending human confirmation, is a pragmatic and honest solution.
- The USDM v4 → NGSI-LD transformer (LY900018 worked example) demonstrates that 102 entities can be extracted from a real protocol JSON with no manual intervention. That is the first step toward automated SDTM domain derivation from the protocol rather than from post-hoc mapping meetings.
- Bitemporality on `cr:Enrollment` means the question *"was this subject enrolled when this data was collected?"* is answerable without joining three tables.

**Cons / Gaps:**
- The SDTM projection layer is described in documentation but mostly unbuilt. There are SPARQL projection stubs, but no working `DM`, `AE`, `LB`, or `VS` domain queries that produce submission-ready datasets from the graph.
- There is no `cr:CRFField` concept — the bridge between an `hcls:Observation` (what was collected) and the eCRF question that collected it. The EDC-to-graph path is partially modeled in `cr:eCRF` but the field-level mapping is not.
- Medidata/Veeva-specific vocabulary is referenced but not modeled. The `cr:OperationalRecord` concept acknowledges the problem without solving the integration.
- Define-XML generation from the graph is not addressed. A sponsor's submission package requires Define-XML 2.1; the graph has the ingredients but no export path.

**Wishlist:**
- Working SPARQL projections for at least the `DM`, `AE`, and `EX` SDTM domains — even if only for the LY900018 fixture.
- A `cr:CRFField` → `hcls:Observation` mapping class that makes the eCRF-to-graph bridge explicit.
- A Define-XML 2.1 export script analogous to the NGSI-LD transformer.
- Codelist binding: `cr:EligibilityCriterion.criterionCategory` should bind to the CDISC CT `INCEXCC` codelist by IRI, not just a free string.

---

## 3. CRO Operations Lead / Study Project Manager

**What they see when they look at the graph:**  
The site lifecycle state machine is the first thing that catches their eye. They have managed spreadsheets of site statuses for 15 years. Seeing `cr:SiteStatusFeasibility`, `cr:SiteStatusReserve`, `cr:SiteStatusDropped` as named individuals — not strings in a CTMS — with a `cr:SiteSelectionDecision` class that *mandates capturing why a site was dropped* — that is institutional memory being modeled as data rather than lost in someone's email archive.

**Pros:**
- The site lifecycle (`Feasibility → Selected → Startup → Active → Closed`, with `Reserve` and `Dropped` branches) mirrors reality. The state machine is clean and the transition logic is explicit in the comments.
- `cr:SiteSelectionDecision.decisionRationale` is marked mandatory for Dropped and Reserve outcomes. This is the first time, in any data standard, that the *reason a site was not selected* is treated as a required field. In practice this institutional intelligence is almost never captured; making it mandatory in the model is a meaningful forcing function.
- The `cr:Delegation` class with `cr:delegator`, `cr:delegate`, `cr:delegatedCapability`, `cr:requiresCredential` maps directly to the DOA log — the document CROs produce and monitors review. For the first time the DOA is a queryable graph rather than a PDF.
- The `cr:Credential` link from `cr:Delegation` means training gaps are surfaceable by query: *"show me all active delegations where the delegate's GCP certificate expired."*

**Cons / Gaps:**
- Site performance metrics are absent. Enrollment rate, screen failure rate, protocol deviation rate, data query rate per site — the KPIs a PM lives by are not modeled. `cr:OperationalRecord` could house them, but no schema exists.
- The `cr:RegulatoryInteraction` class (Pre-IND meeting, EOP2) exists but has no properties. Meeting date, agency, meeting type, outcome — all unmodeled.
- There is no concept of a *monitoring visit* (`cr:MonitoringVisit` would be a natural `cr:Visit` subclass) or a *monitoring finding/observation*. Remote monitoring and risk-based quality management (RBQM) are described in the documentation but not reflected in the ontology.
- No timeline or milestone layer. `top:Milestone` exists in TOP Core, but there is no `cr:StudyMilestone` with milestone type codes (FPI, LPLV, DBL, submission) or a plan-vs-actual deviation property.

**Wishlist:**
- `cr:SiteMetrics` — a periodic snapshot of key performance indicators per site, linked to the `cr:StudySite` and time-stamped. Even five KPIs (screen fail rate, enrollment rate, query rate, days-to-resolve, deviation rate) would enable sponsor oversight graphs.
- `cr:MonitoringVisit` as a `cr:Visit` subclass with a `cr:MonitoringFinding` outcome class.
- `cr:StudyMilestone` with codified milestone types and a `top:variance` linking planned vs. actual date.
- A `cr:RegulatoryInteraction` shape that requires date, agency IRI, and meeting type.

---

## 4. Regulatory Affairs Specialist

**What they see when they look at the graph:**  
A vocabulary that takes regulatory standards seriously. `cr:ICH_E6_R3`, `cr:ICH_E9_R1`, `cr:CFR_21_Part_11`, `cr:EU_CTR_536_2014` are named individuals — not strings. A `cr:Study` can declare which regulatory frameworks govern it via `top:governedBy`, and SHACL shapes can be scoped to apply only under specific jurisdictions. The `cr:BriefingBook` and `cr:CSR` classes acknowledge that regulatory artifacts are first-class entities, not just PDF attachments.

**Pros:**
- The connection between `cr:Delegation`, `cr:Credential`, and `cr:Capability` means ICH E6(R3) Section 5.2.1 (delegation of investigator responsibilities) is directly computable. An auditor can query *"show me all consents obtained, the persons who obtained them, and their valid consent delegation at the time"* — and get an answer from the graph without opening a binder.
- The `top:integrityHash` and `top:signedBy` on `top:Evidence`, combined with the bitemporal SHACL rule that signed/hashed values *must* be `top:Versioned`, directly addresses 21 CFR Part 11 immutability requirements. The model enforces that you cannot sign a value and then mutate it.
- ICH E6(R3)'s shift to risk-based approaches is partially addressed: `cr:StoppingRule` and `cr:EligibilityCriterion` as computable constraints, and the RBQM documentation page.
- The regulatory law individuals (`cr:ICH_E6_R3`, etc.) as `top:RegulatoryLaw` individuals means a SPARQL query can return *"all SHACL violations for studies operating under CFR 21 Part 312"* — jurisdiction-aware validation.

**Cons / Gaps:**
- No 21 CFR Part 312 IND structure. The IND itself — the submission unit, the application number, the Investigational New Drug application as a formal entity — is absent. `cr:RegulatoryInteraction` exists but the IND is not modeled as a `top:Scope` or `top:Evidence` subclass.
- There is no concept of a *protocol deviation* vs. a *protocol violation* as distinct classes. The documentation mentions them; the ontology has no `cr:ProtocolDeviation` class with a severity, causality, or corrective action link.
- MedDRA is listed as a "standards projection target" in the ontology header comment but has no crosswalk. `cr:AdverseEvent` is mapped to OAE but not to MedDRA LLT/PT/SOC codes.
- EU CTR submission structure (Article 25 dossier, CTA) is not modeled beyond the regulatory law individual.

**Wishlist:**
- `cr:ProtocolDeviation` as a `top:Outcome` subclass, with severity (`minor`/`major`), discovery date, root cause, and `cr:CAPA` (corrective and preventive action) linked.
- A MedDRA crosswalk: `cr:AdverseEvent` → MedDRA PT (at minimum), with coded term IRI and dictionary version as provenance.
- `cr:IND` as a `top:Evidence` subclass with application number, sponsor IRI, submission date, and `cr:Sponsor` link.
- `cr:SafetyReport` (SUSAR / SAE expedited report) as a `cr:AdverseEvent` subclass with regulatory authority, submission date, and `cr:ICH_E2A` governance link.

---

## 5. Knowledge Engineer / Ontologist

**What they see when they look at the graph:**  
A well-architected upper ontology instantiation. The three-layer stack (TOP Core → HCLS Core → CR domain) is clean. The BFO alignment is light-edge and honest (no category has a BFO peer unless one genuinely fits). The PROV-O alignment is structurally correct: Activities are `prov:Activity`, Agents are `prov:Agent`, Evidence is `prov:Entity`. The bitemporal model (transaction time via `top:observedAt`, valid time via `top:validFrom`/`top:validUntil` on `top:Versioned`) correctly separates the two clocks. The `owl:imports` aggregator pattern for the core module split is sound.

**Pros:**
- The Universal DNA pattern (`top:identifier`, `top:observedAt`, `top:status` enforced by `top:UniversalDNAShape`) is a principled minimum that every entity must satisfy. It is the right grain — not so much that it burdens simple entities, not so little that graphs cannot join.
- The flavor annotation (`top:flavor "Invariant"/"Tightenable"/"Additive"`) is an elegant extension contract. Downstream ontologies know what they can tighten vs. redefine.
- The SSSOM-compatible crosswalk approach, with `cx:verificationStatus` distinguishing verified-against-source-IRI from speculative, is methodologically sound.
- NGSI-LD's `@context` is generated from the OWL model (not hand-authored), and ObjectProperty terms correctly emit `@type: @id` for relationship semantics. This is non-trivial to get right and it is done correctly.
- The SHACL Tier-1 entailment (signed/hashed values must be `top:Versioned`) is an elegant automatic promotion mechanism.

**Cons / Gaps:**
- `top:CommonEntity` is a bare OWL class with no `owl:Ontology` IRI in the module files. The aggregator carries the ontology declaration, but individual modules are not self-declaring. A consuming tool that loads only `top-agent.ttl` gets no `owl:Ontology` triple.
- The `top:Versioned` pattern uses `prov:specializationOf` for stable identity, but there is no `cr:StableIdentity` or `cr:VersionSeries` class to represent the identity root. The pattern is described in comments but not enforced by a SHACL shape that checks `prov:specializationOf` points to a correctly typed node.
- The crosswalk vocabulary (`cx:`) is defined in `crosswalk-vocab.ttl` but is not published as a separate `cx:` ontology with its own IRI. It is effectively a private vocabulary without a dereferencing namespace.
- No `owl:disjointWith` axioms anywhere. The categories (Agent, Location, Resource, etc.) are intended to be disjoint, but this is stated in comments rather than computable axioms.
- The `top:Organism` class (`rdfs:subClassOf prov:Agent`) is philosophically unusual — organisms are not agents in most upper ontologies (BFO, DOLCE). The rationale (laboratory animals "act" in an operational context) is understandable but will cause alignment friction with BFO's `IndependentContinuant` for organisms.

**Wishlist:**
- `owl:disjointWith` axioms between the eight L2 categories, enforced by a SHACL `sh:disjoint` constraint.
- A `top:VersionSeries` class as the stable identity root for `top:Versioned` nodes, with `prov:specializationOf` range pinned to `top:VersionSeries`.
- Self-declaring module files: each `top-*.ttl` should carry its own minimal `owl:Ontology` triple (`<https://top.scientix.ai/core/v1/modules/top-agent> a owl:Ontology ; owl:imports <https://top.scientix.ai/core/v1/modules/top-root> .`).
- A published `cx:` ontology at `https://top.scientix.ai/crosswalk/v1` with its own `owl:Ontology` declaration and SSSOM alignment.

---

## 6. Clinical Research Coordinator (CRC) / Site Staff

**What they see when they look at the graph:**  
Honestly? Very little directly. This is infrastructure that lives above the EDC. A CRC enters data into Medidata or Castor; this graph is what the sponsor's data warehouse sees after the fact. The immediate operational impact is indirect — better-structured data upstream should mean fewer queries and cleaner audit trails downstream.

**The indirect impact that matters to them:**
- If the delegation model is implemented at a site, the DOA log becomes a live query rather than a binder section. *"Am I authorized to obtain consent today, and is my GCP certificate current?"* becomes answerable in seconds rather than requiring a coordinator to find the latest binder version.
- The site lifecycle model (`cr:SiteStatusStartup`, `cr:SiteStatusActive`) means startup milestones (SIV, first subject enrolled) are events in the graph that the sponsor can see without the CRC manually updating a CTMS.
- `cr:StudySubject` carries no PII. The graph is safe to expose to monitoring systems without HIPAA exposure.

**Honest cons:**
- No UI. This is a knowledge graph, not a software product. A CRC will never directly interact with Turtle files or SPARQL queries.
- The model assumes a well-structured EDC export. In practice, sites often operate on paper CRFs or legacy EDC versions that produce messy exports. The transformer assumes clean USDM JSON; reality is messier.

---

## 7. Software / Data Engineer Building on This

**What they see when they look at the graph:**  
A well-specified integration contract with real artifacts they can use today: a Turtle bundle, a JSON-LD context file, a SHACL shapes bundle, a working Python transformer for USDM v4, and example NGSI-LD entity payloads. The SHA256SUMS checksum file means they can pin a release version without trusting a URL.

**Pros:**
- The NGSI-LD context (`top-cr-v1.ngsi-context.jsonld`) is machine-generated from the OWL model. ObjectProperty terms have `@type: @id`. This is immediately useful for any Scorpio/Orion-LD deployment.
- The `urn:ngsi-ld:top-cr:{Type}:{localId}` URN scheme is idempotent — the same study produces the same URNs across runs, enabling safe upsert.
- The transformer (`examples/usdm/to-ngsi-ld.py`) is a clear, readable reference implementation. It is not a framework; it is a script you can read in an hour and adapt.
- The three-format distribution (Turtle, JSON-LD, N-Triples) with byte-reproducible serialization (canonical blank nodes, sorted N-Triples) means CI can detect accidental model changes via checksum diffs.
- The Python build chain (`build_dist.py`, `build_docs.py`) is self-contained, dependency-light (rdflib, pyshacl), and deterministic.

**Cons / Gaps:**
- No versioning strategy beyond `v1`. There is no `owl:versionIRI` evolution path, no deprecation policy, no `owl:deprecated` pattern. When `cr:Assessment` gains properties in v2, consuming systems have no migration path.
- The NGSI-LD transformer does not post to a broker — it writes JSON files. There is no `POST`/`PATCH` script that actually exercises a live Scorpio instance.
- No test harness for the transformer output. The LY900018 JSON produces 102 entities, but there is no assertion that the SHACL shapes validate them, or that a Scorpio broker accepts them.
- The `cx:mappingConfidence` and LLM inference workflow (`cx:inferredBy` pointing to `top:AutonomousAgent`) is modeled but has no implementation. There is no LLM integration, no inference pipeline, no review workflow UI.
- The two ingestion modes (bulk catch-up via Veeva DDA, live streaming via Kafka/Castor) are described in documentation but neither is implemented.

**Wishlist:**
- A `scripts/post-to-broker.sh` that posts the transformer output to a local Scorpio instance with proper `Link:` header and checks the HTTP 201 responses.
- A `tests/validate-transformer-output.py` that loads the example NGSI-LD files into rdflib and runs the SHACL shapes against them.
- A versioning ADR that specifies the `v1` → `v2` migration pattern: which IRIs are stable, what `owl:deprecated` looks like, how consumers detect a breaking change.
- A `docker-compose.yml` that spins up Scorpio + the NGSI-LD context endpoint locally, for integration testing.

---

## 8. Chief Medical Officer / Sponsor Executive

**What they see when they look at the graph:**  
A long-term infrastructure bet. Not a product that solves next quarter's problem, but a platform that, if adopted, would let a sponsor answer in minutes questions that today require a data-science sprint: *"Across our last five oncology studies, what was the median time from site selection to first patient in, and which site characteristics predicted it?"*

**The strategic value:**
- The `cr:SiteSelectionDecision` with mandatory rationale for rejected sites is worth more than it sounds. A sponsor that captures *why* Site X in Tokyo was dropped from Study A can use that data when qualifying sites for Study B. Today, that institutional knowledge lives in a project manager's head.
- The crosswalk layer — mapping TOP entities to CDISC SDTM/CDASH/USDM, OBI, MedDRA — means the graph is not a silo. It can feed a submission, a regulatory authority portal, or an academic data-sharing repository without re-coding.
- Bitemporality across all versioned entities means a CMO can ask *"what was the safety profile of this compound as we understood it at the time of the EOP2 meeting?"* — a question that is legally important and currently very hard to answer.
- The three-layer model (OWL spec → SHACL validation → NGSI-LD runtime) separates concerns cleanly. The ontology does not require a specific vendor; a sponsor can run it on AWS Garnet today and migrate to a different broker tomorrow.

**Honest concerns:**
- **Adoption friction is high.** This requires CROs to structure their data exports in a way that feeds a graph. Today, CROs are incentivized to keep data in their own systems. There is no business model here for a CRO to participate.
- **The regulatory path is unclear.** A submission that references a knowledge graph rather than a Define-XML flat file would need FDA agreement. The graph could generate Define-XML 2.1, but that path is not built.
- **The community runtime is not production-ready.** AWS Garnet is a CDK reference architecture, not a validated GCP system. Running clinical trial data through it would require the sponsor to validate it under 21 CFR Part 11 — a multi-month effort not addressed here.
- **Data governance.** The `cr:Enrollment` bridge between `hcls:Person` (PII) and `cr:StudySubject` (pseudonymous) is elegantly modeled, but the operational question of who controls the keychain — and under what DUA — is not addressed.

---

## Summary grid

| Stakeholder | Most valuable thing here | Biggest gap | Adoption blocker |
|---|---|---|---|
| Oncologist / PI | Bitemporal protocol versions; delegation audit trail | No CTCAE-coded AE properties; no response criteria | No UI; data enters via EDC, not the graph |
| CDM / Data Manager | LLM-assisted field mapping model; USDM transformer | No working SDTM projection; no Define-XML export | CRO data not structured for graph ingest |
| CRO Ops / PM | Site lifecycle state machine; mandatory site-drop rationale | No site performance KPIs; no monitoring visit model | CRO has no incentive to feed external graph |
| Regulatory Affairs | Jurisdiction-aware SHACL; 21 CFR Part 11 baked into shapes | No MedDRA crosswalk; no IND structure; no protocol deviation class | Not a validated GCP system yet |
| Knowledge Engineer | Clean upper-ontology alignment; SSSOM crosswalks; NGSI-LD context | No disjointness axioms; no self-declaring modules; `cx:` not published | Low — this layer is the audience |
| CRC / Site Staff | Delegation queryability; no PII in the graph | No site-facing interface | Not their system; indirect benefit only |
| Software Engineer | Idempotent URN scheme; working transformer; deterministic builds | No live-broker test; no versioning strategy; no LLM pipeline | Needs Scorpio + SHACL integration test |
| CMO / Executive | Cross-study institutional learning; regulatory framework IRIs | Adoption friction; no GxP validation; no data governance model | Requires CRO buy-in; regulatory pathway unclear |

---

## What this is, honestly

This is a **design-time specification and integration contract**, not yet an operational system. It is the kind of artifact that, in a large sponsor, would be produced by an Architecture Review Board and then handed to vendors to implement against. The ontology is mature. The crosswalks are honest. The transformer is a proof-of-concept. The runtime is a reference architecture.

The gap between *this* and *a running system processing real trial data* is: (a) one validated GxP deployment, (b) one CRO willing to export in USDM format, and (c) one sponsor data engineering team willing to run the ingestion pipeline. None of those are ontology problems.

*Generated from the TOP CR domain v1 branch, commit f6f3d50, June 2026.*
