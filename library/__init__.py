"""CANFAR Science Platform Container Library"""

from pathlib import Path

HADOLINT_CONFIG_PATH = Path(__file__).resolve().parent / ".hadolint.yaml"
RENOVATE_CONFIG_PATH = Path(__file__).resolve().parent / "renovate.json5"
TRIVY_CONFIG_PATH = Path(__file__).resolve().parent / ".trivy.yaml"
DEFAULT_LIBRARY_MANIFEST_FILENAME = ".library.manifest.yaml"
ALLOWED_GIT_SOURCES: list[str] = ["github.com", "gitlab.com"]

__all__ = [
    "HADOLINT_CONFIG_PATH",
    "RENOVATE_CONFIG_PATH",
    "TRIVY_CONFIG_PATH",
    "ALLOWED_GIT_SOURCES",
    "DEFAULT_LIBRARY_MANIFEST_FILENAME",
]
