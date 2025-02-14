from typer.testing import CliRunner
from pvgisprototype.cli.cli import app

runner = CliRunner()


def test_completion_show_command():
    """Test the completion show command."""
    result = runner.invoke(app, ["completion", "show", "bash"])
    assert result.exit_code == 0  # Ensure the command ran successfully
    assert "bash" in result.output  # Check that bash completion is shown


def test_completion_install_command():
    """Test the completion install command."""
    result = runner.invoke(app, ["completion", "install", "bash"])
    assert result.exit_code == 0  # Ensure the command ran successfully
    assert "bash" in result.output  # Check that bash completion installation is shown
