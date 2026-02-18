"""Command token rendering for generic tool execution."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import re

from library.schema import TOOL_TOKEN_PATTERN, ToolInputs


def _resolve_token(
    token_name: str,
    *,
    inputs: Mapping[str, ToolInputs],
    image_reference: str,
) -> str:
    """Resolve a supported command token to a concrete value."""
    if token_name == "image.reference":
        return image_reference
    if token_name.startswith("inputs."):
        input_key = token_name.split(".", maxsplit=1)[1]
        tool_input = inputs.get(input_key)
        if tool_input is None:
            raise ValueError(f"Command references undefined input token: {token_name}")
        return tool_input.destination
    raise ValueError(f"Unsupported command token: {token_name}")


def command(
    command: Sequence[str],
    *,
    inputs: Mapping[str, ToolInputs],
    image_reference: str,
) -> list[str]:
    """Render supported command tokens in a tokenized argv list."""
    rendered: list[str] = []
    for part in command:
        matches = TOOL_TOKEN_PATTERN.findall(part)
        if ("{{" in part or "}}" in part) and not matches:
            raise ValueError("Malformed template token in tool command.")

        def replacer(match: re.Match[str]) -> str:
            token_name = match.group(1)
            return _resolve_token(
                token_name,
                inputs=inputs,
                image_reference=image_reference,
            )

        rendered_part = TOOL_TOKEN_PATTERN.sub(replacer, part)
        if "{{" in rendered_part or "}}" in rendered_part:
            raise ValueError("Malformed template token in tool command.")
        rendered.append(rendered_part)
    return rendered
