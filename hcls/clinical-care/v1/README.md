# TOP HCLS · Clinical-Care v1 (stubs)

This directory exists so clinical-research v1 can ship. It contains **only the
placeholder (stub) classes** that clinical-research crosses into via Pattern B —
`AdverseEvent`, `MedicationAdministration`, `Encounter`, `Procedure` — in
[`clinical-care-stubs.ttl`](clinical-care-stubs.ttl).

The stubs carry just enough structure for SHACL validation to pass. They are **not** a
clinical-care reference graph. Full clinical-care v1 lifts after clinical-research v1
ships, when the clinical-care Working Group forms; the stub URIs stay stable, so
clinical-research's Pattern-B `subClassOf` declarations keep resolving unchanged.

- **Prefix:** `topcd:` → `https://w3id.org/top/hcls/clinical-care/v1#`
- **Governance:** who reviews stub additions until the clinical-care WG activates is the
  seed's Open Question #4.
