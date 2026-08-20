---
name: gh-stack-commit
description: Work with GitHub Stacked PRs (`gh stack`) using well-scoped Conventional Commits. Use when the user asks to create or amend commits, run `/commit`, stage changes, split work into stacked PRs, generate Conventional Commit messages, create stack layers, submit stacked PRs, or update a lower layer while preserving a clean stack.
license: MIT
allowed-tools:
  - "Bash(gh stack init *)"
  - "Bash(gh stack add *)"
  - "Bash(gh stack view *)"
  - "Bash(gh stack checkout *)"
  - "Bash(gh stack rebase *)"
  - "Bash(gh stack submit *)"
  - "Bash(gh pr view *)"
  - "Bash(gh pr edit *)"
  - "Bash(git add *)"
  - "Bash(git reset *)"
  - "Bash(git diff *)"
  - "Bash(git status *)"
  - "Bash(git rebase *)"
  - "Bash(git branch *)"
  - "Bash(git commit *)"
  - "Bash(git log *)"
---

# GitHub Stacked PRs with Conventional Commits

Use this skill to turn local changes into well-scoped Conventional Commits inside GitHub Stacked PRs, combining diff analysis, staging, commit messages, layer creation, lower-layer updates, submission, and PR-description guidance.

## Scope And Authority

This skill owns change decomposition, staging, Conventional Commits, layer placement, amend-vs-new-commit decisions, validation, and PR-description conventions.

For general stack mechanics-remotes, navigation, sync/merge, modify/unstack, exit codes, and recovery-consult GitHub's `gh-stack` companion skill from `github/gh-stack` when available. `gh stack <command> --help` is authoritative for flags and arguments. If the companion skill is unavailable, do not guess beyond commands owned here.

## Safety Rules

- Before changing git state or committing, inspect `git status --short`, `git diff --staged`, and `git diff`.
- Preserve user changes. Stage only files/hunks for the current logical change; avoid `git add .`, `git add -A`, and broad stack staging shortcuts in mixed worktrees.
- Never commit secrets such as `.env`, credentials, tokens, private keys, or generated private config.
- `gh stack init` may enable Git `rerere` as documented. Do not make other git-config changes unless explicitly asked.
- Never skip hooks with `--no-verify` unless explicitly asked. If hooks fail, fix the issue, restage the intended files, and retry.
- Never force push the repository's trunk/default branch (`main`, `master`, or equivalent).
- Treat `git reset`, raw `git rebase`, remote stack mutation, force pushes, and branch deletion as high-risk; use them only when necessary and user intent is clear.
- Do not run `gh stack push`, `submit`, `sync`, `unstack`, or `merge` merely because local commit work was requested.
- Before remote-aware `gh stack` commands such as `rebase`, `push`, or `submit`, apply the companion skill's remote-selection rules; never invent a remote.
- Prefer `gh stack rebase` for normal stack maintenance. Do not improvise raw ancestry rewrites on a tracked stack; consult the companion skill first.

## Quick Reference

| I want to...                              | Command                                                            |
| ----------------------------------------- | ------------------------------------------------------------------ |
| Inspect changed files                     | `git status --short`                                               |
| Inspect staged changes                    | `git diff --staged`                                                |
| Inspect unstaged changes                  | `git diff`                                                         |
| Stage specific files                      | `git add -- <files>`                                               |
| Interactively stage hunks                 | `git add -p`                                                       |
| Commit staged changes                     | `git commit -m "<title>" -m "<body>"`                              |
| Amend current commit                      | `git commit --amend --no-edit` or replace its message              |
| Initialize first stack layer              | `gh stack init <branch-name>`                                      |
| Add a layer on top                        | `gh stack add <branch-name>`                                       |
| Inspect stack structure                   | `gh stack view --json`                                             |
| Check out the owning local layer          | `gh stack checkout <branch>`                                       |
| Rebase descendants after lower-layer edit | `gh stack rebase --upstack`                                        |
| Submit stacked PRs non-interactively      | `gh stack submit --auto`                                           |
| Edit PR title/body                        | `gh pr edit <PR_NUMBER> --title "..." --body-file /tmp/pr-body.md` |

