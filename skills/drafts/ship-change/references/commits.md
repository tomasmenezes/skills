# Conventional Commit message structure

**This is the only convention imported from the user-supplied `graphite-commit` skill.** Its Graphite commands, stack procedures, branch naming rules and absolute preference for more PRs are not adopted. These messages work with plain `git commit`, GitHub squash commits, and optional Graphite operations alike.

```text
<type>(<optional scope>): <imperative, specific description>

<optional brief body>

<optional footer>
```

- Choose a type from: `feat`, `fix`, `docs`, `style` (formatting/no logic), `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Scope: optional but encouraged when useful; use the smallest informative subsystem/component. Avoid a scope that's just an issue number.
- Subject: imperative present tense (`add`, `fix`, `remove`), specific and compact, no trailing period; aim for <72 characters where practical, but clarity wins. **Commit title and PR title should describe the same logical change**; with squash merge, ensure the final squash subject is conventional.
- Body: prefer a concise explanation for non-obvious decisions or when helpful even for a small change; describe **why**, tradeoffs, migration or validation, rather than restating the diff. Do not pad obvious changes with boilerplate.
- Footer: `Refs #456` or `Part of #456` for partial issues; `Closes #123` only if this merged change fulfills the entire issue and closure is intended. Beware GitHub's closing keywords in PR bodies/commit messages: they can close an issue automatically on the default branch.
- Breaking API/contract change: add `!` after the type/scope and/or an explicit `BREAKING CHANGE: ...` footer describing impact and migration.
- Never combine unrelated changes in one commit just to shorten the history; nor generate empty/artificial commits to satisfy a quota.

Examples:

```text
feat(map): add mobile results drawer

Keep drag state outside card selection so scrolling the drawer
cannot accidentally select a listing.

Part of #95
```

```text
fix(cards): handle missing inventory status
```

```text
feat(api)!: remove legacy inventory endpoint

BREAKING CHANGE: clients must use /v2/inventory; migrate callers first.
Refs #204
```

**Important:** This is a *message convention*, not a reason to use Graphite. Only use Graphite for a true dependency between **unmerged** PRs.
