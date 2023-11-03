import pytest
from pvgisprototype.algorithms.pvlib.solar_altitude import calculate_solar_altitude_pvlib
from pvgisprototype import SolarAltitude
import numpy as np
# import matplotlib.pyplot as plt
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import ALTITUDE_NAME, RADIANS


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=RADIANS,
    longitude='longitude',
    latitude='latitude',
    timestamp='timestamp',
    timezone='timezone',
    altitude=ALTITUDE_NAME,
)

tolerances = [0.1]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, expected_solar_altitude, against_unit",
    test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_altitude_pvlib(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_altitude,
    against_unit,
    tolerance,
):
    calculated_solar_altitude = calculate_solar_altitude_pvlib(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
    )

    # Check types
    assert isinstance(calculated_solar_altitude, SolarAltitude)

    # Assert output
    assert pytest.approx(getattr(expected_solar_altitude, against_unit), tolerance) == getattr(
        calculated_solar_altitude, against_unit)

    # Assert range
    assert -np.pi/2 <= calculated_solar_altitude.radians <= np.pi/2




# def plot_solar_altitude_pvlib(
#     longitude,
#     latitude,
#     timestamps,
#     timezone,
#     angle_output_units,
#     expected_solar_altitude_series,
# ):
#     calculated_solar_altitude_series = calculate_solar_altitude_pvlib(
#         longitude=longitude,
#         latitude=latitude,
#         timestamps=timestamps,
#         timezone=timezone,
#         angle_output_units=angle_output_units,
#     )
#     figure, ax = plt.subplots()
#     ax.plot(
#         timestamps,
#         [altitude.value for altitude in expected_solar_altitude_series],
#         label="Expected",
#     )
#     ax.plot(
#         timestamps,
#         [altitude.value for altitude in calculated_solar_altitude_series],
#         label="Calculated",
#     )
#     ax.set_xlabel("Timestamps")
#     ax.set_ylabel(f"Solar Altitude ({angle_output_units})")
#     ax.legend()
#     plt.savefig(f'solar_altitude_series_pvlib.png')
#     return figure



# def get_expected_solar_altitudes(timestamps, longitude, latitude):
#     # Here, you can use a reference model or data to get the expected solar altitudes
#     # For demonstration purposes, I'm returning an array of SolarAltitude objects with dummy values
#     return [SolarAltitude(value=0.5, unit='radians') for _ in timestamps]


# @pytest.mark.mpl_image_compare
# def test_plot_solar_altitude_pvlib():
#     expected_solar_altitude_series = get_expected_solar_altitudes(timestamps_for_a_year, longitude, latitude)
#     return plot_solar_altitude_pvlib(
#         longitude,
#         latitude,
#         timestamps_for_a_year,
#         timezone,
#         angle_output_units,
#         expected_solar_altitude_series,
#     )
