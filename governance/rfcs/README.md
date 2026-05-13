---
layout: default
title: RFC Process
meta_primary: RFC Process
meta_secondary: Structural decisions · markdown PRs
markdown_content: true
---

# TOP RFC Process

> RFCs (Requests for Comment) are how TOP makes structural decisions that affect more than one working group, change Core, alter governance, or commit the project to a direction that will be hard to unravel. The process is deliberately lightweight: a markdown document, a PR, a review, a merge. The artifact stays in the repository as the durable record of the decision.

ADRs in [`../decision-log.md`](../decision-log.md) record decisions *after* they are made — the substance, the moment, the reasoning. RFCs propose decisions *before* they are made — the question, the alternatives, the recommendation. When an RFC ratifies, it merges into `accepted/` and an ADR is appended to the decision log citing the RFC as its source.

## When you need an RFC

File an RFC for any change that:

- **Modifies Core** (`/core/`, `/taxonomy/`) — new categories, new leaves, new Universal DNA properties, renames, architectural shifts.
- **Crosses working groups** — defining a concept that two or more WGs share; relocating a concept from a WG into Core; arbitrating a naming or shape conflict between WGs.
- **Changes governance** — RFC process itself; CODEOWNERS structure; WG lifecycle conventions; release cadence; branch-protection rules.
- **Forms or dissolves a working group** — see [`../working-groups.md`](../working-groups.md).
- **Affects URI / namespace conventions** — anything that changes how downstream consumers cite TOP.
- **Commits the project to a tooling or standards alignment** — adopting a new vocabulary (BFO, OBO Foundry, SSSOM), retiring an existing one.

You do NOT need an RFC for:

- Routine work inside your WG's directory — taxonomy edits, additional worked examples, spec doc additions, sub-object refinements that don't change the operator interface.
- Documentation polish, typo fixes, link repairs.
- Internal restructuring of a WG's directory.
- Adding a new attribute to an existing entity inside your workflow (operator-vocabulary level changes that don't ripple to Core).

When in doubt, file an RFC. The cost of one is small; the cost of an unraveled decision is large.

## How to file an RFC

1. **Copy the template.** [`0000-template.md`](0000-template.md) → `proposed/NNNN-short-title.md`. Use the next sequential number; keep the title short and kebab-case.

2. **Fill it in.** Title, status (Proposed), date, authors, motivation, proposal, alternatives, open questions, consequences. The template guides each section.

3. **Open a PR.** The PR title matches the RFC title. The PR body summarizes the proposal in 3–5 sentences and links to the file.

4. **Tag the affected owners.** Pull requests touching `/governance/rfcs/proposed/` require the convener's review at minimum. RFCs affecting Core need a Core steward; RFCs affecting a specific WG need that WG's review.

5. **Iterate in the PR.** Reviewers leave comments. The author updates the RFC document. Substantive changes can extend the open period; trivial polish does not.

6. **Land or reject.** When consensus emerges:
   - **Accepted:** the PR merges, the file moves to `accepted/NNNN-short-title.md`, and an ADR is appended to [`../decision-log.md`](../decision-log.md) citing the RFC.
   - **Rejected:** the PR closes without merging. The author may revise and refile; the rejection is documented in the closing comment.
   - **Withdrawn:** the author closes the PR voluntarily.
   - **Superseded by another RFC:** rare during proposal; common after acceptance. A new RFC must explicitly cite the one it supersedes.

## RFC numbering

- Proposed RFCs use sequential numbers starting at 0001.
- Numbers do not get reused. A withdrawn or rejected RFC keeps its number; the next proposal takes the next number.
- The template (`0000-template.md`) keeps the reserved number 0000.

## Directory structure

```
governance/rfcs/
├── README.md            (this file)
├── 0000-template.md     (the template; reserved number)
├── proposed/            (RFCs under active review)
│   └── NNNN-short-title.md
└── accepted/            (RFCs that have been ratified)
    └── NNNN-short-title.md
```

Rejected and withdrawn RFCs stay in `proposed/` with their final status field updated; they do not move to a separate directory. The PR's merge or close state, combined with the RFC's `Status:` field, tells the story.

## Quorum and acceptance

While the convener is the review pool of one, acceptance requires the convener's approval. As working groups form, the following minimums apply:

- **RFC affecting only one WG's directory:** approval from at least one WG maintainer of that WG.
- **RFC affecting Core or governance:** approval from at least one Core steward AND, if a workflow WG is affected, at least one maintainer of that WG.
- **RFC crossing multiple WGs:** approval from at least one maintainer of each affected WG plus a Core steward.

A specific RFC can declare a higher quorum if the substance demands it (e.g., a rename of a load-bearing Core class). The author declares the quorum in the RFC's metadata.

## What goes in an accepted RFC

After ratification, the RFC document must read as a durable record of *what was decided and why*. It is the canonical reference for future contributors asking "why is it this way?" The corresponding ADR in [`../decision-log.md`](../decision-log.md) is a one-page summary; the RFC carries the full reasoning.

Edits to an accepted RFC are unusual. Corrections (typos, broken links, clarifications) are fine. Substantive changes require a new RFC that supersedes the old one.
