# GraphRAG Recipe: Eligibility Screening

**US-800-003** — GraphRAG recipe combining SPARQL retrieval + vector similarity
to answer "Is patient eligible?" and emit a `top:Conclusion` with full AI provenance.

## Overview

This recipe implements a two-stage Retrieval-Augmented Generation (RAG) pipeline:

1. **Stage 1 — SPARQL retrieval**: Query the knowledge graph for structured
   eligibility criteria (`cr:EligibilityCriterion`) bound to the target study.
2. **Stage 2 — Vector similarity**: Retrieve relevant clinical note passages
   (patient history, lab values) using embedding similarity against each criterion.
3. **Stage 3 — LLM inference**: Prompt the LLM with retrieved context and
   emit a structured eligibility verdict as `top:Conclusion`.
4. **Stage 4 — Provenance capture**: Write `top:promptTemplate`,
   `top:sourceContext`, and `top:modelVersion` on the `top:Conclusion`.

## SPARQL Query (Stage 1)

```sparql
PREFIX cr:  <https://top.scientix.ai/cr/v1#>
PREFIX top: <https://top.scientix.ai/v1#>

SELECT ?criterion ?text ?type WHERE {
  ?study a cr:Study ;
         cr:hasEligibilityCriterion ?criterion .
  ?criterion cr:criterionText ?text ;
             cr:criterionType ?type .  # "inclusion" | "exclusion"
  FILTER(?study = <{study_iri}>)
}
ORDER BY ?type ?criterion
```

## Vector Similarity (Stage 2)

For each criterion `?text`, retrieve the top-k patient record passages:

```python
def retrieve_passages(criterion_text: str, patient_id: str, k: int = 5):
    """Return top-k clinical note passages relevant to this criterion."""
    query_vec = embed(criterion_text)
    results = vector_store.search(
        query=query_vec,
        filter={"patient_id": patient_id},
        top_k=k
    )
    return [r.text for r in results]
```

## Prompt Template (Stage 3)

```
You are a clinical trial eligibility specialist.

Study eligibility criteria:
{criteria_block}

Patient clinical record excerpts:
{passages_block}

Task: For each criterion, state whether the patient MEETS, DOES NOT MEET, or
CANNOT DETERMINE eligibility based solely on the provided excerpts.
Output a JSON object with keys:
  - "eligible": true | false | "indeterminate"
  - "rationale": string (cite specific criterion + passage)
  - "uncertain_criteria": list of criterion IDs where evidence was insufficient
```

## Python Sketch (Stage 3 + 4)

```python
import json
from datetime import datetime, timezone

TOP = "https://top.scientix.ai/v1#"
CR  = "https://top.scientix.ai/cr/v1#"

def screen_patient(study_iri: str, patient_iri: str, model: str = "gpt-4o-2024-05-13"):
    # Stage 1: SPARQL
    criteria = sparql_query(SPARQL_TEMPLATE.format(study_iri=study_iri))

    # Stage 2: Vector retrieval per criterion
    passages = {}
    for c in criteria:
        passages[c["criterion"]] = retrieve_passages(c["text"], patient_iri)

    # Build prompt
    criteria_block = "\n".join(
        f"[{c['type'].upper()}] {c['criterion']}: {c['text']}" for c in criteria
    )
    passages_block = "\n\n".join(
        f"Criterion {cid}:\n" + "\n".join(f"  - {p}" for p in ps)
        for cid, ps in passages.items()
    )
    prompt = PROMPT_TEMPLATE.format(
        criteria_block=criteria_block,
        passages_block=passages_block
    )

    # Stage 3: LLM call
    response = llm_call(model=model, prompt=prompt)
    verdict = json.loads(response.text)

    # Stage 4: Emit top:Conclusion with provenance
    conclusion_iri = f"https://top.scientix.ai/conclusions/{uuid4()}"
    graph.add((
        conclusion_iri, RDF.type, URIRef(TOP + "Conclusion")
    ))
    graph.add((
        conclusion_iri, URIRef(TOP + "promptTemplate"), Literal(PROMPT_TEMPLATE)
    ))
    graph.add((
        conclusion_iri, URIRef(TOP + "sourceContext"),
        Literal(json.dumps({"criteria": criteria, "passages": passages}))
    ))
    graph.add((
        conclusion_iri, URIRef(TOP + "modelVersion"), Literal(model)
    ))
    graph.add((
        conclusion_iri, URIRef(TOP + "recordedAt"),
        Literal(datetime.now(timezone.utc).isoformat(), datatype=XSD.dateTime)
    ))
    graph.add((
        conclusion_iri, URIRef(CR + "eligibilityVerdict"),
        Literal(verdict["eligible"])
    ))
    return conclusion_iri, verdict
```

## Output Shape

The emitted `top:Conclusion` satisfies:

| Property | Value |
|---|---|
| `rdf:type` | `top:Conclusion` |
| `top:promptTemplate` | verbatim prompt string with `{criteria_block}` / `{passages_block}` filled |
| `top:sourceContext` | JSON blob: SPARQL rows + retrieved passages |
| `top:modelVersion` | e.g. `"gpt-4o-2024-05-13"` |
| `top:recordedAt` | ISO-8601 UTC timestamp |
| `cr:eligibilityVerdict` | `"true"` / `"false"` / `"indeterminate"` |

## HITL Gate Integration

When `cr:eligibilityVerdict = "indeterminate"` or confidence is below threshold,
the conclusion must be flagged for human review before being used to gate enrollment.
A `cx:Mapping` produced by this pipeline MUST carry `cx:inferredBy` and will be
blocked by `cr:LLMInferredMappingConfirmedShape` until a curator adds `cx:confirmedBy`.

## References

- US-800-001: `cr-core-ai.ttl` — `top:promptTemplate`, `top:sourceContext`, `top:modelVersion`
- US-800-002: `shapes/crosswalk.ttl` — `cr:LLMInferredMappingConfirmedShape`
- ICH E6(R3) §5.5.3 — sponsor oversight of automated processes
