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

import numpy
from devtools import debug
from numpy import errstate, ndarray, pi, sin, where
from pandas import DatetimeIndex

from pvgisprototype import (
    InclinedIrradiance,
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
    SolarIncidence,
    SolarAltitude,
    SolarAzimuth,
)
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.irradiance.direct.helpers import compare_temporal_resolution
from pvgisprototype.algorithms.pvis.direct.horizontal import calculate_direct_horizontal_irradiance_series_pvgis
from pvgisprototype.api.irradiance.reflectivity import (
    calculate_reflectivity_factor_for_direct_irradiance_series,
)

from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIRECT_INCLINED_IRRADIANCE,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LOG_LEVEL_DEFAULT,
    PERIGEE_OFFSET,
    RADIANS,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
def calculate_direct_inclined_irradiance_series_pvgis(
    elevation: float,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = str(now_utc_datetimezone()),
    timezone: ZoneInfo | None = None,
    direct_horizontal_irradiance: ndarray | Path | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,
    apply_reflectivity_factor: bool = True,
    solar_incidence_series: SolarIncidence | None = None,
    solar_altitude_series: SolarAltitude | None = None,
    solar_azimuth_series: SolarAzimuth | None = None,
    surface_in_shade_series: ndarray | None = None,
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
) -> InclinedIrradiance:
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
    # Create a sunlit surface time series mask
    # - solar altitude > 0
    # - surface not in shade
    # - solar incidence > 0
    mask_solar_altitude_positive = solar_altitude_series.radians > 0
    # Following, the _complementary_ solar incidence angle is used (Jenčo, 1992)!
    mask_solar_incidence_positive = solar_incidence_series.radians > 0
    mask_not_in_shade = ~surface_in_shade_series.value
    mask_sunlit_surface_series = numpy.logical_and.reduce(
        (mask_solar_altitude_positive, mask_solar_incidence_positive, mask_not_in_shade)
    )
    # Else, the following runs:
    # --------------------------------- Review & Add ?
    # 1. surface is shaded
    # 3. solar incidence = 0
    # --------------------------------- Review & Add ?
    # ========================================================================
    if direct_horizontal_irradiance is None:
        if verbose > 0:
            logger.info(
                ":information: Modelling direct horizontal irradiance...",
                alt=":information: [bold][magenta]Modelling[/magenta] direct horizontal irradiance[/bold]...",
            )
        direct_horizontal_irradiance_series = (
            calculate_direct_horizontal_irradiance_series_pvgis(
                elevation=elevation,
                timestamps=timestamps,
                timezone=timezone,
                solar_altitude_series=solar_altitude_series,
                surface_in_shade_series=surface_in_shade_series.value,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                fingerprint=fingerprint,
            ).value
        )
    else:
        direct_horizontal_irradiance_series = direct_horizontal_irradiance

    try:
        # the number of timestamps should match the number of "x" values
        if verbose > 0:
            logger.info(
                "\ni [bold]Calculating[/bold] the [magenta]direct inclined irradiance[/magenta] .."
            )
        compare_temporal_resolution(
            timestamps, direct_horizontal_irradiance_series
        )

        # Else, the following runs:
        # --------------------------------- Review & Add ?
        # 1. surface is shaded
        # 3. solar incidence = 0
        # --------------------------------- Review & Add ?
        # ========================================================================

        # Initialize the direct irradiance series to zeros
        # array_parameters = {
        #     "shape": timestamps.shape,
        #     "dtype": dtype,
        #     "init_method": "zeros",
        #     "backend": array_backend,
        # }  # Borrow shape from timestamps
        # direct_inclined_irradiance_series = create_array(**array_parameters)
        # if mask_sunlit_surface_series.any():
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
        logger.debug("Is the solar altitude angle zero ?")
        # should this return something? Like in r.sun's simpler's approach?
        raise ValueError

    if not apply_reflectivity_factor:
        direct_inclined_irradiance_before_reflectivity_series = None
        direct_irradiance_reflectivity_factor_series = None
    else:
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

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return InclinedIrradiance(
        value=direct_inclined_irradiance_series,
        unit=IRRADIANCE_UNIT,
        title=DIRECT_INCLINED_IRRADIANCE,
        solar_radiation_model=HOFIERKA_2002,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        solar_incidence=solar_incidence_series,
        solar_altitude=solar_altitude_series,
        solar_azimuth=solar_azimuth_series,
        surface_in_shade=surface_in_shade_series,
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
        values_before_reflectivity=direct_inclined_irradiance_before_reflectivity_series,
        reflectivity_factor=direct_irradiance_reflectivity_factor_series,
    )
