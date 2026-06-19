# TOP Foundations Bucket Strategy

*Status: pre-RFC strategic planning. Author: Bo Lora (BDFL, sole signatory to The Ontology Project as of 2026-05-14). Audience: future foundations working-group leads (Ali for physical-AI per Bo's 2026-05-14 signal; operational-management lead TBD), and HCLS / manufacturing / other-bucket leads whose workflows compose against foundations through smart-X compositions.*

*Companion to TOP Core, to `top-strategy-brief.md` (the architectural umbrella), to `top-workflows-strategy.md` (cross-bucket workflow discipline), and to `top-compositions-strategy.md` (how compositions reference foundations). Pre-RFC; the formal RFC process starts when the foundations working groups do.*

---

## Why this document exists

The foundations bucket is the cross-industry substrate that operational work runs on top of. Physical infrastructure: sensors, building automation, environmental control, access control, security, network. Operational management: HR, finance, procurement, quality, forecasting, scheduling. Hospitals use these layers, but so do offices, factories, warehouses, labs, retail stores, banks.

The bucket is named **foundations** (without the "smart" qualifier) because operational management is foundational without being inherently "smart" and the unqualified name reads more honestly. The parallel structure with the compositions namespace is the architectural clarifier: **foundations are the substrate; compositions are the assemblies built on top.**

This document captures the bucket's commitments. The two workflow extensions inside it (physical-AI and operational management) get their own seeds when they activate.

## What the foundations bucket holds

| Workflow extension | What it covers | Cross-industry reach | WG stewardship |
| --- | --- | --- | --- |
| **physical-AI** | Building infrastructure as a knowledge graph. Sensors, HVAC, lighting, security, access control, environmental monitoring, power, network, building automation. The physical substrate of any sufficiently large facility. | Hospital, factory, warehouse, office, lab, retail outlet, campus, infrastructure facility. | Ali (candidate WG lead, per Bo 2026-05-14). |
| **operational management** | Operational work that runs across any sufficiently large operation. HR, finance, procurement, quality, forecasting, scheduling, contracts, facilities, supply. The non-domain-specific operational layer. | Hospital, university, manufacturer, retailer, financial institution, anywhere operations exist at scale. | TBD. |

The bucket holds two workflow extensions, not one undifferentiated namespace. Physical-AI and operational management have different operator audiences (facilities engineers vs operations executives), different vocabulary, different standards landscapes, and different stewardship cohorts. Keeping them as separate workflow extensions inside one bucket preserves WG independence while signaling their shared role as substrate.

## Bucket-vs-sibling: one bucket or two?

Open question. Strawman:

- **One bucket (`foundations/`) with two workflow extensions inside.** `foundations/physical-ai/`, `foundations/operational/`. Shared CODEOWNERS at the bucket level for cross-extension RFC review. Each workflow extension has its own WG and its own CODEOWNERS at the workflow level.
- **Two top-level buckets** (`physical-ai/` and `operational/`). No bucket-level coordination; each workflow extension stands alone.

The one-bucket strawman is the current pick. Reasoning: physical-AI and operational deploy together so often (every smart-X composition references both) that bucket-level coordination has real value, and operationally they share a posture (cross-industry substrate that other workflows compose against). The strawman gets revisited if stewardship cohorts diverge enough that bucket-level coordination becomes friction rather than value. WG ratifies or restructures at activation time.

## Cross-industry reach

The bucket's defining property: every workflow extension inside it serves multiple buckets. Concretely, physical-AI is composed by:

- **HCLS bucket:** smart-hospital, smart-clinic, smart-lab compositions
- **Manufacturing bucket:** smart factory compositions
- **Future buckets:** smart office, smart warehouse, smart retail, smart campus

Operational management is composed by:

- **HCLS bucket:** smart-hospital, smart-clinic, value-based-care program compositions
- **Manufacturing bucket:** every manufacturing composition with ops dimensions
- **Future buckets:** any sufficiently large enterprise deployment

This is why foundations is its own bucket rather than living inside HCLS or any other domain bucket. Pulling it into HCLS would force manufacturing and future buckets to either duplicate the content (the FHIR mistake again) or to declare cross-bucket dependencies against HCLS classes, which is the wrong shape (HCLS isn't a substrate; HCLS is a domain bucket like any other).

## Composition relationships

Foundations workflow extensions are the most-composed-against artifacts in TOP. Every smart-X composition references at least one foundations workflow. The composition discipline (see `top-compositions-strategy.md`) is what keeps foundations classes from getting redeclared at the composition level: compositions reference foundations classes, never redeclare them.

This puts a specific obligation on foundations workflow extensions: their class definitions and SHACL shapes are designed for composability. Class names are operator-vocabulary precise but not domain-specific (a `Bed` class in physical-AI is just `Bed`, not `HospitalBed`; the hospital-specific semantics live in the composition or as a setting-type property on the instance). Properties are loose enough that compositions can constrain them tighter via SHACL without contradicting foundations.

The obligation is in tension with the practitioner-first axis. Physical-AI's operators are facilities engineers; their vocabulary is precise to the building. Operational management's operators are ops executives and middle managers; their vocabulary is precise to the function (HR, finance, procurement). Neither audience says "Bed" in the abstract; they say "ICU Bed" or "Patient Bed" or "Hospital Bed" in their contexts. The compromise: foundations workflow extensions use the most generic operator-vocabulary that's still operator-recognizable; compositions add the contextual specificity.

## What foundations workflow extensions will ship in v1 (anticipated)

Neither physical-AI nor operational management has activated yet. Anticipated v1 shapes:

**physical-AI v1:**
- 8 to 12 functional areas (sensors, HVAC, lighting, security, access control, environmental monitoring, power, network, building automation, alarms)
- Standards alignment via TBD (Haystack? ISO 16484 BACS? FIWARE Smart Buildings data models? RealEstateCore? The choice waits for Ali's read.)
- Cross-bucket Pattern B declarations against HCLS clinical-care (for medical-grade environmental requirements like surgical-suite air quality) when those crosses are operator-grounded

**operational management v1:**
- 10 to 15 functional areas (HR, finance, procurement, quality, forecasting, scheduling, contracts, facilities, supply, payroll, vendor management)
- Standards alignment via TBD (HR-XML? ISO 9001? Industry-specific frameworks?)
- Cross-bucket Pattern B declarations against HCLS, manufacturing, and other buckets where operator-grounded crosses appear

Both v1 scopes are speculative. The WGs ratify the actual scope when they activate.

## Launch sequence

Foundations workflow extensions lift on their own timeline, driven by composition demand from adopters and by WG capacity (Ali for physical-AI; operational management WG lead TBD). They do not gate clinical-research v1. The first composition to reach activation (likely smart-hospital, given the HCLS launch) creates the first concrete adopter pull for foundations.

Until foundations workflow extensions ship full v1, smart-X compositions cannot ship their full reference; they can ship stubs that the foundations v1 fills in (analogous to how clinical-research v1 ships with Pattern B stubs to clinical-care).

## What this strategy commits the foundations bucket to

- **Foundations is a domain bucket, not a class-level shared tier.** It holds workflow extensions; it has no namespace, no classes, no SHACL shapes of its own.
- **Two workflow extensions inside one bucket** as the strawman. Physical-AI and operational management. WG may restructure at activation.
- **Cross-industry reach is the defining property.** Every foundations workflow extension serves multiple buckets and is referenced by compositions.
- **Composition-friendly class design.** Foundations classes are operator-precise but not domain-specific; contextual specificity lives in compositions or as instance properties.
- **WG independence within shared bucket coordination.** Ali leads physical-AI; operational management WG lead TBD. Bucket-level coordination handles cross-extension RFC review.
- **Strategy ratifies as ADR-0023 (foundations bucket strategy)** when the first foundations WG activates. ADR number is a strawman pending activation order.

## What this strategy does NOT do

- It does not finalize the bucket name. "Foundations" is the strawman; WG ratifies or overrides at activation time.
- It does not commit to one bucket vs two. The one-bucket strawman gets revisited if stewardship cohorts diverge.
- It does not author any class catalog. Physical-AI and operational management each ship their own seeds when their WGs activate.
- It does not commit to specific standards alignment. The standards landscape (Haystack, BACS, FIWARE, RealEstateCore, HR-XML, ISO 9001, etc.) gets decided by the activating WG.
- It does not commit a ship date. Foundations workflow extensions lift on adopter demand + WG capacity.

## Open questions for working-group resolution

1. **Foundations bucket name.** Strawman: `foundations/`. Pairs cleanly with `compositions/`. WG ratifies or overrides.
2. **Bucket structure.** One bucket with two workflow extensions inside, vs two top-level buckets. WG decides at activation.
3. **Physical-AI standards alignment.** Haystack, ISO 16484 BACS, FIWARE Smart Buildings, RealEstateCore, or some combination. Ali's WG decides.
4. **Operational management standards alignment.** HR-XML, ISO 9001, industry-specific frameworks. WG decides at activation.
5. **Composition-friendly vs domain-specific class naming.** How generic is `Bed`? `Sensor`? `EmployeeRecord`? `Contract`? Strawman: most generic operator-recognizable; compositions add contextual specificity. WG sharpens at v1 authoring.
6. **Cross-bucket Pattern B from foundations.** When does a foundations workflow declare a cross-bucket `subClassOf` against an HCLS or manufacturing class? Strawman: not by default; foundations stays generic. WG decides if specific crosses justify exceptions.

## Pointers

- Strategy brief: `top-strategy-brief.md`
- Workflows strategy: `top-workflows-strategy.md`
- Compositions strategy: `top-compositions-strategy.md`
- HCLS bucket strategy: `top-hcls-strategy.md`
- TOP Core: `core/v1/`, `taxonomy/taxonomy.ttl`
- Working groups: `governance/working-groups.md`

---

*Foundations bucket strategy v1. The substance of this strategy becomes the basis for ADR-0023 (foundations bucket strategy) when the first foundations WG activates. ADR number is a strawman.*
