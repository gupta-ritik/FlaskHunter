from typer.testing import CliRunner

from flakehunter import __version__
from flakehunter.cli import app


def test_version() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout == f"flakehunter {__version__}\n"
