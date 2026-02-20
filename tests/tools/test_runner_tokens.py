"""Tests for command token rendering."""

from __future__ import annotations

import pytest

from library.schema import ToolInputs
from library.tools import render


def test_render_inputs_and_image_reference_tokens() -> None:
    """inputs and image.reference tokens resolve to deterministic values."""
    rendered = render.command(
        cmd=[
            "trivy",
            "image",
            "--config",
            "{{inputs.trivy}}",
            "{{image.reference}}",
        ],
        inputs={
            "trivy": ToolInputs(source="default", destination="/config/trivy.yaml")
        },
        image_reference="images.canfar.net/library/sample:latest",
    )

    assert rendered == [
        "trivy",
        "image",
        "--config",
        "/config/trivy.yaml",
        "images.canfar.net/library/sample:latest",
    ]


def test_render_unsupported_token_fails() -> None:
    """Only inputs.* and image.reference tokens are supported."""
    with pytest.raises(ValueError):
        render.command(
            cmd=["{{outputs}}"],
            inputs={},
            image_reference="images.canfar.net/library/sample:latest",
        )


def test_render_undeclared_input_token_fails() -> None:
    """Referencing an undeclared input key fails."""
    with pytest.raises(ValueError):
        render.command(
            cmd=["{{inputs.missing}}"],
            inputs={
                "trivy": ToolInputs(source="default", destination="/config/trivy.yaml")
            },
            image_reference="images.canfar.net/library/sample:latest",
        )
