from typer.testing import CliRunner
from pvgisprototype.cli.cli import app

runner = CliRunner()


def test_conventions():
    """Test the conventions command output."""
    result = runner.invoke(app, ["conventions"])
    assert result.exit_code == 0  # Ensure the command ran successfully
    assert "Conventions" in result.output  # Ensure some key output is present
    print(f"Output : {result.output}")  # Optional: Print the result for debugging
