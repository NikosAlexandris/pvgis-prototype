import typer
from typing import Annotated
from typing import Optional
from typing import NamedTuple
from datetime import datetime
from datetime import time as datetime_time
from datetime import timedelta
from zoneinfo import ZoneInfo
from skyfield import almanac
from skyfield.api import Topos
from skyfield.api import load
from skyfield.api import N
from skyfield.api import W
from skyfield.api import E
from skyfield.api import wgs84
from skyfield.api import load
from ...api.utilities.conversions import convert_to_radians
from ...api.utilities.timestamp import now_utc_datetimezone
from ...api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.named_tuples import generate


def calculate_solar_time_skyfield(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        verbose: bool = False,
        )-> NamedTuple:
    """
    Returns
    -------
    (decimal_hours, units): float, str
    """
    # debug(locals())
    # Handle Me during input validation? -------------------------------------
    if timezone != timestamp.tzinfo:
        try:
            timestamp = timestamp.astimezone(timezone)
        except Exception as e:
            logging.warning(f'Error setting tzinfo for timestamp = {timestamp}: {e}')
    # Handle Me during input validation? -------------------------------------

    midnight = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    next_midnight = midnight + timedelta(days=1)
    timescale = load.timescale()
    midnight_time = timescale.from_datetime(midnight)
    next_midnight_time = timescale.from_datetime(next_midnight)

    ephemeris = load('de421.bsp')
    sun = ephemeris['Sun']
    # location = wgs84.latlon(latitude * N, longitude * W)
    location = wgs84.latlon(latitude * N, longitude * E)
    f = almanac.meridian_transits(ephemeris, sun, location)
    times, events = almanac.find_discrete(midnight_time, next_midnight_time, f)
    
    times = times[events == 1]  # select transits instead of antitransits
    if not times:
        raise ValueError("No solar noon found in the given time range")

    solar_noon = times[0]
    solar_noon_string = str(solar_noon.astimezone(timezone))[:19]
    solar_noon_datetime = solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC'))
    local_solar_time = timestamp - solar_noon_datetime.astimezone(timezone)
    decimal_hours = local_solar_time.total_seconds() / 3600

    if verbose:
        typer.echo(f'Solar noon: {solar_noon_string}')
        typer.echo(f'Local solar time: {local_solar_time}')

    solar_time = generate(
        'solar_time'.upper(),
        (decimal_hours, 'decimal hours'),
    )

    # debug(locals())
    return solar_time
