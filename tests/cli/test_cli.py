from typer.testing import CliRunner
from pvgisprototype.cli.cli import app

runner = CliRunner()


def test_main_help():
    """Test if the CLI shows the main help message."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0  # Ensure the command ran successfully
    assert "PVGIS Command Line Interface" in result.output  # Check for expected output


def test_conventions_command():
    """Test the conventions command output."""
    result = runner.invoke(app, ["conventions"])
    assert result.exit_code == 0  # Ensure the command ran successfully
    # assert (
    #     "Conventions in PVGIS' solar positioning" in result.output
    # )  # Expected output check


def test_cite_command():
    """Test the cite command output."""
    result = runner.invoke(app, ["cite"])
    assert result.exit_code == 0  # Ensure the command ran successfully
    assert "PVGIS" in result.output  # Check for expected citation output


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


def test_performance_help():
    """Test the performance subcommand help."""
    result = runner.invoke(app, ["performance", "--help"])
    assert result.exit_code == 0
    assert (
        "performance" in result.output
    )  # Check that performance help text is available


def test_power_help():
    """Test the power subcommand help."""
    result = runner.invoke(app, ["power", "--help"])
    assert result.exit_code == 0
    assert "power" in result.output  # Check that power help text is available


def test_irradiance_help():
    """Test the irradiance subcommand help."""
    result = runner.invoke(app, ["irradiance", "--help"])
    assert result.exit_code == 0
    assert "irradiance" in result.output  # Check that irradiance help text is available


def test_series_help():
    """Test the series subcommand help."""
    result = runner.invoke(app, ["series", "--help"])
    assert result.exit_code == 0
    assert "series" in result.output  # Check that series help text is available


def test_time_help():
    """Test the time subcommand help."""
    result = runner.invoke(app, ["time", "--help"])
    assert result.exit_code == 0
    assert "time" in result.output  # Check that time help text is available
