# TOP CR Domain

Operator-led, provenance-native, **bitemporal** reference knowledge graph for the
clinical-research lifecycle. Founding domain for TOP (The Ontology Project).

This reference knowledge graph is built **incrementally, sub-domain by sub-domain**. Every increment ships
operator-perspective worked examples and a regression-gated test suite:
**the full suite must stay green before new work lands.**

## Layout
```
cr-domain/
  ontology/      # top-core stub + hcls-core + cr-core (specialize the 8 CLOs)
  shapes/        # SHACL shapes (constraints, graded by severity)
  examples/      # operator-perspective instance data (the worked examples)
  tests/         # run_tests.py harness + manifest.json (grows with each sub-domain)
  conventions.md # bitemporal + PROV envelope conventions
```

## Documentation (start here)
Human-readable, value-first docs (auto-generated from the model, so they never drift):
```
python3 cr-domain/docs/build_dist.py      # (re)build downloadable serializations into docs/dist/
python3 cr-domain/docs/build_docs.py      # regenerate the site after model changes
open cr-domain/docs/index.html            # hub; one page per flow/sub-domain
```
A multi-page site: a hub (what it is / value / how-to-use), a Foundation page (the 8-category
model + Universal DNA + bitemporal/PROV/PII spine, with the **masthead**: version, license,
authorship, citation, and download badges), **one page per flow/sub-domain** (each with its
operator screen, entities, constraints, and views), and a full auto-generated reference.

**Serializations (the rigor layer).** `build_dist.py` merges the ontology modules into one
self-describing artifact (stamped with `owl:Ontology` masthead metadata) and emits it in three
**byte-reproducible** formats — Turtle, JSON-LD, N-Triples — plus separate bundles for the SHACL
shapes and the external crosswalks, into `docs/dist/`. All formats round-trip to identical triple
counts. Builds are **deterministic**: blank-node labels are canonicalized, N-Triples lines sorted,
and JSON-LD keys/arrays normalized, so rebuilding yields identical bytes (and an identical
`SHA256SUMS`). RDF/XML is intentionally not published — rdflib's RDF/XML serializer is not
byte-reproducible, and Turtle is OWL-complete; tools needing RDF/XML can convert from any format.
Masthead constants (version `v1` · `Apache-2.0` · ScientixAI · namespace `top.scientix.ai/cr/v1`)
live in `build_dist.py` as the single source of truth, imported by `build_docs.py`. A
`SHA256SUMS` file is emitted alongside the artifacts so **downstream consumers can pin by
checksum** (verify with `sha256sum -c SHA256SUMS` in `docs/dist/`).

Two JSON-LD artifacts are provided, deliberately:
- **`top-cr-v1.jsonld`** — plain **RDF/JSON-LD**: the model itself (the triples).
- **`top-cr-v1.ngsi-context.jsonld`** — an **NGSI-LD `@context`**: a term→IRI dictionary for the
  domain vocabulary, layered over the NGSI-LD core context, for loading entities into a broker.
  `top:observedAt` deliberately resolves to NGSI-LD core `observedAt` (valid time). This is the
  generic vocabulary context (not IP); NGSI-LD entity *shaping* (Property/Relationship nodes,
  attribute-level temporals) is downstream integration work, not a copy step.

## Run the tests
```
python3 cr-domain/tests/run_tests.py
```
The harness (a) structurally parses every `ontology/` and `shapes/` file, and
(b) SHACL-validates every example in `tests/manifest.json`, asserting each either
**conforms** or **violates** as declared (negative tests prove the shapes bite).

CI runs the full harness on every push/PR (`.github/workflows/ci.yml`) — so every change to
the reference graph is gated. The harness must exit 0 before new work lands.

