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
        verbose: str = False,
    ) -> SolarTime:
    """
    Returns
    -------

    (solar_time, units): float, str
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

    local_solar_time = datetime(
            year=local_solar_time.year,
            month=local_solar_time.month,
            day=local_solar_time.day,
            hour=int(local_solar_time.hour),
            minute=int(local_solar_time.minute),
            second=int(local_solar_time.second),
            tzinfo=local_solar_time.tzinfo,
            )

    return local_solar_time
