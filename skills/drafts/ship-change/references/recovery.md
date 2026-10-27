# Non-destructive recovery matrix

**First action on resumption/failure:** snapshot state by inspecting `git status --porcelain`, HEAD/refs, worktree ownership, PR state, current merge/rebase activity, open descendants and pushed/unpushed commits. No blind retries. Preserve original refs and work before operations that change ancestry.

| Scenario | Correct response |
|---|---|
| Dirty worktree before agent starts | Identify owner; don't stash, overwrite, stage or reset; create a separate clean worktree if new task |
| Same session shifts task | Determine change boundary; finish/handoff old PR, branch fresh from fetched trunk for new independent task |
| Unknown branch/worktree ownership | Pause writes; inspect active agents and open PRs; resolve ownership before mutation |
| Shared branch diverged/push rejected | Re-read remote changes, coordinate; no unconditional force push or reset |
| `git rebase`/cherry-pick interrupted | Inspect active operation/conflicts and uncommitted user edits; only owner may continue/abort with awareness of impact |
| Wrong stack parent or mixed stack | Freeze, inventory history and PR base; rebuild independent changes using reviewed cherry-picks/patches, preserve original refs until verified |
| Child has merged/squashed ancestor | Re-read parent merge status, synchronize/re-target child carefully; watch duplicate commits and re-run tests |
| Parent PR rejected | Replan downstream PRs; don't pretend they can integrate without parent |
| PR closed without merge | Not delivered; link rejection/replacement and mark blocked/abandoned appropriately |
| PR merged but local branch not ancestor | Normal after squash; use remote PR mergedAt+mergeCommit & target branch evidence, ensure no unpushed work/dependent branch; do not automatically force delete |
| Remote PR merged but target code absent | Verify repo, PR base and remote freshness; possible revert or force rewrite; stop and investigate |
| Commit includes secrets | Do not push further; notify owner; rotate compromised credentials if exposed; removing in new commit does not erase history |
| Checks green for earlier head | Run required checks and refresh approvals for current head/merge group; no merge on stale validation |
| Multiple agents modify same interface | Coordinate API/ownership, serialize work or use explicit dependency; independent worktrees alone don't prevent semantic conflict |
| `gt sync` mutates graph owned by other agents | Stop, preserve refs/state, notify owners; no blind restack or force push to recover |
| Build/test tooling missing | Record exact skipped tests and limitations, keep PR for review; do not invent passing evidence |
| Trunk hotfix required | New branch from freshly fetched trunk, even if another feature branch is active |
| Host tool operation timed out | Re-check GitHub object/ref state before retrying creates, pushes, merge or delete; avoid duplicate PRs and accidental double actions |
| Default branch changes / upstream rename | Re-derive integration target from repository settings and governance; don't blindly use `origin/main` |
| Fork PR/remote mismatch | Identify upstream base repository, fork push remote and permissions separately; do not push into the wrong repository |
| Untracked generated assets or LFS pointers | Verify ownership and intention; check tracked binary sizes, .gitattributes, LFS availability; do not auto-delete or publish credentials |
| Feature flag is disabled | Verify incomplete code doesn't affect runtime/contracts, and that acceptance can be assessed; otherwise hold branch |

### Splitting an accidentally mixed branch

1. Stop accepting new unrelated work. Record branch SHA, open PR and parent graph, dirty state, all commits and dependencies.
2. Identify truly separate outcomes and any overlapping code hunks; avoid misleading cherry-picks that silently omit required logic.
3. Create new branch(es) from *freshly fetched* integration ref, deliberately port related commits/hunks after review. Preserve original branch/PR until replacement branches are verified; don't force-delete or rewrite shared history.
4. Validate each replacement in isolation, create distinct PRs and cross-link/supersede old PR with rationale; ensure previous approvals aren't incorrectly recycled.
5. Integrate safely, then clean original only with explicit ownership and no unpushed work/dependents.

### Rules never to relax automatically

No `git reset --hard`, blind `git clean`, blanket `git stash pop`, `push --force`, force deletion of dirty/unmerged branches or worktrees, override of another worker's locked checkout, admin bypass, skip hooks, suppress failing tests, deleting production data, or unreviewed history rewrites. Do not discard user data to maintain a tidy branch graph.
