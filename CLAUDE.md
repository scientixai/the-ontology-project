# Repository guidance for AI sessions

**This is a PUBLIC repository.** Everything committed — code, comments, docs, and
**commit messages** — is world-readable the moment it is pushed.

## IP hygiene (hard rule)

**Public** (fine to write anywhere): the reference knowledge graph, SHACL shapes,
projections, crosswalks, standards alignment, ADRs, and the technical *why* of modeling
decisions — including pure **NGSI-LD** (the open standard).

**Gated** (NEVER in committed content or commit messages): the internal **runtime
engine** — the **PNE Bridge**, the **Factual Layer** / **Adaptive Layer** architecture,
and any runtime-engine detail that ventures past the open NGSI-LD standard. Also out:
commercial / market strategy, unannounced plans, customer or prospect names, and anything
quoted or paraphrased from confidential uploads (e.g. handoffs, narrative decks). That
reasoning belongs in chat; it does not enter the repo.

**Rule of thumb: describe the _reference graph_, never the _runtime_.** This mirrors the
project's "Reference Graph, not Runtime Graph" first principle — the runtime engine is
deliberately not modeled in the public reference graph, and it is not described in it
either.

The gate is enforced: `tools/check_ip_leak.py` (denylist `tools/ip-denylist.json`) runs
as a pre-commit hook and in CI (`.github/workflows/ip-hygiene.yml`). **Do not weaken the
denylist to make a commit pass — fix the content.** Adding a term to the denylist is a
deliberate governance act.

## Commit hygiene

- Commit messages are a **changelog of the diff**, not a transcript of the deliberation.
- End messages with `Co-Authored-By: Claude <noreply@anthropic.com>`.
- Do **not** add a session-URL trailer to commits.

## Local hooks (opt-in, recommended)

    git config core.hooksPath .githooks

Enables the pre-commit + commit-msg IP-hygiene checks locally so a leak is caught before
it is ever pushed. CI is the backstop.
