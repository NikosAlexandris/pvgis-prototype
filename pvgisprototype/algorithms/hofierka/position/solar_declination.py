#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import numpy
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import SolarDeclination
from pvgisprototype.algorithms.hofierka.position.fractional_year import (
    calculate_day_angle_series_hofierka,
)
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.validation.values import identify_values_out_of_range_x


# @validate_with_pydantic(CalculateSolarDeclinationPVISInputModel)
@log_function_call
@custom_cached
def calculate_solar_declination_series_hofierka(
    timestamps: DatetimeIndex,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarDeclination:
    """Approximate the sun's declination for a given day of the year.

    The solar declination is the angle between the Sun's rays and the
    equatorial plane of Earth. It varies throughout the year due to the tilt of
    the Earth's axis and is an important parameter in determining the seasons
    and the amount of solar radiation received at different latitudes.

    The function calculates the `proportion` of the way through the year (in
    radians), which is given by `(2 * pi * day_of_year) / 365.25`.
    The `0.3978`, `1.4`, and `0.0355` are constants in the approximation
    formula, with the `0.0489` being an adjustment factor for the slight
    eccentricity of Earth's orbit.

    Parameters
    ----------
    day_of_year: int
        The day of the year (ranging from 1 to 365 or 366 in a leap year).

    Returns
    -------
    solar_declination: float
        The solar declination in radians for the given day of the year.

    Notes
    -----

    The equation used here is a simple approximation and bases upon a direct
    translation from PVGIS' rsun3 source code:

      - from file: rsun_base.cpp
      - function: com_declin(no_of_day)

    For more accurate calculations of solar position, comprehensive models like
    the Solar Position Algorithm (SPA) are typically used.
    """
    day_angle_series = calculate_day_angle_series_hofierka(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    # Note the - sign for the output solar declination, as is in PVGIS v5.2
    # see : com_declin() in rsun_base.c
    solar_declination_series = numpy.arcsin(
        0.3978
        * numpy.sin(
            day_angle_series.radians
            - 1.4
            + eccentricity_amplitude
            * numpy.sin(day_angle_series.radians - eccentricity_phase_offset)
        )
    )
    out_of_range, out_of_range_index = identify_values_out_of_range_x(
        series=solar_declination_series,
        shape=timestamps.shape,
        data_model=SolarDeclination(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_declination_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarDeclination(
        value=solar_declination_series,
        unit=RADIANS,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        solar_positioning_algorithm=SolarPositionModel.hofierka,  # ?
    )
