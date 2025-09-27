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
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    RADIANS,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
# @validate_with_pydantic(CalculateSolarAltitudeTimeSeriesJencoInput)
def calculate_solar_altitude_series_jenco(
    longitude: Longitude,  # radians
    latitude: Latitude,  # radians
    timestamps: DatetimeIndex,
    timezone: ZoneInfo | None,
    eccentricity_phase_offset: float,
    eccentricity_amplitude: float,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> SolarAltitude:
    """Calculate the solar altitude angle (θ) for a time series at a specific
    geographic latitude and longitude.

    Parameters
    ----------
    longitude : float
        Longitude of the location in radians.
    latitude : float
        Latitude of the location in radians.
    timestamps : DatetimeIndex
        Times for which the solar azimuth will be calculated.
    timezone : ZoneInfo
        Timezone of the location.
    dtype : str, optional
        Data type for the calculations.
    array_backend : str, optional
        Backend array library to use.
    verbose : int, optional
        Verbosity level of the function.
    log : int, optional
        Log level for the function.

    Returns
    -------
    SolarAltitude
        A custom data class that hold a NumPy NDArray of calculated solar
        azimuth angles in radians, a method to convert the angles to degrees
        and other metadata.

    Notes
    -----

    References
    ----------

    Examples
    --------

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
            f"{WARNING_OUT_OF_RANGE_VALUES} "
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
        solar_positioning_algorithm=solar_declination_series.solar_positioning_algorithm,  #
        solar_timing_algorithm=solar_hour_angle_series.solar_timing_algorithm,  #
    )
