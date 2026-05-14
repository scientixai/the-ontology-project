# Branch Protection — intended rules

> Branch protection is configured in GitHub Settings, not in the repository itself. This document records the intended rules so they are transparent to contributors and so the configuration can be reconstructed if it ever drifts.

Per [ADR-0017](decision-log.md#adr-0017-monorepo-with-directory-scoped-ownership), TOP relies on directory-scoped CODEOWNERS plus branch protection to enforce ownership boundaries inside a single repository.

## `main`

The default and only long-lived branch. All work merges to `main` via pull request.

| Rule | Setting | Why |
| --- | --- | --- |
| Require a pull request before merging | On | All changes are reviewable. |
| Require approvals | 1 minimum | The convener is the review pool of one today; this scales as WGs form. |
| Dismiss stale approvals on new commits | On | Force re-review when the diff changes. |
| Require review from Code Owners | On | This is the mechanism that enforces `.github/CODEOWNERS`. Without it, the file is documentation, not enforcement. |
| Require status checks to pass | On (when CI lands) | No checks defined yet; placeholder for when validators are added. |
| Require branches to be up to date before merging | On | Catches drift between long-running branches and main. |
| Require linear history | On | Squash-merge or rebase-merge only; no merge commits. Keeps the history readable. |
| Require signed commits | Off | Optional but not required; signing adds friction without proportional security benefit at current scale. |
| Restrict who can push to matching branches | On (admins + repo write) | Nobody pushes directly to main. |
| Allow force pushes | Off | Never. |
| Allow deletions | Off | Never. |
| Lock branch | Off | Main is editable via PR. |
| Do not allow bypassing the above settings | On | Admins included. The convener follows the same rules as contributors. |

## Working-group branches

Working groups may use their own branch naming conventions (e.g., `clinical-research/feature-x`). No special protection on these — they are working surfaces. Promotion to `main` requires the rules above.

## Release tags

Releases are git tags on `main` commits. Tag names follow `<directory>/v<semver>` — e.g., `core/v1.0.0`, `clinical-research/v0.2.0`. Tags are immutable once pushed.

| Rule | Setting | Why |
| --- | --- | --- |
| Tag protection rule for `*/v*` | On | Tags are first-class release artifacts; they don't get rewritten. |
| Who can create matching tags | Admins | Releases are intentional. |

## How to apply these rules

GitHub → Repository Settings → Branches → Add branch protection rule, applied to `main`. Each row above maps to a checkbox or input on that page. Tag protection lives under GitHub → Repository Settings → Tags.

If a rule needs to change, it changes via [RFC](rfcs/README.md). The RFC documents the rule's old state, new state, and the operational pressure that forced the change.
