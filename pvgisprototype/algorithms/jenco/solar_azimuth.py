from math import cos, pi, sin
from zoneinfo import ZoneInfo

import numpy
from pandas import DatetimeIndex

from pvgisprototype import Latitude, Longitude, SolarAzimuth
from pvgisprototype.algorithms.jenco.solar_declination import (
    calculate_solar_declination_series_jenco,
)
from pvgisprototype.algorithms.noaa.solar_hour_angle import (
    calculate_solar_hour_angle_series_noaa,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    RADIANS,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
# @validate_with_pydantic(CalculateSolarAzimuthTimeSeriesJencoInput)
def calculate_solar_azimuth_series_jenco(
    longitude: Longitude,  # radians
    latitude: Latitude,  # radians
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool = True,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> SolarAzimuth:
    """Calculate the solar azimuth angle (θ) between the sun and meridian
    measured from East for a time series at a specific geographic latitude
    and longitude.

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
    apply_atmospheric_refraction : bool, optional
        Whether to correct the solar zenith angle for atmospheric refraction.
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
    SolarAzimuth
        A custom data class that hold a NumPy NDArray of calculated solar
        azimuth angles in radians, a method to convert the angles to degrees
        and other metadata.

    Notes
    -----
    Two important notes on the calculation of the solar azimuth angle :

    - The equation implemented here follows upon the relevant Wikipedia article
      for the "Solar azimuth angle" [1]_.

    - The angle derived fom the arccosine function requires an adjustment to
    correctly represent both morning and afternoon solar azimuth angles.


    Adjusting the solar azimuth based on the time of day

    Given that arccosine ranges in [0, π] or else in [0°, 180°], the raw
    calculated solar azimuth angle will likewise range in [0, π]. This
    necessitates an adjustment based on the time of day.

    - Morning (solar hour angle < 0): the azimuth angle is correctly
      derived directly from the arccosine function representing angles from
      the North clockwise to the South [0°, 180°].

    - Afternoon (solar hour angle > 0): the azimuth angle needs to be
      adjusted in order to correctly represent angles going further from
      the South to the West [180°, 360°]. This is achieved by subtracting
      the azimuth from 360°.

    On the use of arctan2 from Wikipedia :

    Corollary: if (y1, x1) and (y2, x2) are 2-dimensional vectors, the
    difference formula is frequently used in practice to compute the angle
    between those vectors with the help of atan2, since the resulting
    computation behaves benign in the range (−π, π] and can thus be used
    without range checks in many practical situations.

    The `atan2` function was originally designed for the convention in pure
    mathematics that can be termed east-counterclockwise. In practical
    applications, however, the north-clockwise and south-clockwise conventions
    are often the norm. The solar azimuth angle for example, that uses both the
    north-clockwise and south-clockwise conventions widely, can be calculated
    similarly with the east- and north-components of the solar vector as its
    arguments. Different conventions can be realized by swapping the positions
    and changing the signs of the x- and y-arguments as follows:

    - atan2(y,x) : East-Counterclockwise Convention
    - atan2(x,y) : North-Clockwise Convention
    - atan2(-x,-y) : South-Clockwise Convention

    Changing the sign of the x- and/or y-arguments and/or swapping their
    positions can create 8 possible variations of the atan2 function and they,
    interestingly, correspond to 8 possible definitions of the angle, namely,
    clockwise or counterclockwise starting from each of the 4 cardinal
    directions, north, east, south and west.

    References
    ----------
    .. [0] https://gml.noaa.gov/grad/solcalc/solareqns.PDF

    .. [1] https://en.wikipedia.org/wiki/Solar_azimuth_angle#Conventional_Trigonometric_Formulas

    .. [2] https://github.com/pvlib/pvlib-python

    .. [3] https://github.com/pingswept/pysolar

    .. [4] https://github.com/skyfielders/python-skyfield/

    .. [5] https://github.com/kylebarron/suncalc-py

    Examples
    --------
    >>> from math import radians
    >>> from pvgisprototype.api.utilities.timestamp import generate_datetime_series
    >>> timestamps = generate_datetime_series(start_time='2010-01-27', end_time='2010-01-28')
    >>> from zoneinfo import ZoneInfo
    >>> from pvgisprototype.api.position.azimuth_series import calculate_solar_azimuth_series_noaa
    >>> solar_azimuth_series = calculate_solar_azimuth_series_noaa(
    ... longitude=radians(8.628),
    ... latitude=radians(45.812),
    ... timestamps=timestamps,
    ... timezone=ZoneInfo("UTC"),
    ... apply_atmospheric_refraction=True
    ... )
    >>> print(solar_azimuth_series)
    >>> print(solar_azimuth_series.degrees)

    """
    solar_declination_series = calculate_solar_declination_series_jenco(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_hour_angle_series = calculate_solar_hour_angle_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    C11 = sin(latitude.radians) * numpy.cos(solar_declination_series.radians)
    C13 = cos(latitude.radians) * numpy.sin(solar_declination_series.radians)
    C22 = numpy.cos(solar_declination_series.radians)
    x_solar_vector_component = C22 * numpy.sin(solar_hour_angle_series.radians)
    y_solar_vector_component = C11 * numpy.cos(solar_hour_angle_series.radians) - C13
    # `x` to `y` derives North-Clockwise azimuth
    azimuth_origin = "North"
    solar_azimuth_series = numpy.mod(
        (pi + numpy.arctan2(x_solar_vector_component, y_solar_vector_component)), 2 * pi
    )

    if (
        (solar_azimuth_series < SolarAzimuth().min_radians)
        | (solar_azimuth_series > SolarAzimuth().max_radians)
    ).any():
        out_of_range_values = solar_azimuth_series[
            (solar_azimuth_series < SolarAzimuth().min_radians)
            | (solar_azimuth_series > SolarAzimuth().max_radians)
        ]
        # raise ValueError(# ?
        logger.warning(
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{SolarAzimuth().min_radians}, {SolarAzimuth().max_radians}] radians"
            f" in [code]solar_azimuth_series[/code] : {out_of_range_values}"
        )
    log_data_fingerprint(
        data=solar_azimuth_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarAzimuth(
        value=solar_azimuth_series,
        unit=RADIANS,
        # positioning_algorithm=solar_declination_series.position_algorithm,  #
        timing_algorithm=solar_hour_angle_series.timing_algorithm,  #
        origin=azimuth_origin,
    )
