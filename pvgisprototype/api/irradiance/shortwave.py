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
from pvgisprototype.api.irradiance.direct import calculate_direct_inclined_irradiance_pvgis
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.series.statistics import calculate_series_statistics
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.api.series.statistics import export_statistics_to_csv
from pathlib import Path

from pvgisprototype.cli.typer_parameters import typer_argument_shortwave_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method

import xarray as xr
import numpy as np

from scipy.stats import mode
from rich.table import Table
import csv

from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI


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
)


@app.callback(
    invoke_without_command=True,
    no_args_is_help=True,
    context_settings={"ignore_unknown_options": True},
    help=f"Estimate the global (shortwave) irradiance time series {NOT_IMPLEMENTED_CLI}",
)
def estimate_global_irradiance(
    shortwave: Annotated[Path, typer_argument_shortwave_irradiance],
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
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
        direct_horizontal_component=direct_horizontal_component,
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
        solar_position_models=solar_position_models,
        solar_time_model=solar_time_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        verbose=verbose,
        )
    # on a horizontal surface : G0h = G0 sin(h0)
    extraterrestial_horizontal_irradiance = extraterrestial_normal_irradiance * sin(
        solar_altitude.radians
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
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    global_irradiance = direct_irradiance + diffuse_irradiance + reflected_irradiance

    return global_irradiance
