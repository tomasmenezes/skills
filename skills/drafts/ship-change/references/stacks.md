# Conditional Graphite use: genuine unmerged dependencies only

This reference is based on current Graphite documentation, NOT adopted from the uploaded `graphite-commit` workflow. The only material retained from that old skill is the Conventional Commit message structure in `commits.md`.

## Preconditions

- Every branch/PR has a distinct accepted outcome; child uses code that only exists on its **unmerged parent**. Record exact dependency and parent/base PR mapping. Merely touching the same component or working on one issue does not justify a stack.
- Verify installed `gt` command syntax (`gt --version`, `gt <subcommand> --help`), configured trunk, local graph (`gt log`), remote PR state and worktree ownership. Graphite's shared stack metadata plus branch history can affect multiple workers; do not let two agents re-parent/restack the same stack at once.
- Prefer merging a ready backward-compatible base before making children. Aim for shallow stacks (2–3 is a review signal, not a hard limit). No new unrelated layers on top of an old stack, ever.
- Keep GitHub PR bases correct. GitHub's normal three-dot diff of child vs trunk incorrectly includes ancestor changes; verify child against its **PR parent**. CI/merge systems may run integration tests on different combinations; check each independently valid layer and rollout consistency.

## Operating principle (verify CLI for specific installation)

1. Start from verified trunk for first branch; create base PR with Conventional Commit subject.
2. Create a child branch **only when needed** from that base's branch; submit each PR with its actual base. Avoid `--all` or automatic staging of unrelated work.
3. A child should compile/test in the context of the parent, not pretend to be independent of it; merged base should be safe on its own.
4. Merge base first with applicable per-PR authority. Re-read remote state. Then sync/rebase/re-target child as applicable, re-run changed-head checks and obtain fresh required approvals.
5. Coordinate before `gt sync`/`gt restack`: current Graphite documentation says these can update trunk, restack/rebase branches and remove merged references. On a repo with parallel agent worktrees, those operations can alter another agent's branch history. Don't run them as unattended blanket cleanup. Use a single stack owner; preserve remote refs and perform targeted recovery where needed.
6. Do not rely on a blanket “merge stack” button to bypass per-PR risk/approval boundaries. If Graphite's automated merge integrates multiple PRs, ensure every included PR is authorized and GitHub policy is enforced.

## Failure modes

- **Wrong parent**: STOP; inspect each branch's merge-base/PR base and owner, decide whether safe to re-parent or recreate from trunk. Don't run `gt track`/`gt restack` blind.
- **Old stack contains unrelated work**: freeze; inventory commits and hunks, split from fetched trunk as suitable, preserve originals until replacement PRs are verified and integrated.
- **Base squashed or merged**: verify merger, coordinate sync, check for duplicate ancestor commits and re-run validation on children.
- **Parent rejected/closed without merge**: child cannot advance on an assumed base; re-plan or intentionally port required subset as separate PR.
- **Other agent editing child**: do not amend/rebase/push rewritten history without ownership coordination.
- **GitHub stale-review dismissal**: Graphite warns that some required fresh-approval configurations may be incompatible with Graphite UI stack merging; obey strict protection and choose safe per-PR integration instead of relaxing protections.

Current provider documentation: https://graphite.com/docs/merge-stack-prs-github and https://graphite.com/docs/cli-quick-start. CLI invocation examples are intentionally omitted here: `gt` versions and stack/checkout integration vary. Use installed CLI help rather than copy-pasting legacy flags.
