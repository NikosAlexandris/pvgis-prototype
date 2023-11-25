from devtools import debug
"""
Diffuse irradiance
"""

from rich.logging import RichHandler
from loguru import logger
logger.remove()  # the default handler
logger.add(RichHandler())
import typer
from typing import Annotated
from typing import Optional
from datetime import datetime
from rich import print
from rich.console import Console
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.statistics import calculate_series_statistics
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.api.series.statistics import export_statistics_to_csv
from pathlib import Path
import numpy as np
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from .extraterrestrial import calculate_extraterrestrial_normal_irradiance
from .direct import calculate_direct_horizontal_irradiance
from .loss import calculate_angular_loss_factor_for_nondirect_irradiance
from pvgisprototype.api.geometry.altitude import model_solar_altitude
from pvgisprototype.api.geometry.azimuth import model_solar_azimuth
from pvgisprototype.algorithms.pvis.solar_incidence import calculate_solar_incidence_pvis
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.series.models import MethodsForInexactMatches
from pvgisprototype.api.series.utilities import select_location_time_series
from math import sin
from math import cos
from math import pi
from math import atan2
from pvgisprototype.api.geometry.time import model_solar_time
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_time_series
from pvgisprototype.cli.typer_parameters import typer_argument_global_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_longitude_in_degrees
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude_in_degrees
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_argument_term_n
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_argument_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_argument_solar_altitude
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_argument_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TERM_N_IN_SHADE
from pvgisprototype.constants import RADIANS


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Calculate the diffuse irradiance incident on a solar surface",
)
console = Console()