For other commands, consult the companion `gh-stack` skill rather than extending this reference.

## Commit Analysis Workflow

### What Makes A Good Stacked PR

Evaluate candidate PRs in roughly this order:

- **Atomic/hermetic**: independent of unrelated changes, able to pass CI, and safe to land together with its required lower layers.
- **Dependency-correct**: foundational work belongs lower in the stack; dependent work belongs above it.
- **Narrow semantic scope**: limited to one module, feature, behavior, or one coherent mechanical change across related modules.
- **Small diff**: compact enough to review without hiding intent.

Bias toward more, smaller PRs whenever each remains independently valid. No change is too small if splitting it materially clarifies upstack review. Do not split so aggressively that a layer's branch state cannot build, test, or be meaningfully reviewed.

Independent sibling changes belong in separate stacks rather than being forced into one dependency chain.

### 1. Inspect State

Run:

```bash
git status --short
git diff --staged
git diff
```

If already inside a stack, also run:

```bash
gh stack view --json
```

Use staged changes when they already form a coherent unit; otherwise choose the next logical group from the working tree. On an existing stack, identify the owning layer before editing or committing-never put a lower-layer concern on top merely because that branch is checked out.

### 2. Group Changes

Prefer one logical change per commit and one logical concern per PR. Multiple commits on a branch are valid when each is coherent and all serve that same concern.

Good grouping signals:

- Same feature, bug, module, or behavior.
- Tests/docs that directly validate or explain the implementation.
- One coherent repository-wide mechanical change.

Split unrelated features, fixes, refactors, or reviewer audiences. Keep generated artifacts with the requiring change only when needed for validation, build, or deployment.

### 3. Stage Intentionally

Stage only the current logical change:

```bash
git add -- path/to/file1 path/to/file2
git add -p
```

Then verify exactly what will be committed:

```bash
git diff --staged
```

### 4. Generate The Message

Analyze the staged diff and choose:

- **Type**: the kind of change.
- **Scope**: the smallest useful area, module, package, feature, or subsystem; optional but encouraged.
- **Description**: imperative, present tense, under 72 characters when practical.
- **Body**: prefer one even for small changes; keep it brief when context is simple, and record rationale, behavior changes, tradeoffs, migrations, validation, or why the change belongs in this layer.
- **Footer**: issue references or breaking-change metadata.

Examples:

```text
feat(auth): add session refresh warning
fix(api): handle empty pagination cursors
refactor(ui): simplify toolbar state handling
test(parser): cover nested block parsing
docs: update stacked PR workflow guidance
```

## Conventional Commit Format

Use Conventional Commits:

```text
<type>(<scope>): <description>

<optional body>

<optional footer>
```

The scope is optional but encouraged when it adds useful routing or review context:

```text
docs: update release checklist
```

### Types

| Type       | Purpose                                             |
| ---------- | --------------------------------------------------- |
| `feat`     | New feature                                         |
| `fix`      | Bug fix                                             |
| `docs`     | Documentation-only change                           |
| `style`    | Formatting/style-only change with no logic impact   |
| `refactor` | Code change that is neither a feature nor a bug fix |
| `perf`     | Performance improvement                             |
| `test`     | Add or update tests                                 |
| `build`    | Build system, package manager, or dependency change |
| `ci`       | CI or automation change                             |
| `chore`    | Maintenance that does not fit another type          |
| `revert`   | Revert a previous change                            |

### Message Rules

- Use imperative mood: `add`, not `adds` or `added`.
- Keep the description specific.
- Do not end the description with a period.
- Prefer a body even for small changes; keep it brief when the title already makes the rationale obvious.
- Reference issues when relevant: `Closes #123`, `Refs #456`.

### Breaking Changes

Use `!` after the type or scope:

```text
feat(api)!: remove deprecated session endpoint
```

