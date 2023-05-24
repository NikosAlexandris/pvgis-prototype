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
def test_query_location(
    path_to_data: pathlib.Path,
    filename: pathlib.Path,
    longitude: float,
    latitude: float,
    expected_output: float or List[float],
) -> None:
    """Test the query_location command.

    Args:
        path_to_data (pathlib.Path): The path to the test data as a pathlib.Path object.
        filename (pathlib.Path): The path to the netCDF file as a pathlib.Path object.
        longitude (float): The longitude value.
        latitude (float): The latitude value.
        expected_output (Any): The expected output of the command.

    Returns:
        None

    Raises:
        AssertionError: If the command exit code or output doesn't match the expected values.

    Example:
        >>> path_to_data = pathlib.Path('/path/to/data')
        >>> filename = pathlib.Path('test.nc')
        >>> longitude = 10.0
        >>> latitude = 20.0
        >>> expected_output = 30.0
        >>> test_query_location(path_to_data, filename, longitude, latitude, expected_output)

    Notes:
        - The test data should contain valid netCDF files for accurate testing.
        - Ensure that the provided longitude and latitude values correspond to locations within the test data.
    """
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
