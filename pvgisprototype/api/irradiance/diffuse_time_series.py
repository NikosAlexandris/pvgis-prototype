from devtools import debug
import logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('error.log'),  # Save log to a file
        logging.StreamHandler()  # Print log to the console
    ]
)
from datetime import datetime
import typer
from pathlib import Path
from typing import Annotated
from typing import Optional
from typing import List
from rich.console import Console
from rich import print
from colorama import Fore, Style
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.cli.csv import write_irradiance_csv
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.validation.parameters import BaseTimestampSeriesModel
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_argument_term_n_series
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_global_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_argument_solar_altitude_series
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_argument_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.api.irradiance.direct_time_series import calculate_direct_horizontal_irradiance_time_series
from pvgisprototype.api.irradiance.direct_time_series import calculate_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.api.irradiance.direct_time_series import print_irradiance_table_2
from pvgisprototype.api.geometry.solar_altitude_time_series import model_solar_altitude_time_series
from pvgisprototype.api.geometry.solar_time_time_series import model_solar_time_time_series
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours_time_series
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_if_requested
from pvgisprototype.algorithms.jenco.solar_incidence import calculate_solar_incidence_time_series_jenco
from pvgisprototype.api.geometry.solar_azimuth_time_series import model_solar_azimuth_time_series
from .loss import calculate_angular_loss_factor_for_nondirect_irradiance

from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import TERM_N_IN_SHADE
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.constants import LINKE_TURBIDITY_UNIT
from pvgisprototype.cli.typer_parameters import typer_argument_global_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_longitude_in_degrees
from pvgisprototype.cli.typer_parameters import typer_argument_latitude_in_degrees
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.api.series.utilities import select_location_time_series
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.series.models import MethodsForInexactMatches
import numpy as np
from math import cos
from math import sin
from math import pi


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Calculate the diffuse irradiance incident on a surface",
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
    timestamps: Annotated[Optional[datetime], typer_argument_timestamps],
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
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
    global_horizontal_irradiance_series = select_time_series(
        time_series=shortwave,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
    )#.to_numpy()  # We need NumPy!

    direct_horizontal_irradiance_series = select_time_series(
        time_series=direct,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
    )#.to_numpy()  # We need NumPy!

    diffuse_horizontal_irradiance_series = (
        global_horizontal_irradiance_series
        - direct_horizontal_irradiance_series
    )

    if diffuse_horizontal_irradiance_series.size == 1:
        single_value = float(diffuse_horizontal_irradiance_series.values)
        warning = (
            Fore.YELLOW
            + f"{exclamation_mark} The selected timestamp "
            + Fore.GREEN
            + f"{diffuse_horizontal_irradiance_series.time.values}"
            + Fore.YELLOW
            + f" matches the single value "
            + Fore.GREEN
            + f"{single_value}"
            + Style.RESET_ALL
        )
        logging.warning(warning)

        if verbose > 5:
            debug(locals())

        if verbose > 0:
            print(Fore.YELLOW + warning)

    results = {
        "Diffuse": diffuse_horizontal_irradiance_series.to_numpy(),
    }
    title = 'Diffuse horizontal'

    if verbose > 1 :
        extended_results = {
            "Shortwave": global_horizontal_irradiance_series.to_numpy(),
            "Direct": direct_horizontal_irradiance_series.to_numpy(),
        }
        results = results | extended_results

    if verbose > 5:
        debug(locals())

    print_irradiance_table_2(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        dictionary=results,
        title=title + f' in-plane irradiance series {IRRADIANCE_UNITS}',
        rounding_places=rounding_places,
        verbose=verbose,
    )
    if statistics:
        print_series_statistics(
            data_array=diffuse_horizontal_irradiance_series,
            timestamps=timestamps,
            title="Diffuse horizontal irradiance",
        )
    if csv:
        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=results,
            filename=csv,
        )

    return diffuse_horizontal_irradiance_series


@app.command(
    'n-term-series',
    no_args_is_help=True,
    help=f'N Calculate the N term for the diffuse sky irradiance function for a period of time',
    rich_help_panel=rich_help_panel_toolbox,
)
def calculate_term_n_time_series(
    kb_series: List[float],
    verbose: int = 0,
):
    """Define the N term for a period of time

    Parameters
    ----------
    kb_series: float
        Direct to extraterrestrial irradiance ratio

    Returns
    -------
    N: float
        The N term
    """
    if verbose > 5:
        debug(locals())

    return 0.00263 - 0.712 * kb_series - 0.6883 * np.power(kb_series, 2)


