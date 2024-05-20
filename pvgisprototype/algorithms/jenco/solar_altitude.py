import numpy
from devtools import debug
from datetime import datetime
from zoneinfo import ZoneInfo
from math import sin
from math import cos
from math import isfinite
from pvgisprototype import SolarAltitude
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_series_hofierka
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_series_hofierka
from pvgisprototype.constants import NO_SOLAR_INCIDENCE, RADIANS
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pandas import DatetimeIndex
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.api.position.models import SolarPositionModel


@log_function_call
@cached(cache={}, key=custom_hashkey)
# @validate_with_pydantic(CalculateSolarAltitudeTimeSeriesJencoInput)
def calculate_solar_altitude_time_series_jenco(
    longitude: Longitude,   # radians
    latitude: Latitude,     # radians
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    perigee_offset: float,
    eccentricity_correction_factor: float,
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
    timestamps : Union[datetime, DatetimeIndex]
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
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    # solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
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
        positioning_algorithm=solar_declination_series.position_algorithm,  #
        timing_algorithm=solar_hour_angle_series.timing_algorithm,  #
    )
