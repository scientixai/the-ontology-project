# Crosswalk & curation registry (v1, oncology Pre-competitive)

This file is the **human-readable index** of every crosswalk artefact in
`cr-domain/crosswalks/`. Machine-readable metadata lives in each `.ttl` file
under the `cx:Mapping` class.

---

## Registered crosswalks

| File | Target schema | Pairs | Status | Added |
|------|--------------|-------|--------|-------|
| `cr-to-cdisc.ttl` | CDISC CDASH / SDTM | 8 | validated | 2026-06-24 |
| `cr-to-fhir.ttl` | HL7 FHIR R4 | 7 | validated | 2026-07-01 |

---

## `cr-to-cdisc.ttl` — CDISC CDASH / SDTM crosswalk

**Source prefix:** `cr:` (`https://top.scientix.ai/cr/v1#`)  
**Target prefix:** `cdash:` / `sdtm:` (CDISC namespace)  
**Version:** CDASH 2.1 / SDTM IG 3.4  
**Mapping type:** `skos:closeMatch` (most), one `skos:exactMatch` (Observation)  
**Validation status:** validated  

### Entity-level pairs

| CR entity | CDISC target | Predicate | Confidence | Notes |
|-----------|-------------|-----------|------------|-------|
| `cr:Study` | `cdash:Study` | `closeMatch` | 0.90 | Protocol vs. CRF distinction |
| `cr:Arm` | `cdash:Arm` | `closeMatch` | 0.85 | — |
| `cr:Visit` | `cdash:Visit` | `closeMatch` | 0.80 | Schedule vs. event |
| `hcls:Observation` | `sdtm:Finding` | `exactMatch` | 0.92 | Best fit |
| `cr:AdverseEvent` | `cdash:AE` | `closeMatch` | 0.88 | Severity model differs |
| `cr:Enrollment` | `cdash:SubjectEnrollment` | `closeMatch` | 0.85 | — |
| `cr:EligibilityCriterion` | `cdash:InclusionExclusionCriteria` | `closeMatch` | 0.80 | — |
| `cr:InformedConsent` | `cdash:InformedConsent` | `closeMatch` | 0.87 | — |

---

## `cr-to-fhir.ttl` — HL7 FHIR R4 crosswalk (US-500-001)

**Source prefix:** `cr:` / `hcls:` (`https://top.scientix.ai/cr/v1#`, `https://top.scientix.ai/hcls/v1#`)  
**Target prefix:** `fhir:` (`http://hl7.org/fhir/`)  
**Version:** FHIR R4  
**Mapping type:** `skos:closeMatch` / `skos:exactMatch`  
**Validation status:** validated  

### Entity-level pairs

| CR entity | FHIR R4 resource | Predicate | Confidence | Notes |
|-----------|-----------------|-----------|------------|-------|
| `cr:Study` | `fhir:ResearchStudy` | `closeMatch` | 0.85 | Protocol vs. resource structure differs |
| `cr:Enrollment` | `fhir:ResearchSubject` | `closeMatch` | 0.90 | Close semantic fit |
| `cr:Visit` | `fhir:Encounter` | `closeMatch` | 0.80 | Schedule vs. clinical event |
| `hcls:Observation` | `fhir:Observation` | `exactMatch` | 0.90 | Direct equivalent |
| `cr:AdverseEvent` | `fhir:AdverseEvent` | `exactMatch` | 0.92 | Direct equivalent |
| `cr:InformedConsent` | `fhir:Consent` | `closeMatch` | 0.85 | Consent model differs |
| `hcls:Person` | `fhir:Patient` | `closeMatch` | 0.75 | Person vs. patient role |

### Property gaps

- `cr:Study` → `fhir:ResearchStudy`: missing `primaryPurposeType`, `phase` alignment
- `cr:Visit` → `fhir:Encounter`: scheduling model significantly different
- `hcls:Person` → `fhir:Patient`: `Person` is broader than clinical `Patient`
- `cr:Assessment` not yet mapped (needs `assessmentCode` property before
  `fhir:Procedure` mapping is viable beyond `broadMatch`)

---

## Curation notes

- All mappings authored by `ex:curator-wg` via manual curation (`semapv:ManualMappingCuration`).
- Confidence scores are on a 0–1 decimal scale; scores ≥ 0.85 are considered
  publication-ready.
- `cx:verificationStatus` values: `draft` | `validated` | `deprecated`.
- Property-level crosswalks are planned for a follow-on US.

---

## Provenance

| Field | Value |
|-------|-------|
| Registry version | 1.1 |
| Last updated | 2026-07-01 |
| Maintainer | CR ontology WG |
| Schema | `https://top.scientix.ai/crosswalk/v1#` |
