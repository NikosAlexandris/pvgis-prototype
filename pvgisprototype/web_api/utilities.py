import zoneinfo
from functools import lru_cache
from pandas import DatetimeIndex
from zoneinfo import ZoneInfo
from polars import (DataFrame, 
                    Series,
                    Datetime,
                    Float32,
                    Float64,
                    Int8,
                    Int64,
                    col,
                    )
from pvgisprototype.api.position.models import SolarPositionParameter
from pvgisprototype.constants import (
    NOT_AVAILABLE,
    FINGERPRINT_COLUMN_NAME,
    SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME,
    SHADING_STATES_COLUMN_NAME,
    SUN_HORIZON_POSITIONS_NAME,
    SOLAR_EVENTS_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_TILT_COLUMN_NAME
)


def generate_photovoltaic_output_csv(
    dictionary: dict,
    latitude: float,
    longitude: float,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
) -> DataFrame:
    """
    Create in memory CSV file with the photovoltaic power output
    """
    # Remove 'Title' and 'Fingerprint' to avoid repeated values
    keys_to_remove = [
        "Title",
        FINGERPRINT_COLUMN_NAME,
        SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME,
        SHADING_STATES_COLUMN_NAME,
        SUN_HORIZON_POSITIONS_NAME,
        SolarPositionParameter.timing,
        SOLAR_EVENTS_NAME,
        SURFACE_ORIENTATION_COLUMN_NAME,
        SURFACE_TILT_COLUMN_NAME,
    ]
    for key in keys_to_remove:
        dictionary.pop(key, NOT_AVAILABLE)

    dictionary["Longitude"] = longitude
    dictionary["Latitude"] = latitude
    dataframe = DataFrame(dictionary)
    dataframe = dataframe.with_columns(
        [Series("Time", timestamps).cast(Datetime)]  # type: ignore
    )
    dataframe = dataframe.with_columns(
        [
            (
                col(column).cast(Float32)
                if dataframe.schema[column] == Float64
                else (
                    col(column).cast(Int8)
                    if dataframe.schema[column] == Int64
                    else col(column)
                )
            )
            for column in dataframe.columns
        ]
    )

    # ----------------------------- Why is this happening in first place ? ---
    # Reorder columns to have 'Time', 'Latitude', 'Longitude' first
    columns_order = ["Time", "Latitude", "Longitude"] + [
        column
        for column in dataframe.columns
        if column not in ["Time", "Latitude", "Longitude"]
    ]
    dataframe = dataframe.select(columns_order)
    # ----------------------------- Why is this happening in first place ? ---

    return dataframe.write_csv()  # type: ignore


@lru_cache(maxsize=None)
def get_timezones():
    return sorted(zoneinfo.available_timezones())
