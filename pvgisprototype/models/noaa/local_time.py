from .noaa_models import CalculateLocalSolarTimeNOAAInput
from .decorators import validate_with_pydantic
from .event_time import calculate_event_time_noaa
from datetime import datetime
from datetime import time


@validate_with_pydantic(CalculateLocalSolarTimeNOAAInput)
def calculate_local_solar_time_noaa(
        longitude: float,
        latitude: float,
        timestamp: float,
        timezone: str,
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: bool = False,
        time_output_units: str = 'hours',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        verbose: str = False,
    ) -> float:
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
    solar_noon_timestamp, units = calculate_event_time_noaa(
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
    local_solar_time = timestamp - solar_noon_timestamp
    total_seconds = int(local_solar_time.total_seconds())
    local_solar_timestamp = datetime.utcfromtimestamp(total_seconds).time()


    # hours, remainder = divmod(total_seconds, 3600)
    # minutes, seconds = divmod(remainder, 60)
    # local_solar_timestamp = time(hour=hours, minute=minutes, second=seconds)
    # local_solar_time_ = local_solar_timestamp.strftime("%H:%M:%S")

    if verbose:
        typer.echo(f'Local solar time: {local_solar_timestamp}')

    # debug(locals())
    return local_solar_timestamp, time_output_units
