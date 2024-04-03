from typing import List
from typing import Optional
from fastapi import Query
from fastapi import Depends
from datetime import datetime
from pvgisprototype.api.utilities.timestamp import ctx_attach_requested_timezone
from pvgisprototype.api.utilities.timestamp import parse_timestamp_series
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import now_local_datetimezone
from pvgisprototype.constants import LATITUDE_MINIMUM
from pvgisprototype.constants import LATITUDE_MAXIMUM
from pvgisprototype.constants import LONGITUDE_MINIMUM
from pvgisprototype.constants import LONGITUDE_MAXIMUM
from pvgisprototype.constants import ELEVATION_MINIMUM
from pvgisprototype.constants import ELEVATION_MAXIMUM


longitude_help = "Longitude in decimal degrees ranging in [-180, 360]. If ranging in [0, 360], consider the `convert_longitude_360` option."
latitude_help = "Latitude in decimal degrees ranging in [-90, 90]"
elevation_help = "Topographical elevation"
timestamp_help = "Quoted date-time string of data to extract from series, example: '2112-12-21 21:12:12'"
timestamps_help = "Quoted date-time strings of data to extract from series, example: '2112-12-21, 2112-12-21 12:21:21, 2112-12-21 21:12:12'"
start_time_help = "Start timestamp of the period."
frequency_help = "Frequency for timestamp generation, ex. 30m. A number and date/time unit."
end_time_help = "End timestamp of the period."
timezone_help = "Timezone (e.g., 'Europe/Athens')."
local_time_help = "Use the system's local time zone."
random_time_help = "Generate a random date, time, and timezone."
random_day_help = "Generate a random day."
random_days_help = "Generate random days."
time_series_help = "A time series dataset (any format supported by Xarray)"
mask_and_scale_help = "Mask and scale the series"
nearest_neighbor_lookup_help = "Enable nearest neighbor (inexact) lookups. Read Xarray manual on nearest-neighbor-lookups"
inexact_matches_method_help = "Method for nearest neighbor (inexact) lookups. Read Xarray manual on nearest-neighbor-lookups"
tolerance_help = "Maximum distance between original & new labels for inexact matches. Read Xarray manual on nearest-neighbor-lookups"
in_memory_help = "Whether to process data in memory"
surface_tilt_help = "Surface tilt angle in degrees"
surface_orientation_help = "Surface orientation angle in degrees"
linke_turbidity_help = "Linke turbidity factor"
atmospheric_refraction_help = "Apply atmospheric refraction correction"
solar_zenith_help = "Refracted solar zenith angle in degrees"
albedo_help = "Albedo value for the surface"
angular_loss_factor_help = "Apply angular loss factor"
solar_position_help = "Model used for solar position calculation"
solar_incidence_help = "Model used for solar incidence calculation"
solar_time_help = "Model used for solar time calculation"
time_offset_global_help = "Global time offset in hours"
hour_offset_help = "Hour offset"
solar_constant_help = "Solar constant value"
perigee_offset_help = "Perigee offset value"
eccentricity_correction_help = "Eccentricity correction factor"
system_efficiency_help = "System efficiency"
power_model_help = "Photovoltaic power model"
efficiency_help = "Efficiency value"
rounding_places_help = "Number of decimal places for rounding"
verbose_help = "Verbose level"
log_help = "Log level"
fingerprint_help='Fingerprint the photovoltaic power output time series'
module_temperature_algorithm_description='Algorithms for calculation of the effect of temperature on the power output of a photovoltaic system as a function of temperature and optionally wind speed',


