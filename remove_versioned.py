#!/usr/bin/env python3
"""Remove rdfs:subClassOf top:Versioned from all DEMOTE classes."""

import re
from pathlib import Path

# List of 38 DEMOTE classes from VERSIONED_LEDGER.md
DEMOTE_CLASSES = [
    "cr:Administration",
    "cr:AdverseEvent",
    "cr:ActivityOccurrence",
    "cr:VisitOccurrence",
    "cr:Shipment",
    "cr:ReturnEvent",
    "cr:TemperatureExcursion",
    "cr:ClinicalObservation",
    "cr:Query",
    "cr:CustodyEvent",
    "cr:AssayResult",
    "cr:LabOrder",
    "cr:AssayDefinition",
    "cr:TransferFile",
    "cr:PreScreening",
    "cr:ScreeningRecord",
    "cr:ItemGroup",
    "cr:MitigationPlan",
    "cr:SiteMetrics",
    "cr:MetricObservation",
    "cr:RiskSignal",
    "cr:Endpoint",
    "cr:ParticipantSchedule",
    "cr:PlannedEncounter",
    "cr:ScheduleTimeline",
    "cr:TimingWindow",
    "cr:TransferSpecification",
    "cr:TransferAmendment",
    "cr:RiskManagementPlan",
    "cr:RiskReview",
    "cr:DeviationAntecedent",
    "cr:Phase3Design",
    "cr:StudySite",
    "cr:StudySubject",
    "hcls:Specimen",
    "cr:SiteInitiationVisit",
    "cr:CloseOutVisit",
    "cr:Reconciliation",
]

def find_ontology_files():
    """Find all ontology files in cr-domain and hcls-domain."""
    cr_files = list(Path("cr-domain/ontology").glob("*.ttl"))
    hcls_files = list(Path("hcls-domain/ontology").glob("*.ttl"))
    return cr_files + hcls_files

def remove_versioned_from_class(content, class_name):
    """Remove top:Versioned from rdfs:subClassOf for a given class."""
    # Convert cr:ClassName or hcls:ClassName to just ClassName for matching
    simple_name = class_name.split(":")[-1]
    
    # Pattern to match class definition with top:Versioned in subClassOf
    # Handles various formatting styles
    
    # Try to find the class definition
    # Pattern 1: class with rdfs:subClassOf on same line or next lines
    class_pattern = rf'({class_name})\s+a\s+owl:Class\s*;'
    
    if not re.search(class_pattern, content):
        return content, False
    
    # Find the class block
    lines = content.split('\n')
    modified = False
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a class definition for our target
        if re.search(rf'{class_name}\s+a\s+owl:Class', line):
            # Found the class, now process its properties
            result_lines.append(line)
            i += 1
            
            # Process properties until we hit a blank line or another class
            while i < len(lines):
                line = lines[i]
                
                # If we hit another class or blank line followed by a new definition, we're done
                if re.match(r'^[a-z]+:\w+\s+a\s+owl:', line):
                    break
                
                # Check if this line contains top:Versioned
                if 'top:Versioned' in line:
                    # Remove top:Versioned from rdfs:subClassOf
                    # Handle different formats:
                    # 1. "rdfs:subClassOf top:Versioned ;"
                    # 2. "rdfs:subClassOf top:Versioned, other:Class ;"
                    # 3. "rdfs:subClassOf other:Class, top:Versioned ;"
                    # 4. "top:Versioned," in a multi-line subClassOf
                    
                    original_line = line
                    
                    # Case: standalone "rdfs:subClassOf top:Versioned ;"
                    line = re.sub(r'\s*rdfs:subClassOf\s+top:Versioned\s*;\s*\n?', '', line)
                    
                    # Case: "top:Versioned," or ", top:Versioned"
                    line = re.sub(r',?\s*top:Versioned\s*,?', '', line)
                    
                    # Clean up any resulting ", ," or trailing/leading commas in subClassOf
                    line = re.sub(r',\s*,', ',', line)
                    line = re.sub(r'rdfs:subClassOf\s*,', 'rdfs:subClassOf', line)
                    line = re.sub(r',\s*;', ' ;', line)
                    
                    if line != original_line:
                        modified = True
                    
                    # Only add the line if it's not now empty/whitespace-only
                    if line.strip():
                        result_lines.append(line)
                    i += 1
                    continue
                
                result_lines.append(line)
                i += 1
            continue
        
        result_lines.append(line)
        i += 1
    
    return '\n'.join(result_lines), modified

def main():
    files = find_ontology_files()
    total_removed = 0
    files_modified = []
    
    for file_path in files:
        content = file_path.read_text()
        original_content = content
        
        for class_name in DEMOTE_CLASSES:
            content, modified = remove_versioned_from_class(content, class_name)
            if modified:
                total_removed += 1
                print(f"  Removed top:Versioned from {class_name} in {file_path.name}")
        
        if content != original_content:
            file_path.write_text(content)
            files_modified.append(file_path.name)
    
    print(f"\nTotal classes modified: {total_removed}")
    print(f"Files modified: {len(files_modified)}")
    print(f"Files: {', '.join(sorted(set(files_modified)))}")

if __name__ == "__main__":
    main()
