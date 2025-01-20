from zoneinfo import ZoneInfo
from pvgisprototype.constants import (
    LATITUDE_COLUMN_NAME,
    LONGITUDE_COLUMN_NAME,
    NOT_AVAILABLE,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_NAME,
    TIME_ALGORITHM_NAME,
    UNIT_NAME,
    UNITLESS,
)


def build_caption(
    longitude,
    latitude,
    rounded_table,
    timezone,
    user_requested_timezone,
    minimum_value = None,
    maximum_value = None,
):
    """
    Notes
    -----
    Add the surface orientation and tilt only if they exist in the input
    `rounded_table` !

    """
    first_model = next(iter(rounded_table))
    caption = (
        f"[underline]Position[/underline]  "
        f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold], "
        + (
            f"Orientation : [bold blue]{rounded_table[first_model].get(SURFACE_ORIENTATION_NAME)}[/bold blue], "
            if rounded_table[first_model].get(SURFACE_ORIENTATION_NAME) is not None
            else ""
        )
        + (
            f"Tilt : [bold blue]{rounded_table[first_model].get(SURFACE_TILT_NAME)}[/bold blue] "
            if rounded_table[first_model].get(SURFACE_TILT_NAME) is not None
            else ""
        )
        + f"[dim]{rounded_table[first_model].get(UNIT_NAME, UNITLESS)}[/dim]"
        f"\n[underline]Algorithms[/underline]  "  # ---------------------------
        f"Timing : [bold]{rounded_table[first_model].get(TIME_ALGORITHM_NAME, NOT_AVAILABLE)}[/bold], "
    )
        # f"Positioning: {rounded_table[first_model].get(POSITIONING_ALGORITHM_NAME, NOT_AVAILABLE)}, "
        # f"Incidence: {rounded_table[first_model].get(INCIDENCE_ALGORITHM_NAME, NOT_AVAILABLE)}\n"
        # f"[underline]Definitions[/underline]  "
        # f"Azimuth origin: {rounded_table[first_model].get(AZIMUTH_ORIGIN_NAME, NOT_AVAILABLE)}, "
        # f"Incidence angle: {rounded_table[first_model].get(INCIDENCE_DEFINITION, NOT_AVAILABLE)}\n"

    if user_requested_timezone != ZoneInfo('UTC'):
        caption += f"Local Zone : [bold]{user_requested_timezone}[/bold], "
    else:
        caption += f"Zone : [bold]{timezone}[/bold], "

    if minimum_value:
        caption += f"Minimum : {minimum_value}"

    if maximum_value:
        caption += f"Minimum : {maximum_value}"

    return caption
