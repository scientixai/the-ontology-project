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

## 9. Software Development Engineer

**What they see when they look at the graph:**
A well-specified API contract with working artifacts, but still a long way from something they can ship. An SDE's job is to build applications users interact with. The graph defines what data exists and how it relates; what is missing is the application layer on top of it — authentication, authorization, API endpoints, client libraries, error handling, rate limiting, pagination. The NGSI-LD broker provides a REST API, but that is an infrastructure API, not a product API.

**Pros:**
- The URN scheme (`urn:ngsi-ld:top-cr:{Type}:{localId}`) is stable, predictable, and works as a primary key in any database or cache layer. Building a REST API that wraps entity lookups is straightforward.
- The NGSI-LD broker's standard API (`GET /ngsi-ld/v1/entities/{id}`, `GET /ngsi-ld/v1/entities?type=cr:Study&q=...`) means any SDE can build a service layer without learning SPARQL. The query language is REST parameter-based, not graph-native.
- The JSON-LD output from Scorpio is valid JSON. Any frontend that can consume JSON can consume this — no RDF parsing library needed on the client.
- The Python transformer (`to-ngsi-ld.py`) is a readable reference for how to translate domain objects into the entity model. An SDE can port it to TypeScript/Java/Go in a day.
- The three-format distribution (Turtle, JSON-LD, N-Triples) is useful for testing: load the N-Triples into a test fixture, run assertions against entity structure without spinning up a broker.

**Cons / Gaps:**
- There is no client SDK. Every consuming application has to re-implement the `@context` resolution, the NGSI-LD Property/Relationship node structure, and the URN construction logic. The transformer shows the pattern once; it should be a library.
- The `@context` URL (`https://top.scientix.ai/cr/v1.ngsi-context.jsonld`) is referenced in every entity but has no production host. In development this silently fails `@context` resolution; in production, an outage of the context host breaks all entity serialization.
- No pagination model for large entity collections. A `GET /ngsi-ld/v1/entities?type=cr:EligibilityCriterion` on a large study might return thousands of entities. The NGSI-LD spec has pagination (`count`, `offset`, `limit`) but nothing in this project documents expected cardinalities or page size guidance.
- No authentication layer is modeled or documented. Who can read entity X? Who can write it? The graph has `cr:Delegation` for domain authority but no mapping to OAuth scopes or RBAC roles in the broker.
- No event subscription pattern for application developers. Scorpio supports NGSI-LD Subscriptions (`POST /ngsi-ld/v1/subscriptions`), which is the live-update mechanism an application would use instead of polling. No subscription examples or schemas are included.

**Wishlist:**
- A TypeScript/Python client library that handles URN construction, `@context` header attachment, Property/Relationship wrapping, and typed entity deserialization — so application code never touches raw JSON-LD.
- A local development setup: `docker-compose.yml` with Scorpio + context-file server + pre-loaded LY900018 fixture, so an SDE can run `docker compose up` and have a working graph in five minutes.
- An OpenAPI spec generated from the NGSI-LD entity shapes, for SDEs who prefer HTTP-first documentation to OWL.
- An NGSI-LD Subscription example: "notify my endpoint when any `cr:SiteSelectionDecision` is created with `decisionOutcome = cr:SiteStatusDropped`."

---

## 10. Security Engineer

**What they see when they look at the graph:**
A system that handles clinical trial data — which is sensitive, regulated, and a target — with a threat model that is partially addressed at the design level but not operationalized. The PII separation between `hcls:Person` and `cr:StudySubject` via `cr:Enrollment` is a genuine privacy control baked into the data model. But the operational security questions — who authenticates to the broker, how is the keychain protected, what happens in a breach — are entirely unaddressed.

