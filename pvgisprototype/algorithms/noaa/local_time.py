from datetime import datetime
from datetime import timedelta
from datetime import time
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateLocalSolarTimeNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarTime
from .event_time import calculate_event_time_noaa


@validate_with_pydantic(CalculateLocalSolarTimeNOAAInput)
def calculate_local_solar_time_noaa(
        longitude: Longitude,   # radians
        latitude: Latitude, # radians
        timestamp: datetime,
        timezone: str,
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: bool = False,
        time_output_units: str = 'hours',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        verbose: int = 0,
    ) -> SolarTime:
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
    # # Handle Me during input validation? -------------------------------------
    # if timezone != timestamp.tzinfo:
    #     try:
    #         timestamp = timestamp.astimezone(timezone)
    #     except Exception as e:
    #         logging.warning(f'Error setting tzinfo for timestamp = {timestamp}: {e}')
    # # ------------------------------------------------------------------------
    solar_noon_timestamp = calculate_event_time_noaa(
        longitude,
        latitude,
        timestamp,
        timezone,
        'noon',
        refracted_solar_zenith,
        apply_atmospheric_refraction,
        time_output_units,
        angle_units,
        angle_output_units,
    )

    if timestamp < solar_noon_timestamp:
        previous_solar_noon_timestamp = solar_noon_timestamp - timedelta(days=1)
        local_solar_time_delta = timestamp - previous_solar_noon_timestamp

    else:
        local_solar_time_delta = timestamp - solar_noon_timestamp

    total_seconds = int(local_solar_time_delta.total_seconds())
    # hours, remainder = divmod(total_seconds, 3600)
    # minutes, seconds = divmod(remainder, 60)
    # local_solar_timestamp = time(hour=hours, minute=minutes, second=seconds)

    if verbose:
        typer.echo(f'Local solar time: {local_solar_timestamp}')

    local_solar_time = timestamp + timedelta(seconds=total_seconds)

    return local_solar_time
