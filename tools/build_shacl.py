#!/usr/bin/env python3
"""
TOP build_shacl.py
Reads the OOUX-derived JSON intermediate and emits SHACL shapes (Turtle) for
validating NGSI-LD entity instances against the reference graph's structural
constraints.

Stdlib only. No pip installs.

Usage:
  python tools/build_shacl.py source/top-strawman.json shapes/clinical-trials-shapes.ttl

Sibling to build_context.py. The two scripts read the same source intermediate
and emit complementary artifacts:

  build_context.py   → JSON-LD @context (the type vocabulary)
  build_shacl.py     → SHACL Turtle    (the validation shapes)

Cardinality mapping:
  0..1  →  sh:minCount 0 ; sh:maxCount 1
  1..1  →  sh:minCount 1 ; sh:maxCount 1
  0..N  →  sh:minCount 0
  1..N  →  sh:minCount 1

Attributes use sh:datatype (for literals).
Relationships use sh:class (for object references).
Enum constraints emit sh:in with the allowed values.
"""

import json
import sys
from pathlib import Path


PRELUDE_PREFIXES = """@prefix sh:    <http://www.w3.org/ns/shacl#> .
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix top:   <https://top.scientix.ai/onto/clinical/v1#> .
@prefix topc:  <https://top.scientix.ai/onto/commons/v1#> .
@prefix fhir:  <http://hl7.org/fhir/> .
@prefix usdm:  <https://www.cdisc.org/standards/usdm/v3#> .
@prefix cdash: <https://www.cdisc.org/standards/cdashig/v2-1#> .
@prefix ngsi:  <https://uri.etsi.org/ngsi-ld/> .
@prefix prov:  <http://www.w3.org/ns/prov#> .
"""


def parse_cardinality(card):
    """Translate '0..1', '1..1', '0..N', '1..N' to (minCount, maxCount or None)."""
    if not card:
        return (None, None)
    parts = card.split("..")
    if len(parts) != 2:
        return (None, None)
    lo, hi = parts[0].strip(), parts[1].strip()
    min_count = int(lo) if lo.isdigit() else None
    max_count = int(hi) if hi.isdigit() else None  # 'N' or '*' → None (unbounded)
    return (min_count, max_count)


def turtle_string_literal(s):
    """Escape a string for safe Turtle emission."""
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def emit_attribute_shape(attr, prefix, indent="    "):
    """Emit a SHACL property shape (Turtle bracketed-blank-node) for one attribute."""
    name = attr["name"]
    datatype = attr.get("type", "xsd:string")
    optional = attr.get("optional", False)

    # Map ngsi-ld:URI to xsd:anyURI for SHACL (NGSI-LD URIs are URI-typed at the validation layer)
    if datatype == "ngsi-ld:URI":
        datatype = "xsd:anyURI"
    if not datatype.startswith(("xsd:", "ngsi-ld:")):
        datatype = "xsd:string"

    # Some attributes are typed xsd:object; SHACL doesn't have a direct equivalent.
    # Treat as nested-structure shape; for now we skip datatype assertion for objects.
    use_datatype = datatype != "xsd:object"

    lines = [
        f"{indent}sh:property [",
        f"{indent}    sh:path {prefix}:{name} ;",
    ]
    if use_datatype:
        lines.append(f"{indent}    sh:datatype {datatype} ;")
    lines.append(f"{indent}    sh:minCount {0 if optional else 1} ;")
    lines.append(f"{indent}    sh:maxCount 1 ;")

    if attr.get("enum"):
        enum_values = " ".join(turtle_string_literal(v) for v in attr["enum"])
        lines.append(f"{indent}    sh:in ( {enum_values} ) ;")

    if attr.get("doc"):
        lines.append(f"{indent}    sh:description {turtle_string_literal(attr['doc'])} ;")

    lines.append(f"{indent}    sh:name {turtle_string_literal(name)} ;")
    lines.append(f"{indent}] ;")
    return "\n".join(lines)


def emit_relationship_shape(rel, prefix, target_prefix_map, indent="    "):
    """Emit a SHACL property shape (Turtle bracketed-blank-node) for one relationship.

    When the relationship is flagged with _targetMissing (meaning the target class is
    not yet defined in the OOUX catalog), the minCount is forcibly relaxed to 0. You
    cannot validly point at a class that does not exist in the schema; emitting a
    minCount > 0 against a flagged-missing target makes every realistic example fail
    validation through no fault of the data. The constraint is restored automatically
    once the target class is filled in and the _targetMissing flag is removed.
    """
    name = rel["name"]
    target = rel.get("target", "")
    cardinality = rel.get("cardinality", "0..N")
    min_count, max_count = parse_cardinality(cardinality)

    target_missing = rel.get("_targetMissing")
    if target_missing and min_count is not None and min_count > 0:
        original_min = min_count
        min_count = 0
    else:
        original_min = None

    # Resolve target's prefix (clinical vs commons)
    target_prefix = target_prefix_map.get(target, prefix)
    target_qname = f"{target_prefix}:{target}" if target else None

    lines = [
        f"{indent}sh:property [",
        f"{indent}    sh:path {prefix}:{name} ;",
    ]
    # Suppress sh:class when target is flagged-missing: cannot validly assert a class
    # constraint against a class that does not yet exist in the catalog. Same logic as
    # the minCount relaxation above. Constraint restores automatically once the target
    # class is filled in and _targetMissing is removed.
    if target_qname and not target_missing:
        lines.append(f"{indent}    sh:class {target_qname} ;")
    if min_count is not None:
        lines.append(f"{indent}    sh:minCount {min_count} ;")
    if max_count is not None:
        lines.append(f"{indent}    sh:maxCount {max_count} ;")
    lines.append(f"{indent}    sh:nodeKind sh:IRI ;")

    if rel.get("doc"):
        lines.append(f"{indent}    sh:description {turtle_string_literal(rel['doc'])} ;")
    if target_missing:
        comment = "TARGET-MISSING: " + str(target_missing)
        if original_min is not None:
            comment += f" minCount relaxed from {original_min} to 0 until target class is defined."
        lines.append(f"{indent}    rdfs:comment {turtle_string_literal(comment)} ;")

    lines.append(f"{indent}    sh:name {turtle_string_literal(name)} ;")
    lines.append(f"{indent}] ;")
    return "\n".join(lines)


