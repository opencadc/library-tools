"""HTTP helpers for retrieving repository files."""

from __future__ import annotations

import posixpath
import urllib
import urllib.error
import urllib.request
from urllib.parse import urlparse

from library import ALLOWED_GIT_SOURCES


def _normalize_repo_path(path: str) -> str:
    """Normalize repository path to a slug without leading slash or .git.

    Args:
        path: Repository path from the URL.

    Returns:
        Normalized repository slug.

    Raises:
        ValueError: If the path is empty after normalization.
    """
    normalized = _strip_git_suffix(path.strip("/"))
    if not normalized:
        raise ValueError("Repository path is missing.")
    return normalized


def _strip_git_suffix(path: str) -> str:
    """Strip a trailing .git suffix.

    Args:
        path: Repository path.

    Returns:
        Repository path without a .git suffix.
    """
    if path.endswith(".git"):
        return path[: -len(".git")]
    return path


def _normalize_file_path(path: str | None, filename: str) -> str:
    """Normalize a repo-relative file path.

    Args:
        path: Directory path within the repository.
        filename: File name to append.

    Returns:
        Repo-relative path to the file.
    """
    base = _clean_repo_subdir(path)
    if not base:
        return filename
    return posixpath.join(base, filename)


def _clean_repo_subdir(path: str | None) -> str:
    """Clean a repository subdirectory path.

    Args:
        path: Directory path within the repository.

    Returns:
        Normalized subdirectory path or empty string.
    """
    base = (path or "").strip()
    if base in {"", ".", "./"}:
        return ""
    if base.startswith("./"):
        base = base[2:]
    if base.startswith("/"):
        base = base[1:]
    base = base.rstrip("/")
    return base


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
    _validate_scheme(parsed.scheme)
    payload = _fetch_payload(raw_url, timeout)
    return _decode_payload(payload, raw_url)


def _validate_scheme(scheme: str) -> None:
    """Validate a URL scheme.

    Args:
        scheme: URL scheme.

    Raises:
        ValueError: If the scheme is not http or https.
    """
    if scheme not in {"http", "https"}:
        raise ValueError("Unsupported URL scheme.")


def _fetch_payload(raw_url: str, timeout: float) -> bytes:
    """Fetch remote payload data.

    Args:
        raw_url: Raw file URL to fetch.
        timeout: Timeout in seconds for the HTTP request.

    Returns:
        Raw response payload.

    Raises:
        RuntimeError: For network errors or HTTP errors.
    """
    try:
        with urllib.request.urlopen(raw_url, timeout=timeout) as response:
            status = response.getcode()
            if status is not None and status != 200:
                raise RuntimeError(f"Fetch failed ({status}) for {raw_url}")
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Fetch failed ({exc.code}) for {raw_url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to fetch URL {raw_url}: {exc}") from exc


def _decode_payload(payload: bytes, raw_url: str) -> str:
    """Decode response payload as UTF-8.

    Args:
        payload: Raw response payload.
        raw_url: Source URL for error messages.

    Returns:
        Decoded payload as text.

    Raises:
        RuntimeError: If decoding fails.
    """
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"Failed to decode content as UTF-8 for {raw_url}") from exc
