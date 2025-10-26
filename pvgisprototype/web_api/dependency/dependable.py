from fastapi import Depends
from pvgisprototype.web_api.dependency.fingerprint import process_fingerprint
from pvgisprototype.web_api.dependency.common_datasets import process_horizon_profile
from pvgisprototype.web_api.dependency.location import (
    process_latitude,
    process_longitude,
)
from pvgisprototype.web_api.dependency.shading import process_shading_model
from pvgisprototype.web_api.dependency.surface import (
    process_optimise_surface_position,
    process_surface_orientation,
    process_surface_tilt,
)
from pvgisprototype.web_api.dependency.time import (
    process_start_time,
    process_timezone,
    process_timezone_to_be_converted,
    process_frequency,
)
from pvgisprototype.web_api.dependency.meteorology import (
    create_temperature_series,
    create_wind_speed_series,
    process_linke_turbidity_factor_series,
)
from pvgisprototype.web_api.dependency.spectral_factor import (
    create_spectral_factor_series,
)
from pvgisprototype.web_api.dependency.statistics import (
    process_groupby,
)
from pvgisprototype.web_api.dependency.tmy import (
    tmy_statistic_model,
    _select_data_from_meteorological_variable,
)
from pvgisprototype.web_api.dependency.units import process_angle_output_units

from pvgisprototype.web_api.dependency.position import (
    process_series_solar_position_models_list,
    process_surface_orientation_list,
    process_surface_tilt_list,
    process_series_solar_position_model,
    process_series_solar_incidence_model,
)

from pvgisprototype.web_api.dependency.verbosity import (
    process_quiet,
    process_quiet_for_performance_analysis,
    process_verbose,
    process_verbose_for_performance_analysis,
)

from pvgisprototype.web_api.dependency.common_datasets import (
    process_timestamps,
    convert_timestamps_to_specified_timezone,
    _provide_common_datasets,
    _read_datasets,
)


# Units

fastapi_dependable_angle_output_units = Depends(process_angle_output_units)

# Data

fastapi_dependable_common_datasets = Depends(_provide_common_datasets)
fastapi_dependable_read_datasets = Depends(_read_datasets)
fastapi_dependable_select_data_from_meteorological_variable = Depends(_select_data_from_meteorological_variable)

# Time

fastapi_dependable_convert_timestamps = Depends(convert_timestamps_to_specified_timezone)
fastapi_dependable_convert_timezone = Depends(process_timezone_to_be_converted)
fastapi_dependable_end_time = Depends(process_start_time)
fastapi_dependable_fingerprint = Depends(process_fingerprint)
fastapi_dependable_timestamps = Depends(process_timestamps)
fastapi_dependable_timezone = Depends(process_timezone)
fastapi_dependable_start_time = Depends(process_start_time)

# Location

fastapi_dependable_latitude = Depends(process_latitude)
fastapi_dependable_longitude = Depends(process_longitude)

# Surface position

fastapi_dependable_optimise_surface_position = Depends(process_optimise_surface_position)
fastapi_dependable_surface_orientation = Depends(process_surface_orientation)
fastapi_dependable_surface_orientation_list = Depends(process_surface_orientation_list)
fastapi_dependable_surface_tilt = Depends(process_surface_tilt)
fastapi_dependable_surface_tilt_list = Depends(process_surface_tilt_list)

# Solar position

fastapi_dependable_solar_incidence_models = Depends(process_series_solar_incidence_model)
fastapi_dependable_solar_position_model = Depends(process_series_solar_position_model)
fastapi_dependable_solar_position_models_list = Depends(process_series_solar_position_models_list)

# Horizon

fastapi_dependable_horizon_profile = Depends(process_horizon_profile)
fastapi_dependable_shading_model = Depends(process_shading_model)

# Meteorology

fastapi_dependable_temperature_series = Depends(create_temperature_series)
fastapi_dependable_wind_speed_series = Depends(create_wind_speed_series)
fastapi_dependable_linke_turbidity_factor_series = Depends(process_linke_turbidity_factor_series)

# TMY

fastapi_dependable_tmy_statistic_model = Depends(tmy_statistic_model)
fastapi_dependable_verbose = Depends(process_verbose)
fastapi_dependable_verbose_for_performance_analysis = Depends(process_verbose_for_performance_analysis)

# Statistics

fastapi_dependable_frequency = Depends(process_frequency)
fastapi_dependable_groupby = Depends(process_groupby)

fastapi_dependable_quiet = Depends(process_quiet)
fastapi_dependable_quiet_for_performance_analysis = Depends(process_quiet_for_performance_analysis)

# Spectral Factor

fastapi_dependable_spectral_factor_series = Depends(create_spectral_factor_series)
