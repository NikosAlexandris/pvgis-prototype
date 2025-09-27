#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from enum import verify
from pvgisprototype.api.surface.optimizer import optimizer
from pvgisprototype.api.datetime.datetimeindex import generate_timestamps
from pvgisprototype.api.series.global_horizontal_irradiance import (
    get_global_horizontal_irradiance_series,
)
from pvgisprototype.api.series.direct_horizontal_irradiance import (
    get_direct_horizontal_irradiance_series,
)
from pvgisprototype.api.series.temperature import get_temperature_series
from pathlib import Path
from pvgisprototype.api.surface.optimizer_bounds import define_optimiser_bounds
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMethod
from pvgisprototype.api.series.wind_speed import get_wind_speed_series
from pvgisprototype.api.surface.parameters import build_location_dictionary
from pvgisprototype import (
    Longitude,
    Latitude,
    SurfaceOrientation,
    SurfaceTilt,
)
from zoneinfo import ZoneInfo
from pvgisprototype.api.surface.power import (
    calculate_mean_negative_photovoltaic_power_output,
)
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT


# Location

longitude = Longitude(value=8.628, unit="degrees")
latitude = Latitude(value=45.812, unit="degrees")
timestamps = generate_timestamps(
    start_time="2013-01-01",
    end_time="2013-12-31",
    data_file=None,
)
so = SurfaceOrientation(value=180, unit="degrees")
st = SurfaceTilt(value=45, unit="degrees")
location = build_location_dictionary(
    longitude=longitude.radians,
    latitude=latitude.radians,
    elevation=214,
    timestamps=timestamps,
    surface_orientation=so.radians,
    surface_tilt=st.radians,
    timezone=ZoneInfo("UTC"),
    mode="Orientation",
    verbose=VERBOSE_LEVEL_DEFAULT,
)


# Input time series
sis = get_global_horizontal_irradiance_series(
    longitude=longitude.radians,
    latitude=latitude.radians,
    global_horizontal_irradiance_series=Path("sarah3_sis_12_076.nc"),
    timestamps=timestamps,
    verbose=10,
)
sid = get_direct_horizontal_irradiance_series(
    longitude=longitude.radians,
    latitude=latitude.radians,
    direct_horizontal_irradiance_series=Path("sarah3_sid_12_076.nc"),
    timestamps=timestamps,
    verbose=10,
)
t2m = get_temperature_series(
    longitude=longitude.radians,
    latitude=latitude.radians,
    temperature_series=Path("era5_t2m_over_esti_jrc.nc"),
    timestamps=timestamps,
    verbose=10,
)
ws2m = get_wind_speed_series(
    longitude=longitude.radians,
    latitude=latitude.radians,
    wind_speed_series=Path("era5_ws2m_over_esti_jrc.nc"),
    timestamps=timestamps,
    verbose=10,
)
other_arguments = {
    "global_horizontal_irradiance": sis,
    "direct_horizontal_irradiance": sid,
    "temperature_series": t2m,
    "wind_speed_series": ws2m,
}

# Combine the input parameters
arguments = location | other_arguments

# Define bounds for the optimizer

bounds = define_optimiser_bounds(
    min_surface_orientation=so.min_radians,
    max_surface_orientation=so.max_radians,
    min_surface_tilt=st.min_radians,
    max_surface_tilt=st.max_radians,
    mode=SurfacePositionOptimizerMode.Orientation,
    method=SurfacePositionOptimizerMethod.shgo,
    verbose=VERBOSE_LEVEL_DEFAULT,
)

# Optimise !

print(f"\nOptimizer method = CG")

optimal_position = optimizer(
    arguments=arguments,
    func=calculate_mean_negative_photovoltaic_power_output,
    mode=SurfacePositionOptimizerMode.Orientation,
    method=SurfacePositionOptimizerMethod.cg,
    iterations=3,
)

print(f"Optimal surface position : {optimal_position}")

## SHGO

print(f"\nOptimizer method = SHGO")

optimal_position = optimizer(
    arguments=arguments,
    func=calculate_mean_negative_photovoltaic_power_output,
    mode=SurfacePositionOptimizerMode.Tilt,
    method=SurfacePositionOptimizerMethod.shgo,
    bounds=bounds,
    iterations=3,
)

print(f"\nOptimal surface position : {optimal_position}")

optimal_position = optimizer(
    arguments=arguments,
    func=calculate_mean_negative_photovoltaic_power_output,
    mode=SurfacePositionOptimizerMode.Orientation_and_Tilt,
    bounds=bounds,
    iterations=3,
)

print(f"\nOptimal surface position : {optimal_position}")
