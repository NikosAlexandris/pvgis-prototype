import pytest
from pvgisprototype.api.data_structures import SolarGeometryDayConstants
from pvgisprototype.algorithms.pvgis.solar_geometry import calculate_solar_geometry_pvgis_constants
from pvgisprototype.plot.plot_solar_geometry_pvgis import plot_sunrise_sunset
import datetime


@pytest.mark.parametrize(
    "longitude, latitude, local_solar_time, solar_declination",
    [
        (0, 0, 12, 15),
        (0, 15, 12, 15),
        (0, 30, 12, 15),
        (0, 45, 12, 15),
        (0, 50, 12, 15),
        (0, 65, 12, 15),
    ],
)
def test_solar_geometry_pvgis_day_constants(longitude, latitude, local_solar_time, solar_declination):
    solar_constants = calculate_solar_geometry_pvgis_constants(
            longitude=longitude,
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

location_and_timestamps = [
        (0, 0, datetime.datetime(2023, 1, 1), datetime.datetime(2024, 1, 1)),
        (0, 30, datetime.datetime(2023, 1, 1), datetime.datetime(2024, 1, 1)),
        (0, 45, datetime.datetime(2023, 1, 1), datetime.datetime(2024, 1, 1)),
        (0, 60, datetime.datetime(2023, 1, 1), datetime.datetime(2024, 1, 1)),
    ]
@pytest.mark.parametrize("longitude, latitude, start_date, end_date", location_and_timestamps)
@pytest.mark.mpl_image_compare
def test_solar_geometry_pvgis_constants_plot_latitude(
        longitude: float,
        latitude: float,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        ):
    return plot_sunrise_sunset(longitude, latitude, start_date, end_date)
