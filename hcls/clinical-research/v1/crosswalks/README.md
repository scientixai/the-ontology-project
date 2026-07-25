# Crosswalks — clinical-research v1

External-vocabulary mappings, one [SSSOM](https://mapping-commons.github.io/sssom/) TSV
per target vocabulary. SSSOM keeps every mapping auditable: a metadata block (curie map,
license, source, version, date) then a body of typed mappings.

Discipline (per the seed, §"SSSOM mapping file structure" and `top-hcls-strategy.md`
Tier 3):

- **Pin every mapset.** `mapping_set_version` and `mapping_set_source` are required so a
  mapping can always be traced to the exact upstream release it came from.
- **Import, don't invent.** Tier-3 mapsets come from NCI EVS REST at pinned versions, not
  hand-authored.
- **License honestly.** MedDRA requires a license; the block says so. RxNorm/LOINC are
  deferred (UMLS dependency) — do not add them here until that RFC lands.

Files:

- `ncit-to-meddra.sssom.tsv` — template + example rows (preferred terms elided pending
  a licensed MedDRA pull).
- `ncit-to-icd10cm.sssom.tsv` — TODO (referenced by `topcr:AdverseEvent`).
- Further EVS mapsets (8 total named in `top-hcls-strategy.md` Tier 3) — TODO.
