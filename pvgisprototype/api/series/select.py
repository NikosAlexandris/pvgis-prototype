from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from typing import Any
from typing import Optional
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from datetime import datetime
from pathlib import Path
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.api.series.utilities import select_location_time_series
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.series.utilities import get_scale_and_offset
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.hardcodings import check_mark
from pvgisprototype.api.series.hardcodings import x_mark
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pandas import DatetimeIndex


@log_function_call
@cached(cache={}, key=custom_hashkey)
def select_time_series(
    time_series: Path,
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    remap_to_month_start: Optional[bool] = False,
    # convert_longitude_360: bool = False,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodForInexactMatches = None,
    tolerance: Optional[float] = 0.1, # Customize default if needed
    in_memory: bool = False,
    variable_name_as_suffix: bool = True,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
):
    """Select location series"""
    if time_series is None:
        return None

    # if convert_longitude_360:
    #     longitude = longitude % 360
    # warn_for_negative_longitude(longitude)

    logger.info(f'Dataset : {time_series.name}')
    logger.info(f'Path to : {time_series.parent.absolute()}')
    scale_factor, add_offset = get_scale_and_offset(time_series)
    logger.info(f'Scale factor : {scale_factor}, Offset : {add_offset}')

    if (longitude and latitude):
        coordinates = f'Coordinates : {longitude}, {latitude}'
        logger.info(coordinates)

    location_time_series = select_location_time_series(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        verbose=verbose,
        # log=log,
    )
    # ------------------------------------------------------------------------
    if (start_time or end_time) and not remap_to_month_start:
        timestamps = None  # we don't need a timestamp anymore!

        if start_time and not end_time:  # set `end_time` to end of series
            end_time = location_time_series.time.values[-1]

        elif end_time and not start_time:  # set `start_time` to beginning of series
            start_time = location_time_series.time.values[0]

        else:  # Convert `start_time` & `end_time` to the correct string format
            start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
            end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    
        try:
            location_time_series = (
                location_time_series.sel(time=slice(start_time, end_time))
            )
        except Exception as e:
            print(f"No data found for the given period {start_time} and {end_time}.")

    if remap_to_month_start:
        from pandas import date_range
        month_start_timestamps = date_range(start=timestamps.min().normalize(), end=timestamps.max(), freq='MS')
        try:
            location_time_series = location_time_series.sel(
                time=month_start_timestamps, method=neighbor_lookup
            )
        except Exception as e:
            print(f"No data found for the given 'month start' timestamps {month_start_timestamps}.")

    if timestamps is not None and not start_time and not end_time:
        if len(timestamps) == 1:
            start_time = end_time = timestamps[0]
        
        try:
            location_time_series = (
                location_time_series.sel(time=timestamps, method=neighbor_lookup)
            )
        except KeyError:
            print(f"No data found for one or more of the given {timestamps}.")

    if location_time_series.size == 1:
        single_value = float(location_time_series.values)
        warning = (
            f"{exclamation_mark} The selected timestamp "
            + f"{location_time_series.time.values}"
            + f" matches the single value "
            + f'{single_value}'
        )
        logger.warning(warning)

        if verbose > 0:
            print(warning)

    log_data_fingerprint(
            data=location_time_series.values,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
            )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return location_time_series
