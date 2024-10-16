import pytest
from typer.testing import CliRunner
from .conftest import ValidateTyperApplication
from pvgisprototype.cli.cli import app

runner = CliRunner()
arguments = (["cite"], ["cite", "--help"], ["cite", "--bibtex"])


class TestCliApp(ValidateTyperApplication):

    # override default app !
    @pytest.fixture
    def app(self):
        return app

    @pytest.fixture(params=arguments)  # , ids=something)
    def arguments(self, request):
        return request.param