## Coverage (all green — `python3 cr-domain/tests/run_tests.py`)
- **Foundations & governance** ✅ project scaffolding, conventions, TOP-Core stub, harness, smoke test.
- **Operator model** ✅ hcls-core + cr-core; oncology FIH worked example end-to-end.
- **Graded constraints & bitemporal integrity** ✅ delegation/credential invariant (Violation vs risk-proportionate Warning); as-of reconstruction; back-dating detection.
- **Edge projections** ✅ CDISC SDTM (DM/AE), USDM, FHIR ResearchSubject, DOA log — all as views.
- **Crosswalk & curation** ✅ owned SSSOM mappings with **verified** target IRIs (OAE/OBI, confirmed against source); hardened gate (controlled predicate + semapv justification + confidence + date + author + verification status + PROV); SSSOM TSV export projection.
- **Projection demo** ✅ standards/log views + regulator-query over one native graph. `python3 cr-domain/demo/demo.py`
- **Pre-IND gate** ✅ IND-enabling narrative coherence (unaddressed animal tox = Violation), vague-question Warning, IND 30-day review clock (bitemporal).
- **EOP2 gate** ✅ efficacy traceability (overstatement guard), EOP2 readiness, Project Optimus, SDTM EX.
- **Pharmacovigilance** ✅ SAE expedited 15-day reporting clock (bitemporal compliance).
- **ADaM traceability** ✅ analysis result → ADaM dataset → native source (prov:wasDerivedFrom); orphan dataset = Violation; lineage projection reproduces the number to source.
- **PII containment** ✅ pseudonymized-not-anonymized; `cr:forSubject` must reference a StudySubject, never a Person (leak = Violation); Person is the boundary-only PII layer, Enrollment is the only legal bridge.
- **Site EDC + data fidelity** ✅ CDISC ODM EAV capture (event→CRF→itemgroup→item→observation, OIDs); query/discrepancy + SDV; PHI classification (Warning if unclassified); data-mart projection (EAV→flat). Operator-context sources in `SOURCES.md`.
- **Biospecimen / LIMS lineage** ✅ bitemporal custody chain (state machine → current-state derivation); aliquot/partition lineage (`prov:wasDerivedFrom`); AnalysisService/Request/AssayResult; blood-draw traceback projection (result → aliquot → primary → draw).
- **RBQM** ✅ risk-based monitoring: high-risk CtQ factor must be mitigated (Violation); 100% SDV on low-risk = over-monitoring (Warning); risk-targeted monitoring-allocation projection (risk level → SDV intensity).
- **Site activation / start-up** ✅ activation requires IRB approval + executed CTA + SIV (Violation if premature); enrollment-before-activation flagged preventively (bitemporal); start-up tracker projection (IRB→CTA→SIV→activated timeline).
- **Study start-up package** ✅ the documents a site receives at award, modeled as typed artifacts (via the TMF artifact-type scheme) + the three site work streams (regulatory, budget & contracting, clinops) that consume them and produce site-specific outputs (customized ICF, DoA log, signed CTA); regulatory + budget completion gates the SIV (Violation if premature); every output traces (`prov:wasDerivedFrom`) to its source document (Warning if not); readiness projection. The site-operations companion to the sponsor-side protocol model.
- **Schedule of Activities (bitemporal SoA)** ✅ the footnote-laden 2D table modeled as a timeline across three strata — planned template (windows, relative timing, ordering, repeats) → participant projection (windows resolved off the anchor) → actual execution; out-of-window visit = Warning, broken hard ordering = Violation; **as-of reconstruction across a protocol amendment** + missed-visit detection (what a static SoA cannot do); SoA-table and planned-vs-actual reconciliation projections (the table is a *view* of the timeline).
- **Deviations & CAPA** ✅ the chain most CR models skip — CtQ factor ← *antecedent* (the missing middle) → deviation event → CAPA; significant (critical/major) deviation with no CAPA = Violation (ICH E6 obligation as a shape); deviation with no recorded antecedent = governance Warning; risk signal flags an antecedent; deviation-lineage projection (CAPA → deviation → antecedent → CtQ factor).
- **TMF document binding** ✅ a SKOS artifact-type scheme aligned (by name) to the DIA TMF Reference Model + content-bridge properties (`records`/`documents`/`defines`) from each artifact type to the `cr:` domain class it concerns; classified-but-unbound artifact type = Warning (filing label, not comprehension); binding-map projection. Commons owns the map; runtime classification/extraction is the consuming system (out of scope).
- **GCP & essential records (ICH E6(R3))** ✅ the governance vocabulary no existing ontology owns — essential record, source data/document, audit trail, certified copy, TMF, plus IRB/IEC + service-provider actors — encoded *descriptively* (`rdfs:isDefinedBy` E6(R3), paraphrased not copied) with a SKOS glossary; obligations stay in the shapes (certified-copy must reference its source = Violation; source data with no audit-trail node = ALCOA++ Warning); certified-copy register projection. The authoritative anchor under the TMF binding.

