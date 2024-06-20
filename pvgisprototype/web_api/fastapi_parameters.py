from fastapi import Query

from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.constants import (
    ELEVATION_MAXIMUM,
    ELEVATION_MINIMUM,
    LATITUDE_MAXIMUM,
    LATITUDE_MINIMUM,
    LONGITUDE_MAXIMUM,
    LONGITUDE_MINIMUM,
    RADIATION_CUTOFF_THRESHHOLD,
    SURFACE_ORIENTATION_MAXIMUM,
    SURFACE_ORIENTATION_MINIMUM,
    SURFACE_TILT_MAXIMUM,
    SURFACE_TILT_MINIMUM,
    TOLERANCE_MINIMUM,
)
from pvgisprototype.web_api.descriptions import (
    albedo_description,
    analysis_description,
    angle_output_units_description,
    apply_reflectivity_factor_description,
    atmospheric_refraction_description,
    command_metadata_description,
    csv_description,
    direct_horizontal_irradiance_description,
    eccentricity_correction_description,
    efficiency_description,
    elevation_description,
    end_time_description,
    fingerprint_description,
    frequency_description,
    global_horizontal_irradiance_description,
    groupby_description,
    hour_offset_description,
    in_memory_description,
    index_description,
    latitude_description,
    linke_turbidity_description,
    local_time_description,
    log_description,
    longitude_description,
    mask_and_scale_description,
    module_temperature_algorithm_description,
    nearest_neighbor_lookup_description,
    peak_power_description,
    perigee_offset_description,
    periods_description,
    photovoltaic_module_description,
    power_model_description,
    profiling_description,
    qr_description,
    quite_description,
    radiation_cutoff_threshold_description,
    random_day_description,
    random_days_description,
    random_time_description,
    rounding_places_description,
    solar_constant_description,
    solar_incidence_description,
    solar_position_description,
    solar_time_description,
    solar_zenith_description,
    start_time_description,
    statistics_description,
    surface_orientation_description,
    surface_tilt_description,
    system_efficiency_description,
    temperature_series_description,
    terminal_width_description,
    time_offset_global_description,
    time_series_description,
    timestamp_description,
    timestamps_description,
    timezone_description,
    tolerance_description,
    uniplot_description,
    verbose_description,
    wind_speed_series_description,
    zero_negative_solar_incidence_angle_description,
)