def emit_node_shape(obj, prefix, target_prefix_map):
    """Emit a SHACL NodeShape for one top-level / sub-object / horizontal class.

    When the entity declares a provType (prov:Agent | prov:Activity | prov:Entity),
    also emits a parallel rdfs:subClassOf assertion on the target class so the
    substrate IS a W3C PROV graph by construction (per FIRST-PRINCIPLES.md
    'temporal and provenance, native' commitment). The subClassOf is emitted as
    a separate statement on the targetClass IRI rather than as a SHACL property
    so it carries through to OWL/RDFS reasoners.
    """
    name = obj["id"]
    shape_id = f"{prefix}:{name}Shape"
    target_class = f"{prefix}:{name}"

    parts = []

    # PROV native typing — emit rdfs:subClassOf on the targetClass IRI
    prov_type = obj.get("provType")
    if prov_type:
        parts.append(f"{target_class} rdfs:subClassOf {prov_type} .")
        parts.append("")

    lines = [f"{shape_id} a sh:NodeShape ;"]
    lines.append(f"    sh:targetClass {target_class} ;")
    lines.append(f"    sh:name {turtle_string_literal(name)} ;")
    if obj.get("description"):
        lines.append(f"    sh:description {turtle_string_literal(obj['description'])} ;")

    # Attributes
    for attr in obj.get("attributes", []):
        lines.append(emit_attribute_shape(attr, prefix))

    # Relationships
    for rel in obj.get("relationships", []):
        lines.append(emit_relationship_shape(rel, prefix, target_prefix_map))

    # Replace trailing ' ;' with ' .' on the last property line
    if lines[-1].endswith(" ;"):
        lines[-1] = lines[-1][:-2] + " ."
    else:
        lines[-1] = lines[-1].rstrip() + " ."

    parts.append("\n".join(lines))

    # PROV relationship semantics — emit rdfs:subPropertyOf for relationships that
    # carry PROV semantics (wasAssociatedWith / wasAttributedTo / wasGeneratedBy /
    # wasDerivedFrom / actedOnBehalfOf / wasInformedBy / wasInvalidatedBy)
    prov_rel_lines = []
    for rel in obj.get("relationships", []):
        prov_sem = rel.get("provSemantics")
        if prov_sem:
            rel_iri = f"{prefix}:{rel['name']}"
            prov_rel_lines.append(f"{rel_iri} rdfs:subPropertyOf prov:{prov_sem} .")
    if prov_rel_lines:
        parts.append("")
        parts.extend(prov_rel_lines)

    return "\n".join(parts)


def check_no_polysemous_verbs(source):
    """Fail loudly when a focus class has two relationships (or two attributes) with
    the same name. JSON-LD @context maps each term to one definition; SHACL property
    paths must be unambiguous. Two predicates with the same name and different targets
    on the same class silently overwrite at emission time and corrupt the artifacts.
    Catch it before we emit, not after.

    Each polysemous verb must be split (e.g. publishes -> publishesDocument,
    publishesPublication) so each predicate carries one target type. This is the path
    USDM and FHIR took; it preserves clean one-pass projection from TOP into either
    standard without query-time gymnastics.
    """
    issues = []

    def check_class(cls, scope_label):
        seen_attrs = {}
        for attr in cls.get("attributes", []):
            n = attr.get("name")
            if n in seen_attrs:
                issues.append(f"{scope_label} {cls.get('id')}: duplicate attribute '{n}'")
            seen_attrs[n] = True

        seen_rels = {}
        for rel in cls.get("relationships", []):
            n = rel.get("name")
            target = rel.get("target")
            if n in seen_rels:
                prior_target = seen_rels[n]
                issues.append(
                    f"{scope_label} {cls.get('id')}: polysemous verb '{n}' fires against "
                    f"both '{prior_target}' and '{target}'. Split into "
                    f"'{n}{prior_target}' and '{n}{target}' so each predicate carries one target type."
                )
            seen_rels[n] = target

    for tlo in source.get("top_levels", []):
        check_class(tlo, "top-level")
        for sub in tlo.get("sub_objects", []):
            check_class(sub, "sub-object")
    for h in source.get("horizontals", []):
        check_class(h, "horizontal")

    if issues:
        msg = "Source intermediate has polysemous verbs (will corrupt emission):\n  - " + "\n  - ".join(issues)
        raise ValueError(msg)


def build_target_prefix_map(source):
    """Build a class-name → prefix map so relationship targets resolve correctly."""
    cls_prefix = source.get("prefix", "top")
    hor_prefix = source.get("horizontal_prefix", cls_prefix)

    mapping = {}
    for tlo in source.get("top_levels", []):
        mapping[tlo["id"]] = cls_prefix
        for sub in tlo.get("sub_objects", []):
            mapping[sub["id"]] = cls_prefix
    for h in source.get("horizontals", []):
        mapping[h["id"]] = hor_prefix
    return mapping


