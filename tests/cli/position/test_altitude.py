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


runner = CliRunner()
cases = [
    ("1.553", "47.325", "180", "37", "2005-01-01", "2005-01-02"),
    (" -0.1276", "51.5074", "180", "45", "2010-05-01", "2010-05-02"),
    ("13.4050", "52.5200", "200", "50", "2015-07-01", "2015-07-02"),
]


def test_position_altitude_help():
    result = runner.invoke(app, ["position", "altitude"])
    result_with_help = runner.invoke(app, ["position", "altitude", "--help"])
    assert result.exit_code == 0, f"Failed: {result.output}"
    assert result_with_help.exit_code == 0, f"Failed: {result.output}"
    assert result == result_with_help


@pytest.mark.parametrize("longitude,latitude", [case[:2] for case in cases])
def test_position_altitude_basic(longitude, latitude):
    result = runner.invoke(app, ["position", "altitude", longitude, latitude])
    assert result.exit_code == 0, f"Failed: {result.output}"


@pytest.mark.parametrize(
    "longitude,latitude", [case[:4] for case in cases]
)
def test_position_altitude_with_time(longitude, latitude):
    result = runner.invoke(
        app,
        [
            "position",
            "altitude",
            longitude,
            latitude,
            "2024-10-11 11:00:00",
        ],
    )
    assert result.exit_code == 0, f"Failed: {result.output}"


@pytest.mark.parametrize("longitude,latitude,start_time,end_time", cases)
def test_position_altitude_with_date_range(
    longitude, latitude, start_time, end_time
):
    result = runner.invoke(
        app,
        [
            "position",
            "altitude",
            longitude,
            latitude,
            "--start-time",
            start_time,
            "--end-time",
            end_time,
        ],
    )
    assert result.exit_code == 0, f"Failed: {result.output}"


@pytest.mark.parametrize("longitude,latitude,start_time,end_time", cases)
def test_position_altitude_with_r_and_aou(
    longitude, latitude, start_time, end_time
):
    result = runner.invoke(
        app,
        [
            "position",
            "altitude",
            longitude,
            latitude,
            "--start-time",
            start_time,
            "--end-time",
            end_time,
            "-r",
            "2",
            "-aou",
            "degrees",
        ],
    )
    assert result.exit_code == 0, f"Failed: {result.output}"


@pytest.mark.parametrize("longitude,latitude,start_time,end_time", cases)
def test_position_altitude_with_incidence(
    longitude, latitude, start_time, end_time
):
    result = runner.invoke(
        app,
        [
            "position",
            "altitude",
            longitude,
            latitude,
            "--start-time",
            start_time,
            "--end-time",
            end_time,
            "-r",
            "2",
            "-aou",
            "degrees",
            "-i",
        ],
    )
    assert result.exit_code == 0, f"Failed: {result.output}"


@pytest.mark.parametrize("longitude,latitude,start_time,end_time", cases)
def test_position_altitude_with_uniplot(
    longitude, latitude, start_time, end_time
):
    result = runner.invoke(
        app,
        [
            "position",
            "altitude",
            longitude,
            latitude,
            "--start-time",
            start_time,
            "--end-time",
            end_time,
            "-r",
            "2",
            "-aou",
            "degrees",
            "-i",
            "--uniplot",
        ],
    )
    assert result.exit_code == 0, f"Failed: {result.output}"
