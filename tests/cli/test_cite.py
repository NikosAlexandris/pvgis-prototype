from rich import print
from typer.testing import CliRunner
from pvgisprototype.cli.cli import app

runner = CliRunner()


def test_cite():
    result = runner.invoke(app, ["cite"])
    assert result.exit_code == 0  # Ensure the command ran successfully
    assert "PVGIS" in result.output  # Check for a key part of the citation
    print(f"Result : {result.output}")  # Optional: Print the result for debugging

def test_cite_bibtex():
    result = runner.invoke(app, ["cite", "--bibtex"])
    assert result.exit_code == 0
    assert "@misc{pvgis" in result.output
    assert "title" in result.output
    assert "subtitle" in result.output
    assert "version" in result.output
    assert "author" in result.output
    assert "howpublished" in result.output
    assert "note" in result.output
    assert "institution" in result.output
    assert "address" in result.output
    assert "year" in result.output
    print(f"Result : {result.output}")  # Optional: Print the result for debugging
