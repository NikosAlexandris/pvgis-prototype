from rich import print
from typer.testing import CliRunner
from pvgisprototype.cli.cli import app

runner = CliRunner()


def test_performance():
    result = runner.invoke(app, ["performance"])
    assert result.exit_code == 0 
    print(f"Output : {result.output}")  # Optional: Print the result for debugging


def test_performance_introduction():
    result = runner.invoke(app, ["performance", "introduction"])
    print(f"Output : {result.output}")
    assert result.exit_code == 0 
    # assert "A short primer on the performance of a photovoltaic system" in result.output


def test_performance_broadband():
    result = runner.invoke(app, ["performance", "broadband"])
    print(f"Output : {result.output}")
    assert result.exit_code == 0 


def test_performance_broadband_multi():
    result = runner.invoke(app, ["performance", "broadband-multi"])
    print(f"Output : {result.output}")
    assert result.exit_code == 0 


def test_performance_spectral():
    result = runner.invoke(app, ["performance", "spectral"])
    print(f"Output : {result.output}")
    assert result.exit_code == 0 


def test_performance_spectral_factor():
    result = runner.invoke(app, ["performance", "spectral-factor"])
    print(f"Output : {result.output}")
    assert result.exit_code == 0 
