from zoneinfo import ZoneInfo
from pvgisprototype.api.utilities.timestamp import generate_datetime_series 
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype import (
    Longitude, Latitude, TemperatureSeries, WindSpeedSeries,
    LinkeTurbidityFactor, SpectralFactorSeries,
    SurfaceOrientation, SurfaceTilt,
    )
from pvgisprototype.api.surface.helper_functions import OptimizerMethod, OptimizerMode

cases = [ 
({'longitude': Longitude(value=-38.66174132430271, unit='degrees'),
'latitude': Latitude(value=-44.08756402006285, unit='degrees'),
'elevation':8,
'timestamps': generate_datetime_series(start_time='2014-03-19 00:00:00', end_time='2022-05-24 00:00:00', frequency='h'),'timezone': ZoneInfo('UTC'),
'spectral_factor_series': SpectralFactorSeries(value=1),
'photovoltaic_module': PhotovoltaicModuleModel.CIS_FREE_STANDING,
'temperature_series': TemperatureSeries(value=3.5879628702702644),
'wind_speed_series': WindSpeedSeries(value=3.5605725961015047),
'linke_turbidity_factor_series': LinkeTurbidityFactor(value=1),
'method': OptimizerMethod.shgo, 
'mode':OptimizerMode.orientation, 
'surface_tilt': SurfaceTilt(value=1.372256508541851, unit='radians'),
'workers': -1,
'sampling_method_shgo':'sobol',
},
{'surface_orientation': SurfaceOrientation(value=6.213372137099813, unit='radians', min_radians=0, max_radians=6.283185307179586, min_degrees=0, max_degrees=360), 'surface_tilt': SurfaceTilt(value=1.372256508541851, unit='radians', min_radians=0, max_radians=1.5707963267948966, min_degrees=0, max_degrees=90), 'mean_power_output': 235.9186}),
({'longitude': Longitude(value=139.60107260593605, unit='degrees'),
'latitude': Latitude(value=62.900390793593715, unit='degrees'),
'elevation':24,
'timestamps': generate_datetime_series(start_time='2014-08-04 00:00:00', end_time='2019-11-08 00:00:00', frequency='h'),'timezone': ZoneInfo('UTC'),
'spectral_factor_series': SpectralFactorSeries(value=1),
'photovoltaic_module': PhotovoltaicModuleModel.CIS_FREE_STANDING,
'temperature_series': TemperatureSeries(value=30.249128585649558),
'wind_speed_series': WindSpeedSeries(value=9.620574304769585),
'linke_turbidity_factor_series': LinkeTurbidityFactor(value=1),
'method': OptimizerMethod.shgo, 
'mode':OptimizerMode.orientation, 
'surface_tilt': SurfaceTilt(value=0.6136344640156163, unit='radians'),
'workers': -1,
'sampling_method_shgo':'sobol',
},
{'surface_orientation': SurfaceOrientation(value=3.141592653589793, unit='radians', min_radians=0, max_radians=6.283185307179586, min_degrees=0, max_degrees=360), 'surface_tilt': SurfaceTilt(value=0.6136344640156163, unit='radians', min_radians=0, max_radians=1.5707963267948966, min_degrees=0, max_degrees=90), 'mean_power_output': 213.53023}),
]