fastapi_query_longitude = Query(
    title="Longitude",
    description=longitude_help,
    ge=LONGITUDE_MINIMUM,
    le=LONGITUDE_MAXIMUM,
)
fastapi_query_longitude_in_degrees = Query(
    ...,
    title="Longitude",
    description=longitude_help,
    ge=LONGITUDE_MINIMUM,
    le=LONGITUDE_MAXIMUM,
)
fastapi_query_latitude = Query(
    ...,
    title="Latitude",
    description=latitude_help,
    ge=LATITUDE_MINIMUM,
    le=LATITUDE_MAXIMUM,
)
fastapi_query_latitude_in_degrees = Query(
    ...,
    title="Latitude",
    description=latitude_help,
    ge=LATITUDE_MINIMUM,
    le=LATITUDE_MAXIMUM,
)
fastapi_query_elevation = Query(
    ...,
    title="Elevation",
    description=elevation_help,
    ge=ELEVATION_MINIMUM,
    le=ELEVATION_MAXIMUM,
)
fastapi_query_timestamp = Query(
    default_factory=now_utc_datetimezone,
    description=timestamp_help,
    # Depends(ctx_attach_requested_timezone)
)
fastapi_query_timestamps = Query(
    None,
    description=timestamps_help,
    # Depends(parse_timestamp_series)
)
fastapi_query_start_time = Query(
    description=start_time_help,
)
fastapi_query_frequency = Query(
    description=frequency_help,
)
fastapi_query_end_time = Query(
    description=end_time_help,
)
fastapi_query_timezone = Query(
    description=timezone_help,
    # Depends on ctx_convert_to_timezone
)
fastapi_query_local_time = Query(
    description=local_time_help,
    # Depends on now_local_datetimezone
)
fastapi_query_random_time = Query(
    description=random_time_help,
)
fastapi_query_random_time_series = Query(
    description=random_time_help,
)
fastapi_query_random_day = Query(
    description=random_day_help,
)
fastapi_query_random_days = Query(
    description=random_days_help,
)
fastapi_query_time_series_query = Query(
    description=time_series_help,
)
fastapi_query_mask_and_scale = Query(
    description=mask_and_scale_help,
)
fastapi_query_neighbor_lookup = Query(
    description=nearest_neighbor_lookup_help,
)
fastapi_query_tolerance = Query(
    description=tolerance_help,
)
fastapi_query_in_memory = Query(
    # False,
    description=in_memory_help,
)
fastapi_query_surface_tilt = Query(
    # SURFACE_TILT_DEFAULT,
    description=surface_tilt_help,
)
fastapi_query_surface_orientation = Query(
    # SURFACE_ORIENTATION_DEFAULT,
    description=surface_orientation_help,
)
fastapi_query_linke_turbidity_factor_series = Query(
    # LINKE_TURBIDITY_DEFAULT,
    description=linke_turbidity_help,
)
fastapi_query_apply_atmospheric_refraction = Query(
    # True,
    description=atmospheric_refraction_help,
)
fastapi_query_refracted_solar_zenith = Query(
    # REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    description=solar_zenith_help,
)
fastapi_query_albedo = Query(
    # 2,
    description=albedo_help,
)
fastapi_query_apply_angular_loss_factor = Query(
    # True,
    description=angular_loss_factor_help,
)
fastapi_query_solar_position_model = Query(
    # SOLAR_POSITION_ALGORITHM_DEFAULT,
    description=solar_position_help,
)
fastapi_query_solar_incidence_model = Query(
    # SolarIncidenceModel.jenco,
    description=solar_incidence_help,
)
fastapi_query_solar_time_model = Query(
    # SOLAR_TIME_ALGORITHM_DEFAULT,
    description=solar_time_help,
)
fastapi_query_time_offset_global = Query(
    # 0,
    description=time_offset_global_help,
)
fastapi_query_hour_offset = Query(
    # 0,
    description=hour_offset_help,
)
fastapi_query_solar_constant = Query(
    # SOLAR_CONSTANT,
    description=solar_constant_help,
)
fastapi_query_perigee_offset = Query(
    # PERIGEE_OFFSET,
    description=perigee_offset_help,
)
fastapi_query_eccentricity_correction_factor = Query(
    # ECCENTRICITY_CORRECTION_FACTOR,
    description=eccentricity_correction_help,
)
fastapi_query_system_efficiency = Query(
    # SYSTEM_EFFICIENCY_DEFAULT,
    description=system_efficiency_help,
)
fastapi_query_power_model = Query(
    # None,
    description=power_model_help,
)
fastapi_query_efficiency = Query(
    # None,
    description=efficiency_help,
)
fastapi_query_rounding_places = Query(
    # 5,
    description=rounding_places_help,
)
fastapi_query_verbose = Query(
    # VERBOSE_LEVEL_DEFAULT,
    description=verbose_help,
)
fastapi_query_log = Query(
    description=log_help,
)
fastapi_query_fingerprint = Query(
    description=fingerprint_help,
)
fastapi_query_module_temperature_algorithm = Query(
    description=module_temperature_algorithm_description,
)
fastapi_query_photovoltaic_module_model = Query(
    description='Photovoltaic module' 
)
