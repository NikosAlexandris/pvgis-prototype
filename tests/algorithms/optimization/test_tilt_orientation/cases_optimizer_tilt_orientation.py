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
({'longitude': Longitude(value=178.6957158053279, unit='degrees'),
'latitude': Latitude(value=35.1391756314313, unit='degrees'),
'elevation':25,
'timestamps': generate_datetime_series(start_time='2018-07-25 00:00:00', end_time='2019-06-08 00:00:00', frequency='h'),'timezone': ZoneInfo('UTC'),
'spectral_factor_series': SpectralFactorSeries(value=1),
'photovoltaic_module': PhotovoltaicModuleModel.CIS_FREE_STANDING,
'temperature_series': TemperatureSeries(value=17.568211079805884),
'wind_speed_series': WindSpeedSeries(value=1.6296327954937884),
'linke_turbidity_factor_series': LinkeTurbidityFactor(value=1),
'method': OptimizerMethod.shgo, 
'mode':OptimizerMode.tilt_orientation, 
'workers': -1,
'sampling_method_shgo':'sobol',
},
{'surface_orientation': SurfaceOrientation(value=3.141592653589793, unit='radians', min_radians=0, max_radians=6.283185307179586, min_degrees=0, max_degrees=360), 'surface_tilt': SurfaceTilt(value=0.6981317007977318, unit='radians', min_radians=0, max_radians=1.5707963267948966, min_degrees=0, max_degrees=90), 'mean_power_output': 262.53873}),
({'longitude': Longitude(value=-6.866430118349598, unit='degrees'),
'latitude': Latitude(value=-19.24585400936992, unit='degrees'),
'elevation':47,
'timestamps': generate_datetime_series(start_time='2014-08-08 00:00:00', end_time='2017-07-07 00:00:00', frequency='h'),'timezone': ZoneInfo('UTC'),
'spectral_factor_series': SpectralFactorSeries(value=1),
'photovoltaic_module': PhotovoltaicModuleModel.CIS_FREE_STANDING,
'temperature_series': TemperatureSeries(value=31.538465622739484),
'wind_speed_series': WindSpeedSeries(value=2.8463829071166535),
'linke_turbidity_factor_series': LinkeTurbidityFactor(value=1),
'method': OptimizerMethod.shgo, 
'mode':OptimizerMode.tilt_orientation, 
'workers': -1,
'sampling_method_shgo':'sobol',
},
{'surface_orientation': SurfaceOrientation(value=0.05235987755982989, unit='radians', min_radians=0, max_radians=6.283185307179586, min_degrees=0, max_degrees=360), 'surface_tilt': SurfaceTilt(value=0.33161255787892263, unit='radians', min_radians=0, max_radians=1.5707963267948966, min_degrees=0, max_degrees=90), 'mean_power_output': 253.2122}),
]
