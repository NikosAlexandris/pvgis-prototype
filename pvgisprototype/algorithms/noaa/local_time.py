from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from devtools import debug
from pandas import DatetimeIndex
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateLocalSolarTimeNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import RefractedSolarZenith
from .event_time import calculate_event_time_time_series_noaa
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT


@validate_with_pydantic(CalculateLocalSolarTimeNOAAInput)
def calculate_local_solar_time_noaa(
    longitude: Longitude,  # radians
    latitude: Latitude,  # radians
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    refracted_solar_zenith: RefractedSolarZenith,  # radians
    apply_atmospheric_refraction: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> datetime:
    """
    Returns
    -------

    (solar_time, units): float, str

    Notes
    -----

    The local standard time (LST) 


    The general equation for AST is :

        AST = LST + ET +/-4 * (SL - LL) - DS

        where :

        - AST Apparent Solar Time
        - LST Local Standard Time
        - ET Equation of Time
        - SL Standard Longitude
        - LL Local Longitude
        - DS Daylight Saving *
            * Working with UTC, DS is removed from the equation.

    Thus, the LST is given by :

        LST = AST - ET -/+4 * (SL - LL)

    For noon, AST = 12 thus :

        LST = 12 - ET -/+4 * (SL - LL)

    In solar energy calculations, the apparent solar time (AST) based on the
    apparent angular motion of the sun across the sky expresses the time of
    day. The time when the sun crosses the meridian of the observer is the
    local solar noon. It usually does not coincide with the 12:00 o’clock time
    of a locality. To convert the local standard time (LST) to AST, two
    corrections are applied; the equation of time (ET) and longitude
    correction. These are analyzed next.
    """
    solar_noon_series = calculate_event_time_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        event='noon',
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    local_solar_time_delta = numpy.where(
            timestamps < solar_noon_series,
            timestamps - (solar_noon_series - timedelta(days=1)),
            timestamps - solar_noon_series
            )
    total_seconds = int(local_solar_time_delta.total_seconds())
    local_solar_time_series= timestamps + timedelta(seconds=total_seconds)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return local_solar_time_series
