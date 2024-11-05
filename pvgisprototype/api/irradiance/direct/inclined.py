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
from numpy import sin, pi, errstate

import numpy
from devtools import debug
from numpy import where
from pandas import DatetimeIndex
from xarray import DataArray

from pvgisprototype import (
    Irradiance,
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.irradiance.direct.helpers import compare_temporal_resolution
from pvgisprototype.api.irradiance.direct.horizontal import (
    calculate_direct_horizontal_irradiance_series,
)
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.irradiance.reflectivity import (
    calculate_reflectivity_effect,
    calculate_reflectivity_effect_percentage,
    calculate_reflectivity_factor_for_direct_irradiance_series,
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
from pvgisprototype.api.series.select import select_time_series
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
    PERIGEE_OFFSET,
    PERIGEE_OFFSET_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_FACTOR_COLUMN_NAME,
    REFLECTIVITY_PERCENTAGE_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SHADE_COLUMN_NAME,
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
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.hashing import generate_hash


@log_function_call
@custom_cached
def calculate_direct_inclined_irradiance_series_pvgis(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = str(now_utc_datetimezone()),
    timezone: ZoneInfo | None = None,
    convert_longitude_360: bool = False,
    direct_horizontal_component: Path | None = None,
    neighbor_lookup: MethodForInexactMatches = None,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_reflectivity_factor: bool = True,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    # complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_height: DataArray = None,
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
        complementary_incidence_angle=True,  # True = between sun-vector and surface-plane !
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

    # ========================================================================
    # Essentially, perform calculations for when:
    # - solar altitude > 0
    # - not in shade
    # - solar incidence > 0
    #
    # To add : ---------------------------------------------------------------
    mask_solar_altitude_positive = solar_altitude_series.radians > 0

    # Following, the _complementary_ solar incidence angle is used (Jenčo, 1992)!
    mask_solar_incidence_positive = solar_incidence_series.radians > 0
    # ------------------------------------------------------------------------
    surface_in_shade_series = model_surface_in_shade_series(
        horizon_height=horizon_height,
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
    mask_not_in_shade = ~surface_in_shade_series.value
    mask = numpy.logical_and.reduce(
        (mask_solar_altitude_positive, mask_solar_incidence_positive, mask_not_in_shade)
    )
    # Else, the following runs:
    # --------------------------------- Review & Add ?
    # 1. surface is shaded
    # 3. solar incidence = 0
    # --------------------------------- Review & Add ?
    # ========================================================================

    if not direct_horizontal_component:
        if verbose > 0:
            logger.info(
                ":information: Modelling direct horizontal irradiance...",
                alt=":information: [bold][magenta]Modelling[/magenta] direct horizontal irradiance[/bold]..."
            )
        direct_horizontal_irradiance_series = (
            calculate_direct_horizontal_irradiance_series(
                longitude=longitude,  # required by some of the solar time algorithms
                latitude=latitude,
                elevation=elevation,
                timestamps=timestamps,
                timezone=timezone,
                solar_position_model=solar_position_model,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                dtype=dtype,
                array_backend=array_backend,
                verbose=0,  # no verbosity here by choice!
                log=log,
            ).value
        )  # Important
    else:  # read from a time series dataset
        if verbose > 0:
            logger.info(
                ":information: [bold]Reading[/bold] the [magenta]direct horizontal irradiance[/magenta] from [bold]external dataset[/bold]..."
            )
        direct_horizontal_irradiance_series = (
            select_time_series(
                time_series=direct_horizontal_component,
                # longitude=longitude_for_selection,
                # latitude=latitude_for_selection,
                longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                timestamps=timestamps,
                # convert_longitude_360=convert_longitude_360,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                verbose=0,  # no verbosity here by choice!
                log=log,
            )
            .to_numpy()
            .astype(dtype=dtype)
        )

    try:
        # the number of timestamps should match the number of "x" values
        if verbose > 0:
            logger.info(
                "\ni [bold]Calculating[/bold] the [magenta]direct inclined irradiance[/magenta] .."
            )
        compare_temporal_resolution(timestamps, direct_horizontal_irradiance_series)
        direct_inclined_irradiance_series = (
            direct_horizontal_irradiance_series
            * sin(
                solar_incidence_series.radians
            )  # Should be the _complementary_ incidence angle!
            / sin(solar_altitude_series.radians)
        )
    except ZeroDivisionError:
        logger.error(
            "Error: Division by zero in calculating the direct inclined irradiance!"
        )
        logger.debug("Is the solar altitude angle zero?")
        # should this return something? Like in r.sun's simpler's approach?
        raise ValueError

    if apply_reflectivity_factor:
        # per Martin & Ruiz 2005,
        # expects the _typical_ sun-vector-to-normal-of-surface incidence angles
        # which is the _complement_ of the incidence angle per Hofierka 2002
        direct_irradiance_reflectivity_factor_series = (
            calculate_reflectivity_factor_for_direct_irradiance_series(
                solar_incidence_series=(pi / 2 - solar_incidence_series.radians),
                verbose=0,
            )
        )
        direct_inclined_irradiance_series *= (
            direct_irradiance_reflectivity_factor_series
        )

        # --------------------------------------------------- Is this safe ? -
        with errstate(divide="ignore", invalid="ignore"):
            # this quantity is exclusively generated for the output dictionary !
            direct_inclined_irradiance_before_reflectivity_series = where(
                direct_irradiance_reflectivity_factor_series != 0,
                direct_inclined_irradiance_series
                / direct_irradiance_reflectivity_factor_series,
                0,
            )

    if numpy.any(direct_inclined_irradiance_series < 0):
        logger.info(
            "\n[red]Warning: Negative values found in `direct_inclined_irradiance_series`![/red]"
        )

    components_container = {
        "main": lambda: {
            TITLE_KEY_NAME: DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME,
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: (
                "External data" if direct_horizontal_component else HOFIERKA_2002
            ),
        },
        "extended_2": lambda: (
            {
                REFLECTIVITY_COLUMN_NAME: calculate_reflectivity_effect(
                    irradiance=direct_inclined_irradiance_before_reflectivity_series,
                    reflectivity=direct_irradiance_reflectivity_factor_series,
                ),
                REFLECTIVITY_PERCENTAGE_COLUMN_NAME: calculate_reflectivity_effect_percentage(
                    irradiance=direct_inclined_irradiance_before_reflectivity_series,
                    reflectivity=direct_irradiance_reflectivity_factor_series,
                ),
            }
            if verbose > 6 and apply_reflectivity_factor
            else {}
        ),
        "extended": lambda: (
            {
                REFLECTIVITY_FACTOR_COLUMN_NAME: direct_irradiance_reflectivity_factor_series,
                DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: direct_inclined_irradiance_before_reflectivity_series,
                # } if verbose > 1 and apply_reflectivity_factor else {},
            }
            if apply_reflectivity_factor
            else {}
        ),
        "more_extended": lambda: (
            {
                SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_orientation, angle_output_units
                ),
                SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_tilt, angle_output_units
                ),
                ANGLE_UNITS_COLUMN_NAME: angle_output_units,
                SHADE_COLUMN_NAME: surface_in_shade_series.value,
                SHADING_ALGORITHM_COLUMN_NAME: surface_in_shade_series.shading_algorithm,
            }
            if verbose > 2
            else {}
        ),
        "even_more_extended": lambda: (
            {
                TITLE_KEY_NAME: DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
                + " & relevant components",
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
                # "Shade": in_shade,
            }
            if verbose > 3
            else {}
        ),
        "and_even_more_extended": lambda: (
            {
                INCIDENCE_COLUMN_NAME: getattr(
                    solar_incidence_series, angle_output_units
                ),
                INCIDENCE_ALGORITHM_COLUMN_NAME: solar_incidence_model.value,
                INCIDENCE_DEFINITION: solar_incidence_series.definition,  # Review Me ! Report the _complementary_ incidence angle series ?
                AZIMUTH_COLUMN_NAME: getattr(solar_azimuth_series, angle_output_units),
                ALTITUDE_COLUMN_NAME: getattr(
                    solar_altitude_series, angle_output_units
                ),
            }
            if verbose > 4
            else {}
        ),
        "extra": lambda: (
            {
                POSITION_ALGORITHM_COLUMN_NAME: solar_position_model.value,
                TIME_ALGORITHM_COLUMN_NAME: solar_time_model.value,
                SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
                PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
                ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
            }
            if verbose > 5
            else {}
        ),
        "fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    direct_inclined_irradiance_series
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
        data=direct_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=direct_inclined_irradiance_series,
        unit=IRRADIANCE_UNIT,
        position_algorithm="",
        timing_algorithm="",
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        components=components,
    )
