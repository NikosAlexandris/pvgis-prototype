import pytest
from typer.testing import CliRunner
from pvgisprototype.cli.cli import app


runner = CliRunner()


class ValidateTyperaApplication:
    """Validate Typer app"""

    @staticmethod
    def _check_result_exit_code(result):
        """Assert that the result's exit code is 0 which means that the invoked
        command ran successfully.
        """
        assert result.exit_code == 0

    @pytest.fixture
    def app(self):
        return app

    @pytest.fixture
    def invoke_app_command(self, app, arguments):
        """Run the Typer app with the given arguments.
        See also : CliRunner.invoke?
        """
        return runner.invoke(app, arguments)

    def test_result_exit_code(self, invoke_app_command):
        """Execure an assertion function which is defined as static method of
        the class
        """
        self._check_result_exit_code(invoke_app_command)
