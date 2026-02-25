"""Tests for the init CLI command."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import library.cli.init as cli_init
from library import DEFAULT_LIBRARY_MANIFEST_FILENAME, schema
from library.tools import defaults as runtime_defaults
from richforms import FormConfig
from tests.cli.conftest import cli


def _sample_form() -> cli_init.InitForm:
    return cli_init.InitForm(
        registry=schema.Registry(
            host="images.canfar.net",
            project="library",
            image="sample-image",
        ),
        build=schema.Build(
            context=".",
            file="Dockerfile",
            tags=["latest"],
        ),
        metadata=schema.Metadata(
            discovery=schema.Discovery(
                title="Sample Image",
                description="Sample description for testing.",
                source="https://github.com/opencadc/canfar-library",
                url="https://images.canfar.net/library/sample-image",
                documentation="https://canfar.net/docs/user-guide",
                version="1.0.0",
                revision="abc123",
                created=datetime(2026, 2, 23, 12, 0, 0, tzinfo=timezone.utc),
                authors=[
                    schema.Author(
                        name="Example Maintainer",
                        email="maintainer@example.com",
                    )
                ],
                licenses="MIT",
                keywords=["sample", "testing"],
                kind=["headless"],
                tools=["python"],
            )
        ),
    )


def test_library_init_writes_default_manifest(cli_runner, monkeypatch) -> None:
    """Init should write a valid manifest with materialized default config."""
    monkeypatch.setattr(cli_init, "collect_init_form", lambda: _sample_form())

    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(cli, ["init"])
        manifest_path = Path(DEFAULT_LIBRARY_MANIFEST_FILENAME)

        assert result.exit_code == 0
        assert manifest_path.is_file()
        model = schema.Schema.from_yaml(manifest_path)
        assert model.metadata.discovery.created == datetime(
            2026, 2, 23, 12, 0, 0, tzinfo=timezone.utc
        )
        assert model.metadata.discovery.revision == "abc123"
        assert model.config.cli == runtime_defaults.default_cli()
        assert len(model.config.tools) == len(runtime_defaults.default_tools())


def test_library_init_creates_parent_directories(cli_runner, monkeypatch) -> None:
    """Init should create missing parent directories for --output paths."""
    monkeypatch.setattr(cli_init, "collect_init_form", lambda: _sample_form())

    with cli_runner.isolated_filesystem():
        output = Path("manifests/sample.yaml")
        result = cli_runner.invoke(cli, ["init", "--output", str(output)])

        assert result.exit_code == 0
        assert output.is_file()
        schema.Schema.from_yaml(output)


def test_library_init_decline_overwrite_keeps_existing_file(
    cli_runner, monkeypatch
) -> None:
    """Declining overwrite should leave existing manifest unchanged and exit 0."""
    monkeypatch.setattr(cli_init, "collect_init_form", lambda: _sample_form())

    with cli_runner.isolated_filesystem():
        output = Path(DEFAULT_LIBRARY_MANIFEST_FILENAME)
        output.write_text("keep-me\n", encoding="utf-8")

        result = cli_runner.invoke(cli, ["init"], input="n\n")

        assert result.exit_code == 0
        assert output.read_text(encoding="utf-8") == "keep-me\n"
        assert "left unchanged" in result.stdout


def test_library_init_accept_overwrite_replaces_existing_file(
    cli_runner, monkeypatch
) -> None:
    """Accepting overwrite should replace existing output with a valid manifest."""
    monkeypatch.setattr(cli_init, "collect_init_form", lambda: _sample_form())

    with cli_runner.isolated_filesystem():
        output = Path(DEFAULT_LIBRARY_MANIFEST_FILENAME)
        output.write_text("old-content\n", encoding="utf-8")

        result = cli_runner.invoke(cli, ["init"], input="y\n")

        assert result.exit_code == 0
        model = schema.Schema.from_yaml(output)
        assert model.registry.image == "sample-image"


def test_library_init_handles_keyboard_interrupt(cli_runner, monkeypatch) -> None:
    """Keyboard interrupt should exit with 130."""
    def raise_interrupt() -> cli_init.InitForm:
        raise KeyboardInterrupt

    monkeypatch.setattr(cli_init, "collect_init_form", raise_interrupt)

    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(cli, ["init"])

        assert result.exit_code == 130


def test_collect_init_form_uses_init_schema_and_injected_defaults(monkeypatch) -> None:
    """collect_init_form should prompt init form model with prefilled revision."""
    captured: dict[str, object] = {}
    sample = _sample_form()

    def fake_fill(model, *, initial, config):
        captured["model"] = model
        captured["initial"] = initial
        captured["config"] = config
        return sample

    monkeypatch.setattr(cli_init, "fill", fake_fill)
    monkeypatch.setattr(cli_init, "_current_revision", lambda: "deadbeef")

    form = cli_init.collect_init_form()

    assert form is sample
    assert captured["model"] is cli_init.InitForm
    assert isinstance(captured["config"], FormConfig)
    initial = captured["initial"]
    assert isinstance(initial, dict)
    assert initial["metadata"]["discovery"]["revision"] == "deadbeef"
    assert "config" not in initial
