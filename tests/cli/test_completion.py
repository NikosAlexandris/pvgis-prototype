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