@app.command(
    'from-sarah',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
def calculate_diffuse_horizontal_component_from_sarah(
    shortwave: Annotated[Path, typer_argument_global_horizontal_irradiance],
    direct: Annotated[Path, typer_argument_direct_horizontal_irradiance],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    nearest_neighbor_lookup: Annotated[bool, typer_option_nearest_neighbor_lookup] = False,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = 'series_in',
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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
    """
    global_horizontal_irradiance_location_time_series = select_location_time_series(
        shortwave, longitude, latitude  # global is a reserved word!
    )
    global_horizontal_irradiance_location_time_series.load()  # load into memory for fast processing
    direct_horizontal_irradiance_location_time_series = select_location_time_series(
        direct, longitude, latitude
    )
    direct_horizontal_irradiance_location_time_series.load()

    # ------------------------------------------------------------------------
    if start_time or end_time:
        timestamp = None  # we don't need a timestamp anymore!

        if start_time and not end_time:  # set `end_time` to end of series
            end_time = direct_horizontal_irradiance_location_time_series.time.values[
                -1
            ]  #
            # assuming it'd be identical reading global_horizontal_irradiance_location_time_series

        elif end_time and not start_time:  # set `start_time` to beginning of series
            start_time = direct_horizontal_irradiance_location_time_series.time.values[
                0
            ]
            # assuming it'd be identical reading global_horizontal_irradiance_location_time_series

        else:  # Convert `start_time` & `end_time` to the correct string format
            start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

        global_horizontal_irradiance_location_time_series = (
            global_horizontal_irradiance_location_time_series.sel(
                time=slice(start_time, end_time)
            )
        )
        direct_horizontal_irradiance_location_time_series = (
            direct_horizontal_irradiance_location_time_series.sel(
                time=slice(start_time, end_time)
            )
        )

    if timestamp and not start_time and not end_time:
        # convert timestamp to ISO format string without fractional seconds
        time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if not nearest_neighbor_lookup:
            inexact_matches_method = None
        global_horizontal_irradiance_location_time_series = (
            global_horizontal_irradiance_location_time_series.sel(
                time=time, method=inexact_matches_method
            )
        )
        direct_horizontal_irradiance_location_time_series = (
            direct_horizontal_irradiance_location_time_series.sel(
                time=time, method=inexact_matches_method
            )
        )
    # ------------------------------------------------------------------------

    diffuse_horizontal_irradiance = (
        global_horizontal_irradiance_location_time_series
        - direct_horizontal_irradiance_location_time_series
    )

    if diffuse_horizontal_irradiance.size == 1:
        single_value = float(diffuse_horizontal_irradiance.values)
        warning = (
            f"{exclamation_mark} The selected timestamp "
            + f"{diffuse_horizontal_irradiance[diffuse_horizontal_irradiance.indexes].time.values}"
            + f" matches the single value "
            + f"{single_value}"
        )
        logger.warning(warning)
        if verbose == 3:
            debug(locals())

        if verbose > 0:
            print(f'{warning}')

        return single_value

    # statistics after echoing series which might be Long!
    if statistics:
        data_statistics = calculate_series_statistics(diffuse_horizontal_irradiance)
        print_series_statistics(
            data_statistics, title="Diffuse horizontal irradiance from SARAH"
        )
        if csv:
            export_statistics_to_csv(data_statistics, "diffuse_horizontal_irradiance")

    if verbose == 3:
        debug(locals())

    if verbose > 0:
        print(f"Series : {diffuse_horizontal_irradiance.values}")

    return diffuse_horizontal_irradiance


@app.command(
    'n-term',
    no_args_is_help=True,
    help=f'N Calculate the N term for the diffuse sky irradiance function',
    rich_help_panel=rich_help_panel_toolbox,
)
def calculate_term_n(
    kb: float,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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
    if verbose == 3:
        debug(locals())
    return 0.00263 - 0.712 * kb - 0.6883 * kb ** 2
    

@app.command(
    "sky-irradiance",
    no_args_is_help=True,
    help=f"⇊ Calculate the diffuse sky irradiance",
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
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """ Diffuse transmission function
    """
    diffuse_transmission = (
        -0.015843
        + 0.030543 * linke_turbidity_factor
        + 0.0003797 * linke_turbidity_factor ** 2
    )

    if verbose == 3:
        debug(locals())

    return diffuse_transmission


@app.command(
        'diffuse-altitude-coefficients',
        no_args_is_help=True,
        help=f'☀∡ Calculate the diffuse solar altitude coefficients',
        rich_help_panel=rich_help_panel_toolbox,
        )
def diffuse_solar_altitude_coefficients(
    linke_turbidity_factor: Annotated[Optional[float], typer_argument_linke_turbidity_factor] = 2,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """ """
    # calculate common terms only once
    linke_turbidity_factor_squared = linke_turbidity_factor.value**2
    diffuse_transmission = diffuse_transmission_function(linke_turbidity_factor.value)
    a1_prime = (
        0.26463
        - 0.061581 * linke_turbidity_factor.value
        + 0.0031408 * linke_turbidity_factor_squared
    )
    if a1_prime * diffuse_transmission < 0.0022:
        a1 = 0.0022 / diffuse_transmission if diffuse_transmission else a1_prime
    else:
        a1 = a1_prime
    a2 = (
        2.04020
        + 0.018945 * linke_turbidity_factor.value
        - 0.011161 * linke_turbidity_factor_squared
    )
    a3 = (
        -1.3025
        + 0.039231 * linke_turbidity_factor.value
        + 0.0085079 * linke_turbidity_factor_squared
    )

    if verbose == 3:
        debug(locals())

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
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Diffuse solar altitude function Fd"""
    a1, a2, a3 = diffuse_solar_altitude_coefficients(linke_turbidity_factor)
    return a1 + a2 * sin(solar_altitude) + a3 * sin(solar_altitude) ** 2


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
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    direct_horizontal_irradiance: Annotated[Optional[Path], typer_argument_direct_horizontal_irradiance] = None,
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SolarPositionModels.pvlib,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_argument_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = 'series_in',
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the diffuse irradiance incident on a solar surface

    Notes
    -----

    In order or appearance:

    - extraterrestrial_normal_irradiance : G0
    - extraterrestrial_horizontal_irradiance : G0h = G0 sin(h0)
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
        # extraterrestrial_normal_irradiance = calculate_extraterrestrial_normal_irradiance(day_of_year)
        extraterrestrial_normal_irradiance = calculate_extraterrestrial_normal_irradiance(timestamp)

        # extraterrestrial on a horizontal surface requires the solar altitude
        solar_altitude = model_solar_altitude(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            solar_position_model=solar_position_model,
            solar_time_model=solar_time_model,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            verbose=0,
        )

        # on a horizontal surface : G0h = G0 sin(h0)
        extraterrestrial_horizontal_irradiance = extraterrestrial_normal_irradiance * sin(
            solar_altitude.radians
        )

        # proportion between direct (beam) and extraterrestrial irradiance : Kb
        kb = direct_horizontal_component / extraterrestrial_horizontal_irradiance

        # Dhc [W.m-2]
        diffuse_horizontal_component = (
            extraterrestrial_normal_irradiance
            * diffuse_transmission_function(solar_altitude.radians)
            * diffuse_solar_altitude_function(solar_altitude.radians, linke_turbidity_factor)
        )

        # the N term
        n = calculate_term_n(kb)
        diffuse_sky_irradiance = calculate_diffuse_sky_irradiance(
            surface_tilt,
            n,
        )

        # surface in shade, requires solar incidence
        solar_time = model_solar_time(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            model=solar_time_model,
            refracted_solar_zenith=refracted_solar_zenith,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
        )
        solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time)
        hour_angle = np.radians(15) * (solar_time_decimal_hours - 12)
        solar_incidence_angle = calculate_solar_incidence_pvis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            hour_angle=hour_angle,
            verbose=verbose,
        )
        if sin(solar_incidence_angle.radians) < 0 and solar_altitude.radians >=0:

            # F(γN)
            diffuse_sky_irradiance = calculate_diffuse_sky_irradiance(
                    surface_tilt,
                    n=TERM_N_IN_SHADE,
                    )
            diffuse_inclined_irradiance = (
                diffuse_horizontal_component * diffuse_sky_irradiance
            )

        else:  # sunlit surface and non-overcast sky

            if solar_altitude.radians >= 0.1:  # radians or 5.7 degrees
                diffuse_inclined_irradiance = diffuse_horizontal_component * (
                    diffuse_sky_irradiance * (1 - kb)
                    + kb * sin(solar_incidence_angle.radians) / sin(solar_altitude.radians)
                )

            else:  # if solar_altitude.radians < 0.1:
                # requires the solar azimuth
                solar_azimuth = model_solar_azimuth(
                    longitude=longitude,
                    latitude=latitude,
                    timestamp=timestamp,
                    timezone=timezone,
                    solar_time_model=solar_time_model,
                    apply_atmospheric_refraction=apply_atmospheric_refraction,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                )

                # Normalize the azimuth difference to be within the range -pi to pi
                # A0 : solar azimuth _measured from East_ in radians
                # ALN : angle between the vertical surface containing the normal to the
                #   surface and vertical surface passing through the centre of the solar
                #   disc [rad]
                azimuth_difference = solar_azimuth.radians - surface_orientation
                azimuth_difference = atan2(sin(azimuth_difference), cos(azimuth_difference))
                diffuse_inclined_irradiance = diffuse_horizontal_component * (
                    diffuse_sky_irradiance * (1 - kb)
                    + kb
                    * sin(surface_tilt)
                    * cos(azimuth_difference)
                    / (0.1 - 0.008 * solar_altitude.radians)
                    / (0.1 - 0.008 * solar_altitude.radians)
                )
        # finally, we need to set
        diffuse_irradiance = diffuse_inclined_irradiance

    # one more thing
    if apply_angular_loss_factor:
        diffuse_irradiance_angular_loss_coefficient = sin(surface_tilt) + (
            pi - surface_tilt - sin(surface_tilt)
        ) / (1 + cos(surface_tilt))
        diffuse_irradiance_loss_factor = (
            calculate_angular_loss_factor_for_nondirect_irradiance(
                indirect_angular_loss_coefficient=diffuse_irradiance_angular_loss_coefficient,
            )
        )
        diffuse_irradiance *= diffuse_irradiance_loss_factor

    # if statistics:
    #     data_statistics = calculate_series_statistics(diffuse_irradiance)
    #     print_series_statistics(data_statistics, title='Diffuse horizontal irradiance from SARAH')
    #     if csv:
    #         export_statistics_to_csv(data_statistics, 'diffuse_horizontal_component')

    if verbose == 3:
        debug(locals())
    if verbose > 0:
        print(f'Diffuse irradiance : {diffuse_irradiance}')

    return diffuse_irradiance
