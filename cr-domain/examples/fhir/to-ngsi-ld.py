"""
FHIR R4 ResearchStudy Bundle → NGSI-LD transformer (US-500-004)

Input : a FHIR R4 Bundle JSON file (collection type) containing
        ResearchStudy, Group (eligibility), and ResearchSubject resources.
Output: a list of NGSI-LD entity dicts (printed as JSON-LD).

The transformer emits 7 entity types:
  Study, Arm (per arm), EligibilityCriterion (per criterion),
  StudySubject, Enrollment

Usage:
  python to-ngsi-ld.py sample-research-study.json
"""

import json
import sys
import uuid
from datetime import datetime, timezone

NGSI_CONTEXT = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
CR_NS        = "https://top.scientix.ai/cr/v1#"
TOP_NS       = "https://top.scientix.ai/v1#"


def _id(resource_type: str, fhir_id: str) -> str:
    """Build a stable NGSI-LD entity ID from a FHIR resource."""
    return f"urn:ngsi-ld:{resource_type}:{fhir_id}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fhir_bundle_to_ngsi_ld(bundle: dict) -> list[dict]:
    """Convert a FHIR R4 Bundle to a flat list of NGSI-LD entities."""
    entities: list[dict] = []
    by_id: dict[str, dict] = {}          # resourceType/id → resource

    for entry in bundle.get("entry", []):
        res = entry.get("resource", {})
        rt  = res.get("resourceType", "")
        rid = res.get("id", str(uuid.uuid4()))
        by_id[f"{rt}/{rid}"] = res

    for key, res in by_id.items():
        rt = res["resourceType"]

        if rt == "ResearchStudy":
            rid    = res["id"]
            entity = {
                "@context": NGSI_CONTEXT,
                "id":   _id("Study", rid),
                "type": f"{CR_NS}Study",
                f"{CR_NS}title": {
                    "type":  "Property",
                    "value": res.get("title", ""),
                },
                f"{CR_NS}status": {
                    "type":  "Property",
                    "value": res.get("status", ""),
                },
                f"{TOP_NS}validFrom": {
                    "type":  "Property",
                    "value": {
                        "@type":  "DateTime",
                        "@value": _now(),
                    },
                },
            }
            entities.append(entity)

            # Arms
            for arm in res.get("arm", []):
                arm_id  = arm["name"].replace(" ", "-").lower()
                arm_ent = {
                    "@context": NGSI_CONTEXT,
                    "id":   _id("Arm", f"{rid}-{arm_id}"),
                    "type": f"{CR_NS}Arm",
                    f"{CR_NS}label": {
                        "type":  "Property",
                        "value": arm["name"],
                    },
                    f"{CR_NS}armType": {
                        "type":  "Property",
                        "value": arm.get("type", {}).get("coding", [{}])[0].get("code", ""),
                    },
                    f"{TOP_NS}partOf": {
                        "type":   "Relationship",
                        "object": _id("Study", rid),
                    },
                }
                entities.append(arm_ent)

        elif rt == "Group":
            rid = res["id"]
            for i, char in enumerate(res.get("characteristic", [])):
                crit_id = f"{rid}-crit-{i}"
                ctype   = "exclusion" if char.get("exclude") else "inclusion"
                ctext   = char.get("code", {}).get("text", "")
                crit_ent = {
                    "@context": NGSI_CONTEXT,
                    "id":   _id("EligibilityCriterion", crit_id),
                    "type": f"{CR_NS}EligibilityCriterion",
                    f"{CR_NS}criterionType": {
                        "type":  "Property",
                        "value": ctype,
                    },
                    f"{CR_NS}criterionText": {
                        "type":  "Property",
                        "value": ctext,
                    },
                }
                entities.append(crit_ent)

        elif rt == "ResearchSubject":
            rid        = res["id"]
            study_ref  = res.get("study", {}).get("reference", "")
            study_fhir = study_ref.split("/")[-1] if study_ref else "unknown"
            arm_name   = res.get("assignedArm", "")

            subject_ent = {
                "@context": NGSI_CONTEXT,
                "id":   _id("StudySubject", rid),
                "type": f"{CR_NS}StudySubject",
                f"{CR_NS}subjectId": {
                    "type":  "Property",
                    "value": rid,
                },
                f"{TOP_NS}validFrom": {
                    "type":  "Property",
                    "value": {
                        "@type":  "DateTime",
                        "@value": _now(),
                    },
                },
            }
            entities.append(subject_ent)

            if study_fhir and arm_name:
                arm_id     = arm_name.replace(" ", "-").lower()
                enroll_ent = {
                    "@context": NGSI_CONTEXT,
                    "id":   _id("Enrollment", f"{rid}-enroll"),
                    "type": f"{CR_NS}Enrollment",
                    f"{CR_NS}enrolledInArm": {
                        "type":   "Relationship",
                        "object": _id("Arm", f"{study_fhir}-{arm_id}"),
                    },
                    f"{TOP_NS}partOf": {
                        "type":   "Relationship",
                        "object": _id("Study", study_fhir),
                    },
                    f"{TOP_NS}validFrom": {
                        "type":  "Property",
                        "value": {
                            "@type":  "DateTime",
                            "@value": _now(),
                        },
                    },
                }
                entities.append(enroll_ent)

    return entities


if __name__ == "__main__":
    path   = sys.argv[1] if len(sys.argv) > 1 else "sample-research-study.json"
    with open(path) as fh:
        bundle = json.load(fh)
    entities = fhir_bundle_to_ngsi_ld(bundle)
    print(json.dumps(entities, indent=2))
    print(f"\n# Emitted {len(entities)} NGSI-LD entities.", file=sys.stderr)
