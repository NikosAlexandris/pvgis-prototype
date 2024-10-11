import pytest
from typer.testing import CliRunner
from pvgisprototype.cli.cli import app


runner = CliRunner()
cases = [
    ("1.553", "47.325", "180", "37", "2005-01-01", "2005-01-02"),
    (" -0.1276", "51.5074", "180", "45", "2010-05-01", "2010-05-02"),
    ("13.4050", "52.5200", "200", "50", "2015-07-01", "2015-07-02"),
]


@pytest.mark.parametrize("longitude,latitude", [case[:2] for case in cases])
def test_position_overview_basic(longitude, latitude):
    result = runner.invoke(app, ["position", "overview", longitude, latitude])
    assert result.exit_code == 0, f"Failed: {result.output}"


@pytest.mark.parametrize("longitude,latitude,azimuth", [case[:3] for case in cases])
def test_position_overview_with_azimuth(longitude, latitude, azimuth):
    result = runner.invoke(app, ["position", "overview", longitude, latitude, azimuth])
    assert result.exit_code == 0, f"Failed: {result.output}"


@pytest.mark.parametrize(
    "longitude,latitude,azimuth,tilt", [case[:4] for case in cases]
)
def test_position_overview_with_azimuth_and_tilt(longitude, latitude, azimuth, tilt):
    result = runner.invoke(
        app, ["position", "overview", longitude, latitude, azimuth, tilt]
    )
    assert result.exit_code == 0, f"Failed: {result.output}"


@pytest.mark.parametrize(
    "longitude,latitude,azimuth,tilt", [case[:4] for case in cases]
)
def test_position_overview_with_time(longitude, latitude, azimuth, tilt):
    result = runner.invoke(
        app,
        [
            "position",
            "overview",
            longitude,
            latitude,
            azimuth,
            tilt,
            "2024-10-11 11:00:00",
        ],
    )
    assert result.exit_code == 0, f"Failed: {result.output}"


@pytest.mark.parametrize("longitude,latitude,azimuth,tilt,start_time,end_time", cases)
def test_position_overview_with_date_range(
    longitude, latitude, azimuth, tilt, start_time, end_time
):
    result = runner.invoke(
        app,
        [
            "position",
            "overview",
            longitude,
            latitude,
            azimuth,
            tilt,
            "--start-time",
            start_time,
            "--end-time",
            end_time,
        ],
    )
    assert result.exit_code == 0, f"Failed: {result.output}"


@pytest.mark.parametrize("longitude,latitude,azimuth,tilt,start_time,end_time", cases)
def test_position_overview_with_r_and_aou(
    longitude, latitude, azimuth, tilt, start_time, end_time
):
    result = runner.invoke(
        app,
        [
            "position",
            "overview",
            longitude,
            latitude,
            azimuth,
            tilt,
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


@pytest.mark.parametrize("longitude,latitude,azimuth,tilt,start_time,end_time", cases)
def test_position_overview_with_incidence(
    longitude, latitude, azimuth, tilt, start_time, end_time
):
    result = runner.invoke(
        app,
        [
            "position",
            "overview",
            longitude,
            latitude,
            azimuth,
            tilt,
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


@pytest.mark.parametrize("longitude,latitude,azimuth,tilt,start_time,end_time", cases)
def test_position_overview_with_uniplot(
    longitude, latitude, azimuth, tilt, start_time, end_time
):
    result = runner.invoke(
        app,
        [
            "position",
            "overview",
            longitude,
            latitude,
            azimuth,
            tilt,
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
