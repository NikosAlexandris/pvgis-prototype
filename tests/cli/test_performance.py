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
