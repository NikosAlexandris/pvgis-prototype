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
from click import Context
from typer.core import TyperGroup
from enum import Enum
from datetime import datetime
from rich.console import Console
from colorama import Fore, Style
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.hardcodings import check_mark
from pvgisprototype.api.series.hardcodings import x_mark
from pandas import Timestamp
from ..utilities.conversions import convert_to_radians
from ..utilities.timestamp import parse_timestamp
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import ctx_attach_requested_timezone
from ..series.statistics import calculate_series_statistics
from ..series.statistics import print_series_statistics
from ..series.statistics import export_statistics_to_csv
from pathlib import Path
import xarray as xr
import numpy as np
from scipy.stats import mode
from rich.table import Table
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_surface
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_time
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_atmospheric_properties
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output
import csv
from .extraterrestrial import calculate_extraterrestrial_normal_irradiance
from .direct import calculate_direct_horizontal_irradiance
from .loss import calculate_angular_loss_factor_for_nondirect_irradiance
from pvgisprototype.api.geometry.solar_altitude import calculate_solar_altitude
from pvgisprototype.api.geometry.solar_azimuth import calculate_solar_azimuth
from pvgisprototype.models.standard.solar_incidence import calculate_solar_incidence
from pvgisprototype.api.geometry.time_models import SolarTimeModels
from math import sin
from math import cos
from math import pi
from math import atan2
from ..geometry.solar_declination import calculate_solar_declination
from ..geometry.solar_time import model_solar_time
from ..utilities.timestamp import timestamp_to_decimal_hours
from .constants import SOLAR_CONSTANT

from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_shortwave_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_argument_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_argument_solar_altitude
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_argument_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_days_in_a_year
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_verbose


AOIConstants = []
AOIConstants.append(-0.074)
AOIConstants.append(0.155)


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Calculate the diffuse from global and direct irradiance time series",
)
console = Console()


class MethodsForInexactMatches(str, Enum):
    none = None # only exact matches
    pad = 'pad' # ffill: propagate last valid index value forward
    backfill = 'backfill' # bfill: propagate next valid index value backward
    nearest = 'nearest' # use nearest valid index value


def select_location_time_series(
    time_series_filename: Annotated[Path, typer_argument_time_series],
    # longitude: Annotated[Longitude, typer_argument_longitude_in_degrees],
    # latitude: Annotated[Latitude, typer_argument_latitude_in_degrees],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
):
    data_array = xr.open_dataarray(time_series_filename)
    location_time_series = data_array.sel(
            lon=longitude,
            lat=latitude,
            method=inexact_matches_method)
    # location_time_series.load()  # load into memory for fast processing
    return location_time_series


