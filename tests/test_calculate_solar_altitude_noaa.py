import pytest
# from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_time_series_noaa
from pvgisprototype import SolarAltitude
import numpy as np
# import matplotlib.pyplot as plt
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import ALTITUDE_NAME, DEGREES
from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_noaa


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=DEGREES,
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
def test_calculate_solar_altitude_noaa(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_altitude,
    against_unit,
    tolerance,
):
    calculated_solar_altitude = calculate_solar_altitude_noaa(
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





# longitude=0.5
# latitude=0.5
# timezone=ZoneInfo('UTC')
# apply_atmospheric_refraction=True
# time_output_units='minutes'
# angle_output_units='radians'


# # Set a seed to ensure agreement of plots between tests!
# random.seed(43) # Comment to really pick a random year
# random_year = random.randint(2005, 2023)
# timestamps_for_a_year = generate_timestamps_for_a_year(year=random_year)
# test_cases = [
#     (
#         Longitude(value=0.5, unit='radians'),
#         Latitude(value=0.5, unit='radians'),
#         [datetime(2023, 8, 25, 0, 0), datetime(2023, 8, 26, 0, 0)],
#         ZoneInfo('UTC'),
#         False,
#         'minutes',
#         'radians',
#     ),
#     # Add more test cases here
# ]


# @pytest.mark.parametrize(
#     "longitude, latitude, timestamps, timezone, apply_atmospheric_refraction, time_output_units, angle_output_units",
#     test_cases,
# )
# def test_calculate_solar_altitude_time_series_noaa(
#     longitude,
#     latitude,
#     timestamps,
#     timezone,
#     apply_atmospheric_refraction,
#     time_output_units,
#     angle_output_units,
# ):
#     """ """
#     calculated_altitude_series = calculate_solar_altitude_time_series_noaa(
#         longitude=longitude,
#         latitude=latitude,
#         timestamps=timestamps,
#         timezone=timezone,
#         apply_atmospheric_refraction=apply_atmospheric_refraction,
#         time_output_units=time_output_units,
#         angle_output_units=angle_output_units,
#     )
#     assert np.ndarray == type(calculated_altitude_series)
#     assert len(timestamps) == len(calculated_altitude_series)
#     assert all(SolarAltitude == type(altitude) for altitude in calculated_altitude_series)
#     assert all((-np.pi/2 <= altitude.value <= np.pi/2) for altitude in calculated_altitude_series)
#     assert all(angle_output_units == altitude.unit for altitude in calculated_altitude_series)


# def plot_solar_altitude_noaa(
#     longitude,
#     latitude,
#     timestamps,
#     timezone,
#     apply_atmospheric_refraction,
#     time_output_units,
#     angle_output_units,
#     expected_solar_altitude_series,
# ):
#     calculated_solar_altitude_series = calculate_solar_altitude_time_series_noaa(
#         longitude=longitude,
#         latitude=latitude,
#         timestamps=timestamps,
#         timezone=timezone,
#         apply_atmospheric_refraction=apply_atmospheric_refraction,
#         time_output_units=time_output_units,
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
#     plt.savefig(f'solar_altitude_series_noaa.png')
#     return figure



# def get_expected_solar_altitudes(timestamps, longitude, latitude):
#     # Here, you can use a reference model or data to get the expected solar altitudes
#     # For demonstration purposes, I'm returning an array of SolarAltitude objects with dummy values
#     return [SolarAltitude(value=0.5, unit='radians') for _ in timestamps]


# @pytest.mark.mpl_image_compare
# # def test_plot_solar_altitude_noaa(longitude, latitude, timestamps, timezone, apply_atmospheric_refraction, time_output_units, angle_output_units, expected_solar_altitude_series):
# def test_plot_solar_altitude_noaa():
#     expected_solar_altitude_series = get_expected_solar_altitudes(timestamps_for_a_year, longitude, latitude)
#     return plot_solar_altitude_noaa(
#         longitude,
#         latitude,
#         timestamps_for_a_year,
#         timezone,
#         apply_atmospheric_refraction,
#         time_output_units,
#         angle_output_units,
#         expected_solar_altitude_series,
#     )
