import pytest
# from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa
from pvgisprototype import SolarAzimuth
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import AZIMUTH_NAME, DEGREES
from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_noaa


test_cases_data = read_noaa_spreadsheet(
    './tests/cases/noaa.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=DEGREES,
    longitude='longitude',
    latitude='latitude',
    timestamp='timestamp',
    timezone='timezone',
    altitude=AZIMUTH_NAME,
)

tolerances = [0.1]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, expected_solar_azimuth, against_unit",
    test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_azimuth_noaa(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_azimuth,
    against_unit,
    tolerance,
):
    calculated_solar_azimuth = calculate_solar_azimuth_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
    )

    # Check types
    assert isinstance(calculated_solar_azimuth, SolarAzimuth)

    # Assert output
    assert pytest.approx(
        getattr(expected_solar_azimuth, against_unit), tolerance) == getattr(
            calculated_solar_azimuth, against_unit)

    # Assert range





# test_cases_azimuth = [
#     (
#         Longitude(value=0.5, unit='radians'),
#         Latitude(value=0.5, unit='radians'),
#         [datetime(2023, 8, 25, 0, 0), datetime(2023, 8, 26, 0, 0)],
#         ZoneInfo('UTC'),
#         False,
#         'minutes',
#         'radians',
#         'radians',
#     ),
#     # add more test cases
# ]


# @pytest.mark.parametrize(
#     'longitude, latitude, timestamps, timezone, apply_atmospheric_refraction, time_output_units, angle_units, angle_output_units',
#     test_cases_azimuth,
# )
# def test_calculate_solar_azimuth_time_series_noaa(
#     longitude,
#     latitude,
#     timestamps,
#     timezone,
#     apply_atmospheric_refraction,
#     time_output_units,
#     angle_units,
#     angle_output_units,
# ):
#     calculated_azimuth_series = calculate_solar_azimuth_time_series_noaa(
#         longitude=longitude,
#         latitude=latitude,
#         timestamps=timestamps,
#         timezone=timezone,
#         apply_atmospheric_refraction=apply_atmospheric_refraction,
#         time_output_units=time_output_units,
#         angle_units=angle_units,
#         angle_output_units=angle_output_units,
#     )
#     assert np.ndarray == type(calculated_azimuth_series)
#     assert len(timestamps) == len(calculated_azimuth_series)
#     assert all(SolarAzimuth == type(azimuth) for azimuth in calculated_azimuth_series)
#     assert all((0 <= azimuth.value <= 2*np.pi) for azimuth in calculated_azimuth_series)
#     assert all(angle_output_units == azimuth.unit for azimuth in calculated_azimuth_series)


# def plot_solar_azimuth_noaa(
#     longitude,
#     latitude,
#     timestamps,
#     timezone,
#     apply_atmospheric_refraction,
#     time_output_units,
#     angle_units,
#     angle_output_units,
#     expected_solar_azimuth_series,
# ):
#     calculated_solar_azimuth_series = calculate_solar_azimuth_time_series_noaa(
#         longitude=longitude,
#         latitude=latitude,
#         timestamps=timestamps,
#         timezone=timezone,
#         apply_atmospheric_refraction=apply_atmospheric_refraction,
#         time_output_units=time_output_units,
#         angle_units=angle_units,
#         angle_output_units=angle_output_units,
#     )
#     figure, ax = plt.subplots()
#     ax.plot(
#         timestamps,
#         [azimuth.value for azimuth in expected_solar_azimuth_series],
#         label="Expected",
#     )
#     ax.plot(
#         timestamps,
#         [azimuth.value for azimuth in calculated_solar_azimuth_series],
#         label="Calculated",
#     )
#     ax.set_xlabel("Timestamps")
#     ax.set_ylabel(f"Solar Azimuth ({angle_output_units})")
#     ax.legend()
#     plt.savefig(f'solar_azimuth_series_noaa.png')
#     return figure
