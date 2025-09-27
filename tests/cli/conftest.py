#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import pytest
from typer.testing import CliRunner
from pvgisprototype.cli.cli import app
from itertools import product


runner = CliRunner()


class ValidateTyperApplication:
    """Validate Typer app"""

    @staticmethod
    def _check_result_exit_code(result):
        """Assert that the result's exit code is 0 which means that the invoked command ran successfully."""
        assert result.exit_code == 0, (
            f"Command failed with exit code {result.exit_code}.\n"
            f"Command output:\n{result.output}"
        )

    @pytest.fixture
    def app(self):
        return app

    @pytest.fixture
    def invoke_app_command(self, app, arguments):
        """Run the Typer app with the given arguments. See also : CliRunner.invoke?"""
        return runner.invoke(app, arguments)

    def test_result_exit_code(self, invoke_app_command):
        """Execute an assertion function which is defined as a static method of the class"""
        self._check_result_exit_code(invoke_app_command)

    @staticmethod
    def collect_commands(app):
        """Collect all commands and subcommands from the Typer app."""
        commands = []
        for group in app.registered_groups:
            # Collect main command
            commands.append([group.name])

            # Collect subcommands
            if hasattr(group.typer_instance, 'registered_commands'):
                for command in group.typer_instance.registered_commands:
                    if command.name:
                        commands.append([group.name, command.name])

        return commands

    # @staticmethod
    # def collect_commands(app: Typer):
    #     """Collect all commands and subcommands from the Typer app."""
    #     commands = []
    #     # Collect top-level commands and groups
    #     for command_name, command in app.registered_commands.items():
    #         commands.append((command_name, command))
    #         # If this command is a group, collect its subcommands
    #         if isinstance(command.callback, Typer):
    #             subcommands = command.callback.registered_commands.items()
    #             for subcommand_name, subcommand in subcommands:
    #                 full_command_name = f"{command_name} {subcommand_name}"
    #                 commands.append((full_command_name, subcommand))
    #     return commands

    @staticmethod
    def collect_parameters(command_info):
        """Collect parameters dynamically from a Typer command."""
        parameters = []
        # for param in command.callback.__signature__.parameters.values():
        #     if param.default == param.empty:
        #         parameters.append(f"<{param.name}>")  # Required argument
        #     else:
        #         parameters.append(f"--{param.name}")  # Optional argument
        # return parameters
        for param in command_info.params:
            if param.param_type_name == "Argument":
                parameters.append(f"<{param.name}>")
            elif param.param_type_name == "Option":
                parameters.append(f"--{param.name}")
        return parameters

    @staticmethod
    def build_command_id(command, param_values):
        """Builds a CLI command ID dynamically for manual testing."""
        command_name = " ".join(command)
        param_string = " ".join(param_values)

        command_str = f"python -m pvgisprototype.cli.cli {command_name} {param_string}"
        return command_str

    @staticmethod
    def generate_parameter_combinations(params):
        """Generate combinations of parameters based on provided parameter lists."""
        return list(product(*params))
