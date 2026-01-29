"""Tests for fetch utilities."""

from __future__ import annotations

import pytest

from email.message import Message

from library.utils import fetch


def test_fetch_url_builds_github_raw_url() -> None:
    """Build a GitHub raw URL for a Dockerfile path."""
    repo = "https://github.com/opencadc/canfar-library.git"
    commit = "abc123"
    path = "images/base"
    dockerfile = "Dockerfile"
    assert (
        fetch.url(repo, commit, path, dockerfile)
        == "https://raw.githubusercontent.com/opencadc/canfar-library/abc123/images/base/Dockerfile"
    )


def test_fetch_url_builds_gitlab_raw_url() -> None:
    """Build a GitLab raw URL for a Dockerfile path."""
    repo = "https://gitlab.com/group/subgroup/project"
    commit = "deadbeef"
    path = "./"
    dockerfile = "Dockerfile"
    assert (
        fetch.url(repo, commit, path, dockerfile)
        == "https://gitlab.com/group/subgroup/project/-/raw/deadbeef/Dockerfile"
    )


def test_fetch_url_rejects_disallowed_host() -> None:
    """Reject unsupported git host names."""
    with pytest.raises(ValueError, match="Unsupported git host"):
        fetch.url("https://example.com/org/repo", "abc", ".", "Dockerfile")


class DummyResponse:
    """Stub response for urllib fetch tests."""

    def __init__(self, status: int, body: bytes) -> None:
        self._status = status
        self._body = body

    def __enter__(self) -> "DummyResponse":
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        return None

    def getcode(self) -> int:
        """Return the HTTP status code."""
        return self._status

    def read(self) -> bytes:
        """Return response payload."""
        return self._body


def test_fetch_contents_returns_text(monkeypatch) -> None:
    """Return response text on success."""
    response = DummyResponse(200, b"FROM scratch")
    monkeypatch.setattr(
        fetch.urllib.request, "urlopen", lambda *_args, **_kwargs: response
    )
    assert fetch.contents("https://example.com/file") == "FROM scratch"


def test_fetch_contents_raises_on_http_error(monkeypatch) -> None:
    """Raise a RuntimeError for non-200 responses."""
    error = fetch.urllib.error.HTTPError(
        "https://example.com/file", 404, "Not Found", Message(), None
    )

    def raise_error(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(fetch.urllib.request, "urlopen", raise_error)
    with pytest.raises(RuntimeError, match=r"Fetch failed \(404\)"):
        fetch.contents("https://example.com/file")


def test_fetch_contents_raises_on_request_error(monkeypatch) -> None:
    """Raise a RuntimeError when urllib raises a request error."""
    error = fetch.urllib.error.URLError("boom")

    def raise_error(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(fetch.urllib.request, "urlopen", raise_error)
    with pytest.raises(RuntimeError, match="Failed to fetch URL"):
        fetch.contents("https://x")
