#!/usr/bin/env python3
"""Transform a USDM v4 JSON protocol into NGSI-LD entity payloads.

Reads a USDM v4 compliant JSON file (as produced by the CDISC DDF-RA API or
tools like Protocol Explorer) and emits a batch of NGSI-LD entities ready for
POST to /ngsi-ld/v1/entityOperations/upsert on a Scorpio / AWS Garnet broker.

Each emitted entity is typed against the TOP CR @context and carries Universal
DNA (identifier, observedAt, status). Relationship properties use NGSI-LD
Relationship nodes ({type: Relationship, object: urn:...}). Bitemporal entities
(ProtocolVersion) carry top:validFrom derived from protocol governance dates.

Usage:
    python3 to-ngsi-ld.py ly900018-usdm-v4.json           # stdout
    python3 to-ngsi-ld.py ly900018-usdm-v4.json -o out/   # write per-entity files
    python3 to-ngsi-ld.py ly900018-usdm-v4.json --batch   # write single batch file

The runtime repo (top-runtime) will call this (or a refactored version of it)
as the first stage of the ODM/USDM ingestion pipeline.

Output conforms to NGSI-LD v1.8 (ETSI GS CIM 009).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

# ---- Context references -------------------------------------------------------
# The TOP CR NGSI-LD context layers over the ETSI core context. In production
# this URL is served from the TOP distribution endpoint. For local dev, point to
# the generated file in docs/dist/.
CONTEXT = [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.8.jsonld",
    "https://top.scientix.ai/cr/v1.ngsi-context.jsonld",
]

# ---- URN helpers --------------------------------------------------------------
# All entity IDs are NGSI-LD URNs. We prefix with the USDM instance type so
# IDs are globally unique without a study namespace collision.

def urn(instance_type: str, local_id: str) -> str:
    safe = str(local_id).replace(" ", "_")
    return f"urn:ngsi-ld:top-cr:{instance_type}:{safe}"


def prop(value) -> dict:
    """Wrap a scalar as an NGSI-LD Property node."""
    return {"type": "Property", "value": value}


def rel(target_urn: str) -> dict:
    """Wrap a URN as an NGSI-LD Relationship node."""
    return {"type": "Relationship", "object": target_urn}


def code_prop(code_obj: dict) -> dict:
    """Represent a USDM Code as a structured Property value."""
    if not code_obj:
        return prop(None)
    return prop({
        "code": code_obj.get("code"),
        "codeSystem": code_obj.get("codeSystem"),
        "decode": code_obj.get("decode"),
    })


def dna(identifier: str, status: str = "active", observed_at: str = None) -> dict:
    """Universal DNA — the three properties every TOP entity must carry."""
    return {
        "identifier": prop(identifier),
        "status": prop(status),
        "observedAt": prop(observed_at or datetime.now(timezone.utc).isoformat()),
    }


def base(instance_type: str, local_id: str, identifier: str,
         status: str = "active", observed_at: str = None, ingested_at: str = None) -> dict:
    observed_at = observed_at or ingested_at
    """Base NGSI-LD entity skeleton with Universal DNA."""
    return {
        "id": urn(instance_type, local_id),
        "type": f"cr:{instance_type}" if instance_type not in ("Organization",) else f"hcls:{instance_type}",
        "@context": CONTEXT,
        **dna(identifier, status, observed_at),
    }


# ---- Per-entity-type mappers --------------------------------------------------

def map_organization(org: dict, ingested_at: str) -> dict:
    """USDM Organization → hcls:Organization (cr:Sponsor if type.code=C70793)."""
    org_type_code = (org.get("type") or {}).get("code")
    cr_type = "cr:Sponsor" if org_type_code == "C70793" else "hcls:Organization"

    e = {
        "id": urn("Organization", org["id"]),
        "type": cr_type,
        "@context": CONTEXT,
        **dna(org.get("identifier") or org["id"], "active", ingested_at),
    }
    if org.get("name"):
        e["name"] = prop(org["name"])
    if org.get("label"):
        e["label"] = prop(org["label"])
    if org.get("identifierScheme"):
        e["identifierScheme"] = prop(org["identifierScheme"])
    return e


def map_study(study: dict, ingested_at: str) -> dict:
    """USDM Study → cr:Study."""
    e = base("Study", study["name"], study["name"], ingested_at=ingested_at)
    e["type"] = "cr:Study"
    if study.get("label"):
        e["label"] = prop(study["label"])
    return e


def map_study_version(study_name: str, sv: dict, governance_date: str,
                      ingested_at: str) -> dict:
    """USDM StudyVersion → cr:ProtocolVersion (bitemporal: top:Versioned).

    validFrom is derived from the GovernanceDate in the StudyVersion; this is
    the valid-time start (when this version became true in the world). The
    transaction time (observedAt) is the ingestion timestamp.
    """
    e = base("ProtocolVersion", sv["id"], sv.get("versionIdentifier", sv["id"]),
             ingested_at=ingested_at)
    e["type"] = "cr:ProtocolVersion"
    e["versionIdentifier"] = prop(sv.get("versionIdentifier"))
    e["hasProtocolVersionOf"] = rel(urn("Study", study_name))
    if governance_date:
        e["validFrom"] = prop(governance_date)
    if sv.get("rationale"):
        # Strip HTML tags for the plain-text property value
        import re
        e["rationale"] = prop(re.sub(r"<[^>]+>", " ", sv["rationale"]).strip())
    return e


def map_arm(arm: dict, design_id: str, ingested_at: str) -> dict:
    """USDM StudyArm → cr:Arm."""
    e = base("Arm", arm["id"], arm["name"], ingested_at=ingested_at)
    e["type"] = "cr:Arm"
    if arm.get("label"):
        e["label"] = prop(arm["label"])
    if arm.get("description"):
        e["description"] = prop(arm["description"])
    e["armType"] = code_prop(arm.get("type"))
    e["partOfScope"] = rel(urn("Study", design_id))
    return e


def map_epoch(epoch: dict, ingested_at: str) -> dict:
    """USDM StudyEpoch → top:Scope (study epoch as a named scope boundary)."""
    e = {
        "id": urn("StudyEpoch", epoch["id"]),
        "type": "top:Scope",
        "@context": CONTEXT,
        **dna(epoch.get("name", epoch["id"]), "active", ingested_at),
    }
    if epoch.get("label"):
        e["label"] = prop(epoch["label"])
    if epoch.get("description"):
        e["description"] = prop(epoch["description"])
    if epoch.get("nextId"):
        e["nextEpoch"] = rel(urn("StudyEpoch", epoch["nextId"]))
    if epoch.get("previousId"):
        e["previousEpoch"] = rel(urn("StudyEpoch", epoch["previousId"]))
    return e


def map_encounter(enc: dict, ingested_at: str) -> dict:
    """USDM Encounter → cr:Visit."""
    e = base("Visit", enc["id"], enc["name"], ingested_at=ingested_at)
    e["type"] = "cr:Visit"
    if enc.get("label"):
        e["label"] = prop(enc["label"])
    e["visitType"] = code_prop(enc.get("type"))
    if enc.get("nextId"):
        e["nextVisit"] = rel(urn("Visit", enc["nextId"]))
    if enc.get("previousId"):
        e["previousVisit"] = rel(urn("Visit", enc["previousId"]))
    if enc.get("contactModes"):
        e["contactModes"] = prop([c.get("decode") for c in enc["contactModes"] if c])
    if enc.get("environmentalSettings"):
        e["environmentalSettings"] = prop(
            [c.get("decode") for c in enc["environmentalSettings"] if c])
    return e


def map_eligibility_criterion(ec: dict, item_text: dict, ingested_at: str) -> dict:
    """USDM EligibilityCriterion → cr:EligibilityCriterion."""
    e = base("EligibilityCriterion", ec["id"], ec.get("name", ec["id"]),
             ingested_at=ingested_at)
    e["type"] = "cr:EligibilityCriterion"
    category_code = (ec.get("category") or {}).get("code")
    e["criterionCategory"] = prop("inclusion" if category_code == "C25532" else "exclusion")
    e["criterionNumber"] = prop(ec.get("identifier"))
    if item_text:
        import re
        text = item_text.get("text", "") or ""
        e["criterionText"] = prop(re.sub(r"<[^>]+>", " ", text).strip())
    return e


def map_objective(obj: dict, ingested_at: str) -> dict:
    """USDM Objective → cr:Endpoint (objective level)."""
    e = base("Objective", obj["id"], obj.get("name", obj["id"]),
             ingested_at=ingested_at)
    e["type"] = "cr:Endpoint"
    if obj.get("label"):
        e["label"] = prop(obj["label"])
    e["objectiveLevel"] = code_prop((obj.get("level") or {}))
    return e


def map_endpoint(ep: dict, ingested_at: str) -> dict:
    """USDM Endpoint → cr:Endpoint."""
    e = base("Endpoint", ep["id"], ep.get("name", ep["id"]),
             ingested_at=ingested_at)
    e["type"] = "cr:Endpoint"
    if ep.get("label"):
        e["label"] = prop(ep["label"])
    e["endpointLevel"] = code_prop(ep.get("level"))
    return e


def map_scheduled_activity_instance(sai: dict, ingested_at: str) -> dict:
    """USDM ScheduledActivityInstance → top:Temporal (SoA node).

    In execution these become cr:Visit actuals; at design time they are
    planning nodes. We type them as top:Temporal and link to the epoch.
    """
    e = {
        "id": urn("ScheduledActivityInstance", sai["id"]),
        "type": "top:Temporal",
        "@context": CONTEXT,
        **dna(sai.get("name", sai["id"]), "planned", ingested_at),
    }
    if sai.get("epochId"):
        e["occursInEpoch"] = rel(urn("StudyEpoch", sai["epochId"]))
    if sai.get("defaultConditionId"):
        e["nextScheduledInstance"] = rel(
            urn("ScheduledActivityInstance", sai["defaultConditionId"]))
    if sai.get("activityIds"):
        e["hasActivities"] = [rel(urn("Activity", a)) for a in sai["activityIds"]]
    return e


def map_biomedical_concept(bc: dict, ingested_at: str) -> dict:
    """USDM BiomedicalConcept → top:Evidence (data collection specification).

    BiomedicalConcepts are the protocol-level data collection requirements.
    They map to top:Evidence since they are the specification artifacts that
    back up what data is to be collected; the actual collected values become
    top:Observation at execution time.
    """
    e = {
        "id": urn("BiomedicalConcept", bc["id"]),
        "type": "top:Evidence",
        "@context": CONTEXT,
        **dna(bc.get("name", bc["id"]), "active", ingested_at),
    }
    if bc.get("label"):
        e["label"] = prop(bc["label"])
    if bc.get("reference"):
        e["sdtmReference"] = prop(bc["reference"])
    if bc.get("synonyms"):
        e["synonyms"] = prop(bc["synonyms"])
    return e


def map_amendment(study_name: str, amend: dict, ingested_at: str) -> dict:
    """USDM StudyAmendment → cr:ProtocolVersion (revision of prior version).

    An amendment is a new bitemporal ProtocolVersion that supersedes the
    prior version. We record the amendment number and reason, and link to
    the study. In the full bitemporal model, prov:wasRevisionOf would point
    to the prior ProtocolVersion.
    """
    e = {
        "id": urn("StudyAmendment", amend["id"]),
        "type": "cr:ProtocolVersion",
        "@context": CONTEXT,
        **dna(amend.get("name", amend["id"]), "active", ingested_at),
    }
    e["amendmentNumber"] = prop(amend.get("number"))
    e["hasProtocolVersionOf"] = rel(urn("Study", study_name))
    if amend.get("primaryReason"):
        reason_code = (amend["primaryReason"].get("code") or {})
        e["amendmentPrimaryReason"] = code_prop(reason_code)
    if amend.get("summary"):
        import re
        e["amendmentSummary"] = prop(
            re.sub(r"<[^>]+>", " ", amend["summary"]).strip())
    return e


# ---- Index builders -----------------------------------------------------------

def _index_by_id(items: list) -> dict:
    return {item["id"]: item for item in (items or []) if isinstance(item, dict)}


def _find_all(obj, instance_type: str, results=None) -> list:
    if results is None:
        results = []
    if isinstance(obj, dict):
        if obj.get("instanceType") == instance_type:
            results.append(obj)
        for v in obj.values():
            _find_all(v, instance_type, results)
    elif isinstance(obj, list):
        for v in obj:
            _find_all(v, instance_type, results)
    return results


# ---- Main transform -----------------------------------------------------------

def transform(usdm: dict, ingested_at: str = None) -> list:
    """Return a list of NGSI-LD entity dicts ready for broker upsert."""
    ingested_at = ingested_at or datetime.now(timezone.utc).isoformat()
    entities = []

    study = usdm["study"]
    study_name = study["name"]

    # Study
    entities.append(map_study(study, ingested_at))

    # Organizations
    for org in _find_all(study, "Organization"):
        entities.append(map_organization(org, ingested_at))

    # StudyVersions + amendments
    for sv in study.get("versions", []):
        gov_date = None
        for d in (sv.get("dateValues") or []):
            if d.get("instanceType") == "GovernanceDate":
                gov_date = d.get("dateValue")
                break
        entities.append(map_study_version(study_name, sv, gov_date, ingested_at))

        for amend in (sv.get("amendments") or []):
            entities.append(map_amendment(study_name, amend, ingested_at))

        # EligibilityCriterionItems (text source)
        ec_items = {i["id"]: i for i in _find_all(sv, "EligibilityCriterionItem")}

        for design in (sv.get("studyDesigns") or []):
            # Arms
            for arm in _find_all(design, "StudyArm"):
                entities.append(map_arm(arm, study_name, ingested_at))

            # Epochs
            for epoch in _find_all(design, "StudyEpoch"):
                entities.append(map_epoch(epoch, ingested_at))

            # Encounters → Visits
            for enc in _find_all(design, "Encounter"):
                entities.append(map_encounter(enc, ingested_at))

            # Eligibility criteria
            for ec in _find_all(design, "EligibilityCriterion"):
                item = ec_items.get(ec.get("criterionItemId"))
                entities.append(map_eligibility_criterion(ec, item, ingested_at))

            # Objectives
            for obj in _find_all(design, "Objective"):
                entities.append(map_objective(obj, ingested_at))

            # Endpoints
            for ep in _find_all(design, "Endpoint"):
                entities.append(map_endpoint(ep, ingested_at))

            # ScheduledActivityInstances (SoA nodes)
            for sai in _find_all(design, "ScheduledActivityInstance"):
                entities.append(map_scheduled_activity_instance(sai, ingested_at))

            # BiomedicalConcepts (data collection specifications)
            for bc in _find_all(design, "BiomedicalConcept"):
                entities.append(map_biomedical_concept(bc, ingested_at))

    return entities


# ---- CLI ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="USDM v4 JSON file")
    parser.add_argument("-o", "--output-dir", help="Write per-type JSON files here")
    parser.add_argument("--batch", action="store_true",
                        help="Write a single batch payload file alongside the input")
    parser.add_argument("--ingested-at", help="Override ingestion timestamp (ISO-8601)")
    args = parser.parse_args()

    with open(args.input) as f:
        usdm = json.load(f)

    entities = transform(usdm, ingested_at=args.ingested_at)

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        by_type: dict = {}
        for e in entities:
            t = e["type"].split(":")[-1]
            by_type.setdefault(t, []).append(e)
        for t, es in by_type.items():
            path = os.path.join(args.output_dir, f"{t}.json")
            with open(path, "w") as f:
                json.dump(es, f, indent=2)
            print(f"  {len(es):4d} entities → {path}", file=sys.stderr)
        print(f"\nTotal: {len(entities)} entities", file=sys.stderr)
    elif args.batch:
        out_path = args.input.replace(".json", ".ngsi-ld-batch.json")
        with open(out_path, "w") as f:
            json.dump(entities, f, indent=2)
        print(f"Wrote {len(entities)} entities → {out_path}", file=sys.stderr)
    else:
        json.dump(entities, sys.stdout, indent=2)
        print(f"\n# {len(entities)} entities", file=sys.stderr)


if __name__ == "__main__":
    main()
