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
Calculate the solar incidence angle for a surface that is tilted to any
horizontal and vertical angle, as described by Iqbal [0].

[0] Iqbal, M. “An Introduction to Solar Radiation”. New York: 1983; pp. 23-25.
"""

from math import cos, pi, sin
from typing import List
from zoneinfo import ZoneInfo

import numpy
from devtools import debug
from pandas import DatetimeIndex
from pydantic_numpy import NpNDArray

from pvgisprototype import (
    Latitude,
    Longitude,
    SolarAzimuth,
    SolarIncidence,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.algorithms.noaa.solar_azimuth import (
    calculate_solar_azimuth_series_noaa,
)
from pvgisprototype.algorithms.noaa.solar_zenith import (
    calculate_solar_zenith_series_noaa,
)
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.position.models import (
    SUN_HORIZON_POSITION_DEFAULT,
    SunHorizonPositionModel,
    SolarIncidenceModel,
    select_models,
)
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    NO_SOLAR_INCIDENCE,
    RADIANS,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
def calculate_solar_incidence_series_iqbal(
    longitude: Longitude,
    latitude: Latitude,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = now_utc_datetimezone(),
    timezone: ZoneInfo | None = None,
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    surface_in_shade_series: NpNDArray | None = None,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> SolarIncidence:
    """Calculate the solar incidence angle for a surface oriented in any
    direction.

    Calculate the solar incidence angle between the sun position unit vector
    and the surface normal unit vector for a surface oriented in any direction;
    in other words, the cosine of the angle of incidence. Optionally, the
    output may be the complementary incidence angle between the sun-to-surface
    vector and the surface plane.

    Notes
    -----

    The equation for the incidence angle `I` by Iqbal (1983) [0]_ [1]_

        I = Arc cos( cos(θ) * cos(ω) + sin(ω) * sin(θ) * (Γ - γ) )

    where :

    - θ is the solar zenith angle
    - ω is the surface tilt angle
    - Γ is the astronomers topocentric azimuth angle
    - γ is the navigators topocentric azimuth angle

    Important observations are :

    - The topocentric astronomers azimuth angle `Γ` which is measured _westward
      from south_.

    - The surface orientation angle `γ` (also referred to as surface azimuth
      rotation angle) is measured from south to the projection of the surface
      normal on the horizontal plane, positive or negative if oriented west or
      east from south, respectively.

    - The topocentric azimuth angle `Φ` for navigators and solar radiation
      users (equation 46, p. 588) is measured _eastward from north_ and thus
      equals the astronomers one plus π or else 180 degrees :

       Φ = Γ + 180

       and thus

       Γ = Φ - 180    [*]

    In equation I, the surface orientation angle `γ` measured from south, is
    subtracted from the astronomers topocentric azimuth angle which is likewise
    measured from south. Given that most applications measure azimuthal angles
    from North, care must be taken to feed the correct "version" of these
    angles in this function.

    PVGIS measures the user-requested azimuthal angles Solar Azimuth (follownig
    denoted also with Φ) and the "solar radiation"-relevant Surface Orientation
    from North (follownig denoted as `γΝ`). Equation I based on [*] becomes
    relevant for PVGIS in the following form :

        I = Arc cos( cos(θ) * cos(ω) + sin(ω) * sin(θ) * (Φ - 180 - γN - 180) )

        or else

        cosine_solar_incidence_series = (
            numpy.cos(solar_zenith_series.radians)
            * cos(surface_tilt.radians)
            + sin(surface_tilt.radians)
            * numpy.sin(solar_zenith_series.radians)
            * numpy.cos(solar_azimuth_series.radians -
            surface_orientation.radians - 2 * pi)
        )

    Nonetheless, and for the sake of consistency with the author's original
    definition, such conversion are preferrable to be performed in advance and
    outside the scope of the current function, for both the solar azimuth and
    the surface orientation angles. Therefore the internal form of the equation
    uses as per its definition the astronomers topocentric solar azimuth angle
    and the surface azimuth rotation angle measured from south -- see also
    source code of this function.

    References
    ----------
    .. [0] Iqbal, 1983

    .. [1] Equation 47, p. 588),

    Parameters
    ----------
    longitude : Longitude
    latitude : Latitude
    timestamps : DatetimeIndex
    timezone : ZoneInfo
    surface_orientation : SurfaceOrientation
        Panel azimuth from north.
    surface_tilt : SurfaceTilt
        Panel tilt from horizontal.
    adjust_for_atmospheric_refraction : bool
    complementary_incidence_angle : bool
    zero_negative_solar_incidence_angle : bool
    dtype : str
    array_backend : str
    verbose : int
    log : int

    Returns
    -------
    solar_incidence_series : SolarIncidence
        A times series of solar incidence angles between the sun position
        vector and the surface normal (or plane)

    Notes
    -----
    Notes from the original pvlib function :

    - Usage note: When the sun is behind the surface the value returned is
      negative.  For many uses negative values must be set to zero.

    - Input all angles in degrees.

    References
    ----------
    .. [0] Iqbal, M. “An Introduction to Solar Radiation”. New York: 1983; pp. 23-25.

    """
    solar_zenith_series = calculate_solar_zenith_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
    solar_azimuth_series_north_based = calculate_solar_azimuth_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
        validate_output=validate_output,
    )  # North = 0 according to NOAA's solar geometry equations

    # array_parameters = {
    #     "shape": timestamps.shape,
    #     "dtype": dtype,
    #     "init_method": "empty",
    #     "backend": array_backend,
    # }  # Borrow shape from timestamps
    # solar_incidence_series = create_array(**array_parameters)

    # Convert to south-based
    solar_azimuth_series = SolarAzimuth(
        value=(solar_azimuth_series_north_based.radians - pi),
        unit=RADIANS,
    )
    # Φimit Φ to the range from 0° to 360°.
    # Divide Φ by 360, record the decimal fraction of the division as F.
    # Divide phi by 360 and get the remainder and the fractional part
    fraction_series, _ = numpy.modf(solar_azimuth_series.radians / (2 * pi))

    # If Φ is positive, then the limited Φ = 360 * F .
    # If Φ is negative, then the limited Φ = 360 - 360 *F.

    # Remember all of the metadata ! Review-Me & Abstract-Me !
    solar_azimuth_series = SolarAzimuth(
        value=numpy.where(
            solar_azimuth_series.radians >= 0,
            2 * pi * fraction_series,
            2 * pi - (2 * pi * numpy.abs(fraction_series)),
        ),
        unit=RADIANS,
        solar_positioning_algorithm=solar_azimuth_series_north_based.solar_positioning_algorithm,
        solar_timing_algorithm=solar_azimuth_series_north_based.solar_timing_algorithm,
        origin=solar_azimuth_series_north_based.origin,
    )
    # named 'projection' in pvlib
    cosine_solar_incidence_series = numpy.cos(solar_zenith_series.radians) * cos(
        surface_tilt.radians
    ) + sin(surface_tilt.radians) * numpy.sin(solar_zenith_series.radians) * numpy.cos(
        solar_azimuth_series.radians - surface_orientation.radians
    )  # where :
    # solar_azimuth_series : is the astronomers topocentric solar azimuth measured from south
    # surface_orientation : is the surface rotation azimuth angle measured from south

    # GH 1185 : This is a note from pvlib ?
    # projection = numpy.clip(projection, -1, 1)
    cosine_solar_incidence_series = numpy.clip(cosine_solar_incidence_series, -1, 1)
    solar_incidence_series = numpy.arccos(cosine_solar_incidence_series)

    incidence_angle_definition = SolarIncidence().definition_typical  # This is the "standard"
    incidence_angle_description = SolarIncidence().description_typical
    if complementary_incidence_angle:
        logger.debug(
            f":information: Converting solar incidence angle to {COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION}...",
            alt=f":information: [bold][magenta]Converting[/magenta] solar incidence angle to {COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION}[/bold]...",
        )
        solar_incidence_series = (pi / 2) - solar_incidence_series
        incidence_angle_definition = SolarIncidence().definition_complementary
        incidence_angle_description = SolarIncidence().description_complementary

    # set negative or below horizon angles ( == solar zenith > 90 ) to 0 !

    # Select which solar positions related to the horizon to process
    sun_horizon_positions = select_models(
        SunHorizonPositionModel, sun_horizon_position
    )  # Using a callback fails!
    # and keep track of the position of the sun relative to the horizon
    sun_horizon_position_series = create_array(
        timestamps.shape, dtype="object", init_method="empty", backend=array_backend
    )
    mask_below_horizon = create_array(
        timestamps.shape, dtype="bool", init_method="empty", backend=array_backend
    )
    mask_low_angle = create_array(
        timestamps.shape, dtype="bool", init_method="empty", backend=array_backend
    )
    mask_above_horizon = create_array(
        timestamps.shape, dtype="bool", init_method="empty", backend=array_backend
    )

    # For sun below the horizon
    if SunHorizonPositionModel.below in sun_horizon_positions:
        mask_below_horizon = solar_zenith_series.value > pi / 2
        sun_horizon_position_series[mask_below_horizon] = [
            SunHorizonPositionModel.below.value
        ]

    # For very low sun angles
    if SunHorizonPositionModel.low_angle in sun_horizon_positions:
        mask_low_angle = (
            (solar_zenith_series.value <= pi / 2)
            & (
                solar_zenith_series.value > solar_zenith_series.low_angle_threshoold_radians
            )
            & (sun_horizon_position_series == None)  # Operate only on unset elements
        )
        sun_horizon_position_series[mask_low_angle] = (
            SunHorizonPositionModel.low_angle.value
        )

    if SunHorizonPositionModel.above in sun_horizon_positions:
        mask_above_horizon = numpy.logical_and(
            (solar_zenith_series.value < pi / 2),
            sun_horizon_position_series == None,  # operate only on unset elements
        )
        sun_horizon_position_series[mask_above_horizon] = [
            SunHorizonPositionModel.above.value
        ]

    # Combine relevant conditions for no solar incidence
    mask_no_solar_incidence_series = numpy.logical_or(
        (solar_incidence_series < 0)
        | mask_below_horizon
        | surface_in_shade_series.value,
        sun_horizon_position_series == None,
    )

    # Zero out negative solar incidence angles : is the default behavior !
    if zero_negative_solar_incidence_angle:
        logger.debug(
            f":information: Setting negative solar incidence angle values to zero...",
            alt=f":information: [bold][magenta]Setting[/magenta] [red]negative[/red] solar incidence angle values to [bold]zero[/bold]...",
        )
        solar_incidence_series = numpy.where(
            mask_no_solar_incidence_series,
            # (solar_incidence_series < 0) | (solar_altitude_series.value < 0),
            NO_SOLAR_INCIDENCE,
            solar_incidence_series,
        )

    log_data_fingerprint(
        data=solar_incidence_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return SolarIncidence(
        value=solar_incidence_series,
        sun_horizon_position=sun_horizon_position_series,
        solar_positioning_algorithm=solar_zenith_series.solar_positioning_algorithm,
        solar_timing_algorithm=solar_zenith_series.solar_timing_algorithm,
        algorithm=SolarIncidenceModel.iqbal,
        definition=incidence_angle_definition,  # either the 'typical' or the 'complementary'
        description=incidence_angle_description,  # same as above
        azimuth_origin=solar_azimuth_series.origin,
    )
