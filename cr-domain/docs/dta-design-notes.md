# DTA / DTS extension — design notes & answers to the open modeling questions

Companion to `ontology/dta-module.ttl`, `shapes/dta-*.ttl`, `crosswalks/dta-*`,
`projections/dta_*.rq`, and `examples/dta-lab-safety/`. This is the reasoning
layer: what was built, why, and how each open modeling question from the handoff
(§11) is answered — including the vendor-connector research that grounds the
answers to Q1–Q2 and the USDM transfer-timing gap in Q4.

## The one thing kept right

The DTA working group is building a **better document** — a machine-readable,
USDM-prepopulated DTA/DTS a human still re-authors *per sponsor × vendor × data
type × amendment*, terminating in a hand-built SDTM map. That is a faster horse:
it lowers the cost of one interpretation node without reducing their **number**.

This module designs the interpretation node **out**, and the shapes are written
so that any concept which merely *stores* a manual mapping fails the test:

| DTA-group model (not copied) | What this module builds |
|---|---|
| `ENCOUNTER_MAPPING` stored per DTA | `cr:VendorAlias` — a resolution edge (`cr:aliasResolvesTo` + `cr:resolvedFrom` + confidence), resolved once; the corpus compounds (`crosswalks/dta-encounter-alias.sssom.tsv`) |
| Sponsor hand-authors content into SDTM | `cr:DataElementSpecification` binds to a `cr:BiomedicalConcept`; SDTM `LB` is a **projection** (`projections/dta_sdtm_lb.rq`) |
| Reconciliation/conformance/QC = human process, cut from MVP | Executable SHACL (`shapes/dta-*.ttl`), graded Violation/Warning/Info, run at ingestion |
| Signature = a field; blinding = a boolean; amendment = a re-author | `cr:Attestation` (credential-backed), `cr:BlindingConstraint` (scope+provenance), `cr:TransferAmendment` (bitemporal, propagation forced by shape) |

## Answers to the open modeling questions (§11)

### Q1 — Multi-vendor / multi-scope DTA → model scope explicitly from the start
Adopted the `cr:TransferScope` mediator: one `cr:DataTransferAgreement`
`cr:forDataScope` → N `cr:TransferScope`, each binding a vendor
(`cr:scopeVendor`) and its `cr:TransferSpecification` (`cr:scopeSpecification`).
The single-vendor simplification is exactly where the DTA group's combinatorics
hide, so scope is a first-class node even in the single-vendor worked example.

