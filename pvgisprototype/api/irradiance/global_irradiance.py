"""
Global irradiance
"""

import logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('error.log'),  # Save log to a file
        logging.StreamHandler()  # Print log to the console
    ]
)
import typer
from typer import Argument, Option
from typing import Annotated
from typing import Optional
from typing import Union
from enum import Enum
from datetime import datetime
from rich.console import Console
from pandas import Timestamp
from ..utilities.conversions import convert_to_radians
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from pathlib import Path

import xarray as xr
import numpy as np


class MethodsForInexactMatches(str, Enum):
    none = None # only exact matches
    pad = 'pad' # ffill: propagate last valid index value forward
    backfill = 'backfill' # bfill: propagate next valid index value backward
    nearest = 'nearest' # use nearest valid index value


console = Console()
app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the global solar irradiation",
)


@app.callback(
        invoke_without_command=True,
        no_args_is_help=True,
        context_settings={"ignore_unknown_options": True})
def calculate_global_irradiance(
        sis: Path,
        sid: Path,
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],  # in PVGIS : coloffset
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],  # in PVGIS : rowoffset
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        start_time: datetime = Argument(None, help='Start date of the period'),
        end_time: datetime = Argument(None, help='End date of the period'),
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        inexact_matches_method: Annotated[MethodsForInexactMatches, typer.Option(
            '-m',
            '--method-for-inexact-matches',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Model to calculate solar position")] = MethodsForInexactMatches.nearest,
    ):
    """Calculate the global irradiatiance incident on a solar surface.

    Parameters
    ----------

    Returns
    -------
    global_irradiance: float
        The global radiant flux incident on a surface per unit area in W/m².

    Notes
    -----

    Some of the input arguments to ... in PVGIS' C code:

        # daily_prefix,
        # database_prefix,
        # num_vals_to_read,
        # elevation_file_number_ns,
        # elevation_file_number_ew,
    """
    sis_data_array = xr.open_dataarray(sis)
    sid_data_array = xr.open_dataarray(sid)

    sis_location_time_series = sis_data_array.sel(
            lon=longitude,
            lat=latitude,
            method=inexact_matches_method)

    sid_location_time_series = sid_data_array.sel(
            lon=longitude,
            lat=latitude,
            method=inexact_matches_method)

    sis_location_time_series.load()  # load into memory for fast processing
    sid_location_time_series.load()

    if start_time and end:
        sis_location_time_series = sis_location_time_series.sel(time=slice(start_time, end_time)),
        sis_location_time_series = sid_location_time_series.sel(time=slice(start_time, end_time)),


    diffuse_irradiance = sis_location_time_series - sid_location_time_series
    total_global_irradiance = sis_location_time_series.where(sis_location_time_series > 0).sum()  # sis_sum
    average_global_irradiance = sis_location_time_series.where(sis_location_time_series > 0).mean()  # sis_sum

    # in PVGIS' C code -- is this needed? ------------------------------------
    # beam_coefficient = sid_time_series
    # diff_coefficient = sis_time_series - sid_time_series
    # hourly_var_data = xr.Dataset({
    #         "beam_coefficient": beam_coefficient,
    #         "diff_coefficient": diff_coefficient,
    # })
    # ------------------------------------------------------------------------

    # print(f'diffuse: {diffuse_irradiance}')
    print(f'diffuse: {diffuse_irradiance.values}')
    # print(f'global: {global_irradiance}')
    print(f'Total global: {total_global_irradiance.values}')
    print(f'Average global: {average_global_irradiance.values}')

    return total_global_irradiance, average_global_irradiance


import xarray as xr
import numpy as np
