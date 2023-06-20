import pytest
from pvgisprototype.data_structures import SolarGeometryDayConstants
from pvgisprototype.solar_geometry_constants import calculate_solar_geometry_constants
from pvgisprototype.solar_geometry_constants_plot import plot_sunrise_sunset


@pytest.mark.parametrize(
    "latitude, local_solar_time, solar_declination",
    [
        (0, 12, 15),
        (15, 12, 15),
        (30, 12, 15),
        (45, 12, 15),
        (50, 12, 15),
        (65, 12, 15),
    ],
)
def test_solar_geometry_day_constants(latitude, local_solar_time, solar_declination):
    solar_constants = calculate_solar_geometry_constants(
            latitude=latitude,
            local_solar_time=local_solar_time,
            solar_declination=solar_declination,
            )
    assert isinstance(solar_constants, SolarGeometryDayConstants), " should be an instance of SolarGeometryDayConstants"
    # assert solar_constants.cosine_of_solar_declination == 0.5, "cosine_of_declination should be 0.5"
    # assert solar_constants.sine_of_solar_declination == 0.5, "sine_of_declination should be 0.5"
    assert solar_constants.lum_C11 is not None, "lum_C11 should not be None"
    assert solar_constants.lum_C13 is not None, "lum_C13 should not be None"
    # assert solar_constants.lum_C22 == 0.5, "lum_C22 should be 0.5"
    assert solar_constants.lum_C31 is not None, "lum_C31 should not be None"
    assert solar_constants.lum_C33 is not None, "lum_C33 should not be None"
    assert solar_constants.sunrise_time is not None, "sunrise_time should not be None"
    assert solar_constants.sunset_time is not None, "sunset_time should not be None"


@pytest.mark.mpl_image_compare
def test_solar_geometry_constants_plot_latitude_0():
    return plot_sunrise_sunset(latitude=0, start_day=1, end_day=365)

@pytest.mark.mpl_image_compare
def test_solar_geometry_constants_plot_latitude_45():
    return plot_sunrise_sunset(latitude=45.0, start_day=1, end_day=365)

@pytest.mark.mpl_image_compare
def test_solar_geometry_constants_plot_latitude_65():
    return plot_sunrise_sunset(latitude=65, start_day=1, end_day=365)

# The last one overwrites existing file!
