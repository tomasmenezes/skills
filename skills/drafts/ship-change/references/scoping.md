# Choosing the change boundary

## Decision test

**CONTINUE existing PR** only if: (a) same task/outcome/acceptance; (b) branch and remote ownership verified; (c) PR is open and not already merged; (d) PR base and current diff still match task; (e) action is a correction or completion, not scope expansion. If all true, update it; otherwise do not adopt implicitly.

**START independently** if a change can be safely reviewed and integrated from current trunk even when another PR is open. Related folder, feature family, roadmap issue, user chat or the fact that Graphite is installed is not a dependency.

**STACK** only if the child cannot be validated/integrated without unmerged parent code. Record what symbol/interface/change it consumes; parent/child PRs, order, current base and final target. Prefer merging a backward-compatible foundation first over building long stacks. Typical depth 2–3 is a triage heuristic, not a hard limit.

**GROUP** one feature's code, states, tests, and necessary docs in one PR when they form the same acceptance unit. Split mechanical refactors only if independently useful and safe. Never create a PR whose only purpose is satisfying an arbitrary tiny-diff rule.

**EXPERIMENT** in a bounded branch (optionally draft PR); decide separately whether its result is intended for trunk. A design-lab variant may merit production integration if the acceptance contract is to retain working variants; a throwaway exploration may be intentionally discarded without merge.

## Anti-drift checkpoint (before each newly assigned subtask)

1. Does requested output match the open PR's objective and accepted boundaries? If **no**, complete or hand off existing PR, then start a new branch from fetched trunk.
2. Is the current PR already integrated? If **yes**, new work starts fresh even if called a 'small follow-up'.
3. Does the new work genuinely depend on unmerged code? If **yes**, consider a tracked child; if **no**, do not stack.
4. Are there uncommitted changes of unknown provenance? If **yes**, preserve and isolate, do not unconditionally stash or absorb.
5. Is completing scope impossible without a material product/architecture decision? If **yes**, record the decision in the proper authority (e.g. owning issue) and escalate rather than inventing acceptance criteria.

**Practical granularity:** keep PR size reviewable; avoid rigid per-commit/PR line, file or time limits. Escalate exceptionally large diffs, significant generated outputs, or cross-cutting changes for review. A single coherent mechanical update can be larger than a complex three-line authorization change.
