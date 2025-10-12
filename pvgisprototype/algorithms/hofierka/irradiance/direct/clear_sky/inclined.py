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

from zoneinfo import ZoneInfo

import numpy
from devtools import debug
from numpy import errstate, ndarray, pi, sin, where
from pandas import DatetimeIndex, Timestamp

from pvgisprototype import (
    DirectInclinedIrradiance,
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
    SolarIncidence,
    LocationShading,
    SolarAltitude,
)
from pvgisprototype.api.irradiance.direct.helpers import compare_temporal_resolution
from pvgisprototype.algorithms.hofierka.irradiance.direct.clear_sky.horizontal import calculate_clear_sky_direct_horizontal_irradiance_hofierka
from pvgisprototype.algorithms.martin_ruiz.reflectivity import (
    calculate_reflectivity_effect,
    calculate_reflectivity_factor_for_direct_irradiance_series,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_clear_sky_direct_inclined_irradiance_hofierka(
    elevation: float,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    #
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = ZoneInfo('UTC'),
    #
    direct_horizontal_irradiance: ndarray | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,
    apply_reflectivity_factor: bool = True,
    solar_incidence_series: SolarIncidence | None = None,
    solar_altitude_series: SolarAltitude | None = None,
    # solar_azimuth_series: SolarAzimuth | None = None,
    surface_in_shade_series: LocationShading | None = None,
    #
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    #
    # angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    #
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> DirectInclinedIrradiance:
    """Calculate the direct irradiance incident on a tilted surface [W*m-2].

    Calculate the direct irradiance on an inclined surface based on the
    solar radiation model by Hofierka, 2002. [1]_

    Parameters
    ----------
    elevation : float
        elevation
    surface_orientation : SurfaceOrientation | None
        surface_orientation
    surface_tilt : SurfaceTilt | None
        surface_tilt
    timestamps : DatetimeIndex | None
        timestamps
    timezone : ZoneInfo | None
        timezone
    direct_horizontal_irradiance : ndarray | None
        direct_horizontal_irradiance
    linke_turbidity_factor_series : LinkeTurbidityFactor
        linke_turbidity_factor_series
    apply_reflectivity_factor : bool
        apply_reflectivity_factor
    solar_incidence_series : SolarIncidence | None
        solar_incidence_series
    solar_altitude_series : SolarAltitude | None
        solar_altitude_series
    surface_in_shade_series : LocationShading | None
        surface_in_shade_series
    solar_constant : float
        solar_constant
    eccentricity_phase_offset : float
        eccentricity_phase_offset
    eccentricity_amplitude : float
        eccentricity_amplitude
    dtype : str
        dtype
    array_backend : str
        array_backend
    validate_output : bool
        validate_output
    verbose : int
        verbose
    log : int
        log

    Returns
    -------
    DirectInclinedIrradiance

    Notes
    -----
    In Hofierka (2002) [1]_, see equation 11 :

        Bic = B0c sin δexp

    or equation 12 :

              B   ⋅ sin ⎛δ   ⎞
               hc       ⎝ exp⎠         ⎛ W ⎞
        B   = ────────────────     in  ⎜───⎟
         ic       sin ⎛h ⎞             ⎜ -2⎟
                      ⎝ 0⎠             ⎝m  ⎠

    where :

    - δexp is the solar incidence angle measured between the sun and an
      inclined surface defined in equation 16

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
    if direct_horizontal_irradiance is not None:
        logger.error(
            "The `direct_horizontal_irradiance` should be None at this point !",
            alt = ":information: [bold red]The [code]direct_horizontal_irradiance[/code] input should be [code]None[/code] at this point ![/bold red]",
        )
        raise ValueError(
            ":information: The `direct_horizontal_irradiance` input should be None at this point !",
        )
    else:
        if verbose > 0:
            logger.debug(
                ":information: Modelling direct horizontal irradiance...",
                alt=":information: [bold][magenta]Modelling[/magenta] direct horizontal irradiance[/bold]...",
            )
        direct_horizontal_irradiance_series = (
            calculate_clear_sky_direct_horizontal_irradiance_hofierka(
                elevation=elevation,
                timestamps=timestamps,
                solar_altitude_series=solar_altitude_series,
                surface_in_shade_series=surface_in_shade_series,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                solar_constant=solar_constant,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
            )
        )
    try:
        # the number of timestamps should match the number of "x" values
        if verbose > 0:
            logger.debug(
                "\ni [bold]Calculating[/bold] the [magenta]direct inclined irradiance[/magenta] .."
            )
        compare_temporal_resolution(
            timestamps, direct_horizontal_irradiance_series.value
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
        direct_horizontal_irradiance_series.value
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
        direct_inclined_irradiance_reflectivity_factor_series = None

    else:
        # Calculate the reflectivity factor
        #
        # per Martin & Ruiz 2005 :
        # expects the _typical_ sun-vector-to-normal-of-surface incidence angles
        # which is the _complement_ of the incidence angle per Hofierka 2002
        direct_inclined_irradiance_reflectivity_factor_series = (
            calculate_reflectivity_factor_for_direct_irradiance_series(
                solar_incidence_series=(pi / 2 - solar_incidence_series.radians),
                verbose=0,
            )
        )

        # Apply the reflectivity factor
        direct_inclined_irradiance_series *= (
            direct_inclined_irradiance_reflectivity_factor_series
        )

        # Avoid copying to save memory and time ... ? ----------------- Is this safe ? -
        with errstate(divide="ignore", invalid="ignore"):
            # this quantity is exclusively generated for the output dictionary !
            direct_inclined_irradiance_before_reflectivity_series = where(
                direct_inclined_irradiance_reflectivity_factor_series != 0,
                direct_inclined_irradiance_series
                / direct_inclined_irradiance_reflectivity_factor_series,
                0,
            )
        # ------------------------------------------------------------------------------

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=direct_inclined_irradiance_series,
        shape=timestamps.shape,
        data_model=DirectInclinedIrradiance(),
    )

    if numpy.any(direct_inclined_irradiance_series < 0):
        logger.warning(
            "\n[red]Warning: Negative values found in `direct_inclined_irradiance_series`![/red]"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DirectInclinedIrradiance(
        value=direct_inclined_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        ## Irradiance components
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
        reflected = calculate_reflectivity_effect(
                irradiance=direct_inclined_irradiance_before_reflectivity_series,
                reflectivity_factor=direct_inclined_irradiance_reflectivity_factor_series,
            ),
        reflectivity_factor=direct_inclined_irradiance_reflectivity_factor_series,
        value_before_reflectivity=direct_inclined_irradiance_before_reflectivity_series,
        ## Location
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        #
        solar_positioning_algorithm=solar_incidence_series.solar_positioning_algorithm,
        solar_timing_algorithm=solar_incidence_series.solar_timing_algorithm,
        refracted_solar_altitude=direct_horizontal_irradiance_series.refracted_solar_altitude,
        solar_incidence_model=solar_incidence_series.algorithm,
        solar_incidence_definition=solar_incidence_series.definition,
        shading_algorithm=surface_in_shade_series.shading_algorithm,
        #
        surface_in_shade=surface_in_shade_series,
        solar_incidence=solar_incidence_series,
        solar_altitude=solar_altitude_series,
        # solar_azimuth=solar_azimuth_series,
        #
        linke_turbidity_factor=linke_turbidity_factor_series,
    )
