import typer
from rich.console import Console
from rich import print
from typing import Annotated
from typing import List
from typing import Optional
from pvgisprototype.api.irradiance.diffuse import calculate_term_n_time_series
from pvgisprototype.api.irradiance.diffuse import calculate_diffuse_sky_irradiance_time_series
from pvgisprototype.api.irradiance.diffuse import diffuse_transmission_function_time_series
from pvgisprototype.api.irradiance.diffuse import diffuse_solar_altitude_coefficients_time_series
from pvgisprototype.api.irradiance.diffuse import diffuse_solar_altitude_function_time_series
from pvgisprototype.api.irradiance.diffuse import calculate_diffuse_horizontal_irradiance_time_series
from pvgisprototype.api.irradiance.diffuse import calculate_diffuse_inclined_irradiance_time_series
from pvgisprototype.api.irradiance.diffuse import read_horizontal_irradiance_components_from_sarah
from pvgisprototype.api.irradiance.diffuse import calculate_diffuse_horizontal_component_from_sarah
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_HORIZONTAL_IRRADIANCE
from pvgisprototype.constants import DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_longitude_in_degrees
from pvgisprototype.cli.typer_parameters import typer_argument_latitude_in_degrees
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
from datetime import datetime
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pathlib import Path
from pvgisprototype.cli.typer_parameters import typer_argument_global_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_global_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_term_n_series
from pvgisprototype.cli.typer_parameters import typer_argument_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer_parameters import typer_argument_solar_altitude_series
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_argument_solar_constant
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.constants import RADIANS
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.api.series.models import MethodsForInexactMatches
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_uniplot
from pvgisprototype.cli.typer_parameters import typer_option_uniplot_terminal_width
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_index
import numpy as np
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.cli.typer_parameters import typer_option_log
from pvgisprototype.constants import DEGREES
from pvgisprototype.constants import GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Calculate the diffuse irradiance incident on a surface",
)
console = Console()


@app.command(
    'n-terms',
    no_args_is_help=True,
    help=f'N Calculate the N term for the diffuse sky irradiance function for a period of time',
    rich_help_panel=rich_help_panel_toolbox,
)
def get_term_n_series(
    kb_series: List[float],
    verbose: int = 0,
):
    """Command line interface to calculate_term_n_time_series()

    Define the N term for a period of time

    Parameters
    ----------
    kb_series: float
        Direct to extraterrestrial irradiance ratio

    Returns
    -------
    N: float
        The N term
    """
    term_n_series = calculate_term_n_time_series(
        kb_series=np.array(kb_series),
        verbose=verbose,
    )
    print(term_n_series)


@app.command(
    'sky-irradiances',
    no_args_is_help=True,
    help=f'⇊ Calculate the diffuse sky irradiance for a period of time',
    rich_help_panel=rich_help_panel_toolbox,
    )
def get_diffuse_sky_irradiance_series(
    n_series: Annotated[List[float], typer_argument_term_n_series],  # Needs a callback to parse list of input values !?
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = np.radians(45),
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
    sky_view_fraction_series = calculate_diffuse_sky_irradiance_time_series(
        n_series=np.array(n_series),
        surface_tilt=surface_tilt,
    )

    print(sky_view_fraction_series)


@app.command(
    'transmission-function',
    no_args_is_help=True,
    help=f'⇝ Calculate the diffuse transmission function over a series of linke turbidity factors',
    rich_help_panel=rich_help_panel_toolbox,
)
def get_diffuse_transmission_function_series(
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_argument_linke_turbidity_factor],#: np.ndarray,
    verbose: int = 0,
) -> np.array:
    """ Diffuse transmission function over a period of time """
    diffuse_transmission_series = diffuse_transmission_function_time_series(
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            verbose=verbose,
    )
    
    print(diffuse_transmission_series)


@app.command(
    'diffuse-altitude-coefficients',
    no_args_is_help=True,
    help=f'☀∡ Calculate the diffuse solar altitude coefficients',
    rich_help_panel=rich_help_panel_toolbox,
)
def get_diffuse_solar_altitude_coefficients_series(
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_argument_linke_turbidity_factor],#: np.ndarray,
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
    diffuse_solar_altitude_coefficients_series = diffuse_solar_altitude_coefficients_time_series(
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        verbose=verbose,
    )

    print('a1, a2, a3')
    print(diffuse_solar_altitude_coefficients_series)


@app.command(
    'diffuse-altitude',
    no_args_is_help=True,
    help=f'☀∡ Calculate diffuse solar altitude angle time series',
    rich_help_panel=rich_help_panel_toolbox,
)
def get_diffuse_solar_altitude_function_time_series(
    solar_altitude_series: Annotated[List[float], typer_argument_solar_altitude_series],
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series],#: np.ndarray,
    verbose: int = 0,
):
    """Diffuse solar altitude function Fd"""
    diffuse_solar_altitude_series = diffuse_solar_altitude_function_time_series(
        solar_altitude_series=solar_altitude_series,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
    )

    print(diffuse_solar_altitude_series)