**Pros:**
- The `hcls:Person` / `cr:StudySubject` separation is the right design. Subject-level clinical data lives in `cr:StudySubject` and its linked entities; the PII bridge (`cr:Enrollment → hcls:Person`) can be stored in a separate, access-controlled store. A breach of the main graph does not expose patient identity.
- `top:integrityHash` (SHA-256 or stronger) on `top:Evidence`, combined with the SHACL rule that hashed values must be `top:Versioned`, creates a tamper-evident audit trail. An attacker who modifies a signed record violates the SHACL shape — detectable at next validation run.
- The `top:signedBy` / `top:Attestation` model aligns with 21 CFR Part 11 electronic signature requirements. If implemented with a proper PKI, the graph can produce non-repudiable evidence of who attested what.
- The bitemporal model prevents back-dating by design: `top:observedAt` is set at ingest time by the pipeline, not by the submitting system. A rogue EDC cannot timestamp a falsified entry in the past without the pipeline catching the inconsistency.
- Named individuals for regulatory laws (`cr:ICH_E6_R3`, `cr:CFR_21_Part_11`) as `top:RegulatoryLaw` instances mean compliance scope is declared in the data, not just in a policy document — auditable and queryable.

**Cons / Gaps:**
- No authentication or authorization model. Scorpio exposes an HTTP API with no default auth. Anyone with network access to the broker endpoint can read or write entities. The project is silent on OAuth 2.0 scopes, mTLS, or any IAM integration.
- No secrets management. The `cr:Enrollment` keychain (the mapping from `cr:StudySubject` to `hcls:Person`) is described as "sensitive" in documentation but no key management architecture is specified. Where does this mapping live? Who holds the keys? Under what HSM? What is the break-glass procedure?
- No data residency or sovereignty model. Clinical trials run under EU GDPR, US HIPAA, Japan APPI, Brazil LGPD. The ontology has `cr:EU_GDPR` as a named individual but no properties that bind an entity or a graph partition to a jurisdiction, or that enforce data localization.
- No threat model document. The project does not enumerate: what assets need protecting, who the adversaries are (rogue CRO, nation-state, insider, ransomware), what the attack surface of a Scorpio broker is, or what a breach response looks like.
- `cx:inferredBy` pointing to `top:AutonomousAgent` for LLM-generated mappings introduces a new trust boundary. An LLM that is compromised or prompt-injected could generate malicious mappings that pass the `cx:mappingConfidence` threshold and get promoted to canonical. There is no adversarial input validation for the LLM inference path.

**Wishlist:**
- A security architecture document covering: authentication (OAuth 2.0 + PKCE for human users, mTLS for service accounts), authorization (NGSI-LD tenancy per study, RBAC mapped to `cr:Delegation` roles), and key management for the Enrollment keychain.
- GDPR Article 25 (data protection by design) compliance mapping: which entities contain personal data, where data minimization is applied, what the retention and deletion path is for a subject who withdraws.
- A threat model (STRIDE or similar) for the ingestion pipeline: EDC export → transformer → broker. What can a malicious EDC export do? What does input validation look like at the transformer boundary?
- An audit log SHACL shape: every write to the broker should produce a `top:Log` entry with `prov:wasAssociatedWith` (the writing agent) and `top:observedAt`. Scorpio supports notification subscriptions that could drive this.
- LLM input sanitization guidance for the `cx:OperationalRecord` mapping pipeline: what input validation prevents a prompt-injection attack in a sponsor's custom CRF field value from corrupting the mapping graph.

---

## 11. Ontology Expert

