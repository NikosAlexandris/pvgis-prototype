from fastapi import Query

from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.constants import (
    ALBEDO_DESCRIPTION,
    ALBEDO_MAXIMUM,
    ALBEDO_MINIMUM,
    ANALYSIS_DESCRIPTION,
    ANGLE_OUTPUT_UNITS_DESCRIPTION,
    ARRAY_BACKEND_DESCRIPTION,
    ATMOSPHERIC_REFRACTION_DESCRIPTION,
    COMMAND_METADATA_DESCRIPTION,
    CSV_DESCRIPTION,
    DATA_TYPE_DESCRIPTION,
    DIRECT_HORIZONTAL_IRRADIANCE_DESCRIPTION,
    ECCENTRICITY_CORRECTION_DESCRIPTION,
    EFFICIENCY_DESCRIPTION,
    EFFICIENCY_FACTOR_MAXIMUM,
    EFFICIENCY_FACTOR_MINIMUM,
    ELEVATION_DESCRIPTION,
    ELEVATION_MAXIMUM,
    ELEVATION_MINIMUM,
    ELEVATION_NAME,
    END_TIME_DESCRIPTION,
    FINGERPRINT_DESCRIPTION,
    FREQUENCY_DESCRIPTION,
    GLOBAL_HORIZONTAL_IRRADIANCE_DESCRIPTION,
    GROUPBY_DESCRIPTION,
    IN_MEMORY_DESCRIPTION,
    INCIDENCE_ALGORITHM_DESCRIPTION,
    INDEX_IN_TABLE_OUTPUT_FLAG_DESCRIPTION,
    LATITUDE_DESCRIPTION,
    LATITUDE_MAXIMUM,
    LATITUDE_MINIMUM,
    LATITUDE_NAME,
    LINKE_TURBIDITY_DESCRIPTION,
    LOCAL_TIME_DESCRIPTION,
    LOG_LEVEL_DESCRIPTION,
    LONGITUDE_DESCRIPTION,
    LONGITUDE_MAXIMUM,
    LONGITUDE_MINIMUM,
    LONGITUDE_NAME,
    MASK_AND_SCALE_DESCRIPTION,
    MULTI_THREAD_FLAG_DESCRIPTION,
    NEAREST_NEIGHBOR_LOOKUP_DESCRIPTION,
    OPTIMISE_SURFACE_POSITION_DESCRIPTION,
    PEAK_POWER_DESCRIPTION,
    PEAK_POWER_MINIMUM,
    PERIGEE_OFFSET_DESCRIPTION,
    PERIODS_DESCRIPTION,
    PHOTOVOLTAIC_MODULE_DESCRIPTION,
    POSITION_ALGORITHM_DESCRIPTION,
    POSITION_ALGORITHM_LIST_DESCRIPTION,
    POWER_MODEL_DESCRIPTION,
    POWER_MODEL_LONG_DESCRIPTION,
    QUICK_RESPONSE_CODE_DESCRIPTION,
    QUIET_FLAG_DESCRIPTION,
    RADIATION_CUTOFF_THRESHHOLD,
    RADIATION_CUTOFF_THRESHOLD_DESCRIPTION,
    RANDOM_DAY_DESCRIPTION,
    RANDOM_DAYS_DESCRIPTION,
    RANDOM_TIME_DESCRIPTION,
    REFLECTIVITY_EFFECT_DESCRIPTION,
    REFRACTED_SOLAR_ZENITH_DESCRIPTION,
    ROUNDING_PLACES_DESCRIPTION,
    SAMPLING_METHOD_DESCRIPTION,
    SOLAR_CONSTANT_DESCRIPTION,
    SPECTRAL_EFFECT_DESCRIPTION,
    START_TIME_DESCRIPTION,
    STATISTICS_DESCRIPTION,
    SURFACE_ORIENTATION_DESCRIPTION,
    SURFACE_ORIENTATION_MAXIMUM,
    SURFACE_ORIENTATION_MINIMUM,
    SURFACE_TILT_DESCRIPTION,
    SURFACE_TILT_MAXIMUM,
    SURFACE_TILT_MINIMUM,
    SYSTEM_EFFICIENCY_DESCRIPTION,
    SYSTEM_EFFICIENCY_MAXIMUM,
    SYSTEM_EFFICIENCY_MINIMUM,
    TEMPERATURE_TIME_SERIES_DESCRIPTION,
    TIME_SERIES_DESCRIPTION,
    TIMESTAMP_DESCRIPTION,
    TIMESTAMPS_DESCRIPTION,
    TIMEZONE_DESCRIPTION,
    TIMING_ALGORITHM_DESCRIPTION,
    TOLERANCE_DESCRIPTION,
    TOLERANCE_MINIMUM,
    VERBOSE_LEVEL_DESCRIPTION,
    WIND_SPEED_TIME_SERIES_DESCRIPTION,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DESCRIPTION,
    cPROFILE_FLAG_DESCRIPTION,
)

