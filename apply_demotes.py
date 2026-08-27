#!/usr/bin/env python3
"""Apply DEMOTE axioms by removing top:Versioned from rdfs:subClassOf declarations."""

from pathlib import Path
import re

# 38 DEMOTE classes
DEMOTE_CLASSES = {
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
}

def process_file(filepath):
    """Remove top:Versioned from DEMOTE classes in a TTL file."""
    lines = filepath.read_text().splitlines(keepends=True)
    modified = False
    in_demote_class = None
    output = []
    
    for i, line in enumerate(lines):
        # Check if this line starts a DEMOTE class definition
        for cls in DEMOTE_CLASSES:
            if re.match(rf'^{re.escape(cls)}\s+a\s+owl:Class', line):
                in_demote_class = cls
                break
        
        # If we're in a DEMOTE class definition
        if in_demote_class:
            # Check if line ends the class definition
            if line.rstrip().endswith('.') and 'owl:Class' not in line:
                in_demote_class = None
            
            # Remove top:Versioned from rdfs:subClassOf
            original_line = line
            
            # Pattern 1: "rdfs:subClassOf top:Versioned ." - remove entire line
            if re.match(r'\s*rdfs:subClassOf\s+top:Versioned\s*\.\s*$', line):
                modified = True
                continue  # Skip this line
            
            # Pattern 2: "rdfs:subClassOf top:Versioned," - remove top:Versioned and comma
            line = re.sub(r'rdfs:subClassOf\s+top:Versioned\s*,\s*', 'rdfs:subClassOf ', line)
            
            # Pattern 3: ", top:Versioned" (with possible whitespace/newline)
            line = re.sub(r',\s*top:Versioned\s*([,;\.])', r'\1', line)
            line = re.sub(r',\s*top:Versioned\s*$', '', line)
            
            # Pattern 4: "top:Versioned," at start of continuation line
            line = re.sub(r'^\s*top:Versioned\s*,\s*', '        ', line)
            
            if line != original_line:
                modified = True
        
        output.append(line)
    
    if modified:
        filepath.write_text(''.join(output))
    
    return modified

def main():
    modified_files = []
    
    # Process CR domain
    for f in Path("cr-domain/ontology").glob("*.ttl"):
        if process_file(f):
            modified_files.append(str(f))
    
    # Process HCLS domain (for hcls:Specimen)
    hcls_ont = Path("hcls-domain/ontology")
    if hcls_ont.exists():
        for f in hcls_ont.glob("*.ttl"):
            if process_file(f):
                modified_files.append(str(f))
    
    print(f"Modified {len(modified_files)} files:")
    for f in sorted(modified_files):
        print(f"  {f}")
    
    return len(modified_files)

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() > 0 else 1)
