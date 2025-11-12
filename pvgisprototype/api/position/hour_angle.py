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
from math import acos, tan
from typing import List
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import HourAngleSunrise, Latitude, Longitude, SolarHourAngle
from pvgisprototype.algorithms.noaa.solar_hour_angle import (
    calculate_solar_hour_angle_series_noaa,
)
from pvgisprototype.algorithms.hofierka.position.solar_hour_angle import (
    calculate_solar_hour_angle_series_hofierka,
)
from pvgisprototype.algorithms.pvlib.solar_hour_angle import (
    calculate_solar_hour_angle_series_pvlib,
)
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    FINGERPRINT_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.validation.functions import (
    CalculateEventHourAngleInputModel,
    validate_with_pydantic,
)


@log_function_call
@custom_cached
# @validate_with_pydantic(CalculateSolarHourAngleTimeSeriesNOAAInput)
def model_solar_hour_angle_series(
    longitude: Longitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> SolarHourAngle:
    """ """
    solar_hour_angle_series = None

    if solar_position_model.value == SolarPositionModel.noaa:
        solar_hour_angle_series = calculate_solar_hour_angle_series_noaa(
            longitude=longitude,
            timestamps=timestamps,
            timezone=timezone,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )

    if solar_position_model.value == SolarPositionModel.skyfield:
        pass

    if solar_position_model.value == SolarPositionModel.jenco:
        pass

    if solar_position_model.value == SolarPositionModel.hofierka:
        solar_hour_angle_series = calculate_solar_hour_angle_series_hofierka(
            longitude=longitude,
            timestamps=timestamps,
            timezone=timezone,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value == SolarPositionModel.pvlib:
        solar_hour_angle_series = calculate_solar_hour_angle_series_pvlib(
            longitude=longitude,
            timestamps=timestamps,
            # timezone=timezone,
            # dtype=dtype,
            # array_backend=array_backend,
            # verbose=verbose,
            # log=log,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return solar_hour_angle_series


# @validate_with_pydantic(CalculateSolarHourAngleSeriesInputModel)
def calculate_solar_hour_angle_series(
    longitude: Longitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.noaa],
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> SolarHourAngle:
    """Calculate the hour angle ω'

    ω = (ST / 3600 - 12) * 15 * pi / 180

    Parameters
    ----------

    solar_time : float
        The solar time (ST) is a calculation of the passage of time based on the
        position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds.

    output_units: str, optional
        Angle output units (degrees or radians).

    Returns
    -------

    Tuple(float, str)
        Tuple containg (hour_angle, units). Hour angle is the angle (ω) at any
        instant through which the earth has to turn to bring the meridian of the
        observer directly in line with the sun's rays measured in radian.

    Notes
    -----

    The hour angle ω (elsewhere symbolised with `h`) of a point on the earth’s
    surface is defined as the angle through which the earth would turn to bring
    the meridian of the point directly under the sun. The hour angle at local
    solar noon is zero, with each 360/24 or 15° of longitude equivalent to 1 h,
    afternoon hours being designated as positive. Expressed symbolically, the
    hour angle in degrees is:

        h = ±0.25 (Number of minutes from local solar noon)

    where the plus sign applies to afternoon hours and the minus sign to
    morning hours.

    The hour angle can also be obtained from the apparent solar time (AST);
    that is, the corrected local solar time:

        h = (AST - 12) * 15

    At local solar noon, AST = 12 and h = 0°. Therefore, from Eq <<(2.3)<<, the
    local solar time (LST, the time shown by our clocks at local solar noon)
    is:

        LST = 12 - ET ∓ 4 * (SL - LL)

        where:

            ET is the Equation of Time
            SL Standard Longitude
            LL Local Longitude

    Example 1

    The equation for LST at local solar noon for Nicosia, Cyprus is:

        LST = 12 - ET - 13.32 (minutes)

    Example 2

    Given the ET for March 10 (N = 69) is calculated from Eq (2.1), in which
    the factor B is obtained from Eq <<(2.2)<< as:

        B = 360 / 364 * (N-81) = 360 / 364 * (69- 81) = -11.87

        ET = 9.87 * sin(2*B) - 7.53 * cos(B) - 1.5 * sin(B) =
           = 9.87 * sin(-2 * 11.87) - 7.53 * cos(-11.87) - 1.5 * sin(-11.87)
           = -11.04min ∼ -11min

    The standard meridian for Athens is 30°E longitude.

    The apparent solar time on March 10 at 2:30 pm for the city of Athens,
    Greece (23°40′E longitude) is

        AST = 14:30 - 4 * (30 - 23.66) - 0:11
            = 14:30 - 0:25 - 0:11
            = 13:54 or 1:54 pm

    Additional notes:

    Nomenclature from [1]_

    α [°] solar altitude angle
    β [°] tilt angle
    δ [°] solar declination
    θ [°] solar incidence angle
    Φ [°] solar zenith angle
    h [°] hour angle
    L [°] local latitude
    N [-] day of the year
    z [°] solar azimuth angle
    ZS [°] surface azimuth angle
    AST Apparent Solar Time
    LST Local Standard Time
    ET Equation of Time
    SL Standard Longitude
    LL Local Longitude
    DS Daylight Saving

    .. [1] Determination of Optimal Position of Solar Trough Collector. Available from: https://www.researchgate.net/publication/317826540_Determination_of_Optimal_Position_of_Solar_Trough_Collector [accessed Sep 06 2023].

    In PVGIS :
        hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175

        which means:
        - solar time is expected in seconds
        - conversion to radians `* 0.0175` replaced by `pi / 180`

    In this function:
    """
    results = {}
    for solar_position_model in solar_position_models:
        # for the time being! ------------------------------------------------
        if solar_position_model != SolarPositionModel.noaa:
            logger.warning(
                f"Solar geometry overview series is not implemented for the requested solar position model: {solar_position_model}!"
            )
        # --------------------------------------------------------------------
        if (
            solar_position_model != SolarPositionModel.all
        ):  # ignore 'all' in the enumeration
            solar_hour_angle_series = model_solar_hour_angle_series(
                longitude=longitude,
                # latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_time_model=solar_time_model,
                solar_position_model=solar_position_model,
                dtype=dtype,
                array_backend=array_backend,
                validate_output=validate_output,
                verbose=verbose,
                log=log,
            )
            solar_hour_angle_series.build_output(
                verbose=verbose,
                fingerprint=fingerprint,
                angle_output_units=angle_output_units,
            )
            solar_hour_angle_overview = {
                solar_position_model.name: solar_hour_angle_series.output
            }
            results = results | solar_hour_angle_overview

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return results


@validate_with_pydantic(CalculateEventHourAngleInputModel)
def calculate_event_hour_angle_series(
    latitude: Latitude,
    surface_tilt: float = 0,
    solar_declination: float = 0,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> HourAngleSunrise:
    """Calculate the hour angle (ω) at sunrise and sunset

    Parameters
    ----------

    latitude: float
        Latitude (Φ) is the angle between the sun's rays and its projection on the
        horizontal surface measured in radians

    surface_tilt: float
        Surface tilt (or slope) (β) is the angle between the inclined surface
        (slope) and the horizontal plane.

    solar_declination: float
        Solar declination (δ) is the angle between the equator and a line drawn
        from the centre of the Earth to the centre of the sun measured in
        radians.

    Returns
    -------

    Tuple(float, str)
        Tuple containg (hour_angle, units). Hour angle (ω) is the angle at any
        instant through which the earth has to turn to bring the meridian of the
        observer directly in line with the sun's rays measured in radian.

    Notes
    -----
    Hour angle = acos( -tan * ( Latitude Angle - Tilt Angle ) * tan( Declination Angle ) )

    The hour angle (ω) at sunrise and sunset measures the angular distance
    between the sun at the local solar time and the sun at solar noon.

    ω = acos(-tan(Φ-β)*tan(δ))

    """
    hour_angle_sunrise = acos(
        -tan(latitude.radians - surface_tilt.radians) * tan(solar_declination.radians)
    )

    return HourAngleSunrise(
        value=hour_angle_sunrise,
        unit=RADIANS,
    )
