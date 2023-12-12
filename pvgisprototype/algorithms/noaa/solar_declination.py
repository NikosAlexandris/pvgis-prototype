from typing import Optional
from typing import Union
from typing import Sequence
from datetime import datetime
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationNOAAInput
from pvgisprototype.validation.functions import CalculateSolarDeclinationNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarDeclinationTimeSeriesNOAAInput
from .fractional_year import calculate_fractional_year_noaa 
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_time_series_noaa
from math import sin
from math import cos
from math import isfinite
import numpy as np
from pvgisprototype import SolarDeclination
from pvgisprototype.constants import RADIANS


# @cache_result
@validate_with_pydantic(CalculateSolarDeclinationNOAAInput)
def calculate_solar_declination_noaa(
    timestamp: datetime,
) -> SolarDeclination:
    """Calculate the solar declination angle in radians"""
    fractional_year = calculate_fractional_year_noaa(
        timestamp=timestamp,
    )
    declination = (
        0.006918
        - 0.399912 * cos(fractional_year.radians)
        + 0.070257 * sin(fractional_year.radians)
        - 0.006758 * cos(2 * fractional_year.radians)
        + 0.000907 * sin(2 * fractional_year.radians)
        - 0.002697 * cos(3 * fractional_year.radians)
        + 0.00148 * sin(3 * fractional_year.radians)
        )
    solar_declination = SolarDeclination(
        value=declination,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA'
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

DEFAULT_ARRAY_BACKEND = 'NUMPY'  # OR 'CUPY', 'DASK'
DEFAULT_ARRAY_DTYPE = 'float32'

@validate_with_pydantic(CalculateSolarDeclinationTimeSeriesNOAAInput)
def calculate_solar_declination_time_series_noaa(
    timestamps: Union[datetime, Sequence[datetime]],
    backend: str = DEFAULT_ARRAY_BACKEND,
    dtype: str = DEFAULT_ARRAY_DTYPE,
) -> SolarDeclination:
    """
    """
    fractional_year_series = calculate_fractional_year_time_series_noaa(
        timestamps=timestamps,
        backend=backend,
        dtype=dtype,
        # angle_output_units=RADIANS,
    )
    declination_series = (
        0.006918
        - 0.399912 * np.cos(fractional_year_series.radians)
        + 0.070257 * np.sin(fractional_year_series.radians)
        - 0.006758 * np.cos(2 * fractional_year_series.radians)
        + 0.000907 * np.sin(2 * fractional_year_series.radians)
        - 0.002697 * np.cos(3 * fractional_year_series.radians)
        + 0.00148 * np.sin(3 * fractional_year_series.radians)
    )
    declination_series = SolarDeclination(
        value=declination_series,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )

    # if not np.all((declination_series.min_degrees <= declination_series.degrees) & (declination_series.degrees <= declination_series.max_degrees)):           # FIXME: Comparison between floats
    #     wrong_values_index = np.where((declination_series.degrees < declination_series.min_degrees) | (declination_series.degrees > declination_series.max_degrees))
    #     wrong_values = declination_series.degrees[wrong_values_index]
    #     raise ValueError(f"The calculated solar declination `{wrong_values}` is out of the expected range [{declination_series.min_degrees}, {declination_series.max_degrees}] degrees!")

    return declination_series
