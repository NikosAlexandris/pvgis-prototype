from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from datetime import datetime
from datetime import timezone
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.models.pvis.solar_declination import calculate_solar_declination_pvis

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationPVISInputModel
from pvgisprototype.api.data_classes.models import SolarDeclination


@validate_with_pydantic(CalculateSolarDeclinationPVISInputModel)
def calculate_solar_declination_pvgis(
    timestamp: datetime,
    timezone: str = None,
    days_in_a_year: float = 365.25,
    eccentricity_correction_factor: float = 0.03344,
    perigee_offset: float = 0.048869,
    angle_output_units: str = 'radians',
) -> SolarDeclination:
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
    solar_declination = calculate_solar_declination_pvis(
        timestamp,
        timezone,
        days_in_a_year,
        eccentricity_correction_factor,
        perigee_offset,
        angle_output_units,
        )
    
    solar_declination = SolarDeclination(
        value=-solar_declination.value,
        unit=solar_declination.unit,
        )

    return solar_declination
