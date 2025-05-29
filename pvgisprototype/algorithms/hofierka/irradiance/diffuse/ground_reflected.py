from math import cos
from zoneinfo import ZoneInfo
from devtools import debug
from numpy import nan, ndarray, asarray, array
from pandas import DatetimeIndex, Timestamp

from pvgisprototype import (
    DirectHorizontalIrradiance,
    DiffuseSkyReflectedHorizontalIrradiance,
    GroundReflectedInclinedIrradiance,
    LinkeTurbidityFactor,
)
from pvgisprototype.api.irradiance.diffuse.clear_sky.horizontal import (
    calculate_clear_sky_diffuse_horizontal_irradiance,
)
from pvgisprototype.api.irradiance.direct.horizontal import (
    calculate_direct_horizontal_irradiance_series,
)
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    PERIGEE_OFFSET,
    # UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_ground_reflected_inclined_irradiance_series_pvgis(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = ZoneInfo('UTC'),
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_tilt_threshold = SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: float | None = ALBEDO_DEFAULT,
    global_horizontal_irradiance: ndarray | None = None,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    # angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """Calculate the clear-sky diffuse ground reflected irradiance on an inclined surface (Ri).

    The calculation relies on an isotropic assumption. The ground reflected
    clear-sky irradiance received on an inclined surface [W.m-2] is
    proportional to the global horizontal irradiance Ghc, to the mean ground
    albedo ρg and a fraction of the ground viewed by an inclined surface
    rg(γN).

    """
    # in order to avoid 'NameError's
    irradiance_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": nan,
        "backend": array_backend,
    }
    flat_surface_array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps
    empty_array = create_array(**irradiance_parameters)
    direct_horizontal_irradiance_series = DirectHorizontalIrradiance(value=empty_array)
    diffuse_horizontal_irradiance_series = DiffuseSkyReflectedHorizontalIrradiance(value=empty_array)
    global_horizontal_irradiance_series = create_array(**flat_surface_array_parameters)

    if surface_tilt <= surface_tilt_threshold:  # No ground reflection for a flat or nearly flat surface
       # ground_reflected_inclined_irradiance_series = create_array(**flat_surface_array_parameters)
        ground_view_fraction = 0

    else:
        ground_view_fraction = (1 - cos(surface_tilt)) / 2
        # if not read from external time series,
        # calculate the clear-sky direct & diffuse sky-reflected components
        if global_horizontal_irradiance is None:  # then model it !
            direct_horizontal_irradiance_series = (
                calculate_direct_horizontal_irradiance_series(
                    longitude=longitude,
                    latitude=latitude,
                    elevation=elevation,
                    timestamps=timestamps,
                    timezone=timezone,
                    linke_turbidity_factor_series=linke_turbidity_factor_series,
                    solar_time_model=solar_time_model,
                    solar_constant=solar_constant,
                    eccentricity_phase_offset=eccentricity_phase_offset,
                    eccentricity_amplitude=eccentricity_amplitude,
                    # angle_output_units=angle_output_units,
                    dtype=dtype,
                    array_backend=array_backend,
                    verbose=verbose,
                    log=log,
                    fingerprint=fingerprint,
                )
            )
            diffuse_horizontal_irradiance_series = (
                calculate_clear_sky_diffuse_horizontal_irradiance(
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    timezone=timezone,
                    linke_turbidity_factor_series=linke_turbidity_factor_series,
                    adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                    # unrefracted_solar_zenith=unrefracted_solar_zenith,
                    solar_position_model=solar_position_model,
                    solar_time_model=solar_time_model,
                    solar_constant=solar_constant,
                    eccentricity_phase_offset=eccentricity_phase_offset,
                    eccentricity_amplitude=eccentricity_amplitude,
                    # angle_output_units=angle_output_units,
                    dtype=dtype,
                    array_backend=array_backend,
                    verbose=verbose,
                    log=log,
                    fingerprint=fingerprint,
                )
            )
            global_horizontal_irradiance_series = (
                direct_horizontal_irradiance_series.value
                + diffuse_horizontal_irradiance_series.value
            )

    # --------------------------------------------------------------------

    # At this point, the global_horizontal_irradiance_series is either :
    # _read_ from external time series  Or  estimated from the solar
    # radiation model by Hofierka (2002)

    # clear-sky ground-diffuse inclined irradiance
    ground_reflected_inclined_irradiance_series = asarray(
        global_horizontal_irradiance_series * ground_view_fraction * albedo,
        dtype=dtype
    )
    ground_reflected_inclined_irradiance_series = array(
        ground_reflected_inclined_irradiance_series, ndmin=1
    )

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=ground_reflected_inclined_irradiance_series,
        shape=timestamps.shape,
        data_model=GroundReflectedInclinedIrradiance(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=ground_reflected_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return GroundReflectedInclinedIrradiance(
        value=ground_reflected_inclined_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        #
        ground_view_fraction=ground_view_fraction,
        albedo=albedo,
        #
        global_horizontal_irradiance=global_horizontal_irradiance_series,
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
        diffuse_horizontal_irradiance=diffuse_horizontal_irradiance_series,
        #
        location=(longitude, latitude),
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        surface_tilt_threshold=surface_tilt_threshold,
        solar_positioning_algorithm=diffuse_horizontal_irradiance_series.solar_positioning_algorithm,
        solar_timing_algorithm=diffuse_horizontal_irradiance_series.solar_timing_algorithm,
        # angle_output_units=angle_output_units,
    )
