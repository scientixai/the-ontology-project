# NCIt anchor verification

The 483 NCI C-codes anchored by the USDM-OWL + CT generators (`skos:exactMatch` to `NCIT_*`) were verified against **NCI Thesaurus 26.05d** (verified 2026-06-23).

| check | result |
|---|---|
| codes resolve in NCIt 26.05d | 483 / 483 |
| CDISC preferred label is an NCIt synonym | 456 / 458 |
| tagged into the CDISC DDF terminology subset | 482 / 483 |

(Codelist codes carry no CDISC preferred label; permissible-value codes are general NCIt concepts, so not all are DDF-tagged. The binding check is **resolution**.)

Reproduce: download the NCIt FLAT file from evs.nci.nih.gov/evs-download/thesaurus-downloads and run `python3 tools/usdm-rdf-gen/verify_ncit.py Thesaurus.txt`. The flat file is not vendored (size); `ncit-verification.json` is the durable record.

## Labels to review (resolved, but CDISC pref not an exact synonym)
- `C188825` attr:Endpoint.purpose: CDISC "Study Endpoint Purpose Description" vs NCIt "Study Endpoint Purpose"
- `C94108` value:StudyTitle.type: CDISC "Study Acronym" vs NCIt "Study Protocol Version Acronym"
