#!/usr/bin/env python3
"""Remove top:Versioned from DEMOTE classes - handles multi-line rdfs:subClassOf."""

from pathlib import Path
import re

DEMOTE_CLASSES = [
    "cr:Administration", "cr:AdverseEvent", "cr:ActivityOccurrence", "cr:VisitOccurrence",
    "cr:Shipment", "cr:ReturnEvent", "cr:TemperatureExcursion", "cr:ClinicalObservation",
    "cr:Query", "cr:CustodyEvent", "cr:AssayResult", "cr:LabOrder", "cr:AssayDefinition",
    "cr:TransferFile", "cr:PreScreening", "cr:ScreeningRecord", "cr:ItemGroup",
    "cr:MitigationPlan", "cr:SiteMetrics", "cr:MetricObservation", "cr:RiskSignal",
    "cr:Endpoint", "cr:ParticipantSchedule", "cr:PlannedEncounter", "cr:ScheduleTimeline",
    "cr:TimingWindow", "cr:TransferSpecification", "cr:TransferAmendment",
    "cr:RiskManagementPlan", "cr:RiskReview", "cr:DeviationAntecedent", "cr:Phase3Design",
    "cr:StudySite", "cr:StudySubject", "hcls:Specimen", "cr:SiteInitiationVisit",
    "cr:CloseOutVisit", "cr:Reconciliation",
]

def demote_in_file(filepath):
    """Remove top:Versioned from DEMOTE classes in file."""
    content = filepath.read_text()
    original = content
    
    for cls in DEMOTE_CLASSES:
        # Pattern 1: ", \n    top:Versioned" - most common
        content = re.sub(
            rf'({re.escape(cls)} a owl:Class[^.]*?rdfs:subClassOf[^.]*?),\s*\n\s*top:Versioned',
            r'\1',
            content,
            flags=re.DOTALL
        )
        
        # Pattern 2: "top:Versioned, \n    " - Versioned first
        content = re.sub(
            rf'({re.escape(cls)} a owl:Class[^.]*?rdfs:subClassOf\s+)top:Versioned,\s*\n\s*',
            r'\1',
            content,
            flags=re.DOTALL
        )
        
        # Pattern 3: Single line "rdfs:subClassOf top:Versioned ."
        content = re.sub(
            rf'({re.escape(cls)} a owl:Class[^.]*?)rdfs:subClassOf top:Versioned\s*\.\s*\n',
            r'\1',
            content,
            flags=re.DOTALL
        )
    
    if content != original:
        filepath.write_text(content)
        return True
    return False

def main():
    modified = []
    
    for f in Path("cr-domain/ontology").glob("*.ttl"):
        if demote_in_file(f):
            modified.append(f.name)
    
    if (Path("hcls-domain/ontology").exists()):
        for f in Path("hcls-domain/ontology").glob("*.ttl"):
            if demote_in_file(f):
                modified.append(f"hcls/{f.name}")
    
    print(f"Modified {len(modified)} files: {', '.join(sorted(modified))}")

if __name__ == "__main__":
    main()