fastapi_query_longitude = Query(
    title="Longitude",
    description=longitude_description,
    ge=LONGITUDE_MINIMUM,
    le=LONGITUDE_MAXIMUM,
)
fastapi_query_longitude_in_degrees = Query(
    ...,
    title="Longitude",
    description=longitude_description,
    ge=LONGITUDE_MINIMUM,
    le=LONGITUDE_MAXIMUM,
)
fastapi_query_latitude = Query(
    ...,
    title="Latitude",
    description=latitude_description,
    ge=LATITUDE_MINIMUM,
    le=LATITUDE_MAXIMUM,
)
fastapi_query_latitude_in_degrees = Query(
    ...,
    title="Latitude",
    description=latitude_description,
    ge=LATITUDE_MINIMUM,
    le=LATITUDE_MAXIMUM,
)
fastapi_query_elevation = Query(
    ...,
    title="Elevation",
    description=elevation_description,
    ge=ELEVATION_MINIMUM,
    le=ELEVATION_MAXIMUM,
)
fastapi_query_timestamp = Query(
    default_factory=now_utc_datetimezone,
    description=timestamp_description,
    # Depends(ctx_attach_requested_timezone)
)
fastapi_query_timestamps = Query(
    description=timestamps_description,
    # Depends(parse_timestamp_series)
)
fastapi_query_start_time = Query(
    description=start_time_description,
)
fastapi_query_periods = Query(
    description=periods_description,
)
fastapi_query_frequency = Query(
    description=frequency_description,
)
fastapi_query_end_time = Query(
    description=end_time_description,
)
fastapi_query_timezone = Query(
    description=timezone_description,
    # Depends on ctx_convert_to_timezone
)
fastapi_query_local_time = Query(
    description=local_time_description,
    # Depends on now_local_datetimezone
)
fastapi_query_random_time = Query(
    description=random_time_description,
)
fastapi_query_random_time_series = Query(
    description=random_time_description,
)
fastapi_query_random_day = Query(
    description=random_day_description,
)
fastapi_query_random_days = Query(
    description=random_days_description,
)
fastapi_query_time_series_query = Query(
    description=time_series_description,
)
fastapi_query_mask_and_scale = Query(
    description=mask_and_scale_description,
)
fastapi_query_neighbor_lookup = Query(
    description=nearest_neighbor_lookup_description,
)
fastapi_query_tolerance = Query(
    description=tolerance_description,
    ge=TOLERANCE_MINIMUM,
)
fastapi_query_in_memory = Query(
    # False,
    description=in_memory_description,
)
fastapi_query_surface_tilt = Query(
    # SURFACE_TILT_DEFAULT,
    description=surface_tilt_description,
    ge=SURFACE_TILT_MINIMUM,
    le=SURFACE_TILT_MAXIMUM,
)
fastapi_query_surface_orientation = Query(
    # SURFACE_ORIENTATION_DEFAULT,
    description=surface_orientation_description,
    ge=SURFACE_ORIENTATION_MINIMUM,
    le=SURFACE_ORIENTATION_MAXIMUM,
)
fastapi_query_linke_turbidity_factor_series = Query(
    # LINKE_TURBIDITY_DEFAULT,
    description=linke_turbidity_description,
)
fastapi_query_apply_atmospheric_refraction = Query(
    # True,
    description=atmospheric_refraction_description,
)
fastapi_query_refracted_solar_zenith = Query(
    # REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    description=solar_zenith_description,
)
fastapi_query_albedo = Query(
    # 2,
    description=albedo_description,
)
fastapi_query_apply_reflectivity_factor = Query(
    # True,
    description=apply_reflectivity_factor_description,
)
fastapi_query_solar_position_model = Query(
    # SOLAR_POSITION_ALGORITHM_DEFAULT,
    description=solar_position_description,
)
fastapi_query_solar_incidence_model = Query(
    # SolarIncidenceModel.jenco,
    description=solar_incidence_description,
)
fastapi_query_solar_time_model = Query(
    # SOLAR_TIME_ALGORITHM_DEFAULT,
    description=solar_time_description,
)
fastapi_query_time_offset_global = Query(
    # 0,
    description=time_offset_global_description,
)
fastapi_query_hour_offset = Query(
    # 0,
    description=hour_offset_description,
)
fastapi_query_solar_constant = Query(
    # SOLAR_CONSTANT,
    description=solar_constant_description,
)
fastapi_query_perigee_offset = Query(
    # PERIGEE_OFFSET,
    description=perigee_offset_description,
)
fastapi_query_eccentricity_correction_factor = Query(
    # ECCENTRICITY_CORRECTION_FACTOR,
    description=eccentricity_correction_description,
)
fastapi_query_system_efficiency = Query(
    # SYSTEM_EFFICIENCY_DEFAULT,
    description=system_efficiency_description,
    ge=0.0,  # FIXME ADD VALUES TO CONSTANTS
    le=1.0,  # FIXME ADD VALUES TO CONSTANTS
)
fastapi_query_power_model = Query(
    # None,
    description=power_model_description,
)
fastapi_query_efficiency = Query(
    # None,
    description=efficiency_description,
    ge=0.0,  # FIXME ADD VALUES TO CONSTANTS
    le=1.0,  # FIXME ADD VALUES TO CONSTANTS
)
fastapi_query_rounding_places = Query(
    # 5,
    description=rounding_places_description,
)
fastapi_query_verbose = Query(
    # VERBOSE_LEVEL_DEFAULT,
    description=verbose_description,
)
fastapi_query_log = Query(
    description=log_description,
)
fastapi_query_fingerprint = Query(
    description=fingerprint_description,
)
fastapi_query_module_temperature_algorithm = Query(
    description=module_temperature_algorithm_description,
)
fastapi_query_photovoltaic_module_model = Query(
    description=photovoltaic_module_description,
)
fastapi_query_temperature_series = Query(
    description=temperature_series_description,
)
fastapi_query_wind_speed_series = Query(
    description=wind_speed_series_description,
)
fastapi_query_csv = Query(
    description=csv_description,
)
fastapi_query_global_horizontal_irradiance = Query(
    description=global_horizontal_irradiance_description,
)
fastapi_query_direct_horizontal_irradiance = Query(
    description=direct_horizontal_irradiance_description,
)
fastapi_query_statistics = Query(
    description=statistics_description,
)
fastapi_query_groupby = Query(
    description=groupby_description,
)
fastapi_query_uniplot = Query(
    description=uniplot_description,
)
fastapi_query_uniplot_terminal_width = Query(
    description=terminal_width_description,
)
fastapi_query_index = Query(
    description=index_description,
)
fastapi_query_quiet = Query(
    description=quite_description,
)
fastapi_query_analysis = Query(
    description=analysis_description,
)
fastapi_query_command_metadata = Query(
    description=command_metadata_description,
)
fastapi_query_profiling = Query(
    description=profiling_description,
)
fastapi_query_surface_orientation_list = Query(
    description=surface_orientation_description,
)
fastapi_query_surface_tilt_list = Query(
    description=surface_tilt_description,
)
fastapi_query_zero_negative_solar_incidence_angle = Query(
    description=zero_negative_solar_incidence_angle_description,
)
fastapi_query_angle_output_units = Query(
    description=angle_output_units_description,
)
fastapi_query_peak_power = Query(
    description=peak_power_description,
    ge=0.0,  # FIXME ADD VALUES TO CONSTANTS
)
fastapi_query_radiation_cutoff_threshold = Query(
    description=radiation_cutoff_threshold_description,
    ge=RADIATION_CUTOFF_THRESHHOLD,
)
fastapi_query_qr = Query(
    description=qr_description,
)
