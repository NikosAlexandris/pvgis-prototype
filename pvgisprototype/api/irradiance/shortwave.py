from devtools import debug
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
    help=f"Estimate the global irradiance time series",
)


def select_location_time_series(data_path, longitude, latitude, inexact_matches_method='nearest'):
    data_array = xr.open_dataarray(data_path)
    location_time_series = data_array.sel(
            lon=longitude,
            lat=latitude,
            method=inexact_matches_method)
    location_time_series.load()  # load into memory for fast processing
    return location_time_series


@app.callback(
        invoke_without_command=True,
        no_args_is_help=True,
        context_settings={"ignore_unknown_options": True})
def estimate_global_irradiance(
        shortwave: Annotated[Path, typer.Argument(
            help='Global irradiance (Surface Incoming Shortwave Irradiance, `ssrd`')], 
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
    """Calculate the global irradiance incident on a solar surface.

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
    direct_irradiance = calculate_direct_inclined_irradiance_pvgis(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamp=timestamp,
        timezone=timezone,
        direct_horizontal_component=direct_horizontal_irradiance,
        mask_and_scale=mask_and_scale,
        inexact_matches_method=inexact_matches_method,
        tolerance=tolerance,
        in_memory=in_memory,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        linke_turbidity_factor=linke_turbidity_factor,
        solar_incidence_angle_model=solar_incidence_angle_model,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    # diffuse horizontal
    # G0
    extraterrestial_normal_irradiance = calculate_extraterrestrial_normal_irradiance(timestamp)

    # extraterrestrial on a horizontal surface requires the solar altitude
    solar_altitude = calculate_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_time_model=solar_time_model,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        )
    # on a horizontal surface : G0h = G0 sin(h0)
    extraterrestial_horizontal_irradiance = extraterrestial_normal_irradiance * sin(
        solar_altitude.value
    )
    # Dhc [W.m-2]
    diffuse_horizontal_component = (
        extraterrestial_normal_irradiance
        * diffuse_transmission_function(solar_altitude.value)
        * diffuse_solar_altitude_function(solar_altitude.value, linke_turbidity_factor)
    )

    reflected_irradiance = calculate_ground_reflected_inclined_irradiance(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamp=timestamp,
        timezone=timezone,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        linke_turbidity_factor=linke_turbidity_factor,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        albedo=albedo,
        direct_horizontal_component=direct_horizontal_irradiance, # time series, optional
        apply_angular_loss_factor=apply_angular_loss_factor,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    shortwave_irradiance = direct_irradiance + diffuse_irradiance

    return shortwave_irradiance
