# NCIt anchor verification

The 339 NCI C-codes the USDM-OWL generator anchors (`skos:exactMatch` to `NCIT_*`) were verified against **NCI Thesaurus 26.05d** (verified 2026-06-23).

| check | result |
|---|---|
| codes resolve in NCIt 26.05d | 339 / 339 |
| CDISC preferred label is an NCIt synonym | 338 / 339 |
| concept tagged into the CDISC DDF terminology subset | 339 / 339 |

Reproduce: download the NCIt FLAT file from evs.nci.nih.gov/evs-download/thesaurus-downloads and run `python3 tools/usdm-rdf-gen/verify_ncit.py Thesaurus.txt`. The flat file is not vendored (size); `ncit-verification.json` is the durable record.

## Labels to review (resolved, but CDISC pref not an exact synonym)
- `C188825` attr:Endpoint.purpose: CDISC "Study Endpoint Purpose Description" vs NCIt "Study Endpoint Purpose"
