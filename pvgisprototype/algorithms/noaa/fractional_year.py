from datetime import datetime
from typing import Optional
from typing import Union
from typing import Sequence
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateFractionalYearNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateFractionalYearNOAATimeSeriesInput
from math import pi
from ...api.utilities.conversions import convert_to_degrees_if_requested

from pvgisprototype import FractionalYear

import numpy as np


@validate_with_pydantic(CalculateFractionalYearNOAAInput)
def calculate_fractional_year_noaa(
        timestamp: datetime,
        angle_output_units: str = "radians",  # Returned, not used!
    ) -> FractionalYear:
    """Calculate fractional year in radians """
    fractional_year = (
        2
        * pi
        / 365
        * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
    )

    # slightly less than 0 ?
    if -pi/365 <= fractional_year < 0:  # for example, consider values > -1e-6 as close enough to 0
        fractional_year = 0

    if not 0 <= fractional_year < 2 * pi:
        raise ValueError(f'The calculated fractional year {fractional_year} is outside the expected range [0, 2*pi] radians')

    fractional_year = FractionalYear(value=fractional_year, unit='radians')

    # fractional_year = convert_to_degrees_if_requested(fractional_year, angle_output_units)
    # if angle_output_units == 'degrees':
    #     if not 0 <= fractional_year < 360:
    #         raise ValueError('Fractional year (in degrees) must be in the range [0, 360]')
            
    return fractional_year


@validate_with_pydantic(CalculateFractionalYearNOAATimeSeriesInput)
def calculate_fractional_year_time_series_noaa(
        timestamps: Union[datetime, Sequence[datetime]],
        angle_output_units: str = "radians"
    ) -> Union[FractionalYear, np.ndarray]:

    fractional_years = []
    timestamps = np.atleast_1d(timestamps)  # timestamps as array
    # ------------------------------------------------------------------------
    for timestamp in timestamps:
        fractional_year = (
            2
            * np.pi
            / 365
            * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
        )

        # slightly less than 0 ?
        if -np.pi / 365 <= fractional_year < 0:
            fractional_year = 0

        if not 0 <= fractional_year < 2 * np.pi:
            raise ValueError(
                f"The calculated fractional year {fractional_year} is outside the expected range [0, 2*pi] radians"
            )

        fractional_year = FractionalYear(value=fractional_year, unit=angle_output_units)
        fractional_years.append(fractional_year)
    # ------------------------------------------------------------------------
    fractional_years = np.array(fractional_years, dtype=object)

    if np.isscalar(timestamps):
        return fractional_years[0]
    else:
        return fractional_years
