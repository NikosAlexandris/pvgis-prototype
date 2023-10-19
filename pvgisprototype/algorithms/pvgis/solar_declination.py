from devtools import debug
from datetime import datetime
from math import isfinite
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationPVISInputModel
from pvgisprototype import SolarDeclination


@validate_with_pydantic(CalculateSolarDeclinationPVISInputModel)
def calculate_solar_declination_pvgis(
    timestamp: datetime,
    timezone: str = None,
    eccentricity_correction_factor: float = 0.03344,
    perigee_offset: float = 0.048869,
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
    solar_declination = calculate_solar_declination_pvis(
        timestamp=timestamp,
        timezone=timezone,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
        )
    
    solar_declination = SolarDeclination(
        value=-solar_declination.value,
        unit=solar_declination.unit,
        position_algorithm='PVGIS',
        timing_algorithm='PVGIS'
    )
    if (
        not isfinite(solar_declination.degrees)
        or not solar_declination.min_degrees <= solar_declination.degrees <= solar_declination.max_degrees
    ):
        raise ValueError(
            f"The calculated solar declination angle {solar_declination.degrees} is out of the expected range\
            [{solar_declination.min_degrees}, {solar_declination.max_degrees}] degrees"
        )
    return solar_declination