@app.command(
    'from-sarah',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
def calculate_diffuse_horizontal_component_from_sarah(
    shortwave: Annotated[Path, typer_argument_shortwave_irradiance],
    direct: Annotated[Path, typer_argument_direct_horizontal_irradiance],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = 'series_in',
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
):
    """Calculate the diffuse irradiance incident on a solar surface from SARAH
    time series.

    Parameters
    ----------
    shortwave: Path
        Filename of surface short-wave (solar) radiation downwards time series
        (short name : `ssrd`) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth. This parameter
        comprises both direct and diffuse solar radiation.

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
    global_irradiance_location_time_series = select_location_time_series(
        shortwave, longitude, latitude
    )
    global_irradiance_location_time_series.load()  # load into memory for fast processing
    direct_irradiance_location_time_series = select_location_time_series(
        direct, longitude, latitude
    )
    direct_irradiance_location_time_series.load()

    if timestamp:
        # convert timestamp to ISO format string without fractional seconds
        time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        global_irradiance_location_time_series = (
            global_irradiance_location_time_series.sel(time=time)
        )
        direct_irradiance_location_time_series = (
            direct_irradiance_location_time_series.sel(time=time)
        )
    if start_time or end_time:
        # If only start_time is provided, end_time defaults to the end of the series
        if start_time and not end_time:
            end_time = direct_location_time_series.time.values[-1]
            # end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
        # If only end_time is provided, start_time defaults to the beginning of the series
        elif end_time and not start_time:
            start_time = direct_location_time_series.time.values[0]
            # start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
        # If both start_time and end_time are provided, use them as they are
        # Convert start_time and end_time to the correct string format if they're datetime objects
        else:
            # if isinstance(start_time, datetime):
            start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
            # if isinstance(end_time, datetime):
            end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    
        global_irradiance_location_time_series = (
            global_irradiance_location_time_series.sel(time=slice(start_time, end_time))
        )
        direct_irradiance_location_time_series = (
            direct_irradiance_location_time_series.sel(time=slice(start_time, end_time))
        )

    diffuse_horizontal_irradiance = (
        global_irradiance_location_time_series - direct_irradiance_location_time_series
    )

    # in PVGIS' C code -- is this needed? ------------------------------------
    # beam_coefficient = direct_time_series
    # diff_coefficient = global_time_series - direct_time_series
    # hourly_var_data = xr.Dataset({
    #         "beam_coefficient": beam_coefficient,
    #         "diff_coefficient": diff_coefficient,
    # })
    # ------------------------------------------------------------------------

    if diffuse_horizontal_irradiance.size == 1:
        single_value = float(diffuse_horizontal_irradiance.values)
        warning = Fore.YELLOW + f'{exclamation_mark} The selection matches the single value : {single_value}' + Style.RESET_ALL
        logging.warning(warning)
        if verbose:
            typer.echo(Fore.YELLOW + warning)
        return single_value

    # ---------------------------------------------------------- Remove Me ---
    typer.echo(diffuse_horizontal_irradiance.values)
    # ---------------------------------------------------------- Remove Me ---

    if statistics:
        data_statistics = calculate_series_statistics(diffuse_horizontal_irradiance)
        print_series_statistics(data_statistics, title='Diffuse horizontal irradiance from SARAH')
        if csv:
            export_statistics_to_csv(data_statistics, 'diffuse_horizontal_irradiance')

    return diffuse_horizontal_irradiance


@app.command(
        'n-term',
        no_args_is_help=True,
        help=f'N Calculate the N term for the diffuse sky irradiance function',
        rich_help_panel=rich_help_panel_toolbox,
        )
def calculate_term_n(
        kb,
        ):
    """Define the N term

    Parameters
    ----------
    kb: float
        Direct to extraterrestrial irradiance ratio

    Returns
    -------
    N: float
        The N term
    """
    return 0.00263 - 0.712 * kb - 0.6883 * kb ** 2
    

@app.command(
        'sky-irradiance',
        no_args_is_help=True,
        help=f'⇊ Calculate the diffuse clear-sky irradiance',
        rich_help_panel=rich_help_panel_series_irradiance,
        )
def calculate_diffuse_sky_irradiance(
        n: Annotated[float, typer_argument_term_n],
        surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = 45,
        ):
    """Calculate the diffuse sky irradiance

    The diffuse sky irradiance function F(γN) depends on the surface tilt `γN`
    (in radians)

    Parameters
    ----------
    surface_tilt: float (radians)
        The tilt (also referred to as : inclination or slope) angle of a solar
        surface

    n: float
        The term N

    Returns
    -------

    Notes
    -----
    Internally the function calculates first the dimensionless fraction of the
    sky dome viewed by a tilted (or inclined) surface `ri(γN)`.
    """
    sky_view_fraction = (1 + cos(surface_tilt)) / 2
    diffuse_sky_irradiance = sky_view_fraction
    +(
        sin(surface_tilt)
        - surface_tilt
        * cos(surface_tilt)
        - pi
        * sin(surface_tilt / 2) ** 2
    ) * n

    return diffuse_sky_irradiance


@app.command(
        'transmission-function',
        no_args_is_help=True,
        help=f'⇝ Calculate the diffuse transmission function',
        rich_help_panel=rich_help_panel_toolbox,
        )
def diffuse_transmission_function(
    linke_turbidity_factor: Annotated[Optional[float], typer_argument_linke_turbidity_factor] = 2,
        ):
    """ Diffuse transmission function
    """
    return (
        -0.015843
        + 0.030543 * linke_turbidity_factor
        + 0.3797 * linke_turbidity_factor**2
    )


@app.command(
        'diffuse-altitude-coefficients',
        no_args_is_help=True,
        help=f'☀∡ Calculate the diffuse solar altitude coefficients',
        rich_help_panel=rich_help_panel_toolbox,
        )
def diffuse_solar_altitude_coefficients(
    linke_turbidity_factor: Annotated[Optional[float], typer_argument_linke_turbidity_factor] = 2,
        ):
    """
    """
    # calculate common terms only once
    linke_turbidity_factor_squared = linke_turbidity_factor**2
    diffuse_transmission = diffuse_transmission_function(linke_turbidity_factor)
    a1_prime = (
        0.26463
        - 0.061581 * linke_turbidity_factor
        + 0.0031408 * linke_turbidity_factor_squared
    )
    if a1_prime * diffuse_transmission < 0.0022:
        a1 = 0.0022 / diffuse_transmission if diffuse_transmission else a1_prime
    else:
        a1 = a1_prime
    a2 = (
        2.04020
        + 0.018945 * linke_turbidity_factor
        - 0.011161 * linke_turbidity_factor_squared
    )
    a3 = (
        -1.3025
        + 0.039231 * linke_turbidity_factor
        + 0.0085079 * linke_turbidity_factor_squared
    )

    return a1, a2, a3


@app.command(
        'diffuse-solar-altitude',
        no_args_is_help=True,
        help=f'☀∡ Calculate the diffuse solar altitude angle',
        rich_help_panel=rich_help_panel_toolbox,
        )
def diffuse_solar_altitude_function(
    solar_altitude: Annotated[float, typer_argument_solar_altitude],
    linke_turbidity_factor: Annotated[Optional[float], typer_argument_linke_turbidity_factor] = 2,
        ):
    """Diffuse solar altitude function Fd"""
    a1, a2, a3 = diffuse_solar_altitude_coefficients(linke_turbidity_factor)
    return a1 + a2 * sin(solar_altitude) + a3 * sin(solar_altitude) ** 2


# @app.callback(
#         invoke_without_command=True,
#         no_args_is_help=True,
#         context_settings={"ignore_unknown_options": True})
@app.command(
        'inclined',
        no_args_is_help=True,
        help=f'☀∡ Calculate the diffuse irradiance incident on a tilted surface',
        rich_help_panel=rich_help_panel_series_irradiance,
        )
def calculate_diffuse_inclined_irradiance(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    surface_tilt: Annotated[Optional[float], typer_option_surface_tilt] = 45,
    surface_orientation: Annotated[Optional[float], typer_option_surface_orientation] = 180,
    linke_turbidity_factor: Annotated[float, typer_option_linke_turbidity_factor] = 2,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    direct_horizontal_irradiance: Annotated[Optional[Path], typer.Option(
        help='Read horizontal irradiance time series data from a file',)] = None,
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_declination_model: Annotated[SolarDeclinationModels, typer_option_solar_declination_model] = SolarDeclinationModels.pvis,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_argument_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity] = 0.01672,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = 'series_in',
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
):
    """Calculate the diffuse irradiance incident on a solar surface

    Notes
    -----

    In order or appearance:

    - extraterrestial_normal_irradiance : G0
    - extraterrestial_horizontal_irradiance : G0h = G0 sin(h0)
    - kb : Proportion between direct (beam) and extraterrestrial irradiance : Kb
    - diffuse_horizontal_component : Dhc [W.m-2]
    - diffuse_transmission_function() :
    - linke_turbidity_factor :
    - diffuse_solar_altitude_function() :
    - solar_altitude : 
    - calculate_term_n():
    - n : the N term
    - diffuse_sky_irradiance()
    - sine_solar_incidence_angle
    - sine_solar_altitude
    - diffuse_sky_irradiance 
    - calculate_diffuse_sky_irradiance() : F(γN)
    - surface_tilt :
    - diffuse_inclined_irradiance :
    - diffuse_horizontal_component :
    - azimuth_difference :
    - solar_azimuth :
    - surface_orientation :
    - diffuse_irradiance
    """
    # from the model
    direct_horizontal_component = calculate_direct_horizontal_irradiance(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamp=timestamp,
        timezone=timezone,
        linke_turbidity_factor=linke_turbidity_factor,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
    )

    if surface_tilt == 0:  # horizontal surface
        diffuse_irradiance = diffuse_horizontal_component

    else:  # tilted (or inclined) surface
    # Note: in PVGIS: if surface_orientation != 'UNDEF' and surface_tilt != 0:

        # G0
        # day_of_year = timestamp.timetuple().tm_yday
        # extraterrestial_normal_irradiance = calculate_extraterrestrial_normal_irradiance(day_of_year)
        extraterrestial_normal_irradiance = calculate_extraterrestrial_normal_irradiance(timestamp)

        # extraterrestrial on a horizontal surface requires the solar altitude
        solar_altitude = model_solar_altitude(
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

        # proportion between direct (beam) and extraterrestrial irradiance : Kb
        kb = direct_horizontal_component / extraterrestial_horizontal_irradiance

        # Dhc [W.m-2]
        diffuse_horizontal_component = (
            extraterrestial_normal_irradiance
            * diffuse_transmission_function(solar_altitude.value)
            * diffuse_solar_altitude_function(solar_altitude.value, linke_turbidity_factor)
        )

        # the N term
        n = calculate_term_n(kb)
        diffuse_sky_irradiance = calculate_diffuse_sky_irradiance(
            surface_tilt,
            n,
        )

        # surface in shade, requires : solar declination for/and incidence angles
        solar_declination = model_solar_declination(
                timestamp=timestamp,
                timezone=timezone,
                model=solar_declination_model,
                days_in_a_year=days_in_a_year,
                eccentricity_correction_factor=eccentricity_correction_factor,
                perigee_offset=perigee_offset,
                angle_output_units=angle_output_units,
                )
        solar_time = model_solar_time(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                model=solar_time_model,
                refracted_solar_zenith=refracted_solar_zenith,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                time_output_units=time_output_units,
                angle_units=angle_units,
                angle_output_units=angle_output_units,
        )
        solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time)
        hour_angle = np.radians(15) * (solar_time_decimal_hours - 12)
        solar_incidence_angle = calculate_solar_incidence(
            latitude,
            solar_declination,
            surface_tilt,
            surface_orientation,
            hour_angle,
            angle_output_units=angle_output_units,
        )
        if sin(solar_incidence_angle.value) < 0 and solar_altitude.value >=0:

            # F(γN)
            diffuse_sky_irradiance = calculate_diffuse_sky_irradiance(
                    surface_tilt,
                    n=0.25227,  # term N for surfaces in shade
                    )
            diffuse_inclined_irradiance = (
                diffuse_horizontal_component * diffuse_sky_irradiance
            )

        else:  # sunlit surface and non-overcast sky

            if solar_altitude.value >= 0.1:  # radians or 5.7 degrees
                diffuse_inclined_irradiance = diffuse_horizontal_component * (
                    diffuse_sky_irradiance * (1 - kb)
                    + kb * sin(solar_incidence_angle.value) / sin(solar_altitude.value)
                )

            else:  # if solar_altitude.value < 0.1:
                # requires the solar azimuth
                solar_azimuth = calculate_solar_azimuth(
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

                # Normalize the azimuth difference to be within the range -pi to pi
                # A0 : solar azimuth _measured from East_ in radians
                # ALN : angle between the vertical surface containing the normal to the
                #   surface and vertical surface passing through the centre of the solar
                #   disc [rad]
                azimuth_difference = solar_azimuth.value - surface_orientation
                azimuth_difference = atan2(sin(azimuth_difference), cos(azimuth_difference))
                diffuse_inclined_irradiance = diffuse_horizontal_component * (
                    diffuse_sky_irradiance * (1 - kb)
                    + kb
                    * sin(surface_tilt)
                    * cos(azimuth_difference)
                    / (0.1 - 0.008 * solar_altitude.value)
                )
        # finally, we need to set
        diffuse_irradiance = diffuse_inclined_irradiance

    # one more thing
    if apply_angular_loss_factor:

        diffuse_irradiance_angular_loss_coefficient = sin(surface_tilt) + (
            pi - surface_tilt - sin(surface_tilt)
        ) / (1 + cos(surface_tilt))
        diffuse_irradiance_loss_factor = calculate_angular_loss_factor_for_nondirect_irradiance(
            angular_loss_coefficient=diffuse_irradiance_angular_loss_coefficient,
            solar_incidence_angle_1=AOIConstants[0],
            solar_incidence_angle_2=AOIConstants[1],
        )

        diffuse_irradiance *= diffuse_irradiance_loss_factor

    # if statistics:
    #     data_statistics = calculate_series_statistics(diffuse_irradiance)
    #     print_series_statistics(data_statistics, title='Diffuse horizontal irradiance from SARAH')
    #     if csv:
    #         export_statistics_to_csv(data_statistics, 'diffuse_horizontal_component')

    # ---------------------------------------------------------- Remove Me ---
    typer.echo(diffuse_irradiance)
    # ---------------------------------------------------------- Remove Me ---
    if verbose:
        print(locals())

    return diffuse_irradiance
