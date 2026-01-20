from __future__ import annotations

from tests.cli.conftest import cli


def test_library_hadolint_invokes_docker(cli_runner, monkeypatch, fixtures_dir) -> None:
    monkeypatch.setattr("library.cli.hadolint.run_docker", lambda *_args, **_kwargs: 0)
    monkeypatch.setattr("library.cli.hadolint.fetch_dockerfile", lambda *_args, **_kwargs: "FROM scratch")
    result = cli_runner.invoke(cli, ["hadolint", str(fixtures_dir / "manifest.valid.yml")])
    assert result.exit_code == 0