**Research that grounds this (per the user's steer to look at real EDC APIs):**
the vendors most likely to sit at multiple scopes all expose a Study→Site→
Subject→Event→Form→Item hierarchy under one account, which is precisely why a
DTA spanning several of a vendor's data streams needs an explicit scope node
rather than a repeated agreement:

| Vendor | Public API | Data-model hierarchy (verified terms) | Notes for scope modeling |
|---|---|---|---|
| **Castor EDC** | OAuth2 client-credentials REST, published Swagger (`data.castoredc.com/api`) | `study` → `institute`(site) → `participant` → `visit` → `form` → `field` → `data-point` | `visit` carries `visit_name`/`visit_number`/`visit_order` — ideal alias-corpus keys |
| **Veeva Vault CDMS** | Versioned REST (`developer-cdms.veevavault.com`), async Study Data Extract job | `Study` → `Study Country` → `Site` → `Subject`/`Casebook` → `Event Group` → `Event` → `Form` → `Item Group` → `Item` | `SYS_EVT` extract + `use_external_ids` give stable cross-study visit keys |
| **Medidata Rave (RWS)** | HTTP + CDISC ODM 1.3 (`learn.medidata.com`) | ODM `StudyEventDef`/`FormDef`/`ItemGroupDef`/`ItemDef` + `CodeList` | `mdsol:TargetDays`/`StartWinDays`/`EndWinDays` are real visit **windows** — feed `cr:transferSchedule` + SoA windows |
| **Oracle Clinical One** | OAuth2 REST, ODM-XML extract (`docs.oracle.com/.../coapi`) | study → version → visit → form → form-item | `IntegrationVisit.visitRefname`/`visitTitle` are the label→canonical mapping keys |

The four are captured as `cr:VendorConnectorProfile` instances in
`examples/dta-lab-safety/vendor-connectors.ttl`, each carrying CT-valid
`cr:fileFormat`/`cr:transmissionMethod`/`cr:transmissionType` plus
`cr:vendorApiStyle` and a `cr:vendorDocumentation` URL for provenance.

### Q2 — `TransferProfile` placement: Scope vs Constraint → **both**, as recommended
`cr:TransferProfile` is a `top:Scope` (the operational *declaration* the DTA
references). Its validity is *enforced* by `top:Constraint`-style SHACL
(`shapes/dta-profile.ttl`): mandatory `fileFormat`/`transmissionMethod`/
`transmissionType` in controlled terminology (Violation), blinding scope
(Warning), schedule (Info). Declaration lives in the graph; enforcement lives in
the shapes — the user's chosen split. The vendor connectors (Q1) are the
concrete "connectors under the transfer-profile placement" the user asked for.

### Q3 — `DataElementSpecification` grain: per-file vs per-spec
Resolved as the user framed it: **everything is anchored around a USDM
protocol**, so the grain is **per-spec** (the DTS is the unit of content
definition, `cr:specForStudy` → the USDM `cr:Study` by IRI). When method or
schedule genuinely vary by file, that is a *TransferProfile* difference, not a
content difference — model a second `cr:TransferProfile` (or a per-file
`cr:TransferFile` carrying its own lifecycle timestamps), leaving the
`cr:DataElementSpecification` grain stable. This keeps content and operational
variance on separate axes instead of multiplying the element list per file.

### Q4 — Reuse-vs-extend USDM; transfer frequency/timing is genuinely new
USDM does **not** model transfer frequency/timing, so this module owns it:
`cr:transferSchedule` on `cr:TransferProfile`, and `cr:TransferAmendment` with
`cr:effectiveFrom`/`cr:effectiveTo`. This is a clean win because **temporal is
native to TOP** — cadence, windows, and the full transfer lifecycle
(`cr:specimenCollectedAt` → `cr:specimenReceivedAt` → `cr:analysisCompletedAt` →
`cr:reportGeneratedAt` → `cr:clinicalReviewAt`) are first-class, independently
queryable properties, not prose in a Word cell. Everything else that USDM *does*
own (Study, Organization, Encounter, StudyRole, Amendment) is **referenced by
IRI**, not re-authored (`cr:specForStudy` deliberately has no forced range so the
study's definition stays in the USDM graph).

Real vendor visit-window data confirms the value of native timing: Medidata's
`mdsol:StartWinDays`/`TargetDays`/`EndWinDays` and Castor's `visit_duration`
are exactly the offsets a transfer schedule must respect, and they map onto
TOP's SoA windows rather than a free-text "weekly" note.

### Q5 — Legal layer stays out of scope; reference the document
Confirmed and implemented as the user described: the binding legal contract stays
a prose/DocuSign artifact. TOP Core **has** a document concept (`top:Evidence`),
so the sample response points to one: `cr:referencesLegalDocument` → a
`top:Evidence` document, pinned by `cr:documentHash` (URI + hash + version). We
**reference** the document; we do **not** model liability/indemnification. The
`cr:DTALegalReferenceShape` warns if a referenced legal document is not hash-
pinned, so the reference cannot silently drift.

### Q6 — The uncovered tail (imaging / eCOA / DHT / genomics)
For data with no open-source identifier, the binding is **vendor-certified once
at the catalog**, still bind-once-reuse, and the attestation path is **first-
class, not an exception**: `cr:VendorAlias cr:resolutionAttestedBy` →
`cr:Attestation`. The resolution shape (`cr:VendorAliasResolvedShape`) admits an
alias that is *either* auto-resolved *or* attested — so an imaging analyte with
no LOINC code is conformant precisely when a clinician has attested it.

This matches how imaging actually arrives (per the user): DICOM carries metadata
and the radiologist's notes, and any image entering the clinic is **reviewed by
the PI** — so the clinician attestation genuinely exists and is captured as the
`cr:Attestation`, rather than being invented to satisfy the model.

## Central-lab & the FHIR lab-resource model (the corrected vendor tier)

The first vendor-research pass profiled **EDC** vendors (Castor, Veeva, Medidata,
Oracle). That is the *surrounding* context, not the DTA MVP target. The MVP
primary use case — central-lab **safety labs** — is a **HL7 FHIR R4** problem,
and the right vendor tier is the megalabs, the QHIN/aggregator middleware, and
the developer-first EHRs. This section corrects that framing, grounded in the
"Lab Vendor API Specs for CDISC" analysis, and it independently **validates the
whole design**: the CDISC 360i Digital DTA is itself "a machine-readable config,
generated from USDM, that runs CORE conformance + Dataset-JSON validation *at the
point of ingestion*" — i.e. exactly this module's SHACL-at-ingestion thesis, and
exactly the "Data Validation & Quality" layer the MVP inventory deferred.

### The FHIR request-report triad → TOP classes → SDTM LB
FHIR R4 normalizes lab data as a four-resource graph; the deterministic mapping
into SDTM LB is what the Digital DTA's "core mechanism" encodes
(`crosswalks/dta-to-external.ttl`):

| FHIR R4 resource | TOP class | SDTM LB projection |
|---|---|---|
| `ServiceRequest` (the order) | `cr:AnalysisRequest` | order → result traceability (`DiagnosticReport.basedOn`) |
| `Specimen` (the sample) | `cr:onSample` → `hcls:Specimen` | matrix type (`LBSPEC`) |
| `Observation` (atomic result) | `cr:AssayResult` | `Observation.code` → `LBLOINC`; `valueQuantity.value` → `LBSTRESN`; unit → `LBSTRESU`; interpretation flag → `LBNRIND` |
| `DiagnosticReport` (wrapper) | the transfer file / report | report status, effective time |

This maps 1:1 onto the Sodium worked example: the `cr:AssayResult` is the FHIR
`Observation`, its bound `cr:BiomedicalConcept` carries the LOINC code, and the
UCUM-canonical unit is `LBSTRESU`/`LBSTRESN` (standard units) vs the delivered
`LBORRES` (original) — the SI conversion the DTA has always had to enforce by
hand, here canonical.

### Vendor matrix (grounded; `examples/dta-lab-safety/fhir-lab-connectors.ttl`)

| Vendor | Tier | Surface | Delivery | Notes for the DTA |
|---|---|---|---|---|
| **Labcorp** | Megalab | FHIR R4 (`ServiceRequest`/`DiagnosticReport`/`Observation`/`Specimen`) + legacy EDI | FHIR-API; SFTP/HL7 v2 ORU | a Digital DTA can auto-generate the legacy EDI spec file too |
| **Quest (Quanum)** | Megalab | FHIR R4, OAuth2 auth-code + refresh | FHIR-API | replaces legacy SFTP batch; 21 CFR 11 / HIPAA |
| **Health Gorilla** | TEFCA QHIN | FHIR R4, OAuth2 bearer, resource-scoped scopes | FHIR-API, subscription | `OperationOutcome` errors → conformance handling; Lab Subscription = 2yr history + 72h updates (RWD) |
| **Redox** | Aggregator | Normalized "Results" JSON model | Webhook (New/NewUnsolicited/Query) | one model over 50+ EHRs; OAuth JWT |
| **Particle Health** | Aggregator | FHIR R4 + C-CDA + Delta | FHIR-API | `_include`/`_revinclude` bundles report + observations in one call |
| **Canvas Medical** | Dev-first EHR | FHIR R4 US Core, `$create-lab-report` | FHIR-API | date modifiers `ge`/`le` = **visit-window checking at the query layer**; DocumentReference superseded/current = audit trail |
| **Medplum** | Dev-first EHR (OSS) | FHIR R4 | FHIR-API | `basedOn`/`subject` linkage = SDTM traceability; ideal open "living lab" |
| **Akute Health** | Dev-first EHR | REST + webhooks | Webhook (201/202/400) | `interpretation_code` HH/LL flags; 5 concurrent-request cap → DTA must encode backoff |
| **Elation Health** | Dev-first EHR | FHIR R4 + HL7 ORM/ORU | FHIR-API | OAuth2 client-credentials; bi-directional |

Two of these produced concrete conformance-shape ideas worth a follow-up
(additive, not yet built): capturing the **abnormal-result flag** (HH/LL/H/L/
critical → SDTM `LBNRIND`) as a first-class property with a shape that routes
criticals, and encoding **API constraints** (Akute's 5-concurrent cap, Health
Gorilla's `OperationOutcome`) as part of the `cr:TransferProfile` so the pipeline
self-limits. Both extend the "conformance is executable" thesis onto the wire
protocol itself.

### CT addition
`cr:transmissionMethod` now includes `FHIR-API` and `Webhook` (the event-driven
delivery Akute/Redox/athenahealth/DrChrono use), alongside the file-drop methods.

## Deliverables map

| Path | Contents |
|---|---|
| `ontology/dta-module.ttl` | New leaves (§3.2) as additive subclasses of Core; transfer-lifecycle temporal props; `cr:resolvedFrom` binding provenance |
| `shapes/dta-content.ttl` | Concept-bound + UCUM-unit + coded-concept Violations; value-range Warning |
| `shapes/dta-resolution.ttl` | Unresolved-and-unattested Violation; low-confidence + version-drift Warnings |
| `shapes/dta-profile.ttl` | CT-enforced operational attrs (Violation); blinding scope (Warning); schedule (Info) |
| `shapes/dta-agreement.ttl` | DTA structure + credential-backed-signatory gate + amendment-propagation (Violation); legal hash-pin (Warning) |
| `crosswalks/dta-to-external.ttl` | LOINC 2951-2 / QUDT-UCUM / SDTM LB mappings, gate-validated (`shapes/crosswalk.ttl`) |
| `crosswalks/dta-encounter-alias.sssom.tsv` | The compounding vendor-visit alias corpus |
| `projections/dta_sdtm_lb.rq`, `dta_document.rq` | SDTM LB row + human-readable DTA document, rendered from the graph |
| `examples/dta-lab-safety/` | Sodium conformant trace, deliberately-broken counterpart, warning fixture, vendor connectors |

## Honest tiering (§7)

- **T1 (production-shaped today):** the human-readable DTA document and the
  Dataset-JSON-style content envelope are direct renders of graph facts.
- **T2 (structural automation complete; a human attestation step remains):**
  SDTM LB — the concept→`LBTESTCD` short-name choice and study-specific tail need
  an attestation; the projection renders the structural 60–75%, and the alias
  corpus grows the auto-resolved fraction over time.
- Not claimed as T1. The resolver's actual auto-resolve rate and calibration
  (§8) must be **measured** against the real vendor spreadsheets, not asserted —
  and the confident population acceptance-sampled, since a confidently-wrong
  binding that clears the gate is the lethal failure.

## Research caveat

Vendor facts above were gathered under an egress policy that blocked direct
fetches to most vendor domains; the strongest facts (Castor resource model,
Veeva SDE job + hierarchy, Medidata RWS ODM + `mdsol:` visit-window attributes,
Oracle ODM extract + `IntegrationVisit`) were verified against official client
libraries and CDISC/HL7 source data pulled from GitHub, and LOINC 2951-2 + UCUM
`mmol/L` were verified against HL7 FHIR package data and the `ucum-org/ucum`
essence file. Items that could not be verified are labelled as such in the
connector comments; connector defaults should be re-confirmed from an
unrestricted environment before production use.
