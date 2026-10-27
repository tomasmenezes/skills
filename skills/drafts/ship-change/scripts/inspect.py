#!/usr/bin/env python3
"""Local, read-only advisory for ship-change.

NEVER grants readiness/merge authority. Fetch remote refs *before* running;
no network requests, GitHub calls, branch writes, or repo cleanup are performed.
Exit 0=no local blockers, 2=local blockers, 3=inspection error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SENSITIVE = re.compile(
    r"(^|/)(\.github|\.agents|\.claude|migrations?|drizzle|infra|terraform|"
    r"auth|permissions?|payments?|billing|secrets?|deploy|security|"
    r"policies|supabase|rls)(/|\.|$)|"
    r"(^|/)(AGENTS\.md|CODEOWNERS|\.env(?:\..*)?|wrangler\.(?:toml|jsonc?)|"
    r"package\.json|pnpm-lock\.yaml)(?:$|/)", re.I
)


def git(*args: str, cwd: str | Path | None = None, optional: bool = False) -> str | None:
    # GIT_OPTIONAL_LOCKS=0 prevents Git from refreshing the index as a side effect.
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    proc = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", check=False)
    if proc.returncode != 0:
        if optional:
            return None
        raise RuntimeError(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.strip()}")
    return proc.stdout.rstrip("\n")


def diagnostic(out: list[dict[str, str]], severity: str, code: str, message: str) -> None:
    out.append({"severity": severity, "code": code, "message": message})


def worktrees(root: str) -> list[dict[str, Any]]:
    data = git("worktree", "list", "--porcelain", cwd=root) or ""
    result: list[dict[str, Any]] = []
    for section in data.strip().split("\n\n"):
        if not section:
            continue
        item: dict[str, Any] = {}
        for line in section.splitlines():
            if line.startswith("worktree "):
                item["path"] = line[9:]
            elif line.startswith("branch "):
                item["branch"] = line[7:]
            elif line == "detached":
                item["detached"] = True
            elif line.startswith("locked"):
                item["locked"] = True
            elif line.startswith("prunable"):
                item["prunable"] = True
        result.append(item)
    return result


def branch_inventory(root: str, stale_hours: int) -> list[dict[str, Any]]:
    raw = git("for-each-ref", "--format=%(refname:short)%09%(committerdate:unix)%09%(upstream:short)",
              "--sort=-committerdate", "refs/heads", cwd=root) or ""
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    output: list[dict[str, Any]] = []
    for entry in raw.splitlines():
        fields = entry.split("\t")
        if len(fields) != 3:
            continue
        name, ts, upstream = fields
        try:
            age = round((now - float(ts)) / 3600, 1)
        except ValueError:
            age = None
        output.append({"name": name, "upstream": upstream or None, "last_commit_age_hours": age,
                       "possibly_stale": bool(age is not None and age > stale_hours)})
    return output


def remote_ref(base: str) -> str:
    ref = base if base.startswith("refs/remotes/") else f"refs/remotes/{base}"
    if ref.endswith("/HEAD") or "@{" in ref or any(c.isspace() for c in ref):
        raise ValueError("--base must be a branch's remote-tracking ref, not remote HEAD")
    # Validate exact Git refname (instead of trying to maintain a homemade grammar).
    ok = git("check-ref-format", ref, optional=True)
    if ok is None:
        raise ValueError(f"Invalid remote-tracking ref: {ref}")
    if len(ref.split("/")) < 4:
        raise ValueError("--base must be REMOTE/BRANCH e.g. origin/main")
    return ref


def inspect(mode: str, base: str, stale_hours: int, expected_branch: str | None,
            expected_head: str | None) -> dict[str, Any]:
    root = git("rev-parse", "--show-toplevel")
    if not root:
        raise RuntimeError("Not in a non-bare Git working tree")
    root = str(Path(root).resolve())
    head = git("rev-parse", "HEAD") or ""
    current = git("symbolic-ref", "--quiet", "--short", "HEAD", optional=True)
    base_ref = remote_ref(base)
    base_sha = git("rev-parse", "--verify", "--quiet", f"{base_ref}^{{commit}}", optional=True)
    status_data = git("status", "--porcelain=v1", "-z", "--untracked-files=normal") or ""
    # Porcelain -z is NUL-delimited; pathnames may contain newlines.
    entries = status_data.split("\0") if status_data else []
    entries = [s for s in entries if s]
    trees = worktrees(root)
    active_path = str(Path(git("rev-parse", "--show-toplevel") or root).resolve())
    active = next((w for w in trees if str(Path(w.get("path", "")).resolve()) == active_path), None)
    problems: list[dict[str, str]] = []
    if not base_sha:
        diagnostic(problems, "blocker", "missing-base", f"{base_ref} not locally resolved; fetch and recheck target")
    if not current:
        diagnostic(problems, "blocker", "detached-head", "Detached HEAD; recover branch ownership before writing")
    if expected_branch and current != expected_branch:
        diagnostic(problems, "blocker", "wrong-branch", f"Expected {expected_branch!r}, got {current!r}")
    if expected_head and head.lower() != expected_head.lower():
        diagnostic(problems, "blocker", "head-moved", "HEAD changed since handoff; inspect before rewriting/pushing")
    if entries:
        diagnostic(problems, "blocker" if mode == "finish" else "warning", "dirty-tree",
                   "Working tree has staged/unstaged/untracked entries; establish ownership and staging intent")
    if not active:
        diagnostic(problems, "warning", "unknown-worktree", "Current checkout not identified in worktree listing")

    behind = ahead = None
    paths: list[str] = []
    if base_sha:
        graph = git("rev-list", "--left-right", "--count", f"{base_ref}...HEAD", optional=True)
        if graph:
            try:
                behind, ahead = [int(x) for x in graph.split()]
            except ValueError:
                diagnostic(problems, "blocker", "bad-counts", "Unable to interpret ahead/behind counts")
        common = git("merge-base", "HEAD", base_ref, optional=True)
        if not common:
            diagnostic(problems, "blocker", "unrelated-history", "No merge-base with target; do not submit blindly")
        diff = git("diff", "--name-only", "-z", f"{base_ref}...HEAD", optional=True)
        if diff is None:
            diagnostic(problems, "blocker", "diff-unavailable", "Cannot calculate whole branch diff against base")
        else:
            paths = [x for x in diff.split("\0") if x]
    staged = git("diff", "--cached", "--name-only", "-z", optional=True) or ""
    staged_paths = [x for x in staged.split("\0") if x]
    # `git ls-files --others` reports untracked paths without exposing content.
    untracked = git("ls-files", "--others", "--exclude-standard", "-z", optional=True) or ""
    untracked_paths = [x for x in untracked.split("\0") if x]
    risky = sorted(set(p for p in paths + staged_paths + untracked_paths if SENSITIVE.search(p)))
    if risky:
        diagnostic(problems, "warning", "sensitive-paths", "Potentially protected paths present; path warnings are not semantic risk review")
    upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}", optional=True)
    upstream_counts = None
    if upstream:
        counts = git("rev-list", "--left-right", "--count", "@{upstream}...HEAD", optional=True)
        if counts:
            try:
                remote_unique, local_unique = [int(x) for x in counts.split()]
                upstream_counts = {"remote_only_commits": remote_unique, "local_only_commits": local_unique}
                if remote_unique:
                    diagnostic(problems, "warning", "upstream-divergence", "Tracked branch has remote-only commits; don't overwrite them")
            except ValueError:
                pass
    trunk_name = base_ref.split("/", 3)[-1]
    if mode == "finish":
        if current == trunk_name:
            diagnostic(problems, "blocker", "on-trunk", "Cannot submit a feature PR from integration trunk")
        if ahead is None or ahead == 0:
            diagnostic(problems, "blocker", "no-new-commits", "No distinct branch commits verified")
        if behind and behind > 0:
            diagnostic(problems, "warning", "base-advanced", "Target has commits not on HEAD; inspect merge result and CI")
    if mode == "start" and current and current != trunk_name:
        diagnostic(problems, "info", "feature-branch-active", "Independent work still requires new branch from fetched trunk unless continuing this PR")
    inventory = branch_inventory(root, stale_hours) if mode == "audit" else None
    if inventory:
        for b in inventory:
            if b["possibly_stale"] and b["name"] != trunk_name:
                diagnostic(problems, "info", "stale-hint", f"{b['name']} last commit age {b['last_commit_age_hours']} hours (NOT inactivity proof)")
    return {
        "mode": mode, "root": root, "base": base_ref, "base_sha_local": base_sha,
        "current_branch": current, "head_sha": head, "worktree": active, "worktrees": trees,
        "dirty": bool(entries), "status_count": len(entries), "status_preview": entries[:12],
        "ahead_of_base": ahead, "behind_base": behind, "upstream": upstream,
        "upstream_divergence": upstream_counts, "branch_changed_paths": paths,
        "staged_paths": staged_paths, "untracked_paths": untracked_paths[:100],
        "sensitive_paths": risky, "branches": inventory, "diagnostics": problems,
        "disclaimer": "OFFLINE READ-ONLY INSPECTION. Remote freshness, GitHub review/CI/rules, ownership, product quality and merge authority NOT verified."
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("start", "finish", "audit"), default="start")
    p.add_argument("--base", required=True, help="e.g. origin/main or refs/remotes/upstream/dev")
    p.add_argument("--expected-branch")
    p.add_argument("--expected-head", help="exact SHA expected at handoff")
    p.add_argument("--stale-hours", type=int, default=48)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.stale_hours < 1:
        p.error("--stale-hours must be positive")
    try:
        result = inspect(args.mode, args.base, args.stale_hours,
                         args.expected_branch, args.expected_head)
    except (RuntimeError, ValueError, OSError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 3
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['mode']}: {result['current_branch'] or '(detached)'}, base {result['base']}, ahead={result['ahead_of_base']}, behind={result['behind_base']}")
        for d in result["diagnostics"]:
            print(f"[{d['severity']}] {d['code']}: {d['message']}")
        print(result["disclaimer"])
    return 2 if any(d["severity"] == "blocker" for d in result["diagnostics"]) else 0


if __name__ == "__main__":
    sys.exit(main())
