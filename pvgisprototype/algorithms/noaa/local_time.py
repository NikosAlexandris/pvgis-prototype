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
from datetime import timedelta
from zoneinfo import ZoneInfo
from pvgisprototype.api.position.models import SolarEvent

from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Latitude, Longitude, UnrefractedSolarZenith
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateLocalSolarTimeNOAAInput,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.event_time import calculate_solar_event_time_series_noaa
import numpy as np


@validate_with_pydantic(CalculateLocalSolarTimeNOAAInput)
def calculate_local_solar_time_noaa(
    longitude: Longitude,  # radians
    latitude: Latitude,  # radians
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    event: SolarEvent | None = SolarEvent.noon,
    unrefracted_solar_zenith: UnrefractedSolarZenith = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    # adjust_for_atmospheric_refraction: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> DatetimeIndex:
    """
    Calculate the Local Solar Time (LST) based on the sun's position.

    This function computes the local solar time for a series of timestamps,
    considering solar noon and corrections for the Equation of Time (ET) 
    and longitude. Local solar time reflects the actual position of the sun 
    in the sky, which may differ from local standard time.

    Parameters
    ----------
    longitude : Longitude
        Longitude of the location in radians.
    latitude : Latitude
        Latitude of the location in radians.
    timestamps : DatetimeIndex
        Timestamps for which to calculate the local solar time.
    timezone : ZoneInfo
        Timezone information for the location.
    unrefracted_solar_zenith : UnrefractedSolarZenith, optional
        The zenith of the sun, adjusted for atmospheric refraction. Defaults to
        1.5853349194640094 radians, which corresponds to 90.833 degrees. This
        is the zenith at sunrise or sunset, adjusted for the approximate
        correction for atmospheric refraction at those times, and the size of
        the solar disk.
    # adjust_for_atmospheric_refraction : bool, optional
    #     Whether to apply atmospheric refraction corrections (default is False).
    dtype : str, optional
        Data type for the output (default is DATA_TYPE_DEFAULT).
    array_backend : str, optional
        Backend for array operations (default is ARRAY_BACKEND_DEFAULT).
    verbose : int, optional
        Verbosity level for debugging (default is VERBOSE_LEVEL_DEFAULT).
    log : int, optional
        Logging level (default is LOG_LEVEL_DEFAULT).

    Returns
    -------
    DatetimeIndex
        A series of local solar times corresponding to the input timestamps.

    Notes
    -----

        In solar energy calculations, the Apparent Solar Time (AST) is based on the
    apparent angular motion of the sun across the sky, expressing the time of day.
    The moment when the sun crosses the meridian of the observer is known as 
    local solar noon. This does not usually coincide with 12:00 PM on the clock.

    Local Solar Time (LST) is calculated based on the Apparent Solar Time (AST),
    which is determined by the sun's position. The general equation for converting 
    between Local Solar Time (LST) and Apparent Solar Time (AST) is:

        AST = LST + ET ± 4 * (SL - LL) - DS

    Where:
    - AST: Apparent Solar Time
    - LST: Local Standard Time
    - ET: Equation of Time
    - SL: Standard Longitude for the time zone
    - LL: Local Longitude
    - DS: Daylight Saving Time adjustment. Working with UTC, DS is removed from the equation.

    Thus, the LST is given by :

        LST = AST - ET ± 4 * (SL - LL)

    For noon, AST = 12 thus :

        LST = 12 - ET ± 4 * (SL - LL)

    Definitions:

    - **Local Solar Time (LST)**: Time based on the sun's position at a specific location.
    - **Apparent Solar Time (AST)**: Time measured by the sun's position, specifically at solar noon.
    - **Equation of Time (ET)**: Difference between apparent solar time and mean solar time.
    - **Standard Longitude**: Longitude that defines the center of a time zone.
    - **Local Longitude**: Specific longitude of a location, used for corrections.
    - **Daylight Saving Time (DS)**: Adjustment of the clock to extend evening daylight.

    This function is useful for solar energy calculations and other applications
    where the actual solar time is relevant.

    """
    # Calculate solar noon for the given timestamps
    solar_noon_series = calculate_solar_event_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        event=event.name,
        unrefracted_solar_zenith=unrefracted_solar_zenith,
        # adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
    )

    # Calculate the time difference from solar noon
    local_solar_time_delta = np.where(
        timestamps < solar_noon_series,
        timestamps - (solar_noon_series - timedelta(days=1)),  # Previous solar noon
        timestamps - solar_noon_series,  # Current solar noon
    )

    # Convert time difference to seconds and add to timestamps
    total_seconds = int(local_solar_time_delta.total_seconds())
    local_solar_time_series = timestamps + timedelta(seconds=total_seconds)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return local_solar_time_series
