#!/usr/bin/env python3
"""Integration demo. Two flagship views from one native graph, plus a
regulator question answered as a query. Run: python3 cr-domain/demo/demo.py
"""
import os
from rdflib import Graph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE = os.path.join(ROOT, "examples", "oncology-fih-conformant.ttl")


def _graph():
    g = Graph()
    for f in ("ontology/top-core.ttl", "ontology/hcls-core.ttl", "ontology/cr-core.ttl"):
        g.parse(os.path.join(ROOT, f), format="turtle")
    g.parse(EXAMPLE, format="turtle")
    return g


def _rows(g, query):
    res = g.query(query)
    return [{str(v): str(r[v]) for v in res.vars if r[v] is not None} for r in res]


def run_demo():
    g = _graph()
    sdtm_ae = _rows(g, open(os.path.join(ROOT, "projections", "sdtm_ae.rq")).read())
    doa_log = _rows(g, open(os.path.join(ROOT, "projections", "doa_log.rq")).read())
    # Regulator question, answered as a query: "which subjects had an adverse event?"
    regulator_q = _rows(g, """
        PREFIX cr:   <https://top.scientix.ai/cr/v1#>
        PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?subject WHERE {
          ?ae rdf:type/rdfs:subClassOf* cr:AdverseEvent ; cr:forSubject ?s .
          ?s rdfs:label ?subject .
        }""")
    return {"sdtm_ae": sdtm_ae, "doa_log": doa_log, "regulator_q": regulator_q}


if __name__ == "__main__":
    r = run_demo()
    print("=== Sponsor-side: CDISC SDTM AE (projection) ===")
    for row in r["sdtm_ae"]:
        print(f"  USUBJID={row.get('USUBJID')} | AETERM={row.get('AETERM')}")
    print("\n=== Site-side: Delegation of Authority log (projection) ===")
    for row in r["doa_log"]:
        print(f"  {row.get('delegator')} -> {row.get('delegate')} : {row.get('capability')}")
    print("\n=== Regulator question as a query: subjects with an AE ===")
    for row in r["regulator_q"]:
        print(f"  {row.get('subject')}")
    print("\nAll three are views/queries over one native, bitemporal, provenanced graph.")