*This role is distinct from Knowledge Engineer (#12): an Ontology Expert focuses on formal ontology design, upper-ontology alignment, and OWL/Description Logic correctness — the logical layer, not the knowledge acquisition and modelling workflow layer.*

**What they see when they look at the graph:**
A well-intentioned and mostly sound foundational ontology with some avoidable modelling choices and a few genuine strengths that are rare in domain ontologies. The BFO and PROV-O alignments are honest; most domain ontologies claim alignment and then define classes that contradict it. The bitemporal model is correctly separated from the PROV-O model (PROV models system time; `top:validFrom`/`top:validUntil` model world-time — the declared absence of a PROV peer for valid time is the right call). The extensibility flavor annotation (`Invariant`/`Tightenable`/`Additive`) is an unusual and useful meta-modelling device.

**Pros:**
- The upper ontology layering (TOP Core → HCLS Core → CR domain) is clean. Each layer adds specificity without redefining what the layer above established. `cr:Study rdfs:subClassOf top:Scope` is an honest relationship — a Study is a kind of bounded intent container.
- The decision not to use `owl:sameAs` anywhere in the crosswalk layer is correct. `cx:Mapping` with `skos:exactMatch`/`skos:closeMatch`/`skos:broadMatch` predicates is the right way to express cross-ontology alignment without the inference explosion that `owl:sameAs` causes.
- Roles modelled as object properties (not classes) is the right modelling decision. `cr:principalInvestigator` as a property of `cr:StudySite` rather than a `PIRole` class avoids the classic "role class proliferation" anti-pattern.
- The `top:Versioned` marker class for bitemporal nodes, rather than using `owl:versionInfo` or a timestamp on the entity itself, correctly reflects that versioning is a reification of the value-at-time, not a property of the named entity.
- `owl:FunctionalProperty` on `top:identifier` is correct and computationally meaningful: it tells an OWL reasoner that two entities with the same identifier must be `owl:sameAs`.

**Cons / Gaps:**
- No `owl:disjointWith` axioms between the eight L2 categories. The categories are intended to be disjoint — a `top:Person` should not also be a `top:Equipment` — but without disjointness axioms, an OWL reasoner cannot detect this inconsistency. A domain ontology without disjointness is incomplete at the class level.
- `top:Organism rdfs:subClassOf prov:Agent` is problematic. PROV-O defines an Agent as "something that bears some form of responsibility for an activity taking place." A laboratory mouse does not bear responsibility; it is an experimental subject. The class should be `rdfs:subClassOf top:CommonEntity` with a BFO alignment to `bfo:MaterialEntity`, not a PROV agent.
- `top:Activity` (the leaf class under `top:Temporal`) and `prov:Activity` are in a naming and semantic collision. `top:Activity rdfs:subClassOf top:Temporal rdfs:subClassOf prov:Activity` — so `top:Activity` is a `prov:Activity` that is a `top:Temporal` that is also a `prov:Activity`. The transitivity is fine logically but the naming creates reader confusion between the OWL class `top:Activity` and the PROV concept `prov:Activity`.
- `top:Versioned` is a bare class with no `owl:disjointWith top:CommonEntity` axiom. An entity can be both `top:CommonEntity` and `top:Versioned` — but `top:Versioned` is described as a "marker," not a subclass. Whether versioned entities are a subset of CommonEntity or an orthogonal classification is ambiguous in the OWL.
- The `top:flavor` annotation property has no `owl:oneOf` enumeration on its range. The valid values are documented in comments (`"Invariant"`, `"Tightenable"`, `"Additive"`) but not machine-enforced. A downstream ontology could declare `top:flavor "Mutable"` without any constraint violation.

**Wishlist:**
- `owl:disjointWith` between all pairs of L2 categories, enforced with SHACL `sh:disjoint` for instance data (since OWL open-world assumption does not fire disjointness violations against instances without a closed-world SHACL layer).
- A `top:FlavorValue` SKOS concept scheme with `skos:Concept` individuals `top:FlavorInvariant`, `top:FlavorTightenable`, `top:FlavorAdditive`, and `sh:in` on `top:flavor` to enforce the enumeration.
- Reclassify `top:Organism`: remove `prov:Agent` superclass; add `bfo:MaterialEntity` superclass; add a new property `top:subjectOf` (domain `top:Organism`, range `top:Scope`) to represent the experimental subject relationship.
- A separate `top:VersionSeries` class (the stable identity root) with `prov:specializationOf` range-pinned to `top:VersionSeries`, making the versioning pattern computable and the identity root explicitly typed.
- A closed-world SHACL shape enforcing `top:flavor` values against the SKOS concept scheme, so the linter catches extension violations at PR time.

---

## 12. Knowledge Engineer

*Distinct from Ontology Expert (#11): a Knowledge Engineer focuses on the knowledge acquisition pipeline — how subject-matter experts contribute, how the graph is populated, how queries are designed, how knowledge is maintained and curated over time.*

**What they see when they look at the graph:**
A well-structured knowledge graph that solves the modelling problem but has not yet addressed the population problem. Getting the OWL right is 20% of the job; getting authoritative, current, and complete instance data into the graph — and keeping it there — is the other 80%. The transformer for USDM v4 is a strong start on the automated population path. The crosswalk curation workflow, the LLM-assisted mapping review, and the human expert contribution path are all described but not implemented.

**Pros:**
- The SSSOM-compatible crosswalk approach (`cx:Mapping` with `cx:justification`, `cx:confidence`, `cx:reviewStatus`, `cx:mappingMethod`) is a proper knowledge curation workflow in data form. It distinguishes `ManualMappingCuration` from `LLMInference` from `HybridReview` — the provenance of each knowledge claim is explicit.
- The `cx:reviewStatus` lifecycle (`proposed → under_review → confirmed → rejected → deprecated`) gives a KE team a real workflow to manage mapping quality over time. This is rare; most ontologies treat mappings as a one-time export.
- The `cx:inferredBy → top:AutonomousAgent` and `cx:confirmedBy → hcls:Person` pattern correctly separates machine generation from human confirmation. LLM output is never trusted directly; a human always sits in the confirmation loop.
- The USDM v4 transformer is a template for the "automated knowledge extraction" path: structured input (USDM JSON) → deterministic transformation → graph entities. The KE team does not have to interview anyone to populate a protocol's core structure.
- The `cr:OperationalRecord` class, with a `cx:mappingConfidence` score, is honest about the "long tail" problem — there will always be sponsor-specific fields that do not map cleanly to any standard. Having a holding class with a confidence score is better than ignoring them or mapping them incorrectly.

**Cons / Gaps:**
- No knowledge acquisition tooling. How does a clinical expert contribute to the graph? There is no annotation interface, no expert elicitation form, no editorial workflow UI. The graph is populated by code (transformers) or by editing Turtle files — neither is accessible to a domain expert.
- The crosswalk from USDM to TOP (`usdm-to-cr.ttl`) covers study-level concepts but not the full USDM class hierarchy (86 classes, 693 properties in the reference implementation). The knowledge gap between "what USDM has" and "what TOP currently maps" is large.
- No maintenance lifecycle for crosswalks. When USDM v5 is published (expected), the mappings in `usdm-to-cr.ttl` will need updating. There is no versioned dependency declaration ("this crosswalk targets USDM v4.0.3") and no automated test that would detect a broken mapping when the target schema changes.
- The `top:Conclusion` class (for LLM-inferred outputs) has `top:confidence`, `top:rationale`, and `top:concludesAbout`, but no property for the *query or prompt* that generated the conclusion — the input is not captured, only the output. This breaks reproducibility.
- No concept of a *knowledge gap* or *unknown*. The graph can state what it knows; it cannot state "we have no data on this site's screen failure rate" in a structured way. Open-world assumption is not the same as explicit unknown.

**Wishlist:**
- A lightweight editorial workflow: a structured YAML/JSON form that a clinical expert fills in to propose a new `cx:Mapping`, which is committed to a branch, reviewed by a KE, and merged when confirmed. No Turtle required from the expert.
- A USDM version pin in the crosswalk file metadata: `cx:targetSchemaVersion "4.0.3"` on the crosswalk `owl:Ontology` declaration, tested by a CI job that fetches the target USDM IRI and verifies it still resolves.
- A `top:Conclusion` property for `top:promptTemplate` (the instruction given to the LLM) and `top:sourceContext` (the input excerpt the LLM reasoned over) — so inferences are reproducible and auditable.
- A `cr:KnowledgeGap` class (subClassOf `top:Outcome`) for explicitly recording that a value is unknown, missing, or not collected — distinct from absent (which means "not yet loaded").

---

## 13. Information Architect

**What they see when they look at the graph:**
A knowledge model that has made good decisions about *what* to represent but has not yet thought hard about *how people find things*. An IA's concern is navigability, labelling, faceting, search, and the experience of a user trying to orient themselves in the information space. The ontology provides the semantic backbone; the IA layer sits on top of it and makes it usable.

**Pros:**
- The eight-category top-level structure (Agent, Location, Resource, Scope, Temporal, Evidence, Outcome, Constraint) is a clean primary navigation facet. Eight buckets with meaningful labels at the L2 level is the right grain for information architecture — not so many that users are lost, not so few that everything is in one pile.
- The `top:status` property on every entity is a natural filter facet. *Show me all active sites* / *Show me all closed studies* / *Show me all Dropped site decisions* — these are the first things a user would want to do in a browse interface, and they work out of the box.
- `rdfs:label` and `rdfs:comment` on every class and property provides the raw material for a human-facing glossary and entity type labels. The comments are substantive — they explain *why* the concept exists, not just *what* it is.
- The site lifecycle as a state machine (with comments explaining the reserve and rescue path) is navigation-friendly: a user who sees a site in `SiteStatusReserve` can understand its history and possible futures.
- The published documentation site (21 pages, organized by trial phase — Startup / Conduct / Closeout / Cross-cutting) is a better IA than most ontology projects produce. The flow-based navigation aligns with how practitioners think, not how the ontology is structured.

**Cons / Gaps:**
- No search index. The graph has labels and comments but there is no full-text search over entity definitions, crosswalk rationales, or instance data. A user who wants to find "what concept covers screen failure rate?" has no search path.
- The navigation in the documentation site is flat within each section. There is no breadcrumb, no "related entities" sidebar, no "used by these flows" cross-reference on entity pages. An entity like `cr:Delegation` appears in multiple workflows (consent, assessment, administration) but the docs present it in one place with no contextual pointers.
- Class hierarchies are not visible in the documentation. The `reference.html` page lists all entities but does not render the `rdfs:subClassOf` tree. A user cannot see at a glance that `cr:DoseLimitingToxicity` is a subclass of `cr:AdverseEvent` which is a subclass of `top:Outcome`.
- The crosswalk layer is not integrated into the documentation. An IA would want every entity page to show its mappings: "This concept maps to OBI_0000810 (closeMatch) and USDM InformedConsent (exactMatch)." Currently the crosswalks live in Turtle files that most users will never open.
- No persona-based entry points. The documentation site has a single navigation for all users. A sponsor data manager and a PI have very different questions; a "start here" path for each persona (like the stakeholder perspectives this document represents) would dramatically improve first-use orientation.

**Wishlist:**
- An entity detail page for every class and property in the ontology, auto-generated from the Turtle, showing: label, definition, superclass chain (breadcrumb), properties, crosswalk targets, and which flow pages reference it.
- A faceted browse interface over instance data: filter by entity type, status, study, site, date range. The NGSI-LD broker's `q=` parameter makes this technically trivial; it needs a UI.
- A `rdfs:subClassOf` tree visualization on the Foundation page — a collapsible hierarchy from `top:CommonEntity` down to the domain leaves.
- Persona-based entry points: "I'm a PM → start with Site Lifecycle and Delegation." "I'm a CDM → start with USDM ingestion and crosswalks." "I'm building an app → start with the NGSI-LD context and worked example."
- A crosswalk summary on every entity page: "Maps to: OBI_0000066 (broadMatch, 0.80 confidence, verified 2026-06-20)."

---

## 14. NGSI-LD Expert

**What they see when they look at the graph:**
A project that has done the hard NGSI-LD work correctly — the `@context` is machine-generated from OWL, ObjectProperty terms have `@type: @id`, `top:observedAt` aligns with the NGSI-LD core `observedAt` term, and the URN scheme is well-formed. But the NGSI-LD-specific capabilities — temporal queries, multi-tenancy, subscriptions, geo-queries, Attribute-of-Attribute (Property-of-Property) for bitemporality — are described in the model but not exercised in the implementation.

**Pros:**
- The `@context` generation from OWL is correct and non-trivial. The distinction between ObjectProperty (`@type: @id`) and DatatypeProperty (plain string shortcut) is exactly what the NGSI-LD spec requires for Relationship vs. Property semantics. Getting this wrong (all terms as plain strings) is the most common NGSI-LD context mistake; it is avoided here.
- `top:observedAt` intentionally coincides with NGSI-LD core `observedAt` — transaction time is the NGSI-LD native timestamp. This means the `observedAt` on every Property and Relationship node in the broker is populated automatically by the broker without any application-level logic.
- The bitemporality model maps well to NGSI-LD. `top:validFrom`/`top:validUntil` as top-level entity properties works for entity-level valid time; for attribute-level bitemporality, NGSI-LD's Property-of-Property pattern (a Property node with `observedAt` and additional qualifiers) is the correct mechanism and the model is compatible with it.
- The `urn:ngsi-ld:top-cr:{Type}:{localId}` URN is valid NGSI-LD entity ID format. The type prefix (`top-cr`) in the URN namespace is a useful discriminator for multi-domain deployments.
- The NGSI-LD context file is published separately from the main ontology bundle (`top-cr-v1.ngsi-context.jsonld`) — the right architecture for broker deployments where the context endpoint must be stable and independently servable.

**Cons / Gaps:**
- No use of NGSI-LD Temporal Representation (ETSI GS CIM 009, Section 6.3). The bitemporal model is designed for temporal queries, but there are no example temporal API calls: `GET /ngsi-ld/v1/temporal/entities/{id}?timerel=between&timeAt=2017-01-01T00:00:00Z&endTimeAt=2018-01-01T00:00:00Z`. The broker supports this; the project does not demonstrate it.
- No NGSI-LD Subscription examples. Subscriptions are the primary live-update mechanism in NGSI-LD deployments (e.g., "notify me when a `cr:SiteSelectionDecision` is created"). Without examples, downstream integrators have to discover the subscription API themselves.
- No multi-tenancy design. NGSI-LD supports tenants via the `NGSILD-Tenant` HTTP header — essential for a shared broker hosting multiple sponsor studies. Which tenant owns which study's entities? How is the tenant namespace mapped to a sponsor or study? Not addressed.
- The `@context` URL is not yet served from a stable endpoint. Every entity payload references `https://top.scientix.ai/cr/v1.ngsi-context.jsonld` but this URL is not live. A Scorpio broker that tries to resolve it during entity ingestion will fail with a 404.
- NGSI-LD's `datasetId` mechanism (for representing multiple simultaneous values of the same attribute from different sources) is not used in the model. For a multi-source ingestion scenario (Medidata + Veeva + Castor all reporting on the same subject visit), `datasetId` is the correct mechanism to avoid last-write-wins overwriting.

**Wishlist:**
- A `POST /ngsi-ld/v1/subscriptions` example for the canonical operational use case: "When any `cr:SiteSelectionDecision` is created with `decisionOutcome = cr:SiteStatusDropped`, notify the sponsor data platform."
- Temporal query examples for the LY900018 fixture: "Retrieve the ProtocolVersion that was valid on 2018-01-15" using the NGSI-LD temporal API.
- A production context endpoint: `https://top.scientix.ai/cr/v1.ngsi-context.jsonld` must resolve with `Content-Type: application/ld+json` and a long-lived cache header. This is a prerequisite for any real broker deployment.
- A multi-tenancy design: one Scorpio tenant per sponsor, with study entities namespaced within the tenant. The `NGSILD-Tenant` header value should map to the `cr:Sponsor` IRI.
- `datasetId` examples for multi-source attribute values: a subject's weight recorded by both the site EDC and the sponsor's central lab should produce two Property nodes with different `datasetId` values and `observedAt` timestamps, not one overwritten value.

---

## 15. Property Graph (Neo4j) Expert

**What they see when they look at the graph:**
A rich domain model that has made choices that are idiomatic in RDF but require translation for a property graph. The biggest structural divergence is NGSI-LD/RDF's Property-of-Property pattern (a `Property` node as a first-class object with its own attributes) vs. Neo4j's native edge properties. The second is blank nodes (SHACL constraint objects, NGSI-LD sub-nodes) which have no natural analog in an LPG. But the conceptual model — entities, relationships, properties, temporal metadata — maps cleanly to Neo4j's node/edge/label/property model, and the URN scheme is a natural node key.

**Pros:**
- The eight-category top-level structure maps to eight top-level Neo4j labels (`Agent`, `Location`, `Resource`, `Scope`, `Temporal`, `Evidence`, `Outcome`, `Constraint`) with domain labels stacked on top (`cr__Study:Scope`, `cr__StudySite:Agent`). Neo4j's multi-label nodes handle the `rdfs:subClassOf` hierarchy naturally.
- The `top:identifier` (a stable URN per entity) is a natural Neo4j node key — the `id` property indexed with a `CREATE CONSTRAINT ... IS UNIQUE` constraint. No surrogate key needed.
- The `top:status` as a node property and the lifecycle state machine (site status named individuals) translate directly to a Neo4j string property with a SHACL-equivalent APOC constraint or a graph algorithm traversal over a `(:SiteStatus)-[:NEXT]->(:SiteStatus)` chain.
- Object properties (`cr:sponsoredBy`, `cr:conductedAt`, `cr:hasArm`, etc.) become Neo4j directed relationships — the domain model is already in the right shape. A `cr:Enrollment` bitemporal node becomes a Neo4j relationship node (an intermediate node pattern) with `validFrom`, `validUntil`, and `observedAt` as relationship properties.
- The site lifecycle state machine (`cr:SiteStatusFeasibility → cr:SiteStatusSelected → cr:SiteStatusStartup → cr:SiteStatusActive → cr:SiteStatusClosed`) is a natural Neo4j graph traversal: `MATCH (s:StudySite)-[:HAS_STATUS_HISTORY]->(d:SiteSelectionDecision)-[:OUTCOME]->(status:SiteStatus)`.

**Cons / Gaps:**
- Bitemporality is the hardest translation. In RDF/NGSI-LD, `top:validFrom` lives on a `top:Versioned` node that can be any entity. In Neo4j, edge properties carry temporal metadata well, but *node* bitemporality (multiple versions of the same entity node over time) requires an intermediate "version node" pattern or a time-tree, neither of which is standard. Neo4j's native temporal support (date, datetime types) helps, but the pattern needs explicit design.
- Blank nodes (SHACL `sh:property []` constraint objects, NGSI-LD sub-node structures) have no direct analog in Neo4j. The SHACL layer simply does not exist in a property graph world. There is no standard PG equivalent for SHACL validation; APOC rules and custom Cypher procedures can approximate some constraints but not the full expressiveness.
- `owl:TransitiveProperty` (`top:withinLocation`, `top:partOfScope`) translates to a variable-length Cypher path query (`-[:WITHIN_LOCATION*]->`) — correct but requires performance consideration. In RDF, transitive inference happens once at reasoning time; in Neo4j it happens at every query unless a shadow hierarchy is materialized.
- OWL reasoning does not exist. The inferred facts that an OWL reasoner would produce (`if cr:Delegation exists, then cr:delegate holds cr:delegatedCapability`) must be written as Neo4j stored procedures or trigger-equivalent logic. Every OWL axiom that the project relies on for correctness must be explicitly re-implemented in Cypher.
- The `rdf:type` hierarchy (30+ classes in a chain) becomes a multi-label proliferation in Neo4j. A `cr:DoseLimitingToxicity` node needs labels for `DoseLimitingToxicity`, `AdverseEvent`, `Outcome`, `CommonEntity`, `Versioned`. Neo4j handles this, but label-based indexing becomes expensive as the label count grows.

**Wishlist:**
- A Neo4j data model document: node types with their Neo4j labels, property names, and index/constraint declarations. The OWL model is the source of truth; a `neosemantics` (n10s) import of the Turtle bundle is a start, but the resulting model needs post-processing to be LPG-idiomatic.
- A Cypher translation guide for the top five SPARQL projection queries: "find all active sites for study X" → the equivalent `MATCH` pattern, with performance notes.
- A `neosemantics` (n10s) import script for the Turtle bundle, so a Neo4j user can bootstrap the ontology into their graph with a single Cypher procedure call and use the `n10s.rdf.getByType` helpers to query it.
- A bitemporality pattern for Neo4j: how to model `top:Versioned` entities as version-chain node patterns (current node → previous version → previous version) with Neo4j native datetime properties on the relationship edges.
- An APOC constraint library that approximates the key SHACL shapes: the `UniversalDNAShape` (every node must have `identifier`, `observedAt`, `status`) as an APOC trigger or constraint that fires on node creation.

---

## Summary grid

| Stakeholder | Most valuable thing here | Biggest gap | Adoption blocker |
|---|---|---|---|
| Oncologist / PI | Bitemporal protocol versions; delegation audit trail | No CTCAE-coded AE properties; no response criteria | No UI; data enters via EDC, not the graph |
| CDM / Data Manager | LLM-assisted field mapping model; USDM transformer | No working SDTM projection; no Define-XML export | CRO data not structured for graph ingest |
| CRO Ops / PM | Site lifecycle state machine; mandatory site-drop rationale | No site performance KPIs; no monitoring visit model | CRO has no incentive to feed external graph |
| Regulatory Affairs | Jurisdiction-aware SHACL; 21 CFR Part 11 baked into shapes | No MedDRA crosswalk; no IND structure; no protocol deviation class | Not a validated GCP system yet |
| Knowledge Engineer / Ontologist | Clean upper-ontology alignment; SSSOM crosswalks | No disjointness axioms; no self-declaring modules | Low — this layer is the audience |
| CRC / Site Staff | Delegation queryability; no PII in the graph | No site-facing interface | Not their system; indirect benefit only |
| Software / Data Engineer | Idempotent URN scheme; working transformer; deterministic builds | No live-broker test; no versioning strategy | Needs Scorpio + SHACL integration test |
| CMO / Executive | Cross-study institutional learning; regulatory framework IRIs | Adoption friction; no GxP validation | Requires CRO buy-in; regulatory pathway unclear |
| **Software Dev Engineer** | Stable URN key; broker REST API; JSON-LD output | No client SDK; no auth model; context URL not live | docker-compose local setup missing |
| **Security Engineer** | PII separation by design; tamper-evident hash+SHACL | No auth/AuthZ model; no threat model; no key management | No GxP-validated deployment exists |
| **Ontology Expert** | BFO/PROV-O honest alignment; flavor annotation; `owl:FunctionalProperty` on identifier | No disjointness axioms; `top:Organism` misaligned to `prov:Agent` | Low — formal critique, not a blocker |
| **Knowledge Engineer** | SSSOM curation workflow; LLM confirm/reject lifecycle | No expert contribution UI; no USDM version pin; no prompt capture | Population pipeline unbuilt |
| **Information Architect** | 8-category top-level; `rdfs:label`/`rdfs:comment` coverage; flow-based doc site | No entity detail pages; no class hierarchy view; no crosswalk on entity pages | No browse/search interface |
| **NGSI-LD Expert** | Correct `@type:@id` on ObjectProperty; `observedAt` alignment; well-formed URNs | Context URL not live; no temporal API examples; no subscriptions; no multi-tenancy | Context endpoint must be served before any real deployment |
| **Neo4j / PG Expert** | Entity/relationship model maps to LPG naturally; stable node keys | No Cypher translation; no bitemporality pattern; no SHACL equivalent | OWL reasoning must be re-implemented in Cypher |

---

## What this is, honestly

This is a **design-time specification and integration contract**, not yet an operational system. It is the kind of artifact that, in a large sponsor, would be produced by an Architecture Review Board and then handed to vendors to implement against. The ontology is mature. The crosswalks are honest. The transformer is a proof-of-concept. The runtime is a reference architecture.

The gap between *this* and *a running system processing real trial data* is: (a) one validated GxP deployment, (b) one CRO willing to export in USDM format, and (c) one sponsor data engineering team willing to run the ingestion pipeline. None of those are ontology problems.

*Generated from the TOP CR domain v1 branch, June 2026.*
