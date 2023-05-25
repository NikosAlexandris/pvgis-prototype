import pathlib
import pytest
from typer.testing import CliRunner
from pvgisprototype.cli import app
from .conftest import EU_GEOMETRIC_CENTER_POST_BREXIT
from .test_expected_output import EU_CENTER_LOCATION_VALUES


runner = CliRunner()


@pytest.mark.parametrize(
        'filename, longitude, latitude, expected_output',
        [
            (pathlib.Path('tests/data/era5_2m_temperature_2020_band_4381.nc'),
             EU_GEOMETRIC_CENTER_POST_BREXIT[0],
             EU_GEOMETRIC_CENTER_POST_BREXIT[1],
             298.97149658203125),
            (pathlib.Path('tests/data/minimal_netcdf.nc'),
             EU_GEOMETRIC_CENTER_POST_BREXIT[0],
             EU_GEOMETRIC_CENTER_POST_BREXIT[1],
             EU_CENTER_LOCATION_VALUES),
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
    result = runner.invoke(app, ['query-location', str(filename), str(longitude), str(latitude)])
    output = result.output.strip()

    # Check if the output is a single value
    if isinstance(expected_output, float):
        # Parse the output as a float
        assert float(output) == pytest.approx(expected_output, rel=1e-6)
    # Check if the output is a list of values
    elif isinstance(expected_output, list):
        # Split the output by commas and convert each value to a float
        output_list = [float(value) for value in output[1:-1].split(',')]
        # Compare the output list with the expected output list
        assert output_list == pytest.approx(expected_output, rel=1e-6)
    else:
        raise ValueError("Invalid expected output format")

    assert result.exit_code == 0



def test_create_minimal_netcdf(create_minimal_netcdf):
    minimal_netcdf = create_minimal_netcdf
    print(minimal_netcdf)
    pass
