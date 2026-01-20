"""Tests for git Dockerfile helpers."""

from __future__ import annotations

from library.utils.git import build_git_show_args


def test_fetch_dockerfile_path_builds_correct_git_show_args() -> None:
    """Build git show arguments for a Dockerfile path."""
    repo = "https://github.com/opencadc/canfar-library"
    ref = "refs/heads/main"
    commit = "1234567890"
    path = "images/sample"
    dockerfile = "Dockerfile"
    args = build_git_show_args(repo, ref, commit, path, dockerfile)
    assert args[-1] == f"{commit}:{path}/{dockerfile}"
