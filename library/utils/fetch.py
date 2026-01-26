"""HTTP helpers for retrieving repository files."""

from __future__ import annotations

import posixpath
from urllib.parse import urlparse

import httpx

from library.config import ALLOWED_GIT_SOURCES


def _normalize_repo_path(path: str) -> str:
    """Normalize repository path to a slug without leading slash or .git.

    Args:
        path: Repository path from the URL.

    Returns:
        Normalized repository slug.

    Raises:
        ValueError: If the path is empty after normalization.
    """
    normalized = path.strip("/")
    if normalized.endswith(".git"):
        normalized = normalized[: -len(".git")]
    if not normalized:
        raise ValueError("Repository path is missing.")
    return normalized


def _normalize_file_path(path: str | None, filename: str) -> str:
    """Normalize a repo-relative file path.

    Args:
        path: Directory path within the repository.
        filename: File name to append.

    Returns:
        Repo-relative path to the file.
    """
    base = (path or "").strip()
    if base in {"", ".", "./"}:
        return filename
    if base.startswith("./"):
        base = base[2:]
    if base.startswith("/"):
        base = base[1:]
    base = base.rstrip("/")
    if not base:
        return filename
    return posixpath.join(base, filename)


def url(repo: str, commit: str, path: str | None, filename: str) -> str:
    """Build a raw file URL for a hosted git repository.

    Args:
        repo: Git repository URL.
        commit: Commit SHA to read from.
        path: Path to the directory containing the file.
        filename: File name to fetch.

    Returns:
        Raw URL to the requested file.

    Raises:
        ValueError: If the repo host is not supported or inputs are invalid.
    """
    parsed = urlparse(repo)
    host = parsed.hostname
    if host is None or host not in ALLOWED_GIT_SOURCES:
        raise ValueError("Unsupported git host.")

    repo_path = _normalize_repo_path(parsed.path)
    file_path = _normalize_file_path(path, filename)

    if host == "github.com":
        return f"https://raw.githubusercontent.com/{repo_path}/{commit}/{file_path}"
    if host == "gitlab.com":
        return f"https://gitlab.com/{repo_path}/-/raw/{commit}/{file_path}"

    raise ValueError("Unsupported git host.")


def contents(raw_url: str, timeout: float = 10.0) -> str:
    """Fetch raw file contents via HTTP.

    Args:
        raw_url: Raw file URL to fetch.
        timeout: Timeout in seconds for the HTTP request.

    Returns:
        Text content from the remote file.

    Raises:
        ValueError: If the URL scheme is not http or https.
        RuntimeError: For network errors, HTTP errors, or decode failures.
    """
    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Unsupported URL scheme.")

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(raw_url)
    except httpx.RequestError as exc:
        raise RuntimeError(f"Failed to fetch URL {raw_url}: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(f"Fetch failed ({response.status_code}) for {raw_url}")

    try:
        return response.content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(
            f"Failed to decode content as UTF-8 for {raw_url}"
        ) from exc
