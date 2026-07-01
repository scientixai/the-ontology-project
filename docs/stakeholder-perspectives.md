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
| **Biostatistician** | Endpoint and arm model; ICH E9 R1 regulatory law individual | No estimand, no SAP, no analysis population, no ADaM; `cr:Endpoint` has no properties | No submission-ready output without this layer |
| **Drug Safety / PV Officer** | `cr:AdverseEvent` + `cr:DoseLimitingToxicity` as first-class entities | No SUSAR workflow, no E2B(R3), no aggregate reporting, no signal detection | Cannot replace a pharmacovigilance system |
| **HL7 FHIR Expert** | RDF/JSON-LD base compatible with FHIR RDF serialization | No FHIR crosswalk; EHR-to-graph path entirely absent; `cr:Assessment` has no properties | EHR data cannot enter the graph without a FHIR bridge |
| **Patient / Study Participant** | PII isolation by design; no personal data in the main graph | Right to erasure has no implementation; consent withdrawal is not a graph event; subject has no view of their own data | Patients are modeled as data subjects, not as participants with rights |
| **Data Privacy Counsel / DPO** | `cr:InformedConsent` bitemporal; `cr:EU_GDPR` as named individual; PII separation | No lawful basis declaration; no DPA template; no DSAR path; cross-border transfer unaddressed | Cannot process EU subject data without a GDPR compliance architecture |
| **DevOps / Platform Engineer** | Deterministic builds; SHA256SUMS pin; CDK reference architecture | No CSV; no IQ/OQ/PQ; no change control; no DR/BCP; Garnet not GxP-validated | GxP validation of the platform is a prerequisite for live trial data |
| **Enterprise / Data Architect** | Three-layer model fits medallion architecture; stable URN keys for MDM join | No MDM alignment; no data lineage metadata; no integration pattern for EDW/data lake | Graph is a silo until it connects to the sponsor's existing data estate |
| **AI/ML Engineer** | `top:Conclusion` + `top:AutonomousAgent` inference model; `cx:mappingConfidence`; graph structure for GNN | No vector index; no GraphRAG pattern; no LLM pipeline; no feature store design | Inference capabilities are modeled, not built |

---

## 16. Biostatistician

**What they see when they look at the graph:**
A model that has mapped the clinical trial world carefully but stopped short of the layer they live in. The biostatistician's universe — estimands, analysis populations, statistical analysis plans, hypothesis tests, power calculations, and ADaM datasets — is entirely absent. `cr:Endpoint` exists as a class but has no properties. `cr:Arm` exists but carries no randomization ratio or stratification factors. The graph can tell you *what* the protocol says; it cannot tell you *how the data will be analysed*.

