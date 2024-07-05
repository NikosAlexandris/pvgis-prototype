#EXAMPLE I - 1 DAY

from pvgisprototype import (TemperatureSeries, WindSpeedSeries, SpectralFactorSeries, LinkeTurbidityFactor,
                             Longitude, Latitude, Elevation, SurfaceOrientation, SurfaceTilt,
                            )
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series
from zoneinfo import ZoneInfo
from pvgisprototype.api.surface.graph_power_output import graph_power_output
from pvgisprototype.api.surface.optimize_angles import optimize_angles
from pvgisprototype.api.surface.parameter_models import (SurfacePositionOptimizerMethod, SurfacePositionOptimizerMode)
import math


longitude_value = math.radians(8.628)
latitude_value = math.radians(45.812)
elevation_value = 214 
start_time = '2010-01-01'
end_time = '2010-01-02'
temperature_value = 5
wind_value = 2
surface_orientation_value=math.radians(180)


longitude = Longitude(value=longitude_value, unit='radians')
latitude = Latitude(value=latitude_value, unit='radians')
elevation = elevation_value
timestamps = generate_datetime_series(start_time=str(start_time), end_time=str(end_time), frequency="h")
timezone = ZoneInfo("UTC")
spectral_factor_series = SpectralFactorSeries(value=1)
photovoltaic_module = PhotovoltaicModuleModel.CIS_FREE_STANDING
temperature_series = TemperatureSeries(value=temperature_value)
wind_speed_series = WindSpeedSeries(value=wind_value)
linke_turbidity_factor_series = LinkeTurbidityFactor(value=1)
mode = SurfacePositionOptimizerMode.Tilt
surface_orientation = SurfaceOrientation(value=(surface_orientation_value), unit='radians')

result = optimize_angles(longitude = longitude,
                latitude = latitude,
                elevation = elevation, 
                timestamps = timestamps,
                timezone = timezone,
                spectral_factor_series = spectral_factor_series,
                photovoltaic_module = photovoltaic_module,
                temperature_series = temperature_series,
                wind_speed_series = wind_speed_series,
                linke_turbidity_factor_series = linke_turbidity_factor_series,
                mode = mode,
                surface_orientation = surface_orientation_value
                #SurfaceOrientation(value=(surface_orientation_value), unit='radians'),
                )

graph_power_output(longitude = longitude,
                latitude = latitude,
                elevation = elevation, 
                timestamps = timestamps,
                timezone = timezone,
                spectral_factor_series = spectral_factor_series,
                photovoltaic_module = photovoltaic_module,
                temperature_series = temperature_series,
                wind_speed_series = wind_speed_series,
                linke_turbidity_factor_series = linke_turbidity_factor_series,
                mode = mode,
                surface_orientation = SurfaceOrientation(value=(surface_orientation_value), unit='radians'),
                optimal_surface_tilt = result['surface_tilt'].value,
                optimal_pv_power = result['mean_power_output'] 
                )

print(result)

#NEED TO ADD THE PATH TO THE NETCDF FILES!!!


