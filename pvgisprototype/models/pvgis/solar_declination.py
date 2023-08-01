from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from datetime import datetime
from datetime import timezone
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.geometry.solar_declination import calculate_solar_declination

def calculate_solar_declination_pvgis(
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        days_in_a_year: float = 365.25,
        eccentricity: float = 0.03344,
        perigee_offset: float = 0.048869,
        output_units: Annotated[str, typer.Option(
            '-o',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar declination (degrees or radians)")] = 'radians',
        ) -> float:
    """Approximate the sun's declination for a given day of the year.

    This function is a 1:1 transfer of the solar declination calculation
    implemented in PVGIS' r.sun C code, in form of the function `com_declin()`
    in `rsun_base.c` (or/and `rsun_base.cpp`). It merely exists in comparing
    with the new implementation and understanding the purpose of inverting the
    sign.

    IMPORTANT: In the original C source code, there is at the end of the

    `com_declin` function:

    ```
    decl = - decl;
    ```

    which is actually : `declination = - declination`. Why? The value is
    inverted again at some other part of the program when it gets to read data.
    """
    day_of_year = timestamp.timetuple().tm_yday
    solar_declination = calculate_solar_declination(
        timestamp,
        timezone,
        days_in_a_year,
        eccentricity,
        perigee_offset,
        output_units,
        )

    return - solar_declination