Or add a footer:

```text
feat(config): allow nested project configs

BREAKING CHANGE: project config resolution now stops at workspace root
```

## GitHub Stack Workflow

### Branch Naming

Use the repository's branch convention when one exists. Otherwise prefer a shared stack prefix and a terse concern:

```text
<stack-topic>/<change-description>
```

Example:

```text
auth-bugfix/reorder-args
auth-bugfix/improve-logging
auth-bugfix/update-docs
auth-bugfix/handle-401-status
```

### Create A New Stack

For multi-part work, plan dependency order before implementation and build bottom-up:

1. Inspect state and decide the bottom layer.
2. Initialize that stack layer before committing its work.
3. Stage and commit only the bottom-layer change.
4. Add the next layer only when starting a distinct dependent concern.
5. Repeat until the stack is complete.
6. Validate each layer when practical.
7. Submit only when requested.

Example:

```bash
git status --short
gh stack init auth-bugfix/reorder-args

git add -- path/to/first-change
git diff --staged
git commit \
  -m "fix(auth): reorder login arguments" \
  -m "Keep provider arguments aligned with the canonical authentication call order."

gh stack add auth-bugfix/improve-logging

git add -- path/to/logging-change
git diff --staged
git commit \
  -m "fix(auth): add login failure logging" \
  -m "Record provider and status details so failed login attempts are diagnosable."
```

Prefer ordinary `git add` + `git commit` over stack shortcuts that automatically stage broad worktree state. This keeps mixed changes from leaking into the wrong layer.

### Existing Branches

`gh stack init` can adopt existing branches, but adoption does not repair their Git ancestry. Only adopt an existing chain when its ancestry already matches the intended dependency order; list it bottom-to-top:

```bash
gh stack init branch-a branch-b branch-c
```

Use `--base <trunk>` only when the intended trunk is not the repository default. If the current non-trunk branch already owns the bottom change, identify it with `git branch --show-current` and adopt it as the first layer instead of recreating it.

When adoption or stack metadata is ambiguous, consult the companion `gh-stack` skill before mutating state.

## Updating Existing Branches

### Put Changes On The Owning Layer

Inspect the stack, move to the correct layer, make the change there, then cascade it through descendants:

```bash
gh stack view --json
gh stack checkout <owning-branch>

git add -- <files>
git diff --staged
git commit -m "<message>"
gh stack rebase --upstack
```

Do not duplicate a lower-layer fix in an upstack branch just to avoid rebasing.

### Amend Current Commit

Use this when staged changes belong in the latest commit.

If the message remains correct:

```bash
git add -- <files>
git diff --staged
git commit --amend --no-edit
```

If the amendment changes the commit's meaning, replace the Conventional Commit message:

```bash
git commit --amend \
  -m "fix(auth): handle empty login redirect" \
  -m "Keep callback construction valid when the redirect parameter is omitted."
```

If higher layers exist, rebase them after the rewrite:

```bash
gh stack rebase --upstack
```

Amending rewrites commit SHAs. Do not push the rewritten stack unless remote update was requested.

### Add A Commit To Current Branch

Use another commit when the branch should retain distinct commit history:

```bash
git add -- <files>
git diff --staged
git commit \
  -m "test(auth): cover empty login redirect" \
  -m "Exercise the no-redirect callback path to prevent regressions."
```

Then rebase higher layers when needed. Whether amending or adding a commit, if an open PR's scope changes materially, update its title/body when the remote update is requested.

## Resetting Commits To Unstaged Changes

When committed work needs to be split differently, and only after confirming the commits are local or otherwise safe to rewrite:

```bash
git status --short
git log --oneline --decorate -5
git reset HEAD^       # reset last commit; keep changes unstaged
git reset HEAD~2      # reset multiple commits
git diff HEAD         # inspect the working set
```

Then stage the first logical group and recommit it on the appropriate layer. If a lower layer was rewritten, rebase descendants afterwards.

## Submitting And Editing PRs

### Validate First

