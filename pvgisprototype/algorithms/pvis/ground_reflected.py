from math import cos
from zoneinfo import ZoneInfo
from devtools import debug
from numpy import nan, ndarray, array
from pandas import DatetimeIndex, Timestamp

from pvgisprototype import GroundReflectedIrradiance, LinkeTurbidityFactor
from pvgisprototype.api.irradiance.diffuse.horizontal import (
    calculate_diffuse_horizontal_irradiance_series,
)
from pvgisprototype.api.irradiance.direct.horizontal import (
    calculate_direct_horizontal_irradiance_series,
)
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    CLEAR_SKY_INDEX_MODELLING_NAME,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    PERIGEE_OFFSET,
    POSITION_ALGORITHM_COLUMN_NAME,
    RADIANS,
    REFLECTED_INCLINED_IRRADIANCE,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    TIME_ALGORITHM_COLUMN_NAME,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.arrays import create_array
from pvgisprototype.api.series.hardcodings import exclamation_mark


@log_function_call
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
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: float | None = ALBEDO_DEFAULT,
    global_horizontal_irradiance_series: ndarray | None = None,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
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
    position_algorithm = timing_algorithm = NOT_AVAILABLE
    irradiance_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": nan,
        "backend": array_backend,
    }
    direct_horizontal_irradiance_series = diffuse_horizontal_irradiance_series = (
        create_array(**irradiance_parameters)
    )
    if surface_tilt <= surface_tilt_threshold:  # No ground reflection for a flat or nearly flat surface
        flat_surface_array_parameters = {
            "shape": timestamps.shape,
            "dtype": dtype,
            "init_method": "zeros",
            "backend": array_backend,
        }  # Borrow shape from timestamps
        ground_reflected_inclined_irradiance_series = create_array(**flat_surface_array_parameters)
        global_horizontal_irradiance_series = create_array(**flat_surface_array_parameters)
        ground_view_fraction = 0
        data_source = None

    else:
        ground_view_fraction = (1 - cos(surface_tilt)) / 2
        data_source = 'External time series'
        if global_horizontal_irradiance_series is None:  # then model it !
            data_source = CLEAR_SKY_INDEX_MODELLING_NAME
            calculated_direct_horizontal_irradiance_series = (
                calculate_direct_horizontal_irradiance_series(
                    longitude=longitude,
                    latitude=latitude,
                    elevation=elevation,
                    timestamps=timestamps,
                    timezone=timezone,
                    linke_turbidity_factor_series=linke_turbidity_factor_series,
                    solar_time_model=solar_time_model,
                    solar_constant=solar_constant,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                    angle_output_units=angle_output_units,
                    dtype=dtype,
                    array_backend=array_backend,
                    verbose=verbose,
                    log=log,
                    fingerprint=fingerprint,
                )
            )
            direct_horizontal_irradiance_series = (
                calculated_direct_horizontal_irradiance_series.value
            )
            position_algorithm = getattr(
                calculated_direct_horizontal_irradiance_series.components,
                POSITION_ALGORITHM_COLUMN_NAME,
                NOT_AVAILABLE,
            )
            timing_algorithm = getattr(
                calculated_direct_horizontal_irradiance_series.components,
                TIME_ALGORITHM_COLUMN_NAME,
                NOT_AVAILABLE,
            )
            diffuse_horizontal_irradiance_series = (
                calculate_diffuse_horizontal_irradiance_series(
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    timezone=timezone,
                    linke_turbidity_factor_series=linke_turbidity_factor_series,
                    apply_atmospheric_refraction=apply_atmospheric_refraction,
                    refracted_solar_zenith=refracted_solar_zenith,
                    solar_position_model=solar_position_model,
                    solar_time_model=solar_time_model,
                    solar_constant=solar_constant,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                    angle_output_units=angle_output_units,
                    dtype=dtype,
                    array_backend=array_backend,
                    verbose=verbose,
                    log=log,
                    fingerprint=fingerprint,
                )
            ).value  # Important !
            global_horizontal_irradiance_series = (
                direct_horizontal_irradiance_series
                + diffuse_horizontal_irradiance_series
            )

    # --------------------------------------------------------------------

    # At this point, the global_horizontal_irradiance_series are either :
    # _read_ from external time series  Or  estimated from the solar
    # radiation model by Hofierka (2002)

    # clear-sky ground reflected irradiance
    ground_reflected_inclined_irradiance_series = (
        global_horizontal_irradiance_series * ground_view_fraction * albedo
    )

    if ground_reflected_inclined_irradiance_series.size == 1 and ground_reflected_inclined_irradiance_series.shape == ():
        ground_reflected_inclined_irradiance_series = array(
            [ground_reflected_inclined_irradiance_series], dtype=dtype
        )
        single_value = float(ground_reflected_inclined_irradiance_series)
        warning = (
            f"{exclamation_mark} The selected timestamp "
            + " matches the single value "
            + f"{single_value}"
        )
        logger.warning(warning)
    
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=ground_reflected_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return GroundReflectedIrradiance(
        value=ground_reflected_inclined_irradiance_series,
        unit=IRRADIANCE_UNIT,
        title=REFLECTED_INCLINED_IRRADIANCE,
        solar_radiation_model=HOFIERKA_2002,
        global_horizontal_irradiance=global_horizontal_irradiance_series,
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
        diffuse_horizontal_irradiance=diffuse_horizontal_irradiance_series,
        ground_view_fraction=ground_view_fraction,
        albedo=albedo,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        surface_tilt_threshold=surface_tilt_threshold,
        solar_positioning_algorithm=position_algorithm,
        solar_timing_algorithm=timing_algorithm,
        data_source=data_source,
    )
