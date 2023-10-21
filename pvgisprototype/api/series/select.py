from devtools import debug
from typing import Any
from typing import Optional
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from datetime import datetime
from pathlib import Path
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
import logging
from pvgisprototype.api.series.log import logger
from pvgisprototype.api.series.utilities import select_location_time_series
from pvgisprototype.api.series.models import MethodsForInexactMatches
from pvgisprototype.api.series.utilities import get_scale_and_offset
from colorama import Fore
from colorama import Style
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.hardcodings import check_mark
from pvgisprototype.api.series.hardcodings import x_mark


def select_time_series(
    time_series: Path,
    longitude: Longitude,
    latitude: Latitude,
    timestamps: Optional[Any],
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    # convert_longitude_360: bool = False,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodsForInexactMatches = None,
    tolerance: Optional[float] = 0.1, # Customize default if needed
    in_memory: bool = False,
    variable_name_as_suffix: bool = True,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Select location series"""

    # if convert_longitude_360:
    #     longitude = longitude % 360
    # warn_for_negative_longitude(longitude)

    logger.handlers = []  # Remove any existing handlers
    # file_handler = logging.FileHandler(f'{output_filename}_{time_series.name}.log')
    file_handler = logging.FileHandler(f'{time_series.name}.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s, %(msecs)d; %(levelname)-8s; %(lineno)4d: %(message)s", datefmt="%I:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
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
    )
    # ------------------------------------------------------------------------
    if start_time or end_time:
        timestamps = None  # we don't need a timestamp anymore!

        if start_time and not end_time:  # set `end_time` to end of series
            end_time = location_time_series.time.values[-1]
            # end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')

        elif end_time and not start_time:  # set `start_time` to beginning of series
            start_time = location_time_series.time.values[0]
            # start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')

        else:  # Convert `start_time` & `end_time` to the correct string format
            # if isinstance(start_time, datetime):
            start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
            # if isinstance(end_time, datetime):
            end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    
        location_time_series = (
            location_time_series.sel(time=slice(start_time, end_time))
        )

    
    # # if 'timestamps' is a single datetime object, parse it
    # if isinstance(timestamps, datetime):
    #     timestamps = parse_timestamp_series(timestamps)

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
            Fore.YELLOW
            + f"{exclamation_mark} The selected timestamp "
            + Fore.GREEN
            # + f"{location_time_series[location_time_series.indexes].time.values}"
            + f"{location_time_series.time.values}"
            + Fore.YELLOW
            + f" matches the single value "
            + Fore.GREEN
            + f'{single_value}'
            + Style.RESET_ALL
        )
        logger.warning(warning)
        if verbose > 0:
            print(Fore.YELLOW + warning)
        if verbose == 3:
            debug(locals())

        return single_value

    if verbose > 5:
        debug(locals())

    return location_time_series
