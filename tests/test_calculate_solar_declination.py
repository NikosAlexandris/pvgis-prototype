from devtools import debug
import pytest
# import matplotlib.pyplot as plt
from pvgisprototype.api.geometry.solar_declination import calculate_solar_declination
# from pvgisprototype.plot.plot_solar_declination import plot_solar_declination
# from pvgisprototype.plot.plot_solar_declination import plot_solar_declination_five_years
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import DECLINATION_NAME, DEGREES


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=DEGREES,
    timestamp='timestamp',
    timezone='timezone',
    declination=DECLINATION_NAME,
)

tolerances = [0.1]      # 1, 0.5, 

declination_models = [[
    SolarDeclinationModels.hargreaves,
    SolarDeclinationModels.noaa,
    SolarDeclinationModels.pvis,
    SolarDeclinationModels.pvlib,
]]

@pytest.mark.parametrize(
    "timestamp, timezone, expected_declination, against_unit", test_cases,
)
@pytest.mark.parametrize('declination_models', declination_models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_declination(
    timestamp,
    timezone,
    expected_declination,
    against_unit,
    declination_models,
    tolerance,
):
    calculated = calculate_solar_declination(
        timestamp = timestamp,
        timezone = timezone,
        angle_output_units = against_unit,
        declination_models = declination_models,
    )

    # Check types
    assert isinstance(calculated, list)
    assert len(calculated) == len(declination_models)

    for idx in range(len(declination_models)):
        assert isinstance(calculated[idx], dict)
        assert DECLINATION_NAME not in calculated[idx] or isinstance(calculated[idx][DECLINATION_NAME], float)

        # Assert output
        assert DECLINATION_NAME not in calculated[idx] or pytest.approx(
            getattr(expected_declination, against_unit), tolerance) == calculated[idx][DECLINATION_NAME]








# """
# The solar declination is the angle between
# the rays of the Sun and the plane of the Earth's equator.
# Its value varies between -23.44° and +23.44° (approximately)
# throughout the year due to the tilt of the Earth's axis.

# Verify expected solar declination angles for the listed days
# based on a given formula or lookup table ?
# """


# test_cases = [
#     (datetime.datetime(2023, 1, 1), -23.38044, DEGREES),  # Around vernal equinox
#     (datetime.datetime(2023, 3, 20), 0, DEGREES),  # Around vernal equinox
#     (datetime.datetime(2023, 3, 21), 0, DEGREES),  # Around vernal equinox
#     (datetime.datetime(2023, 6, 20), 23.44, DEGREES),  # Around summer solstice
#     (datetime.datetime(2023, 6, 21), 23.44, DEGREES),  # Around summer solstice
#     (datetime.datetime(2023, 9, 22), 0, DEGREES),  # Around autumnal equinox
#     (datetime.datetime(2023, 9, 23), 0, DEGREES),  # Around autumnal equinox
#     (datetime.datetime(2023, 12, 21), -23.44, DEGREES),  # Around winter solstice
#     (datetime.datetime(2023, 12, 22), -23.44, DEGREES),  # Around winter solstice
#     # (datetime.datetime(2023, 12, 30), -16.428456, DEGREES),  # Around winter solstice
#     (datetime.datetime(2023, 12, 30), -23.44, DEGREES),  # Around winter solstice
# ]
# models = [
#     SolarDeclinationModels.pvis,
#     SolarDeclinationModels.noaa,
# ]
# tolerances = [1, 0.1]
# @pytest.mark.parametrize('timestamp, expected_value, expected_unit', test_cases)
# @pytest.mark.parametrize('model', models)
# @pytest.mark.parametrize('tolerance', tolerances)
# def test_calculate_solar_declination(
#     timestamp: datetime.datetime,
#     expected_value: float,
#     expected_unit: str,
#     model: SolarDeclinationModels,
#     tolerance: float,
# ):
#     calculated = calculate_solar_declination(
#         timestamp=timestamp,
#         timezone=None,
#         models=[model],  # pass as a list!
#         angle_output_units=DEGREES,
#     )
#     model_result = calculated[0]
#     model_name = model_result.get("Model", "")
#     calculated_value = model_result.get(DECLINATION_NAME, "NA")
#     calculated_unit = model_result.get(UNITS_NAME, "")
#     assert pytest.approx(expected_value, tolerance) == calculated_value
#     assert expected_unit == calculated_unit


# # Set a seed to ensure agreement of plots between tests!
# random.seed(43) # Comment to really pick a random year
# random_year = random.randint(2005, 2023)
# @pytest.mark.mpl_image_compare  # instructs use of a baseline image
# def test_plot_solar_declination():
#     assert plot_solar_declination(
#             # start_date,
#             # end_date,
#             year=random_year,
#             title=f'Solar Declination {random_year}',
#             output_units=DEGREES,
#             )


# random_year = random.randint(2005, 2023)
# @pytest.mark.mpl_image_compare  # instructs use of a baseline image
# def test_plot_solar_declination():
#     assert plot_solar_declination(
#             # start_date,
#             # end_date,
#             year=random_year,
#             title=f'Solar Declination {random_year}',
#             output_units='radians',
#             )


# random_year = random.randint(2005, 2023)
# @pytest.mark.mpl_image_compare
# def test_plot_solar_declination_five_years():
#     assert plot_solar_declination_five_years(
#             start_year=random_year,
#             title="Five-Year Variation of Solar Declination",
#             output_units='radians',
#             )
