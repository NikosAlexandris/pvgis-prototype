import pytest
from pvgisprototype.api.geometry.overview import calculate_solar_geometry_overview
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.algorithms.pvgis.solar_geometry import calculate_solar_position_pvgis
from pvgisprototype.validation.data_structures import SolarGeometryDayConstants
from pvgisprototype.validation.data_structures import SolarGeometryDayVariables
from pvgisprototype.plot.plot_solar_position import plot_daily_solar_position
from pvgisprototype.plot.plot_solar_position import plot_daily_solar_position_models
from pvgisprototype.plot.plot_solar_position import plot_daily_solar_position_scatter
from pvgisprototype.plot.plot_solar_position import plot_daily_solar_altitude
from pvgisprototype.plot.plot_solar_position import plot_daily_solar_azimuth
from pvgisprototype.plot.plot_solar_position import plot_yearly_solar_position
from pvgisprototype.plot.plot_solar_position import plot_analemma
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pvgisprototype.constants import (
    POSITION_ALGORITHM_NAME,
    ALTITUDE_NAME,
    DECLINATION_NAME,
    ZENITH_NAME,
    AZIMUTH_NAME,
    INCIDENCE_NAME,
    UNITS_NAME,
)


models = [
        SolarPositionModels.noaa,
        SolarPositionModels.pysolar,
        SolarPositionModels.pvis,
        # SolarPositionModels.pvgis,
        SolarPositionModels.suncalc,
        SolarPositionModels.skyfield,
]
dates = [
        datetime.now().replace(tzinfo=timezone.utc, year=year) for year in range(2000, 2010)
]
valid_coordinates = [
    (0.0, 0.0),  # zero coordinates
    (-180.0, -90.0),  # minimum valid longitudes and latitudes
    (180.0, 90.0),  # maximum valid longitudes and latitudes
]
invalid_coordinates = [
    (-181.0, 0.0),  # invalid longitude
    (181.0, 0.0),  # invalid longitude
    (0.0, -91.0),  # invalid latitude
    (0.0, 91.0),  # invalid latitude
]


@pytest.mark.parametrize("model", models)
def test_calculate_solar_position(model):
    longitude = 0.0
    latitude = 0.0
    utc_zoneinfo = ZoneInfo('UTC')
    timestamp = datetime.now(utc_zoneinfo)
    timezone = utc_zoneinfo
    # handling the 'pvgis' model
    if model == calculate_solar_position_pvgis:
        solar_geometry_day_constants = SolarGeometryDayConstants(
            latitude=45.0,
            solar_declination=23.45,
            cosine_of_solar_declination=0.917,
            sine_of_solar_declination=0.398,
            lum_C11=0.123,
            lum_C13=0.456,
            lum_C22=0.789,
            lum_C31=0.987,
            lum_C33=0.654,
            sunrise_time=6.0,
            sunset_time=18.0,
        )
        year = 2023
        hour_of_year = 100
        solar_altitude, solar_azimuth, sun_azimuth = calculate_solar_position_pvgis(
            solar_geometry_day_constants=solar_geometry_day_constants,
            year=year,
            hour_of_year=hour_of_year
        )

        # Check types
        assert isinstance(solar_altitude, float)
        assert isinstance(solar_azimuth, float)
        assert isinstance(sun_azimuth, float)

        # Assert output
        # assert solar_altitude == expected_solar_altitude
        # assert solar_azimuth == expected_solar_azimuth
        # assert sun_azimuth == expected_sun_azimuth

    else:
        solar_position = calculate_solar_geometry_overview(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            solar_position_models=[model],
        )
        print(f' Result : {solar_position}')
        for model_result in solar_position:
            model_name = model_result.get(POSITION_ALGORITHM_NAME, None)
            declination = model_result.get(DECLINATION_NAME, None)
            if declination is not None:
                assert isinstance(declination, float)
            altitude = model_result.get(ALTITUDE_NAME, None)
            if altitude is not None:
                assert isinstance(altitude, float)
            azimuth = model_result.get(AZIMUTH_NAME, None)
            if azimuth is not None:
                assert isinstance(azimuth, float)
            zenith = model_result.get(ZENITH_NAME, None)
            if zenith is not None:
                assert isinstance(zenith, float)
            incidence = model_result.get(INCIDENCE_NAME, None)
            if incidence is not None:
                assert isinstance(incidence, float)
            units = model_result.get(UNITS_NAME, None)
            if units is not None:
                assert isinstance(units, str)