@app.command(
    'horizontal',
    no_args_is_help=True,
    help=f'☀∡ Estimate the diffuse horizontal irradiance over a period of time [red]Not Complete[/red]',
    rich_help_panel=rich_help_panel_series_irradiance,
)
def get_diffuse_horizontal_irradiance_time_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_time_series: bool = False,
    global_horizontal_irradiance: Annotated[Optional[Path], typer_option_global_horizontal_irradiance] = None,
    direct_horizontal_irradiance: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    surface_orientation: Annotated[Optional[float], typer_option_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[float, typer_option_surface_tilt] = SURFACE_TILT_DEFAULT,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT, # REVIEW-ME + Typer Parser
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModel, typer_option_solar_position_model] = SolarPositionModel.noaa,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.noaa,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_argument_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_FLAG_DEFAULT,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = True,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    uniplot: Annotated[bool, typer_option_uniplot] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = 0,
    index: Annotated[bool, typer_option_index] = False,
    fingerprint: Annotated[bool, typer.Option('--fingerprint', '--fp', help='Fingerprint the photovoltaic power output time series')] = False,
    quiet: Annotated[bool, typer.Option('--quiet', help='Do not print out the output')] = False,
) -> None:
    diffuse_horizontal_irradiance_time_series = calculate_diffuse_horizontal_irradiance_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        timezone=timezone,
        random_time_series=random_time_series,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_angular_loss_factor=apply_angular_loss_factor,
        solar_position_model=solar_position_model,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        random_days=random_days,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        multi_thread=multi_thread,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print import print_irradiance_table_2
            print_irradiance_table_2(
                longitude=convert_float_to_degrees_if_requested(
                    longitude, angle_output_units
                ),
                latitude=convert_float_to_degrees_if_requested(
                    latitude, angle_output_units
                ),
                timestamps=timestamps,
                dictionary=diffuse_horizontal_irradiance_time_series.components,
                title = (
                    DIFFUSE_HORIZONTAL_IRRADIANCE
                    + f" in-plane irradiance series {IRRADIANCE_UNITS}"
                ),
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = diffuse_horizontal_irradiance_time_series.value.flatten().astype(str)
            csv_str = ','.join(flat_list)
            print(csv_str)

    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv
        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=diffuse_horizontal_irradiance_time_series.components,
            filename=csv,
        )
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics
        print_series_statistics(
            data_array=diffuse_horizontal_irradiance_time_series.value,
            timestamps=timestamps,
            title="Diffuse horizontal irradiance",
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_time_series
        uniplot_data_array_time_series(
            data_array=diffuse_horizontal_irradiance_time_series.value,
            data_array_2=None,
            lines=True,
            supertitle = 'Diffuse Horizontal Irradiance Series',
            title = 'Diffuse Horizontal Irradiance Series',
            label = 'Diffuse Horizontal Irradiance',
            label_2 = None,
            unit = IRRADIANCE_UNITS,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=diffuse_horizontal_irradiance_time_series.components)


@app.command(
    'inclined',
    no_args_is_help=True,
    help=f'☀∡ Calculate the diffuse irradiance incident on a surface over a period of time',
    rich_help_panel=rich_help_panel_series_irradiance,
)
def get_diffuse_inclined_irradiance_time_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_time_series: bool = False,
    global_horizontal_irradiance: Annotated[Optional[Path], typer_option_global_horizontal_irradiance] = None,
    direct_horizontal_irradiance: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    surface_orientation: Annotated[Optional[float], typer_option_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[float, typer_option_surface_tilt] = SURFACE_TILT_DEFAULT,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT, # REVIEW-ME + Typer Parser
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModel, typer_option_solar_position_model] = SolarPositionModel.noaa,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.noaa,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_argument_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_FLAG_DEFAULT,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = True,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    uniplot: Annotated[bool, typer_option_uniplot] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = 0,
    index: Annotated[bool, typer_option_index] = False,
    fingerprint: Annotated[bool, typer.Option('--fingerprint', '--fp', help='Fingerprint the photovoltaic power output time series')] = False,
    quiet: Annotated[bool, typer.Option('--quiet', help='Do not print out the output')] = False,
) -> None:
    diffuse_inclined_irradiance_time_series = calculate_diffuse_inclined_irradiance_time_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        timezone=timezone,
        random_time_series=random_time_series,
        global_horizontal_component=global_horizontal_irradiance,
        direct_horizontal_component=direct_horizontal_irradiance,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_angular_loss_factor=apply_angular_loss_factor,
        solar_position_model=solar_position_model,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        random_days=random_days,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        multi_thread=multi_thread,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print import print_irradiance_table_2
            print_irradiance_table_2(
                longitude=convert_float_to_degrees_if_requested(
                    longitude, angle_output_units
                ),
                latitude=convert_float_to_degrees_if_requested(
                    latitude, angle_output_units
                ),
                timestamps=timestamps,
                dictionary=diffuse_inclined_irradiance_time_series.components,
                title = (
                    DIFFUSE_INCLINED_IRRADIANCE
                    + f" in-plane irradiance series {IRRADIANCE_UNITS}"
                ),
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = diffuse_inclined_irradiance_time_series.value.flatten().astype(str)
            csv_str = ','.join(flat_list)
            print(csv_str)

    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv
        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=diffuse_inclined_irradiance_time_series.components,
            filename=csv,
        )
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics
        print_series_statistics(
            data_array=diffuse_inclined_irradiance_time_series.value,
            timestamps=timestamps,
            title="Diffuse inclined irradiance",
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_time_series
        uniplot_data_array_time_series(
            data_array=diffuse_inclined_irradiance_time_series.value,
            data_array_2=None,
            lines=True,
            supertitle = 'Diffuse Inclined Irradiance Series',
            title = 'Diffuse Inclined Irradiance Series',
            label = 'Diffuse Inclined Irradiance',
            label_2 = None,
            unit = IRRADIANCE_UNITS,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=diffuse_inclined_irradiance_time_series.components)


@app.command(
    'from-sarah',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
def get_diffuse_horizontal_component_from_sarah(
    shortwave: Annotated[Path, typer_argument_global_horizontal_irradiance],
    direct: Annotated[Path, typer_argument_direct_horizontal_irradiance],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamps: Annotated[Optional[datetime], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = True,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    uniplot: Annotated[bool, typer_option_uniplot] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = 0,
    index: Annotated[bool, typer_option_index] = False,
    fingerprint: Annotated[bool, typer.Option('--fingerprint', '--fp', help='Fingerprint the photovoltaic power output time series')] = False,
    quiet: Annotated[bool, typer.Option('--quiet', help='Do not print out the output')] = False,
):
    """Calculate the diffuse horizontal irradiance from SARAH time series.

    Parameters
    ----------
    shortwave: Path
        Filename of surface short-wave (solar) radiation downwards time series
        (short name : `ssrd`) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth. This parameter
        comprises both direct and diffuse solar radiation.

    direct: Path
        Filename of surface .. time series
        (short name : ``) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth. 

    Returns
    -------
    diffuse_horizontal_irradiance: float
        The diffuse radiant flux incident on a horizontal surface per unit area in W/m².
    """
    if shortwave and direct:
        horizontal_irradiance_components = (
            read_horizontal_irradiance_components_from_sarah(
                shortwave=shortwave,
                direct=direct,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                mask_and_scale=mask_and_scale,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                in_memory=in_memory,
                multi_thread=multi_thread,
                verbose=verbose,
                log=log,
            )
        )
        global_horizontal_irradiance_series = horizontal_irradiance_components[
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
        direct_horizontal_irradiance_series = horizontal_irradiance_components[
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
        diffuse_horizontal_irradiance_series = calculate_diffuse_horizontal_component_from_sarah(
            global_horizontal_irradiance_series=global_horizontal_irradiance_series,
            direct_horizontal_irradiance_series=direct_horizontal_irradiance_series,
            # longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
            # latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
            # timestamps=timestamps,
            # neighbor_lookup=neighbor_lookup,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )

    if not quiet:
        if verbose > 0:
            from pvgisprototype.constants import TITLE_KEY_NAME
            from pvgisprototype.cli.print import print_irradiance_table_2
            print_irradiance_table_2(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                dictionary=diffuse_horizontal_irradiance_series.components,
                title=diffuse_horizontal_irradiance_series.components[TITLE_KEY_NAME] + f' in-plane irradiance series {IRRADIANCE_UNITS}',
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = diffuse_horizontal_irradiance_series.value.flatten().astype(str)
            csv_str = ','.join(flat_list)
            print(csv_str)
    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv
        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=diffuse_horizontal_irradiance_series.components,
            filename=csv,
        )
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics
        print_series_statistics(
            data_array=diffuse_horizontal_irradiance_series.value,
            timestamps=timestamps,
            title="Diffuse horizontal irradiance",
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_time_series
        uniplot_data_array_time_series(
            data_array=diffuse_horizontal_irradiance_series.value,
            data_array_2=None,
            lines=True,
            supertitle = 'Diffuse Horizontal Irradiance Series',
            title = 'Diffuse Horizontal Irradiance Series',
            label = 'Diffuse Horizontal Irradiance',
            label_2 = None,
            unit = IRRADIANCE_UNITS,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=diffuse_horizontal_irradiance_series.components)
