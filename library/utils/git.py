"""Git helpers for retrieving repository files."""

from __future__ import annotations

import tempfile
from pathlib import Path

from git import Repo


def build_git_show_args(
    repo: str,
    ref: str,
    commit: str,
    path: str,
    dockerfile: str,
) -> list[str]:
    """Build the git show arguments for a Dockerfile.

    Args:
        repo: Git repository URL.
        ref: Git ref to fetch.
        commit: Commit SHA to read from.
        path: Path to the directory containing the Dockerfile.
        dockerfile: Dockerfile filename.

    Returns:
        The git show command arguments.
    """
    return ["git", "show", f"{commit}:{path}/{dockerfile}"]


def fetch_dockerfile(
    repo: str, ref: str, commit: str, path: str, dockerfile: str
) -> str:
    """Fetch a Dockerfile from a git repository without a checkout.

    Args:
        repo: Git repository URL.
        ref: Git ref to fetch.
        commit: Commit SHA to read from.
        path: Path to the directory containing the Dockerfile.
        dockerfile: Dockerfile filename.

    Returns:
        The Dockerfile contents.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        repository = Repo.init(temp_path)
        origin = repository.create_remote("origin", repo)
        origin.fetch(ref, depth=1)
        blob = f"{commit}:{path}/{dockerfile}"
        return repository.git.show(blob)
