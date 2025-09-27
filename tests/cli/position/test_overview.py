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
from rich import print
import pytest
from ..conftest import ValidateTyperApplication
from pvgisprototype.cli.cli import app
from typer.testing import CliRunner


longitude_cases = ["1.553", " -0.1276", "13.4050"]
latitude_cases = ["47.325", "51.5074", "52.5200"]
surface_orientation_cases = ["180", "200"]
surface_tilt_cases = ["37", "45", "50"]
# start_time_cases = ["2005-01-01", "2010-05-01", "2015-07-01"]
start_time_cases = ["2005-01-01"]
# end_time_cases = ["2005-01-02", "2010-05-02", "2015-07-02"]
end_time_cases = ["2005-01-02"]
r_flag_cases = [None, "1", "2", "5"]
aou_flag_cases = [None, "degrees"]
i_flag_cases = [None, "-i"]


runner = CliRunner()


class TestCliApp(ValidateTyperApplication):

    @pytest.fixture
    def app(self):
        return app

    @staticmethod
    def build_test_id(param):
        """Dynamically builds a test ID based on the parameters and command structure."""
        # Retrieve the command object dynamically from Typer's app
        command = next(
            (
                cmd
                for cmd in ValidateTyperApplication.collect_commands(app)
                if cmd == ["position", "overview"]
            ),
            None,
        )
        if command:
            param_values = [
                param[0],
                param[1],
                param[2],
                param[3],
                f"--start-time {param[4]}",
                f"--end-time {param[5]}",
            ]
            # Add optional flags if they exist and format them correctly
            if param[6]:  # r_value
                param_values.extend(["-r", param[6]])
            if param[7]:  # aou_value
                param_values.extend(["-aou", param[7]])
            if param[8]:
                param_values.append(param[8])
            return ValidateTyperApplication.build_command_id(command, param_values)
        return f"Invalid Command : {command}"

    def test_position_overview_with_combinations(self, parameter_combination):
        (
            longitude,
            latitude,
            surface_orientation,
            surface_tilt,
            start_time,
            end_time,
            r_value,
            aou_value,
            i_flag,
        ) = parameter_combination

        command = [
            "position",
            "overview",
            longitude,
            latitude,
            surface_orientation,
            surface_tilt,
            "--start-time",
            start_time,
            "--end-time",
            end_time,
        ]
        if r_value:
            command.extend(["-r", r_value])

        if aou_value:
            command.extend(["-aou", aou_value])

        if i_flag:
            command.append(i_flag)

        result = runner.invoke(app, command)

        # Manually print the output and command for verification
        print(
                f"\n\n[bold]Command[/bold] : "
                f"{' '.join(command)}"
                f"\nOutput :"
                f"\n{result.output}"
              )

        # # Flush the captured output so it appears in the test results
        # captured = capsys.readouterr()
        # print(captured.out)

        self._check_result_exit_code(result)

    @pytest.fixture(
        params=ValidateTyperApplication.generate_parameter_combinations(
            [
                longitude_cases,
                latitude_cases,
                surface_orientation_cases,
                surface_tilt_cases,
                start_time_cases,
                end_time_cases,
                r_flag_cases,
                aou_flag_cases,
                i_flag_cases,
            ]
        ),
        ids=lambda param: TestCliApp.build_test_id(param),
    )
    def parameter_combination(self, request):
        """Fixture that provides combinations of parameters."""
        return request.param
