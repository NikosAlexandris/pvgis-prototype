from enum import Enum
import numpy
from pandas import DatetimeIndex
import qrcode
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.quick_response_code import generate_quick_response_code
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.api.series.statistics import calculate_mean_of_series_per_time_unit, calculate_sum_and_percentage
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT, DATA_TYPE_DEFAULT, FINGERPRINT_COLUMN_NAME, GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME, IRRADIANCE_UNIT_K, PHOTOVOLTAIC_POWER_COLUMN_NAME, PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, POWER_UNIT, ROUNDING_PLACES_DEFAULT, SURFACE_ORIENTATION_COLUMN_NAME, SURFACE_TILT_COLUMN_NAME, SYSTEM_EFFICIENCY_COLUMN_NAME
from datetime import datetime
from typing import Any
from PIL.Image import Image
from rich import print


def print_quick_response_code(
    dictionary: dict,
    longitude: float,
    latitude: float,
    elevation: float | None = None,
    surface_orientation: bool = True,
    surface_tilt: bool = True,
    timestamps: DatetimeIndex = DatetimeIndex([datetime.now()]),
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    output_type: QuickResponseCode = QuickResponseCode.Base64,
) -> None:
    """
    """
    quick_response_code = generate_quick_response_code(
        dictionary=dictionary,
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_orientation=True,
        surface_tilt=True,
        timestamps=timestamps,
        rounding_places=ROUNDING_PLACES_DEFAULT,
        output_type=output_type,
    )
    if output_type.value == QuickResponseCode.Base64:
        print(quick_response_code)

    if output_type.value == QuickResponseCode.Image:
        quick_response_code.print_ascii()
