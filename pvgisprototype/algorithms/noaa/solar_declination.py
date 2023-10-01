from typing import Optional
from typing import Union
from typing import Sequence
from datetime import datetime
from ...api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarDeclinationTimeSeriesNOAAInput
from .fractional_year import calculate_fractional_year_noaa 
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_time_series_noaa
from math import sin
from math import cos
import numpy as np

from pvgisprototype import SolarDeclination


# @cache_result
@validate_with_pydantic(CalculateSolarDeclinationNOAAInput)
def calculate_solar_declination_noaa(
        timestamp: datetime,
        # angle_output_units: Optional[str] = 'radians'
) -> SolarDeclination:
        """Calculate the solar declination in radians"""
        fractional_year = calculate_fractional_year_noaa(
                timestamp=timestamp,
                angle_output_units='radians',
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

        declination = SolarDeclination(value=declination, unit='radians')
        # declination = convert_to_degrees_if_requested(
        #         declination,
        #         angle_output_units,
        #         )
        return declination


@validate_with_pydantic(CalculateSolarDeclinationTimeSeriesNOAAInput)
def calculate_solar_declination_time_series_noaa(
        timestamps: Union[datetime, Sequence[datetime]],
        angle_output_units: str = "radians"
):# -> Union[SolarDeclination, np.ndarray]:

    # timestamps = np.atleast_1d(timestamps)  # timestamps as array
    fractional_year_series = calculate_fractional_year_time_series_noaa(
        timestamps=timestamps,
        angle_output_units="radians",
    )
    fractional_year_series_array = np.array([fy.radians for fy in fractional_year_series])
    declinations = (
        0.006918
        - 0.399912 * np.cos(fractional_year_series_array)
        + 0.070257 * np.sin(fractional_year_series_array)
        - 0.006758 * np.cos(2 * fractional_year_series_array)
        + 0.000907 * np.sin(2 * fractional_year_series_array)
        - 0.002697 * np.cos(3 * fractional_year_series_array)
        + 0.00148 * np.sin(3 * fractional_year_series_array)
    )
    declination_series = [
        SolarDeclination(value=declination, unit="radians")
        for declination in declination_series
    ]

    if angle_output_units == "degrees":
        declination_series = convert_series_to_degrees_if_requested(declination_series, angle_output_units)

    if np.isscalar(timestamps):
        return declinations[0]
    else:
        return np.array(declination_series, dtype=object)