fastapi_query_longitude = Query(
    title=LONGITUDE_NAME,
    description=LONGITUDE_DESCRIPTION,
    ge=LONGITUDE_MINIMUM,
    le=LONGITUDE_MAXIMUM,
)
fastapi_query_longitude_in_degrees = Query(
    ...,
    title=LONGITUDE_NAME,
    description=LONGITUDE_DESCRIPTION,
    ge=LONGITUDE_MINIMUM,
    le=LONGITUDE_MAXIMUM,
)
fastapi_query_latitude = Query(
    ...,
    title=LATITUDE_NAME,
    description=LATITUDE_DESCRIPTION,
    ge=LATITUDE_MINIMUM,
    le=LATITUDE_MAXIMUM,
)
fastapi_query_latitude_in_degrees = Query(
    ...,
    title=LATITUDE_NAME,
    description=LATITUDE_DESCRIPTION,
    ge=LATITUDE_MINIMUM,
    le=LATITUDE_MAXIMUM,
)
fastapi_query_elevation = Query(
    ...,
    title=ELEVATION_NAME,
    description=ELEVATION_DESCRIPTION,
    ge=ELEVATION_MINIMUM,
    le=ELEVATION_MAXIMUM,
)
fastapi_query_surface_orientation = Query(
    # SURFACE_ORIENTATION_DEFAULT,
    description=SURFACE_ORIENTATION_DESCRIPTION,
    ge=SURFACE_ORIENTATION_MINIMUM,
    le=SURFACE_ORIENTATION_MAXIMUM,
)
fastapi_query_surface_orientation_list = Query(
    description=SURFACE_ORIENTATION_DESCRIPTION,
)
fastapi_query_surface_tilt = Query(
    # SURFACE_TILT_DEFAULT,
    description=SURFACE_TILT_DESCRIPTION,
    ge=SURFACE_TILT_MINIMUM,
    le=SURFACE_TILT_MAXIMUM,
)
fastapi_query_surface_tilt_list = Query(
    description=SURFACE_TILT_DESCRIPTION,
)
fastapi_query_timestamp = Query(
    default_factory=now_utc_datetimezone,
    description=TIMESTAMP_DESCRIPTION,
    # Depends(ctx_attach_requested_timezone)
)
fastapi_query_timestamps = Query(
    description=TIMESTAMPS_DESCRIPTION,
    # Depends(parse_timestamp_series)
)
fastapi_query_start_time = Query(
    description=START_TIME_DESCRIPTION,
)
fastapi_query_periods = Query(
    description=PERIODS_DESCRIPTION,
)
fastapi_query_frequency = Query(description=FREQUENCY_DESCRIPTION)
fastapi_query_end_time = Query(
    description=END_TIME_DESCRIPTION,
)
fastapi_query_timezone = Query(
    description=TIMEZONE_DESCRIPTION,
    # Depends on ctx_convert_to_timezone
)
fastapi_query_local_time = Query(
    description=LOCAL_TIME_DESCRIPTION,
    # Depends on now_local_datetimezone
)
fastapi_query_random_time = Query(
    description=RANDOM_TIME_DESCRIPTION,
)
fastapi_query_random_time_series = Query(
    description=RANDOM_TIME_DESCRIPTION,
)
fastapi_query_random_day = Query(
    description=RANDOM_DAY_DESCRIPTION,
)
fastapi_query_random_days = Query(
    description=RANDOM_DAYS_DESCRIPTION,
)
fastapi_query_time_series_query = Query(
    description=TIME_SERIES_DESCRIPTION,
)
fastapi_query_neighbor_lookup = Query(
    description=NEAREST_NEIGHBOR_LOOKUP_DESCRIPTION,
)
fastapi_query_tolerance = Query(
    description=TOLERANCE_DESCRIPTION,
    ge=TOLERANCE_MINIMUM,
)
fastapi_query_mask_and_scale = Query(
    description=MASK_AND_SCALE_DESCRIPTION,
)
fastapi_query_in_memory = Query(
    # IN_MEMORY_FLAG_DEFAULT,
    description=IN_MEMORY_DESCRIPTION,
)
fastapi_query_linke_turbidity_factor_series = Query(
    # LINKE_TURBIDITY_DEFAULT,
    description=LINKE_TURBIDITY_DESCRIPTION,
)
fastapi_query_apply_atmospheric_refraction = Query(
    # True,
    description=ATMOSPHERIC_REFRACTION_DESCRIPTION,
)
fastapi_query_refracted_solar_zenith = Query(
    # REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    description=REFRACTED_SOLAR_ZENITH_DESCRIPTION,
)
fastapi_query_albedo = Query(
    # ALBEDO_DEFAULT,
    description=ALBEDO_DESCRIPTION,
    ge=ALBEDO_MINIMUM,
    le=ALBEDO_MAXIMUM,
)
fastapi_query_apply_reflectivity_factor = Query(
    # ANGULAR_LOSS_FACTOR_FLAG_DEFAULT : To Be Renamed To : REFLECTIVITY_EFFECT_FLAG_DEFAULT
    description=REFLECTIVITY_EFFECT_DESCRIPTION,
)
fastapi_query_solar_time_model = Query(
    # SOLAR_TIME_ALGORITHM_DEFAULT,
    description=TIMING_ALGORITHM_DESCRIPTION,
)
fastapi_query_solar_constant = Query(
    # SOLAR_CONSTANT,
    description=SOLAR_CONSTANT_DESCRIPTION,
)
fastapi_query_perigee_offset = Query(
    # PERIGEE_OFFSET,
    description=PERIGEE_OFFSET_DESCRIPTION,
)
fastapi_query_eccentricity_correction_factor = Query(
    # ECCENTRICITY_CORRECTION_FACTOR,
    description=ECCENTRICITY_CORRECTION_DESCRIPTION,
)
fastapi_query_solar_position_model = Query(
    # SOLAR_POSITION_ALGORITHM_DEFAULT,
    description=POSITION_ALGORITHM_DESCRIPTION,
)
fastapi_query_solar_incidence_model = Query(
    # SolarIncidenceModel.jenco,
    description=INCIDENCE_ALGORITHM_DESCRIPTION,
)
fastapi_query_zero_negative_solar_incidence_angle = Query(
    description=ZERO_NEGATIVE_INCIDENCE_ANGLE_DESCRIPTION,
)
fastapi_query_photovoltaic_module_model = Query(
    description=PHOTOVOLTAIC_MODULE_DESCRIPTION,
)
fastapi_query_system_efficiency = Query(
    # SYSTEM_EFFICIENCY_DEFAULT,
    description=SYSTEM_EFFICIENCY_DESCRIPTION,
    ge=SYSTEM_EFFICIENCY_MINIMUM,
    le=SYSTEM_EFFICIENCY_MAXIMUM,
)
fastapi_query_power_model = Query(
    # None,
    description=POWER_MODEL_DESCRIPTION,
)
fastapi_query_temperature_model = Query(
    description=POWER_MODEL_LONG_DESCRIPTION,
)
fastapi_query_efficiency = Query(
    # EFFICIENCY_FACTOR_DEFAULT,
    description=EFFICIENCY_DESCRIPTION,
    ge=EFFICIENCY_FACTOR_MINIMUM,
    le=EFFICIENCY_FACTOR_MAXIMUM,
)
fastapi_query_peak_power = Query(
    description=PEAK_POWER_DESCRIPTION,
    ge=PEAK_POWER_MINIMUM,
    alias="peak-power",
)
fastapi_query_radiation_cutoff_threshold = Query(
    description=RADIATION_CUTOFF_THRESHOLD_DESCRIPTION,
    ge=RADIATION_CUTOFF_THRESHHOLD,
)
fastapi_query_multi_thread = Query(
    description=MULTI_THREAD_FLAG_DESCRIPTION,
)
fastapi_query_dtype = Query(
    description=DATA_TYPE_DESCRIPTION,
)
fastapi_query_array_backend = Query(
    description=ARRAY_BACKEND_DESCRIPTION,
)
fastapi_query_angle_output_units = Query(
    description=ANGLE_OUTPUT_UNITS_DESCRIPTION,
)
fastapi_query_rounding_places = Query(
    # ROUNDING_PLACES_DEFAULT,
    description=ROUNDING_PLACES_DESCRIPTION,
)
fastapi_query_analysis = Query(
    description=ANALYSIS_DESCRIPTION,
)
fastapi_query_statistics = Query(
    description=STATISTICS_DESCRIPTION,
)
fastapi_query_groupby = Query(
    description=GROUPBY_DESCRIPTION,
)
fastapi_query_csv = Query(
    description=CSV_DESCRIPTION,
)
fastapi_query_verbose = Query(
    # VERBOSE_LEVEL_DEFAULT,
    description=VERBOSE_LEVEL_DESCRIPTION,
)
fastapi_query_index = Query(
    description=INDEX_IN_TABLE_OUTPUT_FLAG_DESCRIPTION,
)
fastapi_query_quiet = Query(
    description=QUIET_FLAG_DESCRIPTION,
)
fastapi_query_log = Query(
    description=LOG_LEVEL_DESCRIPTION,
)
fastapi_query_fingerprint = Query(
    description=FINGERPRINT_DESCRIPTION,
)
fastapi_query_quick_response_code = Query(
    description=QUICK_RESPONSE_CODE_DESCRIPTION,
)
fastapi_query_command_metadata = Query(
    description=COMMAND_METADATA_DESCRIPTION,
)
fastapi_query_profiling = Query(
    description=cPROFILE_FLAG_DESCRIPTION,
)