**Pros:**
- `cr:Endpoint` as a `top:Scope` subclass is the right ontological placement — an endpoint is a defined outcome measure, a bounded intent, not a data point. It correctly separates the *definition* of an endpoint (the protocol's intent) from the *measurement* (an `hcls:Observation`).
- `cr:Arm` linked to `cr:Study` via `cr:hasArm` provides the structural backbone for a parallel-group or crossover design. The existence of multiple arms is representable.
- `cr:StoppingRule` as a `top:Constraint` subclass is the right modeling of a DLT-triggered stopping rule in a dose-escalation oncology study — a constraint that halts an activity when a threshold is crossed.
- The bitemporal model supports the analysis population definition problem: *"Who was enrolled as of the data-cut date for the primary analysis?"* is answerable via a `top:validFrom`/`top:validUntil` query on `cr:Enrollment` — provided the data-cut date is recorded.
- ICH E9(R1) is present as `cr:ICH_E9_R1` (a `top:RegulatoryLaw` individual). The estimand framework's regulatory home is acknowledged.

**Cons / Gaps:**
- `cr:Endpoint` has no properties. Primary vs. secondary vs. exploratory, the endpoint estimand (treatment policy, hypothetical, composite variable, while-on-treatment strategies), the analysis method (MMRM, logrank, CMH), the multiple testing hierarchy — none of these are modeled.
- There is no `cr:Estimand` class. ICH E9(R1) defines the estimand as a four-component construct (population, variable, intercurrent event strategy, population-level summary). This is now the foundational unit of a regulatory submission's efficacy analysis, and it does not exist in the graph.
- There is no `cr:StatisticalAnalysisPlan` class. The SAP is a versioned, protocol-governed document — a natural `top:Evidence, top:Versioned` subclass — but it is absent.
- `cr:Arm` has no `randomizationRatio` property, no `stratificationFactor` links, and no `plannedEnrollment` count. The structural facts a biostatistician needs to validate a power calculation are not capturable.
- There is no `cr:AnalysisDataset` (ADaM-level) concept. The path from raw `hcls:Observation` to a derived analysis variable in ADSL, ADAE, or ADTTE is completely unmodeled.
- No `cr:DataCut` entity. The date at which a database is locked for analysis — with all the enrollment, observation, and AE data frozen at that point — is not representable. Without it, "the analysis population as of the primary data cut" is a query that cannot be answered.

**Wishlist:**
- `cr:Estimand` as a `top:Scope` subclass, with properties for `estimandPopulation` (→ `cr:EligibilityCriterion` set), `estimandVariable` (→ `cr:Endpoint`), `intercurrentEventStrategy` (coded), and `populationLevelSummary` (free text).
- `cr:Endpoint` properties: `endpointType` (primary/key secondary/secondary/exploratory), `endpointEstimand` (→ `cr:Estimand`), `analysisMethod` (coded or free text), `timepoint` (xsd:duration or `cr:Visit` link).
- `cr:DataCut` as a `top:Temporal` subclass, linked to `cr:Study` and carrying a `top:observedAt` timestamp — the anchor for all analysis population queries.
- `cr:AnalysisPopulation` (ITT, mITT, PP, safety population) as a named `top:Scope` subclass linked to the `cr:DataCut` and defined by a set of `cr:EligibilityCriterion`-equivalent inclusion rules.
- A SPARQL projection for "enrollment as of data cut date" — the canonical analysis population query that every trial must answer.

---

## 17. Drug Safety / Pharmacovigilance Officer

**What they see when they look at the graph:**
A model with the right foundation for safety data — `cr:AdverseEvent` as a first-class versioned entity, `cr:DoseLimitingToxicity` as a subclass, `cr:StoppingRule` as a constraint — but no operational pharmacovigilance layer built on it. Safety reporting in clinical trials operates under strict regulatory timelines (15-day SUSAR submission, 7-day fatal/life-threatening expedited reports) and produces structured outputs (E2B(R3) ICSRs, DSURs, PBRERs) that require detailed coded data the graph does not yet carry.

**Pros:**
- `cr:AdverseEvent rdfs:subClassOf top:Outcome, top:Versioned` is the correct placement. An adverse event is a produced outcome, and it is bitemporal — it has a date of onset (valid time) and a date the system recorded it (transaction time). The model correctly separates these.
- `cr:DoseLimitingToxicity rdfs:subClassOf cr:AdverseEvent` captures the oncology dose-escalation pattern where a DLT triggers a dose decision. The subclass relationship is clean.
- `cr:StoppingRule rdfs:subClassOf top:Constraint` means stopping rules are computable constraints, not just text in a protocol. A query can ask: *"Which active studies have a stopping rule that references DLT rate > 33%?"*
- The `prov:wasGeneratedBy` alignment (via `top:producedBy`) means an adverse event can be linked to the clinical assessment that surfaced it — the causality chain is representable.
- The bitemporal model supports late-reporting detection: if `top:observedAt` (system entry date) is significantly later than `top:validFrom` (event onset date), the delta is a pharmacovigilance signal for late reporting.

**Cons / Gaps:**
- No MedDRA coding. `cr:AdverseEvent` has no `meddraLLT`, `meddraPT`, `meddraSOC` properties with coded term IRIs and dictionary version. Every regulatory safety submission requires MedDRA coding; without it the AE entities are narratively described but not submission-ready.
- No CTCAE grading. Adverse event severity is the primary safety signal in oncology. `cr:AdverseEvent` has no grade property linked to NCI CTCAE v5 terms.
- No SUSAR workflow. A Suspected Unexpected Serious Adverse Reaction triggers a regulatory clock (7 or 15 days to submission). There is no `cr:SUSAR` class, no `reportingDeadline` property, and no link to the regulatory authority to which the report is submitted.
- No E2B(R3) output path. Individual Case Safety Reports are the unit of pharmacovigilance exchange between sponsors, authorities, and WHO. The graph has the source data for an ICSR but no serialization path to E2B(R3) XML.
- No aggregate reporting model. DSURs and PBRERs require cumulative exposure counts, AE incidence tables by SOC/PT, and benefit-risk narratives. The graph has the individual events but no aggregate rollup model.
- No causality assessment. Whether an AE is related to the investigational product (unrelated / possible / probable / definite) is a physician judgment that belongs as a property on `cr:AdverseEvent` — and it is absent.

**Wishlist:**
- `cr:AdverseEvent` properties: `aeOnsetDate` (xsd:date, the valid time), `aeResolutionDate` (xsd:date), `aeSeverity` (CTCAE grade 1-5 as a coded term IRI), `aeSerious` (xsd:boolean), `aeCausality` (coded: unrelated/possible/probable/definite), `meddraPreferredTerm` (IRI into MedDRA PT), `meddraSystemOrganClass` (IRI into MedDRA SOC).
- `cr:SUSAR` as a `cr:AdverseEvent` subclass, with `reportingDeadline` (xsd:dateTime), `submittedTo` (→ `top:RegulatoryLaw` individual or regulatory authority IRI), and `submissionDate` (xsd:date).
- A MedDRA crosswalk file (`cr-to-meddra.ttl`) analogous to the OBI crosswalk — mapping `cr:AdverseEvent` to `OAE_0000001` (already done) and to MedDRA PT codes via `cx:Mapping` with a disclaimer that MedDRA is a licensed dictionary and IRIs are reference pointers, not reproductions.
- `cr:CausalityAssessment` as a `top:Conclusion` subclass — the physician's judgment recorded as a conclusion with `top:confidence`, `top:rationale`, and `cx:concludesAbout → cr:AdverseEvent`.
- A SPARQL projection for "all serious AEs in this study, by MedDRA SOC, with their MedDRA PT codes" — the aggregate table that feeds a DSUR section.

---

## 18. HL7 FHIR Expert

**What they see when they look at the graph:**
A parallel universe. FHIR R4 and TOP both model clinical research concepts — studies, subjects, observations, adverse events — but in different shapes, with different identifiers, different temporal conventions, and different relationship patterns. The EHR world speaks FHIR; the clinical trial world (increasingly) speaks USDM/NGSI-LD. TOP sits between them but currently has no bridge to FHIR. Every data point that comes from a site's EHR — and in decentralised trials that is most of the data — must cross this gap without a map.

**Pros:**
- The RDF/JSON-LD serialization of TOP entities is compatible with FHIR's own RDF serialization (`fhir:` namespace). Both are JSON-LD; a broker that serves TOP NGSI-LD entities and a FHIR server that serves FHIR RDF can be joined in a SPARQL federated query without a middleware translation layer.
- `hcls:Person` as the PII boundary maps cleanly to FHIR `Patient`. Both are the real-world human identity at the edge of the system. The `cr:Enrollment` bridge between `hcls:Person` and `cr:StudySubject` has a natural FHIR analog in `ResearchSubject.individual` → `Patient`.
- `cr:Study` maps to FHIR `ResearchStudy`. `cr:Arm` maps to `ResearchStudy.arm`. `cr:EligibilityCriterion` maps to `ResearchStudy.enrollment` → `Group` (with inclusion/exclusion criteria encoded as `Group.characteristic`). The structural correspondence is real.
- `hcls:Observation` (the clinical measurement) maps directly to FHIR `Observation`. Both carry a subject reference, a code (LOINC/SNOMED), a value, and a timestamp. A crosswalk here is straightforward.
- The bitemporal model (`top:observedAt` as transaction time, `top:validFrom` as valid time) aligns with FHIR's `meta.lastUpdated` (transaction time) and `Observation.effectiveDateTime` (valid time). The semantic correspondence is strong.

**Cons / Gaps:**
- No FHIR crosswalk exists anywhere in the project. `cr:Study` → `ResearchStudy`, `cr:Enrollment` → `ResearchSubject`, `hcls:Observation` → `Observation` — these are obvious mappings that should be in `cr-to-external.ttl` or a dedicated `cr-to-fhir.ttl`. They are absent.
- `cr:Assessment` (the clinical act) has no properties. In FHIR, `Procedure` and `Observation` both carry `code` (SNOMED CT), `performer`, `subject`, and `encounter`. Without properties on `cr:Assessment`, there is nothing to map.
- FHIR `Encounter` (the clinical visit) maps to `cr:Visit`, but `cr:Visit` has no FHIR-compatible properties — no encounter class (ambulatory, virtual, inpatient), no service type, no location reference in FHIR's structure.
- Decentralised trial data (wearable sensor readings, ePRO responses, home nursing assessments) arrives as FHIR `Observation` resources from patient-facing apps. There is no ingestion path from FHIR `Bundle` into TOP NGSI-LD entities.
- FHIR `Consent` (a legal resource with provision chains, policy references, and actor-specific permissions) is far richer than `cr:InformedConsent` (currently just a bitemporal act with no content properties). A FHIR-based consent management system cannot interoperate with the current model.

**Wishlist:**
- A `cr-to-fhir.ttl` crosswalk file mapping the core CR entities to their FHIR R4 equivalents: `cr:Study` → `fhir:ResearchStudy`, `cr:Enrollment` → `fhir:ResearchSubject`, `cr:Visit` → `fhir:Encounter`, `hcls:Observation` → `fhir:Observation`, `cr:AdverseEvent` → `fhir:AdverseEvent`.
- A FHIR `Bundle` → NGSI-LD transformer (analogous to the USDM transformer) that reads a FHIR `ResearchStudy` bundle and emits `cr:Study`, `cr:Arm`, and `cr:EligibilityCriterion` entities.
- Properties on `cr:Assessment`: `assessmentCode` (SNOMED CT or LOINC IRI), `assessmentMethod` (coded), linked `hcls:Observation` for the result, and a `performedBy` Relationship.
- `cr:InformedConsent` properties: `consentVersion`, `consentFormIRI`, `witnessedBy` (→ `hcls:Person`), `withdrawalDate` (xsd:date, the event that closes the valid-time interval).
- A FHIR Subscription profile: a FHIR server that holds EHR data can push new `Observation` resources to the TOP ingestion pipeline via a FHIR R4B Subscription, which the pipeline transforms to `hcls:Observation` NGSI-LD entities in near-real-time.

---

## 19. Patient / Study Participant

**What they see when they look at the graph:**
Something both reassuring and alienating. Reassuring: their identity is protected by design — `cr:StudySubject` carries no PII, the link to `hcls:Person` (which does) sits behind a separately controlled `cr:Enrollment` act. Alienating: they are modeled entirely as a data subject, never as a participant with rights, preferences, or agency. Their consent is a node. Their withdrawal is not modeled at all. Their right to see their own data, correct it, or have it erased has no representation anywhere in the graph.

**Pros:**
- The `hcls:Person` / `cr:StudySubject` separation is a genuine privacy protection, not a superficial label. A breach of the operational graph does not expose patient identity. This is the right design for a participant's peace of mind.
- `cr:InformedConsent` as a bitemporal act means the question *"did this person consent before this procedure was performed?"* is answerable by comparing `cr:InformedConsent.validFrom` to `cr:Administration.startTime`. The consent-before-treatment invariant is computable.
- The `cr:Attestation` class as a `top:Versioned` evidence type means a consent form, once signed, is immutable. A participant's consent cannot be quietly altered after the fact.
- `cr:EligibilityCriterion` with full text (demonstrated in the LY900018 transformer) means a participant's eligibility decision is traceable to the exact protocol text that governed it — relevant if a participant later disputes whether they should have been enrolled.
- `cr:StudySubject` carrying `top:status` means the participant's current trial status (enrolled, completed, withdrawn, screen-failed) is a queryable first-class property, not a field in a spreadsheet that may or may not be current.

**Cons / Gaps:**
- Consent withdrawal is not modeled. A participant who withdraws consent is one of the most consequential events in a trial — it closes the `cr:InformedConsent` valid-time interval, may trigger data deletion obligations, and certainly stops further data collection. There is no `cr:ConsentWithdrawal` event, no `validUntil` property set on consent, and no downstream cascade to observations collected after withdrawal.
- GDPR Article 17 (right to erasure) has no implementation path. If a participant in an EU trial requests deletion of their data, there is no mechanism in the graph to identify all entities linked to their `hcls:Person` node, assess which can be deleted under ICH E6(R3) retention requirements, and execute the deletion or pseudonymisation.
- There is no patient-facing view. A participant who wants to see what data the trial has collected about them — their visits, their assessments, their adverse events — has no interface to the graph. GDPR Article 15 (right of access) requires this to be fulfillable.
- `cr:StudySubject` has no `preferredLanguage`, `accessibilityNeeds`, or `contactPreferences` properties. The model treats the participant entirely as a data object; their role as a human being with communication needs is invisible.
- Decentralised trial activities (ePRO, wearable data, home nursing visits) are not modeled. A participant who submits a daily symptom diary via an app is generating `hcls:Observation` data, but the app-to-graph path does not exist.

**Wishlist:**
- `cr:ConsentWithdrawal` as a `top:Temporal` subclass, linked to the `cr:InformedConsent` it closes (setting `validUntil`), with `withdrawalDate`, `withdrawalReason` (coded), and a cascade rule: observations with `top:validFrom` after `withdrawalDate` are flagged for regulatory review before analysis inclusion.
- A GDPR data map: a SPARQL query that, given a `hcls:Person` IRI, returns all graph entities linked to that person directly or transitively — the output of a Data Subject Access Request.
- A `cr:DataRetentionPolicy` linked to each `cr:Study`, declaring the ICH E6(R3)-mandated retention period and the data minimisation policy for post-trial data.
- A participant-facing data summary view: a SPARQL or NGSI-LD query that returns, for a given `cr:StudySubject`, the visits attended, the assessments recorded, and the adverse events reported — in plain-language labels drawn from `rdfs:label`.
- `cr:EproSubmission` as a `top:Temporal` subclass — a patient-initiated data entry event (ePRO questionnaire, wearable sync) that produces `hcls:Observation` entities with `top:observedAt` set by the device and `top:validFrom` set to the measurement time.

---

## 20. Data Privacy Counsel / Data Protection Officer

**What they see when they look at the graph:**
A model that has correctly identified the PII risk and put a structural control in place, but has not followed through on the legal architecture that surrounds it. The `cr:Enrollment` bridge between `hcls:Person` and `cr:StudySubject` is the right privacy-by-design choice. But the GDPR requires more than separation: it requires a declared lawful basis, a documented data processing agreement with every data processor, a data protection impact assessment for high-risk processing, and a mechanism to respond to data subject rights requests. None of these exist in the model or the documentation.

**Pros:**
- Privacy by design is implemented at the data model level, not as a policy overlay. The separation of `hcls:Person` (PII) from `cr:StudySubject` (pseudonymous trial identity) is an architectural control that cannot be bypassed by a misconfigured application.
- `cr:InformedConsent` as a bitemporal, attested, immutable act is the correct legal treatment of consent — it is a contract, not a checkbox. The `top:Versioned` + `top:Attestation` pattern means the consent record has integrity properties that GDPR Article 7(1) requires (demonstrable, freely given, specific, informed).
- `cr:EU_GDPR` as a named `top:RegulatoryLaw` individual means the data governance framework that governs a study can be declared in the data, not just in a Word document.
- The `top:integrityHash` on `top:Evidence` provides the technical basis for an audit log that satisfies GDPR Article 5(2) accountability principle — the controller can demonstrate, at the data level, that records have not been altered.
- The multi-jurisdiction regulatory law individuals (`cr:EU_GDPR`, `cr:CFR_21_Part_11`, `cr:EU_CTR_536_2014`) open the door to jurisdiction-scoped compliance queries — *"which studies processing EU subject data are governed by GDPR?"* — once `top:governedBy` is fully implemented.

**Cons / Gaps:**
- No lawful basis declaration. GDPR Article 6 requires a documented lawful basis for every processing activity. Clinical trial data processing is typically Article 9(2)(j) (scientific research) — but this is not declared anywhere in the model. A DPO cannot demonstrate GDPR compliance without it.
- No Data Processing Agreement (DPA) model. Under GDPR Article 28, every CRO, central lab, and data processor must have a signed DPA with the sponsor. The graph models the CRO as a `cr:CRO` organisation but has no concept of the legal agreement governing what they can do with the data they receive.
- No Data Protection Impact Assessment (DPIA) linkage. High-risk processing (large-scale health data, systematic profiling) requires a DPIA under GDPR Article 35. Clinical trials qualify. The graph has no `cr:DPIA` class or link from a study to its DPIA.
- Cross-border data transfer mechanisms are absent. A study running in the EU with a US-based sponsor processing data on AWS (even in EU regions) requires a transfer mechanism (Standard Contractual Clauses, adequacy decision). There is no `cr:DataTransferMechanism` property or entity.
- The retention and deletion lifecycle is unmodeled. ICH E6(R3) requires trial records to be retained for 15 years (or longer for paediatric studies). GDPR requires data to be deleted when the purpose expires. These two obligations are in tension for health data, and neither is represented in the graph.
- No breach notification workflow. GDPR Article 33 requires notification to the supervisory authority within 72 hours of a personal data breach. There is no `cr:DataBreach` class, no `cr:SupervisoryAuthority` entity, and no notification timeline modeled.

**Wishlist:**
- A `cr:LawfulBasis` class (a `top:RegulatoryLaw` subclass) with instances for GDPR Article 6(1)(a) through (f) and Article 9(2)(a) through (j), linked from `cr:Study` via `top:governedBy`.
- A `cr:DataProcessingAgreement` class (subClassOf `top:Evidence, top:Versioned`) with `processorOrg` (→ `cr:CRO` or `hcls:Organization`), `controllerOrg` (→ `cr:Sponsor`), `effectiveDate`, and `processingPurposes` (→ `cr:LawfulBasis` instances).
- A `cr:RetentionPolicy` class linked from `cr:Study`, carrying `retentionPeriod` (xsd:duration), `retentionBasis` (the regulatory requirement IRI), and `deletionEligibleAfter` (computed from study close date + retention period).
- A `cr:DataSubjectRequest` class for DSAR, erasure, rectification, and portability requests — linked to `hcls:Person`, timestamped, with a `requestStatus` lifecycle and a `responseDeadline` computed from the request date (30 days under GDPR).
- A SPARQL query template for the DPO: *"for a given study, list all organisations that process personal data, the legal basis for each processing activity, the applicable DPA, and the data transfer mechanism if cross-border."*

---

## 21. DevOps / Platform Engineer / SRE

**What they see when they look at the graph:**
An application that wants to run on managed infrastructure but has not yet been designed for it. The AWS Garnet CDK reference architecture is a starting point, not an operations manual. A platform engineer's job is to make the system reliable, observable, deployable, and — in a GxP environment — validated. Every one of those dimensions requires work beyond what is currently specified.

**Pros:**
- The Python build chain (`build_dist.py`, `build_docs.py`) is deterministic and dependency-light. A CI/CD pipeline that runs these scripts and verifies SHA256SUMS between runs can detect accidental ontology changes as a diff in the checksum file. That is a rudimentary but real change-detection mechanism.
- The SHA256SUMS artifact is a natural pin point for an infrastructure deployment: a Terraform or CDK module can fetch `top-cr-v1.ttl` and verify its checksum before loading it into the graph store, failing the deployment if the checksum does not match the pinned value.
- The three-format distribution (Turtle, JSON-LD, N-Triples) means the deployment pipeline can choose the format that loads fastest into the target store (N-Triples for Blazegraph/Jena bulk load; JSON-LD for Scorpio entity ingest; Turtle for human review of what was deployed).
- AWS Garnet as a CDK reference architecture means the infrastructure-as-code is already in a deployable form. A platform engineer can fork the CDK stack, parameterise it for a specific account, and deploy to a VPC without starting from scratch.
- The NGSI-LD context endpoint (`top-cr-v1.ngsi-context.jsonld`) is a static file — deployable as an S3 object behind CloudFront with a 1-year cache header and versioned object key. No application server required.

**Cons / Gaps:**
- No GxP computer systems validation (CSV) package. Running clinical trial data through a system under 21 CFR Part 11 / Annex 11 requires documented IQ (Installation Qualification), OQ (Operational Qualification), and PQ (Performance Qualification). None of these exist for the Garnet/Scorpio stack.
- No change control procedure. The ontology will evolve. In a GxP environment, every change to a validated system requires a documented change request, impact assessment, regression test, and approval before deployment. There is no `CHANGELOG.md`, no semantic versioning strategy (the project is at `v1` with no plan for `v1.1`), and no change control SOP.
- No observability design. How does a platform engineer know the Scorpio broker is healthy? There are no defined health check endpoints documented, no metrics to scrape (entity count by type, ingest latency, query response time), no structured logging format, and no alerting thresholds.
- No disaster recovery / business continuity plan. If the Scorpio broker loses its database, what is the recovery procedure? The ontology can be reloaded from the Turtle bundle; the instance data (the actual trial entities) has no backup strategy documented.
- No infrastructure cost model. The "community runtime" on AWS Garnet has no sizing guidance. How many Scorpio instances for 10,000 entities? For 1,000,000? What RDS instance class for the Scorpio PostgreSQL backend? A platform engineer cannot capacity-plan without this.
- Secrets management is unaddressed. The `cr:Enrollment` keychain (the PII bridge), database credentials for Scorpio's PostgreSQL backend, and API keys for EDC integrations all require secure storage (AWS Secrets Manager, HashiCorp Vault). None of this is specified.

**Wishlist:**
- A CSV package template: IQ/OQ/PQ test scripts for the Scorpio broker deployment, covering entity ingest, query response, subscription delivery, and context resolution — structured as a GAMP 5 Category 4 configured product validation.
- A `CHANGELOG.md` with semantic versioning: `v1.0.0` for the current state, with a documented policy for `MAJOR.MINOR.PATCH` increments — MAJOR for breaking IRI changes, MINOR for additive classes/properties, PATCH for comment and label corrections.
- A Terraform / CDK module with documented sizing parameters: instance type recommendations for Scorpio + PostgreSQL at three scales (pilot: <10K entities, phase 2: <1M entities, commercial: >1M entities), with estimated monthly AWS cost for each tier.
- A `docker-compose.yml` for local development: Scorpio broker + PostgreSQL + context file server + pre-loaded LY900018 fixture, with a `make start` target. This is the single highest-leverage piece of missing infrastructure for every downstream stakeholder.
- An observability stack specification: Prometheus metrics endpoints for Scorpio, Grafana dashboard template for entity ingest rate / query latency / error rate, and CloudWatch alarm thresholds for the production deployment.

---

## 22. Enterprise / Data Architect

**What they see when they look at the graph:**
A well-designed domain model that exists in isolation from the data estate it needs to connect to. Every large pharma sponsor has an enterprise data warehouse, a data lake or lakehouse, a Master Data Management system for organisations and sites, and a growing number of real-world evidence and analytics platforms. TOP is a new node in that network. An enterprise architect's job is to figure out how it connects to everything else — and currently, that question is entirely unanswered.

**Pros:**
- The stable URN scheme (`urn:ngsi-ld:top-cr:{Type}:{localId}`) is a natural foreign key for joining to an EDW. A sponsor's site master (`StudySite` dimension table) can carry a `top_cr_urn` column that links to the graph without rebuilding the EDW.
- The three-layer model (OWL / SHACL / NGSI-LD) maps reasonably well to a medallion architecture: the raw EDC export is the bronze layer; the NGSI-LD entities after transformation and SHACL validation are the silver layer; the SPARQL projections (SDTM, ADaM, FHIR) are the gold layer.
- The crosswalk layer (`cx:Mapping`) is a data lineage artifact. Every canonical mapping from a sponsor field to a TOP entity is recorded with provenance — who mapped it, when, with what confidence. This is the kind of lineage metadata that data catalogue tools (Collibra, Alation, Atlan) ingest.
- The `top:observedAt` transaction timestamp on every entity is a natural watermark for incremental ETL. A downstream EDW that pulls from the NGSI-LD broker can use `observedAt > last_extraction_timestamp` as the incremental filter — standard change data capture semantics.
- The NGSI-LD broker's REST API is a standard integration interface. Any iPaaS platform (MuleSoft, Azure Data Factory, Boomi) can poll `GET /ngsi-ld/v1/entities?type=cr:AdverseEvent&q=observedAt>2026-01-01` without a custom connector.

**Cons / Gaps:**
- No MDM alignment. A sponsor's organisation MDM holds the authoritative record for CROs, sites, and investigators. `cr:StudySite` in the graph is a local entity; it is not linked to the MDM's site ID. When the same site appears in three studies with three different local IDs, there is no deduplication mechanism.
- No data catalogue integration. The ontology is a natural fit for a data catalogue (every class is a business term with a definition; every property is a data element with domain and range). But there is no `dcat:Dataset` declaration, no `dcat:Catalog` entry, and no Dublin Core `dcterms:subject` linking to a controlled business glossary.
- No data lineage model beyond the crosswalk. The path from a raw EDC field → `cx:Mapping` → TOP entity → SPARQL projection → ADaM dataset → submission is not represented end-to-end as a lineage graph. OpenLineage or W3C PROV could carry this, but neither is wired in.
- No integration pattern for the EDW. How does a sponsor's Snowflake or Databricks lakehouse consume entities from the NGSI-LD broker? Polling? Kafka notification stream from Scorpio subscriptions? An AWS Glue connector? None of this is specified.
- No master data strategy for shared reference entities. `cr:Sponsor`, `cr:CRO`, and `cr:StudySite` will appear across many studies. Without a governance process for who creates these entities, when, and how they are deduplicated against the MDM, the graph will accumulate duplicates.

**Wishlist:**
- A `dcat:Dataset` and `dcat:Catalog` declaration wrapping the TOP CR distribution, making the ontology discoverable in enterprise data catalogues via DCAT-AP.
- An MDM alignment pattern: a `cr:MasterSiteID` property on `cr:StudySite` that carries the sponsor's MDM identifier, enabling graph-to-EDW joins without re-keying. Analogous properties for `cr:Sponsor`, `cr:CRO`, and `hcls:Person` (investigator registry ID).
- An OpenLineage dataset specification: the USDM transformer emits an OpenLineage `RunEvent` that records the input (`ly900018-usdm-v4.json`), the output (102 NGSI-LD entity files), and the transformation version — feeding any lineage-aware catalogue automatically.
- A Scorpio → Kafka bridge configuration: Scorpio supports NGSI-LD Subscriptions that POST to a webhook; a Kafka Connect sink can receive those POSTs and publish entity change events to a Kafka topic, making the graph a real-time CDC source for Snowflake, Databricks, or any downstream consumer.
- A data mesh alignment document: which TOP entities are the domain's data products (Study, ProtocolVersion, Enrollment, AdverseEvent), who owns each product (the domain team), what the SLA is, and how each product is discoverable via the enterprise data mesh portal.

---

## 23. AI / ML Engineer

**What they see when they look at the graph:**
An exceptionally well-structured knowledge graph that is a natural substrate for graph-augmented AI — but one that currently has no ML pipeline, no vector index, no embedding strategy, and no inference serving layer. The model is correct about what LLM-assisted mapping should look like (`top:AutonomousAgent` produces `top:Conclusion` with `top:confidence` and `top:rationale`); the pipeline that makes this real does not exist.

**Pros:**
- The knowledge graph structure (entities, typed relationships, coded properties) is the ideal input for a Graph RAG (Retrieval-Augmented Generation) pipeline. A question like *"What eligibility criteria apply to a patient with stage III NSCLC and prior platinum therapy under protocol LY900018?"* can be answered by retrieving the relevant `cr:EligibilityCriterion` nodes from the graph and passing them as context to an LLM — much more reliably than asking the LLM to recall protocol details from parametric memory.
- `top:Conclusion` with `top:confidence`, `top:rationale`, and `top:concludesAbout` is the right output schema for an LLM inference step. The model already knows that machine-produced conclusions are distinct from human-attested evidence, and that confidence is a first-class property. Most ML systems bolt this on as metadata; here it is in the ontology.
- `top:AutonomousAgent` as a `prov:SoftwareAgent` subclass means every LLM invocation can be represented as a named agent in the graph, with a version, a model IRI, and a `prov:wasAssociatedWith` link to the conclusion it produced. This is full inference provenance — rare in practice.
- The `cx:mappingConfidence` + `cx:reviewStatus` lifecycle for field mappings is a human-in-the-loop confirmation workflow — exactly the pattern that responsible AI deployment requires for high-stakes applications. The model demands human confirmation before an LLM mapping is promoted to canonical.
- The NGSI-LD entity structure (flat JSON with Property/Relationship nodes) is more LLM-friendly than raw Turtle. An LLM given an NGSI-LD entity payload as context needs no RDF parsing — it reads the JSON directly. The `@context` compacts IRIs to human-readable short names (`sponsoredBy` not `https://top.scientix.ai/cr/v1#sponsoredBy`).

**Cons / Gaps:**
- No vector index. Graph RAG requires a vector embedding of entity descriptions (and optionally of the graph structure) to support semantic search — *"find the eligibility criterion closest in meaning to 'prior platinum-containing chemotherapy'"*. Neither the broker nor the triple store has a vector index, and no embedding strategy is specified.
- No LLM pipeline. `cx:inferredBy → top:AutonomousAgent` is a provenance claim; there is no actual LLM call, no prompt template, no model selection, and no output parsing that fills in `top:confidence` and `top:rationale`. The inference model is designed but unbuilt.
- No feature store design. The graph is rich in structured features for ML (site characteristics, enrollment timing, AE rates by arm, protocol amendment history) but there is no feature extraction layer, no training dataset construction query, and no model-to-entity feedback path for writing predictions back to the graph.
- `top:Conclusion` is missing `top:promptTemplate` and `top:sourceContext` (the input the LLM reasoned over). Without capturing the input, conclusions are not reproducible — a critical failure for regulated use cases where a regulator may ask "show me exactly what the model saw when it made this determination."
- No Graph Neural Network (GNN) design. The relationship structure (Study → ProtocolVersion → EligibilityCriterion; Study → StudySite → Enrollment → StudySubject → AdverseEvent) is a natural multi-relational graph for link prediction (predicting protocol deviation risk at a site) or node classification (predicting DLT likelihood for a subject). None of this is articulated.

**Wishlist:**
- A Graph RAG recipe for the canonical use case: *"Given a patient's medical history as FHIR Observations, retrieve relevant eligibility criteria from the TOP graph and ask an LLM whether the patient qualifies."* This is achievable today with the existing graph structure and a vector index over `cr:EligibilityCriterion.criterionText`.
- A `top:Conclusion` property extension: `top:promptTemplate` (the instruction given to the model, by IRI to a versioned template), `top:sourceContext` (the input excerpt, as a structured reference or hash), and `top:modelVersion` (the LLM model IRI and version — e.g., `anthropic:claude-sonnet-5`).
- A vector index specification: which entity properties to embed (`rdfs:label`, `rdfs:comment`, `criterionText`, `rationale`), which embedding model to use, and how the index is queried alongside the graph (hybrid retrieval: graph traversal for structure + vector search for semantics).
- A feedback loop design: when a human reviewer changes `cx:reviewStatus` from `proposed` to `confirmed` or `rejected`, that signal should be captured as a training example for fine-tuning or RLHF on the mapping model. The graph already has the structure for this; it needs a pipeline.
- A GNN experiment specification for at least one prediction task: predicting site enrollment underperformance from the graph of site characteristics, protocol complexity, historical delegation patterns, and AE rates — using the graph structure as the feature space, not a flat table.

---

## What this is, honestly

This is a **design-time specification and integration contract**, not yet an operational system. It is the kind of artifact that, in a large sponsor, would be produced by an Architecture Review Board and then handed to vendors to implement against. The ontology is mature. The crosswalks are honest. The transformer is a proof-of-concept. The runtime is a reference architecture.

The gap between *this* and *a running system processing real trial data* is: (a) one validated GxP deployment, (b) one CRO willing to export in USDM format, and (c) one sponsor data engineering team willing to run the ingestion pipeline. None of those are ontology problems.

*Generated from the TOP CR domain v1 branch, June 2026.*
