> Operator-facing object catalog (v0.2). Imported per RFC 0001 (governance/rfcs/proposed/0001-ooux-catalog-and-entity-view-schema.md) as the Docs-as-Code source the entity-view reconciliation is measured against.

# **Section 1\. Introduction**

This is an Object-Oriented UX (OOUX) map of clinical research. The point of the exercise is to give clinical research a shared vocabulary of entities, their data shapes, and the actions that act on them, independent of any one product.

# **Section 2\. Reading guide**

Each object in Section 3 follows the four OOUX columns: Attributes, Metadata, Relationships, and Calls to Action. This section explains what belongs in each column so that the catalog can be parsed consistently by readers, by the NGSI-LD translator, and by the developer.  
Attributes describe the intrinsic properties of the object, the data that belongs to it and travels with it. In NGSI-LD terms, these correspond to Properties, whose values are literals, controlled vocabularies, enumerations, or structured records. Attribute lines are written "name (type): description". Enumerations list the allowed values. Where a value is geographic, it is typed GeoProperty. Where a value references another entity, it is surfaced under Relationships rather than Attributes, even if it is stored on the entity as an identifier.  
Metadata describes facts about the record rather than the thing the record represents: creation and modification timestamps, the person or system that created or modified the record, approval history, effective dates, version, provenance, confidentiality level. In NGSI-LD terms, these are Property metadata or Relationship metadata (createdAt, modifiedAt, observedAt, reliability, providedBy). When a block lists only a couple of metadata lines, the entity still inherits the standard NGSI-LD metadata applicable to all Properties and Relationships.  
Relationships describe the links between this object and other objects in the map. Each relationship line names the verb, the target object, the cardinality, and an optional note. Relationships are directional and named from the perspective of the object that owns the block. Cardinalities allow the translator to derive minCardinality and maxCardinality on the NGSI-LD Relationship.  
Calls to Action describe the things actors can do with an instance of the object, by persona. CTAs are written "action (persona): note". Personas are organisational roles (Sponsor Operations, Site Coordinator, Investigator, Data Manager, Quality, Regulatory Affairs, Finance, Pharmacovigilance, and so on). CTAs are not exhaustive; they are representative of the work that the object exists to enable.

# **Section 3\. Object catalog**

The object catalog is the canonical v0.2 specification. Objects 1 through 55 correspond to the objects enumerated in v0, re-numbered so that Site sits at position 1 as the entry point for the map. Objects 56 through 78 are flagged missing objects: entities that v0 either listed as yellow gaps or implied by its relationship graph without specifying. Their editor notes describe their intended treatment.

## **1\. Site**

A Site is a single physical or virtual location of clinical research conduct: a hospital, clinic, satellite office, decentralized hub, or virtual unit operating under one regulatory and operational identity. Site is the primary anchor for participant enrollment, on-the-ground protocol execution, source documentation, and local regulatory accountability. The attributes below are organised by nine attribute categories (core identity; location and jurisdiction; facility and capability; operational posture; quality and compliance; staffing; contracting and finance; technology and integrations; patient access).  
***Editor note.** v0.2: Site was a TODO in v0; this entry is new. Attributes are grouped by the nine categories. Relationships now include Investigator, Therapeutic Area, IRB/EC, Master Service Agreement, and parent Network/Region.*

### **Attributes**

* **siteId** (string, unique, NGSI-LD URI): Globally unique identifier (urn:ngsi-ld:Site:...).  
* **siteNumber** (string, unique-within-study): Sponsor-issued numeric or alphanumeric site identifier scoped to a Study.  
* **siteName** (string): Display name of the site.  
* **legalName** (string): Legal name of the institution operating the site.  
* **ctgovFacilityId** (string, optional): ClinicalTrials dot gov facility identifier where applicable.  
* **fhirOrganizationId** (string, optional): FHIR Organization.id reference for downstream FHIR projection.  
* **siteType** (enum): HOSPITAL, CLINIC, ACADEMIC\_MEDICAL\_CENTER, RESEARCH\_CENTER, COMMUNITY\_PRACTICE, DECENTRALIZED\_HUB, VIRTUAL.  
* **parentNetworkId** (string, optional): Reference to a parent Network or System (for site networks and SMOs).  
* **siteStatus** (enum): PLANNED, FEASIBILITY, SELECTED, IN\_STARTUP, READY\_TO\_INITIATE, ACTIVE, ON\_HOLD, CLOSED\_TO\_ENROLLMENT, CLOSED.  
* **address** (object {line1, line2, city, region, postalCode}): Postal address.  
* **country** (enum, ISO 3166-1 alpha-3): Country code (used for regulatory and reporting jurisdiction).  
* **region** (enum): Sponsor-defined region grouping (e.g., NORAM, EMEA, APAC, LATAM).  
* **timezone** (IANA timezone string): Local timezone (e.g., America/Chicago).  
* **geo** (GeoProperty (Point)): Latitude and longitude (NGSI-LD GeoProperty).  
* **regulatoryAuthority** (enum, ISO-coded): Primary regulatory authority for the site (FDA, EMA, MHRA, PMDA, NMPA, ANVISA, others).  
* **languagesSupported** (array of BCP-47 codes): Languages the site can support for consent and conduct.  
* **facilityCapabilities** (array\<enum\>): INPATIENT, OUTPATIENT, ICU, ED, INFUSION, IMAGING\_MRI, IMAGING\_CT, IMAGING\_PET, RADIOPHARMACY, NUCLEAR\_MEDICINE, SURGERY, ENDOSCOPY, GENOMICS\_LAB, BIOSPECIMEN\_PROCESSING.  
* **therapeuticExperience** (array\<enum\>): Therapeutic areas with prior trial experience (ONCOLOGY, CARDIOLOGY, NEUROLOGY, IMMUNOLOGY, RARE\_DISEASE, etc.).  
* **investigationalProductHandling** (array\<enum\>): IP modalities the site can handle: SMALL\_MOLECULE, BIOLOGIC, CELL\_THERAPY, GENE\_THERAPY, RADIOLIGAND, DEVICE.  
* **storageCapability** (object): Pharmacy and biospecimen storage profile: ambient, 2 to 8 C, minus 20 C, minus 80 C, liquid nitrogen; controlled substance vault; backup power.  
* **onSiteLab** (enum): NONE, BASIC, FULL\_CLIA, FULL\_CAP.  
* **imagingDevices** (array\<object\>): List of relevant imaging assets and their certifications.  
* **bedCount** (integer, optional): Inpatient bed count where relevant.  
* **operatingHours** (object): Standard operating hours by day of week.  
* **afterHoursContact** (string, encrypted reference): Reference to encrypted after-hours contact record.  
* **decentralizedTrialReadiness** (enum): NONE, PARTIAL, FULL (supports remote consent, home health, televisits, direct-to-patient IP shipping).  
* **homeHealthVendor** (array\<string\>): Home health vendors the site has agreements with.  
* **recruitmentChannels** (array\<enum\>): EHR\_QUERY, REGISTRY, REFERRAL\_NETWORK, SOCIAL, PATIENT\_ADVOCACY, COMMUNITY\_OUTREACH.  
* **backupSiteId** (string, optional): Designated backup site for participant continuity.  
* **gcpCompliance** (enum): COMPLIANT, NONCOMPLIANT, UNDER\_REVIEW.  
* **lastFdaInspectionDate** (date, optional): Most recent FDA bioresearch monitoring inspection.  
* **lastFdaInspectionOutcome** (enum, optional): NAI, VAI, OAI (no action indicated, voluntary action indicated, official action indicated).  
* **lastSponsorAuditDate** (date, optional): Most recent sponsor audit date.  
* **openCAPACount** (integer): Number of open CAPAs at the site (denormalised for dashboards).  
* **gdprApplicability** (boolean): Whether GDPR governs personal data at the site.  
* **hipaaApplicability** (boolean): Whether HIPAA governs PHI at the site.  
* **part11Compliant** (boolean): 21 CFR Part 11 compliance posture for site-managed systems.  
* **principalInvestigatorId** (string, NGSI-LD relationship target): PI of record at this site for this study; modelled as a Relationship to Investigator.  
* **subInvestigatorIds** (array\<string\>): Sub-investigators delegated by the PI; relationship targets.  
* **studyCoordinatorIds** (array\<string\>): Coordinator personnel; relationship targets.  
* **pharmacistIds** (array\<string\>): Investigational pharmacist personnel.  
* **regulatoryContactId** (string): Site regulatory contact.  
* **staffHeadcount** (integer): Total clinical research staff at the site.  
* **staffTrainingCompletionRate** (percentage): Percent of required trainings completed.  
* **masterServiceAgreementId** (string, optional): Site-sponsor MSA reference.  
* **clinicalTrialAgreementId** (string): Per-study CTA reference.  
* **budgetId** (string): Per-study site budget.  
* **paymentTermsDays** (integer): Net payment terms (e.g., 30, 45, 60).  
* **paymentCurrency** (enum, ISO 4217): Currency for site payments.  
* **indirectCostRate** (percentage): Indirect cost or institutional overhead rate.  
* **coverageAnalysisStatus** (enum): NOT\_STARTED, IN\_PROGRESS, COMPLETE; required for US sites with billable items.  
* **ehrSystem** (string): Primary EHR (e.g., Epic, Cerner, Meditech).  
* **ehrIntegrationStatus** (enum): NONE, READ\_ONLY, BIDIRECTIONAL, FHIR\_API.  
* **edcSystemIds** (array\<string\>): EDC systems used at the site for sponsor studies.  
* **ctmsId** (string, optional): CTMS identifier where the site is recorded.  
* **eRegSystem** (string, optional): eRegulatory binder system (e.g., Florence, Veeva SiteVault).  
* **esourceCapability** (boolean): Whether site supports eSource data capture.  
* **integrationProfiles** (array\<object\>): Active integration profiles (HL7, FHIR R4/R5, NGSI-LD subscriptions).  
* **catchmentPopulationSize** (integer, optional): Estimated catchment population for screening.  
* **payerMix** (object): Insurance payer mix percentages.  
* **patientDemographicProfile** (object): Aggregate demographic distribution served by the site.  
* **historicalEnrollmentRate** (number): Average participants enrolled per month per study at this site.  
* **historicalScreenFailRate** (percentage): Average screen fail rate.  
* **languageAccessSupport** (array\<string\>): On-site interpreters and translation services available.  
* **accessibilityProfile** (object): ADA and equivalent accessibility features.

### **Metadata**

* **createdAt** (datetime): NGSI-LD entity creation timestamp.  
* **modifiedAt** (datetime): Last modification timestamp.  
* **createdBy** (string): Person identifier of creator.  
* **modifiedBy** (string): Person identifier of last modifier.  
* **source** (enum): MANUAL, FEASIBILITY\_IMPORT, CTMS\_SYNC, EHR\_SYNC.  
* **dataQualityFlags** (array\<enum\>): Quality issues observed (MISSING\_PI, EXPIRED\_CTA, OVERDUE\_TRAINING, etc.).  
* **ngsi-ld@context** (URI): JSON-LD context describing site vocabulary.

### **Relationships**

* **hasPrincipalInvestigator**: Investigator (1); Per study; PI is now a first-class relationship target rather than a typed Person.  
* **hasSubInvestigators**: Investigator (0..N); Delegated sub-investigators.  
* **hasStaff**: Person (0..N); All site-affiliated personnel (coordinators, pharmacists, regulatory).  
* **participatesIn**: Study (0..N); A site can participate in multiple studies for multiple sponsors.  
* **conductedBy**: Sponsor (0..N); Sponsors with active engagements at the site.  
* **operatedBy**: Organization (1); The legal institution operating the site.  
* **memberOf**: Network (0..1); Site network or SMO membership; flagged as a missing object below.  
* **locatedIn**: Country (1); Country of location; flagged as missing object below.  
* **locatedIn**: Region (1); Sponsor-defined region grouping; flagged as missing object below.  
* **enrolls**: Participant (0..N); Participants screened or enrolled at the site.  
* **hosts**: Visit (0..N); Visits conducted at the site (in-person or hybrid).  
* **holdsAgreement**: Contract (0..N); CTA, MSA, confidentiality and material transfer agreements scoped to the site.  
* **operatesUnderBudget**: Budget (0..N); Site-specific budgets (one per study typically).  
* **receivesPayment**: Payment (0..N); Payments received by the site.  
* **overseenBy**: Oversight Body (0..N); IRB or EC of record for the site.  
* **hasTherapeuticExperience**: Therapeutic Area (0..N); Areas in which the site has prior experience; flagged as a missing object below.  
* **holdsCredentials**: Credential (0..N); Site-level credentials (e.g., CAP, CLIA, GCP organisational training).  
* **operatesEquipment**: Equipment (0..N); Equipment registered to the site.  
* **usesSystem**: System (0..N); Systems the site uses or integrates with (EHR, EDC, CTMS, eReg).  
* **receivesShipment**: Shipment (0..N); Inbound shipments of IP, kits, devices.  
* **raises**: Discrepancy (Query) (0..N); Queries originating from or about site data.  
* **reports**: Deviation (0..N); Deviations occurring at the site.  
* **reports**: Adverse Event (0..N); Adverse events recorded at the site.  
* **reports**: Serious Adverse Event (0..N); SAEs recorded at the site.  
* **receives**: Monitoring Visit (0..N); Monitoring visits hosted by the site.  
* **undergoes**: Audit (0..N); Audits performed at the site.  
* **executes**: CAPA (0..N); CAPAs the site is responsible for.  
* **supplies**: Sample (0..N); Samples collected at the site.  
* **holds**: Investigational Product (0..N); IP allocated to the site (drug, biologic, device).  
* **hostsTrainings**: Training Record (0..N); Trainings completed by site staff.  
* **hasConfiguration**: System Configuration (0..N); Site-scoped configurations of sponsor systems.  
* **hasConfiguration**: Service Configuration (0..N); Site-scoped service configurations.  
* **hasStartupPackage**: Study Startup Package (0..N); Site-specific startup packages.  
* **hasUserRoles**: User Role (0..N); Role assignments scoped to the site.  
* **producesMetrics**: Site Performance Metric (0..N); Aggregated site KPIs (enrollment rate, query age, deviation rate); flagged as a missing object.

### **Calls to Action**

* **Create Site** (Sponsor Ops): Register a new site entity.  
* **Conduct Feasibility** (Site Selection Lead): Capture feasibility responses and rank candidate sites.  
* **Select Site for Study** (Sponsor PM): Promote a site from feasibility to selected.  
* **Initiate Site (SIV)** (CRA): Run the site initiation visit, mark site activated.  
* **Activate Site** (Sponsor Ops): Open enrollment at the site.  
* **Update Site Details** (Site Coordinator): Edit attributes within delegated scope.  
* **Place Site On Hold** (Sponsor Ops): Suspend new enrollment pending issue resolution.  
* **Resume Site** (Sponsor Ops): Lift a hold.  
* **Close Site to Enrollment** (Sponsor PM): Stop new enrollment; allow existing participants to continue.  
* **Close Site** (Sponsor PM): Complete close-out and archive.  
* **Schedule Monitoring Visit** (CRA): Plan the next monitoring visit.  
* **Run Coverage Analysis** (Regulatory / Compliance): Required for US billable items.  
* **Negotiate CTA** (Contracts): Drive CTA execution.  
* **Renew Master Service Agreement** (Contracts): Renew or amend the sponsor-site MSA.  
* **Issue Site Payment** (Finance): Trigger a payment per the budget and payment schedule.  
* **Submit IRB Documents** (Regulatory): Push amendments and consents to local IRB or EC.  
* **Add Investigator Delegation** (PI): Update delegation of authority.  
* **Sync from EHR** (Data Engineering): Pull demographics or labs via FHIR.  
* **Open CAPA** (Quality): Open a corrective action.  
* **Generate Site Performance Report** (Sponsor Analytics): Produce site KPI snapshot for portfolio review.  
* **Project to FHIR Organization** (Visual Explorer): Render the site as an FHIR Organization resource.  
* **Project to USDM StudySite** (Visual Explorer): Render the site as a USDM StudySite element.

## **2\. Sponsor**

A Sponsor is the legal organization responsible for initiating, managing, and financing one or more clinical trials. Sponsors hold regulatory accountability for their studies and own the master data that anchors most other entities.  
***Editor note.** v0.2: type vocabulary expanded to include CRO\_AS\_SPONSOR; added duns and orcid identifiers; added regulatory and finance contact relationships rather than embedded fields. Investigator-Sponsor (academic single-PI sponsor) is supported via sponsorType.*

### **Attributes**

* **sponsorId** (string, unique, NGSI-LD URI): Globally unique identifier.  
* **sponsorName** (string): Display name.  
* **legalName** (string): Registered legal name.  
* **sponsorType** (enum): PHARMACEUTICAL, BIOTECH, ACADEMIC, GOVERNMENT, INVESTIGATOR\_SPONSOR, CRO\_AS\_SPONSOR, OTHER.  
* **duns** (string, optional): DUNS number.  
* **orcid** (string, optional): ORCID identifier when sponsor is an individual investigator-sponsor.  
* **address** (object): Headquarters address.  
* **country** (enum, ISO 3166-1 alpha-3): Country of registration.  
* **phone** (string): Primary phone.  
* **email** (string): Primary email.  
* **website** (URI): Sponsor website.  
* **status** (enum): ACTIVE, INACTIVE, MERGED, ACQUIRED.

### **Metadata**

* **createdAt** (datetime): Entity creation timestamp.  
* **modifiedAt** (datetime): Last modification.  
* **source** (enum): MANUAL, IMPORT.

### **Relationships**

* **runs**: Study (1..N); Studies sponsored by this organization.  
* **employs**: Person (1..N); Employees and contractors.  
* **engages**: Site (1..N); Sites the sponsor has contracted.  
* **contractsWith**: CRO (0..N); Contracted CROs (CRO is flagged as a missing object).  
* **holds**: Contract (1..N); All sponsor-side contracts.  
* **authors**: Budget (1..N); Budgets the sponsor maintains.  
* **publishes**: Document (1..N); Sponsor-controlled documents.  
* **files**: Regulatory Submission (1..N); Submissions filed by the sponsor.  
* **commissions**: Audit (1..N); Sponsor-commissioned audits.  
* **operates**: Training Program (1..N); Sponsor training programs.  
* **maintains**: SOP (1..N); Standard operating procedures.  
* **operates**: System (1..N); Sponsor-owned systems.  
* **produces**: Report (1..N); Reports authored by the sponsor.  
* **plans**: Milestone (1..N); Program-level milestones.  
* **conducts**: Risk Assessment (1..N); Risk assessments owned by the sponsor.  
* **executes**: CAPA (1..N); Sponsor-driven CAPAs.  
* **interfacesWith**: Oversight Body (1..N); IRB, EC, DSMB, IDMC engagement.  
* **publishes**: Publication (1..N); Resulting publications.  
* **signs**: Data Transfer Agreement (1..N); Data transfer agreements.  
* **supplies**: Investigational Product (1..N); IP the sponsor supplies.  
* **organizes**: Tag (0..N); User-defined organizational tags.

### **Calls to Action**

* **Create Sponsor** (Platform Admin): Register a new sponsor.  
* **Update Sponsor Details** (Sponsor Admin): Maintain sponsor profile.  
* **Activate or Deactivate Sponsor** (Platform Admin): Toggle status.  
* **Associate or Remove Study** (Sponsor PM): Link studies to the sponsor.  
* **Manage Sponsor Contacts** (Sponsor Admin): Add or update key contacts.  
* **Review Sponsor Performance** (Sponsor Exec): Run portfolio dashboards.  
* **Generate Sponsor Report** (Sponsor Analytics): Produce sponsor-level performance report.  
* **Audit Sponsor** (Quality): Trigger a sponsor-level audit.

## **3\. Tag**

A Tag is a flexible, user-defined label applied to studies and other objects to enable grouping, filtering, and navigation. Tags can encode therapeutic area, region, phase, custom programs, or any cross-cut the sponsor needs.  
***Editor note.** v0.2: introduced tagScope (which object types the tag may be applied to) and ownerSponsorId. NGSI-LD treats tags as a Property of type array; for explorer use we additionally model Tag as its own entity for filtering UIs.*

### **Attributes**

* **tagId** (string, unique): Unique identifier.  
* **tagLabel** (string): Display label.  
* **tagDescription** (string): Free-text description.  
* **tagPrompt** (string): Helper prompt shown when applying the tag.  
* **tagColor** (string, hex): Color for UI badges.  
* **tagScope** (array\<enum\>): Object types this tag may decorate (STUDY, PARTICIPANT, SITE, etc.).  
* **ownerSponsorId** (string): Sponsor that owns and curates the tag vocabulary.

### **Metadata**

* **createdAt** (datetime): Tag creation.  
* **createdBy** (string): Creator person id.

### **Relationships**

* **decorates**: Study (0..N); Studies the tag is applied to.  
* **ownedBy**: Sponsor (1); Owning sponsor.  
* **managedBy**: Person (0..N); Users authorised to apply or curate.  
* **references**: Document (0..N); Documents categorised by the tag.  
* **reportedIn**: Report (0..N); Reports filtered by tag.  
* **governs**: User Role (0..N); Tag-scoped permissions.  
* **audits**: Audit Trail Entry (1..N); Trail of tag application changes.

### **Calls to Action**

* **Create Tag** (Sponsor Admin): Define a new tag.  
* **Update Tag** (Sponsor Admin): Edit the label, color, or scope.  
* **Delete Tag** (Sponsor Admin): Soft-delete and reassign references.  
* **Assign Tag to Object** (Any User): Apply a tag.  
* **Remove Tag from Object** (Any User): Remove the tag application.

## **4\. Study**

A Study is a single clinical investigation with its own protocol, sponsor, identifier set, and lifecycle. It is the primary container for sites, participants, visits, data, and operational artefacts. Many child objects are surfaced at the study level for monitoring even when their primary owner is a more granular object.  
***Editor note.** v0.2: added masterProtocolId for platform/master/umbrella studies; added regulatoryIdentifiers (IND, EUDRACT, JapicCTI, etc.) as a structured array; clarified that some relationships are denormalised projections of child objects.*

### **Attributes**

* **studyId** (string, unique): Unique identifier.  
* **studyTitle** (string): Official title.  
* **studyDescription** (string): Brief description.  
* **acronym** (string): Short name.  
* **nctId** (string, optional): ClinicalTrials dot gov identifier.  
* **regulatoryIdentifiers** (array\<object\>): INDs, IDEs, EUDRACT, JapicCTI, ChiCTR, others.  
* **masterProtocolId** (string, optional): Reference to a parent master / umbrella / platform protocol.  
* **studyType** (enum): INTERVENTIONAL, OBSERVATIONAL, EXPANDED\_ACCESS.  
* **studyPhase** (enum): PHASE0, PHASE1, PHASE2, PHASE3, PHASE4, NA.  
* **studyStatus** (enum): PLANNED, IN\_STARTUP, ACTIVE, ENROLLING, ENROLLMENT\_COMPLETE, FOLLOW\_UP, COMPLETED, TERMINATED, WITHDRAWN.  
* **startDate** (date): Study start.  
* **endDate** (date): Planned or actual end.  
* **primaryCompletionDate** (date): Primary outcome measure completion.  
* **conditionStudied** (array\<string\>): Primary condition or disease.  
* **interventionModel** (enum): SINGLE\_GROUP, PARALLEL, CROSSOVER, FACTORIAL, SEQUENTIAL.  
* **numberOfArms** (integer): Number of study arms.  
* **enrollmentType** (enum): ACTUAL, ANTICIPATED, TARGET.  
* **enrollmentCount** (integer): Participants enrolled.  
* **responsibleParty** (string): Name of responsible party.  
* **tags** (array\<tagId\>): Applied tags.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Last modification.  
* **studyFirstSubmitDate** (date): First regulatory submission.  
* **lastUpdateSubmitDate** (date): Most recent update submission.

### **Relationships**

* **sponsoredBy**: Sponsor (1); The sponsoring organization.  
* **governedBy**: Protocol (1); The current effective protocol version.  
* **hasArms**: Arm (1..N); Study arms.  
* **conductedAt**: Site (1..N); Sites conducting the study.  
* **enrols**: Participant (0..N); Participants enrolled across all sites.  
* **schedules**: Visit (0..N); Scheduled and completed visits.  
* **captures**: CRF (0..N); CRFs collected.  
* **contains**: Document (0..N); Study documents.  
* **tracks**: Milestone (0..N); Study milestones.  
* **supplies**: Investigational Product (0..N); IP used in the study.  
* **executes**: Plan (0..N); Plans (monitoring, data management, statistical analysis).  
* **overseenBy**: Oversight Body (0..N); IRB/EC, DSMB, IDMC.  
* **records**: Deviation (0..N); Protocol deviations.  
* **records**: Screen Fail (0..N); Screen fails.  
* **employs**: Person (1..N); Investigators, coordinators, monitors.  
* **records**: Adverse Event (0..N); AEs.  
* **captures**: Informed Consent (1..N); Consent records.  
* **hasActionItems**: Action Item (0..N); Action items.  
* **records**: Enrollment (0..N); Enrollment events.  
* **authorizes**: Payment (0..N); Payments.  
* **uses**: System (1..N); EDC, CTMS, eTMF, IRT, others.  
* **consumes**: Service (1..N); Central lab, imaging, biostat services.  
* **hasStartupPackage**: Study Startup Package (1); Study-level startup package.  
* **budgetedBy**: Budget (1); Study budget.  
* **governedByContracts**: Contract (0..N); Study-related contracts.  
* **organizedBy**: Schedule of Assessments (1..N); SOAs (one per arm or unified).  
* **measuredBy**: Endpoint (1..N); Endpoints.  
* **records**: Lab Results (0..N); Lab results.  
* **files**: Regulatory Submission (0..N); Submissions.  
* **undergoes**: Audit (0..N); Audits.  
* **produces**: Report (0..N); Reports.  
* **administers**: Questionnaire (0..N); COA / PRO instruments.  
* **records**: Other Clinical Event (0..N); Other clinical events.  
* **executes**: CAPA (0..N); CAPAs.  
* **marksTime**: Date (0..N); Key dates.  
* **exchanges**: Data Transfer (0..N); Data transfers.  
* **hasUserRoles**: User Role (1..N); Study-scoped role assignments.  
* **records**: Serious Adverse Event (0..N); SAEs.  
* **governedBy**: Statistical Analysis Plan (1); SAP.  
* **hasAmendments**: Amendment (1..N); Protocol amendments.  
* **hasRandomizationLists**: Randomization List (1..N); Randomization lists.  
* **hasQueries**: Discrepancy (Query) (0..N); All queries.  
* **records**: Training Record (1..N); Training records of personnel.  
* **receives**: Monitoring Visit (0..N); Monitoring visits.  
* **assessedBy**: Risk Assessment (1..N); Risk assessments; flagged as missing object below.  
* **producesMetrics**: Study Performance Metric (0..N); Study KPIs; flagged as missing object below.

### **Calls to Action**

* **Create Study** (Sponsor PM): Initialise a new study.  
* **Update Study Details** (Sponsor PM): Edit core attributes.  
* **Submit for Approval** (Regulatory): Submit for governance approval.  
* **Approve or Reject Study** (Sponsor Exec): Sign off internally.  
* **Activate Study** (Sponsor PM): Move to ACTIVE.  
* **Put Study on Hold** (Sponsor Ops): Pause activity.  
* **Close Study** (Sponsor PM): Close out and lock.  
* **Archive Study** (Sponsor PM): Move to long-term archive.  
* **Project to USDM Study** (Visual Explorer): Render as USDM Study element.  
* **Project to FHIR ResearchStudy** (Visual Explorer): Render as FHIR ResearchStudy.

## **5\. Arm**

An Arm is a treatment group within a study, differentiated by intervention, dose, schedule, or comparator. Arms organise participants, visits, IP, and arm-specific eligibility.  
***Editor note.** v0.2: added armCohortType (sequential dose escalation, parallel, expansion cohort) to support oncology and adaptive designs; armId and stratumId disambiguated.*

### **Attributes**

* **armId** (string, unique): Unique arm identifier.  
* **armName** (string): Display name.  
* **armDescription** (string): Description of the intervention assigned.  
* **armType** (enum): EXPERIMENTAL, ACTIVE\_COMPARATOR, PLACEBO\_COMPARATOR, NO\_INTERVENTION, SHAM\_COMPARATOR.  
* **armCohortType** (enum): PARALLEL, DOSE\_ESCALATION, EXPANSION, BACKFILL, BASKET\_SUB\_ARM.  
* **intendedSampleSize** (integer): Target enrollment for the arm.  
* **stratumId** (string, optional): Stratum identifier when stratified.

### **Metadata**

* **createdAt** (datetime): Creation.

### **Relationships**

* **partOf**: Study (1); Parent study.  
* **hasSchedule**: Schedule of Assessments (0..1); Arm-specific SOA when applicable.  
* **hasVisits**: Visit (1..N); Visits scheduled for this arm.  
* **administers**: Investigational Product (0..1); IP assigned to the arm.  
* **enrolls**: Participant (1..N); Participants in this arm.  
* **restrictedBy**: Inclusion Criteria (0..N); Arm-specific inclusion criteria.  
* **restrictedBy**: Exclusion Criteria (0..N); Arm-specific exclusion criteria.  
* **runs**: Procedure (0..N); Procedures specific to the arm.  
* **captures**: CRF (0..N); Arm-specific CRFs.  
* **contains**: Document (0..N); Arm documents.  
* **employs**: Person (0..N); Staff specifically assigned.  
* **tracks**: Milestone (0..N); Arm milestones.  
* **hasTasks**: Task (0..N); Arm tasks.  
* **audits**: Audit Trail Entry (1..N); Audit trail.

### **Calls to Action**

* **Create Arm** (Sponsor PM): Add an arm to a study.  
* **Update Arm Details** (Sponsor PM): Edit attributes.  
* **Assign Participants to Arm** (IRT / Coordinator): Allocate via randomisation or assignment.  
* **Close Arm** (Sponsor PM): Stop new allocations.

## **6\. Visit**

A Visit is a single planned or unplanned encounter where protocol activities are performed for a participant. Visits can be in-clinic, remote, hybrid, or home-health, and they anchor procedures, CRFs, sample collection, and IP dispensation.  
***Editor note.** v0.2: added visitModality (IN\_CLINIC, TELEVISIT, HOME\_HEALTH, HYBRID); visitWindow now structured (start, end, anchor).*

### **Attributes**

* **visitId** (string, unique): Identifier.  
* **visitNumber** (integer): Visit ordinal in the SOA.  
* **visitName** (string): Display name.  
* **visitType** (enum): SCREENING, BASELINE, TREATMENT, FOLLOW\_UP, EARLY\_TERMINATION, UNSCHEDULED.  
* **visitModality** (enum): IN\_CLINIC, TELEVISIT, HOME\_HEALTH, HYBRID.  
* **scheduledDate** (datetime): Planned datetime.  
* **actualDate** (datetime): Actual datetime.  
* **windowStart** (date): Visit window start.  
* **windowEnd** (date): Visit window end.  
* **windowAnchor** (enum): BASELINE, PRIOR\_VISIT, FIXED\_DATE.  
* **visitStatus** (enum): SCHEDULED, IN\_PROGRESS, COMPLETED, MISSED, CANCELED.  
* **visitDuration** (duration): Planned duration.  
* **visitLocation** (string): Physical or virtual location.  
* **windowComplianceStatus** (enum): IN\_WINDOW, OUT\_OF\_WINDOW.  
* **visitCost** (money): Cost for budget accrual.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Last modification.  
* **performedBy** (string): Person who performed the visit.  
* **reviewedBy** (string): Reviewer.  
* **dataEntryDate** (datetime): Date data was entered.  
* **dataEntryBy** (string): Data entry person.

### **Relationships**

* **partOf**: Study (1); Parent study.  
* **hostedAt**: Site (1); Hosting site.  
* **for**: Participant (1); Subject of the visit.  
* **follows**: Schedule of Assessments (1); SOA item.  
* **captures**: CRF (0..N); CRFs at the visit.  
* **runs**: Procedure (0..N); Procedures performed.  
* **collects**: Sample (0..N); Samples collected.  
* **records**: Vital Sign Measurement (0..N); Vitals captured.  
* **dispenses**: Investigational Product (0..N); IP dispensations.  
* **receivesReturn**: Investigational Product (0..N); IP returns.  
* **records**: Adverse Event (0..N); AEs noted at the visit.  
* **records**: Serious Adverse Event (0..N); SAEs noted.  
* **records**: Deviation (0..N); Deviations identified.  
* **records**: Concomitant Medication (0..N); Conmed updates.  
* **administers**: Questionnaire (0..N); COA / PRO administrations.  
* **runs**: Imaging Procedure (0..N); Imaging performed.  
* **orders**: Lab Test (0..N); Lab tests ordered.  
* **runs**: Physical Examination (0..N); Physical exams.  
* **raises**: Discrepancy (Query) (0..N); Queries.  
* **contains**: Document (0..N); Source documents.  
* **contains**: Clinician Assessment (1); Clinician assessment record.  
* **captures**: Endpoint Data Collection (0..N); Endpoint data captured at visit.  
* **records**: Drug Accountability Check (0..N); Accountability events.  
* **updatesEligibility**: Inclusion Criteria (0..N); Eligibility re-checks.  
* **collects**: Wearable Device Data (0..N); Wearable data captured.  
* **runs**: Pharmacokinetic Sample Collection (0..N); PK samples.  
* **runs**: Unscheduled Procedure (0..N); Unplanned procedures.  
* **updates**: Informed Consent (0..1); Re-consent if required.

### **Calls to Action**

* **Schedule Visit** (Coordinator): Plan a visit per SOA.  
* **Reschedule Visit** (Coordinator): Move within or outside window.  
* **Start Visit** (Coordinator): Mark visit in progress.  
* **Complete Visit** (Coordinator): Close the visit.  
* **Cancel Visit** (Coordinator): Cancel with reason.  
* **Project to FHIR Encounter** (Visual Explorer): Render as FHIR Encounter.  
* **Project to USDM ScheduledActivity** (Visual Explorer): Render as USDM ScheduledActivity element.

## **7\. Task**

A Task is a discrete operational unit of work that needs to be done by a person or system, scoped to a study and optionally to a site, visit, or participant.  
***Editor note.** v0.2: added taskOrigin (system-generated vs. user-created) and slaMinutes for service-level tracking.*

### **Attributes**

* **taskId** (string, unique): Identifier.  
* **taskType** (enum): CRF\_REVIEW, QUERY\_RESPONSE, IP\_RECONCILIATION, SHIPMENT\_RECEIPT, MONITORING\_PREP, REGULATORY\_SUBMISSION, GENERIC.  
* **taskCategory** (string): Free-form category.  
* **taskDescription** (string): Description.  
* **taskStatus** (enum): PENDING, IN\_PROGRESS, COMPLETED, OVERDUE, CANCELED.  
* **taskPriority** (enum): LOW, MEDIUM, HIGH, URGENT.  
* **taskOrigin** (enum): SYSTEM, USER, RULE\_ENGINE.  
* **dueDate** (datetime): When due.  
* **completionDate** (datetime): When completed.  
* **estimatedDuration** (duration): Estimated effort.  
* **actualDuration** (duration): Actual effort.  
* **slaMinutes** (integer, optional): SLA target in minutes.  
* **relatedEntityType** (enum): VISIT, PARTICIPANT, DEVIATION, CRF, SHIPMENT, others.  
* **relatedEntityId** (string): Linked entity id.

### **Metadata**

* **creationDate** (datetime): When created.  
* **lastModifiedDate** (datetime): Last modified.  
* **lastModifiedBy** (string): Last modifier.

### **Relationships**

* **partOf**: Study (1); Owning study.  
* **scopedTo**: Site (0..1); Site scope.  
* **scopedTo**: Visit (0..1); Visit scope.  
* **scopedTo**: Participant (0..1); Participant scope.  
* **assignedTo**: Person (1); Assignee.  
* **assignedBy**: Person (0..1); Assigner.  
* **parentTask**: Task (0..1); Parent task for hierarchies.  
* **childTasks**: Task (0..N); Subtasks.  
* **raises**: Action Item (0..N); Action items.  
* **relatesTo**: CRF (0..1); Related CRF.  
* **relatesTo**: Milestone (0..1); Related milestone.  
* **relatesTo**: Protocol (0..1); Related protocol section.  
* **relatesTo**: Investigational Product (0..1); Related IP.  
* **relatesTo**: Adverse Event (0..1); Related AE.  
* **relatesTo**: Deviation (0..1); Related deviation.  
* **relatesTo**: Discrepancy (Query) (0..N); Related queries.  
* **relatesTo**: Shipment (0..1); Related shipment.  
* **relatesTo**: Sample (0..1); Related sample.  
* **raisesIssues**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Task** (Anyone): Manually create.  
* **Assign Task** (PM): Assign or reassign.  
* **Update Task Status** (Owner): Move along workflow.  
* **Complete Task** (Owner): Close as done.  
* **Cancel Task** (PM): Cancel with reason.

## **8\. Participant (Subject)**

A Participant is an individual enrolled (or being screened) in a study. Participant is the central data subject; nearly every clinical observation, sample, and outcome relates back to a Participant.  
***Editor note.** v0.2: deduplicated v0 (which had Participant entries at index 8 and 9 in the relationships list); merged into a single Participant. Added decentralizedConsentMethod to support remote-first studies.*

### **Attributes**

* **participantId** (string, unique): Pseudonymous study identifier (subject number).  
* **screeningNumber** (string): Screening number assigned at site.  
* **randomizationNumber** (string, optional): Randomization id where applicable.  
* **enrollmentStatus** (enum): SCREENING, SCREENED, ELIGIBLE, ENROLLED, RANDOMIZED, ON\_TREATMENT, FOLLOW\_UP, COMPLETED, WITHDRAWN, SCREEN\_FAILED, LOST\_TO\_FOLLOWUP.  
* **gender** (enum, FHIR Administrative Gender): Administrative gender.  
* **sexAssignedAtBirth** (enum, optional): Where collected and permitted by jurisdiction.  
* **dateOfBirth** (date): DOB; subject to anonymization in projections.  
* **age** (integer): Age in years (computed).  
* **race** (array\<enum\>): Race categories per local rules.  
* **ethnicity** (enum): Ethnicity per local rules.  
* **enrollmentDate** (date): Enrollment date.  
* **consentDate** (date): Initial consent date.  
* **consentVersion** (string): Consent form version.  
* **decentralizedConsentMethod** (enum, optional): IN\_PERSON, ECONSENT, REMOTE\_ECONSENT, HYBRID.  
* **lastVisitDate** (date): Most recent visit.  
* **expectedCompletionDate** (date): Anticipated completion.  
* **actualCompletionDate** (date, optional): Actual completion.  
* **completionReason** (enum, optional): Reason completed or discontinued.  
* **withdrawalDate** (date, optional): Withdrawal date.  
* **withdrawalReason** (enum, optional): Reason for withdrawal.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **siteOfRecord** (string): Primary site for the participant.

### **Relationships**

* **enrolledIn**: Study (1); Study.  
* **enrolledAt**: Site (1); Site of enrollment.  
* **allocatedTo**: Arm (0..1); Treatment arm.  
* **hasVisits**: Visit (0..N); Visits.  
* **hasCRFs**: CRF (0..N); CRFs.  
* **hasConsent**: Informed Consent (1..N); Consent records (including re-consents).  
* **hasScreeningRecord**: Screening Record (1); Screening data; flagged as missing object below.  
* **hasRandomizationAssignment**: Randomization Assignment (0..1); Randomization assignment object; flagged as missing.  
* **receives**: Investigational Product Dispensation (1..N); IP dispensations.  
* **records**: Adverse Event (0..N); AEs.  
* **records**: Serious Adverse Event (0..N); SAEs.  
* **records**: Deviation (0..N); Deviations.  
* **hasLabResults**: Lab Results (0..N); Labs.  
* **hasVitals**: Vital Sign Record (0..N); Vitals.  
* **responds**: Questionnaire (0..N); COA / PRO responses.  
* **takes**: Concomitant Medication (0..N); Conmeds; flagged as missing object below.  
* **has**: Medical History Record (0..N); Medical history; flagged as missing object below.  
* **raises**: Discrepancy (Query) (0..N); Queries.  
* **has**: Demographic Information (1); Demographics block.  
* **hasScreenFail**: Screen Fail (0..1); Screen fail record.  
* **hasEarlyTermination**: Early Termination Record (0..1); Early termination; flagged as missing object below.  
* **hasDocuments**: Document (0..N); Signed ICF, source docs.  
* **producesData**: Endpoint Data (0..N); Endpoint data.  
* **suppliesSample**: Sample (0..N); Samples collected from the participant.  
* **hasImaging**: Imaging Record (0..N); Imaging.  
* **records**: Diary Entry (0..N); Diary entries.  
* **runs**: Procedure Record (0..N); Procedures.  
* **assessedAgainst**: Inclusion Criteria (1..N); Eligibility assessments.  
* **assessedAgainst**: Exclusion Criteria (1..N); Eligibility assessments.  
* **producesPRO**: Patient Reported Outcome (0..N); PRO instruments.  
* **generates**: Wearable Device Data (0..N); Wearable data.  
* **providesPK**: Pharmacokinetic Sample (0..N); PK samples.  
* **has**: Drug Accountability Record (0..N); Drug accountability.  
* **receives**: Follow-up Contact (0..N); Follow-up contacts.  
* **has**: Unscheduled Visit (0..N); Unscheduled visits.  
* **hasEnrollmentRecord**: Enrollment (1); Enrollment event record.  
* **receives**: Payment (0..N); Stipends or reimbursements where allowed.  
* **has**: Data Correction Form (0..N); Corrections.  
* **acknowledges**: Amendment (0..N); Amendment acknowledgments.  
* **providesGenetic**: Sample (0..N); Genetic or biomarker samples.  
* **withdrawsConsent**: Informed Consent (0..1); Withdrawal of consent record.

### **Calls to Action**

* **Screen Participant** (Coordinator): Begin screening.  
* **Enroll Participant** (Coordinator): Move to enrolled.  
* **Update Participant Details** (Coordinator): Edit demographics or contacts.  
* **Schedule Participant Visit** (Coordinator): Plan next visit.  
* **Withdraw Participant** (PI): Record withdrawal with reason.  
* **Complete Participant Study** (PI): Mark study completion for the participant.  
* **Project to FHIR Patient** (Visual Explorer): Render as FHIR Patient and ResearchSubject.  
* **Project to USDM StudySubject** (Visual Explorer): Render as USDM StudySubject.  
* **Project to CDASH DM domain** (Visual Explorer): Map demographics to CDASH DM.

## **9\. Discrepancy (Query)**

A Discrepancy (Query) is an issue or question raised about a specific data point or record that requires clarification or correction. Queries are central to data quality workflows.  
***Editor note.** v0.2: added autoGenerated flag to distinguish edit-check-generated queries; queryAgeDays as derived metadata.*

### **Attributes**

* **queryId** (string, unique): Identifier.  
* **queryType** (enum): MISSING\_DATA, OUT\_OF\_RANGE, INCONSISTENCY, CLARIFICATION, AUTO\_EDIT\_CHECK.  
* **queryStatus** (enum): OPEN, ANSWERED, CLOSED, CANCELED.  
* **queryPriority** (enum): LOW, MEDIUM, HIGH.  
* **queryText** (string): Query body.  
* **responseText** (string, optional): Response.  
* **queryCategory** (enum): SAFETY, EFFICACY, ADMINISTRATIVE.  
* **impactLevel** (enum): MINOR, MAJOR, CRITICAL.  
* **source** (enum): DATA\_ENTRY, MONITORING, CENTRAL\_REVIEW, EDIT\_CHECK.  
* **identificationMethod** (enum): MANUAL\_REVIEW, AUTO\_CHECK.  
* **autoGenerated** (boolean): Whether system generated.  
* **dataPointInQuestion** (string): Reference to the data point.  
* **originalValue** (string): Original value.  
* **correctedValue** (string, optional): Corrected value.

### **Metadata**

* **createdDate** (datetime): Creation.  
* **createdBy** (string): Creator.  
* **assignedTo** (string): Assignee.  
* **resolutionDate** (datetime, optional): Resolution.  
* **resolvedBy** (string, optional): Resolver.  
* **queryAgeDays** (integer): Derived: days open.  
* **lifecycleTimestamps** (object): opened, answered, closed.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (1); Site.  
* **scopedTo**: Participant (0..1); Participant.  
* **scopedTo**: Visit (0..1); Visit.  
* **raisedAgainst**: CRF (1); Target CRF.  
* **raisedAgainst**: Lab Results (0..1); Related lab.  
* **raisedAgainst**: Investigational Product (0..1); Related IP.  
* **relatesTo**: Adverse Event (0..1); Related AE.  
* **relatesTo**: Deviation (0..1); Related deviation.  
* **relatesTo**: Task (0..1); Related task.  
* **relatesTo**: Endpoint (0..1); Related endpoint.  
* **relatesTo**: Sample (0..1); Related sample.  
* **relatesTo**: Equipment (0..1); Related equipment.  
* **relatesTo**: Monitoring Visit (0..1); Related monitoring visit.  
* **relatesTo**: Protocol (0..1); Related section.  
* **relatesTo**: Schedule of Assessments (0..1); Related SOA item.  
* **relatesTo**: Data Transfer (0..1); Related transfer.  
* **relatesTo**: CAPA (0..1); Related CAPA.  
* **hasDocuments**: Document (0..N); Supporting evidence.  
* **audits**: Audit Trail Entry (1..N); Trail.  
* **hasComments**: Comment (0..N); Comments.

### **Calls to Action**

* **Create Query** (CRA / Data Manager): Open a new query.  
* **Assign Query** (Data Manager): Assign to site.  
* **Respond to Query** (Site Coordinator): Provide response.  
* **Close Query** (Data Manager): Close after resolution.  
* **Reopen Query** (CRA / Data Manager): Reopen if response insufficient.

## **10\. Deviation**

A Deviation is any departure from the approved protocol, GCP, or applicable regulations. Deviations are tracked for participant safety, data integrity, and regulatory reporting.  
***Editor note.** v0.2: added irbReportingDueDate and regulatoryReportingDueDate derived from severity and jurisdiction; preserved existing severity/category vocabulary.*

### **Attributes**

* **deviationId** (string, unique): Identifier.  
* **deviationType** (enum): INCLUSION\_EXCLUSION, DOSING, PROCEDURE, VISIT\_WINDOW, INFORMED\_CONSENT, OTHER.  
* **deviationCategory** (enum): MINOR, MAJOR, CRITICAL.  
* **deviationClassification** (enum): PROTOCOL\_DEVIATION, GCP\_DEVIATION.  
* **severity** (enum): LOW, MEDIUM, HIGH.  
* **deviationDescription** (string): Description.  
* **deviationDate** (date): Date of occurrence.  
* **discoveryDate** (date): Date of discovery.  
* **identificationMethod** (enum): SITE\_REPORTED, MONITOR\_IDENTIFIED, AUDIT\_FINDING.  
* **rootCauseAnalysis** (string, optional): Root cause text.  
* **correctiveAction** (string, optional): Corrective action.  
* **preventiveAction** (string, optional): Preventive action.  
* **impact** (string): Impact assessment.  
* **protocolSectionReference** (string): Protocol section.  
* **irbReportingStatus** (enum, optional): IRB / EC reporting status.  
* **regulatoryReportingStatus** (enum, optional): Regulatory authority reporting status.  
* **irbReportingDueDate** (date, optional): Derived due date.  
* **regulatoryReportingDueDate** (date, optional): Derived due date.  
* **potentialImpactOnSafety** (string): Patient safety / data integrity impact.

### **Metadata**

* **reportedBy** (string): Reporter.  
* **reportedDate** (datetime): Report date.  
* **reviewedBy** (string): Reviewer.  
* **reviewedDate** (datetime, optional): Review date.  
* **deviationStatus** (enum): REPORTED, REVIEWED, CLOSED.  
* **resolutionDate** (date): Resolution date.  
* **resolvedBy** (string): Resolver.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (1); Site.  
* **scopedTo**: Participant (0..1); Participant.  
* **scopedTo**: Visit (0..1); Visit.  
* **relatesTo**: Task (0..1); Task.  
* **relatesTo**: Adverse Event (0..1); AE.  
* **relatesTo**: Investigational Product (0..1); IP.  
* **raises**: Discrepancy (Query) (0..N); Queries.  
* **relatesTo**: Monitoring Visit (0..1); Monitoring visit.  
* **relatesTo**: CAPA (0..1); CAPA.  
* **relatesTo**: CRF (0..1); CRF.  
* **relatesTo**: Lab Results (0..1); Lab.  
* **relatesTo**: Sample (0..1); Sample.  
* **relatesTo**: Equipment (0..1); Equipment.  
* **relatesTo**: Informed Consent (0..1); Consent.  
* **relatesTo**: Data Transfer (0..1); Transfer.  
* **relatesTo**: Endpoint (0..1); Endpoint.  
* **hasDocuments**: Document (0..N); Supporting docs.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Report Deviation** (Site / CRA): File a new deviation.  
* **Review Deviation** (Sponsor Quality): Review and classify.  
* **Approve or Reject Deviation** (Sponsor Quality): Decision on classification.  
* **Implement Corrective Action** (Site): Execute corrective steps.  
* **Close Deviation** (Sponsor Quality): Close after CAPA verification.

## **11\. Screen Fail**

A Screen Fail records a participant who did not satisfy eligibility during screening. Tracking screen fails is essential for refining eligibility, predicting yield, and assessing site performance.  
***Editor note.** v0.2: timeInScreeningPeriod expressed as duration; reimbursementStatus moved to Payment relationship.*

### **Attributes**

* **screenFailId** (string, unique): Identifier.  
* **screeningNumber** (string): Screening id.  
* **screenFailDate** (date): Date of screen fail.  
* **screenFailReason** (array\<enum\>): Reasons (failed inclusion, failed exclusion, withdrew consent, lost to follow-up, AE during screening, other).  
* **failedInclusionCriteria** (array\<criteriaId\>): Failed inclusion criteria.  
* **failedExclusionCriteria** (array\<criteriaId\>): Failed exclusion criteria.  
* **investigatorAssessment** (string): PI rationale.  
* **informedConsentStatus** (enum): OBTAINED, WITHDRAWN, NOT\_OBTAINED.  
* **rescreeningEligibility** (boolean, optional): Eligible to rescreen.  
* **rescreeningDate** (date, optional): Planned rescreen date.  
* **screenFailVerificationStatus** (enum): PENDING, VERIFIED, DISPUTED.  
* **timeInScreeningPeriod** (duration): Duration in screening.  
* **impactOnEnrollmentMetrics** (string): Impact note.

### **Metadata**

* **reportedBy** (string): Reporter.  
* **reportedDate** (datetime): Report date.  
* **reviewedBy** (string): Reviewer.  
* **reviewedDate** (datetime, optional): Review date.  
* **dataEntryTimestamp** (datetime): Data entry timestamp.  
* **dataEntryUser** (string): Data entry user.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (1); Site.  
* **for**: Participant (1); Participant.  
* **observedAt**: Visit (1); Screening visit.  
* **hasCRFs**: CRF (0..N); Screening CRFs.  
* **hasLabResults**: Lab Results (0..N); Screening labs.  
* **records**: Vital Sign Measurement (0..N); Vitals.  
* **records**: Physical Examination Result (0..N); Exams.  
* **records**: Adverse Event (0..N); AEs during screening.  
* **hasDocuments**: Document (0..N); Source docs.  
* **raises**: Discrepancy (Query) (0..N); Queries.  
* **records**: Concomitant Medication (0..N); Conmeds.  
* **has**: Medical History Item (0..N); Medical history.  
* **records**: Imaging Procedure Result (0..N); Imaging.  
* **administers**: Questionnaire (0..N); Questionnaires.  
* **producesPRO**: Patient Reported Outcome (0..N); PROs.  
* **relatesTo**: Task (0..1); Follow-up task.  
* **relatesTo**: Deviation (0..1); Deviation if screening process deviated.  
* **triggers**: Payment (0..1); Reimbursement payment.  
* **relatesTo**: Sample (0..1); Sample collected during screening.  
* **relatesTo**: Equipment (0..1); Equipment used.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Record Screen Fail** (Coordinator): Capture screen fail.  
* **Review Screen Fail** (PI): Review reasoning.  
* **Approve Screen Fail** (Sponsor Medical): Approve and close.  
* **Plan Rescreen** (Coordinator): Schedule rescreen if eligible.

## **12\. Person**

A Person represents any individual involved in trial conduct, including investigators, coordinators, monitors, biostatisticians, regulatory staff, and pharmacy. The Person object underpins identity, role, training, and access.  
***Editor note.** v0.2: investigators are still represented as Person, but a separate Investigator object is recommended (see Section 6 Change Log and Cross-cutting); added orcid and npi for canonical identifier mapping.*

### **Attributes**

* **personId** (string, unique): Identifier.  
* **firstName** (string): First name.  
* **lastName** (string): Last name.  
* **middleName** (string, optional): Middle name.  
* **title** (string, optional): Title.  
* **orcid** (string, optional): ORCID id.  
* **npi** (string, optional): US National Provider Identifier.  
* **organization** (string): Employer organisation.  
* **department** (string): Department.  
* **email** (string): Email.  
* **phone** (string): Phone.  
* **address** (object): Address.  
* **gender** (enum): Administrative gender.  
* **dateOfBirth** (date, optional): DOB; restricted access.  
* **startDate** (date): Engagement start.  
* **endDate** (date, optional): Engagement end.  
* **status** (enum): ACTIVE, INACTIVE, ON\_LEAVE.  
* **employmentStatus** (enum): EMPLOYEE, CONTRACTOR, CONSULTANT, AFFILIATE.  
* **gcpTrainingStatus** (enum): CURRENT, EXPIRED, NOT\_TRAINED.  
* **protocolTrainingStatus** (enum): CURRENT, EXPIRED, NOT\_TRAINED.  
* **languageProficiency** (array\<BCP-47\>): Languages.  
* **lastSystemAccessDate** (datetime): Last login date.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **worksOn**: Study (0..N); Studies.  
* **worksAt**: Site (0..N); Sites.  
* **holdsRole**: Person Role (1..N); Roles.  
* **holdsCredential**: Credential (0..N); Credentials.  
* **hasTrainingRecords**: Training Record (0..N); Trainings.  
* **holdsCertifications**: Certification (0..N); Certifications.  
* **ownsTasks**: Task (0..N); Tasks assigned or created.  
* **authors**: Document (0..N); Authored or reviewed docs.  
* **raises**: Discrepancy (Query) (0..N); Created or resolved queries.  
* **reports**: Deviation (0..N); Reported or reviewed deviations.  
* **signs**: Signature (0..N); Signatures.  
* **hasUserAccount**: User Account (1); System access.  
* **holdsRoles**: User Role (0..N); System role assignments.  
* **conducts**: Monitoring Visit (0..N); Monitoring visits.  
* **ownsActionItems**: Action Item (0..N); Action items.  
* **logs**: Log Entry (0..N); Log entries.  
* **reports**: Adverse Event (0..N); AEs reported.  
* **reports**: Serious Adverse Event (0..N); SAEs reported.  
* **administers**: Informed Consent (0..N); Consent administrations.  
* **completes**: CRF (0..N); CRFs completed.  
* **has**: CV (1); Curriculum Vitae.  
* **delegatedBy**: Delegation of Authority Record (1..N); Delegation records.  
* **acknowledges**: Amendment (0..N); Amendments acknowledged.  
* **files**: Regulatory Submission (0..N); Submissions handled.  
* **authors**: Report (0..N); Reports.  
* **involvedIn**: CAPA (0..N); CAPAs.  
* **handles**: Shipment (0..N); Shipments.  
* **responsibleFor**: Equipment (0..N); Equipment.  
* **communicates**: Communication Record (0..N); Communication records.  
* **discloses**: Conflict of Interest Disclosure (0..N); COI disclosures.

### **Calls to Action**

* **Create Person** (Sponsor Admin): Create person record.  
* **Update Person Details** (Sponsor Admin): Edit profile.  
* **Assign Role to Person** (Sponsor Admin): Add a role.  
* **Deactivate Person** (Sponsor Admin): Disable.  
* **Reactivate Person** (Sponsor Admin): Re-enable.  
* **Project to FHIR Practitioner** (Visual Explorer): Render as FHIR Practitioner.

## **13\. Person Role**

A Person Role is a named role assignable to a Person, with category, permissions, and description. Roles are the building blocks of access control and accountability.  
***Editor note.** v0.2: added permissions schema reference; clarified relation to User Role (Person Role describes the human role; User Role describes the system permission grouping).*

### **Attributes**

* **roleId** (string, unique): Identifier.  
* **roleName** (string): Display name (e.g., Principal Investigator, Coordinator, Pharmacist).  
* **roleDescription** (string): Description.  
* **roleCategory** (enum): CLINICAL, OPERATIONS, REGULATORY, QUALITY, FINANCE, DATA, EXECUTIVE.  
* **permissions** (array\<permissionId\>): Permission ids granted to the role.  
* **status** (enum): ACTIVE, INACTIVE.

### **Metadata**

* **createdBy** (string): Creator.  
* **creationDate** (datetime): Created.  
* **modifiedBy** (string): Modifier.  
* **modificationDate** (datetime): Modified.

### **Relationships**

* **heldBy**: Person (0..N); People holding this role.  
* **groupedBy**: Tag (0..N); Tags.  
* **mapsToUserRole**: User Role (0..1); Equivalent system permission set.

### **Calls to Action**

* **Create Role** (Sponsor Admin): Define a new role.  
* **Update Role Details** (Sponsor Admin): Edit attributes.  
* **Assign Permissions to Role** (Sponsor Admin): Manage permission grants.  
* **Deactivate Role** (Sponsor Admin): Disable.

## **14\. CRF (Case Report Form)**

A CRF is a structured form used to capture protocol-required data for a participant. CRFs are the primary input to clinical analysis databases and the principal target of source data verification.  
***Editor note.** v0.2: added odmDefRef linking each CRF to its CDISC ODM definition; surfaced lockStatus separately from sdvStatus.*

### **Attributes**

* **crfId** (string, unique): Identifier.  
* **crfName** (string): Display name.  
* **crfType** (enum): DEMOGRAPHICS, VITAL\_SIGNS, ADVERSE\_EVENTS, MEDICAL\_HISTORY, LAB, OTHER.  
* **crfVersion** (string): Version.  
* **crfStatus** (enum): NOT\_STARTED, IN\_PROGRESS, COMPLETED, VERIFIED, LOCKED.  
* **dataEntryMethod** (enum): EDC, PAPER, eSOURCE, IMPORT.  
* **lockStatus** (enum): UNLOCKED, SOFT\_LOCK, HARD\_LOCK.  
* **sdvStatus** (enum): NOT\_REQUIRED, PENDING, COMPLETE.  
* **sdvBy** (string, optional): SDV person.  
* **sdvDate** (date, optional): SDV date.  
* **electronicSignatureStatus** (enum): NOT\_REQUIRED, PENDING, SIGNED.  
* **dataExportStatus** (enum): NOT\_EXPORTED, EXPORTED, EXPORT\_FAILED.  
* **crfTemplateReference** (string): Reference to the template definition.  
* **crfCompletionGuidelinesReference** (string): Reference to completion guidelines.  
* **formSpecificValidationRules** (array\<object\>): Validation rule references.  
* **odmDefRef** (string, optional): CDISC ODM ItemGroupDef reference.

### **Metadata**

* **completedBy** (string): Completer.  
* **completedDate** (datetime): Completion.  
* **reviewedBy** (string, optional): Reviewer.  
* **reviewedDate** (datetime, optional): Review date.  
* **lastModifiedDate** (datetime): Last modified.  
* **lastModifiedBy** (string): Last modifier.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (1); Site.  
* **for**: Participant (1); Participant.  
* **observedAt**: Visit (0..1); Visit (when visit-specific).  
* **contains**: Data Field (1..N); Data fields.  
* **raises**: Discrepancy (Query) (0..N); Queries.  
* **records**: Deviation (0..N); Deviations recorded.  
* **hasDocuments**: Document (0..N); Source docs.  
* **relatesTo**: Task (0..1); Task.  
* **relatesTo**: Lab Results (0..1); Related lab.  
* **relatesTo**: Adverse Event (0..1); Related AE.  
* **relatesTo**: Serious Adverse Event (0..1); Related SAE.  
* **relatesTo**: Concomitant Medication (0..1); Conmed.  
* **relatesTo**: Physical Examination (0..1); Exam.  
* **relatesTo**: Vital Signs (0..1); Vitals.  
* **relatesTo**: Investigational Product Administration (0..1); IP admin record.  
* **relatesTo**: Patient Reported Outcome (0..1); PRO.  
* **relatesTo**: Endpoint Data (0..1); Endpoint data.  
* **relatesTo**: Sample Collection (0..1); Sample.  
* **relatesTo**: Equipment Usage (0..1); Equipment use.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create CRF** (Data Manager): Instantiate from template.  
* **Update CRF** (Coordinator): Edit data.  
* **Complete CRF** (Coordinator): Mark complete.  
* **Review CRF** (PI): Investigator review.  
* **Lock or Unlock CRF** (Data Manager): Apply or release locks.  
* **Sign CRF** (PI): Apply electronic signature.  
* **Project to ODM ItemGroupData** (Visual Explorer): Render as ODM ItemGroupData.

## **15\. Document**

A Document is any file or record associated with the trial: protocols, ICFs, regulatory packs, monitoring reports, source documents, training materials, and so on. Document is heavily used by every other object as supporting evidence.  
***Editor note.** v0.2: added contentHash (SHA-256) for integrity verification; tmfReference points to the TMF zone, section, artifact per DIA TMF Reference Model.*

### **Attributes**

* **documentId** (string, unique): Identifier.  
* **documentTitle** (string): Title.  
* **documentDescription** (string): Description.  
* **documentType** (enum): PROTOCOL, ICF, REGULATORY, SOURCE, TRAINING, REPORT, AGREEMENT, OTHER.  
* **documentClassification** (enum): ESSENTIAL\_DOCUMENT, SOURCE\_DOCUMENT, REGULATORY\_DOCUMENT, ADMINISTRATIVE.  
* **documentVersion** (string): Version.  
* **documentStatus** (enum): DRAFT, IN\_REVIEW, APPROVED, EFFECTIVE, SUPERSEDED, RETIRED.  
* **fileType** (enum): PDF, DOCX, XLSX, PPTX, JPG, PNG, XML, JSON, OTHER.  
* **fileLocation** (URI): Storage URI.  
* **fileSize** (integer, bytes): Size in bytes.  
* **contentHash** (string, SHA-256): Content hash.  
* **documentLanguage** (BCP-47): Language.  
* **retentionPeriod** (duration): Retention period.  
* **expirationDate** (date, optional): Expiration if applicable.  
* **electronicSignatureStatus** (enum): NOT\_REQUIRED, PENDING, SIGNED.  
* **accessControlList** (object): ACL.  
* **tmfReference** (object): TMF zone / section / artifact reference.  
* **documentTemplateReference** (string, optional): Source template id.

### **Metadata**

* **creationDate** (datetime): Creation.  
* **createdBy** (string): Creator.  
* **lastModifiedDate** (datetime): Last modified.  
* **lastModifiedBy** (string): Last modifier.  
* **approvalStatus** (enum): PENDING, APPROVED, REJECTED.  
* **approvalDate** (date, optional): Approval date.  
* **approvedBy** (string, optional): Approver.  
* **qualityControlStatus** (enum): PENDING, PASSED, FAILED.  
* **qualityControlBy** (string): QC person.  
* **qualityControlDate** (date): QC date.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (0..1); Site (if site-specific).  
* **for**: Participant (0..1); Participant (if participant-specific).  
* **relatesTo**: CRF (0..N); Related CRFs.  
* **relatesTo**: Visit (0..1); Related visit.  
* **relatesTo**: Adverse Event (0..1); AE.  
* **relatesTo**: Deviation (0..1); Deviation.  
* **relatesTo**: Monitoring Visit (0..1); Monitoring visit.  
* **relatesTo**: Regulatory Submission (0..1); Submission.  
* **relatesTo**: Audit (0..1); Audit.  
* **translatedFrom**: Document (0..1); Source language version.  
* **translatedTo**: Document (0..N); Translations.  
* **relatesTo**: Training Record (0..N); Trainings.  
* **relatesTo**: Task (0..N); Tasks.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Upload Document** (Anyone): Upload a file.  
* **Update Document Metadata** (Owner): Edit attributes.  
* **Review Document** (Reviewer): Mark reviewed.  
* **Approve Document** (Approver): Approve.  
* **Version Document** (Owner): Create new version.  
* **Archive Document** (Records Manager): Move to archive.

## **16\. Adverse Event**

An Adverse Event (AE) is any unfavourable medical occurrence in a participant during the trial, whether or not related to the intervention. AE tracking is fundamental to participant safety and pharmacovigilance.  
***Editor note.** v0.2: codingDictionary explicitly noted (MedDRA version), and aiPipelineFlag added to mark AE narratives produced or assisted by automated coding.*

### **Attributes**

* **adverseEventId** (string, unique): Identifier.  
* **aeNumber** (string): Site or sponsor AE number.  
* **aeDescription** (string): Description.  
* **aeStartDate** (datetime): Onset.  
* **aeEndDate** (datetime, optional): Resolution.  
* **aeSeverity** (enum): MILD, MODERATE, SEVERE.  
* **intensityGrade** (enum, optional): CTCAE grade where applicable.  
* **aeSeriousness** (enum): NON\_SERIOUS, SERIOUS.  
* **aeRelationship** (enum): NOT\_RELATED, UNLIKELY, POSSIBLE, PROBABLE, DEFINITE.  
* **causalityAssessment** (string): Causality narrative.  
* **actionTaken** (enum): NONE, DOSE\_REDUCED, DOSE\_INTERRUPTED, DRUG\_WITHDRAWN, OTHER.  
* **outcome** (enum): RECOVERED, RECOVERING, NOT\_RECOVERED, RECOVERED\_WITH\_SEQUELAE, FATAL, UNKNOWN.  
* **expectedness** (enum): EXPECTED, UNEXPECTED.  
* **susarStatus** (enum, optional): SUSAR classification.  
* **frequency** (enum): SINGLE, INTERMITTENT, CONTINUOUS.  
* **pattern** (string): Pattern note.  
* **medDraCode** (string): MedDRA Preferred Term code.  
* **medDraTerm** (string): MedDRA preferred term.  
* **codingDictionary** (string): MedDRA version.  
* **regulatoryReportingStatus** (enum): NOT\_REQUIRED, PENDING, SUBMITTED.  
* **aeResolutionStatus** (enum): OPEN, CLOSED, FOLLOW\_UP\_REQUIRED.  
* **followUpRequired** (boolean): Follow-up required flag.  
* **followUpDate** (date, optional): Follow-up date.  
* **aiPipelineFlag** (boolean, optional): Coded with AI assistance.

### **Metadata**

* **reportedBy** (string): Reporter.  
* **reportedDate** (datetime): Report date.  
* **investigatorAssessmentDate** (datetime): PI assessment date.  
* **investigatorAssessmentBy** (string): Assessor.  
* **reviewedBy** (string, optional): Reviewer.  
* **reviewedDate** (datetime, optional): Review date.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (1); Site.  
* **for**: Participant (1); Participant.  
* **relatesTo**: Serious Adverse Event (0..1); Linked SAE.  
* **relatesTo**: Concomitant Medication (0..N); Conmeds.  
* **recordedOn**: CRF (1..N); CRFs.  
* **hasDocuments**: Document (0..N); Supporting evidence.  
* **relatesTo**: Task (0..N); Tasks.  
* **raises**: Discrepancy (Query) (0..N); Queries.  
* **relatesTo**: Deviation (0..1); Deviation cause.  
* **relatesTo**: Visit (0..1); Visit context.  
* **relatesTo**: Lab Results (0..1); Triggering lab.  
* **relatesTo**: Investigational Product Administration (0..1); IP admin event.  
* **triggers**: CAPA (0..N); CAPAs.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Report Adverse Event** (Coordinator): File AE.  
* **Update Adverse Event Details** (Coordinator): Edit.  
* **Assess Adverse Event** (PI): Causality and severity assessment.  
* **Follow Up on Adverse Event** (Coordinator): Follow-up visit.  
* **Close Adverse Event** (PI): Close after resolution.  
* **Project to FHIR AdverseEvent** (Visual Explorer): Render as FHIR AdverseEvent.  
* **Project to CDASH AE domain** (Visual Explorer): Map to CDASH AE.

## **17\. Informed Consent**

An Informed Consent record captures the process and documentation by which a participant agrees to participate after being informed of all relevant aspects. This is an ethical and regulatory cornerstone.  
***Editor note.** v0.2: clarified eConsent fields and added accessibility (large print, audio) attribute; reConsentTriggerEvent enumerates what triggers re-consent.*

### **Attributes**

* **consentId** (string, unique): Identifier.  
* **consentVersion** (string): ICF version.  
* **consentDate** (date): Consent date.  
* **consentTime** (time): Consent time.  
* **consentStatus** (enum): OBTAINED, WITHDRAWN, RECONSENTED.  
* **consentMethod** (enum): IN\_PERSON, ECONSENT, REMOTE\_ECONSENT, HYBRID.  
* **consentLanguage** (BCP-47): Language used.  
* **translatorUsed** (boolean): Translator present.  
* **translatorName** (string, optional): Translator name.  
* **reconsentRequired** (boolean): Re-consent required.  
* **reconsentDueDate** (date, optional): Re-consent deadline.  
* **reConsentTriggerEvent** (enum, optional): AMENDMENT, SAFETY\_UPDATE, JURISDICTION\_CHANGE, OTHER.  
* **withdrawalDate** (date, optional): Withdrawal.  
* **withdrawalReason** (string, optional): Reason.  
* **verifiedBy** (string, optional): Verifier.  
* **verificationDate** (date, optional): Verification date.  
* **electronicSignatureStatus** (enum): NOT\_REQUIRED, PENDING, SIGNED.  
* **accessibilityFeatures** (array\<enum\>): LARGE\_PRINT, AUDIO, BRAILLE, EASY\_READ, TRANSLATED.  
* **consentStorageLocation** (string): Storage location.  
* **consentExpirationDate** (date, optional): Expiration.  
* **consentComprehensionCheckStatus** (enum): NOT\_DONE, PASSED, FAILED.  
* **consentingPersonRelationship** (enum): PARTICIPANT, LEGAL\_REPRESENTATIVE, PARENT\_OR\_GUARDIAN.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **consentingPersonId** (string): Consenting person.  
* **personObtainingConsentId** (string): Person obtaining consent.  
* **consentWitnessId** (string, optional): Witness.  
* **qcStatus** (enum): PENDING, PASSED, FAILED.  
* **qcBy** (string): QC person.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (1); Site.  
* **for**: Participant (1); Participant.  
* **hasDocuments**: Document (1..N); Signed forms, info sheets.  
* **relatesTo**: Visit (0..1); Screening visit typically.  
* **raises**: Discrepancy (Query) (0..N); Queries.  
* **relatesTo**: Deviation (0..1); Deviation if process failed.  
* **containsElements**: Consent Element (1..N); Specific items consented to.  
* **relatesTo**: Protocol (1); Protocol version.  
* **relatesTo**: Amendment (0..1); Amendment that triggered re-consent.  
* **triggersTask**: Task (0..1); Re-consent task.  
* **approvedBy**: Oversight Body (1); IRB / EC approval of the form.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Informed Consent** (Sponsor / Site): Create new ICF instance.  
* **Update Informed Consent** (Coordinator): Update version or status.  
* **Obtain Participant Consent** (PI / Coordinator): Run consent process.  
* **Record Consent Discussion** (Coordinator): Capture discussion notes.  
* **Withdraw Consent** (Participant / Coordinator): Record withdrawal.

## **18\. Action Item**

An Action Item is a granular follow-up item, often arising from monitoring visits, audits, or quality reviews. Action items are typically narrower than tasks and often linked to a finding.  
***Editor note.** v0.2: separated parent and child action items into a relationship; recurrenceFrequency aligned with iCal RRULE.*

### **Attributes**

* **actionItemId** (string, unique): Identifier.  
* **actionItemTrackingNumber** (string): Tracking number.  
* **actionItemDescription** (string): Description.  
* **actionItemStatus** (enum): OPEN, IN\_PROGRESS, COMPLETED, OVERDUE, CANCELED.  
* **priority** (enum): LOW, MEDIUM, HIGH, CRITICAL.  
* **actionItemImpactLevel** (enum): LOW, MEDIUM, HIGH.  
* **actionItemCategory** (enum): DATA\_QUERY, PROTOCOL\_DEVIATION, REGULATORY, SAFETY, OTHER.  
* **actionItemSource** (enum): MONITOR, INVESTIGATOR, DATA\_MANAGER, AUDITOR, OTHER.  
* **dueDate** (datetime): Due date.  
* **completionDate** (datetime, optional): Completion.  
* **estimatedEffort** (duration): Estimated time.  
* **actualEffort** (duration, optional): Actual time.  
* **recurrenceFrequency** (string, RRULE): Recurrence rule.  
* **verificationStatus** (enum): PENDING, VERIFIED, FAILED.  
* **resolutionNotes** (string): Notes.  
* **actionItemClosureNotes** (string): Closure notes.

### **Metadata**

* **creationDate** (datetime): Creation.  
* **createdBy** (string): Creator.  
* **lastModifiedDate** (datetime): Modified.  
* **lastModifiedBy** (string): Modifier.  
* **verifiedBy** (string, optional): Verifier.  
* **verificationDate** (datetime, optional): Verification date.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (0..1); Site (if site-specific).  
* **assignedTo**: Person (1); Assignee.  
* **assignedBy**: Person (1); Assigner.  
* **parentActionItem**: Action Item (0..1); Parent.  
* **childActionItems**: Action Item (0..N); Children.  
* **relatesTo**: Visit (0..1); Visit.  
* **for**: Participant (0..1); Participant.  
* **relatesTo**: Monitoring Visit (0..1); Monitoring visit.  
* **relatesTo**: Audit (0..1); Audit.  
* **relatesTo**: Deviation (0..1); Deviation.  
* **relatesTo**: Adverse Event (0..1); AE.  
* **relatesTo**: CRF (0..1); CRF.  
* **hasDocuments**: Document (0..N); Supporting docs.  
* **raises**: Discrepancy (Query) (0..N); Queries.  
* **triggers**: CAPA (0..1); Linked CAPA.  
* **relatesTo**: Protocol (0..1); Protocol section.  
* **relatesTo**: Investigational Product (0..1); IP.  
* **relatesTo**: Equipment (0..1); Equipment.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Action Item** (Anyone): Create.  
* **Assign Action Item** (PM): Assign or reassign.  
* **Update Action Item Status** (Owner): Workflow update.  
* **Complete Action Item** (Owner): Mark done.  
* **Cancel Action Item** (PM): Cancel.

## **19\. Milestone**

A Milestone marks a significant event or achievement in the lifecycle of a study, used to track progress, manage timelines, and report to stakeholders.  
***Editor note.** v0.2: added forecastDate (model-derived) alongside plannedDate and actualDate to support enrollment and budget forecasting.*

### **Attributes**

* **milestoneId** (string, unique): Identifier.  
* **milestoneName** (string): Name.  
* **milestoneDescription** (string): Description.  
* **milestoneType** (enum): REGULATORY, ENROLLMENT, TREATMENT, DATA\_MANAGEMENT, FINANCIAL, OTHER.  
* **milestoneCategory** (enum): STARTUP, CONDUCT, CLOSEOUT.  
* **plannedDate** (date): Planned date.  
* **forecastDate** (date, optional): Forecast date.  
* **actualDate** (date, optional): Actual date.  
* **milestoneStatus** (enum): PLANNED, IN\_PROGRESS, COMPLETED, DELAYED, CANCELED.  
* **importance** (enum): CRITICAL, HIGH, MEDIUM, LOW.  
* **completionPercentage** (percentage): Progress.  
* **milestoneVisibilityLevel** (enum): SPONSOR\_ONLY, SITE\_VISIBLE, PUBLIC.  
* **milestoneTrackingMethod** (enum): MANUAL, SYSTEM\_CALCULATED.  
* **milestoneFlexibility** (enum): FIXED, ADJUSTABLE.  
* **milestoneDelayReason** (string, optional): Delay reason.  
* **milestoneDelayMitigationPlan** (string, optional): Mitigation plan.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **createdBy** (string): Creator.  
* **lastModifiedDate** (datetime): Modified.  
* **lastModifiedBy** (string): Modifier.  
* **lastReviewDate** (date): Last review.  
* **lastReviewedBy** (string): Last reviewer.  
* **nextReviewDate** (date): Next review.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (0..1); Site (if site-specific).  
* **ownedBy**: Person (1); Owner.  
* **dependsOn**: Milestone (0..N); Prerequisite milestones.  
* **enables**: Milestone (0..N); Dependent milestones.  
* **hasDocuments**: Document (0..N); Supporting docs.  
* **hasTasks**: Task (0..N); Tasks.  
* **hasActionItems**: Action Item (0..N); Action items.  
* **relatesTo**: Protocol Version (0..1); Protocol version.  
* **relatesTo**: Amendment (0..1); Amendment.  
* **relatesTo**: Regulatory Submission (0..1); Submission.  
* **relatesTo**: Contract (0..1); Contract.  
* **relatesTo**: Budget (0..1); Budget.  
* **relatesTo**: Visit (0..1); Visit.  
* **relatesTo**: Endpoint (0..1); Endpoint.  
* **relatesTo**: Report (0..1); Report.  
* **hasNotificationRules**: Notification Rule (0..N); Notifications.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Milestone** (PM): Add a milestone.  
* **Update Milestone Details** (PM): Edit.  
* **Achieve Milestone** (PM): Mark achieved.  
* **Delay Milestone** (PM): Record delay and reason.  
* **Forecast Milestone** (Analytics): Update forecastDate from model.

## **20\. Enrollment**

An Enrollment is a discrete event recording that a participant has been moved into a study at a site. Enrollment is closely related to but distinct from the Participant entity.  
***Editor note.** v0.2: distinguished Enrollment (event) from Participant (entity); added recruitingChannel for source attribution.*

### **Attributes**

* **enrollmentId** (string, unique): Identifier.  
* **enrollmentNumber** (string): Sequence within study.  
* **randomizationNumber** (string, optional): Randomization id.  
* **enrollmentStatus** (enum): SCREENED, ENROLLED, SCREEN\_FAILED, WITHDRAWN.  
* **enrollmentDate** (date): Enrollment date.  
* **enrollmentMethod** (enum): ON\_SITE, REMOTE, HYBRID.  
* **recruitingChannel** (enum): EHR\_QUERY, REGISTRY, REFERRAL\_NETWORK, SOCIAL, COMMUNITY, ADVOCACY, OTHER.  
* **eligibilityConfirmationDate** (date): Eligibility confirmed.  
* **screeningFailureReason** (string, optional): Reason if screen-failed.  
* **withdrawalDate** (date, optional): Withdrawal date.  
* **withdrawalReason** (string, optional): Reason.  
* **protocolVersionAtEnrollment** (string): Protocol version active at enrollment.  
* **investigatorSignatureDate** (date): PI signature date.  
* **enrollmentVerificationStatus** (enum): PENDING, VERIFIED, DISPUTED.  
* **stratificationFactors** (object): Stratification key-values.  
* **firstDoseDate** (date, optional): First dose.  
* **lastDoseDate** (date, optional): Last dose.  
* **treatmentArmAssignment** (string, optional): Arm id.  
* **enrollmentInCompetingStudyStatus** (enum): NONE, DISCLOSED, BLOCKED.  
* **priorStudyParticipationStatus** (enum): NAIVE, PRIOR\_PARTICIPANT.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **eligibilityConfirmedBy** (string): Confirming PI or coordinator.  
* **enrollmentVerifiedBy** (string): Verifier.  
* **enrollmentVerificationDate** (date): Verification date.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (1); Site.  
* **for**: Participant (1); Participant.  
* **records**: Informed Consent (1); Consent.  
* **assesses**: Inclusion Criteria (1..N); Inclusion assessments.  
* **assesses**: Exclusion Criteria (1..N); Exclusion assessments.  
* **observedAt**: Visit (1); Enrollment visit.  
* **hasCRFs**: CRF (1..N); Enrollment CRFs.  
* **raises**: Discrepancy (Query) (0..N); Queries.  
* **records**: Deviation (0..N); Deviations.  
* **hasDocuments**: Document (1..N); Source docs.  
* **hasLabResults**: Lab Results (0..N); Eligibility labs.  
* **hasTasks**: Task (0..N); Tasks.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Open Enrollment** (PM): Open enrollment for the site.  
* **Enroll Participant** (Coordinator): Create enrollment event.  
* **Update Enrollment Status** (Coordinator): Status updates.  
* **Close Enrollment** (PM): Close enrollment site or study-wide.

## **21\. Payment**

A Payment records a financial transaction associated with the trial, such as site invoices, investigator fees, or participant reimbursements.  
***Editor note.** v0.2: added complianceCheckStatus aligned with anti-kickback rules and Sunshine Act reporting.*

### **Attributes**

* **paymentId** (string, unique): Identifier.  
* **paymentAmount** (money): Amount.  
* **paymentCurrency** (enum, ISO 4217): Currency.  
* **exchangeRate** (number, optional): Exchange rate.  
* **paymentDate** (date): Payment date.  
* **paymentStatus** (enum): PENDING, APPROVED, PROCESSED, COMPLETED, CANCELED.  
* **paymentType** (enum): SITE\_PAYMENT, INVESTIGATOR\_FEE, PARTICIPANT\_REIMBURSEMENT, VENDOR\_PAYMENT.  
* **paymentReason** (enum): VISIT\_COMPLETION, PROCEDURE, TRAVEL, MILESTONE, OTHER.  
* **paymentMethod** (enum): BANK\_TRANSFER, CHECK, CASH, CARD.  
* **paymentCategory** (enum): STARTUP, ONGOING, CLOSEOUT.  
* **paymentFrequency** (enum): ONE\_TIME, MONTHLY, QUARTERLY.  
* **paymentNotes** (string): Notes.  
* **invoiceNumber** (string, optional): Invoice number.  
* **invoiceDate** (date, optional): Invoice date.  
* **payer** (string): Paying entity.  
* **payee** (string): Receiving entity.  
* **taxInformation** (object): Tax id, VAT, withholding.  
* **withholdingTaxAmount** (money, optional): Withholding amount.  
* **paymentVerificationStatus** (enum): PENDING, VERIFIED, REJECTED.  
* **complianceCheckStatus** (enum): PENDING, PASSED, FAILED.

### **Metadata**

* **createdBy** (string): Creator.  
* **createdDate** (datetime): Created.  
* **lastModifiedBy** (string): Modifier.  
* **lastModifiedDate** (datetime): Modified.  
* **approvalStatus** (enum): PENDING, APPROVED, REJECTED.  
* **approvedBy** (string): Approver.  
* **approvalDate** (date): Approval date.  
* **paymentVerifiedBy** (string): Verifier.  
* **paymentVerificationDate** (date): Verification date.

### **Relationships**

* **partOf**: Study (1); Study.  
* **scopedTo**: Site (0..1); Site (if site payment).  
* **for**: Participant (0..1); Participant (if reimbursement).  
* **relatesTo**: Visit (0..1); Visit-based payment.  
* **relatesTo**: Procedure (0..1); Procedure-based payment.  
* **relatesTo**: Contract (0..1); Contract.  
* **relatesTo**: Budget Line Item (0..1); Budget line.  
* **hasDocuments**: Document (0..N); Receipts, invoices.  
* **relatesTo**: Task (0..1); Processing task.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Payment** (Finance): Create.  
* **Approve Payment** (Finance Manager): Approve.  
* **Process Payment** (Finance): Process via payment method.  
* **Cancel Payment** (Finance): Cancel.  
* **Record Payment Receipt** (Site): Record receipt.

## **22\. Protocol**

A Protocol is the detailed plan for conducting a clinical trial. It defines objectives, design, methodology, statistics, and organization. Protocol is the canonical anchor for many objects (Visits, Endpoints, Eligibility Criteria, IP, SOA).  
***Editor note.** v0.2: added ddfJsonDocumentId reference for USDM-aligned Digital Definition Format; clarified that Protocol holds version, while Amendment captures changes.*

### **Attributes**

* **protocolId** (string, unique): Identifier.  
* **protocolNumber** (string): Sponsor protocol number.  
* **protocolTitle** (string): Title.  
* **protocolVersion** (string): Version.  
* **protocolStatus** (enum): DRAFT, APPROVED, AMENDED, RETIRED.  
* **therapeuticArea** (enum): ONCOLOGY, CARDIOLOGY, NEUROLOGY, IMMUNOLOGY, INFECTIOUS\_DISEASE, OTHER.  
* **studyPhase** (enum): PHASE1, PHASE2, PHASE3, PHASE4.  
* **studyDesign** (enum): PARALLEL, CROSSOVER, FACTORIAL, ADAPTIVE, SINGLE\_GROUP.  
* **sampleSize** (integer): Planned sample size.  
* **studyDuration** (duration): Overall planned duration.  
* **randomizationMethod** (enum): NONE, SIMPLE, BLOCK, STRATIFIED, ADAPTIVE.  
* **blindingType** (enum): OPEN\_LABEL, SINGLE\_BLIND, DOUBLE\_BLIND, TRIPLE\_BLIND.  
* **primaryEndpoint** (string): Primary endpoint description.  
* **secondaryEndpoints** (array\<string\>): Secondary endpoints.  
* **creationDate** (date): Created.  
* **approvalDate** (date): Approved.  
* **effectiveDate** (date): Effective.  
* **expirationDate** (date, optional): Expiration.  
* **primaryProtocolDocumentId** (string): Reference to PDF protocol.  
* **ddfJsonDocumentId** (string, optional): USDM Digital Definition Format JSON document.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **partOf**: Study (1); Owning study.  
* **hasPI**: Person (1); Principal Investigator.  
* **authoredBy**: Person (1..N); Authors.  
* **reviewedBy**: Person (1..N); Reviewers.  
* **hasObjectives**: Objective (1..N); Objectives; flagged as missing object below.  
* **hasEndpoints**: Endpoint (1..N); Endpoints.  
* **definesInclusion**: Inclusion Criteria (1..N); Inclusion criteria.  
* **definesExclusion**: Exclusion Criteria (1..N); Exclusion criteria.  
* **definesVisits**: Visit (1..N); Planned visits.  
* **definesArms**: Arm (1..N); Treatment arms.  
* **definesIP**: Investigational Product (1..N); IP definitions.  
* **hasSafetyMonitoringPlan**: Plan (1); Safety plan.  
* **hasStatisticalAnalysisPlan**: Plan (1); SAP.  
* **hasAmendments**: Amendment (0..N); Amendments.  
* **hasTasks**: Task (0..N); Tasks.  
* **hasSOPs**: SOP (0..N); SOPs.  
* **triggers**: Regulatory Submission (0..N); Submissions.  
* **hasMilestones**: Milestone (0..N); Milestones.  
* **definesCRFs**: CRF (0..N); CRFs.  
* **administersInstruments**: Questionnaire (0..N); Instruments.  
* **orders**: Lab Test (0..N); Lab tests.  
* **definesProcedures**: Procedure (0..N); Procedures.  
* **anticipates**: Adverse Event Type (0..N); Expected AE types.  
* **allows**: Deviation Type (0..N); Allowed deviation types.  
* **budgetedBy**: Budget (1); Budget.  
* **approvedSites**: Site (0..N); Approved sites.  
* **requires**: Equipment (0..N); Required equipment.  
* **collects**: Sample (0..N); Sample types.  
* **definesDataTransfer**: Data Transfer Specification (0..N); Transfer specs.  
* **producesReports**: Report (0..N); Report types.  
* **hasMonitoringPlan**: Plan (1); Monitoring plan.  
* **assessedBy**: Risk Assessment (0..N); Risk assessments.  
* **requiresTraining**: Training Requirement (1..N); Training requirements.  
* **definesConsentVersions**: Informed Consent (1..N); Consent versions.  
* **definesSOA**: Schedule of Assessments (1..N); SOAs.  
* **overseenBy**: Oversight Body (1..N); IRB / EC, DSMB.  
* **hasPublicationPlan**: Publication Plan (1..N); Publication plans.

### **Calls to Action**

* **Create Protocol** (Sponsor Medical): Draft a new protocol.  
* **Update Protocol** (Sponsor Medical): Edit.  
* **Submit Protocol for Review** (Regulatory): Submit for approval.  
* **Approve or Reject Protocol** (Sponsor Exec): Approve or reject.  
* **Amend Protocol** (Sponsor Medical): File an amendment.  
* **Project to USDM Study Design** (Visual Explorer): Render as USDM Study Design.  
* **Export DDF JSON** (Sponsor Medical): Export USDM-aligned JSON.

## **23\. Investigational Product**

An Investigational Product (IP) is the drug or biologic under investigation. IP is central to study supply, accountability, blinding, and safety.  
***Editor note.** v0.2: separated batchNumber and lotNumber as distinct attributes; explicit blinding and control type vocabularies retained.*

### **Attributes**

* **productId** (string, unique): Identifier.  
* **productName** (string): Name.  
* **productType** (enum): DRUG, BIOLOGIC, CELL\_THERAPY, GENE\_THERAPY, RADIOLIGAND.  
* **productDescription** (string): Description.  
* **manufacturerId** (string): Manufacturer reference.  
* **batchNumber** (string): Batch number.  
* **lotNumber** (string): Lot number.  
* **expirationDate** (date): Expiration.  
* **storageRequirements** (string): Storage requirements.  
* **dosingInstructions** (string): Dosing.  
* **formulation** (string): Formulation.  
* **strength** (string): Strength.  
* **route** (enum): ORAL, INTRAVENOUS, SUBCUTANEOUS, INTRAMUSCULAR, TOPICAL, INHALED, OTHER.  
* **packaging** (string): Packaging.  
* **blindingStatus** (enum): OPEN\_LABEL, BLINDED.  
* **controlType** (enum): PLACEBO, ACTIVE, NONE.  
* **accountabilityRequired** (boolean): Accountability required.  
* **returnRequired** (boolean): Return required.  
* **destructionRequired** (boolean): Destruction required.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **usedIn**: Study (1..N); Studies.  
* **definedBy**: Protocol (1..N); Protocols.  
* **suppliedTo**: Site (1..N); Sites.  
* **administeredTo**: Participant (1..N); Participants.  
* **administeredAt**: Visit (1..N); Visits.  
* **shippedVia**: Shipment (1..N); Shipments.  
* **storedAt**: Storage Location (1..N); Storage locations; flagged as missing object below.  
* **hasDocuments**: Document (1..N); IB, package insert.  
* **causes**: Adverse Event (0..N); AEs.  
* **causes**: Serious Adverse Event (0..N); SAEs.  
* **relatesTo**: Deviation (0..N); Deviations.  
* **relatesTo**: Task (0..N); Tasks.  
* **hasBatches**: Batch (1..N); Batches.  
* **hasDosageForms**: Dosage Form (1..N); Dosage forms.  
* **handledAt**: Pharmacy (1..N); Pharmacy locations.  
* **inventoriedBy**: Inventory Record (1..N); Inventory records.  
* **monitoredBy**: Temperature Log (1..N); Temperature logs.  
* **accountabilityLog**: Accountability Log (1..N); Accountability logs.  
* **returnRecord**: Return/Destruction Record (1..N); Returns and destructions.  
* **mappedTo**: Randomization Code (1..N); Randomization codes.  
* **unblindRecord**: Unblinding Record (0..N); Unblindings.  
* **hasManufacturingRecord**: Manufacturing Record (1..N); Mfg records.  
* **testedBy**: Quality Control Test (1..N); QC tests.  
* **referencedIn**: Regulatory Submission (1..N); Submissions.  
* **producesReports**: Safety Report (1..N); Safety reports; flagged as missing object below.  
* **hasInteractions**: Drug Interaction (0..N); Drug interactions; flagged as missing object below.  
* **restrictsConmeds**: Concomitant Medication (0..N); Restricted conmeds.  
* **monitoredVia**: Lab Test (0..N); Monitoring labs.  
* **administeredBy**: Procedure (1..N); Procedures.  
* **handledWith**: Equipment (1..N); Equipment.  
* **requires**: Training Record (1..N); Trainings.  
* **monitoredVia**: Monitoring Visit (1..N); Monitoring visits.  
* **raises**: Discrepancy (Query) (0..N); Queries.  
* **recordedOn**: CRF (1..N); CRFs.  
* **hasMilestones**: Milestone (0..N); Milestones.  
* **assessedBy**: Risk Assessment (0..N); Risk assessments.  
* **triggers**: CAPA (0..N); CAPAs.

### **Calls to Action**

* **Create Investigational Product** (Sponsor Supply): Define a new IP.  
* **Update Product Details** (Sponsor Supply): Edit.  
* **Assign Product to Study** (Sponsor Supply): Allocate to a study.  
* **Track Product Inventory** (Pharmacy): View site inventory.  
* **Record Product Dispensation** (Pharmacy): Dispense to participant.  
* **Record Product Return** (Pharmacy): Return or destroy.  
* **Project to USDM StudyIntervention** (Visual Explorer): Render as USDM StudyIntervention.  
* **Project to FHIR MedicationAdministration** (Visual Explorer): Render administrations.

## **24\. Investigational Device**

An Investigational Device is a medical device under investigation, including implantable, wearable, disposable, and diagnostic devices.  
***Editor note.** v0.2: this object exists in v0 (relationships \#25; attributes \#23 in PDF) but is missing from the master Object List index; flagged for inclusion. Added udi (Unique Device Identifier).*

### **Attributes**

* **deviceId** (string, unique): Identifier.  
* **deviceName** (string): Name.  
* **deviceType** (enum): IMPLANTABLE, WEARABLE, DISPOSABLE, DIAGNOSTIC.  
* **deviceDescription** (string): Description.  
* **manufacturerId** (string): Manufacturer.  
* **udi** (string): Unique Device Identifier (FDA UDI).  
* **modelNumber** (string): Model.  
* **serialNumber** (string): Serial.  
* **lotNumber** (string): Lot.  
* **expirationDate** (date): Expiration.  
* **macAddress** (string, optional): MAC address (connected devices).  
* **firmwareVersion** (string, optional): Firmware.  
* **softwareVersion** (string, optional): Software.  
* **storageRequirements** (string): Storage.  
* **usageInstructions** (string): Usage.  
* **sterilizationStatus** (enum): NOT\_REQUIRED, STERILE, UNSTERILE.  
* **reuseStatus** (enum): SINGLE\_USE, REUSABLE.  
* **calibrationRequired** (boolean): Calibration required.  
* **calibrationFrequency** (duration, optional): Frequency.  
* **lastCalibrationDate** (date, optional): Last calibration.  
* **batteryType** (string, optional): Battery type.  
* **batteryLife** (duration, optional): Battery life.  
* **chargingInstructions** (string, optional): Charging.  
* **waterResistanceRating** (string, optional): IP rating.  
* **mriCompatibility** (enum, optional): MRI\_SAFE, MRI\_CONDITIONAL, MRI\_UNSAFE.  
* **disposalInstructions** (string): Disposal.  
* **regulatoryClassification** (string): Class I, II, III; CE class.  
* **certifications** (array\<string\>): Certifications.  
* **accountabilityRequired** (boolean): Accountability required.  
* **returnRequired** (boolean): Return required.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **usedIn**: Study (1..N); Studies.  
* **suppliedTo**: Site (1..N); Sites.  
* **manufacturedBy**: Organization (1); Manufacturer.  
* **administeredTo**: Participant (1..N); Participants.  
* **usedAt**: Visit (1..N); Visits.  
* **shippedVia**: Shipment (1..N); Shipments.  
* **storedAt**: Storage Location (1..N); Storage.  
* **hasDocuments**: Document (1..N); Manuals, specs.  
* **causes**: Adverse Event (0..N); AEs.  
* **relatesTo**: Deviation (0..N); Deviations.  
* **relatesTo**: Task (0..N); Tasks.  
* **requires**: Training Record (1..N); Trainings.  
* **hasMaintenanceRecord**: Maintenance Record (1..N); Maintenance.  
* **hasCalibrationRecord**: Calibration Record (1..N); Calibrations.  
* **testedBy**: Quality Control Check (1..N); QC checks.  
* **emits**: Data Transfer (1..N); Device data transfers.  
* **referencedIn**: Regulatory Submission (1..N); Submissions.  
* **producesReports**: Safety Report (1..N); Safety reports.  
* **inventoriedBy**: Inventory Record (1..N); Inventory.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Register Device** (Sponsor Supply): Register a new device.  
* **Calibrate Device** (Site): Run calibration.  
* **Dispense Device** (Site): Dispense to participant.  
* **Return Device** (Site): Process return.  
* **Pull Device Data** (Data Engineering): Trigger data transfer.  
* **Project to FHIR Device** (Visual Explorer): Render as FHIR Device.

## **25\. Plan**

A Plan represents one of several formal plans used in trials: monitoring plan, data management plan, statistical analysis plan, risk management plan, communication plan, and others.  
***Editor note.** v0.2: planType vocabulary expanded; planVersion lifecycle aligns with Document.*

### **Attributes**

* **planId** (string, unique): Identifier.  
* **planType** (enum): MONITORING, DATA\_MANAGEMENT, STATISTICAL\_ANALYSIS, RISK\_MANAGEMENT, SAFETY, COMMUNICATION, PUBLICATION, ARCHIVING.  
* **planTitle** (string): Title.  
* **planVersion** (string): Version.  
* **planStatus** (enum): DRAFT, IN\_REVIEW, APPROVED, EFFECTIVE, RETIRED.  
* **creationDate** (date): Created.  
* **approvalDate** (date): Approved.  
* **effectiveDate** (date): Effective.  
* **expirationDate** (date, optional): Expiration.  
* **description** (string): Description.  
* **keywords** (array\<string\>): Keywords.

### **Metadata**

* **authorId** (string): Author.  
* **reviewerId** (string): Reviewer.  
* **approverId** (string): Approver.  
* **lastModifiedDate** (datetime): Modified.  
* **lastModifiedBy** (string): Modifier.

### **Relationships**

* **partOf**: Study (1); Study.  
* **governedBy**: Protocol (1); Protocol.  
* **hasDocuments**: Document (1..N); Plan documents.  
* **authoredBy**: Person (1..N); People involved.  
* **hasTasks**: Task (0..N); Tasks.  
* **hasMilestones**: Milestone (0..N); Milestones.  
* **scopedTo**: Visit (0..N); Visit scope.  
* **scopedTo**: Site (0..N); Site scope.  
* **relatesTo**: CRF (0..N); CRFs.  
* **relatesTo**: Procedure (0..N); Procedures.  
* **relatesTo**: Lab Test (0..N); Lab tests.  
* **relatesTo**: Adverse Event Type (0..N); AE types.  
* **relatesTo**: Deviation Type (0..N); Deviation types.  
* **guidedBy**: Risk Assessment (0..N); Risk assessments.  
* **governs**: Monitoring Visit (0..N); Monitoring visits.  
* **governs**: Audit (0..N); Audits.  
* **producesReports**: Report (0..N); Reports.  
* **relatesTo**: Data Transfer (0..N); Data transfers.  
* **relatesTo**: Statistical Analysis (0..N); Statistical analyses.  
* **relatesTo**: Quality Control Check (0..N); QC checks.  
* **requiresTraining**: Training Requirement (0..N); Training requirements.  
* **relatesTo**: Oversight Body (0..N); Oversight bodies.  
* **relatesTo**: Regulatory Submission (0..N); Submissions.  
* **relatesTo**: Budget Item (0..N); Budget items.  
* **relatesTo**: Investigational Product (0..N); IP.  
* **relatesTo**: Sample (0..N); Sample types.  
* **relatesTo**: Equipment (0..N); Equipment.  
* **relatesTo**: System (0..N); Systems.  
* **relatesTo**: Service (0..N); Services.  
* **triggers**: CAPA (0..N); CAPAs.  
* **amendedBy**: Amendment (0..N); Amendments.  
* **relatesTo**: SOP (0..N); SOPs.  
* **administersInstruments**: Questionnaire (0..N); Instruments.  
* **relatesTo**: Endpoint (0..N); Endpoints.  
* **relatesTo**: Data Management Rule (0..N); Data rules.  
* **relatesTo**: Publication Plan (0..N); Publication plans.  
* **hasArchivingStrategy**: Archiving Strategy (0..N); Archiving.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Plan** (Sponsor): Create.  
* **Update Plan** (Sponsor): Edit.  
* **Approve Plan** (Approver): Approve.  
* **Implement Plan** (Operations): Roll out.  
* **Review Plan Progress** (PM): Periodic review.

## **26\. Oversight Body**

An Oversight Body is a committee or group responsible for monitoring trial conduct: IRBs, ECs, DSMBs, IDMCs, Steering Committees. Oversight Bodies make safety, data, and ethics decisions.  
***Editor note.** v0.2: added centralVsLocal flag (centralized IRB vs. local IRB) and meetingCadence as RRULE.*

### **Attributes**

* **oversightBodyId** (string, unique): Identifier.  
* **bodyName** (string): Name.  
* **bodyType** (enum): IRB, EC, DSMB, IDMC, SAFETY\_REVIEW, STEERING\_COMMITTEE.  
* **centralVsLocal** (enum): CENTRAL, LOCAL.  
* **description** (string): Description.  
* **contactPerson** (string): Contact.  
* **contactEmail** (string): Email.  
* **contactPhone** (string): Phone.  
* **address** (object): Address.  
* **country** (enum): Country.  
* **approvalStatus** (enum): PENDING, APPROVED, CONDITIONAL, REJECTED.  
* **approvalDate** (date, optional): Approval date.  
* **nextReviewDate** (date, optional): Next review.  
* **meetingFrequency** (string, RRULE): Meeting cadence.  
* **lastMeetingDate** (date): Last meeting.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **oversees**: Study (1..N); Studies overseen.  
* **reviews**: Protocol (1..N); Protocols.  
* **hasMembers**: Person (1..N); Members.  
* **hasChair**: Person (1); Chairperson.  
* **hasDocuments**: Document (1..N); Charters, minutes, reports.  
* **holds**: Meeting (1..N); Meetings; flagged as missing object below.  
* **conducts**: Review (1..N); Reviews; flagged as missing object below.  
* **issues**: Recommendation (1..N); Recommendations; flagged as missing object below.  
* **issues**: Decision (1..N); Decisions; flagged as missing object below.  
* **reviews**: Adverse Event (0..N); AEs reviewed.  
* **reviews**: Serious Adverse Event (0..N); SAEs reviewed.  
* **reviews**: Safety Report (0..N); Safety reports.  
* **conducts**: Interim Analysis (0..N); Interim analyses.  
* **reviews**: Amendment (0..N); Amendments.  
* **reviews**: Informed Consent (0..N); Consent versions.  
* **hasTasks**: Task (0..N); Tasks.  
* **hasMilestones**: Milestone (0..N); Milestones.  
* **reviews**: Deviation (0..N); Deviations.  
* **reviews**: Data Transfer (0..N); Data transfers.  
* **producesReports**: Report (0..N); Reports.  
* **hasNotificationRules**: Notification Rule (0..N); Notifications.  
* **hasCommunicationLog**: Communication Log (0..N); Comms; flagged as missing object below.  
* **hasTrainingRecords**: Training Record (0..N); Trainings.  
* **discloses**: Conflict of Interest Disclosure (0..N); COI.  
* **relatesTo**: Regulatory Submission (0..N); Submissions.  
* **conducts**: Visit (0..N); On-site reviews.  
* **raises**: Discrepancy (Query) (0..N); Queries from reviews.  
* **recommends**: CAPA (0..N); CAPAs.  
* **conducts**: Risk Assessment (0..N); Risk assessments.  
* **audits**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Oversight Body** (Sponsor Regulatory): Register a new body.  
* **Update Oversight Body Details** (Sponsor Regulatory): Edit.  
* **Schedule Oversight Meeting** (Body Coordinator): Schedule.  
* **Record Meeting Minutes** (Body Coordinator): Capture minutes.  
* **Issue Recommendations** (Body Chair): Publish recommendations.

## **27\. System**

A software platform used in trial conduct (EDC, eTMF, IRT, eCOA, CTMS, eRegulatory, ePRO, central lab system).  
***Editor note.** v0.2: added explicit relationships to Service, System Configuration, and Integration Profile; added technology metadata for vendor and version; clarified that System is the platform and Service is the offering on top of it.*

### **Attributes**

* **systemId** (string, IRI): Unique identifier.  
* **systemName** (string): Display name.  
* **systemType** (enum): edc, etmf, ctms, irt, ecoa, eregulatory, esource, central\_lab, imaging, safety, other.  
* **vendor** (string): Vendor.  
* **productName** (string): Product.  
* **version** (string, semver): Version.  
* **environment** (enum): development, validation, production.  
* **validationStatus** (enum): unvalidated, validated, requalification\_due.  
* **validationDate** (date, optional): Last validation date.  
* **ownerOrganizationId** (string, IRI): Owning organization.  
* **supportContact** (string): Support email or phone.  
* **url** (string, URL): Access URL.  
* **ssoEnabled** (boolean): SSO support.  
* **part11Compliant** (boolean): 21 CFR Part 11 compliance.  
* **gdprAdequate** (boolean): GDPR adequacy.  
* **retiredAt** (date, optional): Retirement date.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **hasConfigurations**: System Configuration (0..N); Per study or per site configurations.  
* **provides**: Service (0..N); Services offered.  
* **hostedBy**: Sponsor (0..1); Hosting org.  
* **integratesWith**: System (0..N); Other systems.  
* **hasIntegrationProfiles**: Integration Profile (0..N); Profiles; flagged as missing object below.  
* **hasUserRoles**: User Role (0..N); Roles defined.  
* **hasCredentials**: Credential (0..N); Credentials.  
* **storesData**: CRF (0..N); CRFs.  
* **storesData**: Document (0..N); Documents.  
* **emitsEvents**: Audit Trail Entry (1..N); Audit trail.  
* **producesReports**: Report (0..N); Reports.  
* **supports**: Study (0..N); Studies supported.  
* **operatedAt**: Site (0..N); Sites where used.  
* **hasDataTransfers**: Data Transfer (0..N); Outbound or inbound transfers.  
* **hasShipments**: Shipment (0..N); Shipment records (for IRT).

### **Calls to Action**

* **Register System** (System Owner): Add a new platform.  
* **Update System Details** (System Owner): Edit.  
* **Validate System** (Quality): Initiate validation cycle.  
* **Retire System** (System Owner): Decommission.  
* **Configure System for Study** (Study Manager): Open System Configuration.

## **28\. System Configuration**

A study-specific or site-specific configuration of a System (parameter set, library, build).  
***Editor note.** v0.2: clarified that one System has many Configurations; added validationStatus to track UAT versus production cutover.*

### **Attributes**

* **systemConfigurationId** (string, IRI): Unique identifier.  
* **configurationName** (string): Name (e.g., StudyXYZ\_v2\_PROD).  
* **systemId** (string, IRI): Parent system.  
* **scope** (enum): study, site, sponsor, global.  
* **scopeRefId** (string, IRI, optional): Reference id of scope target.  
* **version** (string, semver): Configuration version.  
* **environment** (enum): dev, val, prod.  
* **validationStatus** (enum): draft, in\_uat, validated, deployed, retired.  
* **effectiveStart** (date): Effective start.  
* **effectiveEnd** (date, optional): Effective end.  
* **changeReason** (string): Reason for change.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **approvedBy** (PersonRef): Approver.

### **Relationships**

* **configures**: System (1); Parent system.  
* **scopedTo**: Study (0..1); Study scope.  
* **scopedTo**: Site (0..1); Site scope.  
* **referencesCRFs**: CRF (0..N); CRF library.  
* **referencesScheduleOfAssessments**: Schedule of Assessments (0..1); SOA build.  
* **referencesEdits**: Edit Check (0..N); Edit check library; flagged as missing object below.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.  
* **hasUserRoleAssignments**: User Role (0..N); Role assignments.  
* **hasAmendments**: Amendment (0..N); Triggered by amendment.

### **Calls to Action**

* **Create Configuration** (Study Build Lead): New configuration.  
* **Promote to UAT** (Study Build Lead): Move to UAT.  
* **Promote to Production** (Quality): Cutover.  
* **Retire Configuration** (Study Build Lead): Retire.

## **29\. Service**

A discrete service offering (data management, monitoring, statistics, central reading, central lab analysis, IRT randomization, eConsent hosting).  
***Editor note.** v0.2: separated Service from System (a Service can be performed by a System or by a vendor team without a System); added providerOrganization and SLA terms.*

### **Attributes**

* **serviceId** (string, IRI): Unique identifier.  
* **serviceName** (string): Service name.  
* **serviceType** (enum): data\_management, monitoring, statistics, central\_lab, central\_reading, irt, econsent, ecoa, etmf, safety\_processing, regulatory, translation, other.  
* **providerOrganizationId** (string, IRI): Vendor or sponsor function.  
* **systemId** (string, IRI, optional): System used to deliver, if any.  
* **slaResponseHours** (integer, optional): Response SLA.  
* **slaResolutionHours** (integer, optional): Resolution SLA.  
* **costModel** (enum): fixed\_fee, time\_and\_materials, per\_subject, per\_site, hybrid.  
* **serviceStatus** (enum): planned, active, suspended, completed.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **providedBy**: Sponsor (1); Vendor or function.  
* **deliveredVia**: System (0..1); System.  
* **hasConfigurations**: Service Configuration (0..N); Service configs.  
* **servesStudy**: Study (0..N); Studies.  
* **servesSite**: Site (0..N); Sites.  
* **governedBy**: Contract (1..N); Contracts.  
* **hasReports**: Report (0..N); Service reports.  
* **hasTasks**: Task (0..N); Service tasks.  
* **hasMilestones**: Milestone (0..N); Service milestones.  
* **hasIssues**: Action Item (0..N); Service action items.

### **Calls to Action**

* **Onboard Service** (Vendor Manager): Set up.  
* **Update Service Terms** (Vendor Manager): Edit.  
* **Suspend Service** (Vendor Manager): Suspend.  
* **Close Out Service** (Vendor Manager): Close.

## **30\. Service Configuration**

Study-specific or site-specific parameters for a Service (rate cards, scope, frequencies, sample handling instructions).  
***Editor note.** v0.2: introduced as a sibling of System Configuration to capture per-study scope of a vendor service.*

### **Attributes**

* **serviceConfigurationId** (string, IRI): Unique identifier.  
* **serviceId** (string, IRI): Parent service.  
* **scope** (enum): study, site, region, global.  
* **scopeRefId** (string, IRI, optional): Reference id of scope target.  
* **effectiveStart** (date): Effective start.  
* **effectiveEnd** (date, optional): Effective end.  
* **monitoringStrategy** (enum, optional): on\_site, remote, central, hybrid.  
* **frequency** (string, RRULE, optional): Cadence.  
* **rateCardId** (string, IRI, optional): Rate card.  
* **notes** (string, optional): Notes.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **configures**: Service (1); Parent service.  
* **scopedTo**: Study (0..1); Study.  
* **scopedTo**: Site (0..1); Site.  
* **governedBy**: Contract (0..1); Contract.  
* **referencesScheduleOfAssessments**: Schedule of Assessments (0..1); SOA reference.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Service Configuration** (Vendor Manager): New config.  
* **Activate Service Configuration** (Vendor Manager): Activate.  
* **Retire Service Configuration** (Vendor Manager): Retire.

## **31\. Study Startup Package**

A bundle of artifacts and tasks required to activate a Site for a Study (regulatory, contracts, training, supplies, IT setup).  
***Editor note.** v0.2: added explicit checklists for Regulatory, Contract, Training, Supplies, IT; added cycle time metrics.*

### **Attributes**

* **studyStartupPackageId** (string, IRI): Unique identifier.  
* **studyId** (string, IRI): Parent study.  
* **siteId** (string, IRI): Site being activated.  
* **packageStatus** (enum): planned, in\_progress, ready\_for\_activation, activated, on\_hold, terminated.  
* **plannedStartDate** (date): Planned start.  
* **plannedActivationDate** (date): Planned activation.  
* **actualActivationDate** (date, optional): Actual activation.  
* **cycleTimeDays** (integer, computed): Days from start to activation.  
* **regulatoryStatus** (enum): not\_started, in\_review, approved, conditional, rejected.  
* **contractStatus** (enum): not\_started, drafted, negotiating, executed.  
* **trainingStatus** (enum): not\_started, in\_progress, complete.  
* **suppliesStatus** (enum): not\_started, ordered, received, deficient.  
* **itSetupStatus** (enum): not\_started, in\_progress, complete.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **ownedBy** (PersonRef): Startup specialist.

### **Relationships**

* **activatesSite**: Site (1); Target site.  
* **forStudy**: Study (1); Parent study.  
* **hasTasks**: Task (1..N); Startup tasks.  
* **hasMilestones**: Milestone (1..N); Startup milestones (e.g., FPI ready).  
* **hasDocuments**: Document (1..N); Regulatory binder contents.  
* **hasContracts**: Contract (1..N); CTA, MSA, budgets.  
* **hasBudgets**: Budget (1); Site budget.  
* **hasTrainingRecords**: Training Record (1..N); Site staff trainings.  
* **hasShipments**: Shipment (0..N); Initial supplies.  
* **hasRegulatorySubmissions**: Regulatory Submission (0..N); Submissions.  
* **hasCredentials**: Credential (0..N); System logins.  
* **hasActionItems**: Action Item (0..N); Open items.  
* **hasRiskAssessment**: Risk Assessment (0..1); Site risk; flagged as missing object below.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Initiate Site Startup** (Site Activation Manager): Open package.  
* **Mark Component Complete** (Site Activation Manager): Update component status.  
* **Activate Site** (Site Activation Manager): Final activation.  
* **Place Site On Hold** (Site Activation Manager): Hold.  
* **Terminate Startup** (Sponsor Operations): Terminate.

## **32\. Budget**

A planned and tracked financial allocation for a Study, Site, or Service.  
***Editor note.** v0.2: separated planned from forecasted; added per-visit and per-procedure rate items; relationship to Payment for actual disbursement; relationship to Coverage Analysis flagged as missing.*

### **Attributes**

* **budgetId** (string, IRI): Unique identifier.  
* **budgetName** (string): Display name.  
* **scope** (enum): study, site, service, sponsor.  
* **scopeRefId** (string, IRI): Scope reference.  
* **currency** (string, ISO 4217): Currency.  
* **plannedTotalAmount** (decimal): Planned total.  
* **forecastTotalAmount** (decimal): Forecast total.  
* **actualTotalAmount** (decimal, computed): Actual to date.  
* **varianceAmount** (decimal, computed): Variance.  
* **budgetStatus** (enum): draft, approved, locked, closed.  
* **effectiveStart** (date): Effective start.  
* **effectiveEnd** (date, optional): Effective end.  
* **indirectCostRate** (decimal): Indirect rate.  
* **holdbackPercent** (decimal): Holdback percent.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **approvedBy** (PersonRef): Approver.  
* **approvedAt** (datetime): Approval time.

### **Relationships**

* **scopedTo**: Study (0..1); Study scope.  
* **scopedTo**: Site (0..1); Site scope.  
* **scopedTo**: Service (0..1); Service scope.  
* **hasLineItems**: Budget Line Item (1..N); Line items; flagged as missing object below.  
* **hasBudgetForecast**: Budget Forecast (0..N); Forecasts; flagged as missing object below.  
* **governedBy**: Contract (0..N); Contracts.  
* **drives**: Payment (0..N); Payments triggered.  
* **hasCoverageAnalysis**: Coverage Analysis (0..1); Coverage analysis; flagged as missing object below.  
* **hasAmendments**: Amendment (0..N); Budget amendments.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Budget** (Finance): New budget.  
* **Add Line Item** (Finance): Add item.  
* **Approve Budget** (Sponsor Finance): Approve.  
* **Lock Budget** (Finance): Lock for execution.  
* **Reforecast Budget** (Finance): Update forecast.  
* **Close Budget** (Finance): Close.

## **33\. Contract**

A binding agreement between parties (CTA, MSA, work order, change order, NDA, vendor agreement).  
***Editor note.** v0.2: split contractType to enumerate cta, msa, work\_order, change\_order, nda, dpa, vendor; added executionDate and effectiveDates separately; added relationship to Budget.*

### **Attributes**

* **contractId** (string, IRI): Unique identifier.  
* **contractName** (string): Display name.  
* **contractType** (enum): cta, msa, work\_order, change\_order, nda, dpa, vendor.  
* **parties** (list\[OrganizationRef\]): Parties to contract.  
* **contractStatus** (enum): draft, in\_negotiation, executed, terminated, expired.  
* **executionDate** (date, optional): Execution.  
* **effectiveStart** (date): Effective start.  
* **effectiveEnd** (date, optional): Effective end.  
* **totalValueAmount** (decimal, optional): Total value.  
* **currency** (string, ISO 4217): Currency.  
* **paymentTermsDays** (integer): Net payment days.  
* **governingLaw** (string): Governing law.  
* **noticePeriodDays** (integer): Notice period.  
* **indemnificationTerms** (string): Indemnification.  
* **ipOwnership** (string): IP ownership.  
* **publicationRights** (string): Publication.  
* **dataPrivacyAddendum** (boolean): DPA included.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **signedBy** (list\[PersonRef\]): Signatories.  
* **signedAt** (datetime): Signature time.

### **Relationships**

* **relatesTo**: Study (0..1); Study.  
* **relatesTo**: Site (0..1); Site.  
* **relatesTo**: Sponsor (1..N); Sponsors and vendors.  
* **references**: Budget (0..1); Budget.  
* **hasDocuments**: Document (1..N); Executed copies.  
* **hasAmendments**: Amendment (0..N); Amendments.  
* **triggers**: Payment (0..N); Payments under contract.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.  
* **hasTasks**: Task (0..N); Negotiation tasks.  
* **hasMilestones**: Milestone (0..N); Milestones.

### **Calls to Action**

* **Draft Contract** (Legal): Draft.  
* **Send for Negotiation** (Legal): Send.  
* **Execute Contract** (Legal): Execute.  
* **Amend Contract** (Legal): Open amendment.  
* **Terminate Contract** (Legal): Terminate.

## **34\. Schedule of Assessments**

The matrix of Visits and the Assessments performed at each, derived from the Protocol.  
***Editor note.** v0.2: explicit relationship to Protocol; introduced Assessment as a related object (flagged missing); SOA versioning aligned with Amendment.*

### **Attributes**

* **scheduleOfAssessmentsId** (string, IRI): Unique identifier.  
* **protocolId** (string, IRI): Parent protocol.  
* **version** (string, semver): SOA version.  
* **effectiveStart** (date): Effective start.  
* **effectiveEnd** (date, optional): Effective end.  
* **epochs** (list\[string\]): Epochs (Screening, Treatment, Follow-up).  
* **assessmentMatrix** (json): Visit by assessment matrix.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **definedBy**: Protocol (1); Parent protocol.  
* **definesVisits**: Visit (1..N); Visit templates.  
* **definesAssessments**: Assessment (1..N); Assessment items; flagged as missing object below.  
* **definesEndpoints**: Endpoint (0..N); Endpoints sourced.  
* **hasAmendments**: Amendment (0..N); Amendments to SOA.  
* **drivesCRFs**: CRF (1..N); CRFs to capture.  
* **drivesQuestionnaires**: Questionnaire (0..N); PROs.  
* **drivesSamples**: Sample (0..N); Samples.  
* **drivesLabResults**: Lab Results (0..N); Labs.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create SOA** (Study Designer): Build SOA.  
* **Add Visit** (Study Designer): Add visit column.  
* **Add Assessment** (Study Designer): Add assessment row.  
* **Version SOA** (Study Designer): Increment version.  
* **Lock SOA** (Study Designer): Lock for execution.

## **35\. Endpoint**

A measurable trial outcome (primary, secondary, exploratory, safety, pharmacokinetic).  
***Editor note.** v0.2: clarified endpoint hierarchy and analysis population; added relationships to Statistical Analysis Plan (in Plan) and Interim Analysis (flagged missing).*

### **Attributes**

* **endpointId** (string, IRI): Unique identifier.  
* **endpointName** (string): Name.  
* **endpointType** (enum): primary, secondary, exploratory, safety, pk, pd, biomarker.  
* **estimand** (string): Estimand definition.  
* **unit** (string, optional): Unit of measure.  
* **analysisPopulation** (string): Analysis population.  
* **successCriterion** (string): Success criterion.  
* **timeFrame** (string): Assessment time frame.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **definedBy**: Protocol (1); Parent protocol.  
* **measuredVia**: Assessment (1..N); Source assessments; flagged as missing object below.  
* **analyzedIn**: Plan (1); Statistical Analysis Plan.  
* **analyzedIn**: Interim Analysis (0..N); Interim analyses; flagged as missing object below.  
* **reportedIn**: Report (0..N); Reports.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Define Endpoint** (Biostatistician): Define.  
* **Update Endpoint** (Biostatistician): Edit.  
* **Retire Endpoint** (Biostatistician): Retire.

## **36\. Lab Results**

Quantitative or qualitative laboratory measurements collected from a Sample for a Subject.  
***Editor note.** v0.2: separated Lab Result (one record per analyte) from Lab Order; clarified normal range, reference units; added relationship to Sample and to Lab.*

### **Attributes**

* **labResultId** (string, IRI): Unique identifier.  
* **subjectId** (string, IRI): Subject.  
* **sampleId** (string, IRI, optional): Source sample.  
* **visitId** (string, IRI): Visit context.  
* **analyteCode** (string, LOINC): Analyte code.  
* **analyteName** (string): Analyte name.  
* **value** (string): Measured value.  
* **valueNumeric** (decimal, optional): Numeric value if applicable.  
* **unit** (string, UCUM): Unit of measure.  
* **referenceRangeLow** (decimal, optional): Low bound.  
* **referenceRangeHigh** (decimal, optional): High bound.  
* **abnormalFlag** (enum, optional): L, H, LL, HH, A, none.  
* **clinicalSignificance** (enum): not\_assessed, not\_clinically\_significant, clinically\_significant.  
* **collectedAt** (datetime): Collection.  
* **receivedAt** (datetime, optional): Lab receipt.  
* **resultedAt** (datetime): Result time.  
* **method** (string, optional): Method.  
* **status** (enum): preliminary, final, corrected, cancelled.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **reviewedBy** (PersonRef): Reviewer.  
* **reviewedAt** (datetime, optional): Review time.

### **Relationships**

* **forSubject**: Participant (Subject) (1); Subject.  
* **fromSample**: Sample (0..1); Source sample.  
* **atVisit**: Visit (1); Visit.  
* **producedBy**: Service (0..1); Central or local lab service.  
* **producedBy**: System (0..1); Lab system.  
* **transmittedVia**: Data Transfer (0..N); Data transfers.  
* **triggers**: Adverse Event (0..N); May trigger AE.  
* **triggers**: Action Item (0..N); May trigger action item.  
* **linkedToCRF**: CRF (0..N); Lab CRF entry.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Receive Lab Result** (Lab Manager): Ingest result.  
* **Flag Clinically Significant** (Investigator): Flag clin-sig.  
* **Reconcile Lab** (Data Manager): Reconcile to CRF.  
* **Correct Result** (Lab Manager): Issue correction.

## **37\. Log**

A site-level log (delegation, training, screening, enrollment, temperature, drug accountability, deviation, monitoring visit log).  
***Editor note.** v0.2: enumerated logType values; clarified that Log is an aggregate; entries belong to Log Entry (flagged missing).*

### **Attributes**

* **logId** (string, IRI): Unique identifier.  
* **logName** (string): Display name.  
* **logType** (enum): delegation, training, screening, enrollment, temperature, drug\_accountability, deviation, monitoring\_visit, visitor, sample, other.  
* **siteId** (string, IRI): Site.  
* **studyId** (string, IRI, optional): Study (if scoped).  
* **logStatus** (enum): active, archived.  
* **lastEntryAt** (datetime, optional): Last entry.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **scopedToSite**: Site (1); Site.  
* **scopedToStudy**: Study (0..1); Study.  
* **hasEntries**: Log Entry (1..N); Entries; flagged as missing object below.  
* **observedBy**: Monitoring Visit (0..N); Reviewed by monitoring visit.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Log** (Coordinator): New log.  
* **Add Entry** (Coordinator): Add entry.  
* **Archive Log** (Coordinator): Archive.

## **38\. Credential**

A grant of access for a Person to a System or to a study scope; tracks expiry and revocation.  
***Editor note.** v0.2: added scope object (study, site) and tied to User Role; added expiry and last-rotated metadata.*

### **Attributes**

* **credentialId** (string, IRI): Unique identifier.  
* **personId** (string, IRI): Holder.  
* **systemId** (string, IRI): System.  
* **userRoleId** (string, IRI): Role granted.  
* **scope** (enum): study, site, sponsor, global.  
* **scopeRefId** (string, IRI, optional): Scope reference.  
* **credentialType** (enum): username\_password, sso, api\_key, certificate.  
* **issuedAt** (date): Issue date.  
* **expiresAt** (date, optional): Expiry.  
* **revokedAt** (date, optional): Revocation.  
* **lastRotatedAt** (date, optional): Last rotation.  
* **mfaEnabled** (boolean): MFA flag.  
* **credentialStatus** (enum): active, expired, revoked, suspended.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **heldBy**: Person (1); Holder.  
* **grantsAccessTo**: System (1); System.  
* **confersRole**: User Role (1); Role.  
* **scopedTo**: Study (0..1); Study scope.  
* **scopedTo**: Site (0..1); Site scope.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Issue Credential** (System Administrator): Issue.  
* **Rotate Credential** (System Administrator): Rotate.  
* **Revoke Credential** (System Administrator): Revoke.  
* **Renew Credential** (System Administrator): Renew.

## **39\. Amendment**

A formal change to a Protocol, Contract, Budget, Schedule of Assessments, Informed Consent, or Plan.  
***Editor note.** v0.2: generalized Amendment to span multiple parent object types (was protocol-only in v0); added impactAssessment and triggersReconsent flags.*

### **Attributes**

* **amendmentId** (string, IRI): Unique identifier.  
* **amendmentName** (string): Display name.  
* **parentObjectType** (enum): protocol, contract, budget, schedule\_of\_assessments, informed\_consent, plan.  
* **parentObjectId** (string, IRI): Parent reference.  
* **version** (string, semver): Resulting version.  
* **amendmentType** (enum): substantial, non\_substantial, administrative.  
* **rationale** (string): Rationale.  
* **summaryOfChanges** (string): Summary.  
* **impactAssessment** (string): Impact assessment.  
* **triggersReconsent** (boolean): Reconsent required.  
* **triggersResubmission** (boolean): Regulatory resubmission required.  
* **effectiveDate** (date, optional): Effective date.  
* **amendmentStatus** (enum): draft, in\_review, approved, implemented, withdrawn.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **approvedBy** (PersonRef): Approver.  
* **approvedAt** (datetime, optional): Approval time.

### **Relationships**

* **amends**: Protocol (0..1); Parent protocol.  
* **amends**: Contract (0..1); Parent contract.  
* **amends**: Budget (0..1); Parent budget.  
* **amends**: Schedule of Assessments (0..1); Parent SOA.  
* **amends**: Informed Consent (0..1); Parent consent.  
* **amends**: Plan (0..1); Parent plan.  
* **triggersReconsentOf**: Participant (Subject) (0..N); Subjects requiring reconsent.  
* **triggers**: Regulatory Submission (0..N); Submissions.  
* **hasDocuments**: Document (1..N); Amendment documents.  
* **hasTasks**: Task (0..N); Implementation tasks.  
* **reviewedBy**: Oversight Body (0..N); Bodies reviewing.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Draft Amendment** (Sponsor Operations): Draft.  
* **Submit for Review** (Sponsor Operations): Submit.  
* **Approve Amendment** (Sponsor Operations): Approve.  
* **Implement Amendment** (Sponsor Operations): Implement.  
* **Withdraw Amendment** (Sponsor Operations): Withdraw.

## **40\. Regulatory Submission**

A package of documents submitted to a regulatory authority or ethics committee.  
***Editor note.** v0.2: enumerated submissionType across IND, CTA, NDA, BLA, IDE, IRB, EC; added eCTD module references; added relationships to Country (flagged missing) and Authority (flagged missing).*

### **Attributes**

* **regulatorySubmissionId** (string, IRI): Unique identifier.  
* **submissionName** (string): Display name.  
* **submissionType** (enum): ind, cta, nda, bla, ide, irb, ec, annual\_report, safety\_report, other.  
* **authorityName** (string): Authority (FDA, EMA, MHRA, PMDA, IRB).  
* **country** (string, ISO 3166): Country.  
* **submissionDate** (date, optional): Submission.  
* **decisionDate** (date, optional): Decision.  
* **decisionOutcome** (enum, optional): approved, conditional, deficient, withdrawn, rejected.  
* **ectdModuleReferences** (list\[string\]): eCTD modules.  
* **submissionStatus** (enum): in\_preparation, submitted, in\_review, decided, withdrawn.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **submittedBy** (PersonRef, optional): Submitter.

### **Relationships**

* **forStudy**: Study (1); Study.  
* **forSite**: Site (0..1); Site (for IRB).  
* **forCountry**: Country (0..1); Country; flagged as missing object below.  
* **toAuthority**: Regulatory Authority (1); Authority; flagged as missing object below.  
* **triggeredBy**: Amendment (0..1); Triggering amendment.  
* **hasDocuments**: Document (1..N); Documents in submission.  
* **hasTasks**: Task (0..N); Submission tasks.  
* **hasMilestones**: Milestone (0..N); Milestones.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Submission** (Regulatory Affairs): Create.  
* **Submit** (Regulatory Affairs): Submit.  
* **Record Decision** (Regulatory Affairs): Record outcome.  
* **Withdraw Submission** (Regulatory Affairs): Withdraw.

## **41\. Audit**

A formal examination of Study, Site, Vendor, or System conduct for compliance with GCP, the protocol, and applicable regulations.  
***Editor note.** v0.2: separated Audit (the engagement) from Audit Trail Entry (the system log); added relationships to CAPA and Finding (flagged missing).*

### **Attributes**

* **auditId** (string, IRI): Unique identifier.  
* **auditName** (string): Display name.  
* **auditType** (enum): internal, external, regulatory\_inspection, for\_cause, routine, system\_validation.  
* **auditScope** (string): Scope description.  
* **scheduledStart** (date): Scheduled start.  
* **scheduledEnd** (date): Scheduled end.  
* **actualStart** (date, optional): Actual start.  
* **actualEnd** (date, optional): Actual end.  
* **auditStatus** (enum): planned, in\_progress, report\_draft, closed, cancelled.  
* **findingCountMajor** (integer): Major findings.  
* **findingCountMinor** (integer): Minor findings.  
* **findingCountCritical** (integer): Critical findings.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **leadAuditor** (PersonRef): Lead auditor.

### **Relationships**

* **ofStudy**: Study (0..1); Target study.  
* **ofSite**: Site (0..1); Target site.  
* **ofSponsor**: Sponsor (0..1); Target sponsor.  
* **ofSystem**: System (0..1); Target system.  
* **ofService**: Service (0..1); Target service.  
* **commissionedBy**: Sponsor (1); Commissioner.  
* **hasFindings**: Finding (0..N); Findings; flagged as missing object below.  
* **triggersCAPAs**: CAPA (0..N); CAPAs.  
* **hasDocuments**: Document (1..N); Reports and letters.  
* **hasTasks**: Task (0..N); Prep and response tasks.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Schedule Audit** (Quality): Schedule.  
* **Conduct Audit** (Quality): Start audit.  
* **Issue Findings** (Quality): Issue findings.  
* **Close Audit** (Quality): Close.

## **42\. Report**

A generated artifact summarizing study, site, or subject data (CSR, DSUR, PSUR, monitoring report, listings, dashboards).  
***Editor note.** v0.2: enumerated reportType; added distinction between generated reports and interactive dashboards; added relationships to Endpoint and Data Transfer.*

### **Attributes**

* **reportId** (string, IRI): Unique identifier.  
* **reportName** (string): Display name.  
* **reportType** (enum): csr, dsur, psur, monitoring\_report, site\_performance, enrollment, safety, data\_quality, listing, dashboard, adhoc.  
* **reportingPeriodStart** (date, optional): Start.  
* **reportingPeriodEnd** (date, optional): End.  
* **generatedAt** (datetime): Generation.  
* **format** (enum): pdf, docx, xlsx, html, json, xml.  
* **version** (string, semver): Version.  
* **reportStatus** (enum): draft, in\_review, final, archived.  
* **uri** (string, URL): Location.  
* **confidentialityLevel** (enum): public, internal, restricted, confidential.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **generatedBy** (PersonRef or SystemRef): Generator.

### **Relationships**

* **forStudy**: Study (0..1); Study.  
* **forSite**: Site (0..N); Sites.  
* **coversEndpoints**: Endpoint (0..N); Endpoints reported.  
* **generatedBySystem**: System (0..1); Source system.  
* **generatedByService**: Service (0..1); Source service.  
* **basedOnDataTransfer**: Data Transfer (0..N); Source data transfers.  
* **hasDocuments**: Document (0..N); Attached files.  
* **reviewedBy**: Oversight Body (0..N); Reviewing bodies.  
* **submittedIn**: Regulatory Submission (0..N); Submissions including.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Generate Report** (Study Manager): Generate.  
* **Schedule Recurring Report** (Study Manager): Schedule.  
* **Finalize Report** (Study Manager): Finalize.  
* **Distribute Report** (Study Manager): Distribute.

## **43\. Shipment**

A physical transfer of Investigational Product, Devices, Equipment, or Samples between Organizations and Sites.  
***Editor note.** v0.2: generalized Shipment to handle IP, Device, Equipment, and Sample transfers; added chain-of-custody and temperature excursion tracking.*

### **Attributes**

* **shipmentId** (string, IRI): Unique identifier.  
* **shipmentType** (enum): ip\_outbound, ip\_return, sample\_outbound, device, equipment, supplies.  
* **trackingNumber** (string, optional): Carrier tracking.  
* **carrier** (string): Carrier.  
* **originOrganizationId** (string, IRI): Origin.  
* **destinationSiteId** (string, IRI): Destination.  
* **shippedAt** (datetime): Ship time.  
* **expectedDeliveryAt** (datetime, optional): Expected delivery.  
* **deliveredAt** (datetime, optional): Actual delivery.  
* **chainOfCustody** (list\[json\]): Custody events.  
* **temperatureExcursion** (boolean): Excursion flag.  
* **excursionDetails** (string, optional): Details.  
* **shipmentStatus** (enum): planned, in\_transit, delivered, lost, damaged, returned.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **contains**: Investigational Product (0..N); IP contents.  
* **contains**: Investigational Device (0..N); Device contents.  
* **contains**: Sample (0..N); Sample contents.  
* **contains**: Equipment (0..N); Equipment contents.  
* **forStudy**: Study (0..1); Study.  
* **forSite**: Site (1); Destination site.  
* **managedBy**: Service (0..1); IRT or central lab service.  
* **managedBy**: System (0..1); IRT or lab system.  
* **mayTrigger**: Deviation (0..N); Excursion-related.  
* **hasDocuments**: Document (0..N); Packing slips, COAs.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Create Shipment** (IRT Coordinator): Create.  
* **Ship** (IRT Coordinator): Ship.  
* **Acknowledge Receipt** (Coordinator): Acknowledge.  
* **Report Excursion** (Coordinator): Report.  
* **Return Shipment** (IRT Coordinator): Initiate return.

## **44\. Questionnaire**

A structured set of items administered to a Subject or Clinician (COA, PRO, ClinRO, PerfO).  
***Editor note.** v0.2: aligned types to COA taxonomy (PRO, ClinRO, ObsRO, PerfO); added scoring algorithm and administration modality.*

### **Attributes**

* **questionnaireId** (string, IRI): Unique identifier.  
* **questionnaireName** (string): Display name.  
* **questionnaireType** (enum): pro, clinro, obsro, perfo, qol, symptom\_diary, safety.  
* **instrumentCode** (string, optional): Instrument code (e.g., EQ-5D-5L, PROMIS-29).  
* **administrationModality** (enum): paper, epro, phone, in\_clinic.  
* **languages** (list\[string, ISO 639\]): Languages available.  
* **itemCount** (integer): Number of items.  
* **scoringAlgorithm** (string): Scoring description.  
* **validationStatus** (enum): validated, under\_validation, unvalidated.  
* **licensingTerms** (string, optional): License.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **partOfSOA**: Schedule of Assessments (0..N); In SOA.  
* **administeredAtVisit**: Visit (0..N); Visit administration.  
* **completedBy**: Participant (Subject) (0..N); Subjects completing.  
* **completedBy**: Person (0..N); Clinicians or observers.  
* **producesCRF**: CRF (0..N); CRF transport.  
* **measuresEndpoint**: Endpoint (0..N); Endpoints measured.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Register Questionnaire** (Study Designer): Register.  
* **Administer Questionnaire** (Coordinator): Administer.  
* **Score Questionnaire** (System): Auto-score.  
* **Review Questionnaire** (Investigator): Review.

## **45\. Other Clinical Event**

A clinical event captured for the Subject that is not an Adverse Event, Concomitant Medication, or Medical History entry (e.g., hospitalization for a planned procedure, pregnancy exposure in partner).  
***Editor note.** v0.2: renamed from v0 Other Event; clarified boundary with Adverse Event and Medical History; added reporting flags.*

### **Attributes**

* **otherClinicalEventId** (string, IRI): Unique identifier.  
* **subjectId** (string, IRI): Subject.  
* **eventCategory** (enum): planned\_procedure, hospitalization, pregnancy\_exposure, protocol\_deviation\_linked, other.  
* **eventTerm** (string): Preferred term.  
* **meddraCode** (string, optional): MedDRA code.  
* **eventStart** (datetime): Start.  
* **eventEnd** (datetime, optional): End.  
* **outcome** (string): Outcome.  
* **reportableToSponsor** (boolean): Reportable.  
* **eventStatus** (enum): ongoing, resolved, resolved\_with\_sequelae, fatal.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **reportedBy** (PersonRef): Reporter.

### **Relationships**

* **forSubject**: Participant (Subject) (1); Subject.  
* **capturedOnCRF**: CRF (0..N); CRF capture.  
* **reviewedBy**: Person (1..N); Reviewers.  
* **mayRelateTo**: Adverse Event (0..N); Adjacent AEs.  
* **mayRelateTo**: Concomitant Medication (0..N); ConMeds; flagged as missing object below.  
* **mayRelateTo**: Medical History (0..N); Medical history; flagged as missing object below.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Record Event** (Coordinator): Record.  
* **Update Outcome** (Investigator): Update.  
* **Flag for Sponsor Report** (Investigator): Flag.

## **46\. CAPA (Corrective and Preventive Action)**

A documented response to a Finding, Deviation, or quality issue that includes a corrective action and a preventive action.  
***Editor note.** v0.2: split rootCause from corrective and preventive arms; added effectivenessCheck date and outcome.*

### **Attributes**

* **capaId** (string, IRI): Unique identifier.  
* **capaName** (string): Display name.  
* **triggerType** (enum): finding, deviation, complaint, audit\_observation, monitoring\_observation, internal\_review.  
* **triggerRefId** (string, IRI): Trigger reference.  
* **rootCause** (string): Root cause.  
* **correctiveAction** (string): Corrective action description.  
* **preventiveAction** (string): Preventive action description.  
* **plannedCompletionDate** (date): Planned completion.  
* **actualCompletionDate** (date, optional): Actual completion.  
* **effectivenessCheckDate** (date, optional): Effectiveness check.  
* **effectivenessOutcome** (enum, optional): effective, not\_effective, partially\_effective.  
* **capaStatus** (enum): open, in\_progress, awaiting\_effectiveness\_check, closed\_effective, closed\_ineffective, cancelled.  
* **severity** (enum): low, medium, high, critical.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **ownedBy** (PersonRef): Owner.

### **Relationships**

* **triggeredBy**: Finding (0..1); Audit finding; flagged as missing object below.  
* **triggeredBy**: Deviation (0..1); Deviation.  
* **triggeredBy**: Audit (0..1); Audit.  
* **triggeredBy**: Monitoring Visit (0..1); Monitoring visit.  
* **triggeredBy**: Discrepancy (Query) (0..1); Query.  
* **affectsStudy**: Study (0..N); Studies.  
* **affectsSite**: Site (0..N); Sites.  
* **affectsSystem**: System (0..N); Systems.  
* **affectsService**: Service (0..N); Services.  
* **hasTasks**: Task (1..N); CAPA tasks.  
* **hasDocuments**: Document (0..N); Documents.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Open CAPA** (Quality): Open.  
* **Update CAPA** (Quality): Update.  
* **Verify Effectiveness** (Quality): Effectiveness check.  
* **Close CAPA** (Quality): Close.

## **47\. Date**

A first-class semantic date for a Subject, Study, or Site (consent date, screening date, randomization date, first dose, last dose, end of study).  
***Editor note.** v0.2: kept Date as a labeled milestone-style object (matches v0 intent); added subjectStatusEffectiveDate and rationale field.*

### **Attributes**

* **dateId** (string, IRI): Unique identifier.  
* **dateLabel** (enum): consent, screening, randomization, enrollment, first\_dose, last\_dose, end\_of\_treatment, end\_of\_study, withdrawal, screen\_fail, ltfu, death, study\_start, study\_end, site\_activation, site\_close.  
* **parentObjectType** (enum): subject, study, site, arm.  
* **parentObjectId** (string, IRI): Parent reference.  
* **dateValue** (date): Date value.  
* **rationale** (string, optional): Rationale or note.  
* **effectiveStatusAfter** (string, optional): Status after this date.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **recordedBy** (PersonRef): Recorder.

### **Relationships**

* **relatesToSubject**: Participant (Subject) (0..1); Subject.  
* **relatesToStudy**: Study (0..1); Study.  
* **relatesToSite**: Site (0..1); Site.  
* **relatesToArm**: Arm (0..1); Arm.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Record Date** (Coordinator): Record.  
* **Edit Date** (Coordinator): Edit (with reason).  
* **Reconcile Date** (Data Manager): Reconcile across systems.

## **48\. Sample**

A biological specimen collected from a Subject (blood, urine, tissue, saliva, biopsy) for laboratory analysis or biobanking.  
***Editor note.** v0.2: added biobanking flags, container metadata, processing chain, and consent linkage.*

### **Attributes**

* **sampleId** (string, IRI): Unique identifier.  
* **subjectId** (string, IRI): Subject.  
* **visitId** (string, IRI): Visit.  
* **sampleType** (enum): whole\_blood, serum, plasma, urine, tissue, biopsy, saliva, csf, swab, stool, other.  
* **volume** (decimal, optional): Volume.  
* **volumeUnit** (string, UCUM, optional): Volume unit.  
* **containerType** (string): Container type.  
* **preservative** (string, optional): Preservative.  
* **collectedAt** (datetime): Collection.  
* **storageTemperatureC** (decimal): Storage temperature.  
* **storageLocationId** (string, IRI, optional): Location reference; flagged as missing object below.  
* **biobankRetained** (boolean): Retained for biobanking.  
* **biobankConsentScope** (string, optional): Consent scope for biobanking.  
* **sampleStatus** (enum): collected, in\_transit, received, processed, analyzed, depleted, destroyed.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **collectedBy** (PersonRef): Collector.

### **Relationships**

* **fromSubject**: Participant (Subject) (1); Subject.  
* **atVisit**: Visit (1); Visit.  
* **producesLabResult**: Lab Results (0..N); Lab results.  
* **shippedVia**: Shipment (0..N); Shipments.  
* **governedByConsent**: Informed Consent (1); Consent governing.  
* **storedAt**: Storage Location (0..1); Storage location; flagged as missing object below.  
* **hasDocuments**: Document (0..N); Chain-of-custody documents.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Collect Sample** (Coordinator): Collect.  
* **Ship Sample** (Coordinator): Ship.  
* **Receive Sample** (Lab Manager): Receive.  
* **Process Sample** (Lab Manager): Process.  
* **Destroy Sample** (Lab Manager): Destroy.

## **49\. Equipment**

A physical instrument used in trial conduct (centrifuge, ECG machine, blood pressure cuff, thermometer, freezer, infusion pump).  
***Editor note.** v0.2: added calibration cadence and last-calibration date; added relationship to Site and to Manufacturer.*

### **Attributes**

* **equipmentId** (string, IRI): Unique identifier.  
* **equipmentName** (string): Display name.  
* **equipmentType** (string): Type.  
* **manufacturer** (string): Manufacturer.  
* **model** (string): Model.  
* **serialNumber** (string): Serial number.  
* **siteId** (string, IRI): Site.  
* **calibrationCadenceDays** (integer): Calibration cadence.  
* **lastCalibrationDate** (date, optional): Last calibration.  
* **nextCalibrationDate** (date, optional): Next calibration.  
* **equipmentStatus** (enum): in\_service, out\_of\_service, retired, in\_calibration.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **locatedAt**: Site (1); Host site.  
* **usedFor**: Visit (0..N); Visits where used.  
* **producedBy**: Sponsor (0..1); Manufacturer organization.  
* **producesData**: CRF (0..N); Data records.  
* **producesData**: Lab Results (0..N); Lab results.  
* **hasShipments**: Shipment (0..N); Shipments.  
* **hasDocuments**: Document (0..N); Calibration certificates.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Register Equipment** (Coordinator): Register.  
* **Calibrate Equipment** (Coordinator): Calibrate.  
* **Take Out of Service** (Coordinator): Out of service.  
* **Retire Equipment** (Coordinator): Retire.

## **50\. Data Transfer**

A scheduled or ad-hoc transfer of data between Systems or between organizations (lab feeds, IRT to EDC, EDC to safety, sponsor to vendor, sponsor to authority).  
***Editor note.** v0.2: added DTA reference (Data Transfer Agreement), schema mapping, reconciliation outcome, and relationship to Service.*

### **Attributes**

* **dataTransferId** (string, IRI): Unique identifier.  
* **dataTransferName** (string): Display name.  
* **transferType** (enum): lab\_feed, irt\_feed, safety\_feed, sponsor\_to\_authority, sponsor\_to\_vendor, vendor\_to\_sponsor, intra\_system.  
* **sourceSystemId** (string, IRI): Source system.  
* **destinationSystemId** (string, IRI): Destination system.  
* **scheduledStartAt** (datetime): Scheduled start.  
* **actualStartAt** (datetime, optional): Actual start.  
* **actualEndAt** (datetime, optional): Actual end.  
* **recordCount** (integer, optional): Records.  
* **fileFormat** (enum): csv, sas\_xpt, json, xml, sdtm, adam, hl7, fhir, edc\_export.  
* **schemaVersion** (string, optional): Schema version.  
* **transferStatus** (enum): scheduled, in\_progress, succeeded, partial, failed, reconciled.  
* **reconciliationOutcome** (enum, optional): matched, discrepancies, not\_reconciled.  
* **dtaReference** (string, IRI, optional): Data Transfer Agreement.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **fromSystem**: System (0..1); Source system.  
* **toSystem**: System (0..1); Destination system.  
* **governedBy**: Service (0..1); Service.  
* **governedBy**: Contract (0..1); DTA.  
* **producesReport**: Report (0..N); Reports.  
* **carriesCRFs**: CRF (0..N); CRF data.  
* **carriesLabResults**: Lab Results (0..N); Lab data.  
* **mayTrigger**: Discrepancy (Query) (0..N); Reconciliation queries.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Schedule Data Transfer** (Data Manager): Schedule.  
* **Run Data Transfer** (Data Manager): Run.  
* **Reconcile Data Transfer** (Data Manager): Reconcile.  
* **Reprocess Failed Transfer** (Data Manager): Reprocess.

## **51\. User Role**

A named bundle of permissions in a System (Investigator, Coordinator, Monitor, Data Manager, Auditor, Read-Only).  
***Editor note.** v0.2: separated User Role (system permission set) from Person Role (clinical role). Added permission scopes and inheritance.*

### **Attributes**

* **userRoleId** (string, IRI): Unique identifier.  
* **userRoleName** (string): Display name.  
* **systemId** (string, IRI): System.  
* **scope** (enum): global, study, site.  
* **permissions** (list\[string\]): Permission strings.  
* **inheritsFrom** (string, IRI, optional): Parent role.  
* **active** (boolean): Active flag.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **definedIn**: System (1); Parent system.  
* **confersTo**: Credential (1..N); Credentials granting role.  
* **mappedToPersonRole**: Person Role (0..N); Mapped clinical role.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Define User Role** (System Administrator): Define.  
* **Update Permissions** (System Administrator): Update.  
* **Retire User Role** (System Administrator): Retire.

## **52\. Inclusion Criteria**

A protocol-defined condition that a candidate must meet to be eligible for a Study.  
***Editor note.** v0.2: split Inclusion and Exclusion into separate object types (was a single Eligibility object in v0); added datatypes for assertion and source value.*

### **Attributes**

* **inclusionCriteriaId** (string, IRI): Unique identifier.  
* **protocolId** (string, IRI): Parent protocol.  
* **ordinal** (integer): Display order.  
* **criterionText** (string): Criterion text.  
* **criterionCode** (string, optional): Coded condition (LOINC, SNOMED).  
* **comparator** (enum, optional): eq, ne, gt, gte, lt, lte, in, contains.  
* **expectedValue** (string, optional): Expected value.  
* **unit** (string, UCUM, optional): Unit.  
* **effectiveStart** (date): Effective start.  
* **effectiveEnd** (date, optional): Effective end.  
* **version** (string, semver): Criterion version.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **definedBy**: Protocol (1); Parent protocol.  
* **evaluatedAgainst**: Participant (Subject) (0..N); Subjects evaluated.  
* **hasAmendments**: Amendment (0..N); Amendments.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Define Inclusion Criterion** (Study Designer): Define.  
* **Edit Inclusion Criterion** (Study Designer): Edit.  
* **Retire Inclusion Criterion** (Study Designer): Retire.

## **53\. Exclusion Criteria**

A protocol-defined condition that disqualifies a candidate from a Study.  
***Editor note.** v0.2: split Exclusion from Inclusion; added rationale and clinical evidence link.*

### **Attributes**

* **exclusionCriteriaId** (string, IRI): Unique identifier.  
* **protocolId** (string, IRI): Parent protocol.  
* **ordinal** (integer): Display order.  
* **criterionText** (string): Criterion text.  
* **criterionCode** (string, optional): Coded condition.  
* **rationale** (string): Rationale.  
* **effectiveStart** (date): Effective start.  
* **effectiveEnd** (date, optional): Effective end.  
* **version** (string, semver): Criterion version.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **definedBy**: Protocol (1); Parent protocol.  
* **evaluatedAgainst**: Participant (Subject) (0..N); Subjects evaluated.  
* **triggers**: Screen Fail (0..N); Triggers screen fail.  
* **hasAmendments**: Amendment (0..N); Amendments.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Define Exclusion Criterion** (Study Designer): Define.  
* **Edit Exclusion Criterion** (Study Designer): Edit.  
* **Retire Exclusion Criterion** (Study Designer): Retire.

## **54\. Monitoring Visit**

An on-site, remote, or central monitoring engagement at a Site to verify data, source documents, IP accountability, regulatory binder, and protocol compliance.  
***Editor note.** v0.2: enumerated visitMode (on\_site, remote, central, hybrid); added riskBasedTrigger and findings linkage.*

### **Attributes**

* **monitoringVisitId** (string, IRI): Unique identifier.  
* **siteId** (string, IRI): Site.  
* **studyId** (string, IRI): Study.  
* **visitMode** (enum): on\_site, remote, central, hybrid.  
* **visitType** (enum): site\_qualification, site\_initiation, interim, close\_out, for\_cause.  
* **scheduledStart** (date): Scheduled start.  
* **scheduledEnd** (date): Scheduled end.  
* **actualStart** (date, optional): Actual start.  
* **actualEnd** (date, optional): Actual end.  
* **monitorId** (string, IRI): Monitor person.  
* **riskBasedTrigger** (string, optional): Risk-based trigger description.  
* **visitStatus** (enum): planned, in\_progress, report\_draft, report\_signed, follow\_up, closed.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **atSite**: Site (1); Target site.  
* **forStudy**: Study (1); Study.  
* **conductedBy**: Person (1); Monitor.  
* **reviewsLogs**: Log (0..N); Reviewed logs.  
* **reviewsCRFs**: CRF (0..N); Reviewed CRFs.  
* **reviewsConsents**: Informed Consent (0..N); Consents reviewed.  
* **reviewsIP**: Investigational Product (0..N); IP accountability.  
* **producesFindings**: Finding (0..N); Findings; flagged as missing object below.  
* **raisesQueries**: Discrepancy (Query) (0..N); Queries raised.  
* **triggersCAPAs**: CAPA (0..N); CAPAs.  
* **hasReports**: Report (1..N); Monitoring reports.  
* **hasActionItems**: Action Item (0..N); Action items.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Schedule Monitoring Visit** (Clinical Operations): Schedule.  
* **Conduct Monitoring Visit** (Monitor): Conduct.  
* **Submit Monitoring Report** (Monitor): Submit report.  
* **Sign Monitoring Report** (Site PI): Sign report.  
* **Close Monitoring Visit** (Clinical Operations): Close.

## **55\. Serious Adverse Event (SAE)**

An Adverse Event meeting seriousness criteria (death, life-threatening, hospitalization, persistent disability, congenital anomaly, other medically significant).  
***Editor note.** v0.2: explicitly modeled as a specialization of Adverse Event with seriousness criteria flags; added expedited reporting metadata.*

### **Attributes**

* **serousAdverseEventId** (string, IRI): Unique identifier.  
* **adverseEventId** (string, IRI): Parent AE.  
* **seriousnessDeath** (boolean): Death.  
* **seriousnessLifeThreatening** (boolean): Life threatening.  
* **seriousnessHospitalization** (boolean): Hospitalization.  
* **seriousnessPersistentDisability** (boolean): Persistent disability.  
* **seriousnessCongenitalAnomaly** (boolean): Congenital anomaly.  
* **seriousnessOtherMedicallySignificant** (boolean): Other medically significant.  
* **onsetAt** (datetime): Onset.  
* **becameSeriousAt** (datetime): Became serious.  
* **initialReportedAt** (datetime): Initial report.  
* **expeditedReportingDueBy** (datetime): Reporting deadline.  
* **expeditedReportingSubmittedAt** (datetime, optional): Submission.  
* **causalityAssessment** (enum): unrelated, unlikely, possible, probable, definite.  
* **expectedness** (enum): expected, unexpected.  
* **saeStatus** (enum): open, reported, under\_review, resolved, closed.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **reportedBy** (PersonRef): Reporter.

### **Relationships**

* **specializes**: Adverse Event (1); Parent AE.  
* **forSubject**: Participant (Subject) (1); Subject.  
* **triggersSafetyReport**: Safety Report (0..N); Safety reports; flagged as missing object below.  
* **triggersRegulatorySubmission**: Regulatory Submission (0..N); Expedited reports.  
* **mayTriggerSignal**: Safety Signal (0..N); Signal; flagged as missing object below.  
* **reviewedBy**: Oversight Body (0..N); Oversight reviews.  
* **hasDocuments**: Document (1..N); Narratives, source.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Report SAE** (Investigator): Report.  
* **Submit Expedited Report** (Pharmacovigilance): Submit.  
* **Update SAE** (Investigator): Update.  
* **Reconcile SAE** (Pharmacovigilance): Reconcile to AE.  
* **Close SAE** (Pharmacovigilance): Close.

## **56\. Region (flagged missing in v0)**

A geographic or operational grouping of Countries or Sites for monitoring, regulatory, or commercial purposes (NA, EU, APAC, LATAM, MENA).  
***Editor note.** v0.2: introduced as a stub. Region is referenced by Site and by Sponsor governance but was a yellow TODO in v0. Needs full attribute and relationship specification before NGSI-LD translation.*

### **Attributes**

* **regionId** (string, IRI): Unique identifier.  
* **regionName** (string): Display name.  
* **regionCode** (string): Code (e.g., NA, EU, APAC).  
* **parentRegionId** (string, IRI, optional): Parent region.  
* **countries** (list\[string, ISO 3166\]): Member countries.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **contains**: Country (1..N); Countries; flagged as missing object below.  
* **contains**: Site (0..N); Sites in region.  
* **monitoredBy**: Person (0..N); Regional leads.  
* **governedBy**: Sponsor (0..N); Regional sponsor org units.

### **Calls to Action**

* **Define Region** (Sponsor Operations): Define.  
* **Assign Country** (Sponsor Operations): Assign country.

## **57\. Country (flagged missing in v0)**

A national jurisdiction; the regulatory and operational boundary for a Site, Submission, and many privacy and labeling rules.  
***Editor note.** v0.2: introduced as a stub. Country is implied by every Site and every Regulatory Submission but had no first-class object in v0.*

### **Attributes**

* **countryId** (string, IRI): Unique identifier.  
* **countryCode** (string, ISO 3166): ISO code.  
* **countryName** (string): Display name.  
* **regulatoryAuthorityId** (string, IRI, optional): Primary authority.  
* **privacyRegime** (enum): gdpr, hipaa, lgpd, pipl, other.  
* **languages** (list\[string, ISO 639\]): Official languages.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **memberOfRegion**: Region (0..1); Region.  
* **hasAuthority**: Regulatory Authority (1..N); Authorities.  
* **hostsSite**: Site (0..N); Sites.  
* **receivesSubmission**: Regulatory Submission (0..N); Submissions.

### **Calls to Action**

* **Add Country** (Regulatory Affairs): Add.  
* **Update Privacy Regime** (Privacy): Update.

## **58\. Site Network (flagged missing in v0)**

A consortium or company that operates many Sites under shared governance (SMO, integrated health system, academic network).  
***Editor note.** v0.2: introduced as a stub. Several Site fields refer to a parent network, but Network had no first-class object in v0.*

### **Attributes**

* **networkId** (string, IRI): Unique identifier.  
* **networkName** (string): Display name.  
* **networkType** (enum): smo, academic, ihn, government, other.  
* **centralIrbId** (string, IRI, optional): Central IRB body.  
* **headquartersCountry** (string, ISO 3166): HQ country.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **ownsSite**: Site (1..N); Member sites.  
* **governedBy**: Oversight Body (0..N); Central governance.  
* **holdsContracts**: Contract (0..N); Master contracts.

### **Calls to Action**

* **Register Network** (Sponsor Operations): Register.  
* **Onboard Member Site** (Network Manager): Add member site.

## **59\. Therapeutic Area (flagged missing in v0)**

A clinical domain (oncology, cardiology, immunology, infectious disease, neurology, rare disease) used to classify Studies, Sites, and Investigators.  
***Editor note.** v0.2: introduced as a stub. Used for Site capability matching and portfolio reporting; absent in v0.*

### **Attributes**

* **therapeuticAreaId** (string, IRI): Unique identifier.  
* **therapeuticAreaName** (string): Display name.  
* **parentTherapeuticAreaId** (string, IRI, optional): Parent area.  
* **icd10Codes** (list\[string\]): Mapped ICD-10 codes.  
* **snomedCodes** (list\[string\]): Mapped SNOMED codes.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **classifiesStudy**: Study (0..N); Studies.  
* **classifiesSite**: Site (0..N); Sites with experience.  
* **classifiesInvestigator**: Person (0..N); Investigators with experience.

### **Calls to Action**

* **Add Therapeutic Area** (Sponsor Operations): Add.  
* **Map Codes** (Sponsor Operations): Map ICD/SNOMED.

## **60\. Regulatory Authority (flagged missing in v0)**

A governmental or supranational body that authorizes and oversees clinical research (FDA, EMA, MHRA, PMDA, NMPA, ANVISA).  
***Editor note.** v0.2: introduced as a stub. Referenced by Submission and by Site jurisdiction; absent in v0.*

### **Attributes**

* **regulatoryAuthorityId** (string, IRI): Unique identifier.  
* **authorityName** (string): Display name.  
* **authorityCode** (string): Short code.  
* **country** (string, ISO 3166): Country.  
* **scope** (enum): national, regional, supranational.  
* **contactDetails** (string): Contact.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **operatesIn**: Country (1..N); Jurisdiction countries.  
* **receivesSubmission**: Regulatory Submission (0..N); Submissions.  
* **conductsInspection**: Audit (0..N); Inspections.

### **Calls to Action**

* **Register Authority** (Regulatory Affairs): Register.  
* **Update Authority** (Regulatory Affairs): Update.

## **61\. Investigator (flagged missing in v0; elevated from Person)**

A specialization of Person who holds the legal responsibility for trial conduct at a Site (Principal Investigator or Sub-Investigator).  
***Editor note.** v0.2: recommended as an elevated subtype of Person to support FHIR Practitioner alignment, regulatory CV tracking, and disclosure history. Could be modeled as a NGSI-LD subProperty of Person.*

### **Attributes**

* **investigatorId** (string, IRI): Unique identifier.  
* **personId** (string, IRI): Linked Person.  
* **investigatorRole** (enum): principal, sub, coordinator\_investigator.  
* **licenseNumber** (string): License number.  
* **licenseAuthority** (string): License authority.  
* **licenseExpiry** (date): License expiry.  
* **cvOnFileDate** (date): CV currency.  
* **gcpTrainingExpiry** (date): GCP training expiry.  
* **form1572OnFile** (boolean): 1572 on file (US).  
* **financialDisclosureOnFile** (boolean): FCOI disclosure.  
* **debarmentStatus** (enum): clear, debarred, under\_review.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **specializes**: Person (1); Parent person.  
* **affiliatedWith**: Site (1..N); Affiliated sites.  
* **delegatedTasksFor**: Study (0..N); Studies.  
* **hasCredentials**: Credential (0..N); System access.  
* **hasDocuments**: Document (1..N); CV, training, 1572\.  
* **classifiedBy**: Therapeutic Area (0..N); Areas of experience.

### **Calls to Action**

* **Onboard Investigator** (Site Activation Manager): Onboard.  
* **Refresh GCP Training** (Investigator): Refresh.  
* **Update FCOI Disclosure** (Investigator): Update.

## **62\. Assessment (flagged missing in v0)**

An individual measurement or observation defined by the Schedule of Assessments and performed at a Visit (vital sign, ECG, lab draw, questionnaire administration, imaging).  
***Editor note.** v0.2: introduced as a stub. v0 only modeled CRF (the data capture form); Assessment is the protocol-defined measurement that drives the CRF.*

### **Attributes**

* **assessmentId** (string, IRI): Unique identifier.  
* **assessmentName** (string): Display name.  
* **assessmentType** (enum): vital\_sign, ecg, lab, imaging, questionnaire, physical\_exam, biopsy, sample\_collection, ip\_administration, other.  
* **code** (string, optional): Coded concept (LOINC, SNOMED).  
* **estimatedDurationMinutes** (integer): Duration.  
* **windowDays** (integer): Visit window.  
* **fastingRequired** (boolean): Fasting required.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **definedBy**: Schedule of Assessments (1); Parent SOA.  
* **performedAt**: Visit (0..N); Visit performances.  
* **producesCRF**: CRF (0..1); CRF output.  
* **producesLabResult**: Lab Results (0..1); Lab output.  
* **producesQuestionnaire**: Questionnaire (0..1); Questionnaire administration.  
* **producesSample**: Sample (0..1); Sample collection.  
* **measuresEndpoint**: Endpoint (0..N); Endpoints.

### **Calls to Action**

* **Define Assessment** (Study Designer): Define.  
* **Edit Assessment** (Study Designer): Edit.

## **63\. Audit Trail Entry (flagged missing in v0)**

An immutable record of a create, update, or delete operation against any object in any System; required by 21 CFR Part 11 and Annex 11\.  
***Editor note.** v0.2: introduced as a stub. v0 referenced "audit" loosely; this object separates the system-generated trail from the human-conducted Audit engagement.*

### **Attributes**

* **auditTrailEntryId** (string, IRI): Unique identifier.  
* **eventTime** (datetime): Event time (UTC).  
* **systemId** (string, IRI): Source system.  
* **actorPersonId** (string, IRI, optional): Actor.  
* **actorSystemId** (string, IRI, optional): Acting system (for automation).  
* **action** (enum): create, read, update, delete, sign, login, logout, export, import.  
* **targetObjectType** (string): Target type.  
* **targetObjectId** (string, IRI): Target id.  
* **oldValueJson** (json, optional): Old value.  
* **newValueJson** (json, optional): New value.  
* **reasonForChange** (string, optional): Reason.  
* **signatureId** (string, IRI, optional): Electronic signature.  
* **ipAddress** (string, optional): IP.  
* **sessionId** (string, optional): Session.

### **Metadata**

* **ingestedAt** (datetime): Ingestion.

### **Relationships**

* **emittedBy**: System (1); Source system.  
* **performedBy**: Person (0..1); Actor person.  
* **affects**: Object (1); Target object (any type).

### **Calls to Action**

* **View Audit Trail** (Auditor): View.  
* **Export Audit Trail** (Auditor): Export.

## **64\. Finding (flagged missing in v0)**

An issue identified during a Monitoring Visit or Audit, classified by severity and category.  
***Editor note.** v0.2: introduced as a stub. Findings are referenced by CAPA but had no object in v0.*

### **Attributes**

* **findingId** (string, IRI): Unique identifier.  
* **findingTitle** (string): Title.  
* **findingDescription** (string): Description.  
* **severity** (enum): critical, major, minor, observation.  
* **category** (enum): protocol\_compliance, informed\_consent, source\_documentation, ip\_accountability, regulatory\_binder, safety\_reporting, data\_integrity, training, other.  
* **identifiedAt** (datetime): Identified.  
* **identifiedBy** (PersonRef): Identifier.  
* **findingStatus** (enum): open, accepted, in\_remediation, resolved, closed\_no\_action.  
* **responseDueBy** (date, optional): Response due.  
* **responseReceivedAt** (datetime, optional): Response received.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **raisedDuring**: Monitoring Visit (0..1); Monitoring visit.  
* **raisedDuring**: Audit (0..1); Audit.  
* **atSite**: Site (0..1); Site.  
* **triggersCAPA**: CAPA (0..N); CAPAs.  
* **hasDocuments**: Document (0..N); Documents.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Record Finding** (Monitor): Record.  
* **Respond to Finding** (Site PI): Respond.  
* **Close Finding** (Quality): Close.

## **65\. Concomitant Medication (flagged missing in v0)**

A medication taken by a Subject during the trial that is not the Investigational Product.  
***Editor note.** v0.2: introduced as a stub. ConMeds are referenced by Adverse Event causality and were a yellow TODO in v0.*

### **Attributes**

* **concomitantMedicationId** (string, IRI): Unique identifier.  
* **subjectId** (string, IRI): Subject.  
* **medicationName** (string): Trade name.  
* **atcCode** (string, optional): ATC code.  
* **rxnormCode** (string, optional): RxNorm code.  
* **indication** (string): Indication.  
* **doseAmount** (decimal): Dose.  
* **doseUnit** (string, UCUM): Dose unit.  
* **frequency** (string, RRULE): Frequency.  
* **route** (enum): oral, iv, im, sc, topical, inhaled, other.  
* **startDate** (date): Start.  
* **endDate** (date, optional): End.  
* **ongoing** (boolean): Ongoing.  
* **protocolProhibited** (boolean): Prohibited per protocol.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **forSubject**: Participant (Subject) (1); Subject.  
* **relatesTo**: Adverse Event (0..N); Causality.  
* **relatesTo**: Medical History (0..N); History context.  
* **mayCauseDeviation**: Deviation (0..N); Deviations.  
* **capturedOnCRF**: CRF (1..N); CRF.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Record ConMed** (Coordinator): Record.  
* **Update ConMed** (Coordinator): Update.  
* **Mark Prohibited** (Coordinator): Mark prohibited.

## **66\. Medical History (flagged missing in v0)**

A pre-existing condition or past event recorded for a Subject at baseline.  
***Editor note.** v0.2: introduced as a stub. Medical history was a yellow TODO and is needed for eligibility, AE causality, and demographics modeling.*

### **Attributes**

* **medicalHistoryId** (string, IRI): Unique identifier.  
* **subjectId** (string, IRI): Subject.  
* **conditionTerm** (string): Condition term.  
* **meddraCode** (string, optional): MedDRA code.  
* **snomedCode** (string, optional): SNOMED code.  
* **onsetDate** (date, partial): Onset (may be partial).  
* **resolutionDate** (date, optional): Resolution.  
* **ongoing** (boolean): Ongoing.  
* **severity** (enum, optional): mild, moderate, severe.  
* **historySource** (enum): self\_report, ehr, clinician, other.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **forSubject**: Participant (Subject) (1); Subject.  
* **evaluatedBy**: Inclusion Criteria (0..N); Eligibility.  
* **evaluatedBy**: Exclusion Criteria (0..N); Eligibility.  
* **relatesTo**: Adverse Event (0..N); Causality.  
* **capturedOnCRF**: CRF (1..N); CRF.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Record Medical History** (Coordinator): Record.  
* **Update Medical History** (Coordinator): Update.

## **67\. Risk Assessment (flagged missing in v0)**

A documented evaluation of risks at the Study, Site, Vendor, or System level (RBQM, ICH E6 R3, GVP).  
***Editor note.** v0.2: introduced as a stub. Yellow TODO in v0; required to model risk-based monitoring and quality management.*

### **Attributes**

* **riskAssessmentId** (string, IRI): Unique identifier.  
* **riskAssessmentName** (string): Display name.  
* **scope** (enum): study, site, vendor, system, country.  
* **scopeRefId** (string, IRI): Scope reference.  
* **framework** (enum): ich\_e6\_r3\_rbqm, ich\_e8\_r1, gvp, internal.  
* **identifiedRisks** (list\[json\]): Risk register.  
* **overallRiskLevel** (enum): low, medium, high, critical.  
* **mitigationsSummary** (string): Mitigations.  
* **effectiveStart** (date): Start.  
* **nextReviewDate** (date): Next review.  
* **assessmentStatus** (enum): draft, approved, retired.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **assessesStudy**: Study (0..1); Study.  
* **assessesSite**: Site (0..1); Site.  
* **drivesMonitoringStrategy**: Service Configuration (0..N); Monitoring strategy.  
* **drivesMonitoringVisits**: Monitoring Visit (0..N); Risk-based triggers.  
* **hasDocuments**: Document (1..N); Risk register documents.  
* **reviewedBy**: Oversight Body (0..N); Oversight.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Conduct Risk Assessment** (Quality): Conduct.  
* **Update Risk Register** (Quality): Update.  
* **Approve Risk Assessment** (Quality): Approve.

## **68\. Data Quality Metric (flagged missing in v0)**

A computed measure of data quality (query rate per page, time-to-resolution, missing data rate, SDV rate, lock rate).  
***Editor note.** v0.2: introduced as a stub. Yellow TODO in v0; required for RBQM dashboards.*

### **Attributes**

* **dataQualityMetricId** (string, IRI): Unique identifier.  
* **metricName** (string): Display name.  
* **metricCode** (enum): query\_rate, ttr\_days, missing\_rate, sdv\_rate, lock\_rate, cdisc\_conformance.  
* **scope** (enum): study, site, subject, crf.  
* **scopeRefId** (string, IRI): Scope reference.  
* **observationWindowStart** (date): Window start.  
* **observationWindowEnd** (date): Window end.  
* **value** (decimal): Value.  
* **unit** (string): Unit.  
* **thresholdLow** (decimal, optional): Low threshold.  
* **thresholdHigh** (decimal, optional): High threshold.  
* **breached** (boolean): Threshold breach.

### **Metadata**

* **computedAt** (datetime): Computation time.  
* **computedBy** (SystemRef): Computing system.

### **Relationships**

* **scopedTo**: Study (0..1); Study.  
* **scopedTo**: Site (0..1); Site.  
* **scopedTo**: CRF (0..1); CRF.  
* **mayTrigger**: Action Item (0..N); Action items.  
* **reportedIn**: Report (0..N); Reports.

### **Calls to Action**

* **Configure Metric** (Data Manager): Configure.  
* **Drill Into Metric** (Data Manager): Drill.

## **69\. Enrollment Forecast (flagged missing in v0)**

A model-generated projection of screening, enrollment, and randomization numbers by Site, Country, or Study over time.  
***Editor note.** v0.2: introduced as a stub. Yellow TODO in v0; distinguishes forecast from Enrollment event and from Study Performance Metric.*

### **Attributes**

* **enrollmentForecastId** (string, IRI): Unique identifier.  
* **forecastName** (string): Display name.  
* **scope** (enum): study, country, site.  
* **scopeRefId** (string, IRI): Scope reference.  
* **methodology** (enum): linear, poisson, monte\_carlo, expert, other.  
* **forecastHorizonStart** (date): Horizon start.  
* **forecastHorizonEnd** (date): Horizon end.  
* **targetCount** (integer): Target enrollments.  
* **projectedCount** (integer): Projected.  
* **confidenceLow** (integer): Low bound.  
* **confidenceHigh** (integer): High bound.  
* **assumptions** (string): Assumptions.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.  
* **generatedBy** (PersonRef or SystemRef): Generator.

### **Relationships**

* **forStudy**: Study (0..1); Study.  
* **forSite**: Site (0..N); Sites.  
* **basedOn**: Enrollment (0..N); Historic enrollments.  
* **reportedIn**: Report (0..N); Reports.

### **Calls to Action**

* **Generate Forecast** (Operations): Generate.  
* **Update Assumptions** (Operations): Update.

## **70\. Budget Forecast (flagged missing in v0)**

A projection of spend over time against a Budget, including accruals, commitments, and holdbacks.  
***Editor note.** v0.2: introduced as a stub. Yellow TODO in v0; separates forward-looking forecast from Budget line-item plan.*

### **Attributes**

* **budgetForecastId** (string, IRI): Unique identifier.  
* **budgetId** (string, IRI): Parent budget.  
* **forecastHorizonStart** (date): Horizon start.  
* **forecastHorizonEnd** (date): Horizon end.  
* **accrualAmount** (decimal): Accrued.  
* **commitmentAmount** (decimal): Committed.  
* **holdbackAmount** (decimal): Holdback.  
* **forecastTotal** (decimal): Forecast total.  
* **currency** (string, ISO 4217): Currency.  
* **assumptions** (string): Assumptions.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **forBudget**: Budget (1); Parent budget.  
* **basedOn**: Payment (0..N); Historic payments.  
* **reportedIn**: Report (0..N); Reports.

### **Calls to Action**

* **Generate Budget Forecast** (Finance): Generate.  
* **Update Forecast** (Finance): Update.

## **71\. Interim Analysis (flagged missing in v0)**

A pre-specified or ad-hoc analysis of accumulating trial data before the final analysis, typically reviewed by a DSMB.  
***Editor note.** v0.2: introduced as a stub. Yellow TODO in v0; distinct from Endpoint analysis and from Report.*

### **Attributes**

* **interimAnalysisId** (string, IRI): Unique identifier.  
* **interimAnalysisName** (string): Display name.  
* **studyId** (string, IRI): Study.  
* **analysisType** (enum): efficacy, futility, safety, sample\_size\_reestimation, adaptation.  
* **triggerType** (enum): time\_based, event\_based, unplanned.  
* **triggerSpec** (string): Trigger specification.  
* **cutoffDate** (date): Data cutoff.  
* **plannedDecisionRules** (string): Pre-specified decision rules.  
* **actualDecision** (enum, optional): continue, stop\_for\_efficacy, stop\_for\_futility, stop\_for\_safety, modify.  
* **decisionRationale** (string, optional): Rationale.  
* **analysisStatus** (enum): planned, in\_progress, complete.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **forStudy**: Study (1); Study.  
* **analyzesEndpoint**: Endpoint (1..N); Endpoints analyzed.  
* **reviewedBy**: Oversight Body (1..N); DSMB.  
* **hasReport**: Report (1); Report.  
* **triggersAmendment**: Amendment (0..N); Resulting amendments.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Plan Interim Analysis** (Biostatistician): Plan.  
* **Conduct Interim Analysis** (Biostatistician): Conduct.  
* **Record Decision** (DSMB Chair): Record.

## **72\. Safety Signal (flagged missing in v0)**

A suspected or confirmed pattern of adverse events or lab abnormalities that may indicate a causal relationship with the Investigational Product.  
***Editor note.** v0.2: introduced as a stub. Yellow TODO in v0; distinct from AE and SAE.*

### **Attributes**

* **safetySignalId** (string, IRI): Unique identifier.  
* **signalTitle** (string): Title.  
* **signalDescription** (string): Description.  
* **signalSource** (enum): spontaneous, literature, analytical, dsmb, authority.  
* **severity** (enum): low, medium, high, critical.  
* **signalStatus** (enum): identified, under\_evaluation, validated, refuted, closed.  
* **identifiedAt** (datetime): Identified.  
* **closedAt** (datetime, optional): Closed.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **basedOn**: Adverse Event (1..N); Source AEs.  
* **basedOn**: Serious Adverse Event (0..N); Source SAEs.  
* **concernsIP**: Investigational Product (1); Target IP.  
* **reviewedBy**: Oversight Body (1..N); DSMB or similar.  
* **triggersAmendment**: Amendment (0..N); Resulting amendments.  
* **triggersSubmission**: Regulatory Submission (0..N); Resulting submissions.  
* **hasDocuments**: Document (1..N); Analyses, narratives.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Identify Signal** (Pharmacovigilance): Identify.  
* **Evaluate Signal** (Pharmacovigilance): Evaluate.  
* **Close Signal** (Pharmacovigilance): Close.

## **73\. Safety Report (flagged missing in v0)**

A periodic or expedited report summarizing safety data for a Study or an IP (DSUR, PBRER, IND Safety Report, Annual Safety Report).  
***Editor note.** v0.2: introduced as a stub. Separates periodic safety reports from the generic Report object.*

### **Attributes**

* **safetyReportId** (string, IRI): Unique identifier.  
* **reportType** (enum): dsur, pbrer, ind\_safety\_report, annual\_safety\_report, iciar, other.  
* **reportingPeriodStart** (date): Start.  
* **reportingPeriodEnd** (date): End.  
* **preparedByOrganizationId** (string, IRI): Preparer org.  
* **submittedToAuthorities** (list\[string\]): Authorities.  
* **reportStatus** (enum): in\_preparation, submitted, accepted, questioned.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **forStudy**: Study (0..N); Studies.  
* **forIP**: Investigational Product (0..1); IP.  
* **aggregatesAE**: Adverse Event (0..N); AEs.  
* **aggregatesSAE**: Serious Adverse Event (0..N); SAEs.  
* **aggregatesSignal**: Safety Signal (0..N); Signals.  
* **submittedIn**: Regulatory Submission (0..N); Submissions.  
* **reviewedBy**: Oversight Body (0..N); Oversight.  
* **hasDocuments**: Document (1..N); Report files.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Prepare Safety Report** (Pharmacovigilance): Prepare.  
* **Submit Safety Report** (Pharmacovigilance): Submit.

## **74\. Communication Log (flagged missing in v0)**

A record of communications between study parties (emails, calls, letters) relevant to compliance and essential documentation.  
***Editor note.** v0.2: introduced as a stub. Yellow TODO in v0; holds essential correspondence required in the eTMF.*

### **Attributes**

* **communicationLogId** (string, IRI): Unique identifier.  
* **subject** (string): Subject line.  
* **communicationType** (enum): email, phone\_call, letter, fax, meeting\_note, video\_call.  
* **direction** (enum): inbound, outbound, internal.  
* **fromPartyId** (string, IRI): From.  
* **toPartyIds** (list\[string, IRI\]): To.  
* **ccPartyIds** (list\[string, IRI\]): CC.  
* **occurredAt** (datetime): Time.  
* **summary** (string): Summary.  
* **containsPhi** (boolean): Contains PHI.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **scopedToStudy**: Study (0..1); Study.  
* **scopedToSite**: Site (0..1); Site.  
* **scopedToSubject**: Participant (Subject) (0..1); Subject.  
* **referencesPersons**: Person (0..N); Persons referenced.  
* **hasAttachments**: Document (0..N); Attachments.  
* **triggersActionItem**: Action Item (0..N); Action items.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Log Communication** (Coordinator): Log.  
* **Link Communication to Object** (Coordinator): Link.

## **75\. Study Timeline (flagged missing in v0)**

A canonical timeline of planned and actual dates for a Study (FPI, LPI, LPO, DBL, CSR).  
***Editor note.** v0.2: introduced as a stub. Yellow TODO in v0; aggregates Date and Milestone into a single timeline view.*

### **Attributes**

* **studyTimelineId** (string, IRI): Unique identifier.  
* **studyId** (string, IRI): Study.  
* **milestoneLabel** (enum): study\_start, fpi, lpi, lpo, dbl, csr, study\_end.  
* **plannedDate** (date): Planned.  
* **forecastDate** (date, optional): Forecast.  
* **actualDate** (date, optional): Actual.  
* **variance** (integer, computed): Days variance.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **forStudy**: Study (1); Study.  
* **realizedBy**: Milestone (0..1); Milestone.  
* **realizedBy**: Date (0..1); Date.  
* **reportedIn**: Report (0..N); Reports.

### **Calls to Action**

* **Update Timeline** (Study Manager): Update.  
* **Rebaseline Timeline** (Study Manager): Rebaseline.

## **76\. Study Performance Metric (flagged missing in v0)**

A KPI for a Study or a Site (cycle times, enrollment rate, query rate, protocol deviation rate, screen failure rate).  
***Editor note.** v0.2: introduced as a stub. Yellow TODO in v0; sibling of Data Quality Metric focused on operational performance.*

### **Attributes**

* **studyPerformanceMetricId** (string, IRI): Unique identifier.  
* **metricCode** (enum): siu\_cycle\_time, activation\_cycle\_time, enrollment\_rate, screen\_fail\_rate, deviation\_rate, query\_rate, sdv\_rate.  
* **scope** (enum): study, country, site.  
* **scopeRefId** (string, IRI): Scope reference.  
* **windowStart** (date): Window start.  
* **windowEnd** (date): Window end.  
* **value** (decimal): Value.  
* **unit** (string): Unit.  
* **thresholdLow** (decimal, optional): Low threshold.  
* **thresholdHigh** (decimal, optional): High threshold.  
* **breached** (boolean): Threshold breach.

### **Metadata**

* **computedAt** (datetime): Computation.  
* **computedBy** (SystemRef): Computing system.

### **Relationships**

* **scopedTo**: Study (0..1); Study.  
* **scopedTo**: Site (0..1); Site.  
* **mayTrigger**: Action Item (0..N); Action items.  
* **reportedIn**: Report (0..N); Reports.

### **Calls to Action**

* **Configure Metric** (Operations): Configure.  
* **Drill Into Metric** (Operations): Drill.

## **77\. Training Record (flagged missing in v0)**

A record of a Person completing a specific training (GCP, protocol, system UAT, safety reporting).  
***Editor note.** v0.2: introduced as a stub. Referenced by Site, Investigator, and Startup Package but absent as an object in v0.*

### **Attributes**

* **trainingRecordId** (string, IRI): Unique identifier.  
* **personId** (string, IRI): Trainee.  
* **trainingTitle** (string): Training title.  
* **trainingType** (enum): gcp, protocol, system, safety, privacy, device, other.  
* **version** (string): Training version.  
* **completedAt** (date): Completion.  
* **expiresAt** (date, optional): Expiry.  
* **certificateReference** (string, IRI, optional): Certificate.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **completedBy**: Person (1); Trainee.  
* **forStudy**: Study (0..1); Study.  
* **forSite**: Site (0..1); Site.  
* **forSystem**: System (0..1); System.  
* **hasDocuments**: Document (1..N); Certificate files.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Record Training** (Training Coordinator): Record.  
* **Refresh Training** (Training Coordinator): Refresh.

## **78\. Storage Location (flagged missing in v0)**

A physical or logical location where Samples, Investigational Products, or Equipment are stored with environmental controls.  
***Editor note.** v0.2: introduced as a stub. Needed for biobanking, drug accountability, and cold-chain compliance.*

### **Attributes**

* **storageLocationId** (string, IRI): Unique identifier.  
* **siteId** (string, IRI): Host site.  
* **locationName** (string): Display name.  
* **storageType** (enum): freezer, refrigerator, room\_temperature, controlled\_temperature, cryogenic, pharmacy\_vault, biobank.  
* **targetTemperatureC** (decimal, optional): Target temperature.  
* **toleranceTemperatureC** (decimal, optional): Tolerance.  
* **capacityUnits** (integer): Capacity.  
* **usedUnits** (integer): Used.  
* **monitoringSystemId** (string, IRI, optional): Monitoring system.  
* **locationStatus** (enum): in\_service, out\_of\_service, retired.

### **Metadata**

* **createdAt** (datetime): Creation.  
* **modifiedAt** (datetime): Modification.

### **Relationships**

* **atSite**: Site (1); Host site.  
* **stores**: Sample (0..N); Samples stored.  
* **stores**: Investigational Product (0..N); IP stored.  
* **stores**: Equipment (0..N); Equipment stored.  
* **monitoredBy**: System (0..1); Monitoring system.  
* **hasLog**: Log (0..N); Temperature logs.  
* **hasAuditTrail**: Audit Trail Entry (1..N); Trail.

### **Calls to Action**

* **Register Storage Location** (Coordinator): Register.  
* **Take Out of Service** (Coordinator): Out of service.

# **Section 4\. Cross-cutting relationships**

The map is held together by a small set of spines and ribs. The central spine is the participant journey: Sponsor commissions a Study, the Study is specified by a Protocol, the Protocol defines a Schedule of Assessments with Visits and Assessments, Sites conduct the Study, Persons are delegated to tasks at Sites, Participants (Subjects) consent and enrol, Visits execute, CRFs and Lab Results and Samples and Questionnaires capture data, Adverse Events and Serious Adverse Events and Deviations and Discrepancies arise along the way, and Reports, Interim Analyses, and the final Endpoint analysis close the loop.  
A second spine runs through governance and compliance: an Oversight Body (IRB, IEC, DSMB, IBC) reviews the Protocol, reviews Amendments, and issues Recommendations and Decisions. Audits and Monitoring Visits generate Findings that trigger CAPAs. Risk Assessments drive the cadence of Monitoring Visits. Audit Trail Entries record every mutation across systems. Regulatory Submissions carry the Protocol, the Amendments, and the Safety Reports to Regulatory Authorities in each Country. Communication Logs preserve the correspondence.  
A third spine runs through resourcing and delivery: Contracts govern the relationships between Sponsor, Sites, and vendor Organizations. Budgets allocate the money. Payments disburse it. Services (data management, monitoring, central lab, central reading, IRT, eCOA) are delivered via Systems configured per Study or per Site. Credentials grant Persons access to Systems with the right User Role and the right scope. Equipment and Investigational Product and Investigational Device and Samples move through Shipments between storage locations. Training Records keep Person competencies current.  
Two horizontal threads weave across these spines. Every object carries an Audit Trail Entry stream, so that every mutation can be attributed and reviewed. Every object that represents clinical data or a clinical decision carries a Consent envelope: Informed Consent governs what Participants agree to, and every Sample, Lab Result, CRF, Questionnaire, and onward data use must fall inside that envelope. The NGSI-LD translation should surface both of these threads as first-class Properties, not as incidental metadata.  
A final note on boundaries. Person and User Role are distinct from Person Role: Person is the human being, Person Role is the clinical or operational role played on a Study or Site, and User Role is the permission set inside a System. Investigator is proposed as a specialization of Person to carry the regulatory history (licenses, 1572, FCOI disclosures, debarment status) that Person cannot cleanly hold. Participant (Subject) is treated as an entity, while Enrollment is treated as the event that binds a Subject to a Study and a Site at a point in time.

# **Section 5\. Standards mapping notes**

The lines below summarise the primary cross-walk each object should follow when projected into FHIR, USDM (CDISC), CDASH, and ODM/XML. They are one-liners, sufficient for the translator to start; full mapping tables belong in the downstream ontology package.

* **Site.** FHIR: Organization (type \= healthcare provider) with Location child. USDM: StudySite. CDASH: DM (SITEID, SITENAME, COUNTRY). ODM/XML: ClinicalData/StudyEventData scoped by SiteRef.  
* **Sponsor.** FHIR: Organization. USDM: Sponsor (Study.sponsor). CDASH: Not a CDASH domain; referenced in DM metadata. ODM/XML: ODM Study metadata (Study/GlobalVariables/StudyName).  
* **Tag.** FHIR: Meta.tag or Coding. USDM: Study keywords (Study.keywords). CDASH: N/A. ODM/XML: ODM StudyEventDef aliases or custom CodeList.  
* **Study.** FHIR: ResearchStudy. USDM: Study. CDASH: DM, TS (Trial Summary). ODM/XML: Study element with GlobalVariables.  
* **Arm.** FHIR: ResearchStudy.arm. USDM: StudyArm. CDASH: DM.ARM. ODM/XML: CodeList for treatment arms.  
* **Visit.** FHIR: Encounter (class \= visit). USDM: ScheduledActivityInstance / ScheduledVisit. CDASH: SV (Subject Visits). ODM/XML: StudyEventDef / StudyEventData.  
* **Task.** FHIR: Task. USDM: Activity / ScheduledActivity. CDASH: N/A (operational). ODM/XML: N/A.  
* **Participant (Subject).** FHIR: Patient and ResearchSubject. USDM: StudySubject. CDASH: DM (USUBJID, SUBJID). ODM/XML: SubjectData @SubjectKey.  
* **Discrepancy (Query).** FHIR: Task or Communication. USDM: Query (DDF data management). CDASH: Query markers in CDASH. ODM/XML: ODM Audit Trail annotation.  
* **Deviation.** FHIR: DetectedIssue. USDM: ProtocolDeviation. CDASH: DV (Protocol Deviations). ODM/XML: AuditRecord Reason \= protocol deviation.  
* **Screen Fail.** FHIR: Encounter.status \= cancelled or ResearchSubject.status \= screen-failed. USDM: StudySubject.status \= screen-failed. CDASH: DM.DSDECOD \= SCREEN FAILURE. ODM/XML: SubjectData disposition record.  
* **Person.** FHIR: Practitioner or RelatedPerson. USDM: Person (Investigator, Site Staff). CDASH: Not a CDASH domain; referenced in DM. ODM/XML: ODM SignatureDef / UserRef.  
* **Person Role.** FHIR: PractitionerRole. USDM: Investigator / StudySiteStaffRole. CDASH: N/A. ODM/XML: ODM Signatures and Roles.  
* **CRF.** FHIR: QuestionnaireResponse or Observation. USDM: StudyDataCollection. CDASH: Aligned to CDASH domain (DM, AE, CM, MH, VS, etc.). ODM/XML: FormData / ItemGroupData / ItemData.  
* **Document.** FHIR: DocumentReference. USDM: TMFDocument. CDASH: N/A. ODM/XML: Referenced via annotations or external URIs.  
* **Adverse Event.** FHIR: AdverseEvent. USDM: AdverseEvent. CDASH: AE (Adverse Events). ODM/XML: ClinicalData ItemGroupData for AE domain.  
* **Informed Consent.** FHIR: Consent. USDM: InformedConsent. CDASH: DS (Disposition) for consent event; protocol-level otherwise. ODM/XML: SubjectData event with signature.  
* **Action Item.** FHIR: Task. USDM: ProcessActivity. CDASH: N/A. ODM/XML: N/A.  
* **Milestone.** FHIR: Task with focus \+ ResearchStudy reference. USDM: Milestone. CDASH: N/A. ODM/XML: N/A.  
* **Enrollment.** FHIR: ResearchSubject.progress (state change). USDM: StudySubject.status \= enrolled. CDASH: DS / DM disposition. ODM/XML: SubjectData disposition record.  
* **Payment.** FHIR: ChargeItem or Invoice. USDM: FinancialTransaction (DDF financial). CDASH: N/A. ODM/XML: N/A.  
* **Protocol.** FHIR: PlanDefinition. USDM: Protocol (DDF). CDASH: Source of CDASH design spec. ODM/XML: MetaDataVersion.  
* **Investigational Product.** FHIR: MedicationKnowledge / Substance. USDM: InvestigationalIntervention. CDASH: EX (Exposure), CM cross-reference. ODM/XML: ItemGroupData for EX domain.  
* **Investigational Device.** FHIR: DeviceDefinition. USDM: InvestigationalIntervention (device). CDASH: EX or DV (device exposure). ODM/XML: ItemGroupData for device exposure.  
* **Plan.** FHIR: PlanDefinition. USDM: StatisticalAnalysisPlan / DataManagementPlan. CDASH: N/A. ODM/XML: N/A.  
* **Oversight Body.** FHIR: Organization (type \= ethics committee) or Group. USDM: OversightBody. CDASH: N/A. ODM/XML: ODM SignatureDef for approvals.  
* **System.** FHIR: Device (software) or Endpoint. USDM: StudySystem. CDASH: N/A. ODM/XML: ODM Admin Metadata.  
* **System Configuration.** FHIR: Device.version \+ Parameter. USDM: SystemConfiguration. CDASH: N/A. ODM/XML: MetaDataVersion revision.  
* **Service.** FHIR: HealthcareService or Contract.service. USDM: StudyService. CDASH: N/A. ODM/XML: N/A.  
* **Service Configuration.** FHIR: Contract.term or Parameter. USDM: ServiceConfiguration. CDASH: N/A. ODM/XML: N/A.  
* **Study Startup Package.** FHIR: Task (group) \+ PlanDefinition. USDM: SiteActivationPackage. CDASH: N/A (operational). ODM/XML: N/A.  
* **Budget.** FHIR: ChargeItemDefinition \+ Invoice. USDM: Budget (DDF financial). CDASH: N/A. ODM/XML: N/A.  
* **Contract.** FHIR: Contract. USDM: LegalAgreement. CDASH: N/A. ODM/XML: N/A.  
* **Schedule of Assessments.** FHIR: PlanDefinition.action. USDM: ScheduleOfAssessments. CDASH: Source of Visit and CDASH domain schedule. ODM/XML: MetaDataVersion StudyEventDef \+ ItemGroupRef.  
* **Endpoint.** FHIR: ResearchStudy.objective \+ outcomeMeasure. USDM: Endpoint (DDF). CDASH: Derived from CDASH \+ SDTM supplemental. ODM/XML: Analysis outputs outside ODM.  
* **Lab Results.** FHIR: Observation (laboratory). USDM: LabResult. CDASH: LB (Laboratory). ODM/XML: ItemGroupData for LB.  
* **Log.** FHIR: List or Provenance. USDM: Log. CDASH: N/A. ODM/XML: ODM ClinicalData (log-form).  
* **Credential.** FHIR: Practitioner.qualification or Device token. USDM: UserAccess. CDASH: N/A. ODM/XML: ODM User / SignatureDef.  
* **Amendment.** FHIR: PlanDefinition (version) or RequestGroup. USDM: Amendment. CDASH: N/A. ODM/XML: MetaDataVersion amendments.  
* **Regulatory Submission.** FHIR: Task or DocumentReference bundle. USDM: RegulatoryPackage. CDASH: N/A. ODM/XML: N/A.  
* **Audit.** FHIR: AuditEvent (human engagement) or Task. USDM: Audit. CDASH: N/A. ODM/XML: AuditRecord for conduct.  
* **Report.** FHIR: DocumentReference (type \= report) or Composition. USDM: Report. CDASH: Listings, tabulations, SDTM/ADaM outputs. ODM/XML: Analysis outputs outside ODM.  
* **Shipment.** FHIR: SupplyDelivery. USDM: Shipment. CDASH: N/A. ODM/XML: N/A.  
* **Questionnaire.** FHIR: Questionnaire / QuestionnaireResponse. USDM: COA (Clinical Outcome Assessment). CDASH: QS (Questionnaires), CO (COA), FA (Findings About). ODM/XML: FormDef / ItemGroupData for QS.  
* **Other Clinical Event.** FHIR: ClinicalImpression or Observation. USDM: ClinicalEvent. CDASH: CE (Clinical Events). ODM/XML: ItemGroupData for CE.  
* **CAPA.** FHIR: DetectedIssue.mitigation or Task. USDM: CAPA. CDASH: N/A. ODM/XML: N/A.  
* **Date.** FHIR: Extension or Observation (effectiveDateTime) on parent. USDM: KeyDate (DDF). CDASH: DM date fields and DS.DSSTDTC. ODM/XML: Item values carrying dates.  
* **Sample.** FHIR: Specimen. USDM: BiologicalSample. CDASH: Not a CDASH domain; referenced by LB/PC/PP. ODM/XML: Sample IDs within LB/PC ItemGroupData.  
* **Equipment.** FHIR: Device. USDM: Equipment. CDASH: Not a CDASH domain; referenced via VS/PE. ODM/XML: Referenced via annotations.  
* **Data Transfer.** FHIR: Task \+ DocumentReference. USDM: DataTransfer. CDASH: N/A. ODM/XML: ODM transport envelope metadata.  
* **User Role.** FHIR: Practitioner.qualification or SecurityRole. USDM: UserRole. CDASH: N/A. ODM/XML: ODM User/Role.  
* **Inclusion Criteria.** FHIR: PlanDefinition.eligibility (inclusion). USDM: InclusionCriterion. CDASH: Referenced by DM for enrollment. ODM/XML: MetaDataVersion StudyParameters.  
* **Exclusion Criteria.** FHIR: PlanDefinition.eligibility (exclusion). USDM: ExclusionCriterion. CDASH: Referenced by DS.DSDECOD for screen failures. ODM/XML: MetaDataVersion StudyParameters.  
* **Monitoring Visit.** FHIR: Encounter (class \= monitoring) or Task. USDM: MonitoringVisit. CDASH: N/A (operational). ODM/XML: ODM Audit-only.  
* **Serious Adverse Event.** FHIR: AdverseEvent (seriousness set). USDM: SeriousAdverseEvent. CDASH: AE.AESER set. ODM/XML: ItemGroupData AE with seriousness items.  
* **Region.** FHIR: Location (region) or Organization hierarchy. USDM: Region (geographic grouping). CDASH: N/A. ODM/XML: N/A.  
* **Country.** FHIR: Location (country) via ISO code. USDM: Country. CDASH: DM.COUNTRY. ODM/XML: StudyParameters Country.  
* **Site Network.** FHIR: Organization (type \= network) with part-of hierarchy. USDM: SiteNetwork. CDASH: N/A. ODM/XML: N/A.  
* **Therapeutic Area.** FHIR: Coding using SNOMED CT or ICD-10 \+ Category. USDM: TherapeuticArea. CDASH: Not a CDASH domain; referenced in TS. ODM/XML: ODM CodeList or StudyParameter.  
* **Regulatory Authority.** FHIR: Organization (type \= regulatory authority). USDM: RegulatoryAuthority. CDASH: N/A. ODM/XML: N/A.  
* **Investigator.** FHIR: Practitioner with role and qualifications. USDM: Investigator. CDASH: Referenced via DM site fields. ODM/XML: ODM SignatureDef / UserRef.  
* **Assessment.** FHIR: PlanDefinition.action or ActivityDefinition. USDM: Activity / Assessment. CDASH: Source of CDASH items per domain. ODM/XML: ItemGroupDef.  
* **Audit Trail Entry.** FHIR: AuditEvent. USDM: AuditRecord. CDASH: N/A. ODM/XML: AuditRecord within ClinicalData.  
* **Finding.** FHIR: DetectedIssue. USDM: Finding. CDASH: N/A. ODM/XML: Audit annotations.  
* **Concomitant Medication.** FHIR: MedicationStatement. USDM: ConcomitantMedication. CDASH: CM (Concomitant Medications). ODM/XML: ItemGroupData for CM.  
* **Medical History.** FHIR: Condition. USDM: MedicalHistory. CDASH: MH (Medical History). ODM/XML: ItemGroupData for MH.  
* **Risk Assessment.** FHIR: RiskAssessment. USDM: RiskAssessment. CDASH: N/A (RBQM). ODM/XML: N/A.  
* **Data Quality Metric.** FHIR: Measure \+ MeasureReport. USDM: DataQualityMetric. CDASH: N/A (operational). ODM/XML: N/A.  
* **Enrollment Forecast.** FHIR: MeasureReport or Goal. USDM: EnrollmentForecast. CDASH: N/A. ODM/XML: N/A.  
* **Budget Forecast.** FHIR: Invoice projection or ChargeItemDefinition. USDM: BudgetForecast. CDASH: N/A. ODM/XML: N/A.  
* **Interim Analysis.** FHIR: Composition \+ Observation bundle. USDM: InterimAnalysis. CDASH: Derived from ADaM subsets. ODM/XML: Analysis outputs outside ODM.  
* **Safety Signal.** FHIR: DetectedIssue or Flag. USDM: SafetySignal. CDASH: N/A (pharmacovigilance). ODM/XML: N/A.  
* **Safety Report.** FHIR: Composition (type \= safety report) or DocumentReference. USDM: PeriodicSafetyReport. CDASH: N/A (pharmacovigilance). ODM/XML: N/A.  
* **Communication Log.** FHIR: Communication \+ DocumentReference. USDM: CommunicationRecord. CDASH: N/A. ODM/XML: N/A.  
* **Study Timeline.** FHIR: PlanDefinition.action with timing or CarePlan. USDM: StudyTimeline. CDASH: N/A. ODM/XML: N/A.  
* **Study Performance Metric.** FHIR: Measure \+ MeasureReport. USDM: StudyPerformanceMetric. CDASH: N/A. ODM/XML: N/A.  
* **Training Record.** FHIR: DocumentReference or Practitioner.qualification. USDM: TrainingRecord. CDASH: N/A. ODM/XML: ODM Signatures.  
* **Storage Location.** FHIR: Location (type \= storage). USDM: StorageLocation. CDASH: N/A. ODM/XML: N/A.

# **Section 6\. Change log (v0 to v0.2)**

The following diff lists material changes from v0 to v0.2. Editorial cleanups, capitalisation harmonisation, and trivial wording fixes are not enumerated.

## **Site (object 1\)**

* **Site existence.** *Before:* TODO placeholder, no attributes, no relationships, no CTAs. *After:* Fully specified across nine attribute categories (core identity; location and jurisdiction; facility and capability; operational posture; quality and compliance; staffing; contracting and finance; technology and integrations; patient access). Relationships now include Investigator, Therapeutic Area, Oversight Body, Master Service Agreement, parent Network, and Region. CTAs cover startup, activation, hold, close, audit, and reporting workflows.  
* **Site identifiers.** *Before:* No identifier model. *After:* siteId (NGSI-LD URI), siteNumber (unique within Study), legalName, ctgovFacilityId, fhirOrganizationId.  
* **Site DCT readiness.** *Before:* Not addressed. *After:* decentralizedTrialReadiness enum and homeHealthVendor list added under Operational posture.

## **Sponsor (object 2\)**

* **Sponsor scope.** *Before:* Sponsor implied as a single org. *After:* sponsorRole enum (sponsor, co-sponsor, cro, vendor) and parentOrganizationId added; relationship to Region and Country surfaced.

## **Tag (object 3\)**

* **Tag taxonomy.** *Before:* Free-text tags. *After:* tagDomain enum (operational, clinical, regulatory, financial) and codingSystem reference (SNOMED, MeSH, custom) added.

## **Study (object 4\)**

* **Study identifiers.** *Before:* No global identifier strategy. *After:* Added clinicalTrialsGovId, eudraCtNumber, irasNumber, jrctNumber, sponsorProtocolId, fhirResearchStudyId.  
* **Study lifecycle.** *Before:* Single status field. *After:* studyStatus enum aligned with FHIR ResearchStudy.status; phaseStudyStatus carried separately.

## **Arm (object 5\)**

* **Arm semantics.** *Before:* Treatment arm only. *After:* armType enum (treatment, comparator, placebo, control, observational); blindingStatus enum added.

## **Visit (object 6\)**

* **Visit modality.** *Before:* On-site implied. *After:* visitMode enum (on\_site, televisit, home\_health, hybrid) and modalityRationale added.

## **Task (object 7\)**

* **Task scope.** *Before:* Operational task only. *After:* taskCategory enum to disambiguate clinical vs operational vs regulatory; relationship to Action Item clarified.

## **Participant (Subject) (object 8\)**

* **Subject identifiers.** *Before:* Single id. *After:* subjectId (urn) plus screeningNumber, randomizationNumber, usubjid (CDISC), and fhirResearchSubjectId.  
* **Subject status.** *Before:* Status string. *After:* subjectStatus enum aligned with ResearchSubject.status; consentStatus tracked separately.

## **Discrepancy (Query) (object 9\)**

* **Query workflow.** *Before:* Open or closed. *After:* queryStatus enum (open, answered, in\_review, closed\_resolved, closed\_unresolved); queryAgeing computed metadata added.

## **Deviation (object 10\)**

* **Deviation classification.** *Before:* Free-text severity. *After:* deviationSeverity enum (minor, major, critical) and deviationCategory enum aligned with ICH E3 Section 10\.

## **Screen Fail (object 11\)**

* **Screen fail rationale.** *Before:* Free-text reason. *After:* screenFailReasonCode aligned with Exclusion Criterion id; rescreeningEligible boolean added.

## **Person (object 12\)**

* **Person scope.** *Before:* Single Person object. *After:* Investigator subtype proposed (object 61\) for licensure and FCOI fields; Person carries identity and contact only.

## **Person Role (object 13\)**

* **Role separation.** *Before:* Single Role object. *After:* Person Role (clinical) and User Role (system permission) explicitly separated; mapping relation added.

## **CRF (object 14\)**

* **CRF versioning.** *Before:* Implicit version. *After:* crfVersion (semver) and crfStatus (draft, active, locked, superseded) added; relationship to Schedule of Assessments surfaced.

## **Document (object 15\)**

* **Document classification.** *Before:* Free-text type. *After:* documentType enum aligned with TMF Reference Model zones; eTMFLocation reference added.

## **Adverse Event (object 16\)**

* **AE coding.** *Before:* Free-text term. *After:* meddraCode (PT, LLT, SOC) added; specialization to Serious Adverse Event made explicit.  
* **AE causality.** *Before:* Single causality field. *After:* causalityAssessmentByInvestigator and causalityAssessmentBySponsor separated; expectedness enum added.

## **Informed Consent (object 17\)**

* **Consent scope.** *Before:* Single consent record. *After:* consentScope sub-properties for biobanking, future research, optional sub-studies; reconsentRequiredAt and reconsentReason added.

## **Action Item (object 18\)**

* **Owner accountability.** *Before:* Free-text owner. *After:* ownerPersonId reference; ownerOrganizationId fallback; dueDate and escalationLevel added.

## **Milestone (object 19\)**

* **Milestone semantics.** *Before:* Generic milestone. *After:* milestoneCategory enum (study, site, subject, regulatory, financial); plannedDate, forecastDate, actualDate separated.

## **Enrollment (object 20\)**

* **Enrollment as event.** *Before:* Conflated with Subject status. *After:* Enrollment treated as an event (timestamped state change) distinct from Participant entity; relationship to Date and to Arm randomization added.

## **Payment (object 21\)**

* **Payment triggers.** *Before:* Manual. *After:* paymentTriggerType enum (per\_visit, per\_procedure, per\_milestone, per\_screening, holdback\_release); reconciliationOutcome enum added.

## **Protocol (object 22\)**

* **Protocol versioning.** *Before:* Single version field. *After:* protocolVersion (semver), protocolStatus (draft, in\_review, approved, amended, superseded), and effectiveDates added; relationship to Plan and Schedule of Assessments surfaced.

## **Investigational Product (object 23\)**

* **IP classification.** *Before:* Generic. *After:* ipModality enum (small\_molecule, biologic, cell\_therapy, gene\_therapy, radioligand, vaccine); blinded boolean and labelLanguage list added.

## **Investigational Device (object 24\)**

* **Device existence.** *Before:* Listed in v0 relationships but absent from v0 master object index. *After:* Promoted to a first-class catalog entry (object 24); UDI, deviceCategory, riskClass, sterilizationMethod added.

## **Plan (object 25\)**

* **Plan ambiguity.** *Before:* Single Plan object. *After:* planType enum (sap, dmp, mp, recruitment\_plan, communication\_plan, risk\_plan); relationship to Endpoint and Interim Analysis surfaced.

## **Oversight Body (object 26\)**

* **Body taxonomy.** *Before:* Generic body. *After:* oversightBodyType enum (irb, iec, dsmb, ibc, scientific\_review\_board); centralVsLocal flag and approvalAuthority scope added.

## **System and System Configuration (objects 27 and 28\)**

* **System vs Configuration.** *Before:* Single System object. *After:* System Configuration broken out as a sibling object so that one System can hold many study-specific or site-specific Configurations with independent validation lifecycles.

## **Service and Service Configuration (objects 29 and 30\)**

* **Service vs Configuration.** *Before:* Service implicit in System. *After:* Service modeled separately to capture vendor-delivered services that may or may not run on a System; Service Configuration carries study-specific service parameters.

## **Study Startup Package (object 31\)**

* **Startup component checklist.** *Before:* Implicit checklist. *After:* Five explicit component statuses (regulatory, contract, training, supplies, IT) and cycleTimeDays computed metric added.

## **Budget (object 32\)**

* **Budget scope.** *Before:* Study-level only. *After:* scope enum (study, site, service, sponsor); planned, forecast, and actual totals separated; relationship to Budget Forecast (flagged) added.

## **Contract (object 33\)**

* **Contract type.** *Before:* Generic contract. *After:* contractType enum (cta, msa, work\_order, change\_order, nda, dpa, vendor); executionDate and effectiveDates separated; relationship to Budget added.

## **Schedule of Assessments (object 34\)**

* **SOA versioning.** *Before:* Implicit. *After:* SOA versioning aligned with Amendment; relationship to Assessment object (flagged missing) introduced.

## **Endpoint (object 35\)**

* **Endpoint hierarchy.** *Before:* Single Endpoint object. *After:* endpointType enum (primary, secondary, exploratory, safety, pk, pd, biomarker); estimand and analysisPopulation fields added; relationship to Interim Analysis (flagged) added.

## **Lab Results (object 36\)**

* **Lab grain.** *Before:* One record per lab order. *After:* Lab Results modeled at one record per analyte; LOINC and UCUM codes added; abnormalFlag and clinicalSignificance separated.

## **Log (object 37\)**

* **Log granularity.** *Before:* Log \= entries. *After:* Log treated as an aggregate; entries split out as Log Entry (flagged missing) so that audit trail and visibility are clean.

## **Credential (object 38\)**

* **Credential lifecycle.** *Before:* Permission grant only. *After:* expiresAt, lastRotatedAt, mfaEnabled, and revocation lifecycle added; scope to Study or Site supported.

## **Amendment (object 39\)**

* **Amendment scope.** *Before:* Protocol amendments only. *After:* parentObjectType enum allows Amendment to span Protocol, Contract, Budget, SOA, Informed Consent, and Plan; triggersReconsent and triggersResubmission flags added.

## **Regulatory Submission (object 40\)**

* **Submission types.** *Before:* Free-text type. *After:* submissionType enum (ind, cta, nda, bla, ide, irb, ec, annual\_report, safety\_report); eCTD module references list added.

## **Audit (object 41\)**

* **Audit overload.** *Before:* Audit and audit trail conflated. *After:* Audit (the engagement) separated from Audit Trail Entry (the system log, flagged as object 63); finding counts (critical, major, minor) added.

## **Report (object 42\)**

* **Report types.** *Before:* Free-text type. *After:* reportType enum (csr, dsur, psur, monitoring\_report, site\_performance, enrollment, safety, data\_quality, listing, dashboard, adhoc); dashboards distinguished from generated reports.

## **Shipment (object 43\)**

* **Shipment scope.** *Before:* IP shipments only. *After:* shipmentType enum extended to handle Sample, Device, Equipment, and Supplies; chain of custody and temperature excursion tracking added.

## **Questionnaire (object 44\)**

* **Questionnaire taxonomy.** *Before:* PRO only implied. *After:* questionnaireType enum (pro, clinro, obsro, perfo, qol, symptom\_diary, safety) aligned with COA taxonomy; scoringAlgorithm and licensingTerms added.

## **Other Clinical Event (object 45\)**

* **Boundary clarification.** *Before:* Boundary with AE unclear. *After:* eventCategory enum and reportableToSponsor flag added; explicit non-overlap with AE, ConMed, and Medical History noted.

## **CAPA (object 46\)**

* **CAPA structure.** *Before:* Single description field. *After:* rootCause separated from correctiveAction and preventiveAction; effectivenessCheckDate and outcome added.

## **Date (object 47\)**

* **Date as object.** *Before:* Loose dates. *After:* dateLabel enum standardised across consent, screening, randomization, first dose, last dose, end of treatment, end of study, withdrawal, screen fail, LTFU, death; effectiveStatusAfter field added.

## **Sample (object 48\)**

* **Sample lifecycle.** *Before:* Collected only. *After:* sampleStatus enum (collected, in\_transit, received, processed, analyzed, depleted, destroyed); biobankRetained and biobankConsentScope added; relationship to Storage Location (flagged) introduced.

## **Equipment (object 49\)**

* **Calibration tracking.** *Before:* Not addressed. *After:* calibrationCadenceDays, lastCalibrationDate, nextCalibrationDate added; equipmentStatus enum added.

## **Data Transfer (object 50\)**

* **Data Transfer existence.** *Before:* Implicit between Systems. *After:* Promoted to first-class object with DTA reference, schema mapping, reconciliation outcome, and relationship to Service.

## **User Role (object 51\)**

* **User Role separation.** *Before:* Conflated with Person Role. *After:* User Role (system permission) modeled distinct from Person Role (clinical role); permission scopes and inheritance added; mapping relation between the two.

## **Inclusion and Exclusion Criteria (objects 52 and 53\)**

* **Eligibility split.** *Before:* Single Eligibility object. *After:* Inclusion Criteria and Exclusion Criteria modeled as separate objects to align with FHIR PlanDefinition.eligibility and to support Screen Fail tracking.

## **Monitoring Visit (object 54\)**

* **Monitoring modality.** *Before:* On-site only implied. *After:* visitMode enum (on\_site, remote, central, hybrid); riskBasedTrigger field added; relationships to Finding and CAPA surfaced.

## **Serious Adverse Event (object 55\)**

* **SAE specialization.** *Before:* Treated as separate from AE. *After:* Modeled as a specialization of Adverse Event; six seriousness criteria flags broken out; expedited reporting deadline tracked.

## **Flagged missing objects (objects 56 through 78\)**

* **Region.** *Before:* Implied by Site address. *After:* Stub introduced; needs full attribute and relationship specification before NGSI-LD translation.  
* **Country.** *Before:* Free-text country code. *After:* Stub introduced with regulatory authority and privacy regime fields; referenced by Site, Submission, and Region.  
* **Site Network.** *Before:* Implied by parent network field. *After:* Stub introduced; SMOs and integrated health systems modelled as Networks owning Sites.  
* **Therapeutic Area.** *Before:* Free-text classification. *After:* Stub introduced with ICD-10 and SNOMED code mappings; classifies Study, Site, and Investigator.  
* **Regulatory Authority.** *Before:* Free-text authority name. *After:* Stub introduced; referenced by Country and Submission.  
* **Investigator.** *Before:* Folded into Person. *After:* Stub introduced as a specialization of Person; carries license, 1572, FCOI disclosure, debarment status, and CV currency.  
* **Assessment.** *Before:* Folded into CRF. *After:* Stub introduced; defined by Schedule of Assessments and produces CRF, Lab Result, Sample, or Questionnaire.  
* **Audit Trail Entry.** *Before:* Audit overload. *After:* Stub introduced for the system-generated trail; separates from human Audit engagement.  
* **Finding.** *Before:* Implicit in Audit narratives. *After:* Stub introduced with severity and category enums; triggers CAPA.  
* **Concomitant Medication.** *Before:* Yellow TODO in v0. *After:* Stub introduced with ATC and RxNorm codes; relates to AE causality.  
* **Medical History.** *Before:* Yellow TODO in v0. *After:* Stub introduced with MedDRA and SNOMED codes; relates to eligibility and AE causality.  
* **Risk Assessment.** *Before:* Yellow TODO in v0. *After:* Stub introduced; framework enum (ich\_e6\_r3\_rbqm, e8\_r1, gvp); drives monitoring strategy.  
* **Data Quality Metric.** *Before:* Yellow TODO in v0. *After:* Stub introduced for RBQM dashboards; threshold breach triggers Action Item.  
* **Enrollment Forecast.** *Before:* Yellow TODO in v0. *After:* Stub introduced with methodology enum and confidence bounds; sibling of Enrollment event and Study Performance Metric.  
* **Budget Forecast.** *Before:* Yellow TODO in v0. *After:* Stub introduced with accrual, commitment, holdback fields; sibling of Budget plan.  
* **Interim Analysis.** *Before:* Yellow TODO in v0. *After:* Stub introduced with analysisType and decision enums; reviewed by DSMB.  
* **Safety Signal.** *Before:* Yellow TODO in v0. *After:* Stub introduced; distinguished from AE and SAE; reviewed by Oversight Body.  
* **Safety Report.** *Before:* Implied in Document. *After:* Stub introduced; periodic reports (DSUR, PBRER, IND Safety Report) modeled as a distinct object.  
* **Communication Log.** *Before:* Yellow TODO in v0. *After:* Stub introduced; preserves essential correspondence required in eTMF.  
* **Study Timeline.** *Before:* Yellow TODO in v0. *After:* Stub introduced; canonical FPI/LPI/LPO/DBL/CSR timeline aggregating Date and Milestone.  
* **Study Performance Metric.** *Before:* Yellow TODO in v0. *After:* Stub introduced; sibling of Data Quality Metric focused on operational KPIs.  
* **Training Record.** *Before:* Implied by Document. *After:* Stub introduced; required for Investigator and Site staff currency tracking.  
* **Storage Location.** *Before:* Implied by Sample storage. *After:* Stub introduced; required for biobanking, drug accountability, and cold-chain compliance.

# **Section 7\. Appendix: V0 source transcription**

The text below is a faithful transcription of the v0 source PDF, included so that reviewers can compare v0.2 against the original. Yellow highlights and TODO markers in v0 are retained verbatim.  
OOUX: Object Oriented UX for clinical  
trials \- latest  
The goal of this document is to capture the different elements in Nucleus and understand how  
they need to interact with each other. More info on OOUX.

Object list:  
   1\. Sponsor  
   2\. Tag  
   3\. Study  
   4\. Arm  
   5\. Site  
   6\. Visit  
   7\. Task  
   8\. Participant (Subject)  
   9\. Discrepancy (Query)  
   10.Deviation  
   11.Screen Fail  
   12.Person  
   13.Person Role  
   14.CRF (Case Report Form)  
   15.Document  
   16.Adverse Event  
   17.Informed Consent  
   18.Action Item  
   19.Milestone  
   20.Enrollment  
   21.Payment  
   22.Protocol  
   23.Investigational Product  
   24.Plan  
   25.Oversight Body  
   26.System  
   27.System Configuration  
   28.Service  
   29.Service Configuration  
   30.Study Startup Package  
   31.Budget  
   32.Contract  
  33.Schedule of Assessments (SOA)  
  34.Endpoint  
  35.Lab Results  
  36.Log  
  37.Credential  
  38.Amendment  
  39.Regulatory Submission  
  40.Audit  
  41.Report  
  42.Shipment  
  43.Questionnaire (COA/PRO)  
  44.Other Clinical Event  
  45.CAPA  
  46.Date something else I  
  47.Sample  
  48.Equipment  
  49.Data Transfer  
  50.User Role  
  51.Inclusion Criteria  
  52.Exclusion Criteria  
  53.Monitoring Visit  
  54.Serious Adverse Events (SAEs)  
  55.Region  
  56.Study Timeline  
  57.Risk Assessment  
  58.Data Quality Metrics  
  59.Enrollment Forecast  
  60.Budget Forecast  
  61.Interim Analysis  
  62.Communication Log  
  63.Study Performance Metrics  
  64.Safety Signal  
  65.Concomitant Medication  
  66.Medical History

Object relationships:  
  1\. Sponsor:  
      The Sponsor object represents the organization responsible for initiating, managing,  
      and/or financing the clinical trial.  
         a. 1-Many Study  
         b. 1-Many Person (employees, contractors)  
        c. 1-Many Site  
        d. 0-Many Service  
        e. 1-Many Contract  
        f. 1-Many Budget  
        g. 1-Many Document  
        h. 1-Many Regulatory Submission  
        i. 1-Many Audit  
        j. 1-Many Training Program  
        k. 1-Many SOP (Standard Operating Procedure)  
        l. 1-Many System  
        m. 1-Many Report  
        n. 1-Many Milestone  
        o. 1-Many Risk Assessment  
        p. 1-Many CAPA (Corrective and Preventive Action)  
        q. 1-Many Oversight Body  
        r. 1-Many Publication  
        s. 1-Many Data Transfer Agreement  
        t. 1-Many Investigational Product  
        u. 0-Many Tag (User construct to group studies)  
2\. Tag:  
    The Tag object represents a flexible, user-defined label that can be applied to studies for  
    grouping and organizational purposes. Tags can represent various concepts such as  
    geographical regions, therapeutic areas, phases, or any other categorization useful for  
    the sponsor.  
        a. 1-Many Study  
        b. 1 Sponsor (the sponsor who created the tag)  
        c. 1-Many Person (users who can apply/manage this tag)  
        d. 0-Many Document (documents related to this tag category)  
        e. 0-Many Report (reports filtered or grouped by this tag)  
        f. 1-Many Audit Trail Entry (tracking changes to tag assignments)  
        g. 0-Many Dashboard (dashboards focused on studies with this tag)  
        h. 0-Many Metric (metrics specific to studies with this tag)  
        i. 0-Many User Role (for tag-specific permissions)  
        j. 0-Many Notification Rule (for tag-based notifications)  
3\. Study:  
    This list aims to capture a comprehensive set of relationships for a Study object in the  
    context of Nucleus. Some of these relationships (like SAEs) are surfaced at this level for  
    easier tracking and management, even though they might have deeper relationships  
    with child objects.  
        a. 1 Sponsor  
        b. 1-Many Tag  
        c. 1-Many Arm  
        d. 1-Many Schedule of Assessments (SOA)  
        e. 1-Many Site  
f. 1-Many Participant  
g. 1-Many Visit  
h. 1-Many CRF (Case Report Form)  
i. 1-Many Document  
j. 1-Many Milestone  
k. 1 Protocol  
l. 1-Many Investigational Product  
m. 1-Many Plan (e.g., Monitoring Plan, Data Management Plan)  
n. 1-Many Oversight Body (e.g., IRB/EC, DSMB)  
o. 0-Many Deviation  
p. 0-Many Screen Fail  
q. 1-Many Person (e.g., Investigator, Coordinator, Monitor)  
r. 0-Many Adverse Event  
s. 1-Many Informed Consent  
t. 0-Many Action Item  
u. 0-Many Enrollment  
v. 0-Many Payment  
w. 1-Many System (e.g., EDC, CTMS, eTMF)  
x. 1-Many Service (e.g., Central Lab, Imaging)  
y. 1 Study Startup Package  
z. 1 Budget  
aa.0-Many Contract  
bb.1-Many Schedule of Assessments (SOA)  
cc.1-Many Endpoint  
dd.0-Many Lab Result  
ee.0-Many Regulatory Submission  
ff. 0-Many Audit  
gg.0-Many Report  
hh.0-Many COA/PRO (Clinical Outcome Assessment/Patient Reported Outcome)  
ii. 0-Many Other Clinical Event  
jj. 0-Many CAPA (Corrective and Preventive Action)  
kk.0-Many Date (key dates in the study lifecycle)  
ll. 0-Many Data Transfer  
mm. 1-Many User Role  
nn.0-Many Serious Adverse Event (SAE)  
oo.1 Statistical Analysis Plan  
pp.1-Many Amendment  
qq.1-Many Randomization List  
rr. 0-Many Query  
ss.0-Many System  
tt. 1-Many Training Record  
uu.0-Many Monitoring Visit  
vv. 1-Many Risk Assessment  
4\. Arm:  
    The Arm object represents a specific group or cohort within a clinical trial, typically  
    differentiated by the intervention or treatment they receive.  
         a. 1 Study (the study this arm belongs to)  
         b. 0-1 Schedule of Assessments (SOA) (arm-specific SOA, if applicable)  
         c. 1-Many Visit (visits specific to this arm)  
         d. 0-1 Investigational Product (the treatment assigned to this arm, if applicable)  
         e. 1-Many Participant (subjects assigned to this arm)  
         f. 1-Many Inclusion Criteria (arm-specific criteria, if any)  
         g. 1-Many Exclusion Criteria (arm-specific criteria, if any)  
         h. 1-Many Procedure (procedures specific to this arm)  
         i. 1-Many CRF (Case Report Form) (forms specific to this arm)  
         j. 1-Many Document (arm-specific documents)  
         k. 1-Many Person (staff specifically assigned to this arm)  
         l. 1-Many Milestone (arm-specific milestones)  
         m. 1-Many Task (arm-specific tasks)  
         n. 1-Many Audit Trail Entry  
         o. 1-Many Comment  
5\. Site: TODO  
6\. Participant:  
    The Participant object is crucial in Nucleus as it represents the core data collection point  
    in clinical trials. These relationships allow for comprehensive tracking of all  
    participant-related data, enabling efficient monitoring, data management, and analysis  
    within the Nucleus solution.  
         a. 1 Study  
         b. 1-Many Tag  
         c. 1 Site  
         d. 1-Many Visit  
         e. 1-Many CRF (Case Report Form)  
         f. 1 Informed Consent  
         g. 1 Screening Record  
         h. 0-1 Randomization Assignment  
         i. 1-Many Investigational Product Dispensation  
         j. 0-Many Adverse Event  
         k. 0-Many Serious Adverse Event (SAE)  
         l. 0-Many Protocol Deviation  
         m. 1-Many Lab Result  
         n. 1-Many Vital Sign Record  
         o. 1-Many COA/PRO (Clinical Outcome Assessment/Patient Reported Outcome)  
         p. 1-Many Concomitant Medication  
         q. 1-Many Medical History Record  
         r. 0-Many Query  
         s. 1 Demographic Information  
         t. 0-1 Screen Fail Record  
         u. 0-1 Early Termination Record  
         v. 1-Many Document (e.g., signed ICF, source documents)  
         w. 1-Many Endpoint Data  
         x. 1-Many Sample Collection Record  
         y. 1-Many Imaging Record  
         z. 1-Many Diary Entry  
         aa.1-Many Questionnaire Response  
         bb.1-Many Procedure Record  
         cc.1-Many Eligibility Criteria Assessment  
         dd.1-Many Patient Reported Outcome (PRO)  
         ee.1-Many Wearable Device Data  
         ff. 1-Many Pharmacokinetic Sample  
         gg.1-Many Drug Accountability Record  
         hh.1-Many Follow-up Contact  
         ii. 0-Many Unscheduled Visit  
         jj. 1 Enrollment Record  
         kk.1-Many Payment Record (if applicable)  
         ll. 1-Many Data Correction Form  
         mm. 1-Many Protocol Amendment Acknowledgment  
         nn.1-Many Genetic/Biomarker Sample  
         oo.1 Withdrawal of Consent Record (if applicable)  
7\. Visit:  
    The Visit object would serve as a central point for organizing and managing all activities  
    and data collections that occur during a participant's visit. This structure allows for  
    efficient tracking of visit-specific information, ensures protocol compliance, and facilitates  
    the monitoring of study progress. It also enables the platform to generate visit-specific  
    reports, track visit completion status, and manage the complex scheduling often required  
    in clinical trials.  
         a. 1 Study  
         b. 1-Many Tag  
         c. 1 Site  
         d. 1 Participant  
         e. 1 Schedule of Assessments (SOA) Item  
         f. 1-Many CRF (Case Report Form)  
         g. 1-Many Procedure  
         h. 1-Many Sample Collection  
         i. 1-Many Vital Sign Measurement  
         j. 1-Many Investigational Product Dispensation  
         k. 1-Many Investigational Product Return  
         l. 0-Many Adverse Event Report  
         m. 0-Many Serious Adverse Event (SAE) Report  
         n. 0-Many Protocol Deviation Report  
         o. 1-Many Concomitant Medication Update  
         p. 1-Many Questionnaire Administration  
        q. 1-Many Patient Reported Outcome (PRO) Collection  
        r. 1-Many Imaging Procedure  
        s. 1-Many Lab Test Order  
        t. 1-Many Physical Examination  
        u. 1 Visit Status (e.g., Scheduled, Completed, Missed)  
        v. 1 Visit Date  
        w. 1-Many Query  
        x. 1-Many Data Correction Form  
        y. 1 Visit Duration  
        z. 1-Many Document (e.g., source documents)  
        aa.1 Clinician Assessment  
        bb.1-Many Endpoint Data Collection  
        cc.1 Visit Cost (for budget tracking)  
        dd.1-Many Staff Involvement Record  
        ee.1 Window Compliance Status  
        ff. 0-1 Informed Consent Update  
        gg.1-Many Drug Accountability Check  
        hh.1-Many Eligibility Criteria Reassessment (if applicable)  
        ii. 1-Many Wearable Device Data Collection  
        jj. 1 Visit Type (e.g., Screening, Baseline, Treatment, Follow-up)  
        kk.0-1 Early Termination Procedures (if applicable)  
        ll. 1-Many Protocol-Specific Assessment  
        mm. 1-Many Pharmacokinetic Sample Collection  
        nn.1 Visit Location (e.g., Site, Remote, Home)  
        oo.1-Many Unscheduled Procedure (if applicable)  
8\. Task:  
    The Task object represents specific actions or activities that need to be completed as  
    part of the clinical trial process. Tasks can be associated with various aspects of the trial  
    and are crucial for managing workflow and ensuring all necessary steps are completed.  
        a. 1-Many Tag  
        b. 0-Many Document  
        c. 0-Many Lab Result  
        d. 1 Study  
        e. 0-1 Site  
        f. 0-1 Visit  
        g. 0-1 Participant  
        h. 1 Task Type  
        i. 1 Task Status  
        j. 1 Task Priority  
        k. 1 Task Description  
        l. 1 Due Date  
        m. 0-1 Completion Date  
        n. 1 Assigned To (Person)  
        o. 0-1 Assigned By (Person)  
        p. 0-1 Parent Task  
        q. 0-Many Child Task  
        r. 0-Many Action Item  
        s. 0-1 CRF  
        t. 0-1 Milestone  
        u. 0-1 Protocol  
        v. 0-1 Investigational Product  
        w. 0-1 Adverse Event  
        x. 0-1 Deviation  
        y. 1 Created Date  
        z. 1 Last Modified Date  
        aa.1-Many Audit Trail Entry  
        bb.0-Many Comment  
        cc.0-1 Estimated Duration  
        dd.1 Task Category  
        ee.0-1 Plan  
        ff. 0-1 Service  
        gg.0-1 System  
        hh.0-Many Discrepancy (Query)  
        ii. 0-1 Budget Item  
        jj. 0-1 Contract Item  
        kk.0-1 Regulatory Submission  
        ll. 0-1 Audit  
        mm. 0-1 Report  
        nn.0-1 Shipment  
        oo.0-1 Sample  
9\. Participant (Subject):  
    The Participant (Subject) object represents an individual enrolled in a clinical trial. This  
    object is crucial for tracking all data related to a specific participant throughout the study.  
        a. 1 Study  
        b. 1-Many Tag  
        c. 1 Site  
        d. 1-Many Visit  
        e. 1-Many Task  
        f. 1 Enrollment Status  
        g. 1 Unique Participant ID  
        h. 1 Randomization Number (if applicable)  
        i. 1-Many Informed Consent  
        j. 1-Many CRF (Case Report Form)  
        k. 1-Many Adverse Event  
        l. 0-Many Serious Adverse Event (SAE)  
        m. 1-Many Lab Result  
        n. 1-Many Questionnaire Response  
        o. 1-Many COA/PRO (Clinical Outcome Assessment/Patient Reported Outcome)  
       p. 1-Many Deviation  
       q. 0-1 Screen Fail (if applicable)  
       r. 1-Many Document  
       s. 1-Many Sample  
       t. 1-Many Investigational Product Dispensation  
       u. 1-Many Investigational Product Return  
       v. 1 Date of Enrollment  
       w. 0-1 Date of Completion/Discontinuation  
       x. 1-Many Concomitant Medication  
       y. 1-Many Vital Sign Measurement  
       z. 1-Many Physical Examination  
       aa.1-Many Imaging Procedure  
       bb.1 Demographic Information  
       cc.1-Many Inclusion Criteria Assessment  
       dd.1-Many Exclusion Criteria Assessment  
       ee.1-Many Patient Diary Entry  
       ff. 1-Many Payment  
       gg.1-Many Discrepancy (Query)  
       hh.1-Many Action Item  
       ii. 1 Randomization Group (if applicable)  
       jj. 1-Many Schedule of Assessments (SOA) Compliance  
       kk.1-Many Endpoint Data  
       ll. 1-Many Other Clinical Event  
       mm. 1-Many Equipment Assignment (e.g., wearable devices)  
       nn.1-Many Data Transfer (e.g., from wearable devices)  
       oo.1-Many Audit Trail Entry  
10.Discrepancy (Query):  
    This object represents questions, issues, or inconsistencies identified in the clinical trial  
    data that require clarification or resolution. This object is crucial for maintaining data  
    quality and integrity throughout the study.  
       a. 1 Study  
       b. 1-Many Tag  
       c. 1 Site  
       d. 0-1 Participant  
       e. 0-1 Visit  
       f. 1 CRF (Case Report Form)  
       g. 1 Discrepancy Type (e.g., missing data, out of range value, inconsistency)  
       h. 1 Discrepancy Status (e.g., open, answered, closed, canceled)  
       i. 1 Discrepancy Priority (e.g., low, medium, high)  
       j. 1 Discrepancy Description  
       k. 1 Created Date  
       l. 1 Created By (Person)  
       m. 0-1 Assigned To (Person)  
       n. 0-1 Resolution Date  
        o. 0-1 Resolved By (Person)  
        p. 1-Many Audit Trail Entry  
        q. 0-Many Document (e.g., supporting evidence)  
        r. 0-1 Related Task  
        s. 0-1 Related Adverse Event  
        t. 0-1 Related Deviation  
        u. 0-1 Related Lab Result  
        v. 0-1 Related Investigational Product  
        w. 0-Many Comment  
        x. 1 Data Point in Question  
        y. 1 Original Value  
        z. 0-1 Corrected Value  
        aa.1 Query Text  
        bb.0-1 Query Response  
        cc.1 Query Category (e.g., safety, efficacy, administrative)  
        dd.0-1 Related Monitoring Visit  
        ee.1 Source of Discrepancy (e.g., data entry, monitoring, central review)  
        ff. 1 Impact Level (e.g., minor, major, critical)  
        gg.0-1 Related Protocol Section  
        hh.0-1 Related SOA (Schedule of Assessments) Item  
        ii. 1 Discrepancy Identification Method (e.g., manual review, automated check)  
        jj. 0-1 Related Data Transfer  
        kk.0-1 Related Endpoint  
        ll. 0-1 Related Sample  
        mm. 0-1 Related Equipment  
        nn.1 Discrepancy Lifecycle Timestamps (e.g., opened, answered, closed)  
        oo.0-1 Related CAPA (Corrective and Preventive Action)  
11.Deviation:  
    The Deviation object represents any departure from the approved study protocol, Good  
    Clinical Practice (GCP), or applicable regulatory requirements. Tracking deviations is  
    crucial for maintaining study integrity, ensuring patient safety, and complying with  
    regulatory requirements.  
        a. 1 Study  
        b. 1-Many Tag  
        c. 1 Site  
        d. 0-1 Participant  
        e. 0-1 Visit  
        f. 1 Deviation Type (e.g., inclusion/exclusion criteria, dosing, procedure)  
        g. 1 Deviation Category (e.g., minor, major, critical)  
        h. 1 Deviation Description  
        i. 1 Date of Occurrence  
        j. 1 Date of Discovery  
        k. 1 Reported By (Person)  
        l. 1 Deviation Status (e.g., reported, reviewed, closed)  
        m. 0-1 Root Cause Analysis  
        n. 0-1 Corrective Action  
        o. 0-1 Preventive Action  
        p. 1-Many Audit Trail Entry  
        q. 0-Many Document (e.g., supporting evidence, correspondence)  
        r. 0-1 Related Task  
        s. 0-1 Related Adverse Event  
        t. 0-1 Related Investigational Product  
        u. 0-Many Discrepancy (Query)  
        v. 1 Impact Assessment  
        w. 1 Protocol Section Reference  
        x. 0-1 Related Monitoring Visit  
        y. 0-1 Related CAPA (Corrective and Preventive Action)  
        z. 1 Deviation Classification (e.g., protocol deviation, GCP deviation)  
        aa.0-1 IRB/EC Reporting Status  
        bb.0-1 Regulatory Authority Reporting Status  
        cc.1 Deviation Severity  
        dd.0-1 Related CRF (Case Report Form)  
        ee.0-1 Related Lab Result  
        ff. 0-1 Related Sample  
        gg.0-1 Related Equipment  
        hh.0-1 Related Informed Consent  
        ii. 1 Deviation Identification Method (e.g., site reported, monitor identified)  
        jj. 0-1 Related Data Transfer  
        kk.0-1 Related Endpoint  
        ll. 1 Deviation Resolution Date  
        mm. 1 Resolved By (Person)  
        nn.0-Many Comment  
        oo.1 Potential Impact on Patient Safety/Data Integrity  
12.Screen Fail:  
    The Screen Fail object represents a participant who did not meet the eligibility criteria for  
    the study during the screening process. Tracking screen fails is important for  
    understanding recruitment challenges, refining inclusion/exclusion criteria, and managing  
    site performance.  
        a. 1 Study  
        b. 1-Many Tag  
        c. 1 Site  
        d. 1 Participant  
        e. 1 Screening Visit  
        f. 1 Screen Fail Date  
        g. 1-Many Reason for Screen Fail  
        h. 1-Many Failed Inclusion Criteria  
        i. 1-Many Failed Exclusion Criteria  
        j. 1 Informed Consent Status  
        k. 1-Many CRF (Case Report Form) related to screening  
        l. 1-Many Lab Result  
        m. 1-Many Vital Sign Measurement  
        n. 1-Many Physical Examination Result  
        o. 0-Many Adverse Event (if any occurred during screening)  
        p. 1 Investigator Assessment  
        q. 1 Screen Fail Reported By (Person)  
        r. 1-Many Document (e.g., source documents, lab reports)  
        s. 0-Many Discrepancy (Query) related to screening data  
        t. 0-1 Re-screening Eligibility (if applicable)  
        u. 1 Demographics Information  
        v. 1-Many Concomitant Medication  
        w. 1-Many Medical History Item  
        x. 0-Many Imaging Procedure Result  
        y. 1 Screen Fail Confirmation Status  
        z. 1-Many Questionnaire Response  
        aa.1-Many Patient Reported Outcome (PRO)  
        bb.0-1 Related Task (e.g., for follow-up actions)  
        cc.1 Screening Number/ID  
        dd.1 Time in Screening Period  
        ee.1-Many Audit Trail Entry  
        ff. 0-Many Comment  
        gg.1 Screen Fail Review Status  
        hh.0-1 Related Deviation (if screening process deviated from protocol)  
        ii. 1 Patient Reimbursement Status (if applicable)  
        jj. 1 Data Entry Timestamp  
        kk.1 Data Entry User  
        ll. 0-1 Related Sample Collection (if any during screening)  
        mm. 0-1 Related Equipment Use (e.g., ECG machine)  
        nn.1 Screen Fail Verification Status  
        oo.1 Impact on Enrollment Metrics  
13.Person:  
    The Person object represents any individual involved in the clinical trial, including but not  
    limited to investigators, coordinators, monitors, and other staff. This object is crucial for  
    managing roles, responsibilities, and access within the study.  
        a. 1-Many Study (a person can be involved in multiple studies)  
        b. 1-Many Tag (This could indicate the person’s interests)  
        c. 0-Many Site (a person can be associated with multiple sites)  
        d. 1-Many Role (e.g., Principal Investigator, Study Coordinator, Monitor)  
        e. 1 First Name  
        f. 1 Last Name  
        g. 1 Unique Identifier (e.g., employee ID)  
        h. 1 Contact Information (e.g., email, phone)  
        i. 1-Many Credential  
        j. 1-Many Training Record  
        k. 1-Many Certification  
        l. 1 Employment Status (e.g., active, inactive)  
        m. 1-Many Task (assigned to or created by)  
        n. 1-Many Document (authored or reviewed)  
        o. 1-Many Audit Trail Entry  
        p. 0-Many Discrepancy (Query) (created or resolved)  
        q. 0-Many Deviation (reported or reviewed)  
        r. 1-Many Signature (e.g., for CRFs, regulatory documents)  
        s. 1 User Account (for system access)  
        t. 1-Many User Role (system permissions)  
        u. 0-Many Monitoring Visit (conducted or participated in)  
        v. 0-Many Action Item (assigned to or created by)  
        w. 1-Many Log Entry (e.g., training log, communication log)  
        x. 0-Many Adverse Event (reported or reviewed)  
        y. 0-Many Serious Adverse Event (reported or reviewed)  
        z. 0-Many Informed Consent (administered or witnessed)  
        aa.0-Many CRF (completed or reviewed)  
        bb.1 CV (Curriculum Vitae)  
        cc.1-Many Delegation of Authority Record  
        dd.0-Many Protocol Amendment (reviewed or acknowledged)  
        ee.0-Many Regulatory Submission (prepared or reviewed)  
        ff. 0-Many Report (authored or reviewed)  
        gg.0-Many CAPA (Corrective and Preventive Action) (involved in)  
        hh.1 GCP Training Status  
        ii. 1 Protocol Training Status  
        jj. 1-Many Shipment (received or sent)  
        kk.0-Many Equipment (responsible for or trained on)  
        ll. 1-Many Communication Record  
        mm. 1 Language Proficiency  
        nn.1-Many Conflict of Interest Disclosure  
        oo.1 Last System Access Date  
14.Person Role:  
    description  
        a. 1-Many Person  
        b. 1-Many Tag  
15.CRF (Case Report Form):  
    The CRF object represents the forms used to collect and report clinical trial data for each  
    participant. CRFs are crucial for standardized data collection and are the primary source  
    of data for analysis in clinical trials.  
        a. 1 Study  
        b. 1-Many Tag  
        c. 1 Site  
        d. 1 Participant  
        e. 1 Visit (if visit-specific)  
        f. 1 CRF Type (e.g., Demographics, Vital Signs, Adverse Events)  
        g. 1 CRF Version  
        h. 1 CRF Status (e.g., Not Started, In Progress, Completed, Verified)  
        i. 1 Date Completed  
        j. 1 Completed By (Person)  
        k. 0-1 Date Verified  
        l. 0-1 Verified By (Person)  
        m. 1-Many Data Field (individual data points within the CRF)  
        n. 1-Many Audit Trail Entry  
        o. 0-Many Discrepancy (Query)  
        p. 0-Many Deviation (if any protocol deviations are recorded on this CRF)  
        q. 1-Many Document (e.g., source documents supporting CRF data)  
        r. 0-1 Related Task  
        s. 0-Many Comment  
        t. 1 Data Entry Method (e.g., EDC, Paper)  
        u. 1 Last Modified Date  
        v. 1 Last Modified By (Person)  
        w. 1 Electronic Signature Status  
        x. 0-1 Related Lab Result  
        y. 0-1 Related Adverse Event  
        z. 0-1 Related Serious Adverse Event  
        aa.0-1 Related Concomitant Medication  
        bb.0-1 Related Physical Examination  
        cc.0-1 Related Vital Signs  
        dd.0-1 Related Investigational Product Administration  
        ee.0-1 Related Patient Reported Outcome  
        ff. 1 CRF Template Reference  
        gg.1 SDV (Source Data Verification) Status  
        hh.1 SDV By (Person)  
        ii. 1 SDV Date  
        jj. 0-1 Related Endpoint Data  
        kk.1 CRF Completion Guidelines Reference  
        ll. 0-1 Related Sample Collection  
        mm. 0-1 Related Equipment Usage  
        nn.1 Data Export Status  
        oo.1 Form Specific Validation Rules  
16.Document:  
    The Document object represents any file or record associated with the clinical trial. This  
    can include protocols, informed consent forms, regulatory submissions, source  
    documents, and many other types of files crucial to the conduct and documentation of  
    the trial.  
        a. 1 Study  
        b. 1-Many Tag  
        c. 0-1 Site (if site-specific)  
        d. 0-1 Participant (if participant-specific)  
        e. 1 Document Type (e.g., Protocol, ICF, Regulatory, Source, Training)  
        f. 1 Document Version  
        g. 1 Document Status (e.g., Draft, Approved, Superseded)  
        h. 1 Creation Date  
        i. 1 Created By (Person)  
        j. 1 Last Modified Date  
        k. 1 Last Modified By (Person)  
        l. 1 Document Title  
        m. 1 Document Description  
        n. 1 File Location/URL  
        o. 1 File Type (e.g., PDF, DOCX, XLSX)  
        p. 1 File Size  
        q. 1-Many Audit Trail Entry  
        r. 0-Many Related Task  
        s. 0-Many Comment  
        t. 1 Approval Status  
        u. 0-1 Approval Date  
        v. 0-1 Approved By (Person)  
        w. 1 Document Classification (e.g., Essential Document, Source Document)  
        x. 0-Many Related CRF  
        y. 0-1 Related Visit  
        z. 0-1 Related Adverse Event  
        aa.0-1 Related Deviation  
        bb.0-1 Related Monitoring Visit  
        cc.0-1 Related Regulatory Submission  
        dd.0-1 Related Audit  
        ee.1 Document Retention Period  
        ff. 1 Document Expiration Date (if applicable)  
        gg.1 Document Language  
        hh.0-Many Translation (for multi-language studies)  
        ii. 1 Electronic Signature Status  
        jj. 1 Quality Control Check Status  
        kk.1 Quality Control Check By (Person)  
        ll. 1 Quality Control Check Date  
        mm. 1 Document Template Reference (if based on a template)  
        nn.0-Many Related Training Record  
        oo.1 Document Access Control List  
17.Adverse Event:  
    The Adverse Event object represents any unfavorable and unintended sign, symptom,  
    or disease temporally associated with the use of a medical treatment or procedure that  
    may or may not be related to the medical treatment or procedure. Tracking adverse  
    events is crucial for patient safety and regulatory compliance.  
        a. 1 Study  
        b. 1-Many Tag  
        c. 1 Site  
        d. 1 Participant  
        e. 1 Adverse Event Description  
        f. 1 Adverse Event Onset Date  
        g. 0-1 Adverse Event End Date  
        h. 1 Adverse Event Severity  
        i. 1 Relationship to Study Treatment  
        j. 1 Action Taken with Study Treatment  
        k. 1 Outcome  
        l. 1 Reported By (Person)  
        m. 1 Reported Date  
        n. 1 Investigator Assessment Date  
        o. 1 Investigator Assessment By (Person)  
        p. 1 Seriousness (Serious or Non-Serious)  
        q. 0-1 Related Serious Adverse Event (if applicable)  
        r. 1 Expectedness (Expected or Unexpected)  
        s. 1-Many Concomitant Medication  
        t. 1-Many CRF (Case Report Form)  
        u. 1-Many Document (e.g., supporting medical records)  
        v. 0-Many Related Task  
        w. 0-Many Discrepancy (Query)  
        x. 0-1 Related Deviation (if AE resulted from protocol deviation)  
        y. 1 MedDRA Coding (System Organ Class, Preferred Term, etc.)  
        z. 1 AE Number/Identifier  
        aa.1 Status (e.g., Open, Closed, Follow-up Required)  
        bb.0-1 Follow-up Date  
        cc.1-Many Audit Trail Entry  
        dd.0-Many Comment  
        ee.1 Causality Assessment  
        ff. 1 Intensity/Grade  
        gg.1 Frequency  
        hh.1 Pattern  
        ii. 0-1 Related Visit  
        jj. 0-1 Related Lab Result  
        kk.0-1 Related Investigational Product Administration  
        ll. 1 Regulatory Reporting Status  
        mm. 0-1 SUSAR (Suspected Unexpected Serious Adverse Reaction) Status  
        nn.1 AE Resolution Status  
        oo.0-Many Related CAPA (Corrective and Preventive Action)  
18.Informed Consent:  
     The Informed Consent object represents the process and documentation by which a  
    participant voluntarily confirms their willingness to participate in a particular trial, after  
having been informed of all aspects of the trial that are relevant to their decision to  
participate. This is a crucial ethical and regulatory requirement for clinical trials.  
    a. 1 Study  
    b. 1-Many Tag  
    c. 1 Site  
    d. 1 Participant  
    e. 1 Informed Consent Form Version  
    f. 1 Consent Date  
    g. 1 Consent Time  
    h. 1 Consenting Person (usually the participant, but could be a legally authorized  
         representative)  
    i. 1 Person Obtaining Consent (typically a study staff member)  
    j. 1 Consent Witness (if required)  
    k. 1 Consent Status (e.g., Obtained, Withdrawn, Re-consented)  
    l. 1 Consent Verification Status  
    m. 0-1 Consent Verification Date  
    n. 0-1 Consent Verified By (Person)  
    o. 1 Language of Consent Form  
    p. 1 Participant's Preferred Language  
    q. 0-1 Translator Used (if applicable)  
    r. 1 Consent Process Notes  
    s. 1-Many Document (e.g., signed consent form, participant information sheet)  
    t. 0-1 Related Visit (typically screening visit)  
    u. 0-Many Discrepancy (Query)  
    v. 0-1 Related Deviation (if consent process deviated from protocol)  
    w. 1-Many Audit Trail Entry  
    x. 0-Many Comment  
    y. 1 Consent Comprehension Check Status  
    z. 0-1 Re-consent Required Flag  
    aa.0-1 Re-consent Due Date  
    bb.0-1 Consent Withdrawal Date (if applicable)  
    cc.0-1 Consent Withdrawal Reason (if applicable)  
    dd.1 Electronic Signature Status (if e-consent used)  
    ee.1 Consent Storage Location  
    ff. 1 Consent Expiration Date (if applicable)  
    gg.1-Many Consent Element (specific items consented to)  
    hh.0-1 Related Task (e.g., for obtaining re-consent)  
    ii. 1 IRB/EC Approval Status of Consent Form  
    jj. 1 Participant Provided Copy of Signed Consent (Yes/No)  
    kk.1 Consent Form Version Matches Current Approved Version (Yes/No)  
    ll. 0-1 Related Protocol Version  
    mm. 0-1 Related Protocol Amendment (if consent due to amendment)  
    nn.1 Consent Quality Control Check Status  
    oo.1 Consent Quality Control Check By (Person)  
19.Action Item:  
    The Action Item object represents specific tasks or actions that need to be completed as  
    part of the clinical trial process. These are typically more granular than general tasks and  
    often arise from monitoring visits, audits, or other quality control processes.  
        a. 1 Study  
        b. 1-Many Tag  
        c. 0-1 Site (if site-specific)  
        d. 1 Action Item Description  
        e. 1 Action Item Status (e.g., Open, In Progress, Completed, Overdue)  
        f. 1 Priority Level (e.g., Low, Medium, High, Critical)  
        g. 1 Due Date  
        h. 1 Assigned To (Person)  
        i. 1 Assigned By (Person)  
        j. 1 Date Created  
        k. 0-1 Date Completed  
        l. 0-1 Completed By (Person)  
        m. 1 Action Item Category (e.g., Data Query, Protocol Deviation, Regulatory, Safety)  
        n. 0-1 Related Visit  
        o. 0-1 Related Participant  
        p. 0-1 Related Monitoring Visit  
        q. 0-1 Related Audit  
        r. 0-1 Related Deviation  
        s. 0-1 Related Adverse Event  
        t. 0-1 Related CRF (Case Report Form)  
        u. 0-Many Related Document  
        v. 0-Many Discrepancy (Query)  
        w. 1-Many Audit Trail Entry  
        x. 0-Many Comment  
        y. 1 Action Item Source (e.g., Monitor, Investigator, Data Manager)  
        z. 0-1 Parent Action Item (if this is a sub-item)  
        aa.0-Many Child Action Item  
        bb.1 Estimated Time to Complete  
        cc.1 Actual Time to Complete  
        dd.0-1 Related CAPA (Corrective and Preventive Action)  
        ee.1 Recurrence Frequency (if recurring action item)  
        ff. 0-1 Related Protocol Section  
        gg.0-1 Related Regulatory Requirement  
        hh.1 Action Item Impact Level  
        ii. 1 Verification Status  
        jj. 0-1 Verified By (Person)  
        kk.0-1 Verification Date  
        ll. 1 Action Item Tracking Number  
        mm. 0-1 Related Equipment  
        nn.0-1 Related Investigational Product  
         oo.1 Action Item Closure Notes  
20.Milestone:  
    The Milestone object represents significant events or achievements in the lifecycle of a  
    clinical trial. Milestones are crucial for tracking progress, managing timelines, and  
    reporting to stakeholders.  
         a. 1 Study  
         b. 1-Many Tag  
         c. 0-1 Site (if site-specific)  
         d. 1 Milestone Name  
         e. 1 Milestone Description  
         f. 1 Milestone Type (e.g., Regulatory, Enrollment, Treatment, Data Management)  
         g. 1 Planned Date  
         h. 0-1 Actual Date  
         i. 1 Milestone Status (e.g., Planned, In Progress, Completed, Delayed)  
         j. 1 Milestone Owner (Person)  
         k. 0-Many Dependent Milestone (milestones that depend on this one)  
         l. 0-Many Prerequisite Milestone (milestones that this one depends on)  
         m. 1-Many Document (e.g., supporting documentation)  
         n. 0-Many Task (associated tasks)  
         o. 0-Many Action Item (associated action items)  
         p. 1 Milestone Importance (e.g., Critical, High, Medium, Low)  
         q. 1 Created Date  
         r. 1 Created By (Person)  
         s. 1 Last Modified Date  
         t. 1 Last Modified By (Person)  
         u. 1-Many Audit Trail Entry  
         v. 0-Many Comment  
         w. 1 Milestone Category (e.g., Start-up, Conduct, Close-out)  
         x. 0-1 Related Protocol Version  
         y. 0-1 Related Protocol Amendment  
         z. 0-1 Related Regulatory Submission  
         aa.0-1 Related Contract  
         bb.0-1 Related Budget  
         cc.1 Milestone Progress Percentage  
         dd.1 Milestone Delay Reason (if applicable)  
         ee.1 Milestone Delay Mitigation Plan (if applicable)  
         ff. 0-Many Notification Rule  
         gg.1 Milestone Visibility Level (e.g., Sponsor Only, Site Visible)  
         hh.0-1 Related Visit (if milestone is visit-specific)  
         ii. 0-1 Related Endpoint (if milestone is related to a specific endpoint)  
         jj. 1 Milestone Tracking Method (e.g., Manual, System-calculated)  
         kk.1 Milestone Flexibility (e.g., Fixed, Adjustable)  
         ll. 1 Last Review Date  
         mm. 1 Last Reviewed By (Person)  
         nn.1 Next Review Date  
         oo.0-1 Related Report (e.g., milestone report)  
21.Enrollment:  
    The Enrollment object represents the process and status of a participant joining a clinical  
    trial. It's a crucial object for tracking recruitment progress, managing participant flow, and  
    ensuring compliance with enrollment criteria.  
         a. 1 Study  
         b. 1-Many Tag  
         c. 1 Site  
         d. 1 Participant  
         e. 1 Enrollment Date  
         f. 1 Enrollment Status (e.g., Screened, Enrolled, Screen Failed, Withdrawn)  
         g. 1 Enrollment Number (unique identifier within the study)  
         h. 1 Randomization Number (if applicable)  
         i. 1 Informed Consent  
         j. 1-Many Inclusion Criteria Assessment  
         k. 1-Many Exclusion Criteria Assessment  
         l. 1 Eligibility Confirmation Date  
         m. 1 Eligibility Confirmed By (Person)  
         n. 0-1 Screening Failure Reason (if applicable)  
         o. 0-1 Withdrawal Date (if applicable)  
         p. 0-1 Withdrawal Reason (if applicable)  
         q. 1-Many Visit (scheduled visits for the participant)  
         r. 1-Many CRF (Case Report Form)  
         s. 0-Many Discrepancy (Query)  
         t. 0-Many Deviation  
         u. 1-Many Document (e.g., source documents)  
         v. 0-Many Lab Result  
         w. 1 Enrollment Visit  
         x. 1-Many Audit Trail Entry  
         y. 0-Many Comment  
         z. 1 Enrollment Method (e.g., On-site, Remote)  
         aa.1 Recruiting Method (how the participant was recruited)  
         bb.0-1 Re-screening Status (if applicable)  
         cc.1 Protocol Version at Enrollment  
         dd.1 Investigator Signature Status  
         ee.1 Investigator Signature Date  
         ff. 1 Enrollment Verification Status  
         gg.1 Enrollment Verified By (Person)  
         hh.1 Enrollment Verification Date  
         ii. 0-1 Stratification Factor(s) (if applicable)  
         jj. 1 First Dose Date (if applicable)  
         kk.1 Last Dose Date (if applicable)  
         ll. 1 Treatment Arm Assignment (if applicable)  
        mm. 1 Enrollment in Competing Study Status  
        nn.1 Prior Study Participation Status  
        oo.1-Many Related Task  
22.Payment:  
     The Payment object represents financial transactions related to the clinical trial,  
    including payments to sites, investigators, systems, and participants (if applicable). This  
    object is crucial for financial management and compliance with payment regulations.  
        a. 1 Study  
        b. 1-Many Tag  
        c. 0-1 Site (if site payment)  
        d. 0-1 Participant (if participant payment)  
        e. 1 Payment Amount  
        f. 1 Payment Currency  
        g. 1 Payment Date  
        h. 1 Payment Status (e.g., Pending, Processed, Completed, Cancelled)  
        i. 1 Payment Type (e.g., Site Payment, Investigator Fee, Participant  
             Reimbursement)  
        j. 1 Payment Reason (e.g., Visit Completion, Procedure, Travel Reimbursement)  
        k. 0-1 Related Visit (if visit-specific payment)  
        l. 0-1 Related Procedure (if procedure-specific payment)  
        m. 1 Payer (entity making the payment)  
        n. 1 Payee (entity receiving the payment)  
        o. 1 Payment Method (e.g., Bank Transfer, Check, Cash)  
        p. 1 Invoice Number (if applicable)  
        q. 0-1 Invoice Date (if applicable)  
        r. 1 Payment Approval Status  
        s. 0-1 Approved By (Person)  
        t. 0-1 Approval Date  
        u. 1-Many Document (e.g., receipts, invoices)  
        v. 1 Created By (Person)  
        w. 1 Created Date  
        x. 1 Last Modified By (Person)  
        y. 1 Last Modified Date  
        z. 1-Many Audit Trail Entry  
        aa.0-Many Comment  
        bb.1 Payment Category (e.g., Start-up, Ongoing, Close-out)  
        cc.0-1 Related Contract  
        dd.0-1 Related Budget Line Item  
        ee.1 Tax Information (e.g., Tax ID, VAT number)  
        ff. 0-1 Withholding Tax Amount (if applicable)  
        gg.1 Payment Frequency (e.g., One-time, Monthly, Quarterly)  
        hh.0-1 Payment Schedule Reference  
        ii. 1 Payment Verification Status  
        jj. 0-1 Payment Verified By (Person)  
       kk.0-1 Payment Verification Date  
       ll. 0-1 Related Task (e.g., payment processing task)  
       mm. 1 Exchange Rate (if payment involves currency conversion)  
       nn.1 Payment Notes  
       oo.1 Compliance Check Status (e.g., for anti-kickback regulations)  
23.Protocol:  
    The Protocol object represents the detailed plan for conducting the clinical trial. It is a  
    crucial document that outlines the study's objectives, design, methodology, statistical  
    considerations, and organization.  
       a. 1 Study  
       b. 1-Many Tag  
       c. 1-Many Document  
       d. 1 Person (Principal Investigator)  
       e. 1-Many Person (Protocol Authors)  
       f. 1-Many Objective  
       g. 1-Many Endpoint  
       h. 1-Many Inclusion Criteria  
       i. 1-Many Exclusion Criteria  
       j. 1-Many Visit  
       k. 1-Many Treatment Arm  
       l. 1-Many Investigational Product  
       m. 1 Safety Monitoring Plan  
       n. 1 Statistical Analysis Plan  
       o. 1-Many Amendment  
       p. 1-Many Task  
       q. 1-Many Audit Trail Entry  
       r. 1-Many Comment  
       s. 1-Many Person (Protocol Reviewers)  
       t. 1-Many Standard Operating Procedure (SOP)  
       u. 1-Many Regulatory Submission  
       v. 1-Many Milestone  
       w. 1-Many CRF (Case Report Form)  
       x. 1-Many Questionnaire  
       y. 1-Many Lab Test  
       z. 1-Many Procedure  
       aa.1-Many Adverse Event Type (expected)  
       bb.1-Many Deviation Type (allowable deviations)  
       cc.1 Budget  
       dd.1-Many Site (approved for the study)  
       ee.1-Many Equipment (required for the study)  
       ff. 1-Many Sample (types to be collected)  
       gg.1-Many Data Transfer Specification  
       hh.1-Many Report (types to be generated)  
       ii. 1-Many Monitoring Plan  
         jj. 1-Many Risk Assessment  
         kk.1-Many Training Requirement  
         ll. 1-Many Informed Consent Version  
         mm. 1-Many Schedule of Assessments (SOA)  
         nn.1-Many Oversight Body (e.g., Data Safety Monitoring Board)  
         oo.1-Many Publication Plan  
24.Investigational Product:  
    The Investigational Product object represents the drug, biologic, or device being tested  
    in the clinical trial. It's a crucial component that is central to the study's purpose and  
    execution.  
         a. 1-Many Study  
         b. 1-Many Tag  
         c. 1-Many Protocol  
         d. 1-Many Site (where the product is used)  
         e. 1-Many Participant (who receive the product)  
         f. 1-Many Visit (where product is administered)  
         g. 1-Many Shipment  
         h. 1-Many Storage Location  
         i. 1-Many Document (e.g., Investigator's Brochure, Package Insert)  
         j. 1-Many Adverse Event  
         k. 1-Many Serious Adverse Event  
         l. 1-Many Deviation (related to product administration)  
         m. 1-Many Task (related to product management)  
         n. 1-Many Audit Trail Entry  
         o. 1-Many Comment  
         p. 1-Many Batch  
         q. 1-Many Dosage Form  
         r. 1-Many Route of Administration  
         s. 1-Many Pharmacy  
         t. 1-Many Inventory Record  
         u. 1-Many Temperature Log  
         v. 1-Many Accountability Log  
         w. 1-Many Return/Destruction Record  
         x. 1-Many Randomization Code  
         y. 1-Many Unblinding Record  
         z. 1-Many Manufacturing Record  
         aa.1-Many Quality Control Test  
         bb.1-Many Regulatory Submission  
         cc.1-Many Safety Report  
         dd.1-Many Drug Interaction  
         ee.1-Many Concomitant Medication (restrictions/interactions)  
         ff. 1-Many Lab Test (for monitoring)  
         gg.1-Many Procedure (for administration)  
         hh.1-Many Equipment (for storage/administration)  
        ii. 1-Many Training Record (for handling/administration)  
        jj. 1-Many Monitoring Visit (product-related checks)  
        kk.1-Many Query (related to product data)  
        ll. 1-Many CRF (for recording product-related data)  
        mm. 1-Many Milestone (related to product availability/use)  
        nn.1-Many Risk Assessment  
        oo.1-Many CAPA (Corrective and Preventive Action)  
25.Investigational Device:  
    The Investigational Device object represents medical devices used in clinical trials,  
    including implantable, wearable, disposable, or diagnostic devices.  
        a. 1-Many Study  
        b. 1-Many Site (where the device is used)  
        c. 1 Manufacturer  
        d. 1-Many Participant (who receive or use the device)  
        e. 1-Many Visit (where device is used or data is collected)  
        f. 1-Many Shipment  
        g. 1-Many Storage Location  
        h. 1-Many Document (e.g., user manuals, technical specifications)  
        i. 1-Many Adverse Event  
        j. 1-Many Deviation (related to device use or malfunction)  
        k. 1-Many Task (related to device management)  
        l. 1-Many Audit Trail Entry  
        m. 1-Many Training Record (for device use)  
        n. 1-Many Maintenance Record  
        o. 1-Many Calibration Record  
        p. 1-Many Quality Control Check  
        q. 1-Many Data Transfer (for data collected by the device)  
        r. 1-Many Regulatory Submission  
        s. 1-Many Safety Report  
        t. 1-Many Inventory Record  
26.Plan:  
    The Plan object represents various types of plans used in clinical trials, such as  
    monitoring plans, data management plans, statistical analysis plans, and risk  
    management plans. These plans outline strategies and procedures for different aspects  
    of the trial.  
        a. 1 Study  
        b. 1-Many Tag  
        c. 1 Protocol  
        d. 1-Many Document  
        e. 1-Many Person (authors, reviewers, approvers)  
        f. 1-Many Task  
        g. 1-Many Milestone  
        h. 1-Many Visit  
        i. 1-Many Site  
        j. 1-Many CRF (Case Report Form)  
        k. 1-Many Procedure  
        l. 1-Many Lab Test  
        m. 1-Many Adverse Event Type  
        n. 1-Many Deviation Type  
        o. 1-Many Risk Assessment  
        p. 1-Many Monitoring Visit  
        q. 1-Many Audit  
        r. 1-Many Report  
        s. 1-Many Data Transfer  
        t. 1-Many Statistical Analysis  
        u. 1-Many Quality Control Check  
        v. 1-Many Training Requirement  
        w. 1-Many Oversight Body  
        x. 1-Many Regulatory Submission  
        y. 1-Many Budget Item  
        z. 1-Many Investigational Product  
        aa.1-Many Sample  
        bb.1-Many Equipment  
        cc.1-Many System  
        dd.1-Many Service  
        ee.1-Many CAPA (Corrective and Preventive Action)  
        ff. 1-Many Amendment  
        gg.1-Many Audit Trail Entry  
        hh.1-Many Comment  
        ii. 1-Many SOP (Standard Operating Procedure)  
        jj. 1-Many Questionnaire  
        kk.1-Many Endpoint  
        ll. 1-Many Data Management Rule  
        mm. 1-Many Publication Plan  
        nn.1-Many Archiving Strategy  
27.Oversight Body:  
    The Oversight Body object represents committees or groups responsible for monitoring  
    various aspects of clinical trials, such as safety, data integrity, and ethical conduct.  
    Examples include Data Safety Monitoring Boards (DSMB), Independent Data Monitoring  
    Committees (IDMC), and Ethics Committees/Institutional Review Boards (EC/IRB).  
        a. 1-Many Study  
        b. 1-Many Protocol  
        c. 1-Many Person (committee members)  
        d. 1-Many Document (e.g., charters, meeting minutes, reports)  
        e. 1-Many Meeting  
        f. 1-Many Review  
        g. 1-Many Recommendation  
        h. 1-Many Decision  
        i. 1-Many Adverse Event (reviewed)  
        j. 1-Many Serious Adverse Event (reviewed)  
        k. 1-Many Safety Report  
        l. 1-Many Interim Analysis  
        m. 1-Many Protocol Amendment (reviewed)  
        n. 1-Many Informed Consent (reviewed versions)  
        o. 1-Many Task  
        p. 1-Many Milestone  
        q. 1-Many Audit Trail Entry  
        r. 1-Many Comment  
        s. 1-Many Deviation (reviewed)  
        t. 1-Many Data Transfer (for data reviews)  
        u. 1-Many Report (generated or reviewed)  
        v. 1-Many Notification Rule  
        w. 1-Many Communication Log  
        x. 1-Many Training Record  
        y. 1-Many Conflict of Interest Disclosure  
        z. 1-Many Regulatory Submission (related to committee actions)  
        aa.1-Many Visit (for on-site reviews, if applicable)  
        bb.1-Many Query (raised during reviews)  
        cc.1-Many CAPA (Corrective and Preventive Actions recommended)  
        dd.1-Many Risk Assessment (reviewed or conducted)  
28.System:  
    The System object represents software applications, databases, or other technological  
    platforms used in the conduct and management of clinical trials. This could include  
    Electronic Data Capture (EDC) systems, Clinical Trial Management Systems (CTMS),  
    Interactive Response Technology (IRT), safety databases, and other specialized  
    software used in clinical research.  
        a. 1-Many Study  
        b. 1-Many Site (where the system is used)  
        c. 1-Many Person (users of the system)  
        d. 1-Many User Role (defining access levels within the system)  
        e. 1-Many Document (e.g., user manuals, validation documents)  
        f. 1-Many Training Record  
        g. 1-Many Data Transfer (data imports/exports)  
        h. 1-Many Audit Trail Entry  
        i. 1-Many Task (related to system use or maintenance)  
        j. 1-Many CRF (Case Report Form, if applicable)  
        k. 1-Many Query (if the system handles data queries)  
        l. 1-Many Report  
        m. 1-Many Notification Rule  
        n. 1-Many Integration (with other systems)  
        o. 1-Many Validation Record  
        p. 1-Many Issue (system-related issues or bugs)  
         q. 1-Many Change Request  
         r. 1-Many Backup  
         s. 1-Many Access Log  
         t. 1-Many Security Assessment  
         u. 1-Many Compliance Check (e.g., 21 CFR Part 11 compliance)  
         v. 1-Many SOP (Standard Operating Procedure for system use)  
         w. 1-Many Risk Assessment  
         x. 1-Many CAPA (Corrective and Preventive Action related to system issues)  
         y. 1-Many Configuration Setting  
         z. 1-Many Data Dictionary  
         aa.1-Many API (Application Programming Interface)  
         bb.1-Many Service Level Agreement  
         cc.1-Many Downtime Record  
29.System Configuration:  
    The System Configuration object represents the specific settings, customizations, and  
    extensions of a system at various organizational levels (sponsor, organizational unit,  
    study, or site).  
         a. 1 System  
         b. 0-1 Sponsor  
         c. 0-1 Organizational Unit  
         d. 0-1 Study  
         e. 0-1 Site  
         f. 0-1 Parent System Configuration  
         g. 0-Many Child System Configurations  
         h. 1-Many Person (who can access this configuration)  
         i. 1-Many Document (related to this configuration)  
         j. 1-Many Audit Trail Entry  
         k. 1-Many Task (related to configuration management)  
         l. 1-Many Integration (with other systems)  
         m. 1-Many User Role (defining access levels for this configuration)  
         n. 1-Many Training Record (for users of this configuration)  
         o. 1-Many Change Request (for this configuration)  
30.Service:  
    The Service object represents various professional services provided in support of  
    clinical trials. These could include data management, biostatistics, medical writing,  
    pharmacovigilance, site monitoring, and other specialized services that are often  
    contracted to support the conduct of clinical trials.  
         a. 1-Many Study  
         b. 1-Many System (service providers)  
         c. 1-Many Contract  
         d. 1-Many Person (service team members)  
         e. 1-Many Task  
         f. 1-Many Milestone  
         g. 1-Many Document (e.g., service reports, SOPs)  
        h. 1-Many Deliverable  
        i. 1-Many Invoice  
        j. 1-Many Budget Item  
        k. 1-Many Timeline  
        l. 1-Many Quality Control Check  
        m. 1-Many Audit  
        n. 1-Many Training Record  
        o. 1-Many Communication Log  
        p. 1-Many Issue (service-related issues)  
        q. 1-Many Risk Assessment  
        r. 1-Many CAPA (Corrective and Preventive Action)  
        s. 1-Many Performance Metric  
        t. 1-Many SLA (Service Level Agreement)  
        u. 1-Many Change Request  
        v. 1-Many Review (of service quality)  
        w. 1-Many Report  
        x. 1-Many Data Transfer (if applicable)  
        y. 1-Many System (systems used to provide the service)  
        z. 1-Many Audit Trail Entry  
        aa.1-Many Comment  
        bb.1-Many Notification Rule  
        cc.1-Many Meeting (service-related meetings)  
        dd.1-Many Compliance Check  
31.Service Configuration:  
    The Service Configuration object represents the specific arrangements, customizations,  
    and extensions of a service at various organizational levels (sponsor, organizational unit,  
    study, or site).  
        a. 1 Service  
        b. 0-1 Sponsor  
        c. 0-1 Organizational Unit  
        d. 0-1 Study  
        e. 0-1 Site  
        f. 0-1 Parent Service Configuration  
        g. 0-Many Child Service Configurations  
        h. 1-Many Person (involved in this specific configuration)  
        i. 1-Many Document (related to this configuration, e.g., specific agreements, work  
            orders)  
        j. 1-Many Audit Trail Entry  
        k. 1 Contract (specific to this configuration level)  
        l. 1 Budget (specific to this configuration level)  
        m. 1-Many Task (related to this configuration)  
        n. 1-Many Milestone (specific to this configuration)  
        o. 1-Many Deliverable (specific to this configuration)  
        p. 1-Many Quality Control Check  
       q. 1-Many Training Record (for this specific configuration)  
       r. 1-Many Communication Log  
       s. 1-Many Issue  
       t. 1-Many Risk Assessment  
32.Study Startup Package:  
    The Study Startup Package object represents the comprehensive collection of  
    documents, materials, and information needed to initiate a clinical trial at a site. It  
    consists of both general (study-wide) and site-specific components.  
       a. 1 Study  
       b. 1 Site  
       c. 1-Many Essential Document  
                i. 1 Investigator Brochure  
                ii. 1 Protocol  
                iii. 1-Many Informed Consent Form Template  
                iv. 1-Many Regulatory Submission Document  
       d. 1-Many Legal and Contractual Document  
                i. 1 Clinical Trial Agreement  
                ii. 1 Confidentiality Agreement  
                iii. 1 Financial Disclosure Agreement  
                iv. 1 Publication Agreement  
                v. 1 Material Transfer Agreement  
                vi. 1 Data Transfer Agreement  
       e. 1-Many Operational Document  
                i. 1 Site Activation Manual  
                ii. 1 Monitoring Plan  
                iii. 1 Safety Reporting Instructions  
                iv. 1 Trial Master File Requirements  
                v. 1 Data Management Plan  
                vi. 1 Randomization and Blinding Procedures  
                vii. 1 Safety and Pharmacovigilance Plan  
                viii.1 Communication Plan  
                ix. 1 Study Timeline  
       f. 1-Many Quality Management Document  
                i. 1 QA and QC Guidelines  
                ii. 1 Monitoring Visit Report Template  
                iii. 1 Site Close-out Instructions  
                iv. 1 Quality Management System Documentation  
       g. 1-Many Training and Support Material  
                i. 1-Many Investigator Meeting Material  
                ii. 1-Many Site Initiation Visit Material  
                iii. 1-Many Regulatory and Ethical Submission Template  
                iv. 1-Many eLearning Module  
                v. 1 FAQ and Reference Guide  
                vi. 1-Many User Manual and Technical Support Documentation  
       h. 1-Many Financial Document  
               i. 1 Budget and Payment Schedule  
               ii. 1-Many Financial Disclosure Form  
               iii. 1 Grant or Contract Agreement  
               iv. 1 Site Cost Workbook  
               v. 1 Coverage Analysis  
               vi. 1-Many Invoicing Instruction and Template  
       i. 1-Many Person (involved in package preparation and review)  
       j. 1-Many Audit Trail Entry  
       k. 1-Many Comment  
       l. 1 Version  
       m. 1 Checklist (for package contents and site readiness)  
       n. 1-Many Task (related to package preparation and distribution)  
       o. 1-Many Milestone (related to package completion and site activation)  
33.Budget:  
    The Budget object represents the financial plan for a clinical trial, detailing the estimated  
    costs and resource allocation for various aspects of the study.  
       a. 1 Study  
       b. 0-Many Site (site-specific budgets)  
       c. 1 Sponsor  
       d. 1-Many Budget Item  
       e. 1-Many Payment Schedule  
       f. 1-Many Currency (for multi-currency budgets)  
       g. 1-Many Document (e.g., budget worksheets, approvals)  
       h. 1-Many Person (budget preparers, approvers)  
       i. 1-Many Audit Trail Entry  
       j. 1-Many Version (for budget revisions)  
       k. 1-Many Comment  
       l. 1-Many Task (budget-related tasks)  
       m. 1-Many Milestone (budget-related milestones)  
       n. 1 Protocol (associated protocol version)  
       o. 1-Many Contract (associated contracts)  
       p. 1-Many System (for outsourced services)  
       q. 1-Many Invoice  
       r. 1-Many Payment  
       s. 1-Many Financial Report  
       t. 1 Approval Status  
       u. 1-Many Budget Category  
       v. 1-Many Cost Center  
       w. 1-Many Funding Source  
       x. 1-Many Exchange Rate (for multi-currency budgets)  
       y. 1-Many Budget Forecast  
       z. 1-Many Budget Variance Analysis  
       aa.1-Many Accrual  
        bb.1-Many Investigational Product Cost  
        cc.1-Many Procedure Cost  
        dd.1-Many Visit Cost  
34.Contract:  
    The Contract object represents the legal agreements between various parties involved in  
    the clinical trial, such as the sponsor, sites, system, and other service providers.  
        a. 1 Study  
        b. 1 Sponsor  
        c. 0-1 Site (for site-specific contracts)  
        d. 0-1 System (for vendor-specific contracts)  
        e. 0-1 Service (for service-specific contracts)  
        f. 1-Many Person (signatories, negotiators, reviewers)  
        g. 1-Many Document (contract documents, amendments)  
        h. 1 Contract Type (e.g., Clinical Trial Agreement, Master Service Agreement)  
        i. 1 Contract Status (e.g., Draft, In Review, Executed, Terminated)  
        j. 1 Effective Date  
        k. 0-1 Expiration Date  
        l. 1-Many Budget (associated budgets)  
        m. 1-Many Payment Schedule  
        n. 1-Many Milestone (contract-related milestones)  
        o. 1-Many Task (contract-related tasks)  
        p. 1-Many Audit Trail Entry  
        q. 1-Many Comment  
        r. 1-Many Version (for contract revisions)  
        s. 1-Many Amendment  
        t. 1-Many Clause (specific contract clauses)  
        u. 1-Many Term (key contract terms)  
        v. 1-Many Obligation (contractual obligations)  
        w. 1-Many Risk (identified contract risks)  
        x. 1-Many Approval (approval workflow)  
        y. 1-Many Signature  
        z. 1-Many Negotiation Record  
        aa.1-Many Legal Review  
        bb.1-Many Compliance Check  
        cc.1-Many Currency (for multi-currency contracts)  
        dd.1-Many Confidentiality Agreement  
        ee.1-Many Indemnification Clause  
35.Schedule of Assessments (SOA):  
     The Schedule of Assessments (SOA) object represents the overall plan and timeline for  
    study-related procedures and data collection activities throughout the clinical trial.  
        a. 1 Study  
        b. 1 Protocol  
        c. 1-Many Arm  
        d. 1-Many Visit  
         e. 1-Many Document (e.g., SOA chart, detailed descriptions)  
         f. 1-Many Person (creators, reviewers)  
         g. 1-Many Version (for SOA revisions)  
         h. 1-Many Audit Trail Entry  
         i. 1-Many Comment  
         j. 1-Many Task (SOA-related tasks)  
         k. 1-Many Milestone (SOA-related milestones)  
         l. 1-Many Amendment (if SOA is changed due to protocol amendments)  
         m. 1 Approval Status  
         n. 1-Many Deviation Type (allowable deviations from the schedule)  
         o. 1 EDC (Electronic Data Capture) System Reference  
36.Endpoint:  
     The Endpoint object represents the key outcomes or measurements that are used to  
    evaluate the efficacy, safety, or other aspects of the intervention being studied in a  
    clinical trial.  
         a. 1 Study  
         b. 1 Protocol  
         c. 1-Many Visit (where endpoint data is collected)  
         d. 1-Many CRF (Case Report Form) (used to collect endpoint data)  
         e. 1-Many Procedure (procedures related to endpoint assessment)  
         f. 1-Many Lab Test (if applicable to the endpoint)  
         g. 1-Many Statistical Analysis Plan (plans for analyzing endpoint data)  
         h. 1-Many Person (staff involved in endpoint definition and assessment)  
         i. 1-Many Document (endpoint-related documentation)  
         j. 1-Many Audit Trail Entry  
         k. 1-Many Comment  
         l. 1-Many Data Point (specific data elements that contribute to the endpoint)  
         m. 0-Many Derived Variable (calculations or derivations used in endpoint  
             assessment)  
         n. 1-Many Quality Control Check (for endpoint data)  
         o. 1-Many Task (related to endpoint data collection or analysis)  
37.Lab Results:  
    The Lab Results object represents the outcomes of laboratory tests performed on  
    specimens collected during the clinical trial.  
         a. 1 Study  
         b. 1 Participant  
         c. 1 Visit  
         d. 1 CRF (Case Report Form)  
         e. 1 Lab Test  
         f. 1 Specimen  
         g. 1 Lab Facility  
         h. 1 Person (who performed the test)  
         i. 1 Person (who reviewed the results)  
         j. 1 Result Status (e.g., Preliminary, Final, Amended)  
        k. 1-Many Document (lab reports, etc.)  
        l. 1-Many Audit Trail Entry  
        m. 1-Many Comment  
        n. 0-Many Discrepancy (Query)  
        o. 0-1 Adverse Event (if result led to AE)  
        p. 1 Normal Range Reference  
        q. 1 Unit of Measurement  
        r. 0-1 Derived Variable (if result is calculated)  
        s. 1 Analysis Method  
        t. 1 Equipment (used for analysis)  
        u. 1-Many Quality Control Check  
        v. 0-1 Repeat Test (if applicable)  
        w. 1 Batch (of tests run together)  
38.Log:  
    The Log object represents a record of events, actions, or observations that occur during  
    the course of a clinical trial.  
        a. 1 Study  
        b. 0-1 Site  
        c. 0-1 Participant  
        d. 1 Log Type (e.g., Communication Log, Training Log, Temperature Log)  
        e. 1 Person (who created the log entry)  
        f. 1-Many Document (related to the log entry)  
        g. 1-Many Audit Trail Entry  
        h. 1-Many Comment  
        i. 0-1 Visit (if log entry is related to a specific visit)  
        j. 0-1 Equipment (if log is related to equipment use or maintenance)  
        k. 0-1 Investigational Product (if log is related to drug accountability)  
        l. 0-1 Shipment (if log is related to shipping/receiving)  
        m. 0-1 Deviation (if log entry is related to a protocol deviation)  
        n. 0-1 Adverse Event (if log entry is related to an AE)  
        o. 0-1 Task (if log entry is related to a specific task)  
        p. 0-1 Monitoring Visit (if log is related to a monitoring visit)  
        q. 0-1 Query (if log entry is related to query resolution)  
        r. 0-1 Training (if log entry is related to training activities)  
        s. 0-1 Communication (if log entry is a communication record)  
        t. 1-Many Tag (for categorizing log entries)  
39.Credential:  
    The Credential object represents qualifications, certifications, or authorizations relevant  
    to the clinical trial, associated with either individuals or sites.  
        a. 0-1 Person  
        b. 0-1 Site  
        c. 1-Many Study  
        d. 1-Many Document  
        e. 1-Many Audit Trail Entry  
         f. 1-Many Comment  
         g. 1 Issuing Authority  
         h. 0-1 Person (who verified the credential)  
         i. 1-Many Task  
         j. 0-Many Regulatory Submission  
         k. 1 Sponsor  
         l. 1-Many Training Record (for person-associated credentials)  
40.Amendment:  
    The Amendment object represents changes or updates made to the study protocol or  
    other key study documents after their initial approval.  
         a. 1 Study  
         b. 1 Protocol  
         c. 1-Many Document  
         d. 1-Many Person (who prepared, reviewed, or approved the amendment)  
         e. 1-Many Regulatory Submission  
         f. 1-Many Site (affected by the amendment)  
         g. 1-Many Task  
         h. 1-Many Milestone  
         i. 1-Many Audit Trail Entry  
         j. 1-Many Comment  
         k. 0-Many Informed Consent (if consent forms need to be updated)  
         l. 0-Many CRF (Case Report Form) (if data collection forms are affected)  
         m. 0-Many Visit (if visit schedule is modified)  
         n. 0-Many Procedure (if procedures are added, removed, or modified)  
         o. 0-Many Investigational Product (if dosing or administration is changed)  
         p. 1-Many Training Record (for staff training on the amendment)  
         q. 0-Many Budget (if amendment affects study costs)  
         r. 0-Many Contract (if contracts need to be updated due to amendment)  
         s. 1 Approval Status  
         t. 1-Many Oversight Body (e.g., IRB/EC that needs to approve the amendment)  
41.Regulatory Submission:  
    The Regulatory Submission object represents the collection of documents and  
    information submitted to regulatory authorities for review and approval in relation to a  
    clinical trial.  
         a. 1 Study  
         b. 1 Sponsor  
         c. 1 Regulatory Authority  
         d. 1-Many Document  
         e. 1-Many Person (involved in preparation, review, or submission)  
         f. 1 Submission Type (e.g., IND, CTA, Protocol Amendment)  
         g. 1-Many Protocol  
         h. 1-Many Amendment  
         i. 1-Many Task  
         j. 1-Many Milestone  
        k. 1-Many Audit Trail Entry  
        l. 1-Many Comment  
        m. 1-Many Version  
        n. 0-Many Site (if site-specific submissions)  
        o. 1-Many Investigational Product  
        p. 1-Many Safety Report  
        q. 0-Many Adverse Event  
        r. 0-Many Serious Adverse Event  
        s. 1-Many Credential (of key study personnel)  
        t. 1-Many Oversight Body (e.g., IRB/EC approvals)  
42.Audit:  
    The Audit object represents a systematic examination of trial-related activities and  
    documents to determine whether these activities were conducted, and data were  
    recorded, analyzed, and accurately reported according to the protocol, sponsor's  
    standard operating procedures, Good Clinical Practice, and applicable regulatory  
    requirements.  
        a. 1 Study  
        b. 0-1 Site  
        c. 1 Sponsor  
        d. 1-Many Person (auditors and auditees)  
        e. 1-Many Document  
        f. 1 Audit Plan  
        g. 1-Many Audit Finding  
        h. 1-Many Task  
        i. 1-Many Milestone  
        j. 1-Many Audit Trail Entry  
        k. 1-Many Comment  
        l. 1 Audit Report  
        m. 1-Many CAPA (Corrective and Preventive Action)  
        n. 1-Many Visit (audit visits)  
        o. 0-Many CRF (Case Report Form) (reviewed during audit)  
        p. 0-Many Informed Consent (reviewed during audit)  
        q. 0-Many Investigational Product (if drug accountability is audited)  
        r. 0-Many Deviation (identified or reviewed during audit)  
        s. 1-Many Training Record (related to audit preparation or findings)  
        t. 0-Many Regulatory Submission (if reviewed during audit)  
43.Report:  
    The Report object represents various types of formal documents that summarize,  
    analyze, or present information related to the clinical trial.  
        a. 1 Study  
        b. 0-1 Site (for site-specific reports)  
        c. 1 Sponsor  
        d. 1-Many Person (authors, reviewers)  
        e. 1 Report Type (e.g., Interim Analysis, Safety Report, Final Study Report)  
         f. 1-Many Document  
         g. 1-Many Data Point  
         h. 1-Many Statistical Analysis  
         i. 0-Many Adverse Event  
         j. 0-Many Serious Adverse Event  
         k. 1-Many CRF (Case Report Form) (data sources)  
         l. 1-Many Lab Result  
         m. 1-Many Audit Trail Entry  
         n. 1-Many Comment  
         o. 1-Many Version  
         p. 1-Many Review  
         q. 1-Many Approval  
         r. 0-Many Regulatory Submission  
         s. 1-Many Task  
         t. 1-Many Milestone  
44.Shipment:  
    The Shipment object represents the physical transfer of materials, such as  
    investigational products, lab kits, or other supplies, between locations involved in the  
    clinical trial.  
         a. 1 Study  
         b. 1 Sender (Site, Depot, or Vendor)  
         c. 1 Receiver (Site, Depot, or Vendor)  
         d. 1-Many Investigational Product  
         e. 1-Many Supply Item  
         f. 1-Many Sample  
         g. 1-Many Document (e.g., shipping manifests, chain of custody forms)  
         h. 1 Shipping Vendor  
         i. 1-Many Person (involved in preparation, sending, or receiving)  
         j. 1-Many Task  
         k. 1-Many Audit Trail Entry  
         l. 1-Many Comment  
         m. 1 Temperature Log  
         n. 1-Many Equipment (e.g., temperature monitors)  
         o. 0-Many Deviation (if shipping issues occur)  
         p. 1 Tracking Number  
         q. 1-Many Customs Document  
         r. 1 Invoice  
         s. 1 Packing List  
         t. 1-Many Quality Control Check  
         u. 0-Many Credential (e.g., import/export licenses, handling certifications)  
45.Questionnaire:  
    The Questionnaire object represents a structured set of questions used to collect  
    standardized data from participants in a clinical trial. (e.g., Standard, COA/eCOA,  
    PRO/ePRO, ClinRO, ObsRO, Patient Diary)  
        a. 1 Study  
        b. 1-Many Visit  
        c. 1-Many CRF (Case Report Form)  
        d. 1-Many Participant  
        e. 1-Many Person (who designed or reviewed the questionnaire)  
        f. 1-Many Document (e.g., questionnaire form, completion guidelines)  
        g. 1-Many Data Point  
        h. 1-Many Audit Trail Entry  
        i. 1-Many Comment  
        j. 1-Many Version  
        k. 1-Many Translation (for multi-language studies)  
        l. 1-Many Validation Record  
        m. 0-Many Deviation (if questionnaire not completed per protocol)  
        n. 1-Many Task  
        o. 0-Many Query (related to questionnaire responses)  
        p. 1 Copyright Information (if applicable)  
        q. 1-Many Scoring Algorithm  
        r. 1-Many Derived Variable  
        s. 1-Many Statistical Analysis Plan  
        t. 0-Many Regulatory Submission (if questionnaire is part of submission)  
46.Other Clinical Event:  
    The Other Clinical Event object represents significant occurrences during a clinical trial  
    that are not captured by other specific objects (like Adverse Events or Deviations), but  
    are still important to record and track.  
        a. 1 Study  
        b. 1 Participant  
        c. 0-1 Visit  
        d. 1 Person (who reported or recorded the event)  
        e. 1-Many Document  
        f. 1-Many CRF (Case Report Form)  
        g. 1-Many Audit Trail Entry  
        h. 1-Many Comment  
        i. 0-Many Task  
        j. 0-1 Investigational Product  
        k. 0-1 Procedure  
        l. 0-1 Lab Result  
        m. 0-Many Query  
        n. 1 Event Category  
        o. 0-1 Medical History Item  
        p. 0-1 Concomitant Medication  
        q. 0-1 Physical Examination  
        r. 0-1 Vital Sign Measurement  
        s. 0-1 Endpoint Assessment  
        t. 0-1 Protocol Milestone  
47.CAPA:  
    The CAPA (Corrective and Preventive Action) object represents the systematic approach  
    to addressing and preventing quality issues identified during the clinical trial process.  
         a. 1 Study  
         b. 0-1 Site  
         c. 1 Sponsor  
         d. 1-Many Person (involved in CAPA creation, implementation, and review)  
         e. 0-Many Deviation (that triggered or is addressed by the CAPA)  
         f. 0-Many Query (that led to the identification of an issue requiring CAPA)  
         g. 1-Many Document  
         h. 1-Many Task  
         i. 1-Many Audit Trail Entry  
         j. 1-Many Comment  
         k. 0-1 Audit (if CAPA resulted from an audit finding)  
         l. 0-1 Monitoring Visit (if CAPA resulted from a monitoring finding)  
         m. 0-Many Training Record (if CAPA involves additional training)  
         n. 1-Many Quality Control Check  
         o. 1-Many Corrective Action  
         p. 1-Many Preventive Action  
         q. 1-Many Milestone  
         r. 1 Effectiveness Check  
         s. 0-Many Regulatory Submission (if CAPA is reported to regulatory authorities)  
48.Date:  
    The Date object represents specific calendar dates that are significant in the context of a  
    clinical trial.  
         a. 1-Many Study  
         b. 1-Many Visit  
         c. 1-Many Milestone  
         d. 1-Many Task  
         e. 0-Many Participant (for participant-specific dates)  
         f. 0-Many Site (for site-specific dates)  
         g. 1-Many Audit Trail Entry  
         h. 1-Many Comment  
         i. 0-Many Protocol (for protocol-related dates)  
         j. 0-Many Amendment  
         k. 0-Many Regulatory Submission  
         l. 0-Many Adverse Event  
         m. 0-Many Deviation  
         n. 0-Many Monitoring Visit  
         o. 0-Many Shipment  
         p. 0-Many Investigational Product (for expiration dates)  
         q. 0-Many Contract (for contract-related dates)  
         r. 0-Many Budget (for budget-related dates)  
         s. 0-Many Payment  
        t. 0-Many Report  
49.Sample:  
    The Sample object represents biological specimens collected from participants during  
    the clinical trial for analysis or storage.  
        a. 1 Study  
        b. 1 Participant  
        c. 1 Visit  
        d. 1 Collection Procedure  
        e. 1 Person (who collected the sample)  
        f. 1 Site (where sample was collected)  
        g. 1-Many Lab Test  
        h. 1-Many Lab Result  
        i. 1-Many Shipment  
        j. 1 Storage Location  
        k. 1-Many Audit Trail Entry  
        l. 1-Many Comment  
        m. 1-Many Document (e.g., lab requisition forms, chain of custody)  
        n. 0-Many Deviation (if sample collection deviated from protocol)  
        o. 1 Sample Type  
        p. 1 Processing Method  
        q. 1 Preservation Method  
        r. 1-Many Quality Control Check  
        s. 1-Many Task (related to sample management)  
        t. 0-Many Query (related to sample collection or processing)  
50.Equipment:  
     The Equipment object represents devices, instruments, or apparatus used in the  
    conduct of the clinical trial.  
        a. 1-Many Study  
        b. 1-Many Site  
        c. 1-Many Person (responsible for or trained on the equipment)  
        d. 1 Equipment Type  
        e. 1-Many Procedure  
        f. 1-Many Maintenance Record  
        g. 1-Many Calibration Record  
        h. 1-Many Document (e.g., user manuals, certificates)  
        i. 1-Many Training Record  
        j. 1-Many Audit Trail Entry  
        k. 1-Many Comment  
        l. 1-Many Task (related to equipment management)  
        m. 0-Many Deviation (if equipment malfunction leads to protocol deviation)  
        n. 1-Many Quality Control Check  
        o. 1-Many Shipment (for equipment transport)  
        p. 0-Many Lab Test  
        q. 0-Many Sample (if used in sample collection or processing)  
       r. 1 Vendor  
       s. 1-Many Inventory Record  
       t. 1-Many Credential (certifications or approvals for the equipment)  
51.Data Transfer:  
    The Data Transfer object represents the process of moving data between different  
    systems or parties involved in the clinical trial.  
       a. 1 Study  
       b. 1 Sender (e.g., Site, Vendor, Sponsor)  
       c. 1 Receiver (e.g., Site, Vendor, Sponsor)  
       d. 1 Data Transfer Type (e.g., EDC export, lab data import)  
       e. 1-Many Document (e.g., data transfer specifications, logs)  
       f. 1-Many Person (involved in the transfer process)  
       g. 1-Many System (source and destination systems)  
       h. 1-Many Audit Trail Entry  
       i. 1-Many Comment  
       j. 1-Many Task  
       k. 1 Data Transfer Status  
       l. 1-Many Quality Control Check  
       m. 0-Many Deviation (if transfer doesn't meet protocol requirements)  
       n. 1-Many Data Point  
       o. 0-Many Query (related to transferred data)  
       p. 1 Transfer Method  
       q. 1-Many Validation Record  
       r. 1 Data Cut-off Date  
       s. 1-Many Security Measure  
       t. 1-Many Regulatory Compliance Check  
52.User Role:  
    The User Role object represents the set of permissions and access rights assigned to  
    users within the clinical trial management system.  
       a. 1-Many Person  
       b. 1-Many Study  
       c. 1-Many Site  
       d. 1-Many System  
       e. 1-Many Permission  
       f. 1-Many Document (e.g., role descriptions, SOPs)  
       g. 1-Many Audit Trail Entry  
       h. 1-Many Comment  
       i. 1 Sponsor  
       j. 1-Many Task (related to role management)  
       k. 1-Many Training Record  
       l. 1-Many Credential (required for the role)  
       m. 1-Many Access Log  
       n. 1-Many Data Transfer (permissions for data transfer)  
       o. 1-Many Report (access to specific reports)  
        p. 1-Many CRF (Case Report Form) (data entry/review rights)  
        q. 1-Many Query (rights to create/respond to queries)  
        r. 1-Many Monitoring Visit (rights related to monitoring)  
        s. 1-Many Regulatory Submission (access to submission data)  
        t. 1-Many Quality Control Check (rights to perform or review QC)  
53.Inclusion Criteria:  
    The Inclusion Criteria object represents the specific characteristics that potential  
    participants must have to be eligible for participation in the clinical trial.  
        a. 1 Study  
        b. 1 Protocol  
        c. 1-Many Amendment (if criteria are modified)  
        d. 1-Many Participant (for eligibility assessment)  
        e. 1-Many CRF (Case Report Form)  
        f. 1-Many Screening Procedure  
        g. 1-Many Lab Test  
        h. 1-Many Document  
        i. 1-Many Audit Trail Entry  
        j. 1-Many Comment  
        k. 1-Many Version  
        l. 1-Many Person (involved in defining or assessing criteria)  
        m. 0-Many Query (related to inclusion criteria assessment)  
        n. 0-Many Deviation (if criteria are not properly applied)  
        o. 1-Many Data Point (used to assess criteria)  
        p. 1-Many Visit (where criteria are assessed)  
        q. 0-Many Regulatory Submission  
        r. 1-Many Statistical Analysis Plan  
        s. 1-Many Training Record (for staff training on criteria)  
        t. 1-Many Task (related to criteria assessment)  
54.Exclusion Criteria:  
    The Exclusion Criteria object represents the specific characteristics that disqualify  
    potential participants from participating in the clinical trial.  
        a. 1 Study  
        b. 1 Protocol  
        c. 1-Many Amendment (if criteria are modified)  
        d. 1-Many Participant (for eligibility assessment)  
        e. 1-Many CRF (Case Report Form)  
        f. 1-Many Screening Procedure  
        g. 1-Many Lab Test  
        h. 1-Many Document  
        i. 1-Many Audit Trail Entry  
        j. 1-Many Comment  
        k. 1-Many Version  
        l. 1-Many Person (involved in defining or assessing criteria)  
        m. 0-Many Query (related to exclusion criteria assessment)  
        n. 0-Many Deviation (if criteria are not properly applied)  
        o. 1-Many Data Point (used to assess criteria)  
        p. 1-Many Visit (where criteria are assessed)  
        q. 0-Many Regulatory Submission  
        r. 1-Many Statistical Analysis Plan  
        s. 1-Many Training Record (for staff training on criteria)  
        t. 1-Many Task (related to criteria assessment)  
55.Monitoring Visit:  
    The Monitoring Visit object represents the on-site or remote review of clinical trial  
    conduct and progress by a clinical research associate (CRA) or monitor.  
        a. 1 Study  
        b. 1 Site  
        c. 1-Many Person (monitors and site staff involved)  
        d. 1 Visit Type (e.g., Site Initiation, Interim, Close-out)  
        e. 1-Many Document (e.g., monitoring reports, follow-up letters)  
        f. 1-Many CRF (Case Report Form) reviewed  
        g. 1-Many Participant record reviewed  
        h. 1-Many Source Document Verified  
        i. 1-Many Query generated or resolved  
        j. 1-Many Deviation identified or reviewed  
        k. 1-Many Task  
        l. 1-Many Action Item  
        m. 1-Many Audit Trail Entry  
        n. 1-Many Comment  
        o. 1 Monitoring Plan  
        p. 1-Many Investigational Product accountability check  
        q. 1-Many Informed Consent review  
        r. 1-Many Regulatory Document review  
        s. 1-Many Training Record review  
        t. 1-Many CAPA (Corrective and Preventive Action) reviewed or initiated  
56.Serious Adverse Events (SAEs):  
    The Serious Adverse Events (SAEs) object represents severe adverse events that occur  
    during the clinical trial that meet specific criteria for seriousness.  
        a. 1 Study  
        b. 1 Participant  
        c. 1 Site  
        d. 1-Many Person (reporters, reviewers)  
        e. 1 Adverse Event (the AE that was determined to be serious)  
        f. 1-Many Document (e.g., SAE reports, medical records)  
        g. 1-Many CRF (Case Report Form)  
        h. 1-Many Audit Trail Entry  
        i. 1-Many Comment  
        j. 1-Many Version (of SAE report)  
        k. 1 Investigational Product  
       l. 1-Many Lab Result  
       m. 1-Many Task  
       n. 1-Many Regulatory Submission  
       o. 1 Safety Review Committee assessment  
       p. 1-Many Follow-up  
       q. 1 Causality Assessment  
       r. 1 Expectedness Assessment  
       s. 1-Many Concomitant Medication  
       t. 1-Many Query

Object Attributes:  
  1\. Sponsor:  
         a. sponsorId  
         b. sponsorName  
         c. sponsorType (e.g., PHARMACEUTICAL, ACADEMIC, GOVERNMENT, OTHER)  
         d. legalName  
         e. duns (Data Universal Numbering System)  
         f. address  
         g. city  
         h. state  
         i. country  
         j. postalCode  
         k. phone  
         l. email  
         m. website  
         n. primaryContactId  
         o. regulatoryContactId  
         p. financialContactId  
         q. status (e.g., ACTIVE, INACTIVE)  
         r. creationDate  
         s. lastModifiedDate  
         t. lastModifiedBy  
  2\. Tag:  
         a. tagId  
         b. tagLabel  
         c. tagDescription  
         d. tagPrompt  
         e. tagColor (for visual organization in the UI)  
  3\. Study:  
         a. studyId (Unique identifier for the study)  
         b. studyTitle (Official title of the study)  
        c. studyDescription (Brief description of the study)  
        d. studyType (e.g., INTERVENTIONAL, OBSERVATIONAL)  
        e. studyPhase (e.g., PHASE1, PHASE2, PHASE3, PHASE4)  
        f. studyStatus (e.g., PLANNED, ACTIVE, COMPLETED, TERMINATED)  
        g. startDate (Date when the study started)  
        h. endDate (Date when the study ended or is expected to end)  
        i. sponsorId (Identifier of the study sponsor)  
        j. protocolId (Identifier of the study protocol)  
        k. acronym (Short name or acronym for the study)  
        l. conditionStudied (Primary condition or disease being studied)  
        m. interventionModel (e.g., SINGLE\_GROUP, PARALLEL, CROSSOVER)  
        n. numberOfArms (Number of study arms)  
        o. enrollmentType (e.g., ACTUAL, ANTICIPATED, TARGET)  
        p. enrollmentCount (Number of participants enrolled)  
        q. primaryCompletionDate (Date of primary outcome measure completion)  
        r. studyFirstSubmitDate (Date of first submission to regulatory authority)  
        s. lastUpdateSubmitDate (Date of most recent update submission)  
        t. responsibleParty (Name of the responsible party)  
        u. nctId (NCT number from clinical trials dot gov)  
        v. tags (array of tagId)  
4\. Site:  
        a. siteId (Unique identifier for the site)  
        b. siteNumber (Number assigned to the site within the study)  
        c. siteName (Name of the research site)  
        d. siteType (e.g., HOSPITAL, CLINIC, RESEARCH\_CENTER)  
        e. siteStatus (e.g., PLANNED, ACTIVE, CLOSED)  
        f. principalInvestigatorId (Identifier of the principal investigator)  
        g. address (Physical address of the site)  
        h. city  
        i. state  
        j. country  
        k. postalCode  
        l. phone  
        m. email  
        n. activationDate (Date when the site was activated for the study)  
        o. deactivationDate (Date when the site was deactivated, if applicable)  
        p. enrollmentTarget (Target number of participants for this site)  
        q. actualEnrollment (Actual number of participants enrolled at this site)  
        r. lastMonitoringVisitDate (Date of the most recent monitoring visit)  
        s. irbId (id of Institutional Review Board or Ethics Committee)  
        t. regulatoryAuthority (Relevant regulatory authority for this site)  
        u. tags (array of tagId)  
5\. Visit:  
        a. visitId  
       b. studyId  
       c. siteId  
       d. participantId  
       e. visitNumber  
       f. visitName  
       g. visitType  
       h. scheduledDate  
       i. actualDate  
       j. visitStatus  
       k. windowStart  
       l. windowEnd  
       m. visitDuration  
       n. visitLocation  
       o. performedBy  
       p. reviewedBy  
       q. dataEntryDate  
       r. dataEntryBy  
       s. lastModifiedDate  
       t. lastModifiedBy  
       u. tags (array of tagId)  
6\. Task:  
       a. taskId  
       b. studyId  
       c. siteId (if site-specific)  
       d. taskType  
       e. taskDescription  
       f. taskStatus (e.g., PENDING, IN\_PROGRESS, COMPLETED, OVERDUE)  
       g. taskPriority (e.g., LOW, MEDIUM, HIGH, URGENT)  
       h. assignedTo  
       i. assignedBy  
       j. creationDate  
       k. dueDate  
       l. completionDate  
       m. estimatedDuration  
       n. actualDuration  
       o. parentTaskId (if this is a subtask)  
       p. relatedEntityType (e.g., VISIT, PARTICIPANT, DEVIATION)  
       q. relatedEntityId  
       r. taskCategory  
       s. lastModifiedDate  
       t. lastModifiedBy  
       u. tags (array of tagId)  
7\. Participant (Subject):  
       a. participantId  
       b. studyId  
       c. siteId  
       d. enrollmentDate  
       e. screeningNumber  
       f. randomizationNumber  
       g. participantStatus (e.g., SCREENED, ENROLLED, COMPLETED, WITHDRAWN)  
       h. gender  
       i. dateOfBirth  
       j. age  
       k. race  
       l. ethnicity  
       m. consentDate  
       n. consentVersion  
       o. lastVisitDate  
       p. expectedCompletionDate  
       q. actualCompletionDate  
       r. completionReason  
       s. withdrawalDate  
       t. withdrawalReason  
       u. tags (array of tagId)  
8\. Discrepancy (Query):  
       a. queryId  
       b. studyId  
       c. siteId  
       d. participantId  
       e. visitId  
       f. crfId  
       g. dataPointId  
       h. queryType  
       i. queryStatus  
       j. queryPriority  
       k. queryText  
       l. responseText  
       m. createdBy  
       n. createdDate  
       o. assignedTo  
       p. dueDate  
       q. resolvedBy  
       r. resolvedDate  
       s. lastModifiedDate  
       t. lastModifiedBy  
       u. tags (array of tagId)  
9\. Deviation:  
       a. deviationId  
       b. studyId  
       c. siteId  
       d. participantId  
       e. visitId  
       f. deviationType  
       g. deviationCategory  
       h. deviationDescription  
       i. deviationDate  
       j. discoveryDate  
       k. reportedBy  
       l. reportedDate  
       m. reviewedBy  
       n. reviewedDate  
       o. deviationStatus  
       p. severity  
       q. impact  
       r. correctiveAction  
       s. preventiveAction  
       t. lastModifiedDate  
       u. lastModifiedBy  
       v. tags (array of tagId)  
10.Screen Fail:  
       a. screenFailId  
       b. studyId  
       c. siteId  
       d. participantId  
       e. screeningNumber  
       f. screenFailDate  
       g. screenFailReason  
       h. failedInclusionCriteria (array)  
       i. failedExclusionCriteria (array)  
       j. investigatorAssessment  
       k. consentStatus  
       l. consentDate  
       m. consentVersion  
       n. rescreeningEligibility  
       o. rescreeningDate  
       p. reportedBy  
       q. reportedDate  
       r. reviewedBy  
       s. reviewedDate  
       t. lastModifiedDate  
       u. lastModifiedBy  
       v. tags (array of tagId)  
11.Person:  
       a. personId  
       b. firstName  
       c. lastName  
       d. middleName  
       e. title  
       f. primaryRoleId  
       g. otherRoles (array of roleIds)  
       h. organization  
       i. department  
       j. email  
       k. phone  
       l. address  
       m. city  
       n. state  
       o. country  
       p. postalCode  
       q. dateOfBirth  
       r. gender  
       s. startDate  
       t. endDate  
       u. status  
       v. tags (array of tagId)  
12.Person Role:  
       a. roleId  
       b. roleName  
       c. roleDescription  
       d. roleCategory (Note: This is a predefined list of general role categories. The actual  
           roles and their specific responsibilities may vary depending on the study or  
           organization. Custom categories can be added as needed.)  
       e. permissions (array of permissionIds)  
       f. createdBy  
       g. creationDate  
       h. modifiedBy  
       i. modificationDate  
       j. status  
       k. tags (array of tagId)  
13.CRF (Case Report Form):  
       a. crfId  
       b. studyId  
       c. crfName  
       d. crfVersion  
       e. crfStatus  
       f. crfType  
       g. visitId  
       h. participantId  
       i. siteId  
       j. completedBy  
       k. completedDate  
       l. reviewedBy  
       m. reviewedDate  
       n. dataEntryMethod  
       o. lastModifiedBy  
       p. lastModifiedDate  
       q. sdvStatus  
       r. sdvBy  
       s. sdvDate  
       t. lockStatus  
       u. tags (array of tagId)  
14.Document:  
       a. documentId  
       b. studyId  
       c. siteId  
       d. documentType  
       e. documentTitle  
       f. documentVersion  
       g. documentStatus  
       h. createdBy  
       i. creationDate  
       j. modifiedBy  
       k. modificationDate  
       l. approvedBy  
       m. approvalDate  
       n. effectiveDate  
       o. expirationDate  
       p. documentLocation  
       q. fileType  
       r. fileSize  
       s. checksum  
       t. retentionPeriod  
       u. tags (array of tagId)  
15.Adverse Event:  
       a. adverseEventId  
       b. studyId  
       c. siteId  
       d. participantId  
       e. aeDescription  
       f. aeStartDate  
        g. aeEndDate  
        h. aeSeverity  
        i. aeSeriousness  
        j. aeRelationship  
        k. aeOutcome  
        l. actionTaken  
        m. expectedness  
        n. reportedBy  
        o. reportedDate  
        p. reviewedBy  
        q. reviewedDate  
        r. medDraCode  
        s. medDraTerm  
        t. followUpRequired  
        u. tags (array of tagId)  
16.Informed Consent:  
        a. consentId  
        b. studyId  
        c. siteId  
        d. participantId  
        e. consentVersion  
        f. consentDate  
        g. consentTime  
        h. consentStatus  
        i. consentMethod  
        j. consentedBy  
        k. consentWitnessedBy  
        l. consentLanguage  
        m. translatorUsed  
        n. translatorName  
        o. reconsentRequired  
        p. reconsentDueDate  
        q. withdrawalDate  
        r. withdrawalReason  
        s. verifiedBy  
        t. verificationDate  
        u. tags (array of tagId)  
17.Action Item:  
        a. actionItemId  
        b. studyId  
        c. siteId  
        d. actionItemDescription  
        e. actionItemStatus  
        f. priority  
       g. dueDate  
       h. assignedTo  
       i. assignedBy  
       j. creationDate  
       k. completionDate  
       l. actionItemCategory  
       m. relatedEntityType  
       n. relatedEntityId  
       o. parentActionItemId  
       p. estimatedEffort  
       q. actualEffort  
       r. resolutionNotes  
       s. lastModifiedDate  
       t. lastModifiedBy  
       u. tags (array of tagId)  
18.Milestone:  
       a. milestoneId  
       b. studyId  
       c. milestoneName  
       d. milestoneDescription  
       e. milestoneType  
       f. plannedDate  
       g. actualDate  
       h. milestoneStatus  
       i. milestoneOwner  
       j. importance  
       k. dependentMilestones (array of milestoneIds)  
       l. prerequisiteMilestones (array of milestoneIds)  
       m. relatedDocuments (array of documentIds)  
       n. creationDate  
       o. createdBy  
       p. lastModifiedDate  
       q. lastModifiedBy  
       r. milestoneCategory  
       s. completionPercentage  
       t. notes  
       u. tags (array of tagId)  
19.Enrollment:  
       a. enrollmentId  
       b. studyId  
       c. siteId  
       d. participantId  
       e. enrollmentDate  
       f. enrollmentStatus  
       g. enrollmentNumber  
       h. randomizationNumber  
       i. stratificationFactors (JSON object)  
       j. eligibilityConfirmationDate  
       k. eligibilityConfirmedBy  
       l. informedConsentId  
       m. screeningFailureReason  
       n. withdrawalDate  
       o. withdrawalReason  
       p. enrollmentVisitId  
       q. protocolVersionAtEnrollment  
       r. investigatorSignatureDate  
       s. enrollmentVerificationStatus  
       t. enrollmentVerifiedBy  
       u. tags (array of tagId)  
20.Payment:  
       a. paymentId  
       b. studyId  
       c. siteId  
       d. participantId (if participant payment)  
       e. paymentAmount  
       f. paymentCurrency  
       g. paymentDate  
       h. paymentStatus  
       i. paymentType  
       j. paymentReason  
       k. relatedVisitId  
       l. relatedProcedureId  
       m. payer  
       n. payee  
       o. paymentMethod  
       p. invoiceNumber  
       q. invoiceDate  
       r. approvalStatus  
       s. approvedBy  
       t. approvalDate  
       u. tags (array of tagId)  
21.Protocol:  
       a. protocolId  
       b. studyId  
       c. protocolNumber  
       d. protocolTitle  
       e. protocolVersion  
       f. protocolStatus (e.g., DRAFT, APPROVED, AMENDED, RETIRED)  
       g. creationDate  
       h. approvalDate  
       i. effectiveDate  
       j. expirationDate  
       k. principalInvestigatorId  
       l. therapeuticArea (e.g., ONCOLOGY, CARDIOLOGY, NEUROLOGY,  
           IMMUNOLOGY)  
       m. studyPhase (e.g., PHASE1, PHASE2, PHASE3, PHASE4)  
       n. studyDesign (e.g., PARALLEL, CROSSOVER, FACTORIAL, ADAPTIVE) (Note:  
           This field describes the overall design structure of the study)  
       o. sampleSize (Note: Total number of participants planned for the study)  
       p. studyDuration (Note: Overall duration of the study in weeks/months/years)  
       q. randomizationMethod (e.g., SIMPLE, BLOCK, STRATIFIED) (Note: Describes  
           the method used to assign participants to treatment groups)  
       r. blindingType (e.g., OPEN\_LABEL, SINGLE\_BLIND, DOUBLE\_BLIND,  
           TRIPLE\_BLIND)  
       s. primaryEndpoint (Note: The main outcome measure that will be used to  
           determine the efficacy of the intervention)  
       t. secondaryEndpoints (array) (Note: Additional outcome measures used to  
           evaluate the intervention's effects)  
       u. tags (array of tagId)  
       v. primaryProtocolDocumentId (Reference to the main protocol document, typically  
           PDF)  
       w. ddfJsonDocumentId (Reference to the Digital Definition Format JSON document)  
       x. relatedDocuments (array of objects) \[ { documentId: string, documentType: string,  
           documentVersion: string } \]  
22.Investigational Product:  
       a. productId  
       b. studyId  
       c. productName  
       d. productType (e.g., DRUG, BIOLOGIC)  
       e. productDescription  
       f. manufacturerId  
       g. batchNumber  
       h. lotNumber  
       i. expirationDate  
       j. storageRequirements  
       k. dosingInstructions  
       l. formulation  
       m. strength  
       n. route (e.g., ORAL, INTRAVENOUS, SUBCUTANEOUS)  
       o. packaging  
       p. blindingStatus (e.g., OPEN\_LABEL, BLINDED)  
       q. controlType (e.g., PLACEBO, ACTIVE, NONE)  
       r. accountabilityRequired (boolean)  
       s. returnRequired (boolean)  
       t. destructionRequired (boolean)  
       u. tags (array of tagId)  
23.Investigational Device:  
       a. deviceId  
       b. studyId  
       c. deviceName  
       d. deviceType (e.g., IMPLANTABLE, WEARABLE, DISPOSABLE, DIAGNOSTIC)  
       e. deviceDescription  
       f. manufacturerId  
       g. modelNumber  
       h. serialNumber  
       i. lotNumber  
       j. expirationDate  
       k. macAddress  
       l. firmwareVersion  
       m. softwareVersion  
       n. storageRequirements  
       o. usageInstructions  
       p. sterilizationStatus  
       q. reuseStatus (e.g., SINGLE\_USE, REUSABLE)  
       r. calibrationRequired (boolean)  
       s. calibrationFrequency  
       t. lastCalibrationDate  
       u. batteryType  
       v. batteryLife  
       w. chargingInstructions  
       x. waterResistanceRating  
       y. mriCompatibility  
       z. disposalInstructions  
       aa.regulatoryClassification  
       bb.certifications (array)  
       cc.accountabilityRequired (boolean)  
       dd.returnRequired (boolean)  
       ee.tags (array of tagId)  
24.Plan:  
       a. planId  
       b. studyId  
       c. planType (e.g., MONITORING, DATA\_MANAGEMENT,  
           STATISTICAL\_ANALYSIS)  
       d. planTitle  
       e. planVersion  
       f. planStatus  
       g. creationDate  
       h. approvalDate  
       i. effectiveDate  
       j. expirationDate  
       k. authorId  
       l. reviewerId  
       m. approverId  
       n. lastModifiedDate  
       o. lastModifiedBy  
       p. documentId  
       q. relatedEntityType  
       r. relatedEntityId  
       s. description  
       t. keywords  
       u. tags (array of tagId)  
25.Oversight Body:  
       a. oversightBodyId  
       b. studyId  
       c. bodyName  
       d. bodyType (e.g., IRB, EC, DSMB, IDMC)  
       e. description  
       f. chairpersonId  
       g. contactPerson  
       h. contactEmail  
       i. contactPhone  
       j. address  
       k. city  
       l. state  
       m. country  
       n. postalCode  
       o. approvalStatus  
       p. approvalDate  
       q. nextReviewDate  
       r. members (array of personIds)  
       s. meetingFrequency  
       t. lastMeetingDate  
       u. tags (array of tagId)  
26.System:  
       a. systemId  
       b. systemName  
       c. systemType (e.g., EDC, CTMS, RTSM, ePRO)  
       d. vendorId  
       e. baseVersion  
       f. status  
       g. validationStatus  
       h. validationDate  
       i. primaryContactId  
       j. technicalContactId  
       k. userManualDocumentId  
       l. validationDocumentId  
       m. accessUrl  
       n. apiDocumentationUrl  
       o. dataBackupFrequency  
       p. disasterRecoveryPlanDocumentId  
       q. tags (array of tagId)  
27.SystemConfiguration:  
       a. configurationId  
       b. systemId  
       c. configurationLevel (e.g., SPONSOR, ORGANIZATIONAL\_UNIT, STUDY, SITE)  
       d. levelId (sponsorId, orgUnitId, studyId, or siteId depending on level)  
       e. configurationVersion  
       f. parentConfigurationId  
       g. configurationStatus  
       h. effectiveDate  
       i. expirationDate  
       j. lastUpgradeDate  
       k. nextUpgradeDate  
       l. customizations (JSON object)  
       m. extensions (JSON object)  
       n. overrides (JSON object)  
       o. accessControls (JSON object)  
       p. integrations (array of integration objects)  
       q. configurationDocumentId  
       r. approvedBy  
       s. approvalDate  
       t. lastModifiedDate  
       u. lastModifiedBy  
       v. tags (array of tagId)  
28.Service:  
       a. serviceId  
       b. serviceName  
       c. serviceType (e.g., DATA\_MANAGEMENT, MONITORING, BIOSTATISTICS)  
       d. providerId  
       e. studyId  
       f. startDate  
       g. endDate  
       h. status  
       i. contractId  
       j. budgetId  
       k. primaryContactId  
       l. escalationContactId  
       m. serviceLevel  
       n. performanceMetrics (JSON object)  
       o. lastReviewDate  
       p. nextReviewDate  
       q. relatedDocuments (array of objects) \[ { documentId: string, documentType: string,  
           documentVersion: string } \]  
       r. notes  
       s. customFields (JSON object)  
       t. lastModifiedDate  
       u. tags (array of tagId)  
29.Service Configuration:  
       a. configurationId  
       b. systemId  
       c. configurationLevel (e.g., SPONSOR, ORGANIZATIONAL\_UNIT, STUDY, SITE)  
       d. levelId (sponsorId, orgUnitId, studyId, or siteId depending on level)  
       e. configurationVersion  
       f. parentConfigurationId  
       g. configurationStatus  
       h. effectiveDate  
       i. expirationDate  
       j. lastUpgradeDate  
       k. nextUpgradeDate  
       l. customizations (JSON object)  
       m. extensions (JSON object)  
       n. overrides (JSON object)  
       o. accessControls (JSON object)  
       p. integrations (array of integration objects)  
       q. configurationDocumentId  
       r. approvedBy  
       s. approvalDate  
       t. lastModifiedDate  
       u. lastModifiedBy  
       v. tags (array of tagId)  
30.Study Startup Package:  
       a. packageId  
       b. studyId  
       c. siteId (null for study-level package)  
       d. packageType (e.g., STUDY\_LEVEL, SITE\_SPECIFIC)  
       e. packageStatus  
       f. creationDate  
       g. lastModifiedDate  
      h. lastModifiedBy  
      i. approvalStatus  
      j. approvalDate  
      k. approvedBy  
      l. sentDate (for site-specific packages)  
      m. receivedDate (for site-specific packages)  
      n. acknowledgedDate (for site-specific packages)  
      o. acknowledgedBy (for site-specific packages)  
      p. parentPackageId (reference to study-level package for site-specific packages)  
      q. relatedDocuments (array of objects) \[ { documentId: string, documentType: string,  
          documentVersion: string } \]  
      r. contractId (for site-specific packages)  
      s. budgetId (for site-specific packages)  
      t. notes  
      u. tags (array of tagId)  
31.Budget:  
      a. budgetId  
      b. studyId  
      c. siteId (null for study-level budget)  
      d. budgetType (e.g., STUDY\_LEVEL, SITE\_SPECIFIC)  
      e. budgetStatus  
      f. budgetVersion  
      g. totalAmount  
      h. currency  
      i. startDate  
      j. endDate  
      k. budgetItems (array of budget item objects)  
      l. paymentSchedule (array of payment schedule objects)  
      m. approvedBy  
      n. approvalDate  
      o. lastModifiedDate  
      p. lastModifiedBy  
      q. relatedDocuments (array of documentIds)  
      r. notes  
      s. overheadRate  
      t. indirectCostRate  
      u. tags (array of tagId)  
32.Contract:  
      a. contractId  
      b. studyId  
      c. siteId (null for study-level contracts)  
      d. contractType (e.g., CLINICAL\_TRIAL\_AGREEMENT,  
          MASTER\_SERVICES\_AGREEMENT)  
      e. contractStatus  
       f. contractVersion  
       g. effectiveDate  
       h. expirationDate  
       i. parties (array of involved parties)  
       j. signatories (array of signatory objects)  
       k. relatedDocuments (array of documentIds)  
       l. amendmentHistory (array of amendment objects)  
       m. termsAndConditions (array of term objects)  
       n. budgetId  
       o. paymentTerms  
       p. confidentialityTerms  
       q. intellectualPropertyTerms  
       r. terminationClauses  
       s. governingLaw  
       t. disputeResolutionMechanism  
       u. tags (array of tagId)  
33.Schedule of Assessments (SOA):  
       a. soaId  
       b. studyId  
       c. protocolVersion  
       d. soaVersion  
       e. approvalStatus  
       f. approvalDate  
       g. approvedBy  
       h. effectiveDate  
       i. expirationDate  
       j. visits (array of visit objects)  
       k. procedures (array of procedure objects)  
       l. assessments (array of assessment objects)  
       m. windows (array of window objects for visit flexibility)  
       n. arms (array of study arm references)  
       o. footnotes (array of footnote objects)  
       p. relatedDocuments (array of documentIds)  
       q. lastModifiedDate  
       r. lastModifiedBy  
       s. comments  
       t. versionHistory (array of previous version references)  
       u. tags (array of tagId)  
34.Endpoint:  
       a. endpointId  
       b. studyId  
       c. endpointType (e.g., PRIMARY, SECONDARY, EXPLORATORY)  
       d. endpointName  
       e. endpointDescription  
       f. measurementUnit  
       g. measurementFrequency  
       h. dataSource (e.g., CRF, LAB\_RESULT, QUESTIONNAIRE)  
       i. analysisMethod  
       j. statisticalPlan  
       k. clinicalRelevance  
       l. validationStatus  
       m. relatedProcedures (array of procedureIds)  
       n. relatedAssessments (array of assessmentIds)  
       o. relatedVisits (array of visitIds)  
       p. derivationFormula (if applicable)  
       q. acceptableRange  
       r. blindingStatus  
       s. regulatoryRelevance  
       t. lastModifiedDate  
       u. tags (array of tagId)  
35.Lab Results:  
       a. labResultId  
       b. studyId  
       c. participantId  
       d. visitId  
       e. siteId  
       f. labId (reference to the performing laboratory)  
       g. specimenId  
       h. collectionDate  
       i. receivedDate  
       j. reportDate  
       k. testCode  
       l. testName  
       m. result  
       n. units  
       o. referenceRangeLow  
       p. referenceRangeHigh  
       q. interpretation (e.g., NORMAL, ABNORMAL, CLINICALLY\_SIGNIFICANT)  
       r. status (e.g., PRELIMINARY, FINAL, AMENDED)  
       s. performedBy  
       t. reviewedBy  
       u. tags (array of tagId)  
36.Log:  
       a. logId  
       b. studyId  
       c. siteId (if applicable)  
       d. logType (e.g., COMMUNICATION, TRAINING, TEMPERATURE,  
           DRUG\_ACCOUNTABILITY)  
       e. entryDate  
       f. entryTime  
       g. enteredBy  
       h. subject  
       i. description  
       j. relatedEntityType (e.g., PARTICIPANT, VISIT, DEVICE)  
       k. relatedEntityId  
       l. attachments (array of documentIds)  
       m. category  
       n. priority  
       o. status  
       p. followUpRequired (boolean)  
       q. followUpDate  
       r. followUpAssignedTo  
       s. reviewedBy  
       t. reviewDate  
       u. tags (array of tagId)  
37.Credential:  
       a. credentialId  
       b. personId  
       c. credentialType (e.g., MEDICAL\_LICENSE, GCP\_CERTIFICATION, CV)  
       d. credentialNumber  
       e. issuingAuthority  
       f. issueDate  
       g. expirationDate  
       h. status (e.g., ACTIVE, EXPIRED, REVOKED)  
       i. verificationStatus  
       j. verificationDate  
       k. verifiedBy  
       l. documentId (reference to uploaded credential document)  
       m. notes  
       n. reminderId (reference to associated reminder)  
       o. lastReviewDate  
       p. nextReviewDate  
       q. applicableStudies (array of studyIds)  
       r. applicableSites (array of siteIds)  
       s. lastModifiedDate  
       t. lastModifiedBy  
       u. tags (array of tagId)  
38.Amendment:  
       a. amendmentId  
       b. studyId  
       c. protocolVersion  
       d. amendmentNumber  
       e. amendmentType (e.g., SUBSTANTIAL, NON\_SUBSTANTIAL)  
       f. status  
       g. creationDate  
       h. approvalDate  
       i. implementationDate  
       j. summary  
       k. rationale  
       l. impactAssessment  
       m. affectedSections (array of protocol sections)  
       n. documentId (reference to amendment document)  
       o. relatedDocuments (array of documentIds)  
       p. regulatorySubmissions (array of submission objects)  
       q. ethicsCommitteeSubmissions (array of submission objects)  
       r. siteNotifications (array of notification objects)  
       s. reConsentRequired (boolean)  
       t. trainingSessions (array of training session objects)  
       u. tags (array of tagId)  
39.Regulatory Submission:  
       a. submissionId  
       b. studyId  
       c. submissionType (e.g., IND, CTA, PROTOCOL\_AMENDMENT)  
       d. regulatoryAuthority  
       e. submissionDate  
       f. status  
       g. dueDate  
       h. actualResponseDate  
       i. outcome  
       j. documents (array of document objects)  
       k. comments  
       l. responsiblePerson  
       m. reviewers (array of personIds)  
       n. relatedAmendmentId  
       o. questions (array of question objects from regulatory authority)  
       p. responses (array of response objects to regulatory authority)  
       q. meetings (array of meeting objects with regulatory authority)  
       r. followUpActions (array of action objects)  
       s. lastModifiedDate  
       t. lastModifiedBy  
       u. tags (array of tagId)  
40.Audit:  
       a. auditId  
       b. studyId  
       c. siteId (if site-specific audit)  
       d. auditType (e.g., INTERNAL, SPONSOR, REGULATORY)  
       e. auditorId (or array of auditorIds)  
       f. auditeeId (or array of auditeeIds)  
       g. startDate  
       h. endDate  
       i. status  
       j. scope  
       k. objectives  
       l. findings (array of finding objects)  
       m. criticalFindings (array of critical finding objects)  
       n. recommendations (array of recommendation objects)  
       o. correctiveActions (array of CAPA objects)  
       p. auditReport (documentId)  
       q. auditPlan (documentId)  
       r. followUpAuditRequired (boolean)  
       s. followUpAuditDate  
       t. closureDate  
       u. tags (array of tagId)  
41.Report:  
       a. reportId  
       b. studyId  
       c. reportType (e.g., INTERIM\_ANALYSIS, SAFETY\_UPDATE,  
           FINAL\_STUDY\_REPORT)  
       d. reportTitle  
       e. version  
       f. status  
       g. creationDate  
       h. approvalDate  
       i. distributionDate  
       j. author  
       k. reviewers (array of personIds)  
       l. approver  
       m. dataCutoffDate  
       n. reportingPeriodStart  
       o. reportingPeriodEnd  
       p. documentId (reference to the report document)  
       q. relatedDocuments (array of documentIds)  
       r. comments  
       s. distributionList (array of recipient objects)  
       t. lastModifiedDate  
       u. tags (array of tagId)  
42.Shipment:  
       a. shipmentId  
       b. studyId  
       c. shipmentType (e.g., INVESTIGATIONAL\_PRODUCT, LAB\_KITS, EQUIPMENT)  
       d. senderId  
       e. recipientId  
       f. originAddress  
       g. destinationAddress  
       h. carrier  
       i. trackingNumber  
       j. shipmentDate  
       k. estimatedDeliveryDate  
       l. actualDeliveryDate  
       m. status  
       n. contents (array of item objects)  
       o. quantity  
       p. temperatureRequirements  
       q. temperatureMonitorId  
       r. customsInformation  
       s. specialHandlingInstructions  
       t. receivedBy  
       u. tags (array of tagId)  
43.Questionnaire:  
       a. questionnaireId  
       b. studyId  
       c. questionnaireName  
       d. questionnaireType (e.g., QUALITY\_OF\_LIFE, SYMPTOMS,  
           PATIENT\_REPORTED\_OUTCOME)  
       e. version  
       f. status  
       g. author  
       h. creationDate  
       i. lastModifiedDate  
       j. language  
       k. translations (array of translation objects)  
       l. validationStatus  
       m. licensingInformation  
       n. copyrightInformation  
       o. administrationMethod (e.g., PAPER, ELECTRONIC, INTERVIEW)  
       p. estimatedCompletionTime  
       q. scoringAlgorithm  
       r. questions (array of question objects)  
       s. skipLogic (array of skip logic rules)  
       t. relatedEndpoints (array of endpointIds)  
       u. tags (array of tagId)  
44.Other Clinical Event:  
       a. eventId  
       b. studyId  
       c. participantId  
       d. eventType  
       e. eventDescription  
       f. startDate  
       g. endDate  
       h. status  
       i. severity  
       j. seriousness  
       k. expectedness  
       l. relationshipToStudy  
       m. actionTaken  
       n. outcome  
       o. reportedBy  
       p. reportedDate  
       q. reviewedBy  
       r. reviewDate  
       s. followUpRequired  
       t. relatedDocuments (array of documentIds)  
       u. tags (array of tagId)  
45.CAPA (Corrective and Preventive Action):  
       a. capaId  
       b. studyId  
       c. siteId (if site-specific)  
       d. initiatedBy  
       e. initiationDate  
       f. capaType (e.g., CORRECTIVE, PREVENTIVE, BOTH)  
       g. status  
       h. priority  
       i. description  
       j. rootCause  
       k. immediateAction  
       l. correctiveAction  
       m. preventiveAction  
       n. dueDate  
       o. assignedTo  
       p. verifiedBy  
       q. verificationDate  
       r. effectiveness  
       s. closureDate  
       t. relatedIssueId  
       u. tags (array of tagId)  
46.Date:  
       a. dateId  
       b. studyId  
       c. dateType (e.g., MILESTONE, DEADLINE, REMINDER)  
       d. dateValue  
       e. timeValue (if applicable)  
       f. timeZone  
       g. relatedEntityType (e.g., STUDY, SITE, PARTICIPANT, VISIT)  
       h. relatedEntityId  
       i. description  
       j. status (e.g., PLANNED, COMPLETED, MISSED)  
       k. importance (e.g., LOW, MEDIUM, HIGH, CRITICAL)  
       l. createdBy  
       m. creationDate  
       n. lastModifiedBy  
       o. lastModifiedDate  
       p. notificationRules (array of notification rule objects)  
       q. recurrence (recurrence pattern if applicable)  
       r. duration (if applicable)  
       s. flexibility (allowed deviation from the planned date)  
       t. actualDate (if different from planned)  
       u. tags (array of tagId)  
47.Sample:  
       a. sampleId  
       b. studyId  
       c. participantId  
       d. visitId  
       e. siteId  
       f. sampleType  
       g. collectionDate  
       h. collectionTime  
       i. collectedBy  
       j. volume  
       k. unit  
       l. storageConditions  
       m. processingMethod  
       n. processingDate  
       o. processingTime  
       p. processedBy  
       q. storageLocation  
       r. status (e.g., COLLECTED, PROCESSED, ANALYZED, DISPOSED)  
       s. shipmentId (if shipped)  
       t. analysisResults (array of result objects)  
       u. tags (array of tagId)  
48.Equipment:  
       a. equipmentId  
       b. studyId  
        c. siteId  
        d. equipmentType  
        e. manufacturer  
        f. model  
        g. serialNumber  
        h. purchaseDate  
        i. installationDate  
        j. lastCalibrationDate  
        k. nextCalibrationDueDate  
        l. calibrationFrequency  
        m. maintenanceSchedule  
        n. lastMaintenanceDate  
        o. status (e.g., OPERATIONAL, UNDER\_MAINTENANCE, OUT\_OF\_SERVICE)  
        p. location  
        q. responsiblePerson  
        r. userManualDocumentId  
        s. certifications (array of certification objects)  
        t. maintenanceLogs (array of maintenance log objects)  
        u. tags (array of tagId)  
49.User Role:  
        a. roleId  
        b. roleName  
        c. description  
        d. permissions (array of permission objects)  
        e. studyId (if study-specific)  
        f. siteId (if site-specific)  
        g. createdBy  
        h. creationDate  
        i. lastModifiedBy  
        j. lastModifiedDate  
        k. status (e.g., ACTIVE, INACTIVE)  
        l. associatedSystems (array of systemIds)  
        m. requiredTraining (array of training course objects)  
        n. requiredCredentials (array of credential type objects)  
        o. escalationRole (roleId of the role to escalate to)  
        p. subordinateRoles (array of roleIds)  
        q. accessLevels (array of access level objects)  
        r. dataAccessRestrictions (array of data access restriction objects)  
        s. auditFrequency  
        t. lastAuditDate  
        u. tags (array of tagId)  
50.Inclusion Criteria:  
        a. criteriaId  
        b. studyId  
       c. criteriaNumber  
       d. description  
       e. version  
       f. status (e.g., ACTIVE, DEPRECATED)  
       g. category  
       h. applicablePhase (e.g., SCREENING, BASELINE, TREATMENT)  
       i. assessmentMethod  
       j. assessmentTiming  
       k. allowedValues  
       l. unitOfMeasure (if applicable)  
       m. relatedProcedures (array of procedureIds)  
       n. relatedCRFs (array of CRF Ids)  
       o. waiverAllowed (boolean)  
       p. waiverCriteria  
       q. createdBy  
       r. creationDate  
       s. lastModifiedBy  
       t. lastModifiedDate  
       u. tags (array of tagId)  
51.Exclusion Criteria:  
       a. criteriaId  
       b. studyId  
       c. criteriaNumber  
       d. description  
       e. version  
       f. status (e.g., ACTIVE, DEPRECATED)  
       g. category  
       h. applicablePhase (e.g., SCREENING, BASELINE, TREATMENT)  
       i. assessmentMethod  
       j. assessmentTiming  
       k. excludedValues  
       l. unitOfMeasure (if applicable)  
       m. relatedProcedures (array of procedureIds)  
       n. relatedCRFs (array of CRF Ids)  
       o. waiverAllowed (boolean)  
       p. waiverCriteria  
       q. createdBy  
       r. creationDate  
       s. lastModifiedBy  
       t. lastModifiedDate  
       u. tags (array of tagId)  
52.Monitoring Visit:  
       a. visitId  
       b. studyId  
       c. siteId  
       d. monitorId  
       e. visitType (e.g., SITE\_INITIATION, INTERIM, CLOSE\_OUT)  
       f. plannedStartDate  
       g. plannedEndDate  
       h. actualStartDate  
       i. actualEndDate  
       j. status  
       k. objectives  
       l. findings (array of finding objects)  
       m. actionItems (array of action item objects)  
       n. documentsReviewed (array of documentIds)  
       o. participantsReviewed (array of participantIds)  
       p. report (documentId of the monitoring report)  
       q. followUpRequired (boolean)  
       r. followUpDate  
       s. approvedBy  
       t. approvalDate  
       u. tags (array of tagId)  
53.Serious Adverse Events (SAEs):  
       a. saeId  
       b. studyId  
       c. participantId  
       d. siteId  
       e. relatedAdverseEventId  
       f. startDate  
       g. endDate  
       h. description  
       i. seriousnessCriteria (array of criteria met)  
       j. outcome  
       k. severity  
       l. relationshipToStudyTreatment  
       m. expectedness  
       n. actionTaken  
       o. reportedBy  
       p. reportDate  
       q. investigatorAssessment  
       r. sponsorAssessment  
       s. regulatoryReportingStatus  
       t. followUpReports (array of follow-up report objects)  
       u. tags (array of tagId)  
54\.  
Calls to action (CTAs)  
This list provides a comprehensive set of actions for each object in Nucleus. Each action would  
have its own metadata and specific implementation details based on the system's requirements.

   1\. Sponsor:  
           a. Create Sponsor  
           b. Update Sponsor Details  
           c. Activate/Deactivate Sponsor  
           d. Associate/Remove Study  
           e. Manage Sponsor Contacts  
           f. Review Sponsor Performance  
           g. Generate Sponsor Report  
           h. Audit Sponsor  
   2\. Tag:  
           a. Create Tag  
           b. Update Tag  
           c. Delete Tag  
           d. Assign Tag to Object  
           e. Remove Tag from Object  
   3\. Study:  
           a. Create Study  
           b. Update Study Details  
           c. Submit for Approval  
           d. Approve/Reject Study  
           e. Activate Study  
           f. Put Study on Hold  
           g. Close Study  
           h. Archive Study  
   4\. Arm:  
           a. Create Arm  
           b. Update Arm Details  
           c. Assign Participants to Arm  
           d. Close Arm  
   5\. Site:  
           a. Create Site  
           b. Update Site Details  
           c. Activate/Deactivate Site  
           d. Initiate Site  
           e. Monitor Site  
           f. Close Site  
   6\. Visit:  
           a. Schedule Visit  
           b. Reschedule Visit  
       c. Start Visit  
       d. Complete Visit  
       e. Cancel Visit  
7\. Task:  
       a. Create Task  
       b. Assign Task  
       c. Update Task Status  
       d. Complete Task  
       e. Cancel Task  
8\. Participant (Subject):  
       a. Screen Participant  
       b. Enroll Participant  
       c. Update Participant Details  
       d. Schedule Participant Visit  
       e. Withdraw Participant  
       f. Complete Participant Study  
9\. Discrepancy (Query):  
       a. Create Query  
       b. Assign Query  
       c. Respond to Query  
       d. Close Query  
       e. Reopen Query  
10.Deviation:  
       a. Report Deviation  
       b. Review Deviation  
       c. Approve/Reject Deviation  
       d. Implement Corrective Action  
       e. Close Deviation  
11.Screen Fail:  
       a. Record Screen Fail  
       b. Review Screen Fail  
       c. Approve Screen Fail  
12.Person:  
       a. Create Person  
       b. Update Person Details  
       c. Assign Role to Person  
       d. Deactivate Person  
       e. Reactivate Person  
13.Person Role:  
       a. Create Role  
       b. Update Role Details  
       c. Assign Permissions to Role  
       d. Deactivate Role  
14.CRF (Case Report Form):  
        a. Create CRF  
        b. Update CRF  
        c. Complete CRF  
        d. Review CRF  
        e. Lock/Unlock CRF  
        f. Sign CRF  
15.Document:  
        a. Upload Document  
        b. Update Document Metadata  
        c. Review Document  
        d. Approve Document  
        e. Version Document  
        f. Archive Document  
16.Adverse Event:  
        a. Report Adverse Event  
        b. Update Adverse Event Details  
        c. Assess Adverse Event  
        d. Follow Up on Adverse Event  
        e. Close Adverse Event  
17.Informed Consent:  
        a. Create Informed Consent  
        b. Update Informed Consent  
        c. Obtain Participant Consent  
        d. Record Consent Discussion  
        e. Withdraw Consent  
18.Action Item:  
        a. Create Action Item  
        b. Assign Action Item  
        c. Update Action Item Status  
        d. Complete Action Item  
        e. Cancel Action Item  
19.Milestone:  
        a. Create Milestone  
        b. Update Milestone Details  
        c. Achieve Milestone  
        d. Delay Milestone  
20.Enrollment:  
        a. Open Enrollment  
        b. Enroll Participant  
        c. Update Enrollment Status  
        d. Close Enrollment  
21.Payment:  
        a. Create Payment  
        b. Approve Payment  
       c. Process Payment  
       d. Cancel Payment  
       e. Record Payment Receipt  
22.Protocol:  
       a. Create Protocol  
       b. Update Protocol  
       c. Submit Protocol for Review  
       d. Approve/Reject Protocol  
       e. Amend Protocol  
23.Investigational Product:  
       a. Create Investigational Product  
       b. Update Product Details  
       c. Assign Product to Study  
       d. Track Product Inventory  
       e. Record Product Dispensation  
       f. Record Product Return  
24.Plan:  
       a. Create Plan  
       b. Update Plan  
       c. Approve Plan  
       d. Implement Plan  
       e. Review Plan Progress  
25.Oversight Body:  
       a. Create Oversight Body  
       b. Update Oversight Body Details  
       c. Schedule Oversight Meeting  
       d. Record Meeting Minutes  
       e. Issue Recommendations  
26.System:  
       a. Create System  
       b. Update System Details  
       c. Configure System  
       d. Integrate System  
       e. Upgrade System  
       f. Decommission System  
27.System Configuration:  
       a. Create Configuration  
       b. Update Configuration  
       c. Apply Configuration  
       d. Rollback Configuration  
28.Service:  
       a. Create Service  
       b. Update Service Details  
       c. Activate/Deactivate Service  
       d. Monitor Service Performance  
       e. Service Configuration:  
       f. Create Service Configuration  
       g. Update Service Configuration  
       h. Apply Service Configuration  
       i. Rollback Service Configuration  
29.Study Startup Package:  
       a. Create Startup Package  
       b. Update Startup Package  
       c. Submit Startup Package  
       d. Approve Startup Package  
       e. Distribute Startup Package  
30.Budget:  
       a. Create Budget  
       b. Update Budget  
       c. Approve Budget  
       d. Track Budget Expenditure  
       e. Close Budget  
31.Contract:  
       a. Create Contract  
       b. Update Contract Terms  
       c. Negotiate Contract  
       d. Sign Contract  
       e. Amend Contract  
       f. Terminate Contract  
32.Schedule of Assessments (SOA):  
       a. Create SOA  
       b. Update SOA  
       c. Approve SOA  
       d. Implement SOA  
       e. Amend SOA  
33.Endpoint:  
       a. Define Endpoint  
       b. Update Endpoint Details  
       c. Collect Endpoint Data  
       d. Analyze Endpoint Data  
34.Lab Results:  
       a. Record Lab Results  
       b. Review Lab Results  
       c. Flag Abnormal Results  
       d. Request Repeat Test  
35.Log:  
       a. Create Log Entry  
       b. Update Log Entry  
       c. Review Log  
       d. Export Log  
36.Credential:  
       a. Create Credential  
       b. Update Credential  
       c. Verify Credential  
       d. Expire Credential  
       e. Renew Credential  
37.Amendment:  
       a. Create Amendment  
       b. Review Amendment  
       c. Approve Amendment  
       d. Implement Amendment  
38.Regulatory Submission:  
       a. Prepare Submission  
       b. Review Submission  
       c. Submit to Authority  
       d. Track Submission Status  
       e. Respond to Queries  
39.Audit:  
       a. Plan Audit  
       b. Conduct Audit  
       c. Record Audit Findings  
       d. Create Audit Report  
       e. Follow Up on Audit Findings  
40.Report:  
       a. Generate Report  
       b. Review Report  
       c. Approve Report  
       d. Distribute Report  
41.Shipment:  
       a. Create Shipment  
       b. Update Shipment Details  
       c. Track Shipment  
       d. Receive Shipment  
       e. Reconcile Shipment  
42.Questionnaire (COA/PRO):  
       a. Create Questionnaire  
       b. Update Questionnaire  
       c. Validate Questionnaire  
       d. Administer Questionnaire  
       e. Score Questionnaire  
       f. Other Clinical Event:  
       g. Record Clinical Event  
        h. Update Event Details  
        i. Review Clinical Event  
        j. Follow Up on Event  
43.CAPA:  
        a. Initiate CAPA  
        b. Investigate Root Cause  
        c. Develop CAPA Plan  
        d. Implement CAPA  
        e. Verify CAPA Effectiveness  
        f. Close CAPA  
44.Date:  
        a. Set Date  
        b. Update Date  
        c. Trigger Date-based Action  
45.Sample:  
        a. Collect Sample  
        b. Process Sample  
        c. Store Sample  
        d. Ship Sample  
        e. Analyze Sample  
        f. Dispose Sample  
46.Equipment:  
        a. Register Equipment  
        b. Calibrate Equipment  
        c. Maintain Equipment  
        d. Record Equipment Usage  
        e. Decommission Equipment  
47.Data Transfer:  
        a. Initiate Data Transfer  
        b. Validate Data  
        c. Execute Data Transfer  
        d. Verify Data Transfer  
        e. Reconcile Data  
48.User Role:  
        a. Create User Role  
        b. Update Role Permissions  
        c. Assign Role to User  
        d. Revoke Role from User  
49.Inclusion Criteria:  
        a. Define Inclusion Criteria  
        b. Update Inclusion Criteria  
        c. Apply Inclusion Criteria  
        d. Waive Inclusion Criteria  
50.Exclusion Criteria:  
       a. Define Exclusion Criteria  
       b. Update Exclusion Criteria  
       c. Apply Exclusion Criteria  
       d. Waive Exclusion Criteria  
51.Monitoring Visit:  
       a. Schedule Monitoring Visit  
       b. Conduct Monitoring Visit  
       c. Record Monitoring Findings  
       d. Follow Up on Findings  
       e. Close Monitoring Visit  
52.Serious Adverse Events (SAEs):  
       a. Report SAE  
       b. Assess SAE  
       c. Report SAE to Authorities  
       d. Follow Up on SAE  
       e. Close SAE  