fastapi_query_optimise_surface_position = Query(
    description=OPTIMISE_SURFACE_POSITION_DESCRIPTION,
)

fastapi_query_sampling_method_shgo = Query(
    description=SAMPLING_METHOD_DESCRIPTION,
)

fastapi_query_convert_timestamps = Query(
    description=TIMESTAMPS_DESCRIPTION,
    include_in_schema=False,
)

fastapi_query_timezone_to_be_converted = Query(
    description=TIMEZONE_DESCRIPTION,
    include_in_schema=False,
)
fastapi_query_global_horizontal_irradiance = Query(
    description=GLOBAL_HORIZONTAL_IRRADIANCE_DESCRIPTION,
    include_in_schema=False,
)
fastapi_query_direct_horizontal_irradiance = Query(
    description=DIRECT_HORIZONTAL_IRRADIANCE_DESCRIPTION,
    include_in_schema=False,
)
fastapi_query_temperature_series = Query(
    description=TEMPERATURE_TIME_SERIES_DESCRIPTION,
    include_in_schema=False,
)
fastapi_query_wind_speed_series = Query(
    description=WIND_SPEED_TIME_SERIES_DESCRIPTION,
    include_in_schema=False,
)
fastapi_query_spectral_effect_series = Query(
    description=SPECTRAL_EFFECT_DESCRIPTION,
    include_in_schema=False,
)
fastapi_query_solar_position_models = Query(
    description=POSITION_ALGORITHM_LIST_DESCRIPTION,
)
