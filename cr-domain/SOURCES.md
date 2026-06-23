# Operator-context sources

The reference tracks where its *operator semantics* come from, the same way it tracks its
*ontology* sources (OAE/OBI). Operator context is tacit practitioner knowledge that the public
ontologies lack (see registry: CTO is registry-metadata, BRIDG is frozen), so its provenance matters.

| Source | Contributes | Used in |
|---|---|---|
| **"Comprehensive Lifecycle Map of Clinical Research"** (Doc 1, JTBD analysis) | lifecycle stages, roles, artifacts, failure points, cost drivers | the operator model + constraints + ROI framing |
| **"Semantic Architecture for the Clinical Trial Lifecycle"** (Doc 2) | public-ontology landscape per lifecycle stage; agent JTBD | crosswalk targets + projection targets |
| **"Architectural Foundations of the Clinical Trial Site Operator Domain"** (site-schema synthesis) | CDISC ODM EAV capture model, LIMS specimen lifecycle, query/SDV/RBQM, data-mart ETL, PHI tagging — synthesized from OpenClinica, VOXCE, LabKey, SENAITE LIMS, ClinicEDC, CommCare | `cr-core-edc` (EAV capture, query/SDV/PHI); data-mart projection; corroborates the bitemporal + projections theses |
| **Dan Sfera ("The Clinical Trials Guru") / Coordinare** (`coordinare.co`) | site-level coordinator reality (start-up, reg binder/1572/DOA, source/SDV, screening, monitoring) | site-side validation SME; informs the site-operations slice |

> Operator context is *structured* into the model here; high-fidelity detail and validation
> require the practitioner sources directly (esp. site-side SME review).
