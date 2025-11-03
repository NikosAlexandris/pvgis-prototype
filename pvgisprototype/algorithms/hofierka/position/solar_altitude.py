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
from math import cos, sin
from zoneinfo import ZoneInfo

import numpy
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Latitude, Longitude, SolarAltitude
from pvgisprototype.algorithms.hofierka.position.solar_declination import (
    calculate_solar_declination_series_hofierka,
)
from pvgisprototype.algorithms.hofierka.position.solar_hour_angle import (
    calculate_solar_hour_angle_series_hofierka,
)
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_NEGATIVE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
# @validate_with_pydantic(CalculateSolarAltitudePVISInputModel)
def calculate_solar_altitude_series_hofierka(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    eccentricity_phase_offset: float,
    eccentricity_amplitude: float,
    # solar_time_model: SolarTimeModel,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarAltitude:
    """Calculate the solar altitude angle.

    Calculate the solar altitude angle based on the equation

    sine_solar_altitude = (
        sin(latitude.radians)
        * np.sin(solar_declination_series.radians)
        + cos(latitude.radians)
        * np.cos(solar_declination_series.radians)
        * np.cos(solar_hour_angle_series.radians)

    Parameters
    ----------
    longitude : float
        The longitude in degrees. This value will be converted to radians.
        It should be in the range [-180, 180].

    latitude : float
        The latitude in degrees. This value will be converted to radians.
        It should be in the range [-90, 90].

    timestamp : datetime, optional
        The timestamp for which to calculate the solar altitude.
        If not provided, the current UTC time will be used.

    timezone : str, optional
        The timezone to use for the calculation.
        If not provided, the system's local timezone will be used.

    Returns
    -------
    float
        The calculated solar altitude.

    Notes
    -----

    NOAA's equation is practically the same, though it targets the cosine
    function of the solar zenith angle which it the complementary of the solar
    altitude angle.

    cosine_solar_zenith = (
        sin(latitude.radians)
        * np.sin(solar_declination_series.radians)
        + cos(latitude.radians)
        * np.cos(solar_declination_series.radians)
        * np.cos(solar_hour_angle_series.radians)

    """
    solar_declination_series = calculate_solar_declination_series_hofierka(
        timestamps=timestamps,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )

    # Idea for alternative solar time modelling, i.e. Milne 1921 -------------
    # solar_time = model_solar_time(
    #     longitude=longitude,
    #     latitude=latitude,
    #     timestamp=timestamp,
    #     timezone=timezone,
    #     solar_time_model=solar_time_model,  # returns datetime.time object
    #     eccentricity_phase_offset=eccentricity_phase_offset,
    #     eccentricity_amplitude=eccentricity_amplitude,
    # )
    # hour_angle = calculate_solar_hour_angle_pvis(
    #         solar_time=solar_time,
    # )
    # ------------------------------------------------------------------------

    solar_hour_angle_series = calculate_solar_hour_angle_series_hofierka(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    C31 = cos(latitude.radians) * numpy.cos(solar_declination_series.radians)
    C33 = sin(latitude.radians) * numpy.sin(solar_declination_series.radians)
    sine_solar_altitude_series = C31 * numpy.cos(solar_hour_angle_series.radians) + C33
    solar_altitude_series = numpy.arcsin(sine_solar_altitude_series)

    # mask_positive_C31 = C31 > 1e-7
    # solar_altitude_series[mask_positive_C31] = numpy.where(
    #     sine_solar_altitude_series < 0,
    #     NO_SOLAR_INCIDENCE,
    #     solar_altitude_series,
    # )

    # The hour angle of the time of sunrise/sunset over a horizontal surface
    # Thr,s can be calculated then as:
    # cos(event_hour_angle_horizontal) = -C33 / C31

    if (
        (solar_altitude_series < SolarAltitude().min_radians)
        | (solar_altitude_series > SolarAltitude().max_radians)
    ).any():
        out_of_range_values = solar_altitude_series[
            (solar_altitude_series < SolarAltitude().min_radians)
            | (solar_altitude_series > SolarAltitude().max_radians)
        ]
        # raise ValueError(# ?
        logger.warning(
            f"{WARNING_NEGATIVE_VALUES} "
            f"[{SolarAltitude().min_radians}, {SolarAltitude().max_radians}] radians"
            f" in [code]solar_altitude_series[/code] : {out_of_range_values}"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_altitude_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarAltitude(
        value=solar_altitude_series,
        unit=RADIANS,
        solar_positioning_algorithm=SolarPositionModel.hofierka,
        solar_timing_algorithm=solar_hour_angle_series.solar_timing_algorithm,
    )
