from math import cos, pi, sin
from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Latitude, Longitude, SolarAzimuth
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateSolarAzimuthTimeSeriesNOAAInput,
)
from pvgisprototype.algorithms.noaa.solar_declination import (
    calculate_solar_declination_series_noaa,
)
from pvgisprototype.algorithms.noaa.solar_hour_angle import (
    calculate_solar_hour_angle_series_noaa,
)
from pvgisprototype.algorithms.noaa.solar_zenith import (
    calculate_solar_zenith_series_noaa,
)
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import validate_with_pydantic


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateSolarAzimuthTimeSeriesNOAAInput)
def calculate_solar_azimuth_series_noaa(
    longitude: Longitude,  # radians
    latitude: Latitude,  # radians
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool = True,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT,
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

    From .. Excel sheet :

    =IF(AC2>0,
        MOD(
            DEGREES(ACOS(((SIN(RADIANS($B$3))*COS(RADIANS(AD2)))-SIN(RADIANS(T2)))/(COS(RADIANS($B$3))*SIN(RADIANS(AD2)))))+180,
        360),
        MOD(
            540-DEGREES(ACOS(((SIN(RADIANS($B$3))*COS(RADIANS(AD2)))-SIN(RADIANS(T2)))/(COS(RADIANS($B$3))*SIN(RADIANS(AD2))))),
        360)
    )

    numerator = (sin(latitude.radians) * cos(solar_zenith.radians)) - sin(solar_declination.radians)
    denominator = (cos(latitude.radians) * sin(solar_zenith.radians))
    cosine_solar_azimuth = numerator / denominator

    if solar_hour_angle > 0:
        (pi + arccos(cosine_solar_azimuth)) % 2*pi

    else:
        (3*pi - arccos(cosine_solar_azimuth)) % 2*pi


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
    >>> from pvgisprototype.api.position.azimuth_series import calculate_solar_azimuth_series_noaa
    >>> solar_azimuth_series = calculate_solar_azimuth_series_noaa(
    ... longitude=radians(8.628),
    ... latitude=radians(45.812),
    ... timestamps=timestamps,
    ... timezone=ZoneInfo("UTC"),
    ... apply_atmospheric_refraction=True
    ... )
    >>> print(solar_azimuth_series)
        value=array([0.20324741, 0.681624  , 1.0347459 , 1.295689  , 1.505737  ,
               1.691547  , 1.8700209 , 2.06125   , 2.250216  , 2.466558  ,
               2.708641  , 2.9751856 , 3.2346206 , 3.50884   , 3.7576592 ,
               3.9807858 , 4.1786404 , 4.3685203 , 4.547683  , 4.73073   ,
               4.933111  , 5.178298  , 5.5035386 , 5.9491134 , 0.19983122],
              dtype=float32) unit='radians' position_algorithm='NOAA' timing_algorithm='NOAA' min_radians=0 max_radians=6.283185307179586 min_degrees=0 max_degrees=360

    >>> print(solar_azimuth_series.degrees)
        [ 11.645218  39.054176  59.28657   74.2375    86.27237   96.9185
         107.144295 118.100914 128.92787  141.32335  155.1937   170.46558
         185.3301   201.04172  215.298    228.08221  239.41844  250.29776
         260.56302  271.05084  282.64642  296.6946   315.32953  340.85907
          11.449485]

    """
    solar_declination_series = calculate_solar_declination_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
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
    solar_zenith_series = calculate_solar_zenith_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
    numerator_series = sin(latitude.radians) * np.cos(
        solar_zenith_series.radians
    ) - np.sin(solar_declination_series.radians)
    denominator_series = cos(latitude.radians) * np.sin(solar_zenith_series.radians)
    cosine_solar_azimuth_series = numerator_series / denominator_series
    solar_azimuth_series = np.arccos(np.clip(cosine_solar_azimuth_series, -1, 1))
    solar_azimuth_series = np.where(
        solar_hour_angle_series.radians > 0,  # afternoon hours !
        np.mod((pi + solar_azimuth_series), 2 * pi),
        np.mod(3 * pi - solar_azimuth_series, 2 * pi),
    )

    if validate_output:
        if (
            (solar_azimuth_series < SolarAzimuth().min_radians)
            | (solar_azimuth_series > SolarAzimuth().max_radians)
        ).any():
            out_of_range_values = solar_azimuth_series[
                (solar_azimuth_series < SolarAzimuth().min_radians)
                | (solar_azimuth_series > SolarAzimuth().max_radians)
            ]
            # raise ValueError(# ?
            raise ValueError(
                f"{WARNING_OUT_OF_RANGE_VALUES} "
                f"[{SolarAzimuth().min_radians}, {SolarAzimuth().max_radians}] radians"
                f" in [code]solar_azimuth_series[/code] : {out_of_range_values}"
            )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_azimuth_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarAzimuth(
        value=solar_azimuth_series,
        unit=RADIANS,
        position_algorithm=SolarPositionModel.noaa,
        timing_algorithm=SolarTimeModel.noaa,
        origin="North",
    )