# @pytest.mark.parametrize("longitude, latitude", valid_coordinates)
# @pytest.mark.parametrize("timestamp", dates)
# @pytest.mark.parametrize("model", models)
# def test_calculate_solar_position_valid_coordinates(longitude, latitude, timestamp, model):
#     # altitude_suncalc, azimuth_suncalc = calculate_solar_position(longitude, latitude, timestamp, SolarPositionModels.suncalc)
#     # altitude_suncalc, azimuth_suncalc = calculate_solar_position(longitude, latitude, timestamp, model)
#     altitude, azimuth = calculate_solar_position(longitude, latitude, timestamp, model)
#     # assert isinstance(altitude_suncalc, float)
#     # assert isinstance(azimuth_suncalc, float)
#     assert isinstance(altitude, float)
#     assert isinstance(azimuth, float)


# @pytest.mark.parametrize("longitude, latitude", invalid_coordinates)
# @pytest.mark.parametrize("timestamp", dates)
# def test_calculate_solar_position_invalid_coordinates(longitude, latitude, timestamp):
#     with pytest.raises(ValueError):
#         calculate_solar_position(longitude, latitude, timestamp, SolarPositionModels.suncalc)
#         # assert False, f"Expected ValueError for invalid coordinates ({longitude}, {latitude}), but got ({altitude_suncalc}, {azimuth_suncalc})"


@pytest.mark.parametrize("model", models)
@pytest.mark.mpl_image_compare
def test_plot_daily_solar_altitude(model):
    longitude = 0.0
    latitude = 0.0
    day = datetime.now()
    
    # handling the 'pvgis' model
    if model == calculate_solar_position_pvgis:
        # Create SolarGeometryDayConstants object
        solar_geometry_day_constants = SolarGeometryDayConstants(
            latitude=45.0,
            solar_declination=23.45,
            cosine_of_solar_declination=0.917,
            sine_of_solar_declination=0.398,
            lum_C11=0.123,
            lum_C13=0.456,
            lum_C22=0.789,
            lum_C31=0.987,
            lum_C33=0.654,
            sunrise_time=6.0,
            sunset_time=18.0,
        )
        year = 2023
        hour_of_year = 100

        try:
            plot_daily_solar_altitude(
                    longitude=longitude,
                    latitude=latitude,
                    day=day,
                    model=model,
                    solar_geometry_day_constants=solar_geometry_day_constants,
                    year=year,
                    hour_of_year=hour_of_year,
                    )
        except Exception as e:
            assert False, f"plot_daily_solar_position raised an error: {e}"
    else:
        try:
            plot_daily_solar_altitude(longitude, latitude, day, model)
        except Exception as e:
            assert False, f"plot_daily_solar_position raised an error: {e}"


@pytest.mark.parametrize("model", models)
@pytest.mark.mpl_image_compare
def test_plot_daily_solar_azimuth(model):
    longitude = 0.0
    latitude = 0.0
    day = datetime.now()
    try:
        plot_daily_solar_azimuth(longitude, latitude, day, model)
    except Exception as e:
        assert False, f"plot_daily_solar_position raised an error: {e}"


@pytest.mark.parametrize("model", models)
@pytest.mark.mpl_image_compare
def test_plot_daily_solar_position(model):
    longitude = 0.0
    latitude = 0.0
    day = datetime.now()
    try:
        plot_daily_solar_position(longitude, latitude, day, model)
    except Exception as e:
        assert False, f"plot_daily_solar_position raised an error: {e}"


@pytest.mark.parametrize("model", models)
@pytest.mark.mpl_image_compare
def test_plot_daily_solar_position_models(model):
    longitude = 0.0
    latitude = 0.0
    day = datetime.now()
    try:
        plot_daily_solar_position_models(longitude, latitude, day, model)
    except Exception as e:
        assert False, f"plot_daily_solar_position raised an error: {e}"


@pytest.mark.parametrize("model", models)
@pytest.mark.mpl_image_compare
def test_plot_daily_solar_position_scatter(model):
    longitude = 0.0
    latitude = 0.0
    day = datetime.now()
    try:
        plot_daily_solar_position_scatter(longitude, latitude, day, model)
    except Exception as e:
        assert False, f"plot_daily_solar_position raised an error: {e}"


@pytest.mark.mpl_image_compare
def test_plot_yearly_solar_position():
    longitude = 0.0
    latitude = 0.0
    year = datetime.today().year
    model = SolarPositionModels.suncalc
    try:
        plot_yearly_solar_position(longitude, latitude, year, model)
    except Exception as e:
        assert False, f"plot_yearly_solar_position raised an error: {e}"


# @pytest.mark.mpl_image_compare
# def test_analemma_plot():
#     longitude = 0.0
#     latitude = 0.0
#     year = datetime.now().year
#     model = SolarPositionModels.suncalc
#     try:
#         return plot_analemma(longitude, latitude, year, model)
#     except Exception as e:
#         assert False, f"plot_analemma raised an error: {e}"
