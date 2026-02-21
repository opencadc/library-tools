"""Output parsers and parser registry for Library tools."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from library.parsers import hadolint, refurbish, trivy


@dataclass(frozen=True, slots=True)
class ParserAdapter:
    """Adapter that bundles parse and report callables for a parser key."""

    parse: Callable[[Path], Any]
    report: Callable[[Any], int]


def registry() -> dict[str, ParserAdapter]:
    """Return built-in parser registry keyed by tool parser name."""
    return {
        "hadolint": ParserAdapter(parse=hadolint.parse, report=hadolint.report),
        "trivy": ParserAdapter(parse=trivy.parse, report=trivy.report),
        "renovate": ParserAdapter(parse=refurbish.parse, report=refurbish.report),
    }


def get(parser: str) -> ParserAdapter:
    """Resolve parser adapter by parser key."""
    adapter = registry().get(parser)
    if adapter is None:
        raise ValueError(f"Unknown parser: {parser}")
    return adapter


__all__ = ["hadolint", "trivy", "refurbish", "ParserAdapter", "registry", "get"]
