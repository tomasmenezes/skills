# ship-change — agent lifecycle skill (v2)

A Git-first, PR-centered source-control skill for solo builders and small multi-agent teams. It replaces the *lifecycle* instructions of `git-commit` and `graphite-commit`; only the latter's **Conventional Commit message structure** survives in `references/commits.md`. Optional Graphite stacks are supported when there are genuine dependencies between unmerged PRs. No Graphite command workflow was copied from the uploaded skill.

## Install

Extract `ship-change` under the skill root recognized by your agent, commonly `<repo>/.agents/skills/ship-change/` (check your agent's actual skill discovery path). A Claude Code configuration may use `<repo>/.claude/skills/ship-change/`. Do not register both as competing coordinators. Invoke `ship-change` whenever implementing code, committing, continuing a PR, stacking or auditing branches. Archive/disable existing commit lifecycle skills to avoid both matching the same intent; if retained, use only as explicitly invoked low-level references.

Suggested minimal `AGENTS.md` addition:

```md
- Use `ship-change` for code change/commit/PR lifecycles. Every independent
  deliverable gets its own bounded PR, with a fresh branch from fetched trunk.
  Continue existing PRs only for the same outcome. Do not reuse old Graphite
  stacks. Follow `references/commits.md` for conventional commit messages.
- Never treat successful CI or this agent's assessment as merge permission.
  Integrate only with verified delegated authority and trusted GitHub rules.
  Never deploy or make production changes without separate authorization.
```

## Diagnostics

Run **after** separately fetching the remote (the script does not fetch):

```bash
python3 /absolute/path/to/ship-change/scripts/inspect.py \
  --mode start --base origin/main --json
python3 /absolute/path/to/ship-change/scripts/inspect.py \
  --mode finish --base origin/main --expected-branch agent/95-mobile-drawer --json
python3 /absolute/path/to/ship-change/scripts/inspect.py \
  --mode audit --base origin/main --json
python3 -m unittest discover -s /absolute/path/to/ship-change/scripts -p 'test_*.py' -v
```

Exit 0 means **no local inspection blockers**, not permission to merge. Exit 2 means local blockers; 3 means inspection error. The script does not contact GitHub, verify CI or branch rules, or decide semantic safety. It never mutates Git state; Git is invoked with optional locks disabled.

## Deployment and permissions

No changes are made to GitHub branch protection, auto-merge settings, `AGENTS.md`, CI, or the repository by installing this ZIP. The skill alone is insufficient for unattended merge. Configure independent branch protection and merge delegation first. Merging to `main` may trigger other actions; inspect workflows before delegation. Default behavior is prepare/submit PR and hand off.

## Tested

Hermetic Git regression tests cover clean/dirty states, detached HEAD, missing or divergent base, branch ownership, linked worktrees, filenames with whitespace, sensitive files, upstream divergence, and JSON inspector output. They do not exercise live GitHub/Graphite merge APIs.

Official references: https://agentskills.io/specification ; https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/automatically-merging-a-pull-request ; https://graphite.com/docs/merge-stack-prs-github .
