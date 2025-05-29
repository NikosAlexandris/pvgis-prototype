import datetime
import random
from zoneinfo import ZoneInfo

from pvgisprototype import (  # SurfaceOrientation,; SurfaceTilt,
    Latitude,
    LinkeTurbidityFactor,
    Longitude,
    SpectralFactorSeries,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.positioning import optimise_surface_position
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series
import math

def generate_random_date():
    date = datetime.datetime(
        random.randrange(2010, 2023),
        random.randrange(1, 12),
        random.randrange(1, 28),
        00,
        00,
    )
    return date


# longitude_value = random.uniform(-180, 180)
longitude = Longitude(value=8.628, unit="degrees")
# latitude_value = random.uniform(-90, 90)
latitude = Latitude(value=45.812, unit="degrees")
elevation = random.randrange(0, 200)

# surface_orientation_value = random.uniform(0, SurfaceOrientation().max_radians)

# surface_orientation = (SurfaceOrientation(value=math.pi, unit="radians"),)
surface_orientation = math.pi
# surface_tilt = (
#     SurfaceTilt(value=random.uniform(0, SurfaceTilt().max_radians), unit="radians"),
# )
surface_tilt = math.pi / 4
# start_time, end_time = generate_random_date(), generate_random_date()
start_time = "2005-01-01"
end_time = "2020-12-31"
timezone = ZoneInfo("UTC")
if start_time > end_time:
    start_time, end_time = end_time, start_time
# temperature_value = random.uniform(0, 35)
temperature_value = 14
# wind_value = random.uniform(0, 15)
wind_value = 1

timestamps = generate_datetime_series(
    start_time=str(start_time), end_time=str(end_time), frequency="h"
)

optimal_surface_position = optimise_surface_position(
    longitude=longitude.radians,
    latitude=latitude.radians,
    elevation=elevation,  # Elevation(value=random.randrange(0,100), unit = 'meters'),
    surface_orientation=surface_orientation,
    surface_tilt=surface_tilt,
    timestamps=timestamps,
    timezone=timezone,
    spectral_factor_series=SpectralFactorSeries(value=1),
    photovoltaic_module=PhotovoltaicModuleModel.CIS_FREE_STANDING,
    temperature_series=TemperatureSeries(value=temperature_value),
    wind_speed_series=WindSpeedSeries(value=wind_value),
    linke_turbidity_factor_series=LinkeTurbidityFactor(value=1),
    method=SurfacePositionOptimizerMethod.shgo,
    mode=SurfacePositionOptimizerMode.Tilt,
    workers=-1,
    sampling_method_shgo=SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
)
print(optimise_surface_position)
