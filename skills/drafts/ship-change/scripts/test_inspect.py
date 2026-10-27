"""Hermetic inspector tests, using only temporary Git repositories."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def call(*args: str, cwd: Path, check: bool = True):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


class InspectTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.origin = self.root / "remote.git"
        self.repo = self.root / "repo"
        call("git", "init", "--bare", str(self.origin), cwd=self.root)
        call("git", "init", "-b", "main", str(self.repo), cwd=self.root)
        call("git", "config", "user.name", "Temporary Test", cwd=self.repo)
        call("git", "config", "user.email", "test@example.invalid", cwd=self.repo)
        (self.repo / "README.md").write_text("initial\n")
        call("git", "add", "README.md", cwd=self.repo)
        call("git", "commit", "-m", "chore: initialize", cwd=self.repo)
        call("git", "remote", "add", "origin", str(self.origin), cwd=self.repo)
        call("git", "push", "-u", "origin", "main", cwd=self.repo)
        call("git", "fetch", "origin", cwd=self.repo)

    def inspect(self, mode="start", *, cwd=None, base="origin/main", extra=()):
        result = call(sys.executable, str(HERE / "inspect.py"), "--mode", mode,
                      "--base", base, "--json", *extra, cwd=cwd or self.repo, check=False)
        return result.returncode, json.loads(result.stdout or result.stderr)

    def new_branch(self, name="agent/one"):
        call("git", "switch", "-c", name, cwd=self.repo)

    def commit_file(self, path="a.txt", content="hello\n"):
        dest = self.repo / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)
        call("git", "add", "--", path, cwd=self.repo)
        call("git", "commit", "-m", "feat(test): add file", cwd=self.repo)

    def codes(self, data):
        return {x["code"] for x in data["diagnostics"]}

    def test_read_only_clean_checkout(self):
        before = call("git", "status", "--porcelain", cwd=self.repo).stdout
        head = call("git", "rev-parse", "HEAD", cwd=self.repo).stdout
        code, result = self.inspect("start")
        self.assertEqual(code, 0)
        self.assertEqual(result["current_branch"], "main")
        self.assertEqual(call("git", "status", "--porcelain", cwd=self.repo).stdout, before)
        self.assertEqual(call("git", "rev-parse", "HEAD", cwd=self.repo).stdout, head)

    def test_trunk_finish_blocks(self):
        code, result = self.inspect("finish")
        self.assertEqual(code, 2)
        self.assertIn("on-trunk", self.codes(result))

    def test_detached_head_blocks(self):
        call("git", "checkout", "--detach", cwd=self.repo)
        code, result = self.inspect()
        self.assertEqual(code, 2)
        self.assertIn("detached-head", self.codes(result))

    def test_dirty_finish_blocked(self):
        self.new_branch()
        (self.repo / "README.md").write_text("edited\n")
        code, result = self.inspect("finish")
        self.assertEqual(code, 2)
        self.assertIn("dirty-tree", self.codes(result))

    def test_sensitivity_untracked_and_committed(self):
        self.new_branch()
        (self.repo / ".env.secret").write_text("TOKEN=demo\n")
        code, result = self.inspect()
        self.assertEqual(code, 0)
        self.assertIn(".env.secret", result["sensitive_paths"])
        (self.repo / ".env.secret").unlink()
        self.commit_file(".github/workflows/ci.yml", "name: test\n")
        code, result = self.inspect("finish")
        self.assertEqual(code, 0)  # Advisory, never merge authority
        self.assertIn(".github/workflows/ci.yml", result["sensitive_paths"])
        self.assertIn("sensitive-paths", self.codes(result))

    def test_missing_base(self):
        code, result = self.inspect(base="origin/missing")
        self.assertEqual(code, 2)
        self.assertIn("missing-base", self.codes(result))

    def test_bad_base_validation(self):
        for ref in ("origin/HEAD", "origin/foo..bar", "origin/foo.lock", "origin/foo bar"):
            code, result = self.inspect(base=ref)
            self.assertEqual(code, 3, ref)
            self.assertIn("error", result)

    def test_head_mismatch(self):
        code, result = self.inspect(extra=("--expected-head", "0" * 40))
        self.assertEqual(code, 2)
        self.assertIn("head-moved", self.codes(result))

    def test_branch_mismatch(self):
        code, result = self.inspect(extra=("--expected-branch", "agent/other"))
        self.assertEqual(code, 2)
        self.assertIn("wrong-branch", self.codes(result))

    def test_linked_worktree(self):
        sibling = self.root / "wt-other"
        call("git", "worktree", "add", "-b", "agent/second", str(sibling), "origin/main", cwd=self.repo)
        code, result = self.inspect(cwd=sibling)
        self.assertEqual(code, 0)
        self.assertEqual(result["worktree"]["path"], str(sibling))

    def test_pathname_with_line_break(self):
        self.new_branch()
        name = "multi\nline.txt"
        self.commit_file(name)
        code, result = self.inspect("finish")
        self.assertEqual(code, 0)
        self.assertIn(name, result["branch_changed_paths"])

    def test_upstream_remote_divergence(self):
        self.new_branch("agent/diverge")
        self.commit_file("tracked.txt")
        call("git", "push", "-u", "origin", "agent/diverge", cwd=self.repo)
        # Advance the remote via a different local clone and fetch it here.
        other = self.root / "other"
        call("git", "clone", str(self.origin), str(other), cwd=self.root)
        call("git", "config", "user.name", "Other", cwd=other)
        call("git", "config", "user.email", "other@example.invalid", cwd=other)
        call("git", "switch", "agent/diverge", cwd=other)
        (other / "remote.txt").write_text("remote\n")
        call("git", "add", "remote.txt", cwd=other)
        call("git", "commit", "-m", "feat: remote", cwd=other)
        call("git", "push", "origin", "agent/diverge", cwd=other)
        call("git", "fetch", "origin", cwd=self.repo)
        code, result = self.inspect("finish")
        self.assertEqual(code, 0)
        self.assertIn("upstream-divergence", self.codes(result))

    def test_branch_inventory(self):
        call("git", "branch", "agent/unused", cwd=self.repo)
        code, result = self.inspect("audit")
        self.assertEqual(code, 0)
        self.assertIn("agent/unused", [x["name"] for x in result["branches"]])


if __name__ == "__main__":
    unittest.main()
