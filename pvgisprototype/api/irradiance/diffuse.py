from devtools import debug
"""
Diffuse irradiance
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
from ..series.statistics import calculate_series_statistics
from ..series.statistics import print_series_statistics
from ..series.statistics import export_statistics_to_csv
from pathlib import Path

import xarray as xr
import numpy as np

from scipy.stats import mode
from rich.table import Table
import csv


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
    help=f"Calculate the diffuse from global and direct irradiance time series",
)


def select_location_time_series(data_path, longitude, latitude, inexact_matches_method='nearest'):
    data_array = xr.open_dataarray(data_path)
    location_time_series = data_array.sel(
            lon=longitude,
            lat=latitude,
            method=inexact_matches_method)
    # location_time_series.load()  # load into memory for fast processing
    return location_time_series


@app.callback(
        invoke_without_command=True,
        no_args_is_help=True,
        context_settings={"ignore_unknown_options": True})
def calculate_diffuse_irradiance(
        shortwave: Annotated[Path, typer.Argument(
            help='Global irradiance (Surface Incoming Shortwave Irradiance, `ssrd`')], 
        direct: Annotated[Path, typer.Argument(
            help='Direct (or beam) irradiance (Surface Incoming Direct radiation, `fdir`)')],
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],  # in PVGIS : coloffset
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],  # in PVGIS : rowoffset
        timestamp: Annotated[Optional[datetime], typer.Option(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        start_time: Annotated[Optional[datetime], typer.Option(
            help='Start date of the period')] = None,
        end_time: Annotated[Optional[datetime], typer.Option(
            help='End date of the period')] = None,
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
        statistics: Annotated[bool, typer.Option(
            help='Print summary statistics for the selected series')] = False,
        csv: Annotated[Path, typer.Option(
            help='CSV output filename',
            rich_help_panel='Output')] = 'series_in',
    ):
    """Calculate the diffuse irradiance incident on a solar surface.

    Parameters
    ----------

    Returns
    -------
    diffuse_irradiance: float
        The diffuse radiant flux incident on a surface per unit area in W/m².

    Notes
    -----

    Some of the input arguments to ... in PVGIS' C code:

        # daily_prefix,
        # database_prefix,
        # num_vals_to_read,
        # elevation_file_number_ns,
        # elevation_file_number_ew,
    """
#     global_data_array = xr.open_dataarray(shortwave)  # global is a reserved word!
#     global_location_time_series = global_data_array.sel(
#             lon=longitude,
#             lat=latitude,
#             method=inexact_matches_method)
#     global_location_time_series.load()  # load into memory for fast processing

#     direct_data_array = xr.open_dataarray(direct)
#     direct_location_time_series = direct_data_array.sel(
#             lon=longitude,
#             lat=latitude,
#             method=inexact_matches_method)
#     direct_location_time_series.load()
    global_location_time_series = select_location_time_series(
        shortwave, longitude, latitude
    )
    global_location_time_series.load()  # load into memory for fast processing
    direct_location_time_series = select_location_time_series(
        direct, longitude, latitude
    )
    direct_location_time_series.load()

    if start_time and end_time:
        global_location_time_series = (
            global_location_time_series.sel(time=slice(start_time, end_time)),
        )
        global_location_time_series = (
            direct_location_time_series.sel(time=slice(start_time, end_time)),
        )

    diffuse_irradiance = global_location_time_series - direct_location_time_series

    # in PVGIS' C code -- is this needed? ------------------------------------
    # beam_coefficient = direct_time_series
    # diff_coefficient = global_time_series - direct_time_series
    # hourly_var_data = xr.Dataset({
    #         "beam_coefficient": beam_coefficient,
    #         "diff_coefficient": diff_coefficient,
    # })
    # ------------------------------------------------------------------------

    if statistics:
        data_statistics = calculate_series_statistics(diffuse_irradiance)
        print_series_statistics(data_statistics)
        # export_statistics_to_csv(data_statistics, 'diffuse_irradiance')

    # # debug(locals())
    return diffuse_irradiance
import math

def calculate_angle_loss():
    # Replace with your function
    pass

AOIConstants = [0, 0]  # Replace with your values

def drad_angle_irradiance(sh, bh, sunVarGeom, sunSlopeGeom, sunRadVar):
    locSinSolarAltitude = sunVarGeom['sinSolarAltitude']
    cosslope = math.cos(sunSlopeGeom['slope'])
    sinslope = math.sin(sunSlopeGeom['slope'])

    dh = sunRadVar['cdh']
    gh = bh + dh
    if sunSlopeGeom['aspect'] != 'UNDEF' and sunSlopeGeom['slope'] != 0.:
        kb = bh / (sunRadVar['G_norm_extra'] * locSinSolarAltitude)
        r_sky = (1. + cosslope) / 2.
        a_ln = sunVarGeom['solarAzimuth'] - sunSlopeGeom['aspect']
        ln = a_ln
        if a_ln > math.pi:
            ln = a_ln - 2 * math.pi
        elif a_ln < -math.pi:
            ln = a_ln + 2 * math.pi
        a_ln = ln
        fg = sinslope - sunSlopeGeom['slope'] * cosslope - math.pi * math.sin(sunSlopeGeom['slope'] / 2.) ** 2
        if sunVarGeom['isShadow'] or sh <= 0.:
            fx = r_sky + fg * 0.252271
        elif sunVarGeom['solarAltitude'] >= 0.1:
            fx = ((0.00263 - kb * (0.712 + 0.6883 * kb)) * fg + r_sky) * (1. - kb) + kb * sh / locSinSolarAltitude
        else:
            fx = ((0.00263 - 0.712 * kb - 0.6883 * kb * kb) * fg + r_sky) * (1. - kb) + kb * sinslope * math.cos(a_ln) / (0.1 - 0.008 * sunVarGeom['solarAltitude'])
        dr = dh * fx
        rr = sunRadVar['alb'] * gh * (1 - cosslope) / 2.
    else:
        dr = dh
        rr = 0.

    diff_radiations = [dr, dr]
    refl_radiations = [rr, rr]

    if calculate_angle_loss():
        c1 = 4. / (3. * math.pi)
        diff_coeff_angleloss = sinslope + (math.pi - sunSlopeGeom['slope'] - sinslope) / (1 + cosslope)
        refl_coeff_angleloss = sinslope + (sunSlopeGeom['slope'] - sinslope) / (1 - cosslope)

        diff_loss_factor = 1. - math.exp(-(c1 * diff_coeff_angleloss + AOIConstants[0] * diff_coeff_angleloss ** 2) / AOIConstants[1])
        refl_loss_factor = 1. - math.exp(-(c1 * refl_coeff_angleloss + AOIConstants[0] * refl_coeff_angleloss ** 2) / AOIConstants[1])

        dr *= diff_loss_factor
        rr *= refl_loss_factor
        diff_radiations[0] = dr
        refl_radiations[0] = rr

    return dr, diff_radiations, refl_radiations
