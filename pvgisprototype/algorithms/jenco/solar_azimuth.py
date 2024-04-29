import numpy
from devtools import debug
from datetime import datetime
from zoneinfo import ZoneInfo
from math import sin
from math import cos
from math import isfinite
from pvgisprototype import SolarAzimuth
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.constants import RADIANS
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pandas import DatetimeIndex
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL


@log_function_call
@cached(cache={}, key=custom_hashkey)
# @validate_with_pydantic(CalculateSolarAzimuthTimeSeriesJencoInput)
def calculate_solar_azimuth_time_series_jenco(
    longitude: Longitude,   # radians
    latitude: Latitude,     # radians
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool = True,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> SolarAzimuth:
    """Calculate the solar azimuth angle (θ) for a time series at a specific
    geographic latitude and longitude.

    Calculate the solar azimuth angle (θ) for a time series at a specific
    geographic latitude and longitude, by default correcting the solar zenith
    angle for atmospheric refraction, as described in the following steps:
    
        1. Calculate the solar declination, solar hour angle, and solar zenith
        using NOAA's General Solar Position Calculations.

        2. Calculate the solar azimuth angle using the equation reported in
        Wikipedia's article "Solar azimuth angle" adjusting for the time of
        day -- see also Notes :

            - Morning (solar hour angle < 0): azimuth derived directly from the
              arccosine function.

            - Afternoon (solar hour angle > 0): azimuth adjusted to range in
              [180°, 360°] by subtracting it from 360°.

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


    1. The equation given in NOAA's General Solar Position Calculations [0]_ is

                         sin(latitude) * cos(solar_zenith) - sin(solar_declination)
        cos(180 - θ) = - ----------------------------------------------------------
                                  cos(latitude) * sin(solar_zenith)


        or after converting cos(180 - θ) to - cos(θ) :

                     sin(latitude) * cos(solar_zenith) - sin(solar_declination)
        - cos(θ) = - ------------------------------------------------------------
                                cos(latitude) * sin(solar_zenith)


        or :

                 sin(latitude) * cos(solar_zenith) - sin(solar_declination)
        cos(θ) = ----------------------------------------------------------
                             cos(latitude) * sin(solar_zenith)

        
        and finally :

                      sin(latitude) * cos(solar_zenith) - sin(solar_declination)
        θ = arccos( -------------------------------------------------------------- )
                                  cos(latitude) * sin(solar_zenith)

        where θ is the wanted solar azimuth angle.

        However, comparing this equation with the _almost identical_ equation
        reported in Wikipedia's relevant article and subsection titled
        "Conventional Trigonometric Formulas" [1]_, there seems to be a
        difference of a minus sign :

                     sin(declination) - cos(zenith) * sin(latitude)
        φs = arccos( ---------------------------------------------- )
                             sin(zenith) * cos(latitude)

        where φs is the wanted solar azimuth angle.

        A cross-comparison of the solar azimuth angle derived by the equation
        reported in Wikipedia's article [1]_ and the libraries pvlib [2]_,
        pysolar [3]_, Skyfield [4]_ and suncalc [5]_, show a high agreement
        across all of them.


    2. Adjusting the solar azimuth based on the time of day

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
    >>> from pvgisprototype.api.position.azimuth_series import calculate_solar_azimuth_time_series_noaa
    >>> solar_azimuth_series = calculate_solar_azimuth_time_series_noaa(
    ... longitude=radians(8.628),
    ... latitude=radians(45.812),
    ... timestamps=timestamps,
    ... timezone=ZoneInfo("UTC"),
    ... apply_atmospheric_refraction=True
    ... )
    >>> print(solar_azimuth_series)
    >>> print(solar_azimuth_series.degrees)

    """
    solar_declination_series = calculate_solar_declination_time_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_zenith_series = calculate_solar_zenith_time_series_noaa(
        latitude=latitude,
        timestamps=timestamps,
        solar_hour_angle_series=solar_hour_angle_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        dtype=dtype,
        backend=array_backend,
        verbose=verbose,
        log=log,
    )
    C11 = sin(latitude.radians) * numpy.cos(solar_declination_series.radians)
    C13 = - cos(latitude.radians) * numpy.sin(solar_declination_series.radians)
    C22 = numpy.cos(solar_declination_series.radians)
    numerator = C11 * numpy.cos(solar_hour_angle_series.radians) - C13
    denominator_a = numpy.power(C22 * numpy.sin(solar_hour_angle_series.radians), 2)
    denominator_b = numpy.power((C11 * numpy.cos(solar_hour_angle_series.radians) + C13), 2)
    denominator = numpy.power(denominator_a + denominator_b, 0.5)
    cosine_solar_azimuth_series = numerator / denominator
    solar_azimuth_series = numpy.arccos(cosine_solar_azimuth_series)

    # # interpretation for afternoon hours !
    # afternoon_hours = solar_hour_angle_series.value > 0
    # solar_azimuth_series[afternoon_hours] = (
    #     (2 * numpy.pi) - solar_azimuth_series[afternoon_hours]
    # )

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
    )