- **Universal DNA alignment** ✅ aligned to canonical TOP Core: one `top:Core` root above the 8 CLOs; every entity carries the Universal DNA — `top:identifier` (identity) + `top:observedAt` (time, canonical NGSI-LD term) + `top:status` (lifecycle); `top:UniversalDNAShape` enforces it (conformant + negative test).
- **Single-pull retrieval views (NGSI-LD, no recursive lookups) — every applicable screen** ✅ the test of the model: an operator pulls **one** entity and gets *every* fact behind the green check, inlined into **one self-contained object** — proven across the whole workflow line (**site activation, delegation, enrollment, consent, blood draw, EDC capture, adverse event, EOP2 gate, study start-up, risk-based monitoring, deviation & CAPA, essential records**). Faithful to **ETSI GS CIM 009** Linked Entity Retrieval: `?join=inline&joinLevel=3` embeds each linked Entity as the `entity` sub-attribute of its Relationship (clause 4.5.23.2), following relationships **forward** only (clause 4.5.23.1). That forward-only rule drove **modeling corrections** — direct forward retrieval edges where the graph pointed the wrong way (`cr:hasConsent`/`cr:producesSpecimen`/`cr:hasCustodyEvent`/`cr:hasAliquot`/`cr:yieldsResult`/`cr:precededByAct` for the draw; `cr:hasQuery` for EDC; `cr:reviewsResult`/`cr:concernsStudy` for EOP2; `cr:activationPackage` for start-up) so each object is reachable by a *stock broker* `join`, not a materialized inverse view. Each screen has a **SHACL retrieval view** (`views/`) that is the attribute projection (the `pick`/`attrs` the screen consumes); `tools/ngsild_view.py` walks them and emits the exact objects the docs render. The blood-draw view is the deep showcase (each green check cites the `reads` path into the one object). Guarded by `view 13/13`.

- **OWL DL well-formedness gate (ingredients, not the cake)** ✅ the reference does **not** run a reasoner — classification/entailment is the consumer's job — but a cheap, pure-Python **structural** gate (`tools/owl_lint.py`, no reasoner, no Java) proves the authored OWL is *sound ingredients* for someone else's reasoner: no illegal punning, every owned term declared, every `domain`/`range` well-typed, no `subClassOf`∩`disjointWith` contradiction. The gate **provably bites** (self-test on a crafted broken ontology). Consuming it — how to point HermiT/ELK/owlrl at the OWL, and how NGSI-LD serves the result — is documented in the **Implementation guide** (§5 Reason, §6 Serve).

Current suite: SHACL 56/56 · bitemporal 3/3 · projections 18/18 · demo 1/1 · safety 2/2 · pre-IND 2/2 · lims 1/1 · startup 2/2 · schedule 3/3 · usdm 1/1 · ncit 1/1 · view 13/13 · owl-lint 2/2.

> Brand note: the substrate/runtime is referred to functionally; TOP is the open commons.
> `ontology/top-core.ttl` is a **local working stub** aligned to the canonical Apache-2.0
> TOP Core (`github.com/scientixai/the-ontology-project`): one root (`top:Core`) + 8 CLOs +
> Universal DNA (identifier + observedAt + status). Not the authoritative source.

## Attribution & licensing
This work is licensed under **Apache-2.0** (the original ontology, shapes, projections, and code).
Full third-party attributions are in [`NOTICE`](./NOTICE). In particular:

> **ICH E6(R3).** The GCP definitional layer (`ontology/cr-core-gcp.ttl`) is an **independent
> derivative adaptation** of the ICH E6(R3) Good Clinical Practice Guideline (Step 4, Jan 2025;
> Principles, Glossary, Annex 1 — Annex 2 not modeled). It is **not endorsed or sponsored by ICH**.
> The original ICH E6(R3) document is copyright © ICH. Definitions are **paraphrased, not copied**;
> changes are labeled (OWL/SKOS structure, obligations as SHACL); no ICH logo is used.
> **DIA TMF Reference Model** is aligned by name only (licensed artifact; no text reproduced).

## Scope boundary — reference KG vs. runtime/agents (decided 2026-06-20)
This repo builds a **reference knowledge graph (an asset)**, not a runtime or agent product.

- **In scope:** the layered ontology (TOP/HCLS/CR-core), graded constraints (SHACL),
  edge-projection *definitions*, crosswalks (SSSOM), operator worked examples, conventions.
- **Out of scope:** agent orchestration / LLM pipelines, the broker/runtime, notification &
  attestation fabric.
- **`demo/` is a projection demonstration only** — it runs the in-scope projection queries
  over a native example graph; it constructs nothing.
- **Worked examples are static reference illustrations, not a running deployment.** A live,
  deployable proof-of-concept that ingests a USDM/M11 protocol and serves it as a running
  NGSI-LD knowledge graph (e.g. on the AWS Garnet Framework) is built in a **separate
  repository** — out of scope here. `examples/usdm-cdisc-pilot-conformant.ttl` shows the
  TOP-grounded project graph such a constructor would produce, validated against the model.

The reference serves agents by being excellent **grounding** (complete model, constraints,
projections, crosswalks, examples) — not by containing the agents or any runtime.
