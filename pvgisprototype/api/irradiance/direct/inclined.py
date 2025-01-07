"""
This Python module is part of PVGIS' API. It implements functions to calculate
the direct solar irradiance.

_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""

from pathlib import Path
from zoneinfo import ZoneInfo

from devtools import debug
from numpy import ndarray
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray

from pvgisprototype import (
    Irradiance,
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.algorithms.pvis.direct.inclined import calculate_direct_inclined_irradiance_series_pvgis
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.irradiance.reflectivity import (
    calculate_reflectivity_effect,
    calculate_reflectivity_effect_percentage,
)

# from pvgisprototype.api.irradiance.shade import is_surface_in_shade_series
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.azimuth import model_solar_azimuth_series
from pvgisprototype.api.position.incidence import model_solar_incidence_series
from pvgisprototype.api.position.models import (
    SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.position.shading import model_surface_in_shade_series
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ANGLE_UNITS_COLUMN_NAME,
    ARRAY_BACKEND_DEFAULT,
    AZIMUTH_COLUMN_NAME,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DEGREES,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE,
    DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_DEFINITION,
    IRRADIANCE_UNIT,
    LOG_LEVEL_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    PERIGEE_OFFSET,
    PERIGEE_OFFSET_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_FACTOR_COLUMN_NAME,
    REFLECTIVITY_PERCENTAGE_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SURFACE_IN_SHADE_COLUMN_NAME,
    SHADING_ALGORITHM_COLUMN_NAME,
    SOLAR_CONSTANT,
    SOLAR_CONSTANT_COLUMN_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_DEFAULT,
    TIME_ALGORITHM_COLUMN_NAME,
    TITLE_KEY_NAME,
    TOLERANCE_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.core.hashing import generate_hash
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
def calculate_direct_inclined_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = str(now_utc_datetimezone()),
    timezone: ZoneInfo | None = None,
    # convert_longitude_360: bool = False,
    direct_horizontal_irradiance: ndarray | None = None,
    # neighbor_lookup: MethodForInexactMatches | None = NEIGHBOR_LOOKUP_DEFAULT,
    # tolerance: float | None = TOLERANCE_DEFAULT,
    # mask_and_scale: bool = False,
    # in_memory: bool = False,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: (
        float | None
    ) = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_reflectivity_factor: bool = True,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    # complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> Irradiance:
    """Calculate the direct irradiance incident on a tilted surface [W*m-2].

    Calculate the direct irradiance on an inclined surface based on the
    solar radiation model by Hofierka, 2002. [1]_

    Notes
    -----
    Bic = B0c sin δexp (equation 11)

    or

          B   ⋅ sin ⎛δ   ⎞
           hc       ⎝ exp⎠         ⎛ W ⎞
    B   = ────────────────     in  ⎜───⎟
     ic       sin ⎛h ⎞             ⎜ -2⎟
                  ⎝ 0⎠             ⎝m  ⎠

        (equation 12)

    where :

    - δexp is the solar incidence angle measured between the sun and an
      inclined surface defined in equation (16).

    or else :

        Direct Inclined = Direct Horizontal * sin( Solar Incidence ) / sin( Solar Altitude )

    The implementation by Hofierka (2002) uses the solar incidence angle
    between the sun-vector and the plane of the reference surface (as per Jenčo,
    1992). This is very important and relates to the hardcoded value `True` for
    the `complementary_incidence_angle` input parameter of the function. We
    call this angle (definition) the _complementary_ incidence angle.

    For the losses due to reflectivity, the incidence angle modifier by Martin
    & Ruiz (2005) expects the incidence angle between the sun-vector and the
    surface-normal. Hence, the respective call of the function
    `calculate_reflectivity_factor_for_direct_irradiance_series()`,
    expects the complement of the angle defined by Jenčo (1992). We call the
    incidence angle expected by the incidence angle modifier by Martin & Ruiz
    (2005) the _typical_ incidence angle.

    See also the documentation of the function
    `calculate_solar_incidence_series_jenco()`.

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    solar_incidence_series = model_solar_incidence_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_incidence_model=solar_incidence_model,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        complementary_incidence_angle=True,  # = Sun-vector To Surface-plane (Jenčo, 1992) !
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        # refracted_solar_zenith=refracted_solar_zenith,
        # solar_time_model=solar_time_model,
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    solar_azimuth_series = model_solar_azimuth_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        # solar_time_model=solar_time_model,
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    surface_in_shade_series = model_surface_in_shade_series(
        horizon_profile=horizon_profile,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_time_model=solar_time_model,
        solar_position_model=solar_position_model,
        shading_model=shading_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
    # elif isinstance(
    #     direct_horizontal_component, ndarray
    #     ):  # NOTE : Here the direct horizontal irradiance is already read as numpy array. Probably include other data structures here?
    #     if verbose > 0:
    #         logger.info(
    #             ":information: Direct horizontal irradiance is already a numpy array...",
    #             alt=":information: [bold] Direct horizontal irradiance is already a [magenta]numpy array[/magenta][/bold]...",
    #         )
    #     direct_horizontal_irradiance_series = direct_horizontal_irradiance


    direct_inclined_irradiance_series = (
        calculate_direct_inclined_irradiance_series_pvgis(
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            timestamps=timestamps,
            timezone=timezone,
            direct_horizontal_irradiance=direct_horizontal_irradiance,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            apply_reflectivity_factor=apply_reflectivity_factor,
            solar_incidence_series=solar_incidence_series,
            solar_altitude_series=solar_altitude_series,
            solar_azimuth_series=solar_azimuth_series,
            surface_in_shade_series=surface_in_shade_series,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            angle_output_units=angle_output_units,
            dtype=dtype,
            array_backend=array_backend,
            validate_output=validate_output,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )
    )

    components_container = {
        DIRECT_INCLINED_IRRADIANCE: lambda: {
            TITLE_KEY_NAME: DIRECT_INCLINED_IRRADIANCE,
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series.value,
            RADIATION_MODEL_COLUMN_NAME: (
                "External data"
                if (direct_horizontal_irradiance is not None)
                else HOFIERKA_2002  # NOTE If it is not a None type
            ),
        },
        "Reflectivity effect": lambda: (
            {
                REFLECTIVITY_COLUMN_NAME: calculate_reflectivity_effect(
                    irradiance=direct_inclined_irradiance_series.values_before_reflectivity,
                    reflectivity=direct_inclined_irradiance_series.reflectivity_factor,
                ),
                REFLECTIVITY_PERCENTAGE_COLUMN_NAME: calculate_reflectivity_effect_percentage(
                    irradiance=direct_inclined_irradiance_series.values_before_reflectivity,
                    reflectivity=direct_inclined_irradiance_series.reflectivity_factor,
                ),
            }
            if verbose > 6 and apply_reflectivity_factor
            else {}
        ),
        "Reflectivity factor": lambda: (
            {
                REFLECTIVITY_FACTOR_COLUMN_NAME: direct_inclined_irradiance_series.reflectivity_factor,
                DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: direct_inclined_irradiance_series.values_before_reflectivity,
                # } if verbose > 1 and apply_reflectivity_factor else {},
            }
            if apply_reflectivity_factor
            else {}
        ),
        "Surface position": lambda: (
            {
                SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_orientation, angle_output_units
                ),
                SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_tilt, angle_output_units
                ),
                ANGLE_UNITS_COLUMN_NAME: angle_output_units,
                SURFACE_IN_SHADE_COLUMN_NAME: surface_in_shade_series.value,
                SHADING_ALGORITHM_COLUMN_NAME: surface_in_shade_series.shading_algorithm,
            }
            if verbose > 2
            else {}
        ),
        "Irradiance metadata": lambda: (
            {
                TITLE_KEY_NAME: DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
                + " & relevant components",
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series.direct_horizontal_irradiance,
                # "Shade": in_shade,
            }
            if verbose > 3
            else {}
        ),
        "Solar position": lambda: (
            {
                INCIDENCE_COLUMN_NAME: getattr(
                    solar_incidence_series, angle_output_units
                ),
                AZIMUTH_COLUMN_NAME: getattr(solar_azimuth_series, angle_output_units),
                ALTITUDE_COLUMN_NAME: getattr(
                    solar_altitude_series, angle_output_units
                ),
            }
            if verbose > 4
            else {}
        ),
        "Solar position metadata": lambda: (
            {
                INCIDENCE_ALGORITHM_COLUMN_NAME: solar_incidence_model.value,
                INCIDENCE_DEFINITION: solar_incidence_series.definition,  # Review Me ! Report the _complementary_ incidence angle series ?
                POSITION_ALGORITHM_COLUMN_NAME: solar_position_model.value,
                TIME_ALGORITHM_COLUMN_NAME: solar_time_model.value,
                SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
                PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
                ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
            }
            # if verbose > 5
            # else {}
        ),
        "Fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    direct_inclined_irradiance_series.value
                ),
            }
            if fingerprint
            else {}
        ),
    }

    components = {}
    for _, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_inclined_irradiance_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=direct_inclined_irradiance_series.value,
        unit=IRRADIANCE_UNIT,
        position_algorithm=solar_altitude_series.position_algorithm,
        timing_algorithm=solar_altitude_series.timing_algorithm,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        components=components,
    )
