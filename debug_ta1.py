#!/usr/bin/env python3
import pyshacl
import rdflib
from pathlib import Path

BASE = Path("cr-domain")
SHAPES_FILE = BASE / "docs" / "dist" / "top-cr-shapes-v1.ttl"
CR_ONTOLOGY_FILE = BASE / "docs" / "dist" / "top-cr-v1.ttl"
CORE_SHAPES_FILE = Path("core/v1/shapes.ttl")
DATA_FILE = BASE / "examples" / "ta-1-thread.ttl"

# Load Core shapes + CR shapes (merged into shapes_graph)
shapes_graph = rdflib.Graph()
shapes_graph.parse(str(CORE_SHAPES_FILE), format="turtle")
shapes_graph.parse(str(SHAPES_FILE), format="turtle")

# Load Core ontology (via imports) + CR ontology for RDFS inference (ont_graph)
ont_graph = rdflib.Graph()
ont_graph.parse(str(CORE_SHAPES_FILE), format="turtle")
ont_graph.parse(str(CR_ONTOLOGY_FILE), format="turtle")

# Load data
data_graph = rdflib.Graph()
data_graph.parse(str(DATA_FILE), format="turtle")

# Run validation
conforms, results_graph, results_text = pyshacl.validate(
    data_graph,
    shacl_graph=shapes_graph,
    ont_graph=ont_graph,
    abort_on_first=False,
    allow_warnings=True,
    advanced=True,
    inference="rdfs",
    serialize_report_graph="turtle"
)

print(f"Conforms: {conforms}")
if not conforms:
    print("\n=== Violations ===")
    print(results_text)
