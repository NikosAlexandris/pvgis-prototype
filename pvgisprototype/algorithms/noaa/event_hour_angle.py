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
import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import EventHourAngle, Latitude, UnrefractedSolarZenith
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateEventHourAngleTimeSeriesNOAAInput,
)
from pvgisprototype.algorithms.noaa.solar_declination import (
    calculate_solar_declination_series_noaa,
)
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import validate_with_pydantic


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateEventHourAngleTimeSeriesNOAAInput)
def calculate_event_hour_angle_series_noaa(
    latitude: Latitude,
    timestamps: DatetimeIndex,
    unrefracted_solar_zenith: UnrefractedSolarZenith,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> EventHourAngle:
    """
    Calculates the event hour angle using the NOAA method.

    Parameters
    ----------
    latitude : Latitude
        The geographic latitude for which to calculate the event hour angle.

    timestamp : datetime
        The date and time for which to calculate the event hour angle.

    unrefracted_solar_zenith : UnrefractedSolarZenith, optional
        The zenith of the sun, adjusted for atmospheric refraction. Defaults to
        1.5853349194640094 radians, which corresponds to 90.833 degrees. This
        is the zenith at sunrise or sunset, adjusted for the approximate
        correction for atmospheric refraction at those times, and the size of
        the solar disk.

    angle_units : str, optional
        The unit in which the angles are input. Defaults to 'radians'.

    angle_output_units : str, optional
        The unit in which the output angle should be returned. Defaults to
        'radians'.

    Returns
    -------
    event_hour_angle : float
        The calculated event hour angle.

    angle_output_units : str
        The unit of the output angle.

    Notes
    -----
    The function implements NOAA calculations for the solar declination and
    the event hour angle. The solar declination is calculated first in radians,
    followed by the event hour angle in radians.

    Commented out: If the output units are 'degrees', the function
    will convert the calculated event hour angle from radians to degrees.

    """
    solar_declination_series = calculate_solar_declination_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )  # radians
    cosine_event_hour_angle_series = np.cos(unrefracted_solar_zenith.radians) / (
        np.cos(latitude.radians) * np.cos(solar_declination_series.radians)
    ) - np.tan(latitude.radians) * np.tan(solar_declination_series.radians)
    event_hour_angle_series = np.arccos(
        np.clip(cosine_event_hour_angle_series, -1, 1)
    )  # radians

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=event_hour_angle_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return EventHourAngle(
        value=event_hour_angle_series,
        unit=RADIANS,
        timing_algorithm=SolarTimeModel.noaa,
    )
