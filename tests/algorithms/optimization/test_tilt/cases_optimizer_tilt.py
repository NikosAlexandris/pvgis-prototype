import random 
import datetime 
from zoneinfo import ZoneInfo
from pvgisprototype.api.utilities.timestamp import generate_datetime_series 
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype import (
    Longitude, Latitude, Elevation,
    TemperatureSeries, WindSpeedSeries,
    LinkeTurbidityFactor, SpectralFactorSeries,
    SurfaceOrientation, SurfaceTilt,
    )
from pvgisprototype.api.surface.optimize_angles import optimize_angles 
from pvgisprototype.api.surface.helper_functions import OptimizerMethod, OptimizerMode

cases = [ 
({'longitude': Longitude(value=25.44970626666634, unit='degrees'),
'latitude': Latitude(value=31.364632314388302, unit='degrees'),
'elevation':74,
'timestamps': generate_datetime_series(start_time='2011-06-02 00:00:00', end_time='2016-04-26 00:00:00', frequency='h'),'timezone': ZoneInfo('UTC'),
'spectral_factor_series': SpectralFactorSeries(value=1),
'photovoltaic_module': PhotovoltaicModuleModel.CIS_FREE_STANDING,
'temperature_series': TemperatureSeries(value=15.595376476208257),
'wind_speed_series': WindSpeedSeries(value=8.395074233989956),
'linke_turbidity_factor_series': LinkeTurbidityFactor(value=1),
'method': OptimizerMethod.shgo, 
'mode':OptimizerMode.tilt, 
'surface_orientation': SurfaceOrientation(value=3.829808223145668, unit='radians'),
'workers': -1,
'sampling_method_shgo':'sobol',
},
{'surface_orientation': SurfaceOrientation(value=3.829808223145668, unit='radians', min_radians=0, max_radians=6.283185307179586, min_degrees=0, max_degrees=360), 'surface_tilt': SurfaceTilt(value=0.5410520681182421, unit='radians', min_radians=0, max_radians=1.5707963267948966, min_degrees=0, max_degrees=90), 'mean_power_output': 272.63068}),
({'longitude': Longitude(value=-141.79431611987303, unit='degrees'),
'latitude': Latitude(value=-58.44052365010102, unit='degrees'),
'elevation':91,
'timestamps': generate_datetime_series(start_time='2022-03-19 00:00:00', end_time='2022-06-10 00:00:00', frequency='h'),'timezone': ZoneInfo('UTC'),
'spectral_factor_series': SpectralFactorSeries(value=1),
'photovoltaic_module': PhotovoltaicModuleModel.CIS_FREE_STANDING,
'temperature_series': TemperatureSeries(value=6.749736495056788),
'wind_speed_series': WindSpeedSeries(value=0.7757590918325846),
'linke_turbidity_factor_series': LinkeTurbidityFactor(value=1),
'method': OptimizerMethod.shgo, 
'mode':OptimizerMode.tilt, 
'surface_orientation': SurfaceOrientation(value=2.249560767432997, unit='radians'),
'workers': -1,
'sampling_method_shgo':'sobol',
},
{'surface_orientation': SurfaceOrientation(value=2.249560767432997, unit='radians', min_radians=0, max_radians=6.283185307179586, min_degrees=0, max_degrees=360), 'surface_tilt': SurfaceTilt(value=0.0, unit='radians', min_radians=0, max_radians=1.5707963267948966, min_degrees=0, max_degrees=90), 'mean_power_output': 56.516388}),
]
