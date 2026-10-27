# Minimal PR and handoff contract

Keep durable product requirements in the owning issue and execution evidence in the PR; do not create competing markdown roadmaps.

```md
## Outcome / issue
- Issue: #...
- Goal: [one-sentence behavior]
- Scope: ... / Explicitly excluded: ...
- Dependency: [none | parent PR #... and why]

## Verification
- HEAD SHA and target base: ...
- Automated checks: [commands + outcomes; note skipped/unavailable]
- Manual/browser checks: [evidence; relevant before/after screenshots]
- Full-diff review: [unexpected changes? migrations? secrets?]

## Risk / integration
- Risk and rollback considerations: ...
- Approval/delegation: [none | owner-approved scope | per-PR reviewed]
- Merge mechanism/gates: [normal GitHub PR | protected queue | paused]
- Deployment/side effects: [none expected | needs separate approval]

## Status
- [DRAFT | READY | WAITING_APPROVAL | BLOCKED | MERGED | ABANDONED]
- Blockers / follow-ups: ...
```

Do not fabricate test results, merge SHA, approval, visual comparison or readiness. PR checks must correspond to current head and actual integration base. Use `Closes #N` only when the PR finishes the **entire** issue; otherwise `Part of #N`. A PR can merge while an issue remains open, especially for a multi-PR roadmap or delayed production activation. Persist decisions and scope change in owning issues, not private local notes only.

A useful final agent response states: what integrated, what remains, PR URL(s), tests/evidence, blockers, whether main was updated, and whether worktree/branch cleanup was safe. No claim of 'done' before verified remote integration, unless clearly describing a 'PR ready' handoff.
