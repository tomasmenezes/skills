# Adoption and governance checklist (repository owner task)

This is NOT part of routine coding-agent activity. Configuring branch protections, required checks, merger identities and deployment gates is a repository-owner task and should be reviewed before enabling unattended merges.

## First stage — PR-first, no autonomous merge

- [ ] Replace matching legacy `git-commit`/`graphite-commit` triggers with `ship-change`; retain only the commit format.
- [ ] Confirm GitHub's actual default/integration branch, push remote, PR base and release workflows.
- [ ] Confirm owning issues define acceptance, while landed main and tests define implementation status.
- [ ] Ensure agent may push feature branches and draft PRs but not alter protected integration branch or policy to grant itself extra permissions.
- [ ] Verify CI includes relevant tests and can be executed for PR changes without exposing privileged secrets to untrusted code. Avoid unsafe `pull_request_target` checkout patterns.
- [ ] Pilot with unrelated feature PRs and one genuinely dependent two-PR stack; verify new work does not reuse previous branch/stack.
- [ ] Pilot interrupted session, dirty checkout and squash merge. Verify no unexpected deletion or history rewrite.

## Second stage — bounded autonomous integration

- [ ] Enable and independently verify protected PR path and required checks/review rules (GitHub settings/rulesets), with no agent bypass or self-approval of protected changes.
- [ ] Define signed/trusted or externally managed delegation: eligible issue/scope, allowed paths/behaviors, protected categories, whether immediate merge/auto-merge/queue is allowed, expiration/revocation and responsible owner. Agent-editable markdown alone is insufficient authorization.
- [ ] Ensure required checks are bound to correct head/integration candidate and cannot be spoofed by arbitrary GitHub Actions job names or replaced by a fork/untrusted actor; specify trusted status-check source where supported.
- [ ] Verify actual effect of merging trunk, including auto-deploy, migrations and external APIs. Keep irreversible release consequences separately authorized or technically gated.
- [ ] Test negative cases: changed policy file, missing CI, branch base switched, reopened draft PR, failing checks, stale approvals, secret detection, parent PR closed, and versioned stack conflicts.
- [ ] Record and monitor stale open PRs, regression/revert rate, time from ready to merge, and human interventions. Don't optimize only on PR count/merge volume.

## Stop conditions

Suspend unattended merges if checks are skipped, a tool uses administrator bypass, required review can be self-granted, the deployment trigger is unknown, incident/rollback risk is uncontrolled, or current tool credentials can edit the merge-policy mechanisms they rely on. Do not fix by weakening the checks.

## About the `allow_auto_merge` flag

The GitHub repository setting controls ability to queue GitHub auto-merge, **not** whether an otherwise fully authorized and protected **immediate merge** may happen. GitHub merge queues have separate behavior. A workflow that checks only `allow_auto_merge` can both block safe authorized work and overlook unsafe merges. Always evaluate actual enforced merge gates and independent delegation.
