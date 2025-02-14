from typer.testing import CliRunner
from pvgisprototype.cli.series.series import app

runner = CliRunner()


def test_series_introduction():
    """Test if the series introduction command works."""
    result = runner.invoke(app, ["series", "introduction"])
    assert result.exit_code == 0
    assert "Introduction on the [cyan]series[/cyan]" in result.output


def test_select_command():
    """Test if the select command works with required options."""
    result = runner.invoke(
        app,
        [
            "series",
            "select",
            "path/to/series.nc",
            "--longitude",
            "10.5",
            "--latitude",
            "20.2",
        ],
    )
    assert result.exit_code == 0
    assert "Selected series" in result.output  # Expected output or behavior


def test_select_sarah_command():
    """Test if the select-sarah command works with required options."""
    result = runner.invoke(
        app,
        [
            "series",
            "select-sarah",
            "path/to/series.nc",
            "--longitude",
            "10.5",
            "--latitude",
            "20.2",
        ],
    )
    assert result.exit_code == 0
    assert "SARAH time series" in result.output  # Replace with actual expected behavior


def test_select_fast_command():
    """Test if the select-fast command works."""
    result = runner.invoke(
        app,
        [
            "series",
            "select-fast",
            "path/to/series.nc",
            "--longitude",
            "10.5",
            "--latitude",
            "20.2",
        ],
    )
    assert result.exit_code == 0
    assert "Done.-" in result.output  # Ensure the command ran successfully


def test_plot_command():
    """Test if the plot command works."""
    result = runner.invoke(
        app,
        [
            "series",
            "plot",
            "path/to/series.nc",
            "--longitude",
            "10.5",
            "--latitude",
            "20.2",
        ],
    )
    assert result.exit_code == 0
    assert (
        "Plot time series" in result.output
    )  # Ensure the plot command is invoked correctly


def test_uniplot_command():
    """Test if the uniplot command works."""
    result = runner.invoke(
        app,
        [
            "series",
            "uniplot",
            "path/to/series.nc",
            "--longitude",
            "10.5",
            "--latitude",
            "20.2",
        ],
    )
    assert result.exit_code == 0
    assert "Plot time series in the terminal" in result.output


def test_resample_command():
    """Test if the resample command works."""
    result = runner.invoke(app, ["series", "resample"])
    assert result.exit_code == 0
    assert "Group-by of time series" in result.output


def test_invalid_command():
    """Test if an invalid command gives an error."""
    result = runner.invoke(app, ["series", "invalid-command"])
    assert result.exit_code != 0
    assert "No such command" in result.output
