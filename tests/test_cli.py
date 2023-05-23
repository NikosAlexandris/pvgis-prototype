import pathlib
import pytest
from typer.testing import CliRunner
from pvgisprototype.cli import app


runner = CliRunner()


@pytest.mark.parametrize(
        'filename, longitude, latitude, expected_output',
        [
            (pathlib.Path('data/era5_2m_temperature_2020_band_4381.nc'), 10, 10, 303.93634033203125),
            (pathlib.Path('data/era5_2m_temperature_2020_band_4381.nc'), 9.902056, 49.843, 298.97149658203125),
            ]
        )
def test_query_location(filename: pathlib.Path, longitude, latitude,
                        expected_output) -> None:
    # result = runner.invoke(app, [filename.as_posix(), 10, 10])
    result = runner.invoke(app, [filename.as_posix(), str(longitude), str(latitude)])
    assert result.exit_code == 0
    assert result.output.strip() == str(expected_output)


def test_create_minimal_netcdf(create_minimal_netcdf):
    minimal_netcdf = create_minimal_netcdf
    print(minimal_netcdf)
    pass