Before submission, run the repository's validation commands from project instructions such as `AGENTS.md`, package scripts, Makefiles, or repository docs.

Common validation categories:

- Formatting/linting.
- Type checks.
- Unit tests for touched areas.
- Build checks when user-facing or shared code changed.

If validation fails, fix it on the layer that owns the problem, commit/amend, and rebase descendants.

### Submit The Stack

Before submitting:

```bash
gh stack view --json
```

Verify the intended trunk, dependency order, and each branch's logical scope. When stacked PRs are requested, use the companion skill's non-interactive submission form; normally:

```bash
gh stack submit --auto
```

Apply the companion skill's remote-selection guidance before execution; leave generalized submit flags and edge cases there.

### PR Titles

Use the Conventional Commit title as the PR title unless the repository has a different convention. Under current `gh-stack` behavior, `submit --auto` uses a one-commit layer's commit subject as its PR title and a humanized branch name for multi-commit layers. Keep commit and branch names strong enough for those defaults, then inspect and edit the submitted PR title if needed.

### PR Descriptions

For non-trivial PRs, use an explicit body. Before replacing an existing PR title/body, inspect it so user-written context and required repository-template sections are preserved:

```bash
gh pr view <PR_NUMBER> --json title,body,baseRefName,headRefName
```

Prefer a temporary Markdown file for complex descriptions, then edit explicitly:

```bash
gh pr edit <PR_NUMBER> \
  --title "fix(auth): handle empty login redirect" \
  --body-file /tmp/pr-body.md
```

Respect repository PR templates and conventions; integrate the stack/layer summary into required sections instead of replacing them. Avoid shell heredocs for complex PR descriptions because Markdown tables, code fences, and shell interpolation are easy to break.

#### Bottom / Trunk-facing PR

Identify the bottom/trunk-facing PR from `gh stack view --json`; do not infer it from the branch you happen to be editing. As this skill's PR-description convention, that PR owns the overall stack summary plus its own layer:

```markdown
## Stack

This stack fixes login redirect handling and improves diagnostics around failed auth flows.

## What?

Handle empty redirect parameters before building the callback URL.

## Why?

Users can currently hit a blank redirect path after provider login. This layer keeps the callback valid and provides the foundation for the diagnostics changes above it.
```

#### Middle And Top PRs

Subsequent PRs describe only their own layer:

```markdown
## What?

Add login failure logging with provider and status details.

## Why?

Support needs structured context to diagnose failed login attempts.
```

GitHub already renders Stack relationships, so do not manually duplicate every PR link unless repository convention requires it.

Before merging, update the bottom PR's stack summary if branches were added, dropped, or materially changed.

## Troubleshooting And Recovery

This section covers only failures that directly affect the commit-layering workflow. For generalized `gh stack` recovery, consult the companion `gh-stack` skill.

| Problem                             | Action                                                                                                             |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Need to inspect ownership           | `gh stack view --json`, then inspect branch diffs/logs if needed                                                   |
| Lower layer changed                 | `gh stack rebase --upstack`                                                                                        |
| Rebase conflict                     | Resolve files, `git add` them, then `gh stack rebase --continue`; consult the companion skill for abort/edge cases |
| Need to split a committed layer     | Reset only local/safe commits, stage selectively, recommit, then rebase descendants                                |
| Need structural reorder/drop/rename | Stop and consult the companion `gh-stack` skill before rewriting stack state                                       |
| Need branch deletion                | Delete only when explicitly requested; consult the companion skill first for submitted stacks                      |
| Submission behaves unexpectedly     | Inspect stack state and consult the companion `gh-stack` skill / `gh stack submit --help` before retrying writes   |

### Interrupted Rebase

First run `git status` and determine whether the active operation came from `gh stack rebase` or from a raw `git rebase` that you deliberately started.

- For a stack rebase, follow the companion `gh-stack` continuation/abort flow.
- For a raw rebase, use `git rebase --continue` or `git rebase --abort` as appropriate.

Do not mix the two recovery paths.
