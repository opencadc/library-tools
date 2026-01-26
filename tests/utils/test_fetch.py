"""Tests for fetch utilities."""

from __future__ import annotations

import httpx
import pytest

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


class DummyClient:
    """Stub httpx client for fetch.contents tests."""

    def __init__(self, response: httpx.Response | None = None, error: Exception | None = None):
        self._response = response
        self._error = error

    def __enter__(self) -> "DummyClient":
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> bool:
        return False

    def get(self, _url: str) -> httpx.Response:
        if self._error is not None:
            raise self._error
        if self._response is None:
            raise AssertionError("DummyClient requires a response or error")
        return self._response


def test_fetch_contents_returns_text(monkeypatch) -> None:
    """Return response text on success."""
    request = httpx.Request("GET", "https://example.com/file")
    response = httpx.Response(200, request=request, content=b"FROM scratch")
    monkeypatch.setattr(fetch.httpx, "Client", lambda **_kwargs: DummyClient(response))
    assert fetch.contents("https://example.com/file") == "FROM scratch"


def test_fetch_contents_raises_on_http_error(monkeypatch) -> None:
    """Raise a RuntimeError for non-200 responses."""
    request = httpx.Request("GET", "https://example.com/file")
    response = httpx.Response(404, request=request, content=b"Not Found")
    monkeypatch.setattr(fetch.httpx, "Client", lambda **_kwargs: DummyClient(response))
    with pytest.raises(RuntimeError, match=r"Fetch failed \(404\)"):
        fetch.contents("https://example.com/file")


def test_fetch_contents_raises_on_request_error(monkeypatch) -> None:
    """Raise a RuntimeError when httpx raises a request error."""
    error = httpx.RequestError(
        "boom", request=httpx.Request("GET", "https://x")
    )
    monkeypatch.setattr(fetch.httpx, "Client", lambda **_kwargs: DummyClient(error=error))
    with pytest.raises(RuntimeError, match="Failed to fetch URL"):
        fetch.contents("https://x")