@app.command(
        'sky-irradiance-series',
        no_args_is_help=True,
        help=f'⇊ Calculate the diffuse sky irradiance for a period of time',
        rich_help_panel=rich_help_panel_series_irradiance,
        )
def calculate_diffuse_sky_irradiance_time_series(
        n_series: Annotated[List[float], typer_argument_term_n_series],
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

    n_series: float
        The term N

    Returns
    -------

    Notes
    -----
    Internally the function calculates first the dimensionless fraction of the
    sky dome viewed by a tilted (or inclined) surface `ri(γN)`.
    """
    sky_view_fraction = (1 + cos(surface_tilt)) / 2
    # -----------------------------------------------------------------------
    # Verify the following : does it work ?
    # diffuse_sky_irradiance_series = sky_view_fraction
    # +(
    #     sin(surface_tilt)
    #     - surface_tilt
    #     * cos(surface_tilt)
    #     - pi
    #     * sin(surface_tilt / 2) ** 2
    # ) * n_series
    # -----------------------------------------------------------------------
    diffuse_sky_irradiance_series = sky_view_fraction
    + (
        sin(surface_tilt)
        - surface_tilt
        * cos(surface_tilt)
        - pi
        * sin(surface_tilt / 2) ** 2
    )

    return diffuse_sky_irradiance_series * n_series


@app.command(
    'transmission-function-series',
    no_args_is_help=True,
    help=f'⇝ Calculate the diffuse transmission function over a series of linke turbidity factors',
    rich_help_panel=rich_help_panel_toolbox,
)
def diffuse_transmission_function_time_series(
    linke_turbidity_factor_series,
    verbose: int = 0,
):
    """ Diffuse transmission function over a period of time """
    is_scalar = False
    
    if isinstance(linke_turbidity_factor_series, LinkeTurbidityFactor):
        is_scalar = True
        linke_turbidity_factor_series = [linke_turbidity_factor_series]
    elif isinstance(linke_turbidity_factor_series, np.ndarray):
        # If the input is a numpy array, convert it to a list for the following processing
        linke_turbidity_factor_series = linke_turbidity_factor_series.tolist()
    
    # Check if the elements in the series are LinkeTurbidityFactor objects and extract the value attribute if true
    if all(isinstance(factor, LinkeTurbidityFactor) for factor in linke_turbidity_factor_series):
        linke_turbidity_factor_series = [factor.value for factor in linke_turbidity_factor_series]
    
    linke_turbidity_factor_series_array = np.array(linke_turbidity_factor_series)
    linke_turbidity_factor_series_squared_array = np.power(linke_turbidity_factor_series_array, 2)

    # From r.pv's source code:
    # tn = -0.015843 + locLinke * (0.030543 + 0.0003797 * locLinke);
    diffuse_transmission_series = (
        -0.015843
        + 0.030543 * linke_turbidity_factor_series_array
        + 0.0003797 * linke_turbidity_factor_series_squared_array
    )

    if verbose > 5:
        debug(locals())

    if is_scalar:
        return diffuse_transmission_series[0]
    else:
        return diffuse_transmission_series.tolist()


@app.command(
        'diffuse-altitude-coefficients-series',
        no_args_is_help=True,
        help=f'☀∡ Calculate the diffuse solar altitude coefficients',
        rich_help_panel=rich_help_panel_toolbox,
        )
def diffuse_solar_altitude_coefficients_time_series(
    # linke_turbidity_factor_series: Union[
    #     List[LinkeTurbidityFactor], LinkeTurbidityFactor
    # ],
    linke_turbidity_factor_series,
    verbose: int = 0,
):
    """
    Vectorized function to calculate the diffuse solar altitude coefficients over a period of time.

    Parameters
    ----------
    - linke_turbidity_factor_series (List[LinkeTurbidityFactor] or LinkeTurbidityFactor): 
      The Linke turbidity factors as a list of LinkeTurbidityFactor objects or a single object.

    Returns
    -------
    """
    is_scalar = False
    if isinstance(linke_turbidity_factor_series, LinkeTurbidityFactor):
        is_scalar = True
        linke_turbidity_factor_series = [linke_turbidity_factor_series]

    # Convert to NumPy array for vectorized operations
    linke_turbidity_factor_series = [factor.value for factor in linke_turbidity_factor_series]
    linke_turbidity_factor_series_array = np.array(linke_turbidity_factor_series)

    # Calculate common terms only once
    linke_turbidity_factor_series_squared_array = np.power(linke_turbidity_factor_series_array, 2)
    diffuse_transmission_series = diffuse_transmission_function_time_series(linke_turbidity_factor_series)
    diffuse_transmission_series_array = np.array(diffuse_transmission_series)
    a1_prime_series = (
        0.26463
        - 0.061581 * linke_turbidity_factor_series_array
        + 0.0031408 * linke_turbidity_factor_series_squared_array
    )
    a1_series = np.where(
        a1_prime_series * diffuse_transmission_series < 0.0022, 
        np.maximum(0.0022 / diffuse_transmission_series_array, a1_prime_series), 
        a1_prime_series
    )
    a2_series = (
        2.04020
        + 0.018945 * linke_turbidity_factor_series_array
        - 0.011161 * linke_turbidity_factor_series_squared_array
    )
    a3_series = (
        -1.3025
        + 0.039231 * linke_turbidity_factor_series_array
        + 0.0085079 * linke_turbidity_factor_series_squared_array
    )

    if verbose == 5:
        debug(locals())
    if is_scalar:
        return a1_series[0], a2_series[0], a3_series[0]
    else:
        return a1_series, a2_series, a3_series


@app.command(
    'diffuse-solar-altitude',
    no_args_is_help=True,
    help=f'☀∡ Calculate diffuse solar altitude angle time series',
    rich_help_panel=rich_help_panel_toolbox,
)
def diffuse_solar_altitude_function_time_series(
    solar_altitude_series: Annotated[List[float], typer_argument_solar_altitude_series],
    linke_turbidity_factor_series: Annotated[List[float], typer_option_linke_turbidity_factor_series],#: np.ndarray,
    verbose: int = 0,
):
    """Diffuse solar altitude function Fd"""
    a1_series, a2_series, a3_series = diffuse_solar_altitude_coefficients_time_series(
        linke_turbidity_factor_series
    )
    solar_altitude_series_array = np.array([altitude.radians for altitude in solar_altitude_series])
    return (
        a1_series
        + a2_series * np.sin(solar_altitude_series_array)
        + a3_series * np.power(np.sin(solar_altitude_series_array), 2)
    )


@app.command(
    'inclined-series',
    no_args_is_help=True,
    help=f'☀∡ Calculate the diffuse irradiance incident on a surface over a period of time',
    rich_help_panel=rich_help_panel_series_irradiance,
)
def calculate_diffuse_inclined_irradiance_time_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_time_series: bool = False,
    global_horizontal_component: Annotated[Optional[Path], typer_option_global_horizontal_irradiance] = None,
    direct_horizontal_component: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    surface_tilt: Annotated[Optional[float], typer_option_surface_tilt] = SURFACE_TILT_DEFAULT,
    surface_orientation: Annotated[Optional[float], typer_option_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: Annotated[List[float], typer_option_linke_turbidity_factor_series] = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SolarPositionModels.noaa,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.noaa,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_argument_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_FLAG_DEFAULT,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
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

    # 1. Calculate the direct horizontal irradiance

    if direct_horizontal_component:  # read from external dataset
        direct_horizontal_irradiance_series = select_time_series(
            time_series=direct_horizontal_component,
            longitude=convert_float_to_degrees_if_requested(longitude, "degrees"),
            latitude=convert_float_to_degrees_if_requested(latitude, "degrees"),
            timestamps=timestamps,
            mask_and_scale=mask_and_scale,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            in_memory=in_memory,
        ).to_numpy()  # We need NumPy!

    else:  # from the model
        direct_horizontal_irradiance_series = calculate_direct_horizontal_irradiance_time_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        verbose=0,  # no verbosity here by choice!
    )

    # 2. Get quantities to calculate the diffuse horizontal irradiance

    # G0
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_time_series(
            timestamps=timestamps,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            random_days=random_days,
        )
    )

    # extraterrestrial on a horizontal surface requires the solar altitude
    solar_altitude_series = model_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=verbose,
        )
    solar_altitude_series_array = np.array([x.radians for x in solar_altitude_series])
    # on a horizontal surface : G0h = G0 sin(h0)
    extraterrestrial_horizontal_irradiance_series = (
        extraterrestrial_normal_irradiance_series
        * np.sin(solar_altitude_series_array)
    )

    # calculate from external data
    if global_horizontal_component and direct_horizontal_component:
        diffuse_horizontal_irradiance_series = (
            calculate_diffuse_horizontal_component_from_sarah(
                shortwave=global_horizontal_component,
                direct=direct_horizontal_component,
                longitude=convert_float_to_degrees_if_requested(longitude, "degrees"),
                latitude=convert_float_to_degrees_if_requested(latitude, "degrees"),
                timestamps=timestamps,
                start_time=start_time,
                end_time=end_time,
                timezone=timezone,
                neighbor_lookup=neighbor_lookup,
                verbose=0,
            )
        ).to_numpy()  # We need NumPy!

    else:  # model it
        # Dhc [W.m-2]
        diffuse_horizontal_irradiance_series = (
            extraterrestrial_normal_irradiance_series
            * diffuse_transmission_function_time_series(linke_turbidity_factor_series)
            * diffuse_solar_altitude_function_time_series(
                solar_altitude_series, linke_turbidity_factor_series
            )
        )

    if surface_tilt == 0:  # horizontal surface
        diffuse_inclined_irradiance_series = diffuse_horizontal_irradiance_series

    else:  # tilted (or inclined) surface
    # Note: in PVGIS: if surface_orientation != 'UNDEF' and surface_tilt != 0:

        # proportion between direct (beam) and extraterrestrial irradiance : Kb
        kb_series = (
            direct_horizontal_irradiance_series
            / extraterrestrial_horizontal_irradiance_series
        )

        # the N term
        n_series = calculate_term_n_time_series(kb_series)
        diffuse_sky_irradiance_series = calculate_diffuse_sky_irradiance_time_series(
            n_series=n_series,
            surface_tilt=surface_tilt,
        )

        # surface in shade requires solar incidence angles -- REVIEW-ME ----
        solar_incidence_series = calculate_solar_incidence_time_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            random_time_series=random_time_series,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            verbose=verbose,
        )
        solar_incidence_series_array = np.array([x.value for x in solar_incidence_series])

        # mask surfaces in shade, yet there is ambient light
        mask = np.logical_and(np.sin(solar_incidence_series_array) < 0, solar_altitude_series_array >= 0)
        if np.any(mask):

            # F(γN)
            diffuse_sky_irradiance_series[mask] = (
                calculate_diffuse_sky_irradiance_time_series(
                    n_series=np.full(len(timestamps), TERM_N_IN_SHADE),
                    surface_tilt=surface_tilt,
                )[mask]
            )
            diffuse_inclined_irradiance_series = np.zeros_like(solar_altitude_series, dtype='float64')
            diffuse_inclined_irradiance_series[mask] = (
                diffuse_horizontal_irradiance_series[mask] 
                * diffuse_sky_irradiance_series[mask]
            )

        else:  # sunlit surface and non-overcast sky
            # extract float values from the SolarAltitude objects
            solar_altitude_series_array = np.array([altitude.radians for altitude in solar_altitude_series])
            # ----------------------------------------------------------------
            azimuth_difference_series_array = None  # Avoid UnboundLocalError!
            solar_azimuth_series_array = None
            # ----------------------------------------------------------------

            if np.any(solar_altitude_series_array >= 0.1):  # radians or 5.7 degrees
                diffuse_inclined_irradiance_series = diffuse_horizontal_irradiance_series * (
                    diffuse_sky_irradiance_series * (1 - kb_series)
                    + kb_series * np.sin(solar_incidence_series_array) / np.sin(solar_altitude_series_array)
                )

            else:  # if solar_altitude.value < 0.1:
                # requires the solar azimuth
                solar_azimuth_series = model_solar_azimuth_time_series(
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    timezone=timezone,
                    solar_position_model=solar_position_model,
                    apply_atmospheric_refraction=apply_atmospheric_refraction,
                    refracted_solar_zenith=refracted_solar_zenith,
                    solar_time_model=solar_time_model,
                    time_offset_global=time_offset_global,
                    hour_offset=hour_offset,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                    verbose=verbose,
                )
                solar_azimuth_series_array = np.array([x.value for x in solar_azimuth_series])
                # Normalize the azimuth difference to be within the range -pi to pi
                # A0 : solar azimuth _measured from East_ in radians
                # ALN : angle between the vertical surface containing the normal to the
                #   surface and vertical surface passing through the centre of the solar
                #   disc [rad]
                azimuth_difference_series_array = solar_azimuth_series_array - surface_orientation
                azimuth_difference_series_array = np.arctan2(np.sin(azimuth_difference_series_array), np.cos(azimuth_difference_series_array))
                diffuse_inclined_irradiance_series = (
                    diffuse_inclined_irradiance_series_before_angular_loss
                ) = diffuse_horizontal_irradiance_series * (
                    diffuse_sky_irradiance_series * (1 - kb_series)
                    + kb_series
                    * sin(surface_tilt)
                    * np.cos(azimuth_difference_series_array)
                    / (0.1 - 0.008 * solar_altitude_series_array)
                )

    # one more thing
    if apply_angular_loss_factor:

        diffuse_irradiance_angular_loss_coefficient = sin(surface_tilt) + (
            pi - surface_tilt - sin(surface_tilt)
        ) / (1 + cos(surface_tilt))
        diffuse_irradiance_loss_factor = calculate_angular_loss_factor_for_nondirect_irradiance(
            indirect_angular_loss_coefficient=diffuse_irradiance_angular_loss_coefficient,
        )
        diffuse_inclined_irradiance_series *= diffuse_irradiance_loss_factor

    # Warning

    LOWER_PHYSICALLY_POSSIBLE_LIMIT = -4
    UPPER_PHYSICALLY_POSSIBLE_LIMIT = 2000  # Update-Me
    # See : https://bsrn.awi.de/fileadmin/user_upload/bsrn.awi.de/Publications/BSRN_recommended_QC_tests_V2.pdf
    out_of_range_indices = np.where(
        (diffuse_inclined_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT)
        | (diffuse_inclined_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    )
    if out_of_range_indices[0].size > 0:
        print(
            f"[blink red on white]{WARNING_OUT_OF_RANGE_VALUES} in `diffuse_inclined_irradiance_series`![/blink red on white]"
        )

    # Reporting ==============================================================

    results = {
        "Diffuse": diffuse_inclined_irradiance_series,
    }
    title = 'Diffuse'

    if verbose > 1 :
        extended_results = {
            "Loss": 1 - diffuse_irradiance_loss_factor if apply_angular_loss_factor else '-',
            "Tilt": convert_float_to_degrees_if_requested(surface_tilt, angle_output_units),
        }
        results = results | extended_results

    if verbose > 2:
        more_extended_results = {
            'Diffuse horizontal': diffuse_horizontal_irradiance_series,
            'Diffuse clear-sky': diffuse_sky_irradiance_series,
        }
        results = results | more_extended_results
        title += ' & relevant components'

    if verbose > 3:
        even_more_extended_results = {
            'term N': n_series,
            'Kb': kb_series,
            'Tilt': surface_tilt,
            'Azimuth difference': azimuth_difference_series_array if azimuth_difference_series_array is not None else '-',
            '⦬ Azimuth': solar_azimuth_series_array if solar_azimuth_series_array is not None else '-',
            '⦩ Altitude': convert_series_to_degrees_if_requested(solar_altitude_series_array, angle_output_units),
        }
        results = results | even_more_extended_results

    if verbose > 4:
        linke_turbidity_factor_series_array = np.array([x.value for x in linke_turbidity_factor_series])
        plus_even_more_extended_results = {
            "Direct horizontal": direct_horizontal_irradiance_series,
            'Extra. horizontal': extraterrestrial_horizontal_irradiance_series,
            "Extra. normal": extraterrestrial_normal_irradiance_series,
            'Linke': linke_turbidity_factor_series_array,
            'Incidence': convert_series_to_degrees_if_requested(solar_incidence_series_array, angle_output_units),
            'Out-of-range': out_of_range_indices,
        }
        results = results | plus_even_more_extended_results

    if verbose > 5:
        debug(locals())

    print_irradiance_table_2(
        longitude=convert_float_to_degrees_if_requested(longitude, angle_output_units),
        latitude=convert_float_to_degrees_if_requested(latitude, angle_output_units),
        timestamps=timestamps,
        dictionary=results,
        title=title + f" in-plane irradiance series {IRRADIANCE_UNITS}",
        rounding_places=rounding_places,
        verbose=verbose,
    )
    if statistics:
        print_series_statistics(
            data_array=diffuse_inclined_irradiance_series,
            timestamps=timestamps,
            title="Diffuse inclined irradiance",
        )
    if csv:
        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=results,
            filename=csv,
        )

    return diffuse_inclined_irradiance_series
