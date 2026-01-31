"""Integration tests for the hadolint CLI workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from library.cli.hadolint import run
from tests.cli.conftest import skip_if_docker_unavailable


@pytest.mark.integration
def test_hadolint_chain_dockerfile(tmp_path: Path) -> None:
    """Run hadolint end-to-end using a local Dockerfile."""
    skip_if_docker_unavailable()
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text(
        "\n".join(
            [
                "FROM alpine:3.19",
                'LABEL org.opencontainers.image.title="Sample"',
                'LABEL org.opencontainers.image.description="Sample image"',
                'LABEL org.opencontainers.image.vendor="CANFAR"',
                'LABEL org.opencontainers.image.source="https://example.com/source"',
                'LABEL org.opencontainers.image.licenses="Apache-2.0"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run(None, dockerfile_path, False)
    assert result == 0
