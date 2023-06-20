import pytest
from pvgisprototype.solar_position import calculate_solar_position
from pvgisprototype.solar_position import SolarPositionModels
from pvgisprototype.solar_position_plot import plot_daily_solar_position
from pvgisprototype.solar_position_plot import plot_daily_solar_position_scatter
from pvgisprototype.solar_position_plot import plot_daily_solar_altitude
from pvgisprototype.solar_position_plot import plot_daily_solar_azimuth
from pvgisprototype.solar_position_plot import plot_yearly_solar_position
from pvgisprototype.solar_position_plot import plot_analemma
from datetime import datetime, timezone


models = [
        SolarPositionModels.suncalc,
        SolarPositionModels.pysolar,
        SolarPositionModels.pvgis,
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
    timestamp = datetime.now().replace(tzinfo=timezone.utc)
    altitude, azimuth = calculate_solar_position(longitude, latitude, timestamp, model)
    assert isinstance(altitude, float)
    assert isinstance(azimuth, float)


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
    try:
        plot_daily_solar_altitude(longitude, latitude, day, model)
    except Exception as e:
        assert False, f"plot_daily_solar_position raised an error: {e}"


def test_plot_daily_solar_position():
    longitude = 0.0
    latitude = 0.0
    day = datetime.now()
    model = SolarPositionModels.suncalc
    try:
        plot_daily_solar_position(longitude, latitude, day, model)
    except Exception as e:
        assert False, f"plot_daily_solar_position raised an error: {e}"

def test_plot_yearly_solar_position():
    longitude = 0.0
    latitude = 0.0
    year = datetime.today().year
    model = SolarPositionModels.suncalc
    try:
        plot_yearly_solar_position(longitude, latitude, year, model)
    except Exception as e:
        assert False, f"plot_yearly_solar_position raised an error: {e}"