def emit_domain_invariants(source):
    """Emit hand-maintained domain invariants for the clinical-trials reference graph.

    These are SHACL-SPARQL constraints that express cross-property and cross-entity
    rules that the property-shape emitter cannot materialize from the source intermediate's
    per-class shape. v0.2 of the strawman will add a structured 'invariants' field on each
    class and emit them mechanically; for now they are hardcoded here.

    Four invariants are emitted:

    1. Soft warning: isSponsorOfRecord=true should imply hasRegulatoryResponsibility=true.
       Permitted under FDA 21 CFR 312.52 (transfer of obligations) but unusual; surfaces to
       a human reviewer rather than blocking validation.

    2. Hard violation: every Study must have at least one Sponsor with isSponsorOfRecord=true.
       Without an SoR, no entity carries regulatory accountability for the trial.

    3. Hard violation: at most one Sponsor with isSponsorOfRecord=true per (Study × jurisdiction).
       Multi-jurisdictional studies have one SoR per regulator; within a single jurisdiction (or
       no explicit scope), exactly one. Sponsors without explicit regulatoryAuthorityScope group
       together as the implicit single-jurisdiction case.

    4. Hard violation: every Study must have at least one Sponsor with hasOperationalResponsibility=true.
       If nobody is running it day-to-day, the trial cannot be conducted.
    """
    cls_prefix = source.get("prefix", "top")
    namespaces = source.get("namespaces", {})
    cls_iri = namespaces.get(cls_prefix, "https://top.scientix.ai/onto/clinical/v1#")

    def sub(text):
        """Substitute placeholders in templates."""
        return text.replace("__P__", cls_prefix).replace("__IRI__", cls_iri)

    invariants = []
    invariants.append("# === Domain invariants (hand-maintained for strawman phase) ===")
    invariants.append("# Cross-property and cross-entity rules that property shapes cannot capture.")
    invariants.append("# Encoded as SHACL-SPARQL constraints (pyshacl supports SPARQLConstraint natively).")
    invariants.append("# v0.2 will introduce a structured 'invariants' field on each class for mechanical emission.")
    invariants.append("")

    # 1. Soft warning: SoR implies regulatory responsibility
    invariants.append(sub("""__P__:SponsorSoRImpliesRegRespShape a sh:NodeShape ;
    sh:targetClass __P__:Sponsor ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Sponsor flagged isSponsorOfRecord=true but hasRegulatoryResponsibility=false. Permitted under FDA 21 CFR 312.52 (transfer of obligations) but unusual; verify intent." ;
        sh:severity sh:Warning ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this __P__:isSponsorOfRecord true .
                $this __P__:hasRegulatoryResponsibility false .
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 2. Hard: every Study must have at least one SoR
    invariants.append(sub("""__P__:StudyMustHaveSoRShape a sh:NodeShape ;
    sh:targetClass __P__:Study ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Study has no Sponsor flagged isSponsorOfRecord=true. At least one sponsor of record is required to carry regulatory accountability." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Study .
                FILTER NOT EXISTS {
                    ?sponsor __P__:runs $this .
                    ?sponsor __P__:isSponsorOfRecord true .
                }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 3. Hard: at most one SoR per (Study × jurisdiction)
    # Sponsors without explicit regulatoryAuthorityScope group together via OPTIONAL,
    # so two unscoped SoRs on the same Study correctly fire a violation.
    invariants.append(sub("""__P__:OneSoRPerStudyPerJurisdictionShape a sh:NodeShape ;
    sh:targetClass __P__:Study ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Study has more than one Sponsor flagged isSponsorOfRecord=true under the same RegulatoryAuthority (or with no explicit scope). Exactly one SoR per (Study x jurisdiction) is required; Sponsors lacking regulatoryAuthorityScope are treated as the implicit single-jurisdiction bucket." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this ?ra WHERE {
                {
                    SELECT $this ?ra (COUNT(?sponsor) AS ?cnt) WHERE {
                        ?sponsor __P__:runs $this .
                        ?sponsor __P__:isSponsorOfRecord true .
                        OPTIONAL { ?sponsor __P__:regulatoryAuthorityScope ?ra }
                    }
                    GROUP BY $this ?ra
                }
                FILTER (?cnt > 1)
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 4. Hard: every Study must have at least one operational Sponsor
    invariants.append(sub("""__P__:StudyMustHaveOperationalSponsorShape a sh:NodeShape ;
    sh:targetClass __P__:Study ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Study has no Sponsor with hasOperationalResponsibility=true. Day-to-day operational ownership must be assigned to at least one Sponsor entity." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Study .
                FILTER NOT EXISTS {
                    ?sponsor __P__:runs $this .
                    ?sponsor __P__:hasOperationalResponsibility true .
                }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # === Site / StudySite / System / Credential invariants (v0.2.0) ===
    invariants.append("# === Site / StudySite / System / Credential invariants (v0.2.0) ===")
    invariants.append("")

    hor_prefix = source.get("horizontal_prefix", cls_prefix)
    hor_namespaces = source.get("namespaces", {})
    hor_iri = hor_namespaces.get(hor_prefix, "https://top.scientix.ai/onto/commons/v1#")

    def sub2(text):
        """Substitute placeholders, including the horizontals namespace."""
        return (text
                .replace("__P__", cls_prefix)
                .replace("__IRI__", cls_iri)
                .replace("__C__", hor_prefix)
                .replace("__CIRI__", hor_iri))

    # 5. Hard: a DECENTRALIZED_HUB Site must have belongsToOrganization populated.
    #    A decentralized hub without a backing institution is structurally broken — there's
    #    no legal entity to file regulatory documents under, no entity to hold the IRB
    #    record, no entity to engage in CTAs.
    invariants.append(sub2("""__P__:SiteDecentralizedHubNeedsOrgShape a sh:NodeShape ;
    sh:targetClass __P__:Site ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Site has siteType=DECENTRALIZED_HUB but no belongsToOrganization. A decentralized hub still requires a legal/operational Organization to anchor regulatory and contractual responsibility." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Site .
                $this __P__:siteType "DECENTRALIZED_HUB" .
                FILTER NOT EXISTS { $this __P__:belongsToOrganization ?org }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 6. Hard: when Site.partOfSiteNetwork is populated, the target Organization's type
    #    must be SITE_NETWORK or SMO. Pointing at a SPONSOR or VENDOR organization as the
    #    "site network" is a modeling error caught early.
    invariants.append(sub2("""__P__:SiteNetworkOrgTypeShape a sh:NodeShape ;
    sh:targetClass __P__:Site ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Site.partOfSiteNetwork points at an Organization whose organizationType is not SITE_NETWORK or SMO. The relationship is intended for site-network or SMO Organizations only; pointing at other types is a modeling error." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            PREFIX __C__: <__CIRI__>
            SELECT $this ?org ?orgType WHERE {
                $this __P__:partOfSiteNetwork ?org .
                ?org __C__:organizationType ?orgType .
                FILTER (?orgType != "SITE_NETWORK" && ?orgType != "SMO")
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 7. Hard: a StudySite with studySiteStatus=ACTIVE must have a hasPrincipalInvestigator.
    #    R3 Section 2.1 GCP-required. A Site cannot be operationally active on a Study
    #    without a qualified Principal Investigator named on the StudySite record.
    invariants.append(sub2("""__C__:StudySiteActiveNeedsPIShape a sh:NodeShape ;
    sh:targetClass __C__:StudySite ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "StudySite has studySiteStatus=ACTIVE but no hasPrincipalInvestigator. ICH E6(R3) Section 2.1 requires a qualified Principal Investigator for any active Site participation." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __C__: <__CIRI__>
            SELECT $this WHERE {
                $this a __C__:StudySite .
                $this __C__:studySiteStatus "ACTIVE" .
                FILTER NOT EXISTS { $this __C__:hasPrincipalInvestigator ?pi }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 8. Hard: a StudySite with studySiteStatus=ACTIVE must have at least one
    #    delegatesAuthorityTo entry. R3 Section 2.3.3 GCP-requires the Delegation of
    #    Authority Log; an active Site participation with zero delegations is not
    #    GCP-compliant.
    invariants.append(sub2("""__C__:StudySiteActiveNeedsDelegationShape a sh:NodeShape ;
    sh:targetClass __C__:StudySite ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "StudySite has studySiteStatus=ACTIVE but no delegatesAuthorityTo entries. ICH E6(R3) Section 2.3.3 GCP-requires a Delegation of Authority Log for any active Site participation." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __C__: <__CIRI__>
            SELECT $this WHERE {
                $this a __C__:StudySite .
                $this __C__:studySiteStatus "ACTIVE" .
                FILTER NOT EXISTS { $this __C__:delegatesAuthorityTo ?p }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 9. Hard: for sponsor-critical Systems (EDC, CTMS, IRT, SAFETY_DB), the
    #    oversightHeldBy Organization must not be a SITE-type Organization (under R3
    #    Section 3.9 sponsor oversight obligation). IIT exception: if the SITE-type
    #    Organization also plays a Sponsor role on a Study using this System, the
    #    constraint does not fire (Site=Sponsor in IIT case).
    invariants.append(sub2("""__C__:SystemSponsorCriticalOversightShape a sh:NodeShape ;
    sh:targetClass __C__:System ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "System has systemType in {EDC, CTMS, IRT, SAFETY_DB} (sponsor-critical) but oversightHeldBy points at an Organization with organizationType=SITE. ICH E6(R3) Section 3.9 places oversight on the Sponsor for sponsor-critical systems. IIT exception applies when the same Organization also plays a Sponsor role on a Study using this System (checked via playsSponsorRole)." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            PREFIX __C__: <__CIRI__>
            SELECT $this ?org WHERE {
                $this a __C__:System .
                $this __C__:systemType ?type .
                FILTER (?type IN ("EDC", "CTMS", "IRT", "SAFETY_DB"))
                $this __C__:oversightHeldBy ?org .
                ?org __C__:organizationType "SITE" .
                FILTER NOT EXISTS {
                    ?org __C__:playsSponsorRole ?sponsor .
                    ?studySite __C__:usesSystem $this .
                    ?studySite __C__:forStudy ?study .
                    ?sponsor __P__:runs ?study .
                }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 10. Hard: a Credential must have exactly one of forPerson, forSite, forEquipment
    #     populated. The polymorphic-target pattern requires single-target discipline;
    #     a Credential pointing at both a Person and a Site is a modeling error.
    invariants.append(sub2("""__C__:CredentialExactlyOneTargetShape a sh:NodeShape ;
    sh:targetClass __C__:Credential ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Credential must have exactly one of forPerson, forSite, forEquipment populated. Polymorphic-target discipline requires single-target binding; a Credential cannot apply to multiple subject types." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __C__: <__CIRI__>
            SELECT $this WHERE {
                $this a __C__:Credential .
                {
                    SELECT $this (COUNT(?t) AS ?cnt) WHERE {
                        $this a __C__:Credential .
                        OPTIONAL { $this __C__:forPerson ?p . BIND(?p AS ?t) }
                        OPTIONAL { $this __C__:forSite ?s . BIND(?s AS ?t) }
                        OPTIONAL { $this __C__:forEquipment ?e . BIND(?e AS ?t) }
                    }
                    GROUP BY $this
                }
                FILTER (?cnt != 1)
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # === Study invariants (v0.3.0) ===
    invariants.append("# === Study invariants (v0.3.0) ===")
    invariants.append("")

    # 11. Hard: a Study with studyStatus in {RECRUITING, ENROLLING_BY_INVITATION,
    #     ACTIVE_NOT_RECRUITING, COMPLETED} must have at least one Endpoint defined.
    #     A study without endpoints has nothing to measure; permissible only in PLANNED
    #     state where the protocol is still being designed.
    invariants.append(sub("""__P__:StudyActiveNeedsEndpointShape a sh:NodeShape ;
    sh:targetClass __P__:Study ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Study has studyStatus in {RECRUITING, ENROLLING_BY_INVITATION, ACTIVE_NOT_RECRUITING, COMPLETED} but no hasEndpoint. A study at or past activation must have at least one defined endpoint to measure." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Study .
                $this __P__:studyStatus ?status .
                FILTER (?status IN ("RECRUITING", "ENROLLING_BY_INVITATION", "ACTIVE_NOT_RECRUITING", "COMPLETED"))
                FILTER NOT EXISTS { $this __P__:hasEndpoint ?ep }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 12. Hard: a Study with studyStatus in {RECRUITING, ENROLLING_BY_INVITATION,
    #     ACTIVE_NOT_RECRUITING, COMPLETED} must have at least one InclusionCriterion.
    #     A recruiting study without inclusion criteria cannot define eligibility.
    invariants.append(sub("""__P__:StudyActiveNeedsInclusionCriterionShape a sh:NodeShape ;
    sh:targetClass __P__:Study ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Study has studyStatus in {RECRUITING, ENROLLING_BY_INVITATION, ACTIVE_NOT_RECRUITING, COMPLETED} but no hasInclusionCriterion. A study at or past recruitment must have at least one inclusion criterion to define eligibility." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Study .
                $this __P__:studyStatus ?status .
                FILTER (?status IN ("RECRUITING", "ENROLLING_BY_INVITATION", "ACTIVE_NOT_RECRUITING", "COMPLETED"))
                FILTER NOT EXISTS { $this __P__:hasInclusionCriterion ?ic }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 13. Hard: a Study with studyStatus in {RECRUITING, ENROLLING_BY_INVITATION,
    #     ACTIVE_NOT_RECRUITING, COMPLETED} must have at least one ScheduleOfAssessments.
    #     The SOA is the visit-by-procedure matrix that drives operational conduct;
    #     a recruiting study without an SOA cannot guide site activities.
    invariants.append(sub("""__P__:StudyActiveNeedsScheduleShape a sh:NodeShape ;
    sh:targetClass __P__:Study ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Study has studyStatus in {RECRUITING, ENROLLING_BY_INVITATION, ACTIVE_NOT_RECRUITING, COMPLETED} but no hasSchedule (Schedule of Assessments). A study at or past recruitment must have a defined SOA to guide site operations." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Study .
                $this __P__:studyStatus ?status .
                FILTER (?status IN ("RECRUITING", "ENROLLING_BY_INVITATION", "ACTIVE_NOT_RECRUITING", "COMPLETED"))
                FILTER NOT EXISTS { $this __P__:hasSchedule ?soa }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 14. Hard: an INTERVENTIONAL Study must have studyPhase populated. Observational,
    #     expanded-access, and registry studies are exempt from this requirement
    #     (they don't have phases in the regulatory sense).
    invariants.append(sub("""__P__:InterventionalStudyNeedsPhaseShape a sh:NodeShape ;
    sh:targetClass __P__:Study ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Study has studyType=INTERVENTIONAL but no studyPhase populated. Interventional studies must declare their phase per ICH E8 / ClinicalTrials.gov. Observational, expanded-access, and registry studies are exempt." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Study .
                $this __P__:studyType "INTERVENTIONAL" .
                FILTER NOT EXISTS { $this __P__:studyPhase ?phase }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 15. Soft warning: a Study with studyStatus=COMPLETED should have actualCompletionDate
    #     populated. A COMPLETED status without an actual completion date suggests
    #     a data-entry omission.
    invariants.append(sub("""__P__:StudyCompletedNeedsCompletionDateShape a sh:NodeShape ;
    sh:targetClass __P__:Study ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Study has studyStatus=COMPLETED but no actualCompletionDate. Verify the completion date is recorded; this is typically last-patient-last-visit (LPLV)." ;
        sh:severity sh:Warning ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Study .
                $this __P__:studyStatus "COMPLETED" .
                FILTER NOT EXISTS { $this __P__:actualCompletionDate ?d }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 16. Hard: a Study with exactly one Arm should not declare interventionModel
    #     in {PARALLEL, CROSSOVER, FACTORIAL, SEQUENTIAL}. Those models require
    #     multiple arms by definition.
    invariants.append(sub("""__P__:MultiArmModelNeedsMultipleArmsShape a sh:NodeShape ;
    sh:targetClass __P__:Study ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Study has interventionModel in {PARALLEL, CROSSOVER, FACTORIAL, SEQUENTIAL} but only one hasArm. Multi-arm intervention models require multiple Arm sub-objects." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Study .
                $this __P__:interventionModel ?model .
                FILTER (?model IN ("PARALLEL", "CROSSOVER", "FACTORIAL", "SEQUENTIAL"))
                {
                    SELECT $this (COUNT(?arm) AS ?armCount) WHERE {
                        $this __P__:hasArm ?arm .
                    }
                    GROUP BY $this
                }
                FILTER (?armCount = 1)
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # === Participant invariants (v0.4.0) ===
    invariants.append("# === Participant invariants (v0.4.0) ===")
    invariants.append("")

    # 17. Hard: a Participant in any post-consent on-trial state must have at least
    #     one InformedConsent sub-object with consentStatus=OBTAINED. ICH E6(R3)
    #     Section 2.4 GCP-required: cannot be on study without consent.
    invariants.append(sub("""__P__:ParticipantOnTrialNeedsConsentShape a sh:NodeShape ;
    sh:targetClass __P__:Participant ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Participant has participantStatus in {ENROLLED, RANDOMIZED, ON_TREATMENT, IN_FOLLOW_UP, COMPLETED, WITHDRAWN, DISCONTINUED, LOST_TO_FOLLOW_UP} but no InformedConsent sub-object with consentStatus=OBTAINED. ICH E6(R3) Section 2.4 GCP-required: cannot be on study without documented consent." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Participant .
                $this __P__:participantStatus ?status .
                FILTER (?status IN ("ENROLLED", "RANDOMIZED", "ON_TREATMENT", "IN_FOLLOW_UP", "COMPLETED", "WITHDRAWN", "DISCONTINUED", "LOST_TO_FOLLOW_UP"))
                FILTER NOT EXISTS {
                    $this __P__:hasInformedConsent ?consent .
                    ?consent __P__:consentStatus "OBTAINED" .
                }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 18. Hard: a Participant with participantStatus=SCREEN_FAILED must have at least
    #     one ScreeningRecord with screeningOutcome=SCREEN_FAILED. The status implies
    #     the event; the event must be on file.
    invariants.append(sub("""__P__:ParticipantScreenFailedNeedsRecordShape a sh:NodeShape ;
    sh:targetClass __P__:Participant ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Participant has participantStatus=SCREEN_FAILED but no ScreeningRecord with screeningOutcome=SCREEN_FAILED. The status implies a recorded screening event with documented failure." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Participant .
                $this __P__:participantStatus "SCREEN_FAILED" .
                FILTER NOT EXISTS {
                    $this __P__:hasScreeningRecord ?sr .
                    ?sr __P__:screeningOutcome "SCREEN_FAILED" .
                }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 19. Hard: a Participant with participantStatus=RANDOMIZED must have assignedToArm
    #     populated AND randomizationDate populated. Randomization is a discrete event
    #     that requires both the arm assignment and the date.
    invariants.append(sub("""__P__:ParticipantRandomizedNeedsArmAndDateShape a sh:NodeShape ;
    sh:targetClass __P__:Participant ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Participant has participantStatus=RANDOMIZED but is missing assignedToArm or randomizationDate (or both). Randomization is a discrete event requiring both an arm assignment and a date." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Participant .
                $this __P__:participantStatus "RANDOMIZED" .
                FILTER (NOT EXISTS { $this __P__:assignedToArm ?arm } || NOT EXISTS { $this __P__:randomizationDate ?d })
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 20. Hard: a Participant with participantStatus=WITHDRAWN must have at least one
    #     WithdrawalRecord with withdrawalCategory=CONSENT_WITHDRAWN. WITHDRAWN is
    #     reserved for subject-initiated withdrawal of consent specifically;
    #     investigator-initiated discontinuation uses participantStatus=DISCONTINUED.
    invariants.append(sub("""__P__:ParticipantWithdrawnNeedsConsentWithdrawalShape a sh:NodeShape ;
    sh:targetClass __P__:Participant ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Participant has participantStatus=WITHDRAWN but no WithdrawalRecord with withdrawalCategory=CONSENT_WITHDRAWN. The WITHDRAWN status is reserved for subject-initiated withdrawal of consent; investigator-initiated discontinuation should use participantStatus=DISCONTINUED instead." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Participant .
                $this __P__:participantStatus "WITHDRAWN" .
                FILTER NOT EXISTS {
                    $this __P__:hasWithdrawalRecord ?wr .
                    ?wr __P__:withdrawalCategory "CONSENT_WITHDRAWN" .
                }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 21. Soft warning: a Participant with participantStatus=COMPLETED should have
    #     completionDate populated. A COMPLETED status without a completion date
    #     suggests data-entry omission.
    invariants.append(sub("""__P__:ParticipantCompletedNeedsCompletionDateShape a sh:NodeShape ;
    sh:targetClass __P__:Participant ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Participant has participantStatus=COMPLETED but no completionDate populated. Verify the completion date is recorded; this is the Participant-level last-visit date." ;
        sh:severity sh:Warning ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Participant .
                $this __P__:participantStatus "COMPLETED" .
                FILTER NOT EXISTS { $this __P__:completionDate ?d }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 22. Hard: cross-entity consistency — a Participant's assignedToArm must belong
    #     to the same Study as the Participant's forStudy. The arm is part of THIS
    #     study's design, not another study's design.
    invariants.append(sub("""__P__:ParticipantArmStudyConsistencyShape a sh:NodeShape ;
    sh:targetClass __P__:Participant ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Participant.assignedToArm references an Arm that does not belong to Participant.forStudy. The Arm must come from this Study's design, not from another Study." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Participant .
                $this __P__:assignedToArm ?arm .
                $this __P__:forStudy ?participantStudy .
                FILTER NOT EXISTS {
                    ?armStudy a __P__:Study .
                    ?armStudy __P__:hasArm ?arm .
                    FILTER (?armStudy = ?participantStudy)
                }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 23. Hard: cross-entity consistency — a Participant's forStudySite must reference
    #     a StudySite whose forStudy matches the Participant's forStudy. Same
    #     consistency principle as the arm rule above, applied to the site anchor.
    invariants.append(sub2("""__P__:ParticipantStudySiteStudyConsistencyShape a sh:NodeShape ;
    sh:targetClass __P__:Participant ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Participant.forStudySite references a StudySite whose forStudy does not match Participant.forStudy. The StudySite anchor and the Study anchor must agree." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Participant .
                $this __P__:forStudySite ?ss .
                $this __P__:forStudy ?participantStudy .
                ?ss __C__:forStudy ?ssStudy .
                FILTER (?ssStudy != ?participantStudy)
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # === Recruit invariants (v0.4.0) ===
    invariants.append("# === Recruit invariants (v0.4.0) ===")
    invariants.append("")

    # 24. Hard: a Recruit with recruitStatus=CONVERTED_TO_PARTICIPANT must have
    #     convertedToParticipant populated. The status is the terminal funnel state
    #     that signals conversion; the relationship is the operational trace.
    invariants.append(sub("""__P__:RecruitConvertedNeedsParticipantShape a sh:NodeShape ;
    sh:targetClass __P__:Recruit ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Recruit has recruitStatus=CONVERTED_TO_PARTICIPANT but convertedToParticipant relationship is not populated. The terminal-funnel-success status requires the operational link to the created Participant." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Recruit .
                $this __P__:recruitStatus "CONVERTED_TO_PARTICIPANT" .
                FILTER NOT EXISTS { $this __P__:convertedToParticipant ?p }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 25. Soft warning: a Recruit with contactAttempts > 5 and still in {RESPONDED,
    #     CONTACTED} states (i.e., not progressing past initial outreach) should
    #     probably be moved to DROPPED. Surfaces stale recruits to the recruiter.
    invariants.append(sub("""__P__:RecruitStalledManyAttemptsShape a sh:NodeShape ;
    sh:targetClass __P__:Recruit ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Recruit has contactAttempts > 5 but is still in early-funnel state (RESPONDED or CONTACTED). Consider moving to DROPPED to keep the funnel clean and surface true conversion-rate metrics." ;
        sh:severity sh:Warning ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Recruit .
                $this __P__:recruitStatus ?status .
                FILTER (?status IN ("RESPONDED", "CONTACTED"))
                $this __P__:contactAttempts ?n .
                FILTER (?n > 5)
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # === Visit invariants (v0.5.0) ===
    invariants.append("# === Visit invariants (v0.5.0) ===")
    invariants.append("")

    # 26. Hard: a Visit with visitStatus in {COMPLETED, PARTIALLY_COMPLETED, OUT_OF_WINDOW}
    #     must have actualStartDate populated. Cannot have completed a visit without
    #     recording when it happened.
    invariants.append(sub("""__P__:VisitCompletedNeedsActualStartShape a sh:NodeShape ;
    sh:targetClass __P__:Visit ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Visit has visitStatus in {COMPLETED, PARTIALLY_COMPLETED, OUT_OF_WINDOW} but no actualStartDate populated. A visit cannot be completed without recording when it actually happened." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Visit .
                $this __P__:visitStatus ?status .
                FILTER (?status IN ("COMPLETED", "PARTIALLY_COMPLETED", "OUT_OF_WINDOW"))
                FILTER NOT EXISTS { $this __P__:actualStartDate ?d }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 27. Hard: a Visit with visitStatus=COMPLETED must have actualEndDate populated.
    invariants.append(sub("""__P__:VisitCompletedNeedsActualEndShape a sh:NodeShape ;
    sh:targetClass __P__:Visit ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Visit has visitStatus=COMPLETED but no actualEndDate populated. A completed visit requires both start and end timestamps." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Visit .
                $this __P__:visitStatus "COMPLETED" .
                FILTER NOT EXISTS { $this __P__:actualEndDate ?d }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 28. Hard: a Visit with visitStatus=UNSCHEDULED must have unscheduledReason populated.
    #     UNSCHEDULED visits require operator justification per protocol-deviation discipline.
    invariants.append(sub("""__P__:VisitUnscheduledNeedsReasonShape a sh:NodeShape ;
    sh:targetClass __P__:Visit ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Visit has visitStatus=UNSCHEDULED but no unscheduledReason populated. Unscheduled visits require operator justification per protocol-deviation discipline." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Visit .
                $this __P__:visitStatus "UNSCHEDULED" .
                FILTER NOT EXISTS { $this __P__:unscheduledReason ?r }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 29. Hard: a Visit with visitStatus=OUT_OF_WINDOW must have protocolDeviationCode populated.
    invariants.append(sub("""__P__:VisitOutOfWindowNeedsDeviationCodeShape a sh:NodeShape ;
    sh:targetClass __P__:Visit ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Visit has visitStatus=OUT_OF_WINDOW but no protocolDeviationCode populated. Out-of-window visits are protocol deviations and require a deviation code." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Visit .
                $this __P__:visitStatus "OUT_OF_WINDOW" .
                FILTER NOT EXISTS { $this __P__:protocolDeviationCode ?c }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 30. Hard: cross-entity consistency — a Visit's forParticipant.forStudySite must
    #     match the Visit's forStudySite. Cross-entity consistency.
    invariants.append(sub2("""__P__:VisitParticipantStudySiteConsistencyShape a sh:NodeShape ;
    sh:targetClass __P__:Visit ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Visit's forParticipant.forStudySite does not match Visit.forStudySite. The participant's anchored StudySite and the visit's hosting StudySite must agree." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            PREFIX __C__: <__CIRI__>
            SELECT $this WHERE {
                $this a __P__:Visit .
                $this __P__:forParticipant ?participant .
                $this __P__:forStudySite ?visitStudySite .
                ?participant __P__:forStudySite ?participantStudySite .
                FILTER (?participantStudySite != ?visitStudySite)
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 31. Hard: an Activity with activityStatus=NOT_PERFORMED must have notPerformedReason
    #     populated.
    invariants.append(sub("""__P__:ActivityNotPerformedNeedsReasonShape a sh:NodeShape ;
    sh:targetClass __P__:Activity ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Activity has activityStatus=NOT_PERFORMED but no notPerformedReason populated. Non-performance requires documented justification." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Activity .
                $this __P__:activityStatus "NOT_PERFORMED" .
                FILTER NOT EXISTS { $this __P__:notPerformedReason ?r }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 32. Hard: a Task with taskStatus=NOT_PERFORMED must have notPerformedReason populated.
    invariants.append(sub("""__P__:TaskNotPerformedNeedsReasonShape a sh:NodeShape ;
    sh:targetClass __P__:Task ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Task has taskStatus=NOT_PERFORMED but no notPerformedReason populated. Non-performance requires documented justification." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Task .
                $this __P__:taskStatus "NOT_PERFORMED" .
                FILTER NOT EXISTS { $this __P__:notPerformedReason ?r }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 33. Hard: a Task with taskStatus=COMPLETED must have a non-empty taskValue.
    invariants.append(sub("""__P__:TaskCompletedNeedsValueShape a sh:NodeShape ;
    sh:targetClass __P__:Task ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Task has taskStatus=COMPLETED but taskValue is missing. Completed Tasks must carry the captured value." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Task .
                $this __P__:taskStatus "COMPLETED" .
                FILTER NOT EXISTS { $this __P__:taskValue ?v }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 34. Soft warning: a VisitObservation with escalated=true should have escalatedTo
    #     populated (when Event lifts). Surfaces ungrounded escalation flags.
    invariants.append(sub("""__P__:VisitObservationEscalatedNeedsLinkShape a sh:NodeShape ;
    sh:targetClass __P__:VisitObservation ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "VisitObservation has escalated=true but no escalatedTo populated. Escalated observations should link to the resulting Event (when Event lifts in v0.7+)." ;
        sh:severity sh:Warning ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:VisitObservation .
                $this __P__:escalated true .
                FILTER NOT EXISTS { $this __P__:escalatedTo ?e }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # === OversightBody invariants (v0.5.1) ===
    invariants.append("# === OversightBody invariants (v0.5.1) ===")
    invariants.append("")

    # 35. Hard: an OversightBody with oversightBodyType in {IRB, EC} must have
    #     scope=LOCAL or scope=CENTRAL. IRBs and ECs are review boards with
    #     defined geographic / institutional scope; SPONSOR or REGULATORY scopes
    #     are operational mismatches.
    invariants.append(sub("""__P__:OversightBodyIRBScopeShape a sh:NodeShape ;
    sh:targetClass __P__:OversightBody ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "OversightBody has oversightBodyType in {IRB, EC} but scope is not LOCAL or CENTRAL. IRBs and ECs are review boards with defined geographic / institutional scope; SPONSOR or REGULATORY scopes indicate a typing mismatch." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:OversightBody .
                $this __P__:oversightBodyType ?type .
                FILTER (?type IN ("IRB", "EC"))
                $this __P__:scope ?scope .
                FILTER (?scope NOT IN ("LOCAL", "CENTRAL"))
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 36. Hard: an OversightBody with oversightBodyType in {DSMB, IDMC} must have
    #     scope=SPONSOR. These are sponsor-convened safety review boards.
    invariants.append(sub("""__P__:OversightBodyDSMBScopeShape a sh:NodeShape ;
    sh:targetClass __P__:OversightBody ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "OversightBody has oversightBodyType in {DSMB, IDMC} but scope is not SPONSOR. DSMB / IDMC are sponsor-convened safety review boards." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:OversightBody .
                $this __P__:oversightBodyType ?type .
                FILTER (?type IN ("DSMB", "IDMC"))
                $this __P__:scope ?scope .
                FILTER (?scope != "SPONSOR")
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # === InvestigationalProduct invariants (v0.6.0) ===
    invariants.append("# === InvestigationalProduct invariants (v0.6.0) ===")
    invariants.append("")

    # 37. Hard: an InvestigationalProduct with isBlinded=true must have at least
    #     one Kit. Blinded studies require kit-level packaging for masking.
    invariants.append(sub("""__P__:IPBlindedNeedsKitShape a sh:NodeShape ;
    sh:targetClass __P__:InvestigationalProduct ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "InvestigationalProduct has isBlinded=true but no hasKit. Blinded studies require Kit sub-objects for IRT-managed treatment-assignment masking." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:InvestigationalProduct .
                $this __P__:isBlinded true .
                FILTER NOT EXISTS { $this __P__:hasKit ?k }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 38. Hard: a Kit with kitStatus in {ASSIGNED, DISPENSED} must have
    #     assignedToParticipant populated.
    invariants.append(sub("""__P__:KitAssignedNeedsParticipantShape a sh:NodeShape ;
    sh:targetClass __P__:Kit ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Kit has kitStatus in {ASSIGNED, DISPENSED} but no assignedToParticipant. Assigned and dispensed kits must reference the Participant." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Kit .
                $this __P__:kitStatus ?status .
                FILTER (?status IN ("ASSIGNED", "DISPENSED"))
                FILTER NOT EXISTS { $this __P__:assignedToParticipant ?p }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 39. Soft warning: a Lot with expirationDate in the past should have
    #     lotStatus=EXPIRED. Surfaces lots that should be retired but aren't
    #     yet flagged. xsd:date is cast through xsd:dateTime for robust comparison
    #     with NOW() across rdflib versions.
    invariants.append(sub("""__P__:LotPastExpiryNeedsExpiredStatusShape a sh:NodeShape ;
    sh:targetClass __P__:Lot ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Lot has expirationDate in the past but lotStatus is not EXPIRED, RECALLED, or DESTROYED. Verify the lot has been retired from active distribution." ;
        sh:severity sh:Warning ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
            SELECT $this WHERE {
                $this a __P__:Lot .
                $this __P__:expirationDate ?exp .
                $this __P__:lotStatus ?status .
                BIND (xsd:dateTime(CONCAT(STR(?exp), "T23:59:59Z")) AS ?expDT)
                FILTER (?expDT < NOW())
                FILTER (?status NOT IN ("EXPIRED", "RECALLED", "DESTROYED"))
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 40. Hard: a Lot with lotStatus=EXPIRED must have expirationDate populated
    #     and <= today (cast through xsd:dateTime for robust comparison).
    invariants.append(sub("""__P__:LotExpiredNeedsPastExpiryShape a sh:NodeShape ;
    sh:targetClass __P__:Lot ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Lot has lotStatus=EXPIRED but expirationDate is missing or in the future. EXPIRED status requires a past expiration date." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
            SELECT $this WHERE {
                $this a __P__:Lot .
                $this __P__:lotStatus "EXPIRED" .
                FILTER (NOT EXISTS { $this __P__:expirationDate ?exp } ||
                        EXISTS { $this __P__:expirationDate ?exp .
                                 BIND (xsd:dateTime(CONCAT(STR(?exp), "T00:00:00Z")) AS ?expDT)
                                 FILTER (?expDT > NOW()) })
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # === Event invariants (v0.7.0) ===
    invariants.append("# === Event invariants (v0.7.0) ===")
    invariants.append("")

    # 41. Hard: a SERIOUS_ADVERSE_EVENT must have regulatoryReportable=true.
    #     SAEs trigger reporting by definition per ICH E2A / 21 CFR 312.32.
    invariants.append(sub("""__P__:EventSAEMustBeReportableShape a sh:NodeShape ;
    sh:targetClass __P__:Event ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Event has eventCategory=SERIOUS_ADVERSE_EVENT but regulatoryReportable is not true. SAEs trigger regulatory submission by definition per ICH E2A and 21 CFR 312.32." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Event .
                $this __P__:eventCategory "SERIOUS_ADVERSE_EVENT" .
                FILTER NOT EXISTS { $this __P__:regulatoryReportable true }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 42. Hard: ctcaeGrade is only valid when eventCategory is AE or SAE.
    #     CTCAE 5.0 grades only apply to clinical adverse events.
    invariants.append(sub("""__P__:EventCtcaeOnlyForAEShape a sh:NodeShape ;
    sh:targetClass __P__:Event ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Event has ctcaeGrade populated but eventCategory is not ADVERSE_EVENT or SERIOUS_ADVERSE_EVENT. CTCAE grades only apply to clinical adverse events per CTCAE 5.0." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Event .
                $this __P__:ctcaeGrade ?grade .
                $this __P__:eventCategory ?cat .
                FILTER (?cat NOT IN ("ADVERSE_EVENT", "SERIOUS_ADVERSE_EVENT"))
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 43. Hard: protocolDeviationCategory is only valid when eventCategory=DEVIATION.
    invariants.append(sub("""__P__:EventDeviationCategoryOnlyForDeviationShape a sh:NodeShape ;
    sh:targetClass __P__:Event ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Event has protocolDeviationCategory populated but eventCategory is not DEVIATION. Protocol deviation categorization only applies to DEVIATION events per ICH E6(R3) Section 6." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Event .
                $this __P__:protocolDeviationCategory ?dc .
                $this __P__:eventCategory ?cat .
                FILTER (?cat != "DEVIATION")
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 44. Hard: regulatoryReportSubmitted=true requires regulatoryReportSubmittedDate.
    #     Audit-trail integrity: a submission claim must carry its timestamp.
    invariants.append(sub("""__P__:EventSubmittedNeedsDateShape a sh:NodeShape ;
    sh:targetClass __P__:Event ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Event has regulatoryReportSubmitted=true but no regulatoryReportSubmittedDate. Audit-trail integrity requires the submission timestamp." ;
        sh:severity sh:Violation ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            SELECT $this WHERE {
                $this a __P__:Event .
                $this __P__:regulatoryReportSubmitted true .
                FILTER NOT EXISTS { $this __P__:regulatoryReportSubmittedDate ?d }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    # 45. Soft warning: regulatoryReportable=true with regulatoryReportDeadline
    #     in the past and regulatoryReportSubmitted still false (overdue).
    invariants.append(sub("""__P__:EventOverdueReportShape a sh:NodeShape ;
    sh:targetClass __P__:Event ;
    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Event is regulatoryReportable=true with regulatoryReportDeadline in the past and regulatoryReportSubmitted still false. Submission is overdue; verify whether the report has been filed and update the record, or escalate per E2B SUSAR timelines." ;
        sh:severity sh:Warning ;
        sh:select \"\"\"
            PREFIX __P__: <__IRI__>
            PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
            SELECT $this WHERE {
                $this a __P__:Event .
                $this __P__:regulatoryReportable true .
                $this __P__:regulatoryReportDeadline ?dl .
                FILTER (?dl < NOW())
                FILTER NOT EXISTS { $this __P__:regulatoryReportSubmitted true }
            }
        \"\"\" ;
    ] ."""))
    invariants.append("")

    return "\n".join(invariants)


def build(source):
    """Emit the SHACL Turtle document."""
    check_no_polysemous_verbs(source)
    cls_prefix = source.get("prefix", "top")
    hor_prefix = source.get("horizontal_prefix", cls_prefix)
    target_prefix_map = build_target_prefix_map(source)

    parts = [PRELUDE_PREFIXES]
    parts.append(f"# TOP SHACL shapes · source version: {source.get('version', 'unspecified')}")
    parts.append("# Generated by build_shacl.py · do not edit by hand")
    parts.append("# Validates NGSI-LD entity instances against the reference graph's structural constraints")
    parts.append("")

    parts.append("# === Top-level classes ===")
    parts.append("")
    for tlo in source.get("top_levels", []):
        parts.append(emit_node_shape(tlo, cls_prefix, target_prefix_map))
        parts.append("")
        for sub in tlo.get("sub_objects", []):
            parts.append(emit_node_shape(sub, cls_prefix, target_prefix_map))
            parts.append("")

    parts.append("# === Cross-cutting horizontals ===")
    parts.append("")
    for h in source.get("horizontals", []):
        parts.append(emit_node_shape(h, hor_prefix, target_prefix_map))
        parts.append("")

    parts.append(emit_domain_invariants(source))

    return "\n".join(parts)


def main():
    if len(sys.argv) != 3:
        print("usage: build_shacl.py <source.json> <output.ttl>", file=sys.stderr)
        sys.exit(2)

    src_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    src = json.loads(src_path.read_text())
    out = build(src)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out)
    print(f"wrote {out_path}")

    # Quick stats
    n_tlo = len(src.get("top_levels", []))
    n_sub = sum(len(t.get("sub_objects", [])) for t in src.get("top_levels", []))
    n_hor = len(src.get("horizontals", []))
    n_attrs = sum(
        len(t.get("attributes", [])) for t in src.get("top_levels", [])
    ) + sum(
        len(s.get("attributes", []))
        for t in src.get("top_levels", [])
        for s in t.get("sub_objects", [])
    ) + sum(len(h.get("attributes", [])) for h in src.get("horizontals", []))
    n_rels = sum(
        len(t.get("relationships", [])) for t in src.get("top_levels", [])
    ) + sum(len(h.get("relationships", [])) for h in src.get("horizontals", []))

    print(f"  shapes: {n_tlo + n_sub + n_hor} ({n_tlo} top-levels, {n_sub} sub-objects, {n_hor} horizontals)")
    print(f"  property shapes: {n_attrs} attributes + {n_rels} relationships = {n_attrs + n_rels}")
    print(f"  domain invariants: 45 (7 soft warnings + 38 hard violations)")


if __name__ == "__main__":
    main()
