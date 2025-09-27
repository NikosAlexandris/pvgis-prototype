from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, Query

from pvgisprototype.api.series.csv import to_csv
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.constants import TOLERANCE_DEFAULT, VERBOSE_LEVEL_DEFAULT
from pvgisprototype.web_api.dependency import process_series_timestamp


async def select(
    time_series: Path,
    longitude: float = Query(None),
    latitude: float = Query(None),
    time_series_2: Path = Query(None),
    timestamps: Optional[List[datetime]] = Depends(process_series_timestamp),
    start_time: datetime | None = Query(None),
    frequency: str | None = Query("H"),
    end_time: datetime | None = Query(None),
    mask_and_scale: bool = Query(False),
    neighbor_lookup: MethodForInexactMatches = Query(None),
    tolerance: float | None = Query(TOLERANCE_DEFAULT),
    in_memory: bool = Query(False),
    statistics: bool = Query(False),
    csv: Path = Query("series.csv"),
    output_filename: Path = Query("series_in"),
    variable_name_as_suffix: bool = Query(True),
    rounding_places: int | None = Query(5),
    verbose: int = Query(VERBOSE_LEVEL_DEFAULT),
):
    location_time_series = select_time_series(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
    )
    location_time_series_2 = select_time_series(
        time_series=time_series_2,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
    )

    # statistics after echoing series which might be Long!

    if statistics:
        print_series_statistics(
            data_array=location_time_series,
            title="Selected series",
        )

    elif csv:
        # export_statistics_to_csv(
        #     data_array=location_time_series,
        #     filename=csv,
        # )
        to_csv(
            x=location_time_series,
            path=str(csv),
        )
    from devtools import debug

    debug(locals())
    return location_time_series.values.tolist()
