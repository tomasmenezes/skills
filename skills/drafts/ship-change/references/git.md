# Git/GitHub operations — examples, not an unattended shell script

Check actual repo instructions, selected remotes/targets and local tool help before commands. Inspect each command's results before the next mutation; no chained destructive operations. `origin`/`main` below are **examples**, not guarantees.

## Discover and fetch

```bash
git rev-parse --show-toplevel
git status --short --branch
git remote -v
git worktree list --porcelain
git branch -vv
git fetch origin
# Verify origin/<integration> exists and is a commit.
git rev-parse --verify origin/main^{commit}
# Inspect related PRs; do not infer PR ownership from local branch name.
gh pr status
```

Run optional diagnostic from the skill's absolute installed path, not by assuming `scripts/inspect.py` is at the repository root:

```bash
python3 /path/to/ship-change/scripts/inspect.py --base origin/main --mode start --json
```

It **never fetches** or knows the remote is up to date; fetch first. It is advisory, not CI or merge-authorization evidence.

## New independent branch

Sequential, clean checkout:

```bash
git switch -c agent/95-mobile-drawer origin/main
```

Parallel agent (avoid sharing writable working directories):

```bash
git worktree add -b agent/95-mobile-drawer ../wt-95-drawer origin/main
# Agent works INSIDE ../wt-95-drawer, not the original checkout.
```

Ensure branch/worktree name unique, ref still current and no other agent already owns branch/path. `git worktree` does not prevent logical conflicts between changes to shared APIs or files.

## Commit and submit

```bash
git status --short
git diff --stat
git add -- src/specific-file.ts tests/specific-file.test.ts
git diff --cached --check
git diff --cached
git commit -m 'feat(map): add mobile results drawer'
git push -u origin agent/95-mobile-drawer
gh pr create --base main --head agent/95-mobile-drawer \
  --title 'feat(map): add mobile results drawer' --body-file /tmp/ship-change-pr.md
```

Use `git add -p` for mixed changes; review hunks; do not blindly `git add -A`. If secrets accidentally enter a commit, do not push and seek safe credential rotation/history repair, preserving evidence. A secret that reached remote requires incident response beyond removing it in a new commit. Inspect `git diff origin/main...HEAD` for *independent* PRs. For a stacked child, use the exact parent branch/PR base.

## Live PR pre-merge verification

```bash
gh pr view <NUMBER> --json number,url,state,isDraft,headRefName,baseRefName,headRefOid,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
```

CLI response fields and statuses may vary by version and GitHub setup. Required checks, review freshness, merge queue, protected branches and policy are enforced on GitHub, not inferred from an abbreviated CLI status. Requery immediately before merge; don't rely on screenshots or earlier green status.

**Only after independently verified delegated authority:** GitHub's supported merge path may be immediate squash merge once gates are met, or delayed `gh pr merge <NUMBER> --auto --squash` when available, or enqueue in the configured merge queue. A disabled auto-merge repository setting doesn't itself disallow an authorized *immediate* merge. Never escalate privileges or `git push` trunk to work around rules.

## Confirm merge and clean up

```bash
gh pr view <NUMBER> --json state,mergedAt,mergeCommit,baseRefName,headRefName
git fetch origin
# Confirm GitHub mergedAt and that the mergeCommit is included in the expected integration ref.
git merge-base --is-ancestor <MERGE_SHA> origin/main
```

For squash merges, `<MERGE_SHA>` is GitHub's final integration/squash SHA, NOT the original branch SHA. If GitHub reports merged but integration SHA verification fails, recheck repository identity and target/base, possibly branch was later rewritten, or GitHub hasn't synchronized. Don't guess. Avoid `git branch -d` / forced delete if live downstream dependents, unpushed commits, dirty worktree, or ownership unknown. Worktrees can be removed normally only after clean, owned status is established; Git may refuse deletion after squash even when remote integration was successful. Treat refusal as safety signal and obtain consent before forced local deletion if needed.

## Non-goals

This file deliberately does not include generic rebase/reset/force-push recipes. When history rewriting, cross-agent branches, interrupted rebases, shared remote divergence or stacks are involved, read `references/recovery.md` and coordinate. Do not treat a series of example commands as authorization to use them.
