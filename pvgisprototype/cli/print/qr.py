from datetime import datetime

from pandas import DatetimeIndex
from rich import print

from pvgisprototype.api.quick_response_code import (
    QuickResponseCode,
    generate_quick_response_code,
    generate_quick_response_code_optimal_surface_position,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
)


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
    optimal_surface_position: bool = False,
    output_type: QuickResponseCode = QuickResponseCode.Base64,
) -> None:
    """ """

    if optimal_surface_position:
        quick_response_code = generate_quick_response_code_optimal_surface_position(
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
    else:
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
