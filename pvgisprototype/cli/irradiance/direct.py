import typer
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND
from pvgisprototype.api.irradiance.direct_time_series import calculate_direct_normal_irradiance_time_series
from pvgisprototype.api.irradiance.direct_time_series import calculate_direct_horizontal_irradiance_time_series
from pvgisprototype.api.irradiance.direct_time_series import calculate_direct_inclined_irradiance_time_series_pvgis
from pvgisprototype.validation.parameters import BaseTimestampSeriesModel
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from typing import Annotated
from typing import Optional
from datetime import datetime
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarIncidenceModels
from pvgisprototype.api.geometry.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_INCIDENCE_ALGORITHM_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_convert_longitude_360
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_optical_air_mass_series
from pvgisprototype import OpticalAirMass
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.constants import RADIANS
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_index
from pathlib import Path
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_verbose
import numpy as np
from pvgisprototype.cli.print import print_irradiance_table_2
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.cli.csv import write_irradiance_csv
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.progress import progress
from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":sun_with_face: Estimate the direct solar irradiance incident on a solar surface",
)


@app.command(
    'normal-series',
    help=f"Estimate the direct normal irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
def get_direct_normal_irradiance_time_series(
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = None, # [LINKE_TURBIDITY_TIME_SERIES_DEFAULT], # REVIEW-ME + Typer Parser
    optical_air_mass_series: Annotated[OpticalAirMass, typer_option_optical_air_mass_series] = None, # [OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT], # REVIEW-ME + ?
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_SERIES_FLAG_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = 'series_in',
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = False,
) -> None:
    # with progress:
    results = calculate_direct_normal_irradiance_time_series(
        timestamps=timestamps,
        start_time=start_time,
        frequency=frequency,
        end_time=end_time,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        optical_air_mass_series=optical_air_mass_series,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        random_days=random_days,
        verbose=verbose,
    )
    # Reporting =============================================================
    if verbose > 0:
        print_irradiance_table_2(
            timestamps=timestamps,
            dictionary=results,
            title=results['Title'] + f" normal irradiance series {IRRADIANCE_UNITS}",
            rounding_places=rounding_places,
            index=index,
            verbose=verbose,
        )
        if statistics:
            print_series_statistics(
                data_array=results['Normal'],
                timestamps=timestamps,
                title=f"Direct normal irradiance series {IRRADIANCE_UNITS}",
                rounding_places=rounding_places,
            )
        if csv:
            write_irradiance_csv(
                longitude=None,
                latitude=None,
                timestamps=timestamps,
                dictionary=results,
                filename=csv,
            )
    else:
        print(results)


@app.command(
    'horizontal-series',
    help=f"Estimate the direct horizontal irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
def get_direct_horizontal_irradiance_time_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,#Annotated[Optional[ZoneInfo], typer_option_timezone] = None,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = None, # [LINKE_TURBIDITY_TIME_SERIES_DEFAULT], # REVIEW-ME + Typer Parser
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = False,
) -> None:
    """Calculate the direct horizontal irradiance (SID) [W*m-2]

    This function implements the algorithm described by Hofierka [1]_.

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.
    """
    results = calculate_direct_horizontal_irradiance_time_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        start_time=start_time,
        frequency=frequency,
        end_time=end_time,
        timezone=timezone,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_position_model=solar_position_model,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    # Reporting =============================================================
    if verbose > 0:
        print_irradiance_table_2(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=results,
            title=results['Title'] + f" horizontal irradiance series {IRRADIANCE_UNITS}",
            rounding_places=rounding_places,
            index=index,
            verbose=verbose,
        )
        if statistics:
            print_series_statistics(
                data_array=results['Normal'],
                timestamps=timestamps,
                title="Direct horizontal irradiance",
                rounding_places=rounding_places,
            )
        if csv:
            write_irradiance_csv(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                dictionary=results,
                filename=csv,
            )
    else:
        print(results)


@app.command(
    'inclined-series',
    help=f"Estimate the direct inclined irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
def get_direct_inclined_irradiance_time_series_pvgis(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_time_series: bool = False,
    direct_horizontal_component: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    surface_tilt: Annotated[Optional[float], typer_option_surface_tilt] = SURFACE_TILT_DEFAULT,
    surface_orientation: Annotated[Optional[float], typer_option_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[SolarIncidenceModels, typer_option_solar_incidence_model] = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = False,
) -> np.array:
    results = calculate_direct_inclined_irradiance_time_series_pvgis(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        start_time=start_time,
        frequency=frequency,
        end_time=end_time,
        convert_longitude_360=convert_longitude_360,
        timezone=timezone,
        random_time_series=random_time_series,
        direct_horizontal_component=direct_horizontal_component,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_angular_loss_factor=apply_angular_loss_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    if verbose > 0:
        longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
        latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
        print_irradiance_table_2(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=results,
            title=f'Direct inclined irradiance series {IRRADIANCE_UNITS}',
            rounding_places=rounding_places,
            index=index,
            verbose=verbose,
        )
        if statistics:
            print_series_statistics(
                data_array=results[DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME],
                timestamps=timestamps,
                title="Direct inclined irradiance",
            )
        if csv:
            write_irradiance_csv(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                dictionary=results,
                filename=csv,
            )
    else:
        print(results)
