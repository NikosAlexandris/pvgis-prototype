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

def generate_photovoltaic_output_csv(dictionary:dict, latitude:float, longitude:float, timestamps:DatetimeIndex, timezone:ZoneInfo)->DataFrame:
    """Create in memory CSV file with the photovoltaic power output
    """

    # Remove 'Title' and 'Fingerprint' to avoid repeated values
    dictionary.pop("Title", NOT_AVAILABLE)
    dictionary.pop(FINGERPRINT_COLUMN_NAME, NOT_AVAILABLE)
    dictionary.pop(SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME, NOT_AVAILABLE)
    dictionary.pop(SHADING_STATES_COLUMN_NAME, NOT_AVAILABLE)
    dictionary.pop(SUN_HORIZON_POSITIONS_NAME, NOT_AVAILABLE)
    dictionary.pop(SolarPositionParameter.timing, NOT_AVAILABLE)
    dictionary.pop(SOLAR_EVENTS_NAME, NOT_AVAILABLE)
    dictionary.pop(SURFACE_ORIENTATION_COLUMN_NAME, NOT_AVAILABLE)
    dictionary.pop(SURFACE_TILT_COLUMN_NAME, NOT_AVAILABLE)
    dictionary["Longitude"] = longitude
    dictionary["Latitude"] = latitude
    dataframe = DataFrame(dictionary)

    dataframe = dataframe.with_columns([
        Series("Time", timestamps).cast(Datetime) # type: ignore
    ])
    dataframe = dataframe.with_columns([
        col(column).cast(Float32) if dataframe.schema[column] == Float64
        else col(column).cast(Int8) if dataframe.schema[column] == Int64
        else col(column)
        for column in dataframe.columns
    ])
    
    # Reorder columns to have 'Time', 'Latitude', 'Longitude' first
    columns_order = ['Time', 'Latitude', 'Longitude'] + [col for col in dataframe.columns if col not in ['Time', 'Latitude', 'Longitude']]
    dataframe = dataframe.select(columns_order)

    return dataframe.write_csv() # type: ignore

@lru_cache(maxsize=None)
def get_timezones():
    return sorted(zoneinfo.available_timezones())