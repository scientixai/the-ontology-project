#!/usr/bin/env bash
#
# federate.sh — carve the monorepo into the RFC-0002 five-repo federation.
#
# NON-DESTRUCTIVE: operates entirely on a fresh mirror clone under ./build.
# `origin` is never modified. New repos are produced locally; you push them
# yourself after inspection (the script prints the exact push commands).
#
# Prereqs: git >= 2.35, git-filter-repo on PATH (pip install git-filter-repo).
# Usage:   ./federate.sh            # produce all repos into ./build
#          KEEP_BUILD=1 ./federate.sh   # keep an existing ./build (else it is recreated)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"    # this bundle's dir

# ---- config ---------------------------------------------------------------
ORG="the-ontology-project"                                   # new neutral GitHub org
SRC_URL="${SRC_URL:-https://github.com/scientixai/the-ontology-project.git}"
SRC_BRANCH="${SRC_BRANCH:-main}"                             # branch to extract from
BUILD="${BUILD:-build}"                                      # local output dir
MIRROR="$BUILD/_mirror"                                      # canonical mirror clone

# Paths, relative to repo root, that leave the monorepo.
HCLS_PATHS=( "cr-domain/ontology/hcls-core.ttl" )
CR_DIR="cr-domain"
CR_STUB="cr-domain/ontology/top-core-stub.ttl"              # deleted, not migrated (see note)
SITE_PATHS=( index.html manifesto.html roadmap.html \
             first-principles.html first-principles-illustrated.html \
             styles.css images CNAME )
# --------------------------------------------------------------------------

need() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: '$1' not found on PATH." >&2; exit 1; }; }
need git
need git-filter-repo

echo ">> federation v1 — output dir: $BUILD"
if [[ -d "$BUILD" && "${KEEP_BUILD:-0}" != "1" ]]; then
  echo ">> clearing existing $BUILD (set KEEP_BUILD=1 to keep)"
  rm -rf "$BUILD"
fi
mkdir -p "$BUILD"

# 1) One clean mirror of the source. Everything else is a copy of this — so
#    `origin` is contacted exactly once and never written to.
if [[ ! -d "$MIRROR" ]]; then
  echo ">> mirroring $SRC_URL ($SRC_BRANCH)"
  git clone --origin upstream --single-branch --branch "$SRC_BRANCH" "$SRC_URL" "$MIRROR"
fi

# helper: fresh working copy of the mirror to run a filter-repo against
fork_mirror() {  # fork_mirror <dest>
  local dest="$1"
  rm -rf "$dest"
  cp -a "$MIRROR" "$dest"
  # filter-repo refuses a repo with a configured remote unless --force; drop it.
  git -C "$dest" remote remove upstream 2>/dev/null || true
}

# ---------------------------------------------------------------------------
# hcls — path-level extraction of a single file (subtree cannot carve a file)
# ---------------------------------------------------------------------------
echo ">> [hcls] extracting ${HCLS_PATHS[*]}"
fork_mirror "$BUILD/hcls"
( cd "$BUILD/hcls"
  args=(); for p in "${HCLS_PATHS[@]}"; do args+=( --path "$p" ); done
  git filter-repo "${args[@]}"
  # lift hcls-core.ttl to the repo root as ontology/hcls-core.ttl
  git filter-repo --path-rename "cr-domain/ontology/:ontology/"
)

# ---------------------------------------------------------------------------
# clinical-research — the whole cr-domain, MINUS hcls-core and the core stub
# ---------------------------------------------------------------------------
echo ">> [clinical-research] extracting $CR_DIR (minus hcls-core, minus top-core stub)"
fork_mirror "$BUILD/clinical-research"
( cd "$BUILD/clinical-research"
  git filter-repo \
    --path "$CR_DIR/" \
    --invert-paths --path "${HCLS_PATHS[0]}" --path "$CR_STUB"
  # hoist cr-domain/* to the repo root
  git filter-repo --path-rename "cr-domain/:"
)

# ---------------------------------------------------------------------------
# site — the web surface
# ---------------------------------------------------------------------------
echo ">> [site] extracting ${SITE_PATHS[*]}"
fork_mirror "$BUILD/site"
( cd "$BUILD/site"
  args=(); for p in "${SITE_PATHS[@]}"; do args+=( --path "$p" ); done
  git filter-repo "${args[@]}"
  # Apply the overlay: retarget the site to the-ontology-project.org and add a
  # web-appropriate .gitignore. The live monorepo root CNAME (top.scientix.ai) is
  # NOT touched — only this extracted copy is retargeted (flip DNS before serving).
  cp "$SCRIPT_DIR/site-overlay/CNAME" "$SCRIPT_DIR/site-overlay/.gitignore" ./
  git add -A && git -c user.name="federation" -c user.email="federation@localhost" \
    commit -q -m "site: retarget to the-ontology-project.org (RFC 0002 §0)"
)

# ---------------------------------------------------------------------------
# core — the monorepo with the carve-outs removed
# ---------------------------------------------------------------------------
echo ">> [core] removing carve-outs from the monorepo history"
fork_mirror "$BUILD/core"
( cd "$BUILD/core"
  args=( --invert-paths --path "$CR_DIR/" )
  for p in "${SITE_PATHS[@]}"; do args+=( --path "$p" ); done
  git filter-repo "${args[@]}"
)

# ---------------------------------------------------------------------------
# standards — greenfield (no history to preserve); seed skeleton
# ---------------------------------------------------------------------------
echo ">> [standards] seeding greenfield repo"
mkdir -p "$BUILD/standards"
( cd "$BUILD/standards"
  git init -q -b main
  mkdir -p axes crosswalks manifests
  cat > README.md <<'EOF'
# standards — shared HCLS alignments (license-quarantined)

Owned crosswalks and axis-alignment spines shared across HCLS workflows. Pins `hcls` + `core`.
Holds **owned mappings + pinned source manifests only** — never license-encumbered third-party
blobs (fetched at build time). See RFC 0002 §Proposal.2 and Open-Question 3.

- `axes/`        — provenance-axis alignments (FHIR `w5` ↔ TOP categories; AFO/BFO ↔ TOP edges)
- `crosswalks/`  — derived `cx:Mapping` rows (SSSOM-exportable)
- `manifests/`   — pinned upstream source coordinates (FHIR R4, AFO REC, NCIt subsets)
EOF
  printf 'fhir.ttl\nafo.ttl\n*.owl\nvendor/\n' > .gitignore
  git add -A && git -c user.name="federation" -c user.email="federation@localhost" \
    commit -q -m "standards: seed skeleton (RFC 0002)"
)

# ---------------------------------------------------------------------------
# summary + push instructions (NOT executed)
# ---------------------------------------------------------------------------
cat <<EOF

================================================================================
Produced locally under $BUILD/ (origin untouched):

  $BUILD/core                $BUILD/hcls              $BUILD/clinical-research
  $BUILD/standards           $BUILD/site

Inspect first, e.g.:
  git -C $BUILD/hcls log --oneline | head
  git -C $BUILD/clinical-research ls-files | head
  python3 -c "from rdflib import Graph; Graph().parse('$BUILD/hcls/ontology/hcls-core.ttl')"

Then push each (review these — the script does NOT run them):

  for r in core hcls clinical-research standards site; do
    git -C $BUILD/\$r remote add origin git@github.com:$ORG/\$r.git
    git -C $BUILD/\$r push -u origin main
  done

Post-push: commit domain-registry.seed.ttl into core as registry/domains.ttl,
then apply branch protection per governance/branch-protection.md.
================================================================================
EOF
